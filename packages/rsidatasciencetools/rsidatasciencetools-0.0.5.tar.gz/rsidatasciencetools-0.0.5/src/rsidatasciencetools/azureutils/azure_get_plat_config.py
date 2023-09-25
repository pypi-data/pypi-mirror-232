import os
import asyncio
import sys
import pymongo
from argparse import ArgumentParser
from itertools import chain
import logging

from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import (
    BlobCheckpointStore
)
from rsidatasciencetools.azureutils import az_logging
from rsidatasciencetools.config.baseconfig import EnvConfig, log_level_dict
from pathlib import Path


logger = az_logging.get_az_logger(__name__)


# dotenv_path = Path('.az_env')
COSMOS_DB = COSMOS_COLLECTION = COSMOS_CONNECTION_STRING = None
EVENT_HUB_CONNECTION_STRING = EVENT_HUB_NAME = \
    CONSUMER_GROUP = BLOB_STORAGE_CONNECTION_STRING = \
        BLOB_CONTAINER_NAME = REVX_CONFIG_MATCH_KEY = None

_debug = 0
status = []
events_list = []
mongo_client = None


def init_eh_datastore(env):
    global EVENT_HUB_CONNECTION_STRING, EVENT_HUB_NAME, \
        CONSUMER_GROUP, BLOB_STORAGE_CONNECTION_STRING, \
            BLOB_CONTAINER_NAME, REVX_CONFIG_MATCH_KEY
    EVENT_HUB_CONNECTION_STRING = env['EVENT_HUB_CONNECTION_STRING']
    EVENT_HUB_NAME = env['EVENT_HUB_NAME']
    CONSUMER_GROUP = env['CONSUMER_GROUP']
    BLOB_STORAGE_CONNECTION_STRING = env['BLOB_STORAGE_CONNECTION_STRING']
    BLOB_CONTAINER_NAME = env['BLOB_CONTAINER_NAME']
    REVX_CONFIG_MATCH_KEY = env['REVX_CONFIG_MATCH_KEY']
    logger.info('connecting to EH with:\n    ' + '\n    '.join([
        f'{k}: {env[k]}' for k in [
            'EVENT_HUB_CONNECTION_STRING',
            'CONSUMER_GROUP',
            'EVENT_HUB_NAME']]))


def init_mongo_conn(env):
    global mongo_client, COSMOS_DB, COSMOS_COLLECTION, COSMOS_CONNECTION_STRING
    COSMOS_DB = env['COSMOS_DB']
    COSMOS_COLLECTION = env['COSMOS_COLLECTION']
    COSMOS_CONNECTION_STRING = env['COSMOS_CONNECTION_STRING']
    try:
        mongo_client = pymongo.MongoClient(COSMOS_CONNECTION_STRING)
        try:
            mongo_client.server_info()
        except (
            pymongo.errors.OperationFailure,
            pymongo.errors.ConnectionFailure,
            pymongo.errors.ExecutionTimeout,
        ) as err:
            sys.exit("Can't connect:" + str(err))
    except Exception as err:
        sys.exit("Error:" + str(err))
    logger.info('connecting to Cosmos/Mongo-like DB with:\n    ' + 
        '\n    '.join([f'{k}: {env[k]}' for k in [
            'COSMOS_CONNECTION_STRING',
            'COSMOS_DB',
            'COSMOS_COLLECTION']]))        


