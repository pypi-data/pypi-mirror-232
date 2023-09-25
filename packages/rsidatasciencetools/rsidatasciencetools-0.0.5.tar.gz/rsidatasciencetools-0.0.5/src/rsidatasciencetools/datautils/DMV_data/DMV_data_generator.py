# This code generates records of compliant and non-compliant Data for DMV
# to be used in RSI Machine Learning Models.

# USAGE:
# $python DMV_data_generator.py --n_samples=40 --seed=1 --p_nc=0.05 --export_csv --debug 

from abc import abstractmethod
import pandas as pd
import numpy as np
#import random
import os
from os import path
import math

import string
from typing import Dict, List
import argparse

from rsidatasciencetools.datautils.datagen import IdSource, random_datetimes, RecordGenerator, get_no
from rsidatasciencetools.datautils.fraud_data.fraud_data_generator import GenSSN, GenBankInfo, GenDriverLicense 
from rsidatasciencetools.config.baseconfig import YmlConfig
from rsidatasciencetools.azureutils.az_data_io import download_data_from_azure

# Obs: DMV does collect SSN and bank info. 

class GenVIN():
    """
    This class generate a fake VIN following the following structure:
    1 num - 2 letters - 5 numbers - 'X' - 2 letters - 6 num (serial number)
    The idSource class is used for the numbers, so it will be unique.
    
    This is not a real VIN number, just a visual approximation to it.
    
    """
    def __init__(self, rng: np.random.mtrand.RandomState = None, seed: int = None) -> str:
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None) and (rng is None) else seed
        self.rng = rng if rng else np.random.RandomState(seed=seed)
        self.length = 13 # We need 13 numbers out of 17 characters for this configuration
        
    def get_sample(self):
        
        gen_numbers = IdSource(rng=self.rng, length=self.length)
        vin_numbers = str(gen_numbers.get_sample())
        vin_letters = ''.join(self.rng.choice(list(string.ascii_letters[26:]), size=3))

        vin = vin_numbers[0] + vin_letters[0:2] + vin_numbers[1:6] + 'X' + vin_letters[2] + vin_numbers[6:]
        return vin
    
    
class GenPlate(IdSource):
    """
    This class generates plates by setting together a set of alphanumerical
    characters. 
    
    This is random data just for testing purposes, so no rules have been 
    considered for the position of the numbers/letters, which usually exist.
    
    The plate is unique because it uses the IdSource class.
    
    Args:
    state_lenght: the numbers of characters that the plate has. Default to seven,
        which is the length for Maryland plates.
    """
    def __init__(self, rng: np.random.mtrand.RandomState = None, 
                 seed: int = None, state_length: int = 7) -> str:
        self.state_length = state_length
        # NOTE: license plates can be alphabetical /and/ numeric characters (typically)
        super().__init__(rng=rng, is_num=True, is_alpha=True, length=self.state_length)

    def get_sample(self) -> str:    
        return super().get_sample().upper()
        
# Income is nor registrated by DMV
# However it's important to contrast with vehicle ownership
# so we are generating income here that may be used later
# for MeF income generation as well

class GenHouseholdIncome():
    """
    This function generates a household income
    based on the src file data.
    Obs. or first version: Source data is based on the whole
    population of Maryland of the Census Bureau 2020.
    
    The data provides the income per range and 
    proportion of population in that range.
    
    The range is represented by the mid-point of the range.
    
    Args:
    yml: a dictionary of the config. The ['source_income'] entry
        should contain the path to a csv file that contains two columns:
        `p` and `mid_income_range`. For example,
            p, mid_income_range,
            0.029844031000145887, 5000.0
            0.015139876345411753, 12500.0
    rng: a random number generator of the type numpy.random.mtrand.RandomState
    src_income: in case you want to override the path of the yml file    
    """
    def __init__(self, yml: Dict = None,  src_income: str = None, 
                 rng: np.random.mtrand.RandomState = None,  seed: int = None):
        self.yml = yml
        self.src_income = src_income if src_income else yml['income_path'] 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if seed is None and rng is None else seed
        self.rng = rng if rng else np.random.RandomState(seed=self.seed)
        
    def get_sample(self) -> float:
        #Income
        income_distr = pd.read_csv(self.src_income)
        income_mid_range = self.rng.choice(income_distr['mid_income_range'], p=income_distr['p'])

        income_sample = abs(self.rng.normal(loc=income_mid_range, scale=income_mid_range/2))
        return round(income_sample,2)

    
