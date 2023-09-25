from typing import Dict
import pandas as pd
import numpy as np
import pytest
import os
import datetime as dt
import re
import yaml
 


from rsidatasciencetools.datautils.mef_data.mef_datagen import (MefAuthenticationHeaderData,
    MefReturnHeaderData, MefFinancialTransactionsData,
    IPv6Address, MACAddress, FinAccountRecord, PtinGen, gen_money,
    MefDataGen, calculate_age, EtinGen, ItinGen, EfinGen,
    MefDataGen, MefDatasetGenerator
    )
from rsidatasciencetools.datautils.fraud_data.fraud_data_generator import IPv4Address
from rsidatasciencetools.config.baseconfig import YmlConfig


seed = 19
rng = np.random.RandomState(seed)
path_to_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tests')
print('path_to_config:',path_to_config)
yml = YmlConfig(path_to_config, base_str='mef_rec_gen', read_all=True,ext='yaml',auto_update_paths=True)
print(yml)

mef_gen_legit = MefDataGen(rng=rng,config=yml,config_key='legit')
mef_gen_fraud = MefDataGen(rng=rng,config=yml,config_key='fraud')
mef_datatypes = [MefAuthenticationHeaderData, MefReturnHeaderData, 
                 MefFinancialTransactionsData]

# Check that the records include correct fields in fraud and legit cases
def test_legit_record_fields():
    [rec_ah, rec_rh, rec_ft] = mef_gen_legit.get_record()

    for k in rec_ah:
        assert k in MefAuthenticationHeaderData.__members__.keys(), \
            f"{k} does not belong to the AuthenticationHeader in MeF"
    for k in rec_rh:
        assert k in MefReturnHeaderData.__members__.keys(), \
            f"{k} does not belong to the ReturnHeader in MeF"
    for k in rec_ft:
        assert k in MefFinancialTransactionsData.__members__.keys(), \
            f"{k} does not belong to the FinancialTransactions in MeF"


def test_fraud_record_fields():
    [rec_ah, rec_rh, rec_ft] = mef_gen_fraud.get_record()

    for k in rec_ah:
        assert k in MefAuthenticationHeaderData.__members__.keys(), \
            f"{k} does not belong to the AuthenticationHeader in MeF"
    for k in rec_rh:
        assert k in MefReturnHeaderData.__members__.keys(), \
            f"{k} does not belong to the ReturnHeader in MeF"
    for k in rec_ft:
        assert k in MefFinancialTransactionsData.__members__.keys(), \
            f"{k} does not belong to the FinancialTransactions in MeF"

def test_fraud_flag_correctly_assigned_in_legit():
    [rec_ah, rec_rh, rec_ft] = mef_gen_legit.get_record()
    assert rec_ah.is_fraud == 0
    assert rec_rh.is_fraud == 0
    assert rec_ft.is_fraud == 0

def test_fraud_flag_correctly_assigned_in_fraud():
    [rec_ah, rec_rh, rec_ft] = mef_gen_fraud.get_record()
    assert rec_ah.is_fraud == 1
    assert rec_rh.is_fraud == 1
    assert rec_ft.is_fraud == 1
    
def test_gen_money():
    # Test with default arguments
    # Testing type, and 2 decimals max
    result = gen_money(rng=rng)
    assert isinstance(result, float)
    assert 0 <= result
    assert result == round(result, 2)
    
    # Test with custom mean and standard deviation
    result = gen_money(rng=rng, mean=50000, stdev=10000)
    assert isinstance(result, float)
    assert 0 <= result
    assert result == round(result, 2)
    
    # Test with a negative value for stdev
    with pytest.raises(ValueError):
        gen_money(rng=rng, stdev=-10000)

def test_ipv6_address():
    valid_chars = set('0123456789abcdefABCDEF:')
    for _ in range(1,100):
        ipv6_address = IPv6Address().get_sample()
        #IPV6 length is correct
        assert len(ipv6_address) == 39
        # IPv6 address contains only valid characters
        for char in ipv6_address:
            assert char in valid_chars
            