async def cosmos(platform_config):
    db = mongo_client[COSMOS_DB]
    if COSMOS_DB not in mongo_client.list_database_names():
        # Create a database with 400 RU throughput that can be shared across
        # the DB's collections
        if 'cosmos' in COSMOS_CONNECTION_STRING.lower():
            db.command({"customAction": "CreateDatabase", "offerThroughput": 400})
            logger.debug(f"Created db '{COSMOS_DB}' with shared throughput.\n")
        else:
            logger.debug(f"Created db '{COSMOS_DB}' within mongo framework.\n")

    else:
        logger.debug(f"Using database: '{COSMOS_DB}'.\n")

    collection = db[COSMOS_COLLECTION]
    index_cfg = {'names': ["_id", "PlatformConfigurationId"],
                 'order': [1,2]}
    if COSMOS_COLLECTION not in db.list_collection_names():
        # Creates a unsharded collection that uses the DBs shared throughput
        indexes = [
            {"key": {n: ord}, "name": f"_id_{ord:d}"}
            for n, ord in zip(index_cfg["names"], index_cfg['order'])
        ]
        if 'cosmos' in COSMOS_CONNECTION_STRING.lower():
            db.command(
                {"customAction": "CreateCollection", "collection": COSMOS_COLLECTION}
            )
            db.command(
                {
                    "customAction": "UpdateCollection",
                    "collection": COSMOS_COLLECTION,
                    "indexes": indexes,
                }
            )
        else:
            collection.create_index([(n, ord if ord < index_cfg['order'][-1] else -1) 
                for n, ord in zip(index_cfg['names'], index_cfg['order'])])
        logger.debug("Created collection '{}'.\n".format(COSMOS_COLLECTION))
        logger.debug("Indexes are: {}\n".format(sorted(collection.index_information())))
    else:
        msg = "Using collection: '{}'.".format(COSMOS_COLLECTION)
        logger.debug(msg)
        status.append(msg)
    
    """Create new document and upsert (create or replace) to collection"""    
    result = collection.update_one(
        {"PlatformConfigurationId": platform_config["PlatformConfigurationId"]}, {"$set": platform_config}, upsert=True
    )
    #print("Upserted document with _id {}\n".format(result.upserted_id))    
    msg = "Upserted document with _id {}".format(result.upserted_id)
    logger.debug(msg)
    status.append(msg)
    
    if result.upserted_id:
        doc = collection.find_one({"_id": result.upserted_id})
        #print("Found a document with _id {}: {}\n".format(result.upserted_id, doc))        
        msg = "Found a document with _id {}".format(result.upserted_id)
        logger.debug(msg)
        status.append(msg)
    
    # """Query for documents in the collection"""
    print(f"PlatformConfiguration with ConfigurationType '{REVX_CONFIG_MATCH_KEY}':\n")
    allPlatformConfigurationQuery = {"ConfigurationType": REVX_CONFIG_MATCH_KEY}
    for doc in collection.find(allPlatformConfigurationQuery).sort(
        "PlatformConfigurationId", pymongo.ASCENDING
    ):
        msg = "Found a PlatformConfiguration with _id {}".format(doc["_id"])
        logger.debug(msg)
        status.append(msg)


async def on_event_batch(partition_context, events):
    logger.info(f'processing and filtering {len(events)} events:')
    for e in events:
        platform_config = e.body_as_json()
        events_list.append(platform_config['ConfigurationType'])
        if (REVX_CONFIG_MATCH_KEY == platform_config['ConfigurationType'].strip()):
            logger.info(e.enqueued_time, platform_config['ConfigurationName'],
                             platform_config['PlatformConfigurationId'],platform_config['TenantID'])            
            status.append(platform_config['ConfigurationName'] + ' : ' + str(e.enqueued_time))
            await cosmos(platform_config)
    
    # Update the checkpoint so that the program doesn't read the events
    # that it has already read when you run it next time.    
    await partition_context.update_checkpoint()


async def main_eh_data_collector(start_offset="-1", debug=0):
    global mongo_client, _debug
    
    if mongo_client is None:
        env = EnvConfig(*((args['cfg'],) if args['cfg'] is not None else tuple()))
        _debug = env.get('DEBUG', debug)
        logger.setLevel(log_level_dict[_debug])
        init_mongo_conn(env)
        init_eh_datastore(env)
    
    # Create an Azure blob checkpoint store to store the checkpoints.
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        BLOB_STORAGE_CONNECTION_STRING, BLOB_CONTAINER_NAME
    )

    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STRING,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENT_HUB_NAME,
        checkpoint_store=checkpoint_store,
    )
    async with client:
        # Call the receive method. Read from the beginning of the
        # partition (starting_position: "-1")
        await client.receive_batch(
            on_event_batch=on_event_batch, 
            starting_position=start_offset,
            max_wait_time=5,
            max_batch_size=100)


if __name__ == "__main__":
    
    parser = ArgumentParser(description='Run the Event Hub AML configuration scraper')
    parser.add_argument('--cfg', nargs='?', type=str, default=None,
                        help='the path to the connection configuration .env files')
    parser.add_argument('--debug', '-d', nargs='?', type=int,  const=1, default=0,
                        help='debug level')

    # print('args = ', args)
    args = {k:v for k,v in parser.parse_args().__dict__.items()}

    _debug = args['debug']
    logger.setLevel(level=log_level_dict[_debug])

    loop = asyncio.get_event_loop()
    if _debug <= 1:
        loop.run_until_complete(main_eh_data_collector())
    else:
        # start the event pointer earlier - grab records from two weeks ago
        import datetime
        loop.run_until_complete(main_eh_data_collector(debug=_debug, 
            start_offset=(datetime.datetime.now()-datetime.timedelta(days=3))))