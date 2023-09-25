from abc import ABC, abstractmethod
from asyncore import write
from email.mime import multipart
from os import environ, path, PathLike, listdir, curdir
from string import printable
import yaml
from glob import glob
from warnings import warn
import logging
import json
import time
import sys
from rsidatasciencetools.utils import log_level_dict



def load_json(file):
    with open(file,'r') as f:
        data = json.load(f)
    return data

def load_yaml(file):
    with open(file,'r') as f:
        data = yaml.safe_load(f)
    return data

def load_env(file, search_prefix, env_comment_marker='#'):
    data = {}
    warn_invalid_viable_lines = False
    with open(file,'r') as f:
        lines = [ln for ln in f.read().split('\n') 
            if len(ln) > 0 and not(ln.strip().startswith(env_comment_marker))]
        if len(lines) == 0:
            print(f'no config data found in: {file}')
            return {}
        for ln in lines:
            if '=' not in ln:
                if not(ln.startswith(env_comment_marker)) and len(ln.strip()):
                    warn_invalid_viable_lines = True
                continue
            v = '='.join(ln.split('=')[1:])
            if "'" not in v:
                v = v.split(env_comment_marker)[0].strip()
            else:
                v = v.strip().strip("'")
            k = ln.split('=')[0]
            k = k.strip()
            if k.lower().startswith('export ') and len(k) > 7:
                k = k[:7].lower() + k[7:]
                k = k.split('export ')[-1]
            if search_prefix is not None and k.startswith(search_prefix):
                k = ''.join(k.split(search_prefix)[1:])
            # strip out comments and whitespace, and then assign to the LHS key
            value = v = v.split(env_comment_marker)[0].strip() 
            try:
                value = float(v)
            except (TypeError,ValueError):
                pass
            try:
                value = int(v)
            except (TypeError,ValueError):
                pass
            if isinstance(v,str) and (v.lower() == 'false' or v.lower() == 'true'):
                value = True if v.lower() == 'true' else False
            data[k] = value
    if warn_invalid_viable_lines:
        warn(f'not every viable line has an "=" delimiting key-value pairs in: {file}')
    return data


