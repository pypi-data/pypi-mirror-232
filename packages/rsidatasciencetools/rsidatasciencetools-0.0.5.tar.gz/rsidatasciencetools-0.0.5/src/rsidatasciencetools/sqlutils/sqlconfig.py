from abc import ABCMeta
import json
from os import path
from warnings import warn

from ..config.baseconfig import Config


class SQLConfig(Config):
    ''' Class to auto-search the provided file or directory
        for database connection json configuration info.
        
        Inputs:
            Required: host, dialect_driver
            Optional: port, user, password, localfile 
    '''
    def __init__(self, *args, search_prefix='RSI_SQL_', debug=0, **kwargs):
        self.search_str = ['sql']
        super().__init__(*args, debug=debug, child=self, **kwargs)
        self.obfuscate_on_stringify = ['password','pw','pass']
        self.check_host_is_local_path()

    def check_host_is_local_path(self):
        if self._config.get('localfile', False) and (
                '%%path' in self._config.get('host','None')):
            localfile = self._config['host'].split('%%path')[1].strip(path.sep)
            self._config['host'] = path.sep.join([self.primary_path, localfile])

    def get_conn_str(self, update={}, obfuscate=False):
        return self.__class__.get_conn_str_static(self.dict_elem(**update),
            obfuscate=obfuscate)

    @staticmethod
    def get_conn_str_static(_config, obfuscate=False):
        islocalfile = _config.get("localfile",False)
        hasUser = _config["user"] if "user" in _config else ""
        hasPW = (('password' in _config and _config["password"] is not None) and 
            len(_config["password"]))
        hasPort = (':'+str(_config["port"]) if ('port' in _config
            ) and _config["port"] is not None else '')
        has_db = (('' if islocalfile else '/')+_config["database"] if ("database" in _config
            ) and _config["database"] is not None else "")
        assert all([not(param) or (isinstance(param,str) and len(param) == 0) for param in [hasUser, hasPW, hasPort, has_db]]
            ) or not(islocalfile), 'local sqlite database should not have a user, pw, port, or DB name'
        pw = (':' + ('****' if obfuscate 
                    else (_config["password"].replace('@','%40') 
                        if (hasPW and ('@' in _config["password"])) else (
                        _config["password"])))
                if hasPW else ''
        )
        host = _config["host"]
        if host.startswith('./'):
            host = host[2:]
        sep = "////" if islocalfile else "//"
        connection_str = (f'{_config["dialect_driver"]}:{sep}{hasUser}'
            f'{pw}{"@" if ("user" in _config) and not(islocalfile) else ""}{host}{hasPort}'
            f'{has_db}') # connect to database

        if not(islocalfile) and any(k.startswith('param_') for k in _config):
            connection_str = '?'.join([connection_str, 
                *['='.join([k.strip('param_'), v]) 
                    for k,v in _config.items() if k.startswith('param_')]])
        return connection_str

    def validate(self, config):
        tocheck = (["dialect_driver", "host"] 
            if config.get('localfile', False) 
            else ["dialect_driver", "host", "port", "user"])
        missing = [k for k in tocheck
                if (k not in config)]
        assert len(missing) == 0, (
            f'configuration failed validation | missing keys: {", ".join(missing)}')
        if ("database" not in config) and not(config.get("localfile",False)):
            warn("no default database found")
        
    def setup_config(self,pw=None, pwENVname='RSI_SQL_pw',**kwargs):
        ''' Automatically search the provided file or directory
            for database connection json configuration.
        '''
        from os import environ
        # if self.debug:
        #     print(f'running overridden version of setup_config() in {self.__class__.__name__}')
        _config = self.setup_base_config(**kwargs)

        # automatically use-lower case from possible upper-case env vars
        override_params = {k.lower(): v 
            for k, v in self.__class__.get_env_overrides(self.search_prefix).items()}
        # self.warn_updates(_config, override_params)
        _config = self.override_config_file(_config, source='env', **override_params)
        if 'pw' in _config:
            _config['password'] = _config['pw']

        if pw is not None:
            if 'password' in _config and len(_config['password']):
                warn('replacing existing password from configuration .json file')
            _config['password'] = pw
        elif 'password' not in _config and pwENVname in environ:
            _config['password'] = environ[pwENVname]
        elif ('password' not in _config) and ('password' not in kwargs):
            if not(_config.get("localfile",False)):
                warn('no password specified')
                _config['password'] = None

        _config = self.override_config_file(_config,**kwargs)
        return _config
