#=====custom imports
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from azureml import core
import os
import numpy as np
import mlflow
from sklearn import __version__ as sklearnver
from packaging.version import Version
if Version(sklearnver) < Version("0.23.0"):
    from sklearn.externals import joblib
else:
    import joblib

# can be local files or pip/conda installed
# be sure to mark in the appropriate section 
# of the .yml file
from example_imports.extra import test_func

# these are overridden by 'base setup' after 'custom imports' 
# (this section) is run
log_text = []
output_path, model_path, model_name, run, run_id, workspace, env = \
    None,  None, None, None, None, None, None


#=====import data
X, y = load_diabetes(as_frame=True, return_X_y=True)

#=====custom training code
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=0)
data = {"X_train":  X_train, "y_train": y_train,
        "X_test": X_test, "y_test": y_test}

# list of numbers from 0.0 to 1.0 with a 0.05 interval
alphas = np.arange(0.0, 1.0, 0.05)

best_run_model_filename, model = None, None
best_mse = np.inf
for alpha in alphas:
    # Use Ridge algorithm to create a regression model
    reg = Ridge(alpha=alpha)
    reg.fit(X_train, y_train)

    preds = reg.predict(X_test)
    mse = mean_squared_error(preds, y_test)
    run.log('alpha', alpha)
    run.log('mse', mse)

    model_file_name = os.path.join(output_path, 
        'ridge_{0:.2f}.pkl'.format(alpha))
    # save model in the outputs folder so it automatically get uploaded
    with open(model_file_name, "wb") as file:
        joblib.dump(value=reg, filename=file)
    if best_run_model_filename is None or mse < best_mse:
        best_run_model_filename = model_file_name
        best_mse = mse
        model = reg
        
    log_text.append('alpha is {0:.2f}, and mse is {1:0.2f}'.format(alpha, mse))
    
desc = 'Test regression model on diabetes data'
tags = {'domain':'test_azureml','application': 'health-regression', 
        'model': str(model.__dict__),
        'MLtype':'supervised', 'MLmode':'regression', 
        'run_id': f'{run_id}',
        'data_dim': str({k: v.shape for k,v in data.items()}),
        'data_feature_names': str(X_train.columns.tolist())
    } 
model_framework = core.model.Model.Framework.SCIKITLEARN
