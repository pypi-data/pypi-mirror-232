"""
Functions to upload and download data from Azure
"""
import pandas as pd
import io
import os
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

from rsidatasciencetools.config.baseconfig import EnvConfig 


def download_data_from_azure(az_blobname:str, az_container: str = None, path_to_config=None) -> pd.DataFrame:
    """
    Load data from an Azure Blob Storage container.

    Parameters:
        az_blobname (str): The name of the blob to download from Azure Blob Storage.
            Azure call blob to what we regularly call files. Like a csv file, for example.
        az_container (str): The name of the container in Azure with the file
    
    Config credentials:
        An enviromental file (extension .env) with azure credentials must be available, containing 
        the following Azure account details: 
            AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY, AZURE_CONTAINER
        AZURE_ACCOUNT_NAME=largedatafiles
        AZURE_ACCOUNT_KEY=abcdefghijklmno............
        AZURE_CONTAINER_NAME=pytestdata
        Notice that no quotes ("") are necesary 

    Returns:
        pd.DataFrame: A pandas DataFrame containing the data from the downloaded blob

    Raises:
        ResourceNotFoundError in case no file or blob is found.

    Example:
        az_blobname = "data.csv"
        data = download_data_from_azure(az_blobname)
        data.head()
    """
    # Load Azure account details from the credentials file
    if path_to_config == None:
        config = EnvConfig(search_prefix='AZURE_')
    else: config = EnvConfig(path_to_config, search_prefix='AZURE_')
    
    az_acct = config['ACCOUNT_NAME']
    az_acct_key = config['ACCOUNT_KEY']
    if az_container is None:
        az_container = config['CONTAINER_NAME']
        
    connect_str = "DefaultEndpointsProtocol=https;AccountName=" + az_acct + ";AccountKey=" + az_acct_key + ";EndpointSuffix=core.windows.net"    

    # Connect to Azure Blob Storage
    print("Connecting with Azure")
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=az_container, blob=az_blobname)
    
    try:
        stream = blob_client.download_blob()
    except ResourceNotFoundError:
        error_message = f"No data found in Azure blob {az_blobname} in container {az_container}"
        raise FileNotFoundError(error_message)
    
    # Read and process blob data
    blob_data = stream.readall()
    azure_data_df = pd.read_csv(io.BytesIO(blob_data))
    print("Download completed")
    
    return azure_data_df



def upload_data_to_azure(az_blobname:str, local_file_path:str, az_container: str = None, overwrite: bool = False, path_to_config=None):
    """
    Uploads a local file to Azure Blob Storage.

    Args:
        az_blobname (str): The name of the blob to be created in Azure Blob Storage. Blob is the name Azure give to files.
        local_file_path (str): The path to the local file to be uploaded.
        az_container (str, optional): The name of the Azure Blob Storage container. If not provided,
            the container name will be obtained from the environment configuration.
        overwrite (bool, optional): Whether the blob should overwrite existing data in Azure.
            Defaults to False.

    Credentials: 
        A config .env file like the one specified in load_data_from_azure() function must be available
        with the fields AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY. 
        AZURE_CONTAINER_NAME must be specified if parameter az_container=None.

    Returns:
        bool: True if the upload was successful and the local file exists, False otherwise.
    
    Sample usage:
    upload_data_to_azure(az_blobname='delete_this_test.csv', 
                        az_container='testcontainer', 
                        local_file_path='./test.csv', 
                        overwrite=True)
    """
    # Setting up credentials
    if path_to_config == None:
        config = EnvConfig(search_prefix='AZURE_')
    else: config = EnvConfig(path_to_config, search_prefix='AZURE_')
    
    az_acct = config['ACCOUNT_NAME']
    az_acct_key = config['ACCOUNT_KEY']
    if az_container is None:
        az_container = config['CONTAINER_NAME']
    
    print("Start uploading data in Azure") 
    connect_str = "DefaultEndpointsProtocol=https;AccountName=" + az_acct + ";AccountKey=" + az_acct_key + ";EndpointSuffix=core.windows.net" 
    
    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    
    # Creating container if needed
    container_client = blob_service_client.get_container_client(az_container)
    if not container_client.exists():
        print(f'{az_container} Azure container does not exist. Createing it...')
        container_client.create_container()

    blob_client = blob_service_client.get_blob_client(container=az_container, blob=az_blobname)
    print(f"Uploading to Azure Storage local file: {local_file_path} with blob name: {az_blobname} in container: {az_container}")
    
    file_exists = os.path.exists(local_file_path)
    if file_exists:
        with open(file=local_file_path, mode="rb") as data:
            blob_client.upload_blob(data, overwrite=overwrite)
    else:
        print(f"file not exists at {local_file_path}")
    
    print("end data upload to Azure") 
    return file_exists