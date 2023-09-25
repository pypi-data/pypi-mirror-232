import pytest
from os import environ, path, remove, removedirs
from glob import glob
from rsidatasciencetools.config.cacheconfig import CacheConfig

for k in environ:
    if k.startswith('RSI_'):
        del environ[k]

loc = path.dirname(path.realpath(__file__))

environ['RSI_ML_API_CACHE_LOC'] = loc

cc = CacheConfig()

def test_cache_config_init():
    assert cc.prefix == None
    assert cc.cache_folder_prefix == '.rsi_aml_api_'

@pytest.fixture(scope="session")
def test_cache_config_api_file_loc():
    cache_loc = cc.get_api_file_cache()
    assert cache_loc == path.join(loc,
        cc.cache_folder_prefix + 'incoming_file_cache'), (
            'path rtn does not match')
    assert path.exists(cache_loc), 'cache path (incoming file) does not exist'

@pytest.fixture(scope="session")
def test_cache_config_api_model_loc():
    cache_loc = cc.get_model_cache_loc()
    assert cache_loc == path.join(loc,
        cc.cache_folder_prefix + 'model_cache')
    assert path.exists(cache_loc), 'cache path (model loc) does not exist'

@pytest.fixture(scope="session")
def test_cache_config_api_model_loc():
    cache_loc = cc.get_train_data_dir()
    assert cache_loc == path.join(loc, '.rsi_aml_train_data')
    assert path.exists(cache_loc), 'cache path (training dir) does not exist'

def pytest_sessionfinish(session, exitstatus):
    """ delete folders when tests finish """
    # raise Exception('trying to delete folders generated')
    for dir in [cc.get_api_file_cache(), 
            cc.get_model_cache_loc(), cc.get_train_data_dir()]:
        try:
            removedirs(cc.get_api_file_cache())
        except FileNotFoundError:
            raise AssertionError(
                f'folder [{dir}] was not created as expected')
