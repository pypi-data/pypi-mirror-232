import pytest
import azure
import azureml
from os import environ, path
from rsidatasciencetools.azureutils.azureconfig import AzureConfig

for k in environ:
    if k.startswith('RSI_'):
        del environ[k]

loc = path.join(path.dirname(path.realpath(__file__)),'..', '..', 'config', 'tests')


# errorTypes = [azure.core.exceptions.ClientAuthenticationError]
# try:
#     from azureml._vendor.azure_cli_core.azclierror import AuthenticationError as AuthError
# except AttributeError:
#     AuthError = None
# else:
#     errorTypes.append(AuthError)


def test_azure_config():
    cfg = AzureConfig(path.join(loc,'azure-test-config.json'), testing=True)
    assert cfg._config == {
        "subscription_id": "000117e3-d9eb-4084-8233-e90cd78d6149",
        "resource_group": "RSI-CE-AML-RVX-RG",
        "workspace_name": "RSI-CE-AML-RVX-WS",
        "tenantid": "test",
        "clientid": "test"
    }


def test_sp_auth_failure():
    environ['RSI_AZURE_password'] = 'fakepassword'
    with pytest.raises(ValueError):
        AzureConfig(path.join(loc,'azure-test-config.json'), testing=True, debug=2)


def test_azure_config_env_var():
    if 'RSI_AZURE_password' in environ:
        del environ['RSI_AZURE_password']
    environ['RSI_AZURE_tenantid'] = 'test2'
    cfg = AzureConfig(path.join(loc,'azure-test-config.json'), testing=True)
    assert cfg._config == {
        "subscription_id": "000117e3-d9eb-4084-8233-e90cd78d6149",
        "resource_group": "RSI-CE-AML-RVX-RG",
        "workspace_name": "RSI-CE-AML-RVX-WS",
        "tenantid": "test2",
        "clientid": "test"
    }
