import pandas as pd
import numpy as np
import os

from rsidatasciencetools.datautils.workflows.taskuser_datagen import gen_records_from_data
from rsidatasciencetools.datautils.workflows.taskuser_datagen import (TaskDatabase, UserSource, TenureSource, 
                                       RoleSource, NameSource)
from rsidatasciencetools.datautils.clean import fix_lists
from rsidatasciencetools.config.baseconfig import YmlConfig


def test_workflow_tasks_datagen():
    data_config_dir = os.path.dirname(__file__)

    df, yml = gen_records_from_data(data_config_dir, debug=0, numrec=10, as_df=True,
            write_to_db=False, overwrite=False, add_unique_label=False,
            seed=42, display=False)
    assert isinstance(yml, YmlConfig)

    test_output = os.path.join(data_config_dir,'test_workflow_tasks_output.seed42.temp')
    ref_output = os.path.join(data_config_dir,'test_workflow_tasks_output.seed42.csv')
    df.to_csv(test_output, index=False)
    
    df_test = pd.read_csv(test_output)
    df_ref = pd.read_csv(ref_output)
    
    try:
        os.remove(test_output)
    except FileNotFoundError:
        pass

    non_time_keys = [k for k in df_ref.columns if 'datetime' not in k]
    time_keys = [k for k in df_ref.columns if 'datetime' in k and 'update' not in k]
    for tk in time_keys:    
        df_ref[tk] = df_ref[tk].apply(lambda x: pd.Timestamp(x).timestamp())
        df_test[tk] = df_test[tk].apply(lambda x: pd.Timestamp(x).timestamp())

    df_ref['updatedatetime'] = df_ref['updatedatetime'].apply(lambda x: [pd.Timestamp(y).timestamp() 
                                                                        for y in fix_lists(x)])
    df_test['updatedatetime'] = df_test['updatedatetime'].apply(lambda x: [pd.Timestamp(y).timestamp() 
                                                                        for y in fix_lists(x)])

    assert all((df_ref[non_time_keys] == df_test[non_time_keys]).all())
    
    # assert all([np.isclose(df_ref[tk].values, df_test[tk].values).all() for tk in time_keys])
    # assert all([np.isclose(ref, test).all() 
    #                  for ref,test in zip(df_ref['updatedatetime'],df_test['updatedatetime'])])