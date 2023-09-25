'''Test service principal -based authentication'''
from rsidatasciencetools.azureutils.azureconfig import AzureConfig
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
import os, json


def test_SP_auth(config_dir='./example_run'):
    
    print(os.listdir(config_dir))

    cfg = AzureConfig(config_dir,read_all=True,debug=3)
    print(cfg)

    # with open(os.path.join(config_dir,'azure-app-auth-config.json'),'r') as fin:
    #     app_config = json.load(fin)
    # with open(os.path.join(config_dir,'azure-config.json'),'r') as fin:
    #     config = json.load(fin)
    # print(f'app SP config:\n{app_config}\nsubscription config:\n{config}')

    # sp = ServicePrincipalAuthentication(
    #     tenant_id=app_config['tenantid'], # tenantID
    #     service_principal_id=app_config['clientid'], # clientId - the app needing authentication
    #     service_principal_password=app_config['password']) # clientSecret

    # ws = Workspace.get(name=config['workspace_name'],
    #                 auth=sp,
    #                 subscription_id=config['subscription_id'],
    #                 resource_group=config['resource_group'])
    # print(ws.get_details())

if __name__ == '__main__':
    test_SP_auth()