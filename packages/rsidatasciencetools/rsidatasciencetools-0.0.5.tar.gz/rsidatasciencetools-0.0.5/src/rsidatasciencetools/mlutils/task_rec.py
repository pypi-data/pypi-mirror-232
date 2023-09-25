
import tensorflow as tf
import tensorflow_recommenders as tfrs
from typing import Dict, Text


# TODO: need to add the retrieval model, but this relies on google 'scann' quantized 
# serach/query tool, can't install on a Mac Arm M1/2 (at least not easily), need
# to test on docker linux with appropo python packages

class ElaspsedTimeModel(tf.keras.Model):

  def __init__(self, unique_user_ids, unique_tasks):
    super().__init__()
    embedding_dimension = 32

    # Compute embeddings for users.
    self.user_embeddings = tf.keras.Sequential([
      tf.keras.layers. StringLookup(
        vocabulary=unique_user_ids, mask_token=None),
      tf.keras.layers.Embedding(len(unique_user_ids) + 1, embedding_dimension)
    ])

    # Compute embeddings for tasks.
    self.task_embeddings = tf.keras.Sequential([
      tf.keras.layers.StringLookup(
        vocabulary=unique_tasks, mask_token=None),
      tf.keras.layers.Embedding(len(unique_tasks) + 1, embedding_dimension)
    ])

    # Compute predictions.
    self.time_on_task_predictor = tf.keras.Sequential([
      # Learn multiple dense layers.
      tf.keras.layers.Dense(256, activation="relu"),
      tf.keras.layers.Dropout(0.3),
      tf.keras.layers.Dense(64, activation="relu"),
      tf.keras.layers.Dropout(0.3),
      # Make time-elapsed predictions in the final layer.
      tf.keras.layers.Dense(1)
  ])
    
  def call(self, inputs):

    user_id, movie_title = inputs

    user_embedding = self.user_embeddings(user_id)
    task_embeddings = self.task_embeddings(movie_title)

    return self.time_on_task_predictor(tf.concat([user_embedding, task_embeddings], axis=1))


class BuildTimeOnTaskModel(tfrs.models.Model):

  def __init__(self, elapsed_time_model:ElaspsedTimeModel):
    super().__init__()
    self.tasktime_model: tf.keras.Model = elapsed_time_model
    self.objective: tf.keras.layers.Layer = tfrs.tasks.Ranking(
      loss = tf.keras.losses.MeanSquaredError(),
      metrics=[tf.keras.metrics.RootMeanSquaredError()]
    )

  def call(self, features: Dict[str, tf.Tensor]) -> tf.Tensor:
    return self.tasktime_model(
        (features["lastuser"], features["taskname"]))

  def compute_loss(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
    labels = features.pop("elapsedtime_min")
    
    elapsedtime_predictions = self(features)

    # The task computes the loss and the metrics.
    return self.objective(labels=labels, predictions=elapsedtime_predictions)


def prep_usertask_dataset(df,tf_shuffle_seed=42):
    '''prep the data and massage into tensorflow data'''
    df_input = df[[k for k in df.columns if all(
        kk not in k for kk in ['date', 'days', 'timeframe', 'required', 'background', 'complexity']) and not(isinstance(df[k].iloc[0],list))]].copy()
    df_input['ref_idx'] = df_input.index
    df_input['taskname'] = df.taskname.apply(lambda x: str(x))
    tf.random.set_seed(tf_shuffle_seed)

    dataset = tf.data.Dataset.from_tensor_slices(dict(df_input))
    shuffle = 42
    split, train_size, test_size = True,0.7,0.2
    val_size = 1-train_size-test_size

    DATASET_SIZE = len(dataset)
    full_dataset = (dataset.shuffle(DATASET_SIZE, 
          seed=tf_shuffle_seed, reshuffle_each_iteration=False) 
        if tf_shuffle_seed is not None and not(isinstance(tf_shuffle_seed,bool) and not(tf_shuffle_seed)) 
        else dataset)
    if split:
        train_size = int(train_size * DATASET_SIZE)
        val_size = int(test_size * DATASET_SIZE)
        test_size = int(val_size * DATASET_SIZE)
        
        train = full_dataset.take(train_size)
        test_dataset = full_dataset.skip(train_size)
        test = test_dataset.take(test_size)
        val = test_dataset.skip(test_size)
    
    unique_tasks = df.taskname.unique()
    unique_user_ids = df.lastuser.unique()

    lastuser_role = {user: df[df.lastuser == user].lastuserrole.iloc[0] for user in unique_user_ids}

    print(f'unique users / tasks: {df.lastuser.unique().shape} / {df.taskname.unique().shape}')
    return df, full_dataset, train, test, val, unique_tasks, unique_user_ids