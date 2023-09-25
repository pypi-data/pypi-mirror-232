# Test of Fraud Data Generation

from rsidatasciencetools.datautils.fraud_data.fraud_data_generator import (GenSSN, IPv4Address, #gen_ip,
    create_multiple_duplicates, FraudDatasetGenerator)
from rsidatasciencetools.datautils.datagen import DataValidationException
from rsidatasciencetools.config.baseconfig import YmlConfig

import pandas as pd
import numpy as np
import pytest
import os
from os import path
from typing import List

from pandas.testing import assert_frame_equal
#import datetime
import ipaddress
import re

src_file = path.join(path.dirname(__file__),'ssn_codes_per_zip_code.csv')

# Generate the random number generator
seed=19
rng = np.random.RandomState(seed=seed)

path_to_config = os.path.dirname(os.path.abspath(__file__))
yml = YmlConfig(path_to_config, read_all=True, ext='yaml', auto_update_paths=True)

codes = {
    "California": {
        "zipmin": '00001',
        "zipmax": '00005',
        "ssn_code_min": '000',
        "ssn_code_max": '000',
        "p": 0.25,
        "p_adj": 0.1
    },
    "New York": {
        "zipmin": '00098',
        "zipmax": '00102',
        "ssn_code_min": '000',
        "ssn_code_max": '001',
        "p": 0.25,
        "p_adj": 0.1
    },
    "Maryland": {
        "zipmin": '11100',
        "zipmax": '11105',
        "ssn_code_min": '111',
        "ssn_code_max": '111',
        "p": 0.25,
        "p_adj": 0.7
    },
    "Texas": {
        "zipmin": '23398',
        "zipmax": '23402',
        "ssn_code_min": '233',
        "ssn_code_max": '234',
        "p": 0.25,
        "p_adj": 0.1
    }
}


full_codes_df = pd.DataFrame(codes).T
full_codes_df.index.name='state'
full_codes_df.reset_index(inplace=True)
codes_df = full_codes_df[['state','zipmin', 'zipmax','p']].copy()
codes_adjusted_df = full_codes_df[['state','zipmin', 'zipmax','p_adj','ssn_code_min','ssn_code_max']].copy()
codes_adjusted_df.rename(columns={'p_adj':'p'}, inplace=True)

# GenSSN
def test_genssn_fit():
    ssn_gen = GenSSN(seed=1, return_state='Maryland', p_born_in_state=0.7, codes=codes_df)
    # calculation of the modified probability for the sample
    # in addition the selection of the 3-first-digits code from the zipcodes
    generated = ssn_gen.fit()
    # print('generated', generated)
    # print('codes_adjusted_df', codes_adjusted_df)
    assert_frame_equal(generated, codes_adjusted_df)
    

def test_genssn_get_sample():
    # format
    regex_pattern = r'^\d{3}-\d{2}-\d{4}$'
    for i in range(10):
        ssn_gen = GenSSN(seed=1, return_state=False, src_data=src_file)
        ssn_gen.fit()
        ssn = ssn_gen.get_sample()
        assert re.match(regex_pattern, ssn), f"Format of {ssn} does not match ###-##-####"    

def test_gen_ip():
    # Checking on format and type
    ip_gen = IPv4Address()
    for i in range(10):
        ip = ip_gen.get_sample()
        assert isinstance(ip, str)
        try:
            ipaddress.IPv4Address(ip)
        except ValueError as ve:
            raise(ve)
        except Exception as e:
            raise DataValidationException(f'non-address validation error: {str(e)}')
    
    
def test_Frauddatasetgenerator_get_dataset():
    # LEGIT DATAFRAME
    # Label 0 is assigned correctly
    legit_dataset_gen = FraudDatasetGenerator(yml=yml, 
                                  rng=rng,
                                  n_samples=100, 
                                  p_fraud=0,
                                  debug=False, 
                                  export_csv=False,
                                  seed=seed
    )
    legit_dataset_df = legit_dataset_gen.get_dataset()
    legit_dataset_df.reset_index(inplace=True)
    
    assert legit_dataset_df['isFraud'].sum() == 0
    
    # There is no consistent repetitions in ID columns in legitimate records
    # Cases where there are not driver licenses are marked with str 'None', so we eliminate those cases.
    # Phone number it was considered here at the beggining, but failed. 
    # Two people may have same number? Yes, in an office.
    id_columns = ['taxid', 'email', 'ssn','ip',  'driver_license', 'bank_account']   
    assert not any(legit_dataset_df[col].drop(legit_dataset_df[legit_dataset_df[col]=='None'].index).duplicated().any() for col in id_columns)
    
    # FRAUDULENT DATAFRAME
    # Label 1 is assigned correctly
    fraud_dataset_gen = FraudDatasetGenerator(yml=yml, 
                                  rng=rng,
                                  n_samples=100, 
                                  p_fraud=1,
                                  debug=False, 
                                  export_csv=False,
                                  seed=seed
    )
    fraud_dataset_df = fraud_dataset_gen.get_dataset()
    fraud_dataset_df.reset_index(inplace=True)
    
    assert fraud_dataset_df['isFraud'].sum() == fraud_dataset_df.shape[0]
    
    # There is no consistent repetitions in ID columns in Fraudulent records
    # Idem drop 'None' cases in driver license
    # No repetitions are expected in this class. 
    # Repetitions are generated after with create_multiple_duplicates() function
    for col in id_columns:
        col_df = fraud_dataset_df[col].replace('None', pd.NA).dropna()
        assert not col_df.duplicated().any()
    
    
def test_create_multiple_duplicates():
    # Will test in a dataset with only fraudulent records that 
    # after applying this function some duplicates must appear in all involved columns
    
    # First, we create a dataset of fraudulent records with no duplicates in the IDs
    # tested in the prior test
    fraud_dataset_gen = FraudDatasetGenerator(yml=yml, 
                                  rng=rng,
                                  n_samples=100, 
                                  p_fraud=1,
                                  debug=False, 
                                  export_csv=False,
                                  seed=seed
    )
    fraud_dataset_df = fraud_dataset_gen.get_dataset()
    fraud_dataset_df.reset_index(inplace=True)
    
    # Second, we check that the new dataframe have duplicates in each of the the col_sets
    col_sets = [['ip'],['routing_number'], ['routing_number', 'bank_account']]
    fraud_dataset_with_dups = create_multiple_duplicates(rng=rng, fraud_df=fraud_dataset_df, 
                               col_sets=col_sets, 
                               p_duplicates=0.5, debug=False
    )

    for col in col_sets:
        assert fraud_dataset_with_dups[col].duplicated().any()
        
## Function gen_aba and BankInfo() are tested in test_DMV_data_generator.py