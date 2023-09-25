from glob import glob
import subprocess
import shutil
# from pathlib import Path
from os import curdir, remove, path, PathLike, rmdir, makedirs, scandir
import sys
import io
from subprocess import Popen, STDOUT, DEVNULL
from warnings import warn
from xml.sax.handler import property_declaration_handler
# from debugpy import connect
import importlib_metadata
from itertools import chain
from enum import Enum, auto
import yaml
import pandas as pd
from time import sleep

import azureml
from azureml import Workspace, Experiment, ScriptRunConfig
from azureml import Environment, Model
from azureml.compute import ComputeTarget, AmlCompute
from azureml.compute_target import ComputeTargetException

from azureml.model import InferenceConfig
from azureml.webservice import AciWebservice, LocalWebservice, Webservice

from azureml.runconfig import DockerConfiguration
from azureml.conda_dependencies import CondaDependencies
# from azureml.exceptions import WebserviceException

import mlflow

from ..sqlutils import sql_connect as sqlutil
from ..sqlutils.sqlconfig import SQLConfig
from ..config.baseconfig import EnvConfig, YmlConfig
from .azureconfig import AzureConfig

import logging
from rsidatasciencetools.azureutils import az_logging
from rsidatasciencetools.config.baseconfig import log_level_dict


logger = az_logging.get_az_logger(__name__)


class RegistrationStatus(Enum):
    UNINITIALIZED = auto()
    LOCAL = auto()
    REGISTERED_NEW = auto()
    REGISTERED_EXISTING = auto()


def convert_readable_size(_size):
    if _size <= 2**10:
        return f'{_size:.1f} B'
    elif 2**10 < _size <= 2**20:
        return f'{_size/2**10:.1f} kB'
    elif 2**20 < _size <= 2**30:
        return f'{_size/2**20:.1f} mB'
    else:
        return f'{_size/2**30:.1f} gB'


def read_ignore():
    try:
        with open('../dockerutils/.dockerignore','r') as f:
            ig_lines = f.read().split('\n')
        return [ln.strip() for ln in ig_lines]
    except:
        return []


def get_dir_size(_path='.',ignore=None):
    sleep(0.35)
    if ignore is None:
        ignore = read_ignore()
    total = 0
    with scandir(_path) as it:
        for entry in it:
            if not(path.exists(entry)):
                continue
            if it in ignore:
                continue
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

