'''
Pytest for function to download and upload files to Azure
'''
import os
from os import path
import pandas as pd
import pytest
from azure.storage.blob import BlobServiceClient

from rsidatasciencetools.azureutils.az_data_io import download_data_from_azure, upload_data_to_azure
from rsidatasciencetools.config.baseconfig import EnvConfig

# Setting credentials
path_to_config = path.abspath(path.dirname(__file__))


# Define a condition to skip tests if the credentials file doesn't exist
skip_if_no_credentials = pytest.mark.skipif(
    not path.exists(path.join(path_to_config, "./az_io_test.env")),
    reason="Azure credentials not available"
)


az_blobname = "not_to_delete_testing_data_io_functions.csv"
az_container = "pytestdata"

# Integration test
@skip_if_no_credentials
def test_integration_download_data_from_azure():

    azure_data_df = download_data_from_azure(az_blobname=az_blobname,
                                             az_container=az_container,
                                             path_to_config=path_to_config
                                            )
    
    # Assert there is data in the file, and it is a dataframe
    assert not azure_data_df.empty, f"No data in file {az_blobname} container: {az_container} "
    assert isinstance(azure_data_df, pd.DataFrame)


# Uploading data 
@skip_if_no_credentials
def test_integration_upload_data_to_azure():
    local_file_path = './not_to_delete_testing_data_io_functions.csv'
    upload_data_to_azure(az_blobname=az_blobname,
                        local_file_path=local_file_path,
                        az_container=az_container,
                        overwrite=True,
                        path_to_config=path_to_config
                        )