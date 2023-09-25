#=====base imports
from azureml import core
import mlflow
import os
from warnings import warn
from time import time
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
try:
    from sklearnex import patch_sklearn
    patch_sklearn() 
except:
    warn('unable to import sklearn intel ex module for speed-ups')
# classification metrics
from sklearn.metrics import (roc_curve, log_loss, roc_auc_score, 
    accuracy_score, precision_score, recall_score)
# clustering metrics
from sklearn.metrics import (adjusted_mutual_info_score, 
    adjusted_rand_score, completeness_score, 
    fowlkes_mallows_score, homogeneity_score, mutual_info_score, 
    normalized_mutual_info_score, rand_score, v_measure_score)
# regression metrics
from sklearn.metrics import (explained_variance_score, max_error, 
    mean_absolute_error, mean_squared_error, mean_squared_error, 
    mean_squared_log_error, median_absolute_error, r2_score, 
    mean_poisson_deviance, mean_gamma_deviance,
    mean_absolute_percentage_error
    #, d2_absolute_error_score, d2_pinball_score, d2_tweedie_score
)

classifier_metrics = [log_loss, roc_auc_score, accuracy_score, 
    precision_score, recall_score]
regression_metrics = [explained_variance_score, max_error, 
    mean_absolute_error, mean_squared_error, mean_squared_error, 
    mean_squared_log_error, median_absolute_error, r2_score, 
    mean_poisson_deviance, mean_gamma_deviance,
    mean_absolute_percentage_error 
    #, d2_absolute_error_score, d2_pinball_score, d2_tweedie_score
]
clustering_metrics = [adjusted_mutual_info_score, 
    adjusted_rand_score, completeness_score, 
    fowlkes_mallows_score, homogeneity_score, mutual_info_score, 
    normalized_mutual_info_score, rand_score, v_measure_score]
from sklearn.base import is_classifier, is_regressor
from packaging.version import Version
# these imports are for basic usage with sklearn, others
# may be needed for tensorflow, etc.
from sklearn import __version__ as sklearnver
if Version(sklearnver) < Version("0.23.0"):
    from sklearn.externals import joblib
else:
    import joblib

#=====custom imports
# use this "------- ^^<section name>" to indicate 
# where the code from the train file should replace this template

#=====base setup
output_path = './outputs'
os.makedirs(output_path, exist_ok=True)

#=====set experiment and model name
experiment_name = 'default_experiment_name'
model_name = 'default_model_name'

#=====connect to services
run = core.run.Run.get_context()
run_id = run.id
workspace = run.experiment.workspace
env = run.get_environment()
experiment_name = run.experiment.name

#=====start the run
start = time()
metrics = {}
log_text = []  # append new lines of str type to the list
tags, desc, model_framework, input_example = None, None, None, None
model_path = os.path.join(output_path,'model.pkl')
mlflow_model_path = os.path.join(output_path,'mlflow_model')

#=====import data
# output relies on unsegmented, cleaned, prepped, split
# data as having the output name 'df' (dataframe)

#=====custom training code
# clean, prep, and split data here, put into and use
# from a 'data' dict variable with elements "X_train",
# "y_train", "X_test", "y_test"...
#
# data = {"X_train":  X_train, "y_train": y_train,
#         "X_test": X_test, "y_test": y_test}
#
# if multiple models are to be trained, then at least 
# "y_{train/test}" must have a dictionary of model tags 
# (keys) associated with the labels for each model
data = None

# the final model should be name 'model' for registration purposes
model = None

#=====save the model
# this may need to be updated based on the type of model 
# implemented: i.e., sklearn vs tensorflow, etc.
with open(model_path, "wb") as file:
    joblib.dump(value=model, filename=file)

#=====standard metrics
metrics["training_time"] = time() - start
predictions = model.predict(data['X_train'])
eg_model_key = None
try:
    if is_classifier(model):
        metrics_functions = classifier_metrics
    elif is_regressor(model):
        metrics_functions = regression_metrics
    else:
        metrics_functions = clustering_metrics
    if isinstance(predictions,dict):
        for mkey, pred in predictions.items():
            metrics.update({
                f'{mkey}.train_{f.__name__}': f(data['y_train'][mkey], pred) 
                    for f in metrics_functions})
        if isinstance(data['X_train'],dict):
            eg_model_key = mkey
    else:
        metrics.update({f'train_{f.__name__}': f(data['y_train'], predictions) 
                for f in metrics_functions})

    if (data['y_test'][eg_model_key].size > 0 
        if eg_model_key is not None else data['y_test'].size > 0):
        # Predict the transformed test fields
        test_predictions = model.predict(data['X_test'])
        if isinstance(predictions,dict):
            for mkey, pred in test_predictions.items():
                metrics.update({
                    f'{mkey}.test_{f.__name__}': f(data['y_test'][mkey], pred) 
                        for f in metrics_functions})
        else:
            metrics.update({f'test_{f.__name__}': f(data['y_test'], test_predictions) 
                for f in metrics_functions})