def driveusage(_path):
    sleep(0.1)
    if not(path.exists(_path)):
        return '?'
    here = path.realpath(_path); 
    rtn = subprocess.Popen(
        ['du','-sh', here], 
        stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, status = rtn.communicate()
    if status is None:
        return stdout.decode().split('\n')[0].split('\t')[0]
    else:
        return '?'

class AzureMLRun(object):
    ''' AzureMLRun object
            Used for automatic management of all related Azure 
            configurations; able to perform setup, execute training, 
            and initiate deployments; relies on experiment folder 
            containing the relevant set up credentials
            and configuration information (azure.compute_env, 
            azure-config.json, and <experiment-name>.yml)
    '''
    azure_compute_config = dict(
        compute_node_name=None,
        max_nodes=1,
        idle_seconds_before_scaledown=600,
        vm_size='Standard_DS11_v2',  #'STANDARD_D2_V2',
        deploy_dns_name=None,
        deploy_cluster_name=None,
        deploy_cpu_cores=0.2,
        deploy_memory_gb=1
    )
    env_keys = [
        'name',
        'version',
        'description',
        'tags',
        'image',
        'conda_file',
        'build',
        'build.dockerfile_path',
        'os_type',
        'inference_config']
    required_script_sections = [
        'import data',
        'custom training code'
    ]
    default_base_docker_img = ('mcr.microsoft.com/azureml/'
        'openmpi4.1.0-cuda11.6-cudnn8-ubuntu20.04')
    default_env_name = 'rsi-ml-default-env-name'
    default_mlflow_model_type = 'sklearn'
    skip_script_sections = []  # need 'record with MLFlow' to log the figures
    base_imports = [
        'pandas', 
        'numpy', 
        'matplotlib',
        'scikit-learn',
        'packaging',
        'pip',
        {'pip': ['pip', 'mlflow', 'azureml',
            'azureml-core', 'azureml-mlflow', 
            'azureml-defaults',
            'azureml-contrib-services',
            'azureml-contrib-dataset',
            'azureml-mlflow', 'inference-schema'
            # , 'scikit-learn-intelex'
            ]}
    ]
    web_service = None
    cpu_cluster = None
    deploy_cluster = None

    def __init__(self, experiment_path, name=None, model_name=None,
            azure_cred_loc=None, azure_env_name=None, project_folder=None,
            use_docker=True, register_model=None, register_env=True, 
            azure_compute_config=None, yaml_loc=None, env_from_yaml_file=True, 
            deprovision_immediately=False, copy_all_cred=True, 
            copy_no_passwords=False, attach_password_in_env=True,
            local=False, no_template=False, debug=0,
            skip_standard_metrics=False, skip_metrics_plots=False):
        '''
            Args:
                experiment_path (string/path-like, required)
                
                Names used in Azure experiment and model logging
                    name=None, derived from yml file if not provided
                    model_name=None, derived from yml file if not provided
                    azure_env_name=None, derived from yml file if not provided
                    project_folder=None, if provided, the setup process will
                        skip many of the file-copying exercises and use the
                        existing project folder

                Azure configuration from files:
                    azure_cred_loc=None, looks in experiment_path directory 
                        if not provided
                    azure_compute_config=None, Azure compute variables, looks in experiment_path 
                        directory if not provided
                    yaml_loc=None, experiment information looks in experiment_path 
                        directory if not provided

                Other run configuration settings:
                    use_docker=True or '<docker base image url/str>'
                    register_model=None (False or the string of 
                        the model flavor to be used, valid options in 
                        mlflow._model_flavors_supported, e.g., 'sklearn', 
                        will also be auto-populated from .yml 'mlflow_model_type' 
                        variable if input is None)
                    register_env=True
                    local=False, (not implemented yet) run the experiment locally
                    no_template=False, do not use the template train python file, 
                        instead just copy the train.py file as is
                    env_from_yaml_file=True
                    copy_all_cred=True
                    copy_no_passwords=True
                    attach_password_in_env=True
                    deprovision_immediately=False
                    skip_standard_metrics=False
                    skip_metrics_plots=False
                    debug=0

            Returns:
                AzureMLRun object
        '''
        self.experiment_path = path.abspath(experiment_path)
        self.debug = debug
        self.local_run = local
        self.copy_all_cred = copy_all_cred
        self.copy_no_passwords = copy_no_passwords
        self.attach_password_in_env = attach_password_in_env
        self.use_docker = use_docker
        self.register_model = register_model
        self.register_env = register_env
        self.deprovision_immediately = deprovision_immediately
        self.env_from_yaml_file = env_from_yaml_file
        self.env_status = RegistrationStatus.UNINITIALIZED
        if skip_standard_metrics:
            self.skip_script_sections.append('standard metrics')
        if skip_metrics_plots:
            self.skip_script_sections.append('save performance plots')
        if not(self.register_model):
            self.skip_script_sections.append('register the model')
        self.no_template = no_template

        self.train_script_url = path.join(self.experiment_path,'train.py')
        if not(path.exists(self.train_script_url)):
            raise FileNotFoundError((f'{self.train_script_url} training '
                'script does not exist'))
        if (project_folder is not None) and not(path.exists(project_folder)):
            warn('provided existing folder not found, initiating new project directory')
        self.reload_settings(name=name, model_name=model_name, 
            project_folder=project_folder, yaml_loc=yaml_loc,
            azure_compute_config=azure_compute_config, azure_env_name=azure_env_name, register_model=register_model,
            azure_cred_loc=azure_cred_loc, use_docker=use_docker, 
            use_existing_folder=((project_folder is not None) and path.exists(project_folder)))
        logger.setLevel(log_level_dict[self.debug])


    def reload_settings(self, name=None, model_name=None, project_folder=None, 
            yaml_loc=None, azure_compute_config=None, azure_env_name=None, register_model=None, 
            azure_cred_loc=None, use_docker=None, use_existing_folder=False):
        if use_docker is not None:
            self.use_docker = use_docker
        self._load_yaml(yaml_loc)
        if 'image' in self.yaml_config and self.use_docker == True:
            self.use_docker = self.yaml_config['image']
        self._load_azure_provisioning_settings(azure_compute_config)
        if register_model is not None:
            self.register_model = register_model
        elif 'mlflow_model_type' in self.yaml_config:
            self.register_model = self.yaml_config['mlflow_model_type']
        else:
            warn_msg = f'no model registration type provided, using the default: "{self.default_mlflow_model_type}"'
            warn(warn_msg)
            logger.warning(warn_msg)
            self.register_model = self.default_mlflow_model_type
        if self.register_model is not None and isinstance(self.register_model, str):
            if 'register the model' in self.skip_script_sections:
                del self.skip_script_sections[self.skip_script_sections.index('register the model')]
        assert (('model_name' in self.yaml_config) or (model_name is not None)
            ) or not(self.register_model), ('model name must be specified if '
            'model is to be registered')
        assert isinstance(self.register_model,bool) or (
            self.register_model in mlflow._model_flavors_supported), (
                'model registration type ({self.register_model}) '
                'is not a valid mlflow model flavor; valid options include: ' 
                f'{mlflow._model_flavors_supported}')
        self.model_name = (model_name if model_name is not None else (
            self.yaml_config['model_name'] if 'model_name' in self.yaml_config 
                else 'default_model'))
        self.expr_name = (self.yaml_config['name'] if name is None else name)
        self.azure_env_name = (azure_env_name
            if azure_env_name is not None else (
                self.yaml_config['env_name'] if 'env_name' in self.yaml_config 
                else self.default_env_name))
        if (project_folder is not None):
                self.project_folder = project_folder
                self.use_existing_project_contents = use_existing_folder
        else:
            self.use_existing_project_contents = False
            self.project_folder = path.join(self.experiment_path,
                (f'azure_temp-run_{self.expr_name}_'
                f'{int(pd.Timestamp.now(tz="utc").timestamp())}'))
    
        self.azure_cred = AzureConfig((self.experiment_path 
                if azure_cred_loc is None else azure_cred_loc), 
            read_all=True,
            error_no_file_found=not(self.local_run), debug=self.debug)
        self._ws = self.azure_cred.Workspace
    
        self.azure_env, self.conda_pkgs, self.pip_pkgs, \
            self.pkg_versions = None, None, None, None
        self.cleanup()

    @property
    def Workspace(self):
        return self._ws

    def __str__(self):
        '''Full string representation of the object (large)'''
        return self.__class__.__name__ + ':\n   ' + '\n   '.join([
            k + ': ' + 
            ('\n         '.join(v.split('\n')) if isinstance(v,str) 
                else str(v)) 
            for k,v in self.__dict__.items() if not(k.startswith('_'))])
            
    def __repr__(self):
        '''Abbreviated string representation of the object (smaller)'''
        cluster_name = (self.cpu_cluster 
            if getattr(self.cpu_cluster,"name",None) is None else self.cpu_cluster.name)
        abbrev_script_path = ("... " + self.project_folder[-60:] 
            if len(self.project_folder) > 63 else self.project_folder)
        abbrev_expr_path = ("... " + self.experiment_path[-40:] 
            if len(self.experiment_path) > 43 else self.experiment_path)
        return self.__class__.__name__ + ': ' + ' | '.join([
            f'Experiment: {self.expr_name} ({abbrev_expr_path})', 
            f'Model: {self.model_name}',
            'Azure Cred: ' + ', '.join(str(self.azure_cred).split('\n')),
            f'Azure Env: {self.azure_env_name} ({self.env_status.name})',
            f'Azure Compute: {cluster_name} ({self.state})',
            (f'Script Folder: {abbrev_script_path}'
                # f'(size: {convert_readable_size(get_dir_size(self.project_folder))})')
                f'(size: {driveusage(self.project_folder)})')
        ])

    def setup_run(self,force_new_setup=False,reload=False,debug=False):
        ''' Instantiate the: module versions, azure environment, 
            Azure compute node, then copy local files into experiment 
            directory and write the train script to file
        '''
        if force_new_setup:
            self.use_existing_project_contents = False
        if reload or force_new_setup:
            self.reload_settings(name=self.expr_name, model_name=self.model_name, 
                project_folder=(None if force_new_setup else self.project_folder), 
                yaml_loc=self.yaml_config.loc, azure_compute_config=self.azure_compute_config.loc, 
                azure_env_name=self.azure_env_name, register_model=self.register_model, 
                azure_cred_loc=self.azure_cred.loc, use_docker=self.use_docker)
        self._populate_versions()
        self._setup_azure_env(debug=max(int(debug), self.debug))
        self._provision_compute_services(debug=max(int(debug), self.debug))
        self._setup_run_script(debug=max(int(debug), self.debug))
        if not(force_new_setup) and self.use_existing_project_contents and (debug or (self.debug > 0)):
            warn('using preexisting project folder, skipping setup '
                'of run script and project folder')
        logger.debug(f'Finished setup of: {self.__repr__()}')
        self.use_existing_project_contents = True

    # def connect_db_data(self):
    #     self._run, self.cpu_cluster = None, None
    #     if sql_data:
    #         self.dataset = self.setup_sql(sql_data)
    #     # elif azure_data:
    #     #     self.dataset = self.

    # def setup_sql(self,sqlconfigpath):
    #     ''' create data extraction text to insert into the script'''
    #     # add DS tools to local path, and sql dependencies to pip installs
    #     # self.pip
    #     # SQLConfig(sqlconfigpath) # FormPOC1
    #     pass

    def cleanup(self, remove_project_folder=False):
        ''' Delete the experiment directory and reset the 
            internal configuration class variables
        '''
        if remove_project_folder:
            try:
                shutil.rmtree(self.project_folder, ignore_errors=True)
                # rmdir(self.project_folder)
            except FileNotFoundError:
                pass
        self.delete_service()
        self.experiment, self.docker_config, self.script_src, \
            self._run, self.cpu_cluster, self.pkg_versions, \
                self.web_service = \
                    None, None, None, None, None, None, None

    def _load_yaml(self, yaml_file=None):
        ''' Load the yml/yaml data for this experiment '''
        
        logger.info('loading yml config from: ',
                (self.experiment_path if yaml_file is None else yaml_file))

        self.yaml_config = YmlConfig((self.experiment_path 
            if yaml_file is None else yaml_file), base_str='',
            key_check_primary='model_name')
        logger.info(f'yaml key-value pairs found: \n{self.yaml_config}')
        if 'dependencies' not in self.yaml_config:
            self.yaml_config.setkeyvalue('dependencies',[])

    def _load_azure_provisioning_settings(self,azure_compute_config):
        ''' Load the experiment Azure environment (and 
            register, if requested)
        '''
        if azure_compute_config is None:
            compute_cfg_loc = self.experiment_path
        elif isinstance(azure_compute_config, AzureConfig):
            if len(azure_compute_config.locs) > 1:
                compute_cfg_loc = [loc for loc in azure_compute_config.locs 
                    if 'compute' in path.split(loc)[-1].lower()]
            if compute_cfg_loc:
                compute_cfg_loc = compute_cfg_loc[0]
            else:
                compute_cfg_loc = azure_compute_config.loc
        elif not(path.exists(azure_compute_config)):
            warn(('provided azure_compute_config file/path does not exist, '
                'using experiment directory'))
            compute_cfg_loc = self.experiment_path
        else:
            compute_cfg_loc = azure_compute_config
        _azure_compute_config = AzureConfig(compute_cfg_loc, skipload_env_var=True)
        # env_config_lower = self.azure_compute_config.lowerkeys()
        self.azure_compute_config.update({k:v for k,v in _azure_compute_config.items() 
            if k in self.azure_compute_config})

        if 'compute_node_name' in _azure_compute_config:
            self.azure_compute_config['compute_node_name'] = \
                _azure_compute_config['compute_node_name']
        if 'max_nodes' in _azure_compute_config:
            self.azure_compute_config['max_nodes'] = int(_azure_compute_config['max_nodes'])
        if 'deploy_cpu_cores' in _azure_compute_config:
            self.azure_compute_config['deploy_cpu_cores'] = float(_azure_compute_config['deploy_cpu_cores'])
        if 'deploy_memory_gb' in _azure_compute_config:
            self.azure_compute_config['deploy_memory_gb'] = float(_azure_compute_config['deploy_memory_gb'])
        if 'idle_seconds_before_scaledown' in _azure_compute_config:
            self.azure_compute_config['idle_seconds_before_scaledown'] = int(
                _azure_compute_config['idle_seconds_before_scaledown'])
        if 'vm_size' in _azure_compute_config:
            if ('compute_node_name' in _azure_compute_config) and self.debug:
                warn(('compute node type specified when compute node name '
                    'also specified, if the node name exists, then the node '
                    'type specified will be ignored unless'))
            self.azure_compute_config['vm_size'] = \
                 _azure_compute_config['vm_size']
        if self.deprovision_immediately:
            self.azure_compute_config['idle_seconds_before_scaledown'] = min(
                60,  self.azure_compute_config['idle_seconds_before_scaledown'])
        assert self.azure_compute_config['compute_node_name'] is not None, (
            '"compute_node_name has not been set in the input arguments, '
            'or could not find a "azure-compute-config.json file in your '
            'experiment folder')

    @property
    def azure_cred_str(self):
        if self._ws is None:
            return 'Azure workspace not initialized'
        else:
            return '\n'.join([self._ws.name, self._ws.resource_group, 
                self._ws.location, self._ws.subscription_id])

    def _populate_versions(self):
        ''' record the local version of packages - used in cloud 
            when MLflow used to log local runs
        '''

        conda_pkgs = set(el for el in self.base_imports 
            if not(isinstance(el,dict)))
        conda_pkgs.update(set(dep for dep in self.yaml_config['dependencies'] 
            if not(isinstance(dep,dict))))
        pip_pkgs = [el for el in self.base_imports if isinstance(el,dict) and 'pip' in el]
        if len(pip_pkgs):
            pip_pkgs = set(pip_pkgs[0]['pip'])
        _pip = [dep for dep in self.yaml_config['dependencies'] 
            if isinstance(dep,dict) and 'pip' in dep]
        if len(_pip):
            pip_pkgs.update(set(_pip[0]['pip']))

        pkgs = [el for el in importlib_metadata.distributions() 
            if el.name in conda_pkgs or el.name in pip_pkgs]
        self.pkg_versions = {'azureml-core': azureml.core.VERSION}
        self.pkg_versions.update({lib.name: lib.version for lib in pkgs})
        self.conda_pkgs = list(sorted(conda_pkgs))
        self.pip_pkgs = list(sorted(pip_pkgs))
        self.whl_pkgs = (self.yaml_config['wheel'] if 'wheel' in self.yaml_config else [])

    def _setup_azure_env(self, debug=0):
        ''' Set up the Azure python environment (prep work for 
            Docker container)
        '''
        assert self.conda_pkgs is not None and self.pip_pkgs is not None, (
            'conda and pip packages lists have not be instantiated')
        if self.env_from_yaml_file:
            strict_yaml_loc = path.join(path.dirname(path.abspath(__file__)),'temp.yml')
            envdict = {k:v for k,v in self.yaml_config.items(
                        filter=CondaDependencies._VALID_YML_KEYS)}
            envdict['name'] = '-'.join([
                self.yaml_config['name'],self.yaml_config['env_name']])
            with open(strict_yaml_loc,'w') as f:
                yaml.safe_dump(envdict, f)
            conda_dependencies = CondaDependencies(
                conda_dependencies_file_path=strict_yaml_loc)
            try:
                remove(strict_yaml_loc)
            except FileNotFoundError:
                pass
            del envdict
        else:
            PYTHON_VERSION = "{major}.{minor}.{micro}".format(
                major=sys.version_info.major,
                minor=sys.version_info.minor,
                micro=sys.version_info.micro)
            conda_dependencies = CondaDependencies.create(
                python_version=PYTHON_VERSION,
                conda_packages=(self.conda_pkgs if len(self.conda_pkgs) else None),
                pip_packages=(self.pip_pkgs if len(self.pip_pkgs) else None)
                )
        
        # pass in credentials in env variables instead of copying files
        if self.attach_password_in_env:
            env_var = {}
            if self.copy_no_passwords:
                files = [f for f in self.azure_cred.file_locs if f not in self.azure_cred.file_locs_no_pws]
                for_env = {}
                for f in files:
                    for_env.update(self.azure_cred._reader_used(f))
                env_var.update(for_env)
            env_var.update({self.azure_cred.search_prefix + k: v for k,v in self.azure_cred.items() 
                        if any((kk in k) for kk in ['pw', 'password'])} )
        else:
            env_var = {}
            
        if debug > 2:
            obfs = {k: self.azure_cred.get_obfuscated(k, v) for k, v in env_var.items()}
            logger.info(f'setting env_var: {obfs}')

        # NOTE: it should be ensured that the bdist and build folders have
        # the most updated version of the module intended to be uploaded
        # by running:
        #       python setup.py bdist_wheel --universal
        # in the top level directory of the module of interest (ensuring
        # that setuptool's and 'wheel' packages are pip-installed)
        for whl in self.whl_pkgs:
            whl_url = Environment.add_private_pip_wheel(workspace=self._ws,
                file_path=whl,exist_ok=True)
            conda_dependencies.add_pip_package(whl_url)

        if debug:
            logger.debug('\n'.join([str(('conda dep: ', self.conda_pkgs)),
                str(('pip dep: ', self.pip_pkgs)),
                str(('wheel pkgs: ', self.whl_pkgs))]))

        found_matching = False
        if (self._ws is not None) and self.register_env:
            azure_env = None
            try:
                azure_env = Environment.get(self._ws, self.azure_env_name)  #, version=None, label=None)
                docker_matches = (azure_env.docker.base_image == (self.use_docker
                        if isinstance(self.use_docker,str) else self.default_base_docker_img))
                conda_dep_check = azure_env.python.conda_dependencies.as_dict()
                conda_dep_dict = conda_dependencies.as_dict()
                conda_deps = set([dep for dep in conda_dep_check['dependencies'] 
                    if not(isinstance(dep,dict))]), set([
                        dep for dep in conda_dep_dict['dependencies']
                            if not(isinstance(dep,dict))])
                pip_deps = \
                    set(chain.from_iterable(
                        [dep['pip'] for dep in conda_dep_check['dependencies'] 
                        if (isinstance(dep,dict) and ('pip' in dep))])), \
                    set(chain.from_iterable(
                        [dep['pip'] for dep in conda_dep_dict['dependencies'] 
                            if (isinstance(dep,dict) and ('pip' in dep))]))
                matching_env_var = all(((k in azure_env.environment_variables) and 
                        (v == azure_env.environment_variables[k])) for k,v in env_var.items()) and all(
                    ((k in env_var) and (v == env_var[k]))
                        for k,v in azure_env.environment_variables.items())
                conda_deps_match = (len(conda_deps[0].symmetric_difference(conda_deps[1])) == 0)
                pip_deps_match = (len(pip_deps[0].symmetric_difference(pip_deps[1])) == 0)
                if docker_matches and matching_env_var and (
                        conda_dep_dict['name'] == conda_dep_check['name'] and
                        conda_deps_match and pip_deps_match):
                    found_matching = True
                    self.azure_env = azure_env
                    self.env_status = RegistrationStatus.REGISTERED_EXISTING
                    warn(f'found matching environement to use: {self.azure_env_name}')
                    return
            except Exception as exc:
                if 'Error retrieving the environment definition' not in str(exc):
                    raise(exc)
        if not(found_matching):
            if debug and (azure_env is not None):
                logger.debug(f'environment {azure_env.name} found but did not match: '
                    f'docker[{docker_matches}], conda[{conda_deps_match}], '
                    f'pip[{pip_deps_match}], env[{matching_env_var}]')
                if debug > 1:
                    if not docker_matches:
                        logger.info(f'Docker found: {azure_env.docker.base_image}, desired: {self.use_docker}')
                    if not conda_deps_match:
                        logger.info(f'Conda \n    found: {conda_deps[0]}\n    desired: {conda_deps[1]}')
                    if not pip_deps_match:
                        logger.info(f'Pip \n    found: {pip_deps[0]}\n    desired: {pip_deps[1]}')
                    if not matching_env_var:
                        logger.info(f'Env \n    found: {azure_env.environment_variables}\n    desired: {env_var}')

            self.azure_env = Environment(self.azure_env_name)
            if isinstance(self.use_docker,str) and len(self.use_docker):
                self.azure_env.docker.base_image = self.use_docker
                # self.azure_env.docker.enabled = bool(self.use_docker)
            elif self.use_docker:
                self.azure_env.docker.base_image = self.default_base_docker_img
            if self.use_docker and debug > 1:
                logger.debug(f'using docker base image: {self.default_base_docker_img}')
            self.azure_env.python.conda_dependencies = conda_dependencies
            self.azure_env.environment_variables.update(env_var)
            self.env_status = RegistrationStatus.LOCAL
            if debug > 1:
                logger.debug('new environment created')
            if (self._ws is not None) and self.register_env:
                self.azure_env.register(self._ws)
                self.env_status = RegistrationStatus.REGISTERED_NEW
                if debug > 1:
                    logger.debug('new environment registered')

    @property
    def state(self,string=False):
        assert ((self.cpu_cluster is None) or 
            (getattr(self.cpu_cluster,'status',None) is not None) or 
            (isinstance(self.cpu_cluster,str) and 
                self.cpu_cluster.startswith('local'))), (
            'cpu_cluster must be AciCompute object or string with "local" '
            'or "localdocker" specified')
        return (None if self.cpu_cluster is None 
            else ('Running' 
            if isinstance(self.cpu_cluster,str) and self.cpu_cluster.startswith('local')
            else self.cpu_cluster.status.__dict__[(
                'state' if 'state' in self.cpu_cluster.status.__dict__ 
                    else 'provisioning_state')]))

    def _provision_compute_services(self, compute_node_name=None, 
            vm_size=None, max_nodes=None, debug=False):
        ''' Set up the Azure compute node to be used for training - 
            Provision CPU cluster, provide name, VM size, etc.
        '''
        if self.state is not None and (self.state in [
                'Running', 'Starting', 'Preparing', 'Idle', 'Succeeded']):
            logger.debug('compute node status state: ', self.state)
            return

        if self.local_run:
            self.cpu_cluster = 'local'
            logger.debug('Using local compute resource ' +
                    ('in native compute mode.' if not(self.use_docker) else 
                    'to execute run in docker container.'))
        else:
            if compute_node_name is not None:
                self.azure_compute_config['compute_node_name'] = compute_node_name
            if vm_size is not None:
                self.azure_compute_config['vm_size'] = vm_size
            if max_nodes is not None:
                self.azure_compute_config['max_nodes'] = max_nodes
            # Verify that cluster does not exist already
            try:
                self.cpu_cluster = ComputeTarget(workspace=self._ws, 
                    name=self.azure_compute_config['compute_node_name'])
                logger.debug('Found existing compute: '
                        f'{self.azure_compute_config["compute_node_name"]}, '
                        f'status: {self.cpu_cluster.status}')
            except ComputeTargetException:
                node_types = AmlCompute.supported_vmsizes(workspace=self._ws, location='eastus')
                if self.azure_compute_config['vm_size'] not in [
                        cfg['name'] for cfg in node_types]:
                    raise NameError('Unrecognized compute node type: '
                        f'{self.azure_compute_config["vm_size"]}\n'
                        f'Valid options include: {node_types}')
                compute_config = AmlCompute.provisioning_configuration(
                    vm_size=self.azure_compute_config['vm_size'], 
                    max_nodes=self.azure_compute_config['max_nodes'],  # 4
                    idle_seconds_before_scaledown=\
                        self.azure_compute_config['idle_seconds_before_scaledown']
                )
                self.cpu_cluster = ComputeTarget.create(self._ws, 
                    self.azure_compute_config['compute_node_name'], compute_config)
            # wait for the cluster start process to complete
            self.cpu_cluster.wait_for_completion(show_output=(self.debug > 1 or debug))

    def _setup_run_script(self, debug=0):
        ''' Perform the following setup actions:
        
            - Create the experiment directory.
            - Copy the custom portions of the train script into the
              `./setup_run_template.py` lines into the eperiment directory.
            - Also copy the local modules/directories/files specified in 
              the yml file.
        '''
        if not(self.use_existing_project_contents):
            if self._ws is None:
                self.skip_script_sections.append('register the model')

            # create the temporary folder for execution
            makedirs(self.project_folder, exist_ok=True)
            # this touch ensures that the folder becomes a 'module', 
            # allowing relative referencing of imports, may not be needed
            # Path(path.join(self.project_folder,'__init__.py')).touch()
            
            self._scrape_and_populate_train_script()

            self._copy_local_modules(debug=debug)

        if self._ws is not None:
            assert self.cpu_cluster is not None, (
                'Connection to Azure CPU cluster not established')
            assert self.azure_env is not None, 'Azure Environment not established'

            self.experiment = Experiment(
                workspace=self._ws, name=self.yaml_config['name'])
            self.docker_config = DockerConfiguration(use_docker=bool(self.use_docker))
            self.script_src = ScriptRunConfig(source_directory=self.project_folder, 
                                script='train.py', 
                                compute_target=self.cpu_cluster, 
                                environment=self.azure_env,
                                docker_runtime_config=self.docker_config)
        elif self.local_run:
            warn('Azure workspace (local credentials file) not found - cloud logging will not occur')
        else:
            raise Exception('Azure workspace (local credentials file) not found')

    @property
    def isready(self):
        ''' Return boolean status of whether env, compute node, and 
            experiment directory are ready to be run.
        '''
        if not(self.local_run) and ((self.cpu_cluster is None) or (
                self.cpu_cluster.status.state not in ['Running', 'Starting'])):
            return False
        return all(el is not None for el in 
            [self.azure_env, self.experiment, 
                self.docker_config, self.script_src])

    def train_model(self,debug=False):
        '''train the model either locally or in the cloud'''

        # if self.local_run:
        #     run_command = f'cd {self.project_folder}; python train.py'
        #     p = Popen(run_command, shell=True, 
        #         stdout=(STDOUT if self.debug else DEVNULL), stderr=STDOUT)
        # else:
        self._run = self.experiment.submit(config=self.script_src)
        self._run.wait_for_completion(show_output=(self.debug > 1 or debug))

    def deploy_model(self,override_local=None,port=6789,
            force_restart=False,debug=False):
        '''deploy the model API either locally or to the cloud'''
        # write the score script into the project run directory
        self.score_script_url = path.join(self.experiment_path,'score.py')
        with open(self.score_script_url,'r') as fin:
            score_file = fin.read()
            with open(path.join(self.project_folder,'score.py'),'w') as fout:
                fout.write(score_file)

        model = Model(self._ws,name=self.yaml_config['model_name'])

        # this is the custom model deployment
        inference_config = InferenceConfig(entry_script='score.py', 
            source_directory=self.project_folder.split(path.sep)[-1], 
            environment=self.azure_env)

        service = None
        local = self.local_run
        if override_local is not None:
            local = override_local
        if local:
            if force_restart:
                self.delete_service()
            deployment_config = LocalWebservice.deploy_configuration(port=port)
        else:        
            deployment_config = AciWebservice.deploy_configuration(
                dns_name_label=self.azure_compute_config['deploy_dns_name'], 
                cpu_cores=self.azure_compute_config['deploy_cpu_cores'], 
                memory_gb=self.azure_compute_config['deploy_memory_gb'])

            existing_service = [webserve for webserve in Webservice.list(self._ws) 
                if webserve.name == self.yaml_config['service_name']]
            if len(existing_service):
                assert len(existing_service) == 1, ('found more than one active '
                    'service with this name, this should not happen')
                service = existing_service[0]
                if force_restart:
                    warn(f'found existing webservice, deleting service: {service.name}')
                    service.delete()
                    service = None
                else:
                    warn(f'found existing webservice, attaching to service: {service.name}')
        if service is None:
            if self.azure_compute_config['deploy_cluster_name']:
                try:
                    self.deploy_cluster = ComputeTarget(workspace=self._ws, 
                        name=self.azure_compute_config['deploy_cluster_name'])
                    logger.debug('Found existing deploy target: '
                            f'{self.azure_compute_config["deploy_cluster_name"]}, '
                            f'status: {self.deploy_cluster.status}')
                except ComputeTargetException:
                    self.deploy_cluster = ComputeTarget(workspace=self._ws, 
                        name=self.azure_compute_config['deploy_cluster_name'])
            self.web_service = Model.deploy(workspace=self._ws,
                                name=self.yaml_config['service_name'],
                                models=[model],
                                inference_config=inference_config,
                                deployment_config=deployment_config,
                                deployment_target=self.deploy_cluster, 
                                overwrite=True)

            self.web_service.wait_for_deployment(show_output=(self.debug > 1 or debug))
        else:
            self.web_service = service

    def delete_service(self):
        if self.local_run and self.web_service is not None:
            self.web_service.delete()
            self.web_service = None

    def __del__(self):
        self.delete_service()

    def metrics(self,ret=False):
        ''' Retrieve cloud-logged metrics and possibly plot them '''
        met = self._run.get_metrics()
        ret = ret or not(len(met) and isinstance([met[k] 
            for k in met][0],(pd.ndarray,list)))
        if not(ret):
            try: 
                from matplotlib import pyplot as plt
                _, ax = plt.subplots(1,1,figsize=(5,5))
                pd.DataFrame(met).plot(ax=ax)
                plt.show()
            except ImportError:
                ret = True
        if ret:
            return met

    def _copy_local_modules(self, debug=0):
        ''' Copy the local modules/files specified in the experiment 
            .yml file needed for this run
        '''
        if ('local' in self.yaml_config and 
                self.yaml_config['local'] is not None and 
                len(self.yaml_config['local'])):
            debug = int(debug)
            logger.info(f'\nCopying {len(self.yaml_config["local"])} local module elements:')
            base = path.dirname(self.yaml_config.file_loc)
            exclude_list = ['.git']
            if 'exclude' in self.yaml_config:
                exclude_list.extend(self.yaml_config['exclude'])
            exclude = ' '.join([f'--exclude {excl}' for excl in exclude_list])
            # makedirs(f'{self.project_folder}{path.sep}source_dir',exist_ok=True)
            for file in self.yaml_config['local']:
                if len(file.split()) > 1:
                    file = file.split()
                else:
                    file = [file]
                copy_cmd = (f'rsync -aLq {exclude} {path.join(base,file[0])} '
                    f'{self.project_folder}{path.sep}{(file[1] if len(file) > 1 else "")}')

                logger.info(f'file: {path.join(base,file[0])} - exists: {path.exists(path.join(base,file[0]))}')
                logger.info(f'copy command: {copy_cmd}')
                p = Popen(copy_cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)
                if not(path.isdir(file[0])):
                    warn(('copying local file as an import, but python does not allow '
                        'import from files, rather they must be in folder-based modules'))
                else:
                    rmv_git = ("rm -rf `find "
                        f"{self.project_folder}{path.sep}{(file[1] if len(file) > 1 else file[0])} "
                        "-maxdepth 2 -name '.git'`")
                    p = Popen(rmv_git, shell=True, stdout=DEVNULL, stderr=STDOUT)
                logger.info('')

            # shouldn't be able to reach this assertion error
            assert not(self.azure_cred.error_no_file_found and self.azure_cred.file_loc is None), (
                'could not find any valid Azure credentials .json file ')
            # copy the azure config file(s)
            if (self.azure_cred.file_loc is not None) and path.exists(self.azure_cred.file_loc):
                logger.info(f'copying azure cred: no pw: {self.copy_no_passwords}; all: {self.copy_all_cred}')
                if self.copy_all_cred:
                    if self.copy_no_passwords:
                        files = self.azure_cred.file_locs_no_pws
                    else:
                        files = self.azure_cred.file_locs
                else:
                    files = [self.azure_cred.file_loc]
                logger.info(f'files to copy: {files}')
                for file in files:
                    copy_cmd = (f'cp -rL {file} '
                        f'{self.project_folder}{path.sep}{path.basename(file)}')
                    logger.info(f'copy command: {copy_cmd}')
                    p = Popen(copy_cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    def _scrape_and_populate_train_script(self):
        ''' Read in the custom and template scripts and write out the 
            final script to the project directory
        '''
        self.train_script_url = path.join(self.experiment_path,'train.py')
        if self.no_template:
            with open(self.train_script_url,'r') as fin:
                train_file = fin.read()
                with open(path.join(self.project_folder,'train.py'),'w') as fout:
                    fout.write(train_file)
        else:
            if not(path.exists(self.train_script_url)):
                raise FileNotFoundError('could not find training script')
            template_path = path.join(path.dirname(path.abspath(__file__)), 
                'setup_run_template.py')
            with open(template_path,'r') as f:
                lines_template = f.read().split('\n')
            with open(self.train_script_url,'r') as f:
                _lines_custom = f.read().split('\n')
            lines_custom = {}
            next = []
            sec_key = '#====='
            last_sec = None
            for lno, ln in enumerate(_lines_custom):
                if sec_key in ln:
                    if len(next) and last_sec:
                        lines_custom[last_sec] = next
                    next = []
                    last_sec = ln.split(sec_key)[-1].strip()
                # check to see if there is a bad section header
                # with insufficient ='s or whitespace between # and =
                elif (('#' in ln) and ('=' in ln)) and ((
                    ('#=' in ln) and (len(ln.split('#')[0].strip()) == 0)) or ((
                        len(ln.split('#')) > 1) and ( # don't error on a comment
                        len(ln.split('#')[0].strip()) == 0) and (
                        # check if there are spaces between the # and = characters
                        (' ' in ln.split('#')[1].split('=')[0]) and 
                            len(ln.split('#')[1].split('=')[0].strip()) == 0))):
                    raise KeyError('found a bad section header key in '
                        f'the train.py script on line: {lno+1}')
                next.append(ln)
            lines_custom[last_sec] = next
            assert all((k in lines_custom.keys()) for k in self.required_script_sections), (
                'missing required sections in the training script: ' + ', '.join([
                    f"'{k}'" for k in self.required_script_sections 
                    if (k not in lines_custom.keys())]) + ' | keys found: ' + 
                    ', '.join([f"'{k}'" for k in lines_custom.keys()])
                )
            lines_partitioned = {}
            sec_order = []
            next = []
            for ln in lines_template:
                if sec_key in ln:
                    if len(next) and last_sec:
                        if last_sec in lines_custom:
                            lines_partitioned[last_sec] = \
                                lines_custom[last_sec]
                        else:
                            lines_partitioned[last_sec] = next
                    next = []
                    last_sec = ln.split(sec_key)[-1].strip()
                    sec_order.append(last_sec)
                next.append(ln)
            # the last section of lines won't be include unless we account for them here
            if last_sec in lines_custom:
                lines_partitioned[last_sec] = lines_custom[last_sec]
            else:
                lines_partitioned[last_sec] = next            
            unknown_secs = [cust_sec for cust_sec in lines_custom.keys() 
                if (cust_sec not in sec_order)]
            if unknown_secs:
                raise KeyError(f'unknown train script section(s): {unknown_secs}')
            if not(self.register_model):
                lines_partitioned['register the model'] = [
                    '#=====register the model',
                    '#  ----> skip model registration'
                ]
            else:    
                lines_partitioned['register the model'] = [
                    '#=====register the model',
                    f'mlflow.{self.register_model}.log_model(',
                    '    model,',
                    '    artifact_path=mlflow_model_path,',
                    '    input_example=input_example,',
                    '    registered_model_name=model_name,',
                    '    conda_env=env.python.conda_dependencies.as_dict()'
                    ,')']

            if 'set experiment and model name' not in lines_custom:
                warn('no expr/model naming section in training script, '
                    'populating from AzureRun object')
                lines_partitioned['set experiment and model name'] = [
                    "#=====set experiment and model name",
                    f"experiment_name = '{self.expr_name}'",
                    f"model_name = '{self.model_name}'", '']

            if self.local_run:
                # replace MS compute node -based run
                # 'run = Run.get_context()',
                # 'workspace = run.experiment.workspace',
                # 'env = run.get_environment()'
                connect_lines = ['#=====connect to services']
                connect_lines.extend(([
                    'env = Environment(self.azure_env_name)',
                    f'env.docker.base_image = "{self.azure_env.docker.base_image}"',
                    'env.docker.python.conda_dependencies = ' +
                            str(self.azure_env.python.conda_dependencies.as_dict())
                        ] if self._ws is None 
                    else [
                        'from rsidatasciencetools.azureutils.azureconfig import AzureConfig',
                        'azure_config = AzureConfig("./")',
                        'workspace = azure_config.Workspace  # core.Workspace.from_config("./azure-config.json")',
                        f'uri = ("{self.project_folder}" if workspace is None' +
                            ' else workspace.get_mlflow_tracking_uri())',
                        'mlflow.set_tracking_uri(uri)']))
                connect_lines.extend([
                    # 'workspace = run.experiment.workspace',
                    'mlflow.set_experiment(experiment_name)',
                    'mlflow.start_run()',
                    'run = mlflow.active_run()',
                    'run_id = run.info.run_id'
                ])
                lines_partitioned['connect to services'] = connect_lines
                del lines_partitioned['record with MLFlow']
                lines_partitioned['closing'].append('mlflow.end_run()')

            with open(path.join(self.project_folder,'train.py'),'w') as f:
                f.write('\n'.join(chain.from_iterable(
                    [lines_partitioned[sec] for sec in sec_order 
                        if sec not in self.skip_script_sections and sec in lines_partitioned])))
