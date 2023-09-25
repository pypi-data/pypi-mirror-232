import pytest
from os import environ, path
from rsidatasciencetools.mlutils.model_io import ModelManager

for k in environ:
    if k.startswith('RSI_'):
        del environ[k]
loc = path.join(path.dirname(path.realpath(__file__)),'..', '..', 'config', 'tests')
environ['RSI_CONFIG_PATH'] = loc
print('RSI_CONFIG_PATH:', environ['RSI_CONFIG_PATH'])

mm = ModelManager(istest=True, debug=3)
env, cache, yml, azure = mm.configtuple

def test_init_mm():
    assert env._config == {
            'ENV_VAR1': 'value1',
            'ENV_VAR2': 2,
            'ENV_PASSWORD': 'env_password',
            'CONFIG_PATH': loc
        }

def test_yml_config():
    assert yml._config == {
        'model_name': 'test_model_name',
        'name': 'name_of_the_thing',
        'property1': 'propertyABC',
        'number': 10,
        'alist': ['element1', 'element2']}

def test_azure_config():
    assert azure._config == {
        "subscription_id": "000117e3-d9eb-4084-8233-e90cd78d6149",
        "resource_group": "RSI-CE-AML-RVX-RG",
        "workspace_name": "RSI-CE-AML-RVX-WS",
        "tenantid": "test",
        "clientid": "test"
    }    

# TODO: need tests to verify model retrieval and storage, but auth with Azure is still uncertain,
# maybe we can embed the Azure SP password in some github / sonarcloud settings that is hidden? 