'''A few homebrew speed-ups for implementing SQL Alchemy -based querying/insertion'''
import pandas as pd
# from debugpy import connect
import numpy as np
import os
# from matplotlib import pyplot as plt
# import pickle as pkl
from warnings import warn
import sqlalchemy as sql
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
# import pyodbc
from .sqlconfig import SQLConfig
from rsidatasciencetools.config.baseconfig import log_level_dict

import logging
from rsidatasciencetools.azureutils import az_logging

logger = az_logging.get_az_logger(__name__)


'''
Example calls:
    with dbgen.gen_connection() as conn:
        datadf = pd.read_sql(('SELECT transactionId, Amount, Class FROM ccdata '
                            'WHERE Amount > 100 AND Class = 1'), 
            conn.connection)
    print(datadf.shape)
    datadf.head()
'''

def gettypes(_df):
    d = {}
    logger.info('Dataframe auto-types: ' + str((k, val_type, type(val_type)) 
        for k,val_type in zip(_df.dtypes.index,_df.dtypes)))

    for k,val_type in zip(_df.dtypes.index,_df.dtypes):
        converts2flt = converts2int = False
        try:
            converts2flt = all([isinstance(float(v),float) for v in _df[k].values])
        except ValueError:
            pass
        if converts2flt:
            try:
                converts2int = all([isinstance(int(v),int) for v in _df[k].values])
            except ValueError:
                pass
        if ('object' in str(val_type)) and not(converts2flt):
            maxlen = _df[k].str.len().max()
            d[k] = sql.types.VARCHAR(10 if maxlen == 0 else int(maxlen*1.5))
        elif ('float' in str(val_type)) or (converts2flt and not(converts2int)):
            d[k] = sql.types.FLOAT(126)
        elif ('int' in str(val_type)) or converts2int:
            d[k] = sql.types.INTEGER()
        else:
            raise Exception(f'unknown handling of input type: {val_type}')
    return d

class ConnectCommand(object):
    def __init__(self,engine,meta,conn,parent=None):
        self.engine = engine
        self.meta = meta
        self.connection = conn
        self.parent_context = parent

    def close(self):
        if self.connection is not None:
            try:
                self.connection.close()
                self.connection = None
            except:
                pass

    def connect(self, new=False):
        if (self.connection is None) or new:
            self.connection = self.engine.connect() # pull metadata of a table

    def execute_query(self,query,values=None):
        ''' form query with one of below
                sql.select([<sql table object>])
                sql.insert([<sql table object>]).values(col0=val0,col1=val1,...)
                sql.update([<sql table object>]).values(attribute = new_value)
                sql.delete([<sql table object>])
            
            optionally adding 
                .where(condition)
                
            with 'insert' of many records, must provide secondary argument 
            to pass records along with query 'insert' method, i.e., as 
                execute(sql.insert(tbl), values_list)
            where
                values_list = [dict(col0=val0,col1=val1,...),dict(),...]


        '''
        ResultConn = self.connection.execute(query)
        ResultSet = None
        if True:
            # standard fetch execution
            ResultSet = ResultConn.fetchall()
        else:
            # better for large datasets
            flag = True
            while flag:
                partial_results = ResultConn.fetchmany(50)
                if(partial_results == []): 
                    flag = False

        # close query connection
        ResultConn.close()

        # convert SQL data query result to dataframe
        if ResultSet is None:
            return
        if sql.insert.__name__ != query.__class__.__name__ and 'selected_columns' in query.__dict__:
            return pd.DataFrame(ResultSet, columns=[c.name for c in query.selected_columns])

    def drop_table(self,table):
        tbl = self.get_table(table)
        return tbl.drop(self.engine)
    
    def drop_all_tables(self):
        return self.meta.drop_all(self.engine)
    
    def get_table(self,table):
        if isinstance(table,list):
            tbls = []
            for tbl in table:
                tbls.append(self.get_table(tbl))
            return tbls
        else:
            return sql.Table(table, self.meta, autoload=True, autoload_with=self.engine)

    def list_tables(self):
        return self.table_names()
            
    def list_collections(self):
        return self.table_names()

    def table_names(self):
        insp = sql.inspect(self.engine)
        return insp.get_table_names()
        
    def table_names_from_meta(self):
        return [t.name for t in self.meta.sorted_tables]
    
    def columns(self,table):
        tbl = sql.Table(table, self.meta, autoload=True, autoload_with=self.engine)
        return [c.name for c in tbl.columns]
    
    def insert_into_table(self,values,table):
        ''' this one is better for existing tables with complex/unique data types
            (the implicit types will be interpreted into the correct type)
        '''
        if isinstance(values,pd.DataFrame):
            ddata = values.to_dict()
            row_indices = list(list(ddata.values())[0].keys())
            recs = []
            for row in row_indices:
                recs.append({k:v[row] for k,v in ddata.items()})
            values = recs
        elif isinstance(values,dict):
            values = [values]
        elif isinstance(values,list):
            if len(values) == 0:
                return
            elif ~isinstance(values[0],dict):
                raise NotImplementedError(f'list element type "{type(values[0])}" not handled')
        else:
            raise NotImplementedError(f'values type "{type(values)}" not handled')
        _table = self.get_table(table)

        return self.connection.execute(_table.insert(),values)


    def upload_df_to_table(self, df, tablename, if_exists='append', index=False, 
            auto_type=True, dtypes=None, debug=0):
        ''' this one is better for creating/appending tables with no existing data 
            or having only simple data types
        '''
        if dtypes is None:
            if auto_type:
                coltypes = None
            else:
                coltypes = gettypes(df)
        else:
            coltypes = dtypes
        debug and logger.warning(f'\nCol types: {coltypes}')
        df.to_sql(name=tablename, con=self.engine, 
          if_exists=if_exists, # 'replace' / 'append'
          index=index, dtype=coltypes)
    
