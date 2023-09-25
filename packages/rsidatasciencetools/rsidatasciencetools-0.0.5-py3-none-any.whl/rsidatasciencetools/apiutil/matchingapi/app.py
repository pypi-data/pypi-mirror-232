import os
import json
import requests
import uvicorn
import subprocess
import asyncio
import pandas as pd
from typing import Union, Dict, List
from argparse import ArgumentParser
import yaml, json
from itertools import chain
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException  # to import later: BackgroundTasks
from fastapi_versioning import VersionedFastAPI, version
# to be utilized as necessary:
# from starlette.middleware import Middleware
from rsidatasciencetools.apiutil.matchingapi.schemas import SetConfig_t
from rsidatasciencetools.config.baseconfig import EnvConfig, YmlConfig
from rsidatasciencetools.sqlutils.sqlconfig import SQLConfig
# the following function is for polling and storing the platform config data:
# from rsidatasciencetools.azureutils.azure_get_plat_config import main_eh_data_collector
from rsidatasciencetools.datautils import matching_vectorembed
from rsidatasciencetools.datautils.matching_vectorembed import main_embed_call

APP_URI = 'http://' + os.getenv('RSI_HOSTNAME', 'localhost:8000') + '/docs'
print(f"Matching API URI = {APP_URI}")

defaults_path = os.path.join(os.path.dirname(__file__), 'tests')

if 'RSI_CONFIG_PATH' not in os.environ:
    os.environ['RSI_CONFIG_PATH'] = defaults_path

env = EnvConfig(error_no_file_found=False, debug=1)
match_tool_dir = os.path.dirname(os.path.abspath(matching_vectorembed.__file__))

app = FastAPI(title="RSI Matching API")
app = FastAPI(
    title='Matching API',
    description=('Matching API is used to build embedding model on dataset '
        'and match incoming new records'),
    middleware=None        
)

tenant_path = lambda tenant: os.path.join(env.primary_path,tenant)

class ModelBuildTask:
    def __init__(self):
        self.message = []
        self.inprogress = False
    
    def background_work(self, tpath, debug=0):    
        self.message = []
        self.inprogress = True
        # print(tpath, type(tpath), debug, type(debug))
        loc_cmd_args = (os.path.abspath(os.path.join(os.path.dirname(__file__),'../../datautils')),
                        f'python matching_vectorembed.py -s -c {tpath} -d {debug} --load 0')
        # print("loc_cmd_args:", loc_cmd_args)
        self.message.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + 
                            f' Command to run (in {loc_cmd_args[0]}): {loc_cmd_args[1]}')
        completed_process = subprocess.run(
            loc_cmd_args[1].split(' '), 
            cwd=loc_cmd_args[0], 
            # shell=True, 
            stdout=subprocess.PIPE)
        self.message.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + 
                            ' Train unsuprvised embedding model using reference record data')
        self.message.append(completed_process.stdout.decode('utf-8').splitlines())

        self.inprogress = False

    def get_status(self):
        return self.message

    def get_progress(self):
        return self.inprogress

model_build_task = ModelBuildTask()

@app.get("/")
@version(1, 0)
async def read_root():
    return "matching API V1.0 is Running..."

# @app.get("/")
# @version(1, 1)
# async def read_root():
#     print(jwt_values["revx_user"])
#     print(jwt_values["tenant_id"])
#     return "matching API V1.1 is Running..."


@app.post("/set_matching_config")
@version(1, 0)
async def matching_config(tenant:str, config: SetConfig_t):
    config = dict(config)
    tpath = tenant_path(tenant)
    # print(f" tenant: {tenant}") 
    if not os.path.exists(tpath):
        os.mkdir(tpath)
    dbconfig = SQLConfig(config['dbconfig'], auto_update_paths=True)
    dbfn = os.path.join(tpath,f"{tenant}_sql-db-config.json")
    with open(dbfn,'w') as f:
        f.write(json.dumps(dbconfig.dict_elem(), indent=4))

    defaults = YmlConfig(defaults_path, base_str='default')
    match_config = config['embed_config']
    for k in defaults:
        match_config[k] = config['embed_config'].get(k,defaults[k])
    match_config['dbconfig'] = dbfn
    fn = os.path.join(tpath,f"{tenant}_matching_embed_config.yml")
    with open(fn,'w') as f:
        f.write(yaml.dump(match_config))
    
    return json.dumps({'config_fn': fn, 'final_matching_config': match_config})


