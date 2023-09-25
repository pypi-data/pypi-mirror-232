'''example sql db connection generator object setup'''
from .sql_connect import DbConnectGenerator
# from .sqlconfig import SQLConfig

# specify database configurations
config = {
    'dialect_driver': 'mysql+pymysql',
    'host': 'localhost',
    'port': 6603,
    'user': 'auditor',
    'password': 'auditorpw',
    'database': 'ccfraud'
}

# specify connection string
hasPW = (':'+config["password"] 
    if config["password"] is not None and len(config["password"]) else '')
connection_str = (f'mysql+pymysql://{config["user"]}'
    f'{hasPW}@{config["host"]}:{config["port"]}/'
    f'{config["database"]}') # connect to database

# engine_fraud = sql.create_engine(connection_str)
# connection_fraud = engine.connect()# pull metadata of a table

# metadata_fraud = sql.MetaData(bind=engine_fraud)
# metadata.reflect(only=['ccdata'])

# connect to SQLite file/DB
dbgen_local_census = DbConnectGenerator('sqlite:///census.sqlite')

# remote host/port connect (simulated via Docker container running mySQL-server)
dbgen_dk_ccfraud = DbConnectGenerator(**config)

dbgen_dk_census = DbConnectGenerator(
    dialect_driver='mysql+pymysql',
    host='localhost',
    port=6603,
    user='worker',
    password='workerpw',
    database='census')