# Training, Credentials, and Deployment

1. [Training](#training)

    0. [Steps](#steps)
    1. [Preparing the train.py base file](#preparing-the-train.py-base-file)
    2. [Azure cloud training setup](#azure-cloud-training-setup)
    3. [Credential protection](#credential-protection)
    4. [Executing training in Azure](#executing-training-in-azure)
2. [Deployment in Azure](#deployment-in-azure)
    1. [Required files](#required-files)
    2. [Local Deployment](#local-deployment)
    3. [Azure Deployment](#azure-deployment)


The Analytics Team uses the `test-AzureRun-submit.ipynb` notebook to execute the training and initiate deployment in Azure. This notebook relies on several files explained in the coming sections. The notebook path is: `DataScienceTools/rsidatasciencetools/azureutils/example_run/`. That folder is a good example of what needs to be constructed for deployment, so we advise you to follow it in parallel with this README file.

## Training

### Steps

 The steps for the training can be summarized in four:
 
 1) Prepare the train.py base file. For more details see the [next section](#preparing-the-train.py-base-file)
 2) Prepare the set of 3 additional files for credentials and environment configuration. [See Azure cloud training setup](#azure-cloud-training-setup) 
 3) Set up one folder with:
     - the four files mentioned in steps 1 and 2, plus
     - the `test-AzureRun-submit.ipynb` notebook, plus
     - the enviromental file with Azure credentials
 4) Use the `test-AzureRun-submit.ipynb` to train the model in Azure Machine Learning Studio. [See the execution of the training here](#executing-training-in-Azure)
 
Details for steps 1, 2 and 4 plus additional considerations for credentials and more follow.

### **Preparing the train.py base file**
The base `train.py` is the content needed in a script to perform training and evaluation locally. It is a `base` because it doesn't contain all the data required for Azure training. However, several sections will be included automatically later by using the `AzureMLRun` class. 

To prepare the base `train.py` pay attention that key sections must be marked with #=====. The key sections that must be filled in the base score.py file are:

        - `=====set experiment and model name` 
        - `=====import data`
        - `=====custom training code` 
        
   Other sections, such as `#=====base imports`, `#=====connect to services`, `#=====start the run` will be populated automatically in the code when submitting the model training to azure using the `AzureMLRun` class. Sections are filled automatically only if not present in the base train.py. If present, a section will not be overwritten.
       
It may be helpful to review the [`setup_run_template.py`](./setup_run_template.py) script to see how the actual training scripts are constructed from abbreviated `train.py` scripts with the appropriate sections filled in from the hand mentioned above.


#### __Force skipping a section__
In general, this is not necessary. But if there is any section that you want to force to be skipped, you can always include it with no content. For example, suppose you want to force ignoring performance plots without using the given parameters; you can add the line: `#=====save performance plots (if selected in `AzureMLRun` settings)` at the end of the score file as per the below image.

<img src="images/force-to-skip-section.png" width="500">


#### __Smoke check for the base train.py file__

I recommend always running your train file locally, like using `$python train.py` in the directory containing the `train.py` file, to ensure the file is running in the first place.

#### __Smoke check for spacy model training__
The spacy model training from the config file usually takes a long time, and if the code fails, you will have to train it all again! I recommend tweaking the number of Epocs in the spaCy config file to do just one Epoc and not a complete training.

To do this, change the line `max_epochs = 0` to `max_epochs = 1` in the `[training]` section. Zero epochs mean unlimited, whereas one means one epoch will go way faster. DON’T FORGET TO PUT IT BACK TO 0 after the smoke check.


### **Azure cloud training setup**

The `azureutils.AzureMLRun` class relies on four necessary files to be in the experiment folder (sample files in `DataScienceTools/rsidatasciencetools/azureutils/example_run`):

- `azure-config.json`: specifies the Azure connection subscription/authentication information - this is not stored in the repo, so you will need to populate a JSON file and put it in the experiment folder (in this case, `example_run`)

- `azure-compute-config.json`: specifies the compute nodes or existing nodes to use, as well as the amount of memory and other azure compute-related parameters

- `<experiment_name>.yml`. For example, `forms-Spacy-PII-models.yml` <- Use the given file as a template. This file contains the following:
    - the experiment name, model name, environment name, image, and service name
    - imports required for this run. Add the necessary packages and dependencies that are not included in the template
    - any folders of local imports must be listed under `local` in the `<expr_name>.yml` file and can be relative to the location of the experiment folder. For example, files such as CSV files, spacy_config.cfg, etc.
    

### **Credential protection**

The credential protection is managed using EnvConfig import in general, and AzureConfig for Azure training, and the `azure-export-dev-config.env` file.

#### __azure-export-dev-config.env__

An environment file loads all the credentials into the bash environment. An example of this file is `azure-export-dev-config.env`. This file is not in git and should never be committed to any repository. Make sure to have included `.env` in your `.gitignore` list of files of any repository that needs credentials, as in line 9 of the file below. 

<img src="images/gitignore_env_files.PNG" width=400>

This file can be requested from any Analytics Team member. 

#### __EnvConfig import__

This import allows importing the credentials located outside the code for general use (including credentials for Azure as well as other tools). Azure credentials will be in the `azure-export-dev-config.env,` but the non-secure credential and compute parameters can also be loaded with the `azure*config.json` files. Parameeters from additional `.env` files can also be loaded if the `EnvConfig` instantiation is provided the directory of or exact file to import. The default function will automatically pull `RSI_AZURE_` prefixed credentials from an environmental file (`.env`), and look for in the current directory (`/formsML`) or the one above (`../formsML`). The env configuration will look for the prefix `RSI_` on variables coming from the environement. If you specify a file (as in the example), variables don't need to be prefixed; multiple files can be loaded, but order will matter and parameters can override previously loaded variables (a warning will be issued).

This import resides in `rsidatasciencetools/config/baseconfig.py`. Since rsidatasciencetools should already be in your path, EnvConfig can be imported directly as:

`from rsidatasciencetools.config.baseconfig import EnvConfig`

To use it, you instantiate `EnvConfig` and can use the different credentials by extracting the values of a dictionary whose keys are the credential names. See below for an example of extracting data from a datablob.  
```
from rsidatasciencetools.config.baseconfig import EnvConfig
from azureml.core import Workspace, Dataset

env = EnvConfig('./.env', error_no_file_found=False)
workspace = Workspace(env['subscription_id'], env['resource_group'], env['workspace_name'])
dataset = Dataset.get_by_name(workspace, name='preliminary_pii_calc_classification')
```

If you are interested in having only lowercase variables, you can use .lowerkeys() function as: `env_dict_lk = env.lowerkeys()`.

Finally, when variables are prefixed by "RSI_" for `EnvConfig` ("RSI_AZURE_" for `AzureConfig`) the prefix will be removed when the variable is stored in the config object. For example, "RSI_AZURE_subscription_id" will become "subscription_id” in the `AzureConfig` object.


#### __AzureConfig for credentials and worskpace instanciation__
For training in Azure ML Studio, a key element is the `AzureConfig` class. This class auto-search the environment or directory for Azure credentials setup (`azure*config.json` files). In a score script, `AzureConfig` will allow setting up the credentials from the Linux environment in Azure.  For example,

```
from rsidatasciencetools.azureutils.azureconfig import AzureConfig
import os

azureconfig = AzureConfig(os.path.dirname(__file__))
workspace = azureconfig.Workspace
dataset = Dataset.get_by_name(workspace, name='preliminary_pii_calc_classification')
```

### **Executing training in Azure**
The `AzureMLRun` class allows you to execute the training straightforwardly. We will mention here all the steps run by just executing a cell.

#### __First: Instantiated the AzureMLRun class__
Check on the parameters that may need updates. You can run `AzureMLRun?` to see them all, as shown below.

<img src="images/AzureMLRun_parameters.PNG" width="300">

For example: for any model that is not sklearn, you may need to update the `register_model` defaulted to sklearn. For spaCy, we will use `register_model=”spacy”` instead.

To start the training, you will first instantiate the `AzureMLRun` into object `arun`. You just run the import and second cell with `Ctrl+Enter` as usual in a jupyter notebook:
<img src="images/training_deployment_AzureRunClass.PNG" >

#### __Second: setup the run__
During this step, the program sets up the environment that will host the model. Generates the authentication, provision the nodes and the memory, connect the cluster involved and register the model.
<img src="images/arun_1setup_run.PNG" >


#### __Third: train the model__
In this step, a new job will start running in Azure ML Studio. You can follow the link in the output or go to the Azure Workspace and check the list of Jobs.

<img src="images/arun_2train_model.PNG" >


The `Status` column of the panel will tell you that the model is in `Queued` to be trained, `Running` the training, `Completed`, or `Failed`.


<img src="images/Queued_azure_training_job.PNG" >

When the model fails, there are `Outputs+logs` that show the reason for the failure. You should correct it and re-run the process. For example, in the example below, a python package is missing in the yml file, so we add the line with the package’s name in that file, restart the kernel, and run the notebook from the beginning.

<img src="images/Failed_training_missing_python_package.PNG">


## Deployment in Azure ML Studio

### **Requirements**

For deployment, you will use the same folder you used for training, ([see step 3 in Steps of training](#steps)), plus:

    - [the completed trained model in Azure](#third:-train-the-model)
    - a `score.py` file that Azure will use to make predictions with the model. You can see an example in the [example_run folder](./example_run/score.py).
    - an additional file called `azure-compute-config.json` which defines the compute type (for example "aks" for Azure Kubernets Service) and the compute target name where to do the deployment. Sample files also in the `DataScienceTools/rsidatasciencetools/azureutils/example_run/` folder, an example of this file is:
        ```
        {
            "compute_node_name": "ExampleComputeClusterNode",
            "max_nodes": 1,
            "vm_size": "Standard_DS11_v2",
            "idle_seconds_before_scaledown": 600,
            "deploy_cpu_cores": 0.2,
            "deploy_memory_gb": 1,
            "deploy_cluster_name": "DevelopDeployed",
            "deploy_dns_name": "ExampleDeployedModel",
        }
        ```

The deployment of a trained model in Azure has two steps: local deployment and Azure deployment.


### **Local Deployment**
Make sure to have installed `uvicorn` and `fastapi`.

If you don't have them, use pip to do the installation"
`$ pip install uvicorn fastapi`

The local deployment will ensure that the API will not break. It is advisable to smoke-check the deployment to avoid losing time in Azure. Later on, in Azure deployment, other things, such as dependencies, can still fail.

For local, you can run in ubuntu, located on the folder with the files you want to deploy (if the uvicorn app is called in the `__main__` section of the script):
`$python path/to/mlapi/applciation.py`

Or using uvicorn directly, specifying that `api` is the variable that should be run:
`$uvicorn path/to/mlapi/application.py:api --host 0.0.0.0 --port 8000`

The image below shows the output from running the python command. 


<img src="images/deployement_local_1_python_run_http_location.PNG" width="1000">

The API can be tested in the `http://0.0.0.0:8000` address that appears at the bottom. If that address does not work in your browser, make a minor tweak to use the local host by changing the initial part `http://0.0.0.0` to `localhost:8000/docs`. You should see an output similar to the image below.

<img src="images/deployement_local_2_succesful_api_connection.PNG" width="1000">


#### __`uvicorn` options__

Options for the `uvicorn` can be accessed with 
`$uviconr --help`

For example, 
an option to change PORT is available in case defaults are not what you want, as appears in this image below: 

<img src="images/uvicorn_help.PNG" width="500">

Also, the option to reload can be applied using the additional argument:

`$uvicorn path/to/mlapi/application.py:api --host 0.0.0.0 --port 8000 --reload`

The reload functionality must never be used in production. Still, it is beneficial when doing local deployment since it allows changes to be *reloaded* immediately and automatically without having to run all again.


### **Azure Deployment**

Once your API works locally, it is time to deploy your model in Azure. For this, you will continue working on your `test-AzureRun-submit` notebook.

For this you will need to add to the same folder you used for training:
    -

#### __First, make sure you have a proper service_name__ 

The `service name` is a crucial value and must not currently exist. For this reason, `arun.yaml_config.setkeyvalue` allows you to manually change the name when the current name is already taken. This usually happens if your deployment service names or DNS has already been used, so a new name other than the default may be required. 
The name can be easily modified by changing the last digit. For example, if the current name forms-spacy-nlp-service-3 is taken, you can update it to forms-spacy-nlp-service-4 by using: `arun.yaml_config['service_name'][:23] + '-4'` as in the image below.

<img src="images/arun3_yaml_config.PNG">

#### __Second, make sure you have a proper `deploy_dns_name`__
Similarly to step one, if your `deploy_dns_name` is already in use, you need to change it. You can either leave the DNS name blank (`None`) or you can also use the trick of changing the last digit, as in the image below:

<img src='images/arun_4azure_compute_config.PNG'>

#### __Third, deploy the model__
To initiate deployment, you run the deploy_model method as in the image below. We usually force restart and use debug to see the steps while processing.

<img src="images/arun_5deploy_model.PNG" >

The deployment will start running as a new **Endpoint** in Azure ML Studio. 
If you click the Endpoint, it will show you the **Details** tab, which includes, more importantly, the **"Deployment state"**, which will become "Healthy" if the deployment succeeds. Other states are "Unhealthy" if it didn't succeed, "Transitioning" and "Loading" when still the deployment is running.
In the **Test tab**, you can test the model with an input, as shown in the images below.

<img src="images/deployment_1New_End_Point.PNG">
<img src="images/EndPoint_2Details.PNG">

<img src='images/deployment_3testing.PNG'>




