def n_vehicles(household_income, rng=None, seed=None, is_nc=0):
    """
    This function calculates the number of vehicles associated 
    to an individual based on the houshold income.
    
    This is a draft estimation for the purpose of fake data 
    generation, and it is based on an study for Portland and 
    Seattle.
    
    Non-compliant cases have been marked as having between 2 and 5 vehicles above what it
    is expected.
    
    """
    seed = np.random.randint(0,np.iinfo(np.int32).max) if seed is None and rng is None else seed
    rng = rng if rng else np.random.RandomState(seed)
    
    if is_nc==0:
        nvehicles = 0.67 * math.log(household_income.iloc[0]) - 5.81 + rng.normal(0,0.75)
        nvehicles = int(nvehicles)
        n_vehicles = min(nvehicles, 10)
        
    if is_nc:
        nvehicles = int( 0.67 * math.log(household_income) - 5.81 + rng.normal(0,0.75) + rng.randint(2, 5))
        n_vehicles = min(nvehicles, 10)
    
    return max(n_vehicles, 0)


class DMVRecordGenerator(object):
    """
    This is the parent class for generating DMV data for the 
    machine learning model training, including 
    personal information such as name, address, phone number,
    social security number, driver license,  
    bank info such as routing number and bank account.
    It also includes data for plates, income and 
    vehicle registration amount
    """

    def __init__(self,
                 yml,
                 path_to_config:str,
                 rng: np.random.mtrand.RandomState = None,
                 src_file: str = None,
                 seed: int = None,
                 debug: bool = False,
                 data_in_azure = True,
                 rec_gen=None, gen_income=None, bank_info_gen=None, # class generators
                 plate_gen=None, vin_gen=None, vehicle_id=None # more class generators
                ):
        assert all((a is not None) for a in [rec_gen,gen_income,bank_info_gen,plate_gen,
                                             vin_gen,vehicle_id])
        self.yml = yml
        self.path_to_config=path_to_config
        self.seed = (np.random.randint(0,np.iinfo(np.int32).max) 
            if seed is None and rng is None else seed)
        self.rng = (rng if rng is not None else np.random.RandomState(seed))
        self.debug = debug
        self.data_in_azure = data_in_azure
        if self.data_in_azure == False:
            self.vehicle_options_df = pd.read_csv(self.yml['vehicle_data_url'])
        else: self.vehicle_options_df = download_data_from_azure(
                                                az_blobname = self.yml['az_data_blobname'], 
                                                az_container = self.yml['az_container'],
                                                path_to_config = path.join(self.path_to_config, self.yml['config_path'])
            )
        self.src_file = (src_file if src_file else yml['src_file_zips_ssn'])
        self.rec_gen, self.gen_income, self.bank_info_gen, \
            self.gen_plate, self.gen_vin, self.gen_vehicle_id = \
            rec_gen, gen_income, bank_info_gen, plate_gen, vin_gen, vehicle_id
        self.social_gen = self.prob_letter = self.p_us = self.prob_born_in_state = \
            self.driver_license_gen = self.state_of_sample = None

    def generate_vehicle_data(self, n_cars:int, dmv_userid:str) -> pd.DataFrame:
        """Generates the details of the vehicle, such as vin, color,
        model, etc. in a pandas dataframe."""
        vehicle_records_df = pd.DataFrame({})
        for k in range(0, n_cars):
            vehicle_index_choice = self.rng.choice(
                self.vehicle_options_df.shape[0])
            vehicle = pd.DataFrame(self.vehicle_options_df.iloc[
                vehicle_index_choice]).T
            
            vehicle['dmv_userid'] = int(dmv_userid)
            vehicle['plate'] = self.gen_plate.get_sample()
            vehicle['vin'] = self.gen_vin.get_sample()
            vehicle['vehicle_id'] = self.gen_vehicle_id.get_sample()

            vehicle_records_df = pd.concat([vehicle_records_df, vehicle])

        return vehicle_records_df

    def get_record(self) -> pd.DataFrame:
        """
        Returns two datafames:, one for the owners and one for vehicles owned
        """
        # Generate basic info: name, city, zip code, phoneno, etc.
        # Use datagen.py
        _, basic_info = self.rec_gen.gen_records(num=1, as_df=True)
        owner_record_df = basic_info
        # Rename taxid with dmv_userid
        owner_record_df.rename(columns={'taxid':'dmv_userid'}, inplace=True)
        
        # Generate SSN
        ssn_sample = self.social_gen.get_sample()
        owner_record_df['ssn'] = ssn_sample
                
        # Generate Driver License()
        driver_license = self.driver_license_gen.get_sample()
        owner_record_df['driver_license'] = driver_license
           
        # Generate Bank data
        [routing_number, bank_account] = self.bank_info_gen.get_sample()
        owner_record_df['routing_number'] = routing_number
        owner_record_df['bank_account'] = bank_account
        
        # Generate household income
        household_income = self.gen_income.get_sample()
        owner_record_df['h_income'] = household_income
        
        # Generate number of vehicles
        owner_record_df['n_vehicles'] = n_cars = n_vehicles(
            owner_record_df['h_income'])
        
        # Compliant record Flag - default to 0
        owner_record_df['is_nc'] = 0
        
        # VEHICLE DETAILS - Generates the vehicle_record_df
        # which would go in a separate sql table
        vehicle_records_df = self.generate_vehicle_data(n_cars,
            owner_record_df['dmv_userid'].values)

        return owner_record_df, vehicle_records_df
    

