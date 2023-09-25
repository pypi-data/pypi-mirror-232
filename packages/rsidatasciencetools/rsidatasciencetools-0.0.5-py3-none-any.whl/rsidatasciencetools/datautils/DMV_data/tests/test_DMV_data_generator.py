import pytest
import pandas as pd
import numpy as np
import os
from os import path
import string
from typing import List
from collections import Counter
from pandas.testing import assert_frame_equal

from rsidatasciencetools.datautils.DMV_data.DMV_data_generator import GenVIN, DMVDatasetGenerator, GenBankInfo
from rsidatasciencetools.datautils.fraud_data.fraud_data_generator import gen_aba
from rsidatasciencetools.config.baseconfig import YmlConfig



# Set random state
seed = 19
rng = np.random.RandomState(seed=seed)

# Set path
# This path to config is used for the azure credentials in the az_credentials.env, and the yml file, both in same directory
path_to_config = os.path.dirname(os.path.abspath(__file__))

yml = YmlConfig(path_to_config, read_all=True, ext='yaml', auto_update_paths=True)

# Condition to skip test with azure credentials from github, and just use large file in github
if path.exists(path.join(path_to_config, "./az_credentials.env")) == False:
    data_in_azure = False
else: data_in_azure = True


def test_gen_vin():
    # Format and type
    vin = GenVIN().get_sample()
    assert isinstance(vin, str)
    assert len(vin) == 17
    assert vin[0].isdigit()
    assert vin[1:3].isalpha()
    assert vin[3:8].isdigit()
    assert vin[8] == 'X'
    assert vin[9:10].isalpha()
    assert vin[11:].isdigit()
    
#     # Unicity if vins
#     # Leave it as example for future reference
#     # More general method for several ids in test_DMVDatasetGenerator_compliant_get_datasets()

#     # Create a list of 1000 generated VINs
#     vin_list = [GenVIN().get_sample() for k in range(1000)]
    
#     # Use Counter to count the number of occurrences of each VIN
#     vin_counts = Counter(vin_list)
    
#     # Assert that each VIN occurs only once
#     for vin, count in vin_counts.items():
#         assert count == 1
    

def test_DMVDatasetGenerator_compliant_get_datasets():
    # COMPLIANT DATAFRAME
    # Label 0 is assigned correctly
    compl_owner_vehicle_gen = DMVDatasetGenerator(
                                  yml=yml, 
                                  path_to_config=path_to_config,
                                  rng=rng,
                                  n_samples=10, 
                                  p_nc=0,
                                  debug=False, 
                                  data_in_azure=data_in_azure,
                                  export_csv=False,
                                  
    )
    compl_owner_df, vehicle_df = compl_owner_vehicle_gen.get_datasets()
    #compl_owner_df.reset_index(inplace=True)
    
    assert compl_owner_df['is_nc'].sum() == 0
    
    # There is no consistent repetitions in ID columns in compliant records
    # Cases where there are not driver licenses are marked with str 'None', so we eliminate those cases.
    # Phone number it was considered here at the beggining, but failed. 
    # Two people may have same number? Yes, in an office.
    id_columns_owner = ['dmv_userid', 'email', 'ssn', 'driver_license', 'bank_account']   
    id_columns_vehicle = ['vehicle_id', 'vin', 'plate']
    
    for col in id_columns_owner:
        col_df = compl_owner_df[col].replace('None', pd.NA).dropna()
        if  col_df.duplicated().any():
            duplicated_col = col
        assert not col_df.duplicated().any(), f" Duplicates in compliant owner table col {col}"
        
    for col in id_columns_vehicle:
        col_df = vehicle_df[col]
        if  col_df.duplicated().any():
            duplicated_col = col
        assert not col_df.duplicated().any(), f" Duplicates in compliant vehicle table col {col}"
  

def test_DMVDatasetGenerator_non_compliant_get_datasets():  
    # NON-COMPLIANT DATAFRAME
    # Label 1 is assigned correctly
    dmv_dataset_gen = DMVDatasetGenerator(
                                  yml=yml, 
                                  path_to_config = path_to_config,
                                  rng=rng,
                                  n_samples=100, 
                                  p_nc=1,
                                  debug=False, 
                                  data_in_azure=data_in_azure,
                                  export_csv=False,
                                  
    )
    owner_df, vehicle_df = dmv_dataset_gen.get_datasets()
    #nc_dataset_df.reset_index(inplace=True)
    
    assert owner_df['is_nc'].sum() == owner_df.shape[0]
    
    # There is no consistent repetitions in ID columns in non-compliant records
    # Idem drop 'None' cases in driver license
    
    id_columns_owner = ['dmv_userid', 'email', 'ssn', 'driver_license', 'bank_account']   
    id_columns_vehicle = ['vehicle_id', 'vin', 'plate']
    
    for col in id_columns_owner:
        col_df = owner_df[col].replace('None', pd.NA).dropna()
        if  col_df.duplicated().any():
            duplicated_col = col
        assert not col_df.duplicated().any(), f" Duplicates in compliant owner table col {col}"
        
    for col in id_columns_vehicle:
        col_df = vehicle_df[col]
        if  col_df.duplicated().any():
            duplicated_col = col
        assert not col_df.duplicated().any(), f" Duplicates in compliant vehicle table col {col}"


def test_gen_aba():
        
    for i in range(1000):
        # US Routing number (ABA)
        aba_us = gen_aba(rng=rng, intl=False)
        
        # Output is a string of 9 characters
        assert isinstance(aba_us, str)
        assert len(aba_us) == 9
        # The first two digits are in the range 1-12
        assert int(aba_us[:2]) in range(1, 13)
        # Validate checksum
        assert aba_us[-1] == str(10 - (sum([int(digit) * weight for digit, weight in zip(aba_us[:-1], [3, 7, 1, 3, 7, 1, 3, 7])]) % 10))[-1]
        
        # International IBAN
        aba_intl = gen_aba(rng=rng, intl=True)
        assert isinstance(aba_intl, str)
        assert len(aba_intl) in range(13)
        #First and second letter are strings
        assert all(x.isalpha() for x in aba_intl[:2])
        assert int(aba_intl[3:-1]) in range(10**7)


def test_BankInfo_gen_bank_info():

    gen_bank = GenBankInfo(rng=rng)
    sample = gen_bank.get_sample()

    # Check output is a list
    assert isinstance(sample, list)
    
    # Check two entries in the list
    assert len(sample) == 2
    
    # Check first entry is a string
    assert isinstance(sample[0], str)
    
    # Check second entry is a string
    assert isinstance(sample[1], str)
    
    # Check first entry is either an ABA number or IBAN
    assert sample[0].isdigit() or sample[0].isalnum(), (
        f'sample ({sample}) is not a valid digit or alpha sequence')
    
    # Check length of second entry is between 8 and 12 characters
    assert 8 <= len(sample[1]) <= 12, (
        f'sample acct number ({sample[0]}) is an invalid length')
