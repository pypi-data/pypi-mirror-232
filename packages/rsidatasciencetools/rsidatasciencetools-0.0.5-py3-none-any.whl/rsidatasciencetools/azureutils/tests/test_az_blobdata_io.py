'''
Pytest for function to download and upload files to Azure
'''
import os
from os import path
import pandas as pd
import numpy as np
import pandas.testing
import pytest
from typing import Union

from azure.storage.blob import BlobServiceClient

from rsidatasciencetools.config.baseconfig import EnvConfig
from rsidatasciencetools.azureutils.az_blobdata_io import (
    download_data_from_azure, upload_data_to_azure,
    generate_noisy_identity_matrix,
    anonymize_numeric_dataframe,
    float2int,
    mask_id_column
)


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

# Functions to anonymize data
def generate_noisy_identity_matrix():
    matrix_size = 5
    min_noise = -0.05
    max_noise = 0.05
    
    result_matrix = generate_noisy_identity_matrix(matrix_size, min_noise, max_noise)
    assert result_matrix.shape == (matrix_size, matrix_size)
    
    # Check if diagonal values are within specified range
    noise_diagonal = np.diagonal(result_matrix)
    assert all((1+min_noise) <= value <= (1+max_noise) for value in noise_diagonal)
    
    # Check if values outside the diagonal are zero
    off_diagonal = result_matrix - np.diag(np.diagonal(result_matrix))
    assert np.all(off_diagonal == 0)


def test_anonymize_numeric_dataframe() :
    # Example usage with array
    float_array = np.array([[1.5, 2.7, 3.3], [4.1, 5.9, 6.2]])
    tolerance = 0.05
    modified_array = anonymize_numeric_dataframe(float_array,min_proportional_noise=-tolerance,max_proportional_noise=tolerance)
    assert modified_array.shape == float_array.shape
    assert np.all(modified_array != float_array)
    assert np.all(np.abs(modified_array - float_array) <= np.abs(float_array) * tolerance)
    
    # array with integers
    int_array = np.array([[100, 302, 205], [404, 606, 1007]])
    modified_array = anonymize_numeric_dataframe(int_array,min_proportional_noise=-tolerance,
                                                 max_proportional_noise=tolerance,is_int=True)
    assert modified_array.shape == int_array.shape
    assert np.any(modified_array != int_array)
    assert np.all(abs(modified_array-int_array) <= (int_array * tolerance) + 1)
    assert np.all(modified_array == modified_array.astype(int))
    
    # Example usage with DataFrame
    sample_data_df = pd.DataFrame(float_array, columns=['col1', 'col2', 'col3'])
    min_noise = -tolerance
    max_noise = tolerance
    modified_df = anonymize_numeric_dataframe(sample_data_df, min_noise, max_noise)
    assert modified_df.shape == sample_data_df.shape
    assert modified_df.dtypes.equals(pd.Series([float, float, float], index=sample_data_df.columns))
    assert (abs(modified_df - sample_data_df) <= abs(sample_data_df) * tolerance).all, 'Example with df no int difference is more than tolerance'
    
    # Test case with transforming to integers, shape.
    sample_data_int_df = pd.DataFrame(int_array, columns=['col1', 'col2', 'col3'])
    modified_df_with_int = anonymize_numeric_dataframe(sample_data_int_df, min_noise, max_noise, is_int=True)
    assert modified_df_with_int.shape == sample_data_int_df.shape
    assert modified_df_with_int.dtypes.equals(pd.Series([int, int, int], index=sample_data_int_df.columns))
    

def test_anonymize_numeric_dataframe_with_limits():
    num_test_cases = 1000
    num_columns = 5
    
    # Generate random test data close to 0 and 1
    test_data_low = np.random.uniform(low=0.00001, high=0.00002, size=(num_test_cases, num_columns))
    test_data_high = np.random.uniform(low=0.99998, high=0.99999, size=(num_test_cases, num_columns))
    df_low = pd.DataFrame(test_data_low, columns=[f'col{i}' for i in range(1, num_columns + 1)])
    df_high = pd.DataFrame(test_data_high, columns=[f'col{i}' for i in range(1, num_columns + 1)])
    
    # Apply the function with limits
    modified_df_low = anonymize_numeric_dataframe(df_low, lim_max=1.0, lim_min=0.0)
    modified_df_high = anonymize_numeric_dataframe(df_high, lim_max=1.0, lim_min=0.0)
    
    # Check that values are within the specified limits
    assert (modified_df_low >= 0.0).all().all()
    assert (modified_df_high <= 1.0).all().all()
    
    
    

def test_float2int():
    # Obs 8.5 ->8, 8.51->9
    # Test case with an array
    float_array = np.array([1.5, 2.7, 3.3, 5.1, 5.9])
    int_array = float2int(float_array)
    assert np.array_equal(int_array, np.array([2, 3, 3, 5, 6]))

    # Test case with a DataFrame
    data = {'col1': [1.5, 2.7, 3.3, 5.1, 5.9], 'col2': [4.1, 5.9, 6.2, 7.3, 8.5]}
    df = pd.DataFrame(data)
    expected_data = {'col1': [2, 3, 3, 5, 6], 'col2': [4, 6, 6, 7, 8]}
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(float2int(df), expected_df)
    
def test_mask_id_column():
    data = {'id1': [100, 200, 300],
            'id2': [500, 600, 700]}
    df = pd.DataFrame(data)

    initial_str = "106"
    add_value = 265
    transformed = mask_id_column(df['id1'], initial_str, add_value)

    expected_result = pd.Series(['106365', '106465', '106565']).rename('id1')
    pd.testing.assert_series_equal(transformed, expected_result)