def test_mac_address():
    valid_chars = set('0123456789abcdefABCDEF:')
    for _ in range(1,100):
        mac_address = MACAddress().get_sample()
        # MAC length is correct
        assert len(mac_address) == 17
        # MAC address contains only valid characters
        for char in mac_address:
            assert char in valid_chars
            
def test_ptin_gen():
    ptin_generator = PtinGen()
    ptin = ptin_generator.get_sample()
    assert ptin.startswith("P")
    assert len(ptin) == 9


def test_itin_gen_integer():
    itin_gen = ItinGen(seed=42)
    itin = itin_gen.get_sample()
    assert isinstance(itin, int)
    assert 900000000 < itin < 999999999

def test_itin_gen_string():
    itin_gen = ItinGen(seed=42, return_int=False)
    itin = itin_gen.get_sample()
    assert isinstance(itin, str)
    assert bool(re.match(r'^9\d{2}-\d{2}-\d{4}$', itin))

def test_itin_gen_uniqueness():
    itin_gen = ItinGen(seed=42)
    generated_itins = set()
    for _ in range(1000):
        itin = itin_gen.get_sample()
        assert itin not in generated_itins
        generated_itins.add(itin)


# Test the default behavior of EtinGen
def test_generate_etin():
    for _ in range(1,100):
        etin_generator = EtinGen()
        etin = etin_generator.get_sample()
        assert 5 == len(etin) 
        assert etin.isdigit(), f"ETIN is not just digits: {etin}"
        
        
@pytest.fixture
def efin_generator():
    return EfinGen(seed=42)

def test_generate_efin_length(efin_generator):
    efin = efin_generator.get_sample()
    assert isinstance(efin, str), f"EFIN must be string, but it is {type(efin)}"
    assert len(efin) == 6
    
def test_generate_efin_integer(efin_generator):
    efin = efin_generator.get_sample(return_int=True)
    assert isinstance(efin, int), f"EFIN must be integer, but it is {type(efin)}"

def test_generate_efin_unique(efin_generator):
    generated_efins = set()
    for _ in range(1000):
        efin = efin_generator.get_sample()
        assert efin not in generated_efins, "EFIN Duplicate found "
        generated_efins.add(efin)

    
def test_calculate_age():
    # Test case 1: Calculate age when birthday hasn't occurred yet this year
    date_of_birth = dt.date(1990, 5, 15)
    reference_date = dt.date(2023, 1, 1)  # Before the birthday
    assert calculate_age(date_of_birth, reference_date) == 32

    # Test case 2: Calculate age when birthday has already occurred this year
    date_of_birth = dt.date(1990, 5, 15)
    reference_date = dt.date(2023, 9, 5)  # After the birthday
    assert calculate_age(date_of_birth, reference_date) == 33

    # Test case 3: Calculate age when birthday is on the reference date
    date_of_birth = dt.date(1990, 5, 15)
    reference_date = dt.date(2023, 5, 15)  # Same day as the birthday
    assert calculate_age(date_of_birth, reference_date) == 33
            
# Testing the generation of the datasets
# Load the YAML configuration file
 
def test_mef_dataset_generator():
    # Create an instance of MefDatasetGenerator using the loaded configuration
    generator = MefDatasetGenerator(
                            config=yml, 
                            seed=19, 
                            p_fraud=0.1,
                            export_csv=False,
                            debug=False
    )

    # Generate records using the generator
    result = generator.gen_records(num=10)

    # Assertions or checks on the generated results
    assert len(result) == 3  
    
    # Check if all generated dataframes are different from each other
    assert result[0] is not result[1]
    assert result[1] is not result[2]
    assert result[2] is not result[0]
    
    # Check if the number of rows of all generated dataframes is 10
    assert result[0].shape[0] == 10
    assert result[1].shape[0] == 10
    assert result[2].shape[0] == 10




# Test datatyypes of output

# Test generated columns

# Test that dates are consistent
    