class Config(ABC):
    """
    Configuration base class.

    Allows scanning of local directory or provided folders
    for the relevant configuration files. Reads in these
    parameters or environment variables and makes them
    accessible in a dictionary-like manner.
    """
    search_str = None
    search_prefix = None
    ext = 'json'
    base_str = '*config'
    comment_marker = '#'
    key_check_primary = None
    obfusc_value_exceptions = ['localhost', '127.0.0.1']
    file_has_pw_keys = ['password', 'pw']

    def __init__(self, *args, child=None, debug=0, base_str=None,
            error_no_file_found=None, ext=None, read_all=False,
            auto_update_paths=False, key_check_primary=None, logger=None, **kwargs):
        """
        Args:
            (first position arg) (str/pathlike, optional): directory 
                in which files should be found or file from which 
                config params should be aggregated 
            params (dict,optional): base set of parameters 
                with which to populate the config object
            dir (str/pathlike, optional): the directory in 
                which to look for config files (default in 
                the current working directory)
            debug=1 (int): debug level
            base_str='*config' (str): substring to search for when 
                sifting through relevant configuration files
            search_str=None (str or list[str]): secondary string(s)
                with which to filter the config files found in the 
                specified directory
            error_no_file_found=True (bool): raise an error if no
                configuration file is found
            ext='json' (str): the extension to look for when
                searching for config files (default will change
                depending on the child config class type)
            key_check_primary=None (str): the key of the parameter
                key-value pair that must exist in the primary config
                file (i.e., there may be multiple .yml or .env files,
                but this key will indicate which is the correct one
                to use)
            auto_update_paths=False (optional bool): whether to attempt to
                update relative paths with the path to the config
                file that has been read
            logger=None (optional logging object)
        """
        self._config = {}
        self.loc = None
        self.file_loc = None
        self.file_locs = []
        self.file_has_passwords = None
        if base_str is not None:
            self.base_str = base_str
        self.debug = debug
        self.read_all = read_all
        self.auto_update_paths = auto_update_paths
        self.obfuscate_on_stringify = []
        self.obfuscate_func = lambda x, _type: '****'
        if ext is not None:
            self.ext = ext
        if key_check_primary is not None:
            self.key_check_primary = key_check_primary
        self.config_str_selector = None
        self.child = child
        self.logger = get_stdout_logger(self.__class__.__name__,self.debug) if logger is None else (
            logger(self.__class__.__name__, self.debug) if callable(logger) else logger)
        self.error_no_file_found = False if ('RSI_CONFIG_PATH' in environ
            and (error_no_file_found is None)) else (
                True if error_no_file_found is None else error_no_file_found)

        self.refresh_config(*args, **kwargs)
        if (('CONFIG_PATH' in self._config) or ('RSI_CONFIG_PATH' in environ)
                ) and len([k for k in self._config.keys() if k != 'CONFIG_PATH']) == 0:
            # only search for the 'CONFIG_PATH' env variable if the config is
            # empty; otherwise, just use the config found from the original
            # directory to which the config initialization was pointed
            self.error_no_file_found = error_no_file_found
            args = list(args)
            if 'CONFIG_PATH' in self._config:
                args.insert(0, self._config['CONFIG_PATH'])
            else:
                args.insert(0, environ['RSI_CONFIG_PATH'])
            args = tuple(args)
            self.refresh_config(*args, **kwargs)
        
        self.logger.info(self.__repr__())

    def refresh_config(self, *args,**kwargs):
        if len(args):
            if isinstance(args[0],(str,PathLike)):
                self.loc = path.realpath(args[0])
                self.logger.debug(f'{self.child.__class__.__name__}: using provided location: {self.loc}')
                args = args[1:]
            elif isinstance(args[0],list):
                assert all(isinstance(l,(str,PathLike)) for l in args[0]), (
                    'providing urls must be valid PathLike strings')
                self.loc = [path.realpath(l) for l in args[0]]
                self.logger.debug(f'{self.child.__class__.__name__}: using provided locations: {self.loc}')
                args = args[1:]
            elif isinstance(args[0],dict):
                kwargs.update(args[0])
                args = args[1:]
        if 'search_str' in kwargs:
            self.search_str = (kwargs['search_str']
                if isinstance(kwargs['search_str'],list) 
                else [kwargs['search_str']])
        assert self.search_str is None or (isinstance(self.search_str, list) and 
                all(isinstance(el,str) for el in self.search_str)), (
            'search_str should be a list of strings')
        if self.child is not None:
            self.child._config = self.child.setup_config(*args,**kwargs)
            self.child.validate(self.child._config)
        else:
            self._config = self.setup_config(*args,**kwargs)
        if self.auto_update_paths:
            self.auto_prepend_loc_url()

    @abstractmethod
    def validate(self,*args, **kwargs):
        raise NotImplementedError('this method should be implemented by the child class')

    def get_obfuscated(self, k, v, shorten=80):
        rtn = (v if (v is None) or not(any(kk.lower() in k.lower() 
                    for kk in self.obfuscate_on_stringify)) or any(
                vv.lower() in v.lower() for vv in self.obfusc_value_exceptions) 
            else self.obfuscate_func(v,k))
        if not(isinstance(rtn, str)):
            rtn = str(rtn)
        if shorten and len(rtn) > shorten:
            return rtn[:int(shorten/2)] + '...' + rtn[-int(shorten/2):]
        else:
            return rtn

    def __repr__(self, **kwargs):
        return (self.__class__.__name__ + 
            ' | {\n   ' + '\n   '.join([f'{k}:{self.get_obfuscated(k, v, **kwargs)}' 
                for k, v in self._config.items()]) + ' }')

    def __contains__(self,key):
        return key in self._config

    def __getitem__(self,key):
        return self._config[key]
    
    def __iter__(self):
        for k in self._config:
            yield k

    def get(self,key,default=None,key_error=False):
        if key not in self._config:
            if key_error:
                raise KeyError(f'key "{key}" not found')
            return default
        return self._config[key]

    def setkeyvalue(self,key,value=None,env=False,check_value=True,write_to_file=None):
        '''
        NOTE: trying to ensure no one accidentally 
        overrides a parameter of importance by forcing 
        this call instead of overloading the 
        operator (i.e., via __setitem__)
        '''
        if isinstance(key,dict):
            for k,v in key.items():
                self.setkeyvalue(k, v, env=env, write_to_file=write_to_file)
            return
        elif check_value:
            assert value is not None, 'value not provided'
        self._config[key] = value
        if env:
            environ[('' if self.search_prefix is None else self.search_prefix) + key] = str(value)
        if write_to_file:
            with open(write_to_file,'w') as f:
                if env:
                    envkey = ('' if self.search_prefix is None else self.search_prefix) + key
                    f.write(f'{envkey.upper()}={value}\n')
                else:
                    f.write(json.dumps({key: value}, indent=3))

    def auto_prepend_loc_url(self):
        ''' use the base config file url to prepend the path to
            the referenced local file urls
        '''
        if not(len(self.file_locs) and len(self._config)):
            return
        locs2try = list(set([path.split(f)[0] for f in self.file_locs]))
        for k, el in self._config.items():
            if isinstance(el, (PathLike,str)) and not(path.isabs(el)):
                found = 0
                for loc in locs2try:
                    if path.exists(path.join(loc,el)):
                        self.setkeyvalue(k,path.join(loc,el))
                        found += 1
                if not(found):
                    self.logger.debug((f'tried to update path of URL config param [{k}] to be '
                        f'absolute, but file ["{"-or-".join(locs2try)}" + "{el}"] '
                        'does not exist'))
                elif found > 1:
                    warn('found multiple extant files for the auto-path expansion '
                        'from base paths of config file(s), using the last one')


    @property
    def file_locs_no_pws(self):
        return [f for f, has_pw in zip(self.file_locs,
            self.file_has_passwords) if not(has_pw)]

    @property
    def primary_path(self):
        self.logger.info('Config.primary_path() => self.file_loc:', self.file_loc, 
                             'self.file_locs:', self.file_locs, 'self.loc:', self.loc)
        if self.file_loc is not None and len(self.file_loc):
            loc = (self.file_loc[0] if isinstance(self.file_loc,list) and len(self.file_loc) else self.file_loc)
            if isinstance(loc, list) and len(loc) == 0:
                loc = self.loc
            else:
                if path.isdir(loc):
                    return loc
                else:
                    return path.dirname(loc)
        else:
            return self.loc

    def items(self,filter=None,contains=None,reject=None):
        for k,v in self._config.items():
            if filter is None and contains is None and reject is None:
                yield k,v
            else:
                if reject and (k in reject):
                    continue
                if not(filter) and not(contains):
                    yield k,v
                if filter and (k in filter):
                    yield k,v
                if contains and any((cc in k) for cc in contains):
                    yield k,v


    def dict_elem(self,**override):
        d = {k:v for k, v in self._config.items()}
        if len(override):
            d.update(override)
        return d

    def setup_config(self,*args,**kwargs):
        '''
        for inheriting classes reimplementing this function,
        they should contain the following 'setup_base_config` 
        call followed by custom overrides and then by key-word
        overrides
        '''
        _config = self.setup_base_config(*args,**kwargs)
        return self.override_config_file(_config,**kwargs)

    def setup_base_config(self,*args,**kwargs):
        ''' Automatically search the provided file or directory
            for database connection json/env/etc configuration.
        '''
        if self.loc is None:
            self.loc = path.abspath(path.curdir)
        multipaths = isinstance(self.loc,list)
        if not(multipaths) and path.isfile(self.loc):
            _files = [path.realpath(self.loc)]
            self.search_str = None
        else:
            if not(multipaths):
                loc = [self.loc]
            else:
                loc = self.loc
            _files = []
            for l in loc:
                if self.ext != 'env':
                    __files = glob(path.join(l,self.base_str+'*.'+self.ext))
                else:
                    __files = [path.join(l,f) for f in listdir(l) if f.endswith(self.ext)]
                _files.extend(__files)
        self.logger.info(f'{self.ext} files found: {_files}')

        # Only check for string search matches against the file itself (and
        # nothing in the fullpath up to the filename)
        files = [f for f in _files if self.search_str is None or 
            any([st.lower() in path.split(f)[-1].lower() for st in self.search_str])]

        self.logger.info(f'{self.ext} | using {self.search_str}, filtered files found: {files}')

        if self.ext != 'env' and len(files) > 1 and not(self.read_all):
            warn((f'in this directory found more than one [{self.base_str}*.{self.ext}] ' +
                f'file match for config type: {self.__class__.__name__}, ' +
                ('overriding / replacing according to read-in order' 
                    if self.read_all else 'using first file found')))
        if len(files) == 0:
            if self.error_no_file_found:
                raise IOError((f'could not find a .{self.ext} config '
                    f'file in {self.loc}:\n'
                    f'Files in this directory:\n{_files}'))
            elif (self.ext != 'env'):
                warn_msg = ('could not find config file in this directory, '
                    f'{self.__class__.__name__} object unpopulated')
                warn(warn_msg)
                self.logger.warning(warn_msg)
                self.logger.warning(f'director(y/ies) searched where no config files found: {self.loc}')
                self.file_loc, self.file_locs =  self.loc, [self.loc]
                return {}
            else:
                self.file_loc, self.file_locs =  self.loc, [self.loc]

        self.file_locs = files
        self.file_has_passwords = [False for f in files]
        if (self.ext != 'env') and not(self.key_check_primary):
            self.file_loc = (files if self.read_all else files[0])
        _config = {}
        if self.ext in ['yml', 'yaml', 'json']:
            if self.ext.lower() == 'json':
                reader = load_json 
            else:
                reader = load_yaml
            found_pkey = False
            for fi, _file in enumerate(files):
                file = path.realpath(_file)
                new = reader(file)
                self.logger.info(f'read file: {file} with keys:\n{list(new.keys())}')
                if any([any(kk in k for kk in self.file_has_pw_keys) for k in new.keys()]):
                    self.file_has_passwords[self.file_locs.index(_file)] = True
                    self.logger.info('    >>> updating file password status')
                if not(self.read_all) and (
                        (fi > 1 and not(self.key_check_primary)) or (
                        self.key_check_primary and found_pkey)):
                    continue

                if self.key_check_primary:
                    found_pkey = (self.key_check_primary.lower() in [
                        nk.lower() for nk in new.keys()])
                    if found_pkey:
                        if (self.key_check_primary not in new):
                            warn_msg = ("found matching config file with primary key, "
                                "but the letter case of the key string was mismatched")
                            warn(warn_msg)
                            self.logger.warning(warn_msg)
                        self.file_loc = file
                    if found_pkey or self.read_all:
                        _config.update(new)
                else:
                    _config.update(new)
                    if not(self.read_all):
                        break
        else:
            self.file_loc = files
            reader = lambda fn: load_env(fn, self.search_prefix, 
                env_comment_marker=self.comment_marker)
            if self.ext != 'env':
                warn_msg = 'attempting to parse as .env file, may not produce valid config'
                warn(warn_msg)
                self.logger.warning(warn_msg)
            warn_override = []
            _config = {}
            for _file in files:
                file = path.realpath(_file)
                __config = reader(file)
                for k in __config:
                    if k in _config:
                        warn_override.append(k)
                _config.update(__config)

            if warn_override:
                if len(files) > 1:
                    warn_msg = ('found more than one config file in this directory, '
                        f'overridden were: {warn_override}')
                    warn(warn_msg)
                    self.logger.warning(warn_msg)
                else:
                    err_msg = (f'found config variable more one time in this .{self.ext} ' 
                        f'file, overrides: {warn_override}')
                    self.logger.fatal(err_msg)
                    raise KeyError(err_msg)
        self._reader_used = reader
        return _config

    @staticmethod
    def get_env_overrides(search_prefix):
        if search_prefix is None:
            return {}
        from os import environ
        env_overrides = {}
        for k,v in environ.items():
            if k.startswith(search_prefix):
                value = v
                try:
                    value = float(v)
                except (TypeError,ValueError):
                    pass
                try:
                    value = int(v)
                except (TypeError,ValueError):
                    pass
                env_overrides[k.split(search_prefix)[-1]] = value
        return env_overrides

    def lowerkeys(self):
        return {k.lower():v for k, v in self._config.items()}
        
    def replace_config(self,new_config):
        self._config = new_config

    def override_config_file(self, _config, source='', **kwargs):
        '''should be called at the end of the custom setup_config'''
        warnlist = []
        for k,v in kwargs.items():
            if k in _config and _config[k] is not None and len(_config[k]):
                warnlist.append(k)
            _config[k] = v
        if warnlist:
            warn_msg = (f'{(source + " items " if len(source) else "")}replacing existing '
                 f'config elements obtained from .{self.ext} file | {warnlist}')
            self.logger.warning(warn_msg)
            warn(warn_msg)
        return _config

