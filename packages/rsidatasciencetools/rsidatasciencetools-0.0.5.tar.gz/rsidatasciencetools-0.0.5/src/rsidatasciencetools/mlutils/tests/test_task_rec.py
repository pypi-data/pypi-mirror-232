
import pandas as pd
import numpy as np
import os
import pprint
import tempfile
from matplotlib import pyplot as plt

import tensorflow as tf

from rsidatasciencetools.datautils.clean import fix_lists
from rsidatasciencetools.sqlutils.sqlconfig import SQLConfig
from rsidatasciencetools.sqlutils.sql_connect import DbConnectGenerator
from rsidatasciencetools.datautils.workflows import taskuser_datagen
from rsidatasciencetools.mlutils.task_rec import ElaspsedTimeModel, BuildTimeOnTaskModel, prep_usertask_dataset

data_config_dir = os.path.join(os.path.dirname(os.path.realpath(taskuser_datagen.__file__)),'tests')

def test_usertask_ranking():
    df, yml = taskuser_datagen.gen_records_from_data(
            data_config_dir, debug=2, numrec=1000, as_df=True,
            write_to_db=False, overwrite=False, add_unique_label=False,
            seed=43, display=False)
    print(f'generated data: {df.shape}, {df.columns}:\n\n{df.head(3)}')

    for k in ['usermodlist','updatedatetime']:
        df[k] = df[k].apply(lambda x: fix_lists(x,try_datetimes='datetime' in k))
    print('datase: unique tasks / total records:', df.taskname.unique().shape,df.shape[0])

    df, full_dataset, train, test, val, unique_tasks, unique_user_ids = prep_usertask_dataset(df)

    # lastuser_role = {user: df[df.lastuser == user].lastuserrole.iloc[0] for user in unique_user_ids}

    elapsed_time_model = ElaspsedTimeModel(unique_user_ids, unique_tasks)

    model = BuildTimeOnTaskModel(elapsed_time_model)
    model.compile(optimizer=tf.keras.optimizers.legacy.Adagrad(learning_rate=0.1))

    cached_train = train.shuffle(8_000).batch(1024).cache()
    cached_test = test.batch(256).cache()

    def get_callbacks(name):
        return [
            # tfdocs.modeling.EpochDots(),
            # tf.keras.callbacks.EarlyStopping(monitor='val_binary_crossentropy', patience=200),
            # tf.keras.callbacks.TensorBoard(os.path.join(logdir,name))
        ]
    history = model.fit(
        cached_train,
        # steps_per_epoch = 2,
        epochs=5,
        callbacks=get_callbacks('tasktime'))

    # model.fit(cached_train, epochs=3)
    print(model.tasktime_model.summary())
    print(model.evaluate(cached_test, return_dict=True))

