import pytest
from os import environ, path
from rsidatasciencetools.config.baseconfig import Config, EnvConfig, YmlConfig

for k in environ:
    if k.startswith('RSI_'):
        del environ[k]

loc = path.dirname(path.realpath(__file__))

environ['RSI_TEST_ENV_VAR'] = 'env_test_value'
env = EnvConfig(path.join(loc,'./test.env'))

def test_config():
    with pytest.raises(TypeError):
        # class with abstract method 'validate' cannot be instantiated
        Config({'var1':'value1'})

def test_env_config():
    assert env._config == {
        'ENV_VAR1': 'value1',
        'ENV_VAR2': 2,
        'ENV_PASSWORD': 'env_password',
        'TEST_ENV_VAR':'env_test_value'
    }

def test_obfuscate():
    strout = env.__repr__()
    for ln in strout.split('\n'):
        if any((k in ln.lower()) for k in ['pw', 'password']):
            assert '****' in ln

def test_yml_config():
    yml = YmlConfig(path.join(loc))
    assert yml._config == {
        'model_name': 'test_model_name',
        'name': 'name_of_the_thing',
        'property1': 'propertyABC',
        'number': 10,
        'alist': ['element1', 'element2']}
