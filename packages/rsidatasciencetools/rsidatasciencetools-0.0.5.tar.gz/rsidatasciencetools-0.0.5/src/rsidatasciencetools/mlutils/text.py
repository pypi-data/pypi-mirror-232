'''utilties for managing and processes textual data from SQL stores into DataFrames and TF.Dataset'''

from typing import Union, List, Callable
from warnings import warn
import numpy as np
import pandas as pd
import datetime as dt
import pandas as pd

from rsidatasciencetools.sqlutils.sqlconfig import SQLConfig
from rsidatasciencetools.sqlutils.sql_connect import DbConnectGenerator
from rsidatasciencetools.config.baseconfig import YmlConfig

import logging
from rsidatasciencetools.azureutils import az_logging

logger = az_logging.get_az_logger(__name__)


def get_text_data_from_records(yml:Union[YmlConfig,str], in_df:pd.DataFrame=None, as_df:bool=True, 
        preprocess:Callable=lambda x: x.replace(';','').replace('-',' ').replace(
                                '"',' ').replace('#', 'apt ').lower(),
        merge_fields:List[str]=None, train_size:float=0.8, test_size:float=0.1, val_size:float=0.1, 
        split:bool=True, shuffle:int=42, debug:int=1):
    ''' Extract usable text data for matching purposes from SQL-like records '''
    if not(isinstance(yml,YmlConfig)):
        yml = YmlConfig(yml, auto_update_paths=True)
    assert np.isclose(1.0,sum([train_size, test_size, val_size])), (
        'train, test, and validation set size fractions do not sum to 1.0')
    if in_df is None:
        sqlcfg = SQLConfig(yml['dbconfig'],debug=debug,auto_update_paths=True)
        db = DbConnectGenerator(config=sqlcfg)
        logger.info(repr(yml) + repr(sqlcfg) + repr(db))

        with db.gen_connection() as conn:
            in_df = pd.read_sql(sqlcfg['reftable'],con=conn.connection)
    else:
        in_df = in_df.copy()
        logger.debug('skipping DB access, using provided data')

    merge_fields = (['compositename', 'maidenname', 'birthday', 'birthmonth', 
            'taxid', 'compositeaddress', 'email', 'phoneno'] 
        if merge_fields is None and ('merge_fields' not in yml) else (
            merge_fields if merge_fields is not None else yml['merge_fields']))
    
    if 'birthmonth' in merge_fields:
        in_df['birthmonth'] = in_df.birthday.apply(lambda x: x.month_name())
    if not(isinstance(in_df.birthday[0], (np.datetime64, pd.Timestamp, dt.datetime))):
        assert isinstance(in_df.birthday[0], str), "birthday is not string or datetime type"
        in_df['birthday'] = in_df.birthday.apply(lambda x: pd.Timestamp(x))
    in_df['birthday'] = in_df.birthday.apply(
        lambda x: f'{x.year}-{x.month:02d}-{x.day:02d}')
    for int_field in [mf for mf in merge_fields if mf in ['taxid', 'phoneno']]:
         in_df[int_field] = in_df[int_field].apply(lambda x: int(x))

    assert all(k in in_df.columns for k in merge_fields), ('imported SQL or '
        'passed data does not contain all required record fields (req: '
        f'{merge_fields}, contains: {list(in_df.columns)})')

    for_df = dict(sentence_data=[
        ("; ".join([str(el) for el in d.values.tolist() if el is not None and not(
            isinstance(el, (int,float)) and np.isnan(el))
        ])).lower()
        for i, d in in_df[merge_fields].iterrows()])
    if 'metric_id' in in_df:
        for_df.update(dict(metric_id=in_df.metric_id.values))
    else:
        for_df.update(dict(taxid=in_df.taxid.values))
    sentence_inputs = pd.DataFrame(for_df)

    if preprocess is not None:
        sentence_inputs['sentence_data'] = sentence_inputs.sentence_data.apply(preprocess)

    train_examples = val_examples = test_examples = None
    if as_df:
        DATASET_SIZE = len(sentence_inputs)
        if DATASET_SIZE == 1:
            return sentence_inputs
        if not(split):
            return yml, DATASET_SIZE, full_dataset, train_examples, val_examples, test_examples
        train_size = int(train_size * DATASET_SIZE)
        val_size = int(test_size * DATASET_SIZE)
        test_size = int(val_size * DATASET_SIZE)
        if shuffle is not None and not(isinstance(shuffle,bool) and not(shuffle)):
            full_dataset = sentence_inputs.sample(
                frac=1,replace=False,random_state=int(shuffle)).reset_index(drop=True)
        else:
            full_dataset = sentence_inputs
        train_examples = full_dataset.loc[:train_size].copy() if train_size > 0 else pd.DataFrame({})
        test_examples = (full_dataset.loc[train_size:(train_size+test_size)].copy() 
            if test_size > 0 else pd.DataFrame({}))
        val_examples = full_dataset.loc[(train_size+test_size):].copy() if val_size > 0 else pd.DataFrame({})
        return yml, DATASET_SIZE, full_dataset, train_examples, val_examples, test_examples

    try:
        import tensorflow as tf
    except ImportError as ie:
        warn('unable to load tensorflow library needed for data set manipulation')
        raise(ie)

    dataset = tf.data.Dataset.from_tensor_slices(sentence_inputs.sentence_data)
    DATASET_SIZE = len(dataset)
    full_dataset = (dataset.shuffle(DATASET_SIZE, seed=shuffle) 
        if shuffle is not None and not(isinstance(shuffle,bool) and not(shuffle)) 
        else dataset)
    if not(split):
        return yml, DATASET_SIZE, full_dataset, train_examples, val_examples, test_examples
    train_size = int(train_size * DATASET_SIZE)
    val_size = int(test_size * DATASET_SIZE)
    test_size = int(val_size * DATASET_SIZE)

    train_examples = full_dataset.take(train_size)
    test_dataset = full_dataset.skip(train_size)
    test_examples = test_dataset.take(test_size)
    val_examples = test_dataset.skip(test_size)
    return yml, DATASET_SIZE, full_dataset, train_examples, val_examples, test_examples