class DMVCompRecordGenerator(DMVRecordGenerator):
    """
    This class generates a compliant record of DMV data for the 
    machine learning model training, including 
    personal information such as name, address, phone number,
    social security number, driver license,  
    bank info such as routing number and bank account.
    It also includes data for plates, income and 
    vehicle registration amount
    """

    def __init__(self,
                 yml,
                 path_to_config: str,
                 rng: np.random.mtrand.RandomState = None,
                 src_file: str = None,
                 seed: int = None,
                 debug: bool = False,
                 data_in_azure: bool = True,
                 **kwargs):
    
        super().__init__(
            yml, path_to_config, rng, src_file, seed, debug, data_in_azure, **kwargs
        )
        self.prob_letter = [0.77, 0.33]
        self.p_us = self.yml['p_bank_in_the_us'] if yml else 0.95
        self.prob_born_in_state = self.yml['p_born_in_state']
        self.state_of_sample = self.yml['state_of_sample']
        
        # p_none=0 because all people registered at DMV has a Driv.Lic.
        self.driver_license_gen = GenDriverLicense(rng=self.rng,
            state=self.yml['state_of_sample'],
            letters=["S", "L"], p_letter=self.prob_letter,
            p_none=0.0, length=12
        )
        self.social_gen = GenSSN(rng=self.rng, return_state=False, \
            src_data=self.src_file, state_of_sample=self.state_of_sample,\
            p_born_in_state=self.prob_born_in_state, debug=False
        )
        # Based on Maryland, use GenSSN()
        self.social_gen.fit(state_of_sample=self.state_of_sample) 
        

    def get_record(self) -> pd.DataFrame:
        owner_record_df, vehicle_record_df = super().get_record()
        # Compliant Flag = 0 by default

        return owner_record_df, vehicle_record_df


# @TODO: when applying model, we will also include cases for 
# non-compliance, where emails or bank accounts matches black list
    
class DMVNonCompRecordGenerator(DMVRecordGenerator):
    """
    This class generates a record of a non-compliant case for the 
    machine learning model training.
    """

    def __init__(self,
                 yml,
                 path_to_config: str,
                 rng: np.random.mtrand.RandomState = None,
                 src_file: str = None,
                 seed: int = None,
                 debug: bool = False,
                 data_in_azure: bool = True,
                 **kwargs):
        super().__init__(
            yml, path_to_config, rng, src_file, seed, debug, data_in_azure, **kwargs
        )
        self.prob_letter = [0.5, 0.5]
        self.p_us = 0.75

        self.driver_license_gen = GenDriverLicense(rng=self.rng,
            state=self.yml['state_of_sample'],
            letters=["S", "L"], p_letter=self.prob_letter,
            p_none=0.00, length=12
        )
        # NOTE: to PACA, I don't have visibility of geh GenSSN function,
        # but I think it will still work this way, the passing of the zip
        # code may have to happen in the fit() function
        self.social_gen = GenSSN(rng=self.rng, return_state=False,
            src_data=self.src_file, state_of_sample=None,
            p_born_in_state=None, debug=False
        )
        # Based on Maryland, use GenSSN()
        # Fit without state_of_sample will take the 3-digits from zipcodes,
        # but not recalculate probs        
        self.social_gen.fit(state_of_sample=None)


    def get_record(self) -> pd.DataFrame:
        
        owner_record_df, vehicle_record_df = super().get_record()
        # Non-Compliant Flag
        owner_record_df['is_nc'] = 1

        return owner_record_df, vehicle_record_df


