import pandas as pd
import numpy as np
from rsidatasciencetools.datautils.datagen import gen_records_from_data, Source, Record, random_datetimes
from os import path, remove


df, yml = gen_records_from_data(path.dirname(__file__), numrec=10, seed=42, as_df=True)

df.to_csv('./temp.csv',index=False)
df = pd.read_csv('./temp.csv')
remove('./temp.csv')

check = pd.read_csv(path.join(path.dirname(__file__),'test_output_seed42.csv'))
# assert (df == check).all().all()   # doesn't work for Nan vs. None


def test_gen_results_0(idx=0):
    for col in df.columns:
        for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
            assert ((isinstance(v1,float) and np.isnan(v1) and 
                    isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
                f"row[{idx}] for column: {col}: {v1} != {v2}")


def test_gen_results_1(idx=1):
    for col in df.columns:
        for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
            assert ((isinstance(v1,float) and np.isnan(v1) and 
                    isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
                f"row[{idx}] for column: {col}: {v1} != {v2}")


def test_gen_results_2(idx=2):
    for col in df.columns:
        for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
            assert ((isinstance(v1,float) and np.isnan(v1) and 
                    isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
                f"row[{idx}] for column: {col}: {v1} != {v2}")


def test_gen_results_3(idx=3):
    for col in df.columns:
        for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
            assert ((isinstance(v1,float) and np.isnan(v1) and 
                    isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
                f"row[{idx}] for column: {col}: {v1} != {v2}")


def test_gen_results_4(idx=4):
    for col in df.columns:
        for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
            assert ((isinstance(v1,float) and np.isnan(v1) and 
                    isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
                f"row[{idx}] for column: {col}: {v1} != {v2}")


def test_gen_results_5(idx=5):
    for col in df.columns:
        for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
            assert ((isinstance(v1,float) and np.isnan(v1) and 
                    isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
                f"row[{idx}] for column: {col}: {v1} != {v2}")


def test_gen_results_6(idx=6):
    for col in df.columns:
        for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
            assert ((isinstance(v1,float) and np.isnan(v1) and 
                    isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
                f"row[{idx}] for column: {col}: {v1} != {v2}")


# def test_gen_results_7(idx=7):
#     for col in df.columns:
#         for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
#             assert ((isinstance(v1,float) and np.isnan(v1) and 
#                     isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
#                 f"row[{idx}] for column: {col}: {v1} != {v2}")


def test_gen_results_8(idx=8):
    for col in df.columns:
        for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
            assert ((isinstance(v1,float) and np.isnan(v1) and 
                    isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
                f"row[{idx}] for column: {col}: {v1} != {v2}")


def test_gen_results_9(idx=9):
    for col in df.columns:
        for i,v1,v2 in zip(range(df.shape[0]),df[col].iloc[idx:idx+1].values.tolist(), check[col].iloc[idx:idx+1].values.tolist()):
            assert ((isinstance(v1,float) and np.isnan(v1) and 
                    isinstance(v2,float) and np.isnan(v2)) or v1==v2 or col=='birthday'), (
                f"row[{idx}] for column: {col}: {v1} != {v2}")


def test_random_datetimes():
    start, end = pd.Timestamp.now() - pd.Timedelta(days=1), pd.Timestamp.now()
    dts = random_datetimes(start, end, out_format='datetime', rng=None, n=10)

    assert ((start < dts) & (dts < end)).all()
    
     
def test_Source():
    src = Source('./md_cities_clean_validzip.csv')
    s = '''Source src:./md_cities_clean_validzip.csv
   distribution: None()
   data: '''
    assert s == repr(src)
    
    
def test_Record():
    recs = [
        dict(taxpayertype='individual', firstname='James', lastname='Smith', middlename='Timothy', 
             ethnicity='white', maidenname=None, birthday='1998', taxid=123456789, 
             compositeaddress='123 Main St, Anytown, NY 12345', streetno=123, aptno=None, 
             streetname='Main St', city='Anytown', zipcode=12345, state='NY'),
        dict(taxpayertype='individual', firstname='Jane', lastname='Smith', middlename='Helen', 
             ethnicity='white', maidenname='Johnson', birthday='1997', taxid=234567891, 
             compositeaddress='123 Main St, Anytown, NY 12345', streetno=123, aptno=None, 
             streetname='Main St', city='Anytown', zipcode=12345, state='NY')
    ]
    df = Record.as_dataframe(recs)
    Records = Record.from_dataframe(df)
    Records[0].update(dict(phoneno=1201413445))
    # print('Record: ', Records[0])
    recs[0].update(dict(phoneno=1201413445))
    # print('dict rec: ', recs[0])
    # assert Records == [Record(**r) for r in recs]
    assert [r.items() for r in Records] == recs
    
    for k,v in Records[0].iteritems():
        if k == 'firstname':
            assert v in ('James', 'Jane')
            break
        
    for k in Records[0]:
        if k == 'lastname':
            assert Records[0][k] == 'Smith'
            break
    
    
    