from rsidatasciencetools.config.baseconfig import EnvConfig
import joblib
import numpy as np
import os
from glob import glob
import sys

from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType

from sklearn.datasets import load_diabetes

X, y = load_diabetes(as_frame=True, return_X_y=True)

dir_containing_pkg = os.path.dirname(os.path.realpath(__file__))
try:
    from rsidatasciencetools.mlutils.model_io import ModelManager

except ImportError:
    # packagedir = os.path.dirname(os.path.dirname(currentdir))
    print(f'>> adding to PYTHONPATH: {dir_containing_pkg}')
    sys.path.append(dir_containing_pkg)

    from rsidatasciencetools.mlutils.model_io import ModelManager
# import debugpy
# # Allows other computers to attach to debugpy on this IP address and port.
# debugpy.listen(('0.0.0.0', 5678))
# # Wait 30 seconds for a debugger to attach. If none attaches, the script continues as normal.
# debugpy.wait_for_client()
# print("Debugger attached...")
dir_containing_pkg = os.path.dirname(os.path.realpath(__file__))
if 'RSI_CONFIG_PATH' not in os.environ:
    os.environ['RSI_CONFIG_PATH'] = dir_containing_pkg

mm = ModelManager(dir_containing_pkg)
# The init() method is called once, when the web service starts up.
#
# Typically you would deserialize the model file, as shown here using joblib,
# and store it in a global variable so your run() method can access it later.
# def init():
#     global model

#     # The AZUREML_MODEL_DIR environment variable indicates
#     # a directory containing the model file you registered.
#     model_path = os.path.join(os.environ['AZUREML_MODEL_DIR'], model_filename)

#     model = joblib.load(model_path)

def init():
    global model
    model_name = 'sklearn-ridge-regr-diabetes'
    model, _ = mm.load_model(model_name, _from='azure')


# The run() method is called each time a request is made to the scoring API.
#
# Shown here are the optional input_schema and output_schema decorators
# from the inference-schema pip package. Using these decorators on your
# run() method parses and validates the incoming payload against
# the example input you provide here. This will also generate a Swagger
# API document for your web service.
@input_schema('data', NumpyParameterType(X.values[0,:].reshape(1,10)))
@output_schema(NumpyParameterType(y.values[0].reshape(1)))
def run(data):
    # Use the model object loaded by init().
    result = model.predict(data)

    # You can return any JSON-serializable object.
    return result.tolist()