class ContextConnect(object):
    '''ContextConnect
    
        Usage: 
            with conn:
                <do pandas sql stuff>
        OR
            cmd = conn()
    '''
    def __init__(self,engine,meta):
        self.engine = engine
        self.meta = meta
        self.open = False
        self.connection = None
        self.open_commands = []

    def connect(self, new=False):
        if not(self.open) or new:
            self.open = True
            self.connection = self.engine.connect() # pull metadata of a table

    def close(self):
        if self.open and self.connection is not None:
            self.connection.close()
            self.connection = None
        self.open = False

    def close_all(self):
        for cmd in self.open_commands:
            if cmd.connection is not None:
                cmd.connection.close()
                cmd.connection = None
        self.open_commands = []

    def __call__(self,new=False) -> ConnectCommand:
        self.connect(new)
        cmd = ConnectCommand(self.engine, self.meta, self.connection, parent=self)
        if not(any(conn == cmd.connection for conn in self.open_commands)):
            self.open_commands.append(cmd)
        return cmd
       
    def __enter__(self):
        self.connect()
        return ConnectCommand(self.engine, self.meta, self.connection)
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()
        if exc_type is not None:
            raise exc_type.with_traceback(exc_value, exc_traceback)
    
class DbConnectGenerator(object):
    '''
    Class for connecting to, reading and writing data from/to SQL-like databases
    '''
    def __init__(self, *args, config=None, debug=0, **connect_config):
        self.debug = debug
        logger.setLevel(az_logging.log_level_dict[self.debug])
        if isinstance(config, SQLConfig):
            self._config = config
            self._config.setkeyvalue(connect_config)
        elif (isinstance(connect_config,dict) and len(connect_config)) or (
                isinstance(config,dict) and len(config)):
            if (isinstance(config,dict) and len(config)):
                _connect_config = config
                _connect_config.update(connect_config)
                connect_config = _connect_config
            assert all([k in connect_config for k in [
                'dialect_driver','user','password','port']]), (
                'insufficient data in connect config dict')
            self._config = SQLConfig(error_no_file_found=False, **connect_config)
        elif not(args or config or connect_config):
            warn('no input credentials, empty connector')
            return None
        else:
            connect_url = args[0]
            assert isinstance(connect_url,str), (
                'cannot connect with data provided as '
                f'type: {type(connect_url)}; use dict or str')
            connect_config = self.get_sql_config_elements(connect_url, todict=True)
            self._config = SQLConfig(error_no_file_found=False, 
                **connect_config, debug=max(0,self.debug-1))
        # database connection url
        self.engine = sql.create_engine(self._config.get_conn_str())
        if self._config.get('localfile',False) and not(
                database_exists(self.connection_str_method(
                obfuscate=False, nodb=True))):
            Base = declarative_base()
            Base.metadata.create_all(self.engine)
            # create_database(self._config.get_conn_str())
        logger.debug('engine connection:', self.engine)
        self.meta = sql.MetaData(bind=self.engine)

    def __repr__(self):
        return self.__class__.__name__ + ': ' + self.connection_str
    
    def get_sql_config_elements(self, _connection_str, todict=False, **update):

        islocalfile = '////' in _connection_str
        params = {}
        escape_pw = False
        if not(islocalfile):
            elements = _connection_str.split('@')
            num_ATs = len(elements) - 1
            escape_pw = num_ATs > 1
            front, host_db = ''.join(elements[0:num_ATs]), ''.join(elements[num_ATs:])
            dialect, userpw = front.split('//')
            user, pw = (None, None if islocalfile else userpw.split(':'))
            if '?' in host_db:
                split_qm = host_db.split('?')
                host_db, _params = split_qm[0], split_qm[1:]
                for param in _params:
                    try:
                        k, v = param.split('=')
                    except ValueError:
                        k, v = param, None
                    params['param_' + k] = v
            host, portdb = host_db.split(':')
            if '/' in portdb:
                port, db = portdb.split('/')
            else:
                port, db = portdb, None
        else:
            dialect, host = _connection_str.split('////')
            user, pw, port, db = tuple([None]*4)
        if todict or len(update):
            outkeys = ['dialect_driver', 'user', 'password', 
                       'host', 'port', 'database']
            dictout = {k: v
                    for k, v in zip(outkeys,[dialect, user, pw, host, port, db]) 
                    if v is not None}
            if islocalfile:
                dictout.update({'localfile': True})
            dictout.update(params)
            if todict:
                return dictout
            else:
                dictout.update(update)
                outlist = [dictout[k] for k in outkeys]
                outlist.append(params)
                return tuple(outlist)
        else:
            if escape_pw:
                pw = pw.replace('@', '%40')
            return dialect, user, pw, host, port, db, islocalfile, params

    @property
    def connection_str(self):
        return self.connection_str_method(obfuscate=True)

    def connection_str_method(self, obfuscate=True, nodb=False, **update):
        # obfuscate the PW
        if nodb:
            update.update({'database': None})
        return self._config.get_conn_str(update, obfuscate=obfuscate)

    def list_schemas(self):
        insp = sql.inspect(self.engine)
        return insp.get_schema_names()

    def list_dbs(self, schema='sys', as_dataframe=False):
        with self.gen_connection(nodb=True) as conn:
            df = pd.read_sql(
                f'''
                SELECT name{(', database_id, create_date' if as_dataframe else '')}  
                FROM {schema}.databases;  
                ''', con=conn.connection)
        if as_dataframe:
            return df
        else:
            return df.name.values.tolist()

    def gen_connection(self, db=None, create_nonexist=False, nodb=False):
        if nodb:
            return ContextConnect(sql.create_engine(self.connection_str_method(
                obfuscate=False, nodb=True)), sql.MetaData(bind=self.engine))
        elif db:
            engine = sql.create_engine(self.connection_str_method(
                obfuscate=False, database=db))
            if not(database_exists(engine.url)):
                if create_nonexist:
                    create_database(engine.url)
                    engine = sql.create_engine(self.connection_str_method(
                        obfuscate=False, database=db))
                else:
                    raise sql.exc.DatabaseError(f'Database url "{engine.url}" does not exist')
            return ContextConnect(engine, sql.MetaData(bind=self.engine))
        else:
            return ContextConnect(self.engine, self.meta)

    @staticmethod
    def execute_query(query, conn):
        '''functional execution of queries with SQLAlchemy - requires connection object'''
        ResultConn = conn.execute(query)
        ResultSet = None
        if True:
            # standard fetch execution
            ResultSet = ResultConn.fetchall()
        else:
            # better for large datasets
            while flag:
                partial_results = ResultConn.fetchmany(50)
                if(partial_results == []): 
                    flag = False

        # close query connection
        ResultConn.close()

        # convert SQL data query result to dataframe
        if ResultSet is None:
            return
        logger.info(f'query return data: {query.__dict__}')
        return pd.DataFrame(ResultSet, columns=[c.name for c in query.selected_columns])