except Exception as e:
    warn(f'error trying to evaluate metrics: {str(e)}')

#=====record with MLFlow
mlflow.start_run(run_id) # will be deleted for a local / MLflow run

#=====log stdout debug text lines
mlflow.log_text('\n'.join(log_text), os.path.join(output_path,'run.log'))

#=====save metrics
if len(metrics):
    mlflow.log_metrics({k: v for k,v in metrics.items()})
    # for k,v in metrics.items():
    #     run.log(k, v)

#=====create example inputs
# try:
#     input_example = (data['X_train'].iloc[0] 
#         if isinstance(data['X_train'], pd.DataFrame) 
#         else np.asarray(data['X_train'])[0,:])
# except:
#     input_example = None

#=====register the model
# (if selected in AzureRun settings)

# if running on a `compute instance` then MLflow 
# must be used to save the model if the link 
# between experiement and model is to be preserved
# NOTE: for models based on other modules (tensorflow, 
# etc.) a different mlflow.<module_type>.log_model() call
# must be used 
mlflow.sklearn.log_model(
    model,
    artifact_path=mlflow_model_path,
    registered_model_name=model_name,
    input_input=input_example,
    conda_env=env.python.conda_dependencies.as_dict()
)

# using the 'run' to register the model ensure the experiement 
# run id is logged within the model - however, within the
# context of the Azure compute run, the model_path cannot 
# seem to be found:
# run.register_model(model_name, model_path=model_path, 
#     tags=tags, model_framework=model_framework,
#     description=desc)

# # this will successfully register the model (the path is
# # able to be found), but it will not associate the model
# # with the current experiement:
# core.model.Model.register(model_name=model_name, 
#     model_path=model_path, workspace=workspace,
#     model_framework=model_framework,
#     description=desc, tags=tags)

#=====add tags if present
if tags and (workspace is not None) and (model_name != 'default_model_name'):
    cloud_model = core.Model(workspace,model_name)
    cloud_model.update(tags=tags,description=desc)

#=====save performance plots
# (if selected in AzureRun settings)
# relies on 'data' dict variable being defined in the custom training 
# code above with the DataFrame or ndarray elements key by 'X_train', 
# 'y_train', etc.
if is_classifier(model):
    roc_curves = {}
    for lbl, Xy in [('train',(data['X_train'],data['y_train'])), 
            ('test',(data['X_test'],data['y_test']))]:
        if ((eg_model_key is None and Xy[0].size > 0) or 
                (eg_model_key is not None and Xy[0][eg_model_key].size > 0)):
            pred_prob = model.predict_proba(Xy[0])
            # num_amb = ((pred_prob < AMBIGUOUS_PROB_RANGE[-1]) & 
            #     (pred_prob > AMBIGUOUS_PROB_RANGE[0])).sum()
            # metrics[lbl + '_numAmb'] = num_amb
            # if debug:
            #     print(f'Number of ambiguous classifications: {lbl:4s} -> {num_amb}')
            if isinstance(pred_prob,dict):
                for mkey,pp in pred_prob.items():
                    roc_curves['.'.join([mkey,lbl])] = roc_curve(Xy[1][mkey], pred_prob[mkey])
            else:
                pred_prob = pred_prob[:,1]
                roc_curves[lbl] = roc_curve(Xy[1], pred_prob)


    fig, ax = plt.subplots()
    annot_pos = []
    for lbl, roc_data in roc_curves.items():
        roc_key = [k for k in metrics.keys() if k.startswith(lbl) and k.endswith("roc_auc_score")]
        ax.plot(*roc_data[:2],linewidth=2,
                label=f'{lbl}' + (f' | AUC={metrics[roc_key[0]]:.2f}' if len(roc_key) else ''))
        thr = roc_data[2]
        subselect = np.arange(len(thr))[
            np.array([(len(thr)-1)*posfrac for posfrac in [0.25,0.55,0.8]],dtype=int)]
        for thres, x, y in zip(thr[subselect],
                                roc_data[0][subselect],
                                roc_data[1][subselect]):
            pos = np.array([x*0.9,y*1.1])
            if any([np.linalg.norm(pos-prev) < 0.05 for prev in annot_pos]):
                continue
            annot_pos.append(pos)
            ax.annotate(f'thres:{thres:.2f}',pos,fontsize=10,alpha=0.8)
    ax.plot([0,1],[0,1],color='tab:red',linestyle='--',linewidth=2,label='Random')
    ax.plot([0,0,1],[0,1,1],color='k',linestyle=':',linewidth=2,label='Ideal')
    ax.set_title('ROC Curve (missed events vs. false alarms trade-off)',fontsize=14)
    ax.set_xlabel('False positive rate',fontsize=14)
    ax.set_ylabel('True positive rate',fontsize=14)
    ax.legend(fontsize=13)
    plt.show()
    output_plots = './outputs/plots'
    os.makedirs(output_plots, exist_ok=True)
    mlflow.log_figure(fig, os.path.join(output_plots,f"{experiment_name}-{model_name}.png"))

#=====closing

#=====DONE