class DMVDatasetGenerator():
    """
    This class generates a dataset of non-compliant data by concatenating 
    random records.

    Args:
        path_to_config: the path to the .env credential file (and yml assumed is the same)
        n_samples:  An integer representing the number of records in the dataset. 
        seed:       An initial random state
        p_nc(float) Probability for a record to be non-compliant
        rng:        an numpy random number generator, usually initialized with 
                    a seed as: rng = np.random.RandomState(seed=seed)
        data_in_azure: bool. True if the data to use is in Azure, False if it is not.
             For testing set to False, since credentials are not in github.
    """
    
    def __init__(self, 
            yml: Dict, 
            path_to_config: str,
            rng: np.random.mtrand.RandomState = None, 
            n_samples: int = 50,
            p_nc: float = 0.05,
            debug: bool = False, 
            export_csv: bool = True, 
            seed: int = None, 
            data_in_azure: bool = True,
            **kwargs
        ):
        
        self.n_samples = n_samples
        self.seed = (np.random.randint(0,np.iinfo(np.int32).max) 
            if seed is None and rng is None else seed)
        self.rng = (rng if rng is not None
            else np.random.RandomState(seed=self.seed))
        self.p_nc = p_nc
        self.debug = debug
        self.export_csv = export_csv
        
        self.yml = yml
        self.path_to_config = path_to_config
        self.data_in_azure = data_in_azure
        
        self.p_us = self.yml['p_bank_in_the_us'] if yml else 0.95
        self.user_rec_gen = RecordGenerator(
            config=self.yml, rng=self.rng, debug=self.debug)
        self.plate_gen = GenPlate(rng=self.rng,
            state_length=self.yml['state_plate_length'])
        self.vin_gen = GenVIN(rng=self.rng)
        self.vehicle_id = IdSource(rng=self.rng, length=9)
        self.bank_info_gen = GenBankInfo(rng=self.rng, p_us=self.p_us)

        # Generate household income
        self.gen_income = GenHouseholdIncome(yml=self.yml)

        self.rec_gen_compliant = DMVCompRecordGenerator(
            yml=self.yml, 
            path_to_config=self.path_to_config,
            data_in_azure=self.data_in_azure,
            rec_gen=self.user_rec_gen,
            gen_income=self.gen_income,
            plate_gen=self.plate_gen, vin_gen=self.vin_gen, vehicle_id=self.vehicle_id, 
            bank_info_gen=self.bank_info_gen, rng=self.rng, debug=self.debug) 
        self.rec_gen_noncompliant = DMVNonCompRecordGenerator(
            yml=self.yml, 
            path_to_config = self.path_to_config,
            data_in_azure=self.data_in_azure,
            rec_gen=self.user_rec_gen, 
            gen_income=self.gen_income, 
            plate_gen=self.plate_gen, vin_gen=self.vin_gen, vehicle_id=self.vehicle_id,
            bank_info_gen=self.bank_info_gen, rng=self.rng, debug=self.debug)


    def get_datasets(self) -> List:
        """
        Returns:
            A list with two pandas dataframes: one with the details about the user, 
            and another with the details about vehicle ownership per user.
            The dmv_userid connects both tables.
        """
        
        vehicle_dataset_df = pd.DataFrame({})
        owner_dataset_df = pd.DataFrame({})
          
        for k in range(0, self.n_samples):
            p_selection_of_record_type = self.rng.random()
            
            # Decision of generating legit or non-compliant case
            if p_selection_of_record_type > self.p_nc:
                new_owner_record, new_vehicle_record = self.rec_gen_compliant.get_record()
                if self.debug:
                    print('gnueenerating compliant record', k,
                          ', p_selection_of_record_type:' , p_selection_of_record_type)

            else:
                new_owner_record, new_vehicle_record = self.rec_gen_noncompliant.get_record()
                if self.debug:
                    print('generating non-compliant record', k,
                        ', p_selection_of_record_type:' , p_selection_of_record_type)
            
            # Dataset construction - NOTE: we don't need the 'initial' flag,
            # we can just concat to the initially empty DF
            owner_dataset_df = pd.concat(
                [owner_dataset_df, new_owner_record], axis=0
            )
            vehicle_dataset_df = pd.concat(
                [vehicle_dataset_df, new_vehicle_record], axis=0
            )

                
        # Reorder columns
        new_owner_order = ['dmv_userid', 'taxpayertype', 'compositename',
            'firstname', 'lastname', 'middlename', 'maidenname', 
            'driver_license',  'ssn', 'birthday',
            'phoneno', 'email', 'ethnicity',
            'compositeaddress', 'streetno', 'aptno', 'streetname', 'city', 'zipcode', 
            'routing_number', 'bank_account', 
            'h_income', 'n_vehicles', 'is_nc']
    
        owner_dataset_df = owner_dataset_df.reindex(columns=new_owner_order)
    
        new_vehicle_order = ['dmv_userid', 'vehicle_id', 
                    'vehicle_type', 'plate', 'vin',
                    'manufacturer', 'model', 'prod_year', 'color',
                    'category', 'leather interior', 'fuel_type', 'engine_volume', 'mileage',
                    'cylinders', 'gear_box_type', 'drive_wheels', 'doors', 'wheel', 
                    'airbags', 'levy', 'price']
    
        vehicle_dataset_df = vehicle_dataset_df.reindex(columns=new_vehicle_order)
    
        #Rename some columns
        vehicle_dataset_df.rename(columns={'price': 'purchase_price'}, inplace=True)  

           
        # Output
        print("#######################################################################")
        print(" DMV data generation succesful")
        print(" Number of compliant records:", len(owner_dataset_df[owner_dataset_df['is_nc'] == 0]))
        print(" Number of non-compliant records:", len(owner_dataset_df[owner_dataset_df['is_nc'] == 1]))
        print(" Number of vehicles:", vehicle_dataset_df.shape[0])
        print(" Summary of results:")
        print(" Columns included in owner dataset:")
        print(owner_dataset_df.dtypes)
        print(" Columns included in vehicle dataset:")
        print(vehicle_dataset_df.dtypes)
        print(f" Size of the owner dataset: {owner_dataset_df.shape}")
        print(f" Size of the vehicle dataset: {vehicle_dataset_df.shape}")

        if self.export_csv:
            path_to_new_file1 = path.join(path.dirname(path.abspath(__file__)),'./tests/dmv_owner_dataset.csv')
            owner_dataset_df.to_csv(path_to_new_file1, index=False)
            path_to_new_file2 = path.join(path.dirname(path.abspath(__file__)),'./tests/dmv_vehicle_dataset.csv')
            vehicle_dataset_df.to_csv(path_to_new_file2, index=False)
            print("CSV Files succesfully exported")
            print(f"Path to owners: {path_to_new_file1}")
            print(f"Path to vehicles: {path_to_new_file2}")
            
        return owner_dataset_df, vehicle_dataset_df


