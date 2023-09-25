
from os import path, remove
import pandas as pd
import numpy as np
from copy import deepcopy

from rsidatasciencetools.sqlutils.sql_connect import DbConnectGenerator
from rsidatasciencetools.sqlutils.sqlconfig import SQLConfig

def test_db_connector():
    fdir = path.dirname(path.abspath(__file__))
    cfg_check = SQLConfig(fdir, auto_update_paths=True)
    # print(cfg_check)
    rng = np.random.RandomState(seed=42)
    
    test_df = pd.DataFrame({
        'designation': [k for k in 'abcde'],
        'number': np.round(rng.normal(size=5),3).tolist()})

    cfg = deepcopy(cfg_check)
    cfg.setkeyvalue('host', path.join(fdir,'sql-test-db.sqlite3'))
    db = DbConnectGenerator(config=cfg)
    db_check = DbConnectGenerator(config=cfg_check)
    # print(db_check)
    with db_check.gen_connection() as conn:
        tables = conn.table_names()
    assert tables == ['designations_table']
    
    with db_check.gen_connection() as conn:
        data = pd.read_sql(f"select * from {cfg_check['table']} limit 2", con=conn.connection)
    # print('data\n',data)
    # check = pd.DataFrame({'designation':['a', 'b'],'number':[0.497, -0.138]})
    # print('check\n',check)
    assert (data.values == test_df.iloc[0:2].values).all().all()
    
    path.exists(cfg['host']) and remove(cfg['host'])
    # with db_check.gen_connection() as conn:    
    with db.gen_connection() as conn:
        test_df.to_sql(cfg['table'], con=conn.connection, index=False)

    with db.gen_connection() as conn:
        retreive_test = pd.read_sql(cfg['table'], con=conn.connection)

    # with open(cfg['host'],'rb') as fin0:
    #     bin_db = fin0.read()
        
    # with open(cfg_check['host'],'rb') as fin1:
    #     bin_db_ck = fin1.read()

    # assert bin_db == bin_db_ck  # doesn't work because of OS dependent changes in sqlite3 format
    assert (test_df.values == retreive_test).all().all()

    remove(cfg['host'])