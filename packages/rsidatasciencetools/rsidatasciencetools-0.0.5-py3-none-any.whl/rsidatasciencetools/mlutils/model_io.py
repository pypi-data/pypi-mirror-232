'''Methods for saving and retrieving ML models '''
from inspect import istraceback
from pathlib import Path
import pickle
from typing import Union, Dict, List
import pandas as pd
import mlflow
from glob import glob
from warnings import warn
from os import path, PathLike, mkdir, remove
from shutil import rmtree
import json
from azureml.core import Model, Workspace
from rsidatasciencetools.mlutils.object_util import make_dict_from_obj, jstringify_model_object
from rsidatasciencetools.config.baseconfig import Config, YmlConfig, EnvConfig
from rsidatasciencetools.config.cacheconfig import CacheConfig
from rsidatasciencetools.azureutils.azureconfig import AzureConfig
from rsidatasciencetools.mlutils.multi_model import MultipleOutputModel

from rsidatasciencetools.config.baseconfig import get_stdout_logger, log_level_dict

multi_path_string = Union[List[str],List[PathLike],str,PathLike,None]


class ModelManager(object):
    default_mflow_format = 'sklearn'
    default_mlflow_expr_name = 'model_manager_default_experiment'
    ''' Class for managing the retrieval and loading of ML models
        both from Azure and locally cached
    '''
    def __init__(self, loc:multi_path_string=None,
            prefix:Union[str,None]=None, model_name:Union[str,None]=None, 
            model:Union[str,None]=None, model_format:Union[str,None]=None, 
            env:Union[multi_path_string,EnvConfig]=None, 
            yml:Union[multi_path_string,YmlConfig]=None, 
            cache:Union[multi_path_string,CacheConfig]=None, 
            azure:Union[multi_path_string,AzureConfig]=None,
            istest=False, logger=None,
            error_no_file_found=True, debug=0) -> None:
        ''' ModelManager
                can be instantiate using existing config class objects or directories 
                in which relevant config files live, e.g., 
                    envcfg = EnvConfig()
                    cache = CacheConfig(cachepath='./')
                    # in this situation it is expected that only one azure_temp* folder 
                    # will exist, the "*" is used to make the code generic
                    azure_configs = glob(os.path.join(dir_containing_pkg, 'azure_temp*/*config*'))
                    yml_dir = os.path.dirname(azure_configs[0])
                    ModelManager(env=envcfg, yml=yml_dir, azure=azure_configs)

                or simply with, for example,
                    ModelManager('./')

            Only the yml and azure config class instantiations must find config files, the 
            cache and env configs can be generated without one. If a path is not provided for 
            a config type, then the base path will be attempted.

            Args:
                loc=None                a base path/location to search for config files
                prefix=None             the prefix to use in the cache folder name generation
                model_name=None         name of the model (can be extracted from the yml experiment file)
                model=None              an existing model with which to prepopulate the manager
                model_format=None       the MLflow pickling format (see mlflow._model_flavors_supported)
                env=None                path/loc or EnvConfig object
                yml=None                path/loc or YmlConfig object
                cache=None              path/loc or CacheConfig object
                azure=None              path/loc or AzureConfig object
                istest                  indicates a test is running, to connection to remote resources 
                                        will be artificial
                logger                  the logging object or log-getter function
                error_no_file_found=True error if files are not found for azure or yml
                debug=0                 output detail logging level
            Returns: ModelManager() return a ModelManager object...this init explicitly returns None
        '''
        self.base_loc = (loc if loc is None else (
            [path.realpath(l) for l in loc] if isinstance(loc, list) else path.realpath(loc)
        ))
        self.error_no_file_found = error_no_file_found
        self.prefix = prefix
        self.debug = debug
        self.istest = istest

        self.logger = get_stdout_logger(self.__class__.__name__,self.debug) if logger is None else (
            logger(self.__class__.__name__, self.debug) if callable(logger) else logger)
        self.logger.setLevel(log_level_dict[self.debug])

        self.yml_config = self.cache_config = self.azure_config = self.env_config = None
        self.set_configs(env=env, cache=cache, yml=yml, azure=azure)
        self.refresh_model_details(model_name=model_name, model_format=model_format)
        
        self.clear_model_cache()
        self._model = model
        self._model_info = self._model_info_cache = None
        if self._current_model_name and self._model is not None:
            self._model_cache[self._current_model_name] = self._model
            if self._current_model_version is not None:
                self._model_cache[(self._current_model_name,self._current_model_version)
                    ] = self._model
        
    def __repr__(self) -> str:
        return self.__class__.__name__ + ':\n' + '\n'.join([repr(t) for t in self.configtuple])

    def clear_model_cache(self) -> None:
        self._model_cache = dict()

    def refresh_model_details(self, model_name=None, model_format=None):
        if model_name is not None:
            self._current_model_name = model_name
        elif self.yml_config is not None and 'model_name' in self.yml_config:
            self._current_model_name = self.yml_config['model_name']
        else:
            self._current_model_name = None
        if self._current_model_name is not None and (':' in self._current_model_name):
            self._current_model_version = int(self._current_model_name.split(':')[-1])
            self._current_model_name = self._current_model_name.split(':')[0]
        else:
            self._current_model_version = None
        self.get_model_versions(check_current=True)
        if model_format is not None:
            self._current_model_format = model_format
        elif self.yml_config is not None and 'mlflow_model_type' in self.yml_config:
            self._current_model_format = self.yml_config['mlflow_model_type']
        else:
            self._current_model_format = None
        assert self._current_model_format is None or (
            self._current_model_format in mlflow._model_flavors_supported), (
                f'unsupported mlflow model format specified: {self._current_model_format};\n'
                f'allowable formats include: {mlflow._model_flavors_supported}')

    @property
    def configtuple(self):
        ''' returns tuple of all config setups
            env_config, cache_config, yml_config, azure_config
        '''
        return self.env_config, self.cache_config, self.yml_config, self.azure_config

    def set_configs(self, env=None, cache=None, yml=None, azure=None) -> None:
        ''' Set the configuration objects
            
            Args:
                cache=None (Pathlike or CacheConfig)
                yml=None (Pathlike or YmlConfig)
                env=None (Pathlike or EnvConfig)
                azure=None (Pathlike or AzureConfig)

            Returns: was_set (bool): indicates whether a config was updated
        '''
        has_base_loc = (self.base_loc is not None) and isinstance(self.base_loc,(PathLike,str,list))

        was_set = False
        this_set = True
        env_paths = []
        if env is None and has_base_loc:
            env = self.base_loc
        if env is not None:
            if (isinstance(env, (PathLike,str)) and path.exists(env)) or (
                    isinstance(env,list) and any(isinstance(l,(str,PathLike)) for l in env)):
                self.env_config = EnvConfig(env, error_no_file_found=False, debug=max(self.debug-1,0))
                env_paths = (env if isinstance(env,list) else [env])
            elif isinstance(env,EnvConfig):
                self.env_config = env
            else:
                this_set = False
                raise TypeError(f'input "env" of type {type(env)} is not accepted')
        else:
            self.env_config = EnvConfig(error_no_file_found=False, debug=max(self.debug-1,0))
            warn('env config file/loc not provided, using only ENV variables')
        if ('CONFIG_PATH' in self.env_config):
            locs = [self.env_config['CONFIG_PATH']]
            locs.extend(env_paths)
            self.env_config = EnvConfig(locs, error_no_file_found=False, debug=max(self.debug-1,0))
            self.logger.debug(f'after using RSI_CONFIG_PATH, env config is\n: {self.env_config}')
        was_set = was_set or this_set

        self.logger.debug(f'Env config: {self.env_config}')

        has_config_path = ('CONFIG_PATH' in self.env_config)

        self.istest = self.istest or (('IS_TESTING' in self.env_config) and (
            self.env_config['IS_TESTING'].lower() == 'true'))
        if ('IS_TESTING' in self.env_config):
            self.logger.debug('testing mode forced by ENV variable')
        if not(isinstance(cache, CacheConfig)):
            if ('ML_API_CACHE_LOC' in self.env_config):
                cache = self.env_config['ML_API_CACHE_LOC']
            elif cache is None and has_base_loc:
                cache = self.base_loc

        if not(isinstance(yml, YmlConfig)):
            if has_config_path:
                yml = self.env_config['CONFIG_PATH']
            elif yml is None and has_base_loc:
                yml = self.base_loc

        if not(isinstance(azure, AzureConfig)):
            if has_config_path:
                azure = self.env_config['CONFIG_PATH']
            elif azure is None and has_base_loc:
                azure = self.base_loc

        for input, class_var, kwargs, config_class in zip(
                [cache, yml, azure],
                ['cache_config', 'yml_config', 'azure_config'],
                [dict(error_no_file_found=False, prefix=self.prefix), 
                    dict(error_no_file_found=(has_config_path and self.error_no_file_found)), 
                    dict(error_no_file_found=(has_config_path and self.error_no_file_found),
                        testing=self.istest)
                ],
                [CacheConfig, YmlConfig, AzureConfig]):
            # if input is not None:
            this_set = True
            if input is None or ((isinstance(input, (PathLike,str)) 
                    # and path.exists(input)
                    )) or (
                    isinstance(input,list) and any(
                        [isinstance(l, (PathLike,str))
                        # and path.exists(l) 
                        for l in input])):
                if self.debug > 3:
                    self.logger.info('Config detail: ' + str((class_var, input, config_class)))
                self.__dict__[class_var] = config_class(input, debug=self.debug, **kwargs)
            elif isinstance(input, config_class):
                self.__dict__[class_var] = input
            else:
                this_set = False
                raise TypeError(f'input "{class_var.split("_")[0]}" of type {type(input)} is not accepted')
            was_set = was_set or this_set

        self.refresh_model_details()
        return was_set

    def is_config_unset(self, test_env=True, test_azure=True):

        return (self.cache_config is None) or (test_env and (self.env_config is None)
            ) or (test_azure and (self.azure_config is None))

    def get_model_versions(self, name=None, version=None, check_current=False):
        if isinstance(self.azure_config, AzureConfig) and (
                self.azure_config.Workspace is not None) and not(self.azure_config.testing):
            model_list = Model.list(workspace=self.azure_config.Workspace, 
                name=(self._current_model_name if name is None else name))
            self._available_model_versions = [m.version for m in model_list]
        else:
            self._available_model_versions = None
        if check_current:
            self.check_model_versions(version=version)
    
    def check_model_versions(self, version=None):
        ver = (version if version is not None else self._current_model_version)
        if self._available_model_versions and ver:
            assert ver in self._available_model_versions, (
                f'the version specified [{ver}] is not among '
                f'those available in Azure [{self._available_model_versions}]')

    def get_model_fn_from_env(self, model_name, version=None, debug=0):
        ''' get_model_fn_from_env: get the local filename from env var 
                if already stored
            Args: model_name (str), version (int,None)=None, debug=0
            Returns: modelfn (str,Pathlike)
        '''
        modelfn = None
        if self.env_config is not None:
            if 'MODEL_DOWNLOADED_URL' in self.env_config:
                modelfn = self.env_config['MODEL_DOWNLOADED_URL']
                if model_name not in modelfn:
                    # the model name should be in the model file url
                    modelfn = None
                try:
                    version_current = modelfn.split(model_name)[-1].split(path.sep)[0]
                except (AttributeError,IndexError):
                    version_current = None
                if version is not None and str(version) == version_current:
                    self.logger.warning(f"found env [MODEL_DOWNLOADED_URL] = '{modelfn}' "
                        f"but could not find version: {version}")
                    modelfn = None
                if modelfn:
                    self.logger.warning(f"found env [MODEL_DOWNLOADED_URL] = '{modelfn}'")
            if modelfn is not None and not(path.exists(modelfn)):
                # if the local file has been remove, we will not try to load it
                modelfn = None
                self.logger.warning('MODEL_DOWNLOADED_URL reference set, but model at url does not exist')
        return modelfn

    def record_model_in_env(self, modelfn):
        """ Once the model file has been create, this functions executes 
            optional recording of reference to model file url in environment 
            config.
        """
        if isinstance(self.env_config, EnvConfig):
            loc  = (path.join(self.env_config['CONFIG_PATH'], 'model_loc_config.env') 
                if 'CONFIG_PATH' in self.env_config else None)
            self.env_config.setkeyvalue('MODEL_DOWNLOADED_URL', modelfn, envfile=loc)
        else:
            warn('record_model_in_env() execute, but no valid EnvConfig object available')

    def load_model(self, model_name=None, _from='azure', version=None, 
            model_format=None, model_update=False, debug=0):
        ''' load_model: Retrieve sklearn/spacy/et al. 
            search order:
                - first using lookup into model cache
                - then search local env / filesystem for an existing model to load
                - if not present, then try to load from Azure
            Args:
                model_name (str,None)=None      name of the model
                _from (str)='azure'             from where the model should be loaded
                                                (can be 'azure', 'file', 'db'; although 
                                                db does not work yet)
                version (int,None)=None         model version
                model_format (str,None)=None    model format; should be one of 
                                                mlflow._model_flavors_supported
                model_update(bool)=False        whether this should force a model update
                debug(int)=0                    how much talking to do
            Returns tuple of:
                sklearn unpickled model or loaded mlflow model
                model_info or None
        '''
        _model_format_in = model_format
        if model_format is None:
            if ((model_name is None) or (model_name in self._current_model_name)) and (
                    self._current_model_format is not None):
                model_format = self._current_model_format

        if model_name is None:
            model_name = self._current_model_name
        assert model_name is not None, 'model_name not provided and not found in .yml config (or no config found)'
        if version is None:
            if self._current_model_version is not None:
                version = self._current_model_version
        else:
            self.check_model_versions(version)
        assert self.cache_config is not None, 'set_configs() has not been called to set the cache object'
        model_pipe = model_info = None
        if self._model_cache is None:
            self._model_cache = dict()
        if self._model_info_cache is None:
            self._model_info_cache = dict()
        if not(model_update) and (any(k.startswith(model_name) for k in self._model_cache
                ) and version is None) or (version is not None and ((model_name,version
                ) in self._model_cache)):
            # load model from the memory cache if applicable
            if version is None:
                if model_name in self._model_cache:
                    model_pipe = self._model_cache[model_name]
                    model_info = self._model_info_cache[model_name]
                else:
                    # get the most recent model
                    version_model = {mn[1]: model for mn, model in self._model_cache.items()
                        if isinstance(mn,tuple) and mn[0] == model_name}
                    version_info = {mn[1]: minfo for mn, minfo in self._model_info_cache.items()
                        if isinstance(mn,tuple) and mn[0] == model_name}
                    latest = list(sorted(version_model.keys()))[-1]
                    model_pipe = version_model[latest]
                    model_info = (version_info[latest] if latest in version_info else None)

            else:
                model_pipe = self._model_cache[(model_name,version)]
                model_info = (self._model_info_cache[(model_name,version)] 
                    if (model_name,version) in self._model_info_cache else None)
        else:
            if not(model_update) and (_from == 'file' or self.istest):
                # load model from file if already present/downloaded
                model_file_loc = self.cache_config.get_model_cache_loc()
                if model_format in mlflow._model_flavors_supported:
                    modelfn = self.get_model_fn_from_env(model_name, debug=max(self.debug,debug))
                    if modelfn is not None:
                        model_pipe = mlflow.__dict__[model_format].load_model(modelfn)
                if model_pipe is None:
                    modelfns = glob(path.join(model_file_loc, f'*{model_name}*.pkl'))
                    if len(modelfns):
                        modelfn = max(modelfns, key=path.getctime)
                        try:
                            with open(path.join(model_file_loc, modelfn), 'rb') as f:
                                model_pipe = pickle.loads(f.read())
                                if (debug or self.debug):
                                    self.logger.warning('Model read successfully!')
                        except:
                            self.logger.warning('unable to load model from local file')
            if (model_pipe is None or _from == 'azure') and (isinstance(self.azure_config, AzureConfig
                    ) and not(self.azure_config.testing)):
                # if loading locally fails, try from Azure
                assert isinstance(self.azure_config, AzureConfig), (
                    "requested Azure retrieval of model, AzureConfig data not available")
                model_info, model_format, isMLflow = self.get_check_cloud_model_details(
                    model_name, version, _model_format_in)
                # retrieve the model
                modelfn = self.get_model_fn_from_env(model_name, version=version, debug=max(self.debug,debug))
                if modelfn is None or len(modelfn.strip()) == 0:
                    version_print = ((model_info.version if (
                        model_info is not None) and (model_info.version is not None) else ""
                        ) if version is None else version)
                    self.logger.warning(f'env MODEL_DOWNLOADED_URL not set, loading model {model_name}'
                        f'{(":"+str(version_print) if version_print is not None else "")} from Azure')
                    
                    modelfn = Model.get_model_path(model_name, version=version,
                        _workspace=self.azure_config.Workspace)
                    self.logger.warning(f'Model downloaded succesfully to {modelfn}!')
                    modelfn = path.realpath(modelfn)
                if isMLflow:
                    model_pipe = mlflow.__dict__[model_format].load_model(modelfn)
                else:
                    # model_file_loc = self.cache_config.get_model_cache_loc()
                    # model_in_ws = Model(workspace=self.azure_config.Workspace, name=model_name)
                    # modelfn = model_in_ws.download(model_file_loc,exist_ok=True)  
                    warn_msg = (f'attempting to load non-MLflow model type[{model_format}] '
                        'or problem loading; attempting unpickling')
                    warn(warn_msg)
                    self.logger.warning(warn_msg)
                    try:
                        with open(modelfn,'rb') as fin:
                            model_pipe = pickle.load(fin.read())
                    except Exception as e:
                        warn_msg = (f'issue running unpickle / back up model load: {str(e)}')
                        warn(warn_msg)
                        self.logger.warning(warn_msg)
                if model_pipe is None:
                    # back up - attempt to load from Azure Workspace
                    model_file_loc = self.cache_config.get_model_cache_loc()
                    warn_msg = (f'attempting to load unknown model type[{model_format}] '
                        'or problem loading; attempting unpickling')
                    self.logger.warning(warn_msg)
                    model_in_ws = Model(workspace=self.azure_config.Workspace, name=model_name)
                    modelfn = model_in_ws.download(model_file_loc,exist_ok=True)  
                    with open(modelfn,'rb') as fin:
                        model_pipe = pickle.load(fin.read())
                self.record_model_in_env(modelfn)
            elif _from == 'db':
                err = 'DB model saving/loading not yet set up'
                self.logger.fatal(err)
                raise NotImplementedError(err)
            # save the model to the memory cache
            if version is not None:
                self._model_cache[(model_name,version)] = model_pipe
                if model_info is not None:
                    self._model_info_cache[(model_name,version)] = model_info
            else:
                self._model_cache[model_name] = model_pipe
                if model_info is not None:
                    self._model_info_cache[model_name] = model_info
                    if model_info.version is not None:
                        self._model_cache[(model_name, model_info.version)] = model_pipe
                        self._model_info_cache[(model_name, model_info.version)] = model_info
        self._model = model_pipe
        self._model_info = model_info

        return model_pipe, model_info

    @property
    def model(self):
        return self._model

    @property
    def modelname(self):
        return self._current_model_name

    @property
    def version(self):
        return self._current_model_version

    @property
    def mformat(self):
        return self._current_model_format

    def allmodelversions(self, update=False):
        if update:
            self.get_model_versions()
        # return a copy
        return list(tuple(self._available_model_versions))

    @property
    def modeldetails(self):
        return (self._current_model_name, self._current_model_version, self._current_model_format)

    def get_check_cloud_model_details(self, model_name, version=None, model_format=None):
        try:
            if version is not None:
                self.get_model_versions(name=model_name, version=version, check_current=True)
        except AssertionError:
            warn(f'could not find valid version: {version} for model "{model_name}"')
            version = None
        mlflow_details, minfo = {}, None
        if isinstance(self.azure_config.Workspace, Workspace):
            minfo = Model(self.azure_config.Workspace, name=model_name, version=version)
            minfo.properties['flavors']
            mlflow_details = ({} if 'model_json' not in minfo.properties else
                json.loads(minfo.properties['model_json']))
            fmts = [o for o in minfo.properties['flavors'].split(',') 
                if o in mlflow._model_flavors_supported]
            if len(fmts) > 1:
                err = ('found more than one mlflow model flavor option for '
                f'model saved in Azure: {minfo.properties["flavors"]}')
                self.logger.fatal(err)
                raise AssertionError(err)
            if len(fmts) and self._current_model_format is None or self._current_model_format != fmts[0]:
                if self._current_model_format != fmts[0]:
                    warn_msg = (f'updating model mlflow format to {fmts[0]}, specified load '
                        'format did not match that recorded in Azure')
                    self.logger.warning(warn_msg)
                    warn(warn_msg)
                self._current_model_format = fmts[0]
        if self._current_model_format is None:
            self._current_model_format = self.default_mflow_format
            warn_msg = (f'assuming model is the "{self.default_mflow_format}" flavor of mlflow saved models')
            self.logger.warning(warn_msg)
            warn(warn_msg)
        if model_format is None:
            model_format = self._current_model_format

        isMLflow = ('mlflow_version' in mlflow_details) and (
            model_format in mlflow._model_flavors_supported)

        return minfo, model_format, isMLflow

    # NOTE: (TODO) save functionality is not yet fully working

    def save_model(self, model_pipeline, predict_type, model_name=None, ts=None, 
            datahash=None, jsonmodel=False, nowritereturn=False, model_format=None,  
            to='file', simple_jsonify=False, allow_overwrite=True, save_model_env_ref=False, debug=0):
        debug = max(debug, self.debug)
        if model_format is None:
            if (model_name is None or model_name == self._current_model_name
                    ) and self._current_model_format is not None:
                # don't want ot use the format specified in the yml file unless the 
                # model matches or will be pulled from the yml file
                self.logger.warning('model format not supplied, assuming format '
                        f'[{self._current_model_format}] from yml file configuration')
                model_format = self._current_model_format
            else:
                # assert False,'assuming model format'
                warn(f'assuming model is the "{self.default_mflow_format}" flavor of mlflow saved models')
                model_format = self.default_mflow_format

        if model_name is None and self._current_model_name is not None:
            model_name = self._current_model_name
        elif not(isinstance(model_name,str)) and model_name:
            model_name = '.'.join([
                'model', model_pipeline[-1].__class__.__name__, 
                'TS-'+str(pd.Timestamp.now(tz='utc').timestamp() if ts is None else ts),
                'hash-'+str(datahash), 
                predict_type])
        if jsonmodel or nowritereturn and not(to == 'file'):
            self.logger.info(f'jsonmodel: {jsonmodel}, nowritereturn: {nowritereturn}')

            # record model info for unit tests
            model_elements = jstringify_model_object(model_pipeline, simple_jsonify=simple_jsonify)
            if nowritereturn:
                if isinstance(model_pipeline, MultipleOutputModel):
                    return model_name, model_elements
                else:
                    return model_name, {predict_type: model_elements}
            else:
                if isinstance(model_pipeline, MultipleOutputModel):
                    model_data = json.dumps(model_elements)
                else:
                    model_data = json.dumps({predict_type: model_elements})

        if not(jsonmodel):
            model_data = model_pipeline
        if to == 'file':
            mfn, _model = self.__class__.save_model_to_file(model_data, model_name, cache_config=self.cache_config, 
                jsonmodel=jsonmodel, model_format=model_format, allow_overwrite=allow_overwrite, debug=debug)
        elif to == 'azure':
            mfn, _model = self.__class__.save_model_to_azure(model_pipeline, model_name,
                azure_config=self.azure_config, debug=debug, allow_overwrite=allow_overwrite,
                model_format=model_format, cache_config=self.cache_config, 
                mlflow_run_name=(self.default_mlflow_expr_name 
                    if self.yml_config is None or 'name' not in self.yml_config
                    else self.yml_config['name']))
        elif to == 'db':
            mfn, _model = self.__class__.save_model_to_db(model_data, model_name, debug=debug)
        else:
            NotImplementedError(f'unknown model storage mode: "{to}"')
        if (to in ['file', 'azure']) and save_model_env_ref:
            self.record_model_in_env(mfn)
        return mfn, _model

    @staticmethod
    def save_model_to_azure(model_pipeline, mname, azure_config, **kwargs):
        ''' 
            Args;
                model_pipeline
                mname
                model_format=None
                cache_config (optional, req. if model is to be generic pickled, vs using mlflow)
                **kwargs - must pass `cache_config` through to `save_model_to_file` and 
                    optionally `model_format`
            Returns:
                registration status
        '''
        if ('debug' in kwargs) and kwargs['debug'] > 1:
            print('running `save_model_to_azure`')
        assert 'jsonmodel' not in kwargs or not(kwargs['jsonmodel']), 'cannot interact with Azure for `jsonmodel=True`'
        model_data = pickle.dumps(model_pipeline)
        fn, _ = ModelManager.save_model_to_file(model_data, mname, **kwargs)
        # save the model to the cloud
        return fn, Model.register(model_name=mname, 
            model_path=fn, workspace=azure_config.Workspace)

    @staticmethod
    def save_model_to_file(outdata, outfn, cache_config, model_format=None, jsonmodel=False, 
            allow_overwrite=True, debug=0):
        debug and print('running `save_model_to_file`')
        wrt_success, isMLflow = False, ((model_format is not None) and 
            (model_format in mlflow._model_flavors_supported))
        faccess, writeto = ('w' if jsonmodel else 'wb'), path.join(
            cache_config.get_model_cache_loc(), outfn + ('.json' if jsonmodel else ('' if isMLflow else '.pkl')))
        if not(jsonmodel) and isMLflow:
            # incorporate mlflow tools to properly save models to file for upload to Azure ML
            # https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-mlflow-models?tabs=fromjob%2Cmir%2Csdk
            if path.exists(writeto) and allow_overwrite:
                try:
                    remove(writeto)
                except IsADirectoryError:
                    rmtree(writeto, ignore_errors=False, onerror=None)
            mlflow.__dict__[model_format].save_model(
                outdata, path=writeto, input_example=None)
            wrt_success = True
        else:
            if not(jsonmodel):
                outdata = pickle.dumps(outdata)
            with open(writeto, faccess) as f:
                f.write(outdata)
                wrt_success = True
        if debug:
            if wrt_success:
                print('\n'.join([
                    f'Model write success! (output model file: {outfn} (isMLflow: {isMLflow})',
                    f'    size: {path.getsize(writeto)/2**10:.3g}kB',
                    f'    location: {cache_config.get_model_cache_loc()}']))
            else:
                warn_msg = f'unable to write mode [{outfn}] to file'
                warn(warn_msg)
        return writeto, outdata

    @staticmethod
    def save_model_to_db(*args,**kwargs):
        if ('debug' in kwargs) and kwargs['debug'] > 1:
            print('running `save_model_to_db`')
        raise NotImplementedError('DB model saving not yet set up')
        # return fn, model