if __name__ == '__main__':
    
    path_to_config = path.join(path.dirname(path.abspath(__file__)),'./tests')
    
    yml = YmlConfig(path_to_config, read_all=True, ext='yaml', auto_update_paths=True)
    #yml_headers = yml.lowerkeys().keys()

    # Create an argument parser
    parser = argparse.ArgumentParser(
        description='This code generates random DMV records')

    # Define the arguments
    parser.add_argument('--n_samples', type=int, 
                        help='Number of owner records to generate', default=40
    )
    parser.add_argument('--seed', type=int, 
                        help='Seed to start random state', default=1
    )
    parser.add_argument('--p_nc', type=float, 
                        help='Probability for a record to be non-compliant', 
                        default=0.00
    )
    parser.add_argument('--export_csv', action='store_true', 
                        help='Export generated dataset to CSV', default=False
    )
    parser.add_argument('--debug', action='store_true', 
                        help='Enable debugging', default=False
    )


    # Parse the arguments
    args = parser.parse_args()
    
    # Generate the random number generator
    rng = np.random.RandomState(seed=args.seed)
    
    # Generate the datasets
    dmv_dataset_gen = DMVDatasetGenerator(yml=yml, 
                                  path_to_config=path_to_config,
                                  rng=rng,
                                  n_samples=args.n_samples, 
                                  p_nc=args.p_nc,
                                  debug=args.debug, 
                                  export_csv=args.export_csv,
                                  data_in_azure=True,
    )
    owner_dataset_df, vehicle_dataset_df = dmv_dataset_gen.get_datasets()
    owner_dataset_df.reset_index(inplace=True)   # I did this because for some weird reason 
    vehicle_dataset_df.reset_index(inplace=True) # the index was repetitions of zero

    if args.debug:
        print("owner_dataset_df")
        print(owner_dataset_df)
        print(" ")
        print("vehicle_dataset_df")
        print(vehicle_dataset_df)
    print("####################################################################")
        
    # Run code with:
    # python DMV_data_generator.py --n_samples=40 --seed=19 --p_nc=0.05 --export_csv --debug 

"""
Standarization of names. 
For classes, `Gen` is used at the beggining for individual
    characterististics, such ssn, driver license, etc. Whereas
`Generator` is used at the end for generators of records
(several individual characteristics), and datasets (several records).
"""
      
