'''collect baseline query data'''
import pandas as pd
import numpy as np
import os
# from pprint import pprint
import pymysql
from sqlutils import util, sqlconfig
from mlutils.corp_tax_audit_features import get_query_lut

try:
    from tqdm import tqdm 
except ImportError:
    tqdm = None

def print_info_from_baseline_queries(write_to_file=False):
    # unq_cols = set()
    data_loc = '/home/dtladmin/Work/projects/SEA-audit'
    # labels = pd.read_csv(os.path.join(data_loc,'SEA-audit-labeled-cit-cleaned.csv'))

    qfiles_d = get_query_lut()
    db = util.DbConnectGenerator(config=sqlconfig.SQLConfig(data_loc))
    # print(db.connection_str)
    with db.gen_connection() as conn:
        for qf in qfiles_d.values():
            print(qf)
            try:
                with open(qf,'r') as qfile:
                    data = pd.read_sql((qfile.read()),
                        conn.connection)
                printinfo = (f'    > number of records: {data.shape}, unique business ids: {len(data.business_id.unique())} ')
                periods = []
                if 'obl_year' in data.columns:
                    periods.append('obl_year')
                if 'obl_period' in data.columns:
                    periods.append('obl_period')
                if len(periods):
                    yqs = [d for g,d in data.groupby(by=periods)]
                    printinfo += (f', unique year/quarters: {len(yqs)}')
                outf = os.path.join(data_loc, qf.split('.sql')[0] + '.csv.fpq')
                if write_to_file:
                    data.to_parquet(outf,index=False,compression='brotli')
                    printinfo += (f'\n      (compressed csv file size: {os.path.getsize(outf)/float(2**20):6.3f} MB)')
                print(printinfo)
                # unq_cols.update(data.columns.tolist())

            except (pymysql.ProgrammingError, pymysql.OperationalError, pymysql.DatabaseError) as dbe:
                print('   >>> DB error' + str(dbe))

    return