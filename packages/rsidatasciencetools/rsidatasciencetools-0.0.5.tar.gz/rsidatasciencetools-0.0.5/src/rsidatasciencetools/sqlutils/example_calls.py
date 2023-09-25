'''quick reference for example calls use pandas, sqlalchemy, and util_sqlalchemy (local module)'''
import sqlalchemy as sql
import pandas as pd
from config_connection import dbgen_dk_ccfraud, dbgen_dk_census
from .sql_connect import gettypes

# see `config_connection` for example of calls `DbConnectGenerator` to get connection 
# generator instantiated

def example1():
    '''1) use pandas `read_sql` command'''
    with dbgen_dk_ccfraud.gen_connection() as conn:
        datadf = pd.read_sql(('SELECT transactionId, Amount, Class FROM ccdata '
                            'WHERE Amount > 100 AND Class = 1'), 
            conn.connection)
    print(datadf.shape)
    print(datadf.head(3))

def example2(call=1):
    with dbgen_dk_ccfraud.gen_connection() as conn:
        tbl = conn.get_table('ccdata')
        if call == 1:
            # call 1.
            data = conn.execute_query(sql.select([tbl]))
        elif call == 2:
            # call 2.
            data = conn.execute_query(sql.select([tbl]).where(tbl.columns.Class == 1))
            # example call 3.
            data = conn.execute_query(
                sql.select([
                    tbl.columns.transactionId,
                    tbl.columns.Class,
                    tbl.columns.Time,
                    tbl.columns.Amount
                ]).where(tbl.columns.Class == 1))
    # view the retrieved data:
    print(data.shape)
    print(data.head(3))

def example3():
    with dbgen_dk_census.gen_connection() as conn:
        print(conn.table_names())
        tbl = conn.get_table('census')
        data = conn.execute_query(sql.select([tbl])) # .where(tbl.columns.age==0))
    print(data.head())

def example4():
    with dbgen_dk_census.gen_connection() as conn:
        tbl = conn.get_table('census')
        print([c.name for c in tbl.columns])
        data = conn.execute_query(sql.select([tbl.columns.state,
                sql.func.sum(tbl.columns.pop2008).label('pop2008'),
            sql.func.sum(tbl.columns.pop2000).label('pop2000')                                 
            ]).order_by(
            tbl.columns.state).group_by(tbl.columns.state))
    #     data = conn.execute_query(sql.select([tbl]).where(
    #         tbl.columns.sex == 'M'))
    #         sql.and_(tbl.columns.sex == 'M', tbl.columns.pop2000 > 70000)))
    print(data.shape)
    print(data.head(3))

def example5():
    with dbgen_dk_census.gen_connection() as conn:
        tbls = conn.get_table(['census', 'state_fact'])
        print([c.name for c in tbls[0].columns])

        # only way to join tables without pre-existing foreign keys is to use 
        # standard labels inline views within full syntax capability - need to 
        # figure out why join fails when SELECT for 1st table specifies
        # columns
        data = pd.read_sql((
                'SELECT * FROM state_fact JOIN ('
                'SELECT state, SUM(pop2000) AS p2000, SUM(pop2008) AS p2008 '
                "FROM census GROUP BY state) AS popSum ON state_fact.name = popSum.state"),
            conn.connection)

    print(data.shape)
    print(data.head())

def example6(df, upload=False):
    '''upload directly from pandas dataframe - append column types as input option'''

    if upload:
        with dbgen_dk_ccfraud.gen_connection() as conn:
            df.to_sql(name='ccdata', con=conn.engine, 
                    if_exists='append', # 'replace'
                    index=False, dtype=gettypes(df))