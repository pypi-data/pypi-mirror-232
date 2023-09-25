"""
Functions to upload and download data from Azure
Function to anonymize data
"""
import pandas as pd
import io
import os
import numpy as np
from typing import Union
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

from rsidatasciencetools.config.baseconfig import EnvConfig 


def download_data_from_azure(az_blobname:str, 
                             az_container: str = None, 
                             path_to_config=None
                            ) -> pd.DataFrame:
    """
    Load data from an Azure Blob Storage container.

    Parameters:
        az_blobname (str): The name of the blob to download from Azure Blob Storage.
            Azure call blob to what we regularly call files. Like a csv file, for example.
        az_container (str): The name of the container in Azure with the file
    
    Config credentials:
        An enviromental file (extension .env) with azure credentials must be available, containing 
        the following Azure account details: 
            AZURE_ACCOUNT_NAME (mandatory)
            AZURE_ACCOUNT_KEY (mandatory)
            AZURE_CONTAINER (optional)
            
        example:    
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



def upload_data_to_azure(az_blobname:str, 
                         local_file_path:str,
                         az_container: str = None, 
                         overwrite: bool = False, 
                         path_to_config=None):
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

# Functions to anonymize data
def generate_noisy_identity_matrix(n: int , min_noise: float = -0.05, max_noise: float = 0.05):
    """
    Generates an identity matrix with the diagonal elements modified by adding random noise
    sampled from a uniform distribution between specified values.

    Args:
        n (int): The size of the square matrix.
        min_noise (float, optional): The minimum value of random noise to be added to the diagonal.
            Default is -0.05.
        max_noise (float, optional): The maximum value of random noise to be added to the diagonal.
            Default is 0.05.

    Returns:
        numpy.ndarray: A matrix with dimensions (n, n) where the diagonal has been
            perturbed by random noise.

    Example usage:
        matrix_size = 5
        min_noise = -0.05
        max_noise = 0.05
        result_matrix = generate_noisy_identity(matrix_size, min_noise, max_noise)
        print(result_matrix)
    """
    if n <= 0:
        raise ValueError("Matrix size must be greater than 0")
    if min_noise >= max_noise:
        raise ValueError("Minimum noise must be less than maximum noise")

    noise = np.random.uniform(min_noise, max_noise, n)
    
    # Matrix is the identity plus a noise
    matrix = np.eye(n) + np.diag(noise)
    return matrix


def anonymize_numeric_dataframe(df: Union[pd.DataFrame, np.ndarray], 
                                min_proportional_noise: float = -0.01, 
                                max_proportional_noise: float = 0.01,
                                is_int: bool = False,
                                lim_max: float = None,
                                lim_min: float = None
                               ) -> Union[pd.DataFrame, np.array]:
    """
    Apply anonymization to a numeric pandas DataFrame by multiplying it with a noisy identity matrix,
    and optionally transform the result to integers.

    Args:
        df (pd.DataFrame): The input DataFrame or array to be anonymized. It must contain only numeric data.
        min_proportional_noise (float, optional): The minimum value of random noise to be added to the identity matrix.
            Default is -0.05.
        max_proportional_noise (float, optional): The maximum value of random noise to be added to the identity matrix.
            Default is 0.05.
        is_int (bool, optional): Whether to transform the modified data to integers using rounding. Default is False.

    Returns:
        pd.DataFrame or numpy.ndarray: Anonymized DataFrame with the same structure as the input DataFrame, where
            numeric columns have been modified by matrix multiplication with a noisy identity matrix, and optionally
            transformed to integers.

    Example:
        sample_data = generate_sample_data(10)
        sample_data_df = pd.DataFrame(sample_data, columns=['col1', 'col2', 'col3'])
        min_noise = -0.05
        max_noise = 0.05
        modified_data = anonymize_numeric_dataframe(sample_data_df, min_noise, max_noise, is_int=True)
        print(modified_data)
    """
    n = df.shape[1]
    noisy_matrix = generate_noisy_identity_matrix(n=n, min_noise=min_proportional_noise, max_noise=max_proportional_noise)
    
    if isinstance(df, np.ndarray):
        modified_data = df @ noisy_matrix  # @ represents the matrix multiplication
    else:
        modified_data = df.values @ noisy_matrix
        
    if lim_max is not None:
        modified_data[modified_data > lim_max] = lim_max - (modified_data[modified_data > lim_max] - lim_max)
        
    if lim_min is not None:
        modified_data[modified_data < lim_min] = lim_min + (modified_data[modified_data < lim_min] - lim_min)
    
    if is_int:
        modified_data = float2int(modified_data)

    if isinstance(df, pd.DataFrame):
        modified_df = pd.DataFrame(modified_data, columns=df.columns)
        return modified_df
    return modified_data




def float2int(data: Union[np.ndarray, pd.DataFrame]) -> Union[np.ndarray, pd.DataFrame]:
    """
    Function to transform a dataset or array from float to integers.
    Made with the intention of allowing anonymization of data 
    when it has integers.
    
    Args:
    data: pd.DataFramew or array with the numeric data to transform
    
    # Example usage with array
        float_array = np.array([1.5, 2.7, 3.3, 5.1, 5.9])
        int_array = float2int(float_array)
        print("Original Float Array:")
        print(float_array)
        print("Transformed Int Array:")
        print(int_array)

        # Example usage with DataFrame
        data = {'col1': [1.5, 2.7, 3.3, 5.1, 5.9], 'col2': [4.1, 5.9, 6.2, 7.3, 8.5]}
        df = pd.DataFrame(data)
        int_df = float2int(df)
        print("\nOriginal DataFrame:")
        print(df)
        print("\nTransformed Int DataFrame:")
        print(int_df)
    """
    
    if isinstance(data, np.ndarray):
        return np.round(data).astype(int)
    elif isinstance(data, pd.DataFrame):
        return np.round(data).astype(int)
    else:
        raise ValueError("Unsupported data type")
        
        
def mask_id_column(column:pd.Series, initial_str:str, add_value:int)->pd.Series:
    """
    Masks an ID value by adding a constant value and prefixing with an initial string
    applied to all values of a column.

    Parameters:
    value (int): The original ID value to be transformed.
    initial_str (str): The initial string to prefix the masked ID.
    add_value (int): The value to be added to the original ID.

    Returns:
    int: The transformed masked ID value.

    Examples:
    >>> data = {'id1': [100, 200, 300],
    ...         'id2': [500, 600, 700]}
    >>> df = pd.DataFrame(data)
    >>> initial_str = "106"
    >>> add_value = 265
    >>> df['id1'] = df['id1'].apply(mask_id, args=(initial_str, add_value))
    >>> df
       id1     id2
    0  106365  500
    1  106465  600
    2  106565  700
    """
    def mask_id(value):

        transformed_value = initial_str + str(int(value) + int(add_value))
        return transformed_value
    return column.apply(mask_id)