class YmlConfig(Config):

    def __init__(self,*args, debug=0, base_str='*', **kwargs) -> None:
        self.search_str = ['yaml', 'yml']
        self.base_str = (base_str if base_str.startswith('*') else '*' + base_str)
        self.ext = 'yml'
        super().__init__(*args, debug=debug, child=self, **kwargs)
        self.obfuscate_on_stringify = ['password', 'pw']

    def validate(self,*args, **kwargs):
        return True

class EnvConfig(Config):

    def __init__(self,*args, search_prefix='RSI_', debug=0, 
            skipload_env_var=False, **kwargs) -> None:
        self.search_str = ['env']
        self.ext = 'env'
        self.search_prefix = (search_prefix if not(skipload_env_var) else None)
        super().__init__(*args, debug=debug, child=self, **kwargs)
        self.obfuscate_on_stringify = ['password', 'pw', 'connection_string']
        '''
            additional param options:

            search_prefix="RSI_" (str): the prefix to search for in the
                environment variables 
            skipload_env_var=False (bool): whether to skip attempting to 
                load the environment variables
        '''

    def validate(self,*args, **kwargs):
        return True

    def setkeyvalue(self,key,value,envfile=None):
        super().setkeyvalue(key,value,env=True, write_to_file=envfile)

    def setup_config(self,*args,**kwargs):
        ''' Automatically search the provided file or directory
            for database connection json configuration.
            
            Gets called by refresh_config when the Config (or Config child class) 
            object is instantiated - does not need to be manually called
        '''
        _config = self.override_config_file(self.setup_base_config(*args,**kwargs), **kwargs)
        override_params = self.__class__.get_env_overrides(self.search_prefix)
        # self.warn_updates(_config, override_params)
        _config = self.override_config_file(_config, source='env', **override_params)

        return _config


def get_stdout_logger(name, level):
    ''' return a basic logger as a placeholder for debugging 
        output when Azure Insights isn't connected
    '''
    FORMAT = "[%(filename)s:%(lineno)s-%(funcName)12s()|%(levelname)8s] %(message)s"

    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger(name)
    ch = logging.StreamHandler(sys.stdout)

    # create formatter
    formatter = logging.Formatter(FORMAT)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    logger.setLevel(log_level_dict[level])
    # print('====================================')
    # print([(s.filename, s.function, s.lineno) for s in inspect.stack()])
    # print('====================================')
    # print(f'basic logger level set to: {logger.level}')
    return logger

# create a default env config object by searching for an .env config 
# with the CONFIG_PATH populated to the run directory or from the file found

# go up to DS Tools top level
here = path.join(path.dirname(path.dirname(path.realpath(__file__))),'..','..')  

env = EnvConfig([here, path.realpath(curdir)], error_no_file_found=False, debug=0)
if ('RSI_CONFIG_PATH' not in env) or len(env.file_loc) == 0:
    import os
    os.environ['RSI_CONFIG_PATH'] = path.realpath(curdir)
    env.setkeyvalue('CONFIG_PATH', path.realpath(curdir))