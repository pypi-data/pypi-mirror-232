'''Configuration setup for local/remote ML model and data storage'''
# from distutils.log import warn
from warnings import warn
from os import path, mkdir
from rsidatasciencetools.config.baseconfig import get_stdout_logger, log_level_dict

class CacheConfig(object):
    _path = None
    def __init__(self,cachepath=None, prefix:str=None, 
            error_no_file_found:bool=False, logger=None, debug:int=0):
        self.prev_apidata_cache = None
        self.prev_traindata_dir = None
        self.prev_models_cache = None
        self.prefix = prefix
        self.cache_folder_prefix = ('.rsi_aml_api_' if self.prefix is None 
            else '.' + '_'.join([self.prefix,'aml_api_']))
        self.debug = debug
        self.logger = get_stdout_logger(self.__class__.__name__,debug) if logger is None else logger
        if cachepath is None:
            if error_no_file_found:
                raise IOError('cachepath not specified')
            default = path.dirname(path.abspath(__file__))
            warn_msg = (f'setting up a default path for the CacheConfig: {default}')
            
            self._defaultpath = default
        else:
            if isinstance(cachepath,list):
                # TODO: could check to see which of these paths actually exisits
                cachepath  = cachepath[0]
            self._path = cachepath

    def __str__(self) -> str:
        cache_loc =  [f.__name__ + '=' + f(dryrun=True) 
            for f in [self.get_api_file_cache, self.get_model_cache_loc, self.get_train_data_dir]]
        return self.__class__.__name__ + ': ' + ', '.join(cache_loc)

    def __repr__(self) -> str:
        cache_loc =  [f'   {f.__name__:20s}: ' + f(dryrun=True)
            for f in [self.get_api_file_cache, self.get_model_cache_loc, self.get_train_data_dir]]
        cache_loc.insert(0, self.__class__.__name__ + ': ')
        return '\n '.join(cache_loc)

    def get_api_file_cache(self, dryrun=False):
        from os import environ
        if self._path is None:
            if 'RSI_ML_API_CACHE_LOC' in environ:
                self._path = environ['RSI_ML_API_CACHE_LOC']
            else:
                self._path = self._defaultpath
        assert not(self.cache_folder_prefix.startswith('.rsi')), 'cache prefix is .rsi'
        cache_loc = path.join(self._path, self.cache_folder_prefix + 'incoming_file_cache')
        if not path.exists(cache_loc) and not(dryrun):
            mkdir(cache_loc)
        if self.prev_apidata_cache is not None and self.prev_apidata_cache != cache_loc:
            warn_msg = ('api file cache location has changed!!!')
            warn(warn_msg)
            self.logger.warning(warn_msg)
        self.prev_apidata_cache = cache_loc
        return cache_loc

    def get_model_cache_loc(self, dryrun=False):
        from os import environ
        if self._path is None:
            if 'RSI_ML_API_CACHE_LOC' in environ:
                self._path = environ['RSI_ML_API_CACHE_LOC']
            else:
                self._path = self._defaultpath
        models_loc = path.join(self._path, self.cache_folder_prefix + 'model_cache')
        if not path.exists(models_loc) and not(dryrun):
            mkdir(models_loc)
        if self.prev_models_cache is not None and self.prev_models_cache != models_loc:
            warn_msg = ('model cache location has changed!!!')
            warn(warn_msg)
            self.logger.warning(warn_msg)
        self.prev_models_cache = models_loc
        return models_loc

    def get_train_data_dir(self, dryrun=False):
        from os import environ
        if 'RSI_TRAINDATADIR' in environ:
            train_data_loc = environ['RSI_TRAINDATADIR']
        else:
            train_data_loc = path.join(
                (self._defaultpath if self._path is None else self._path),
                '.rsi_aml_train_data' if self.prefix is None 
                else '.' + '_'.join([self.prefix,'rsi_aml_train_data']))
        if not path.exists(train_data_loc) and not(dryrun):
            mkdir(train_data_loc)
        if self.prev_traindata_dir is not None and self.prev_traindata_dir != train_data_loc:
            warn_msg = ('training data location has changed!!!')
            warn(warn_msg)
            self.logger.warning(warn_msg)
        self.prev_traindata_dir = train_data_loc
        return train_data_loc