@app.post("/build_model")
@version(1, 0)
async def build_model(tenant:str, debug:int=0):    
    result = []
    result.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + 
                  ' Start Train matching model using DB data')
    model_build_task.background_work(tenant_path(tenant),debug)
    if debug:
        result.extend(model_build_task.message)
    result.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + 
                  ' End Train matching model using DB data')
    return {"result": result}


@app.post("/check_model_loaded")
@version(1, 0)
async def check_model_loaded():       
    result = main_embed_call(None, check_model=True)
    return {"loaded": result}    


@app.post("/upload_model")
@version(1, 0)
async def upload_model():       
    result = []
    result.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + 
        ' Start matching Model upload to Azure Gen2 Blob')
    # completed_process = subprocess.run(['python', 'az-rasa-prod.py', '-i', 'rasa/models'], stdout=subprocess.PIPE)
    # result.append(completed_process.stdout.decode('utf-8').splitlines())
    result.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + 
    ' End matching Model upload to Azure Gen2 Blob')
    print('model uploaded')
    return {"result": result}    


@app.post("/find_match")
@version(1, 0)
async def find_match(tenant:str, record:Union[Dict,List,str], n_return:int=10, 
                     thres:float=0.015, update_model:bool=False, debug:int=0):    
    
    result = []
    result.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + 
    ' Start retreive similar records from matching model')
    df = None
    if isinstance(record, Dict):
        df = pd.DataFrame({k: [str(v)] for k, v in record.items()})
    elif isinstance(record,list) and isinstance(record[0],dict):
        keys = set(chain.from_iterable(list(rec.keys()) for rec in record))
        df = pd.DataFrame({k: [rec.get(k,None) for rec in record] for k in keys})
    if df is None:
        assert isinstance(record[0],str), 'for list of non-dict elements, elements should be strings'
        df = record
    debug > 0 and print('data provided as query: \n', df)
    query_results = main_embed_call(tenant_path(tenant),text_or_df=df, 
                                    reload=update_model,
                                    n_return=n_return, thres=thres, 
                                    as_records=True, debug=debug)
    if debug > 1:
        query_results = query_results[0]
    query_results = json.loads(json.dumps(query_results))
    result.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + 
        ' End retreive similar records')
    return {"log": result, 'query_results': query_results}

# @app.post("/matching_model_build")
# @version(1, 0)
# async def matching_model_build(background_tasks: BackgroundTasks):
#     if model_build_task.get_progress():
#         return {"message": "matching Model build in progress. Check status using get_status() matching API"}

#     start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
#     model_build_task.message.append(start_time + 
# ' Started matching Model Build')
#     background_tasks.add_task(model_build_task.background_work)
#     return {"message": "matching Model build started. Check status using get_status() matching API"}

@app.get("/get_status")
@version(1, 0)
def status():
    result = model_build_task.get_status()
    if not model_build_task.get_progress():
        model_build_task.message = []
        return {"message": "matching Model build is not running. Use matching_model_build() API to start build."}     
    return result


app = VersionedFastAPI(
    app=app,
    version_format='{major}.{minor}',
    prefix_format='/v{major}.{minor}',
    description='Matching API allows calls to embedding-based matching tools',
      )

# @app.on_event("startup")
# async def az_hub_schedule():    
#     azplatformconfig.status.append('AZ Event Hub batch receive process started: ' + datetime.now().strftime('%F %T.%f')[:-3])
#     loop = asyncio.get_event_loop()
#     loop.create_task(main_eh_data_collector())

if __name__ == "__main__":
    
    parser = ArgumentParser(description='Run the Matching API')
    parser.add_argument('--host', nargs='?', type=str, default='localhost', #'0.0.0.0',
                        help='the hostname to use in starting the API')
    parser.add_argument('--port', '-p', nargs='?', type=int, default=8000,
                        help='port to use to host the API')
    parser.add_argument('--reload', '-r', nargs='?', const=True, default=False,
                        help='reload the API when the main script is updated')

    # print('args = ', args)
    args = {k:v for k,v in parser.parse_args().__dict__.items()}
    print('starting uvicorn api host')
    print('===== MATCHING API IS RUNNING =====')
    uvicorn.run('app:app', host=args['host'], port=args['port'], reload=args['reload'])
