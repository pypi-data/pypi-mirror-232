'''
This code generates records of Fraud Data for 
RSI Machine Learning Model
Run code with default values on terminal:
$python fraud_data_generator.py --n_samples=10 --seed=1 --p_fraud=0.01 --p_duplicates=0.2 --export_csv --debug
'''
from datetime import datetime, time
from datetime import timedelta
import os
import string
from typing import Dict, List
import argparse
import pandas as pd
import numpy as np
#import random
#import ipaddress # from standard python tools

from rsidatasciencetools.datautils.datagen import  Source, IdSource, random_datetimes, RecordGenerator
from rsidatasciencetools.config.baseconfig import YmlConfig


class IPv4Address(IdSource):
    """
    Class that provides IPv4Address-formatted IP Addresses
    that are unique.
    """
    def __init__(self, furl=None, rng=None, seed=None, join_char='.') -> None:
        super().__init__(furl, rng, seed, base=255, join_char=join_char,
                         is_num=True, is_alpha=False, check_unique=True, length=4)

# ip-address
def gen_ip(ip_obj=None, rng:np.random.mtrand.RandomState = None,
           seed: int = None) -> str:
    """
    This function generate a random IP address
    using the class IPv4Address.
    """
    # Generate a seed in case we do not have an rng
    seed = (np.random.randint(0,np.iinfo(np.int32).max) 
            if (seed is None) and (rng is None) else seed)
    rng = (rng if rng is not None else np.random.RandomState(seed=seed))

    if ip_obj is None:
        ip_obj = IPv4Address(rng=rng, seed=seed)
        ip = ip_obj.get_sample()
        return ip, ip_obj

    # Generate a random IP address
    ip = ip_obj.get_sample()
    return ip


# Social Security Number
class GenSSN(Source):
    """
    This class generates a random social security number with unique 
    last 6 digits using the IdSource class. The first 3 digits are created
    by mixing area codes based on a probability distribution determined by 
    the population of each state in 2020.

    To control the location code provided, the function generates its own 
    first 3 digits instead of IdSource. This allows for generating codes for 
    a particular state with a higher proportion of codes from that state. 
    Notice that the first 3 numbers of a ssn are the ones
    from the zip code of the address of the user when issued the ssn.
    
    Since the IdSource() class is used for the last 6 digits, all ssn generated
    will be unique.
    
    Args:
    src_file: a source file with the area code groups and the 
        probability associated to each group. Mandatory columns:
        ['state','zipmin', 'zipmax', 'p']
    return_state: bool. If True it will return additionally the associated 
        state where this ssn was issued at the return value. Default to True.
    state_of_sample: str. The name of the state for which we are consrtructing  
        the sample. If it is in general all the U.S., indicate None or False.
    p_born_in_state: float. The proportion of population of the 
        state_of_sample that was born in the state, so to adjust the ssn 
        area codes accordingly. For example, in Maryland, app 46% of the 
        population was borned in the state, then 46% of the ssn should be
        from Maryland.
        
    Returns:
    a list with two strings: the random social security number, and the 
    associated state during the generation. Notice that the first 3 codes 
    can be associated to more than one state, but only the intended state 
    is listed.
    """
    
    def __init__(self,
                 src_data: str = 'tests/ssn_codes_per_zip_code.csv',
                 rng: np.random.mtrand.RandomState=None,
                 seed : int=None,
                 codes: pd.DataFrame=None,
                 debug: bool = False,
                 return_state: bool = True,
                 state_of_sample: str = 'Maryland',
                 p_born_in_state: float = 0.462,
                 return_as_int=False
                 ):
        super().__init__(src_data=src_data,rng=rng,seed=seed)
        self.codes = codes if codes is not None else pd.read_csv(
            self.src_data, dtype={'zipmin': str, 'zipmax': str})
        self.debug = debug
        self.return_state = return_state
        self.state_of_sample = state_of_sample
        self.second_part = IdSource(rng=self.rng, check_unique=False, length=6)
        self.p_born_in_state = p_born_in_state
        self.reset_db()
        self.return_as_int = return_as_int

    def reset_db(self):
        """
        Allows to reset the list of ids
        to check for uniqueness to empty
        """
        self.global_id_db = []

    def fit(self, state_of_sample=None) -> pd.DataFrame:
        """
        This function loads the file with zip codes and probabilities, 
        do adjustments to get first 3-digit of the zipcodes,
        and increase/adjust probabilities for the sample state if available
        Returns a DataFrame with the following columns:
        ['state', 'zipmin', 'zipmax', 'ssn_code_min', 'ssn_code_max', p ]
        """
        state_of_sample = (state_of_sample if state_of_sample else self.state_of_sample)
        # Adjusting data of zip codes for ssn areas
        # Keep str type for zipmin/zipmax because some codes start with zero
        self.codes['ssn_code_min'] = self.codes['zipmin'].str[0:3].values.copy()
        self.codes['ssn_code_max'] = self.codes['zipmax'].str[0:3].values.copy()
         
        # Normalized possible probability that sum up to 0.99 or similar
        self.codes['p'] = self.codes['p'].values/self.codes['p'].sum()
        
        # Adjust probabilities if we are making data for a particular state
        if state_of_sample:
            # Adjustment of probabilities for a particular state. i.e. "Maryland"
            orig_prob_state = self.codes['p'].loc[self.codes['state'] == state_of_sample].sum()
            self.codes['p'] = self.codes['p'].values.copy() / (1 - orig_prob_state) * (1-self.p_born_in_state)
                    
            # Select the rows for the given state, and aggregate prob associated to all zipcodes
            # in the state
            state_rows = self.codes.loc[self.codes['state'] == state_of_sample]
            total_p = state_rows['p'].sum()

            # Increase the probability for the sample state proportionally
            self.codes.loc[self.codes['state'] == state_of_sample, 'p'] = \
                self.p_born_in_state * state_rows['p'].values.copy() / total_p
  
        if self.debug:
            print("Results pre-normalization")
            print(self.codes.loc[self.codes['state'] == state_of_sample])
            print(self.codes)
            print(self.codes['p'].sum())

        # Normalized possible probability that sum up to 0.99 or similar
        self.codes['p'] = self.codes['p']/self.codes['p'].sum()
        return self.codes 
        
        
    def get_sample(self, max_attempts=10, **kwargs):
        """
        Generates a random and unique social security number.
        Args:
            max_attempts (int, optional): Max number of attempts to find a unique 
            cobination for the ssn. Defaults to 10.

        Returns:
            ssn: an string of the shape XXX-XX-XXXX 
        """
        for _ in range(max_attempts):
            # Randomly choose a row based on the probabilities in the p column
            chosen_row_no = self.rng.choice(range(0,(self.codes.shape[0])),
                                            p=self.codes['p']
            )
            chosen_ssn_state = self.codes['state'][chosen_row_no]

            # Choose a random number between the start and end columns
            # of the chosen row
            chosen_row = self.codes.iloc[chosen_row_no,:]
            start_val = int(chosen_row['ssn_code_min'])
            end_val = int(chosen_row['ssn_code_max'])
            ssn_areacode = str(
                self.rng.randint(start_val, end_val + 1)).zfill(3)

            # Social Security Number last 6 digits
            second_part = self.second_part.get_sample()
            
            # Join code to the last digits
            ssn = ssn_areacode \
                + '-' \
                + second_part[0:2] \
                + '-' \
                + second_part[2:6]
            if ssn not in self.global_id_db:
                break
            else:
                ssn = None
        self.global_id_db.append(ssn)
        
        if self.return_as_int:
            ssn = int(ssn_areacode + second_part[0:2] + second_part[2:6])
        
        if self.return_state:
            return [ssn, chosen_ssn_state]
        if self.return_state is False:
            return ssn

# Banks: routing number and account number
def gen_aba(rng: np.random.mtrand.RandomState = None, seed: int = None, intl: bool = False)-> str:
    '''
    This function generate random routing numbers for
    U.S. (aba) and international banks (iban).
    following these rules:
    1) The first two digits are between 01 and 12 
    2) The next 6 digits are random
    3) The last digit is a checksum digit. Thus, it is
    calculated using the ABA number checksum algorithm, 
    and combined with the first 8 digits creates the 
    full 9-digit ABA number. 
    
    The checksum algorithm do as follows: 
    the first 8 digits of the ABA number are multiplied 
    by a set of weights (3, 7, 1, 3, 7, 1, 3, 7), and 
    the products are summed. The checksum digit is the 
    value that, when added to this sum, results in a 
    multiple of 10.
    
    Note that this code is for synthetic purposes only 
    and should not be used to generate actual ABA numbers.
    
    In the case of international, the class add two prefixed letters
    and get up to 11 characters, but not other checks are done.
    
    Arg:
    seed: integer to set up an specific random state
    intl: if the number is international
    '''
    seed = (np.random.randint(0,np.iinfo(np.int32).max) 
        if (seed is None) and (rng is None) else seed)
    rng = (rng if rng else np.random.RandomState(seed=seed))    
    # Generate a random number for the first 2 digits between 01 and 12
    first_two_digits = str(rng.randint(1, 12)).zfill(2)
    
    # The next 6 digits of an ABA number are assigned to banks and cannot be random
    # We will generate a random number for the last digit for demonstration purposes only
    # In practice, you would need to obtain a valid bank's ABA number to generate a legitimate number
    next_six_digits = str(rng.randint(0, 999999)).zfill(6)
    
    # Combine the first 2 digits with the next 6 digits to create the first 8 digits of the ABA number
    first_eight_digits = first_two_digits + next_six_digits
    
    # Calculate the checksum digit using the ABA number checksum algorithm
    weighted_sum = sum([int(digit) * weight 
        for digit, weight in zip(first_eight_digits, [3, 7, 1, 3, 7, 1, 3, 7])])
    remainder = weighted_sum % 10
    checksum_digit = (10 - remainder) if remainder != 0 else 0
    
    # Combine the first 8 digits with the checksum digit to create the full ABA number
    aba_number = first_eight_digits + str(checksum_digit)
    
    # International add 2 letters at the beggining
    if intl:
        letters = ''.join(rng.choice(list(string.ascii_letters[26:]), size=2))
        aba_number = letters + str(aba_number)
        
    return str(aba_number)


class GenBankInfo(Source):
    """
    This class returns random bank information.
    The aba number and the bank account are generated using the Fake python library.
    Accounts can be located in the U.S. or internationally, determined bu the p_us parameter.
    
    Args:
    p_us: float. The probability for the bank account to be in the US.
        Accordingly with the US State Department's estimate from 2021,
        2.7% of Americans live abroad, so may have intl accounts.
    
    Returns: a list with two entries: aba or iban and a bank account
    """
    
    def __init__(self, rng: np.random.mtrand.RandomState = None,
                 p_us: float = 0.973, seed: int = None, return_is_intl=False):
        super().__init__(rng=rng,seed=seed)
        self.p_us = p_us
        self.return_is_intl = return_is_intl
        self.is_intl = None

    def get_sample(self, **kwargs) -> List:
        """Generates the random and unique routing number and account number.

        Returns:
            List: the routing first and account number second
        """
        random_account_country = self.rng.random()
        
        # Generate a fake bank account number
        num_dig = self.rng.choice([8,9,10,11,12], size=1)
        num_gen = IdSource(rng=self.rng, length=num_dig)
        account_number = num_gen.get_sample()

        # Generate a fake routing number in the U.S. or international
        if random_account_country < self.p_us:
            routing_number = gen_aba(rng=self.rng, intl=False)
            self.is_intl = 0
        else:
            routing_number = gen_aba(rng=self.rng, intl=True)
            prefix = ''.join(self.rng.choice(['A', 'B', 'C', 'D', 'P', 'O', 'U', 'GB', 'CH', 'EU', 'R'],
                    size=2, replace=False))
            account_number = prefix + account_number
            self.is_intl = 1
        
        if self.return_is_intl:
            return [routing_number, account_number, self.is_intl]
        
        else:
            return [routing_number, account_number]


# Driver license in Maryland
class GenDriverLicense(Source):
    """
    This function generates driver licenses from the State of Maryland, which
    comprises one letter (S or L) followed by 12 digits.
    It can be extended for other states, but may need some format/code
    adaptations.
    
    Args:
    letters: a list containing the options for first letter in the driver 
        license. In the case of Maryland, S is used for citizens, and L for
        other residents.
    p_letter: list. It contains the probability of using the letters, for poeple 
        that actually has a driver license. For example, 77% of the Maryland .
        population are citizens ("S") and 23% other type of residents ("L").
    length: int. The number of digits that follows the first letter.
    p_none: probability of a person of 16 years old or older to not have a 
        driver license. 
    
    Obs: this class uses IdSource for the ending part, so it garantees not 
        duplicates.
    """
    
    def __init__(self,
                 rng: np.random.mtrand.RandomState = None,
                 state: str = "MD",
                 letters: List = ["S", "L"],
                 p_letter: List = [0.77, 0.23],

                 p_none: float = 0.069,
                 length: int = 12,
                 seed:int = None
    ):
        super().__init__(rng=rng,seed=seed)
        self.state = state
        self.letters = ["S", "L"] if letters is None else letters
        self.p_letter = [0.77, 0.23] if p_letter is None else p_letter
        self.p_none = p_none
        self.length = length
        self.second_part_idsrc = IdSource(rng=self.rng, length=12)
        
    def get_sample(self, **kwargs) -> str:
        '''
        Generates a random driver license
        '''
        p_S = self.p_letter[0]     
        random_num_with_license = self.rng.random()
        random_num_without_license = self.rng.random()
        
        # If it has a driver license
        if random_num_with_license < p_S:
            first_letter = self.letters[0]
        else:
            first_letter = self.letters[1]

        second_part = self.second_part_idsrc.get_sample()
        driver_license = f"{first_letter}{second_part}"
        
        # If it doesn't have a driver license
        if random_num_without_license < self.p_none:
            driver_license = 'None'
        
        
        return driver_license


class GenRandomTime(Source):
    """
    This class generates a random time (hour + min + sec), 
    with a custom probability associated to desired ranges. 
    The hours goes from 0 to 24, instead of AM/PM.
    This was created for fraud detection syntetic data creation, 
    since online requests that are legitime usually ranges closer to U.S. 
    business hours. 
    Ilegitimate refund claims or general fraudulent online requests 
    may come from othermcountries with times 
    like 3am, or very unusual for U.S. citizens refund claims.
    
    The probabilities are consider as uniform in each of the ranges.

    Args.
    hour_ranges: list of hour ranges. For example:
        [np.arange(0, 7), np.arange(7, 23), np.arange(23, 24)]
    p: List of probabilities for each range of hours (aggregated per range).
        They must sum up to 1.
    
    Returns:
    A datetime.time object with 3 integers which represent a random hour, min and sec. 
    For example `datetime.time(13, 23, 59)`
    """
    
    def __init__(self,
                 rng: np.random.mtrand.RandomState = None,
                 hour_ranges: List = None,
                 p: List = None,
                 seed: int = None,
                 debug: bool = False
    ):
        super().__init__(rng=rng,seed=seed)
        self.hour_ranges = ([np.arange(0, 7), np.arange(7, 23), np.arange(23, 24)] 
            if hour_ranges is None else hour_ranges)
        self.p = [0.05, 0.92, 0.03] if p is None else p
        self.debug = debug
    
    def get_sample(self, **kwargs):
        """Generates the random time object.
        Returns:
            a datetime.time object with 3 integers representing hour, min and sec. 
        """
        # Define uniform probabilities as step functions for each range
        concat_hour_ranges = np.concatenate(self.hour_ranges)
        concat_len = np.concatenate([
            np.full(len(hour_range), len(hour_range)) for hour_range in self.hour_ranges])
        concat_prob_partial = np.concatenate([
            np.full(len(hour_range), prob) 
            for hour_range, prob in zip(self.hour_ranges, self.p)])
        concat_prob_indiv = concat_prob_partial / concat_len

        if self.debug:
            print("Hours:", concat_hour_ranges)
            # print("steps:", values)  # what is 'values'?
            print("length of associated step", concat_len)
            print("patial probability of each step", concat_prob_partial)
            print("individual probability of each hour", concat_prob_indiv)


        # Generate a random integer from the specified probability distribution
        random_hour = self.rng.choice(concat_hour_ranges, p=concat_prob_indiv)
        random_min = self.rng.randint(0,59)
        random_sec = self.rng.randint(0,59)

        return time(random_hour, random_min, random_sec)

# date/time for requests open/submitted
class GenDateTimeRegistry(Source):
    """
    This class generates a random set open&close datetimes for a tax-refund-claim.
    It uses a function random_datetime() to generate the date, and the class 
    GenRandomTime() to generate a time that has some probability distribution
    that bias towards U.S. business times with higher probability.
    
    Obs: in the case of uniform probabilities of time along the date, it is
    best to use the random_datetime() function.
    
    Args:
    start, end: the arguments for the random_datetime generation. 
        A pd.Timestamp values for the start and end of the period for the 
        sample.
    hour_ranges: list of hour ranges to give probabilities. For example:
        [np.arange(0, 7), np.arange(7, 23), np.arange(23, 24)]
    p: A list with the aggregated probabilities associated to each of the 
        hour_ranges listed above.
    
    Returns:
        A dictionary with several values of date, time, submission time, 
        and day of week for open an online request and submission of a request.
        Day of week and type int and goes from 0->6:  Monday (0) Sunday (6)
        `elapse time of submission`: type datetime.timedelta
        `datetime open online request`: type datetime
        `submission time`: type datetime.time
    """
    
    def __init__(self, rng: np.random.mtrand.RandomState = None,
                 start=pd.Timestamp('12-31-2010'),
                 end=pd.Timestamp('12-31-2022'),
                 hour_ranges:List=None,
                 p=None,
                 elapse_mean_days=5,
                 elapse_std_days=2,
                 seed=None,
                 debug=False):
        super().__init__(rng=rng,seed=seed)
        self.start = start
        self.end = end
        self.hour_ranges = ([np.arange(0, 7), np.arange(7, 23), np.arange(23, 24)] 
            if hour_ranges is None else hour_ranges)
        self.p = [0.05, 0.92, 0.03] if p is None else p
        self.debug = debug
        self.elapse_mean_days = elapse_mean_days
        self.elapse_std_days = elapse_std_days
        self.time_source = GenRandomTime(rng=self.rng,hour_ranges=self.hour_ranges,p=self.p)

    def get_sample(self, start=None, end=None, **kwargs):
        """
        Generates a sample of times for a record of a tax claim.
        Returns:
            A dictionary with times in relation to the open, submission
            and elapse time of an online tax claim.
        """
        if start is None:
            start = self.start
            
        if end is None:
            end = self.end

        # Open request date: combine date and time from different sources
        date_open_request = random_datetimes(
                            rng=self.rng, start=start, end=end, n=1)
      
        open_time = self.time_source.get_sample()
        datetime_open_request = datetime.combine(date_open_request.date(), open_time)
        open_day_of_week = datetime_open_request.weekday()

        # Generate a random elapse time between the openning and submition
        # of the online request from a normal distribution
        mean = pd.Timedelta(hours=self.elapse_mean_days*24)  # Default to 5 days
        std = pd.Timedelta(hours=self.elapse_std_days*24)   # Default to 2 days
      
        # We do not allow negative elapse times
        elapse_time_of_submission = timedelta(days=abs(self.rng.normal(mean.days, std.days)))

        # Close online request (benefit claim, refund)
        datetime_submission_request = datetime_open_request + elapse_time_of_submission
        submission_time = datetime_submission_request.time()
        submission_day_of_week = datetime_submission_request.weekday()
      
        if self.debug:
            print('Original date open online request', date_open_request)
            print('Actual open online request using GenRandomTime(): ', datetime_open_request)
            print('Submit online request: ', datetime_submission_request)
            print('Elapse of time: ', elapse_time_of_submission)
      
        return {'datetime open online request': datetime_open_request,
                'datetime submission online request': datetime_submission_request, 
                'elapse time of submission': elapse_time_of_submission,
                'open time': open_time,
                'submission time': submission_time,
                'open day-of-week (0:Sun, 6:Sat)':open_day_of_week,
                'submission day-of-week': submission_day_of_week
               }


class LegitFraudRecordGenerator(Source):
    """
    This class generates a record of legit data for the fraud 
    machine learning model training, including 
    personal information such as name, address, phone number,
    social security number, driver license, ip-address, 
    bank info such as routing number and bank account, 
    as well as date, time, and elapse time of an online 
    request for a refund or claim.
    """

    def __init__(self,
                 yml: Dict,
                 rng: np.random.mtrand.RandomState = None,
                 src_data: str = None,
                 seed: int = None,
                 debug: bool = False,
                 rec_gen=None, ip_gen=None
                 ):
        super().__init__(src_data=(src_data if src_data else yml['src_file_zips_ssn']),
                         rng=rng,seed=seed)
        self.yml = yml
        self.debug = debug
        self.social_gen = GenSSN(rng=self.rng, return_state=False, 
                            src_data=self.src_data, state_of_sample = self.yml['state_of_sample'],
                            p_born_in_state = self.yml['p_born_in_state'], debug=False
        )
        # Generate Driver License()
        self.driver_license_gen = GenDriverLicense(rng=self.rng, state=self.yml['state_of_sample'],
                                letters=["S", "L"], p_letter=[0.77, 0.23],
                                p_none=0.09, length=12, seed=self.seed
        )
        self.ip_gen, self.rec_gen = ip_gen, rec_gen

        self.ip_gen, self.rec_gen = ip_gen, rec_gen

    def get_record(self) -> pd.DataFrame:
      
        # Generate basic info: name, city, zip code, phoneno, etc.
        # Use datagen.py
        recs, basic_info = self.rec_gen.gen_records(num=1, as_df=True)
        record_df = basic_info
        
        # Generate SSN
        # Based on Maryland, use GenSSN()
        self.social_gen.fit()
        record_df['ssn'] = self.social_gen.get_sample()

        # Generate ipaddress, driver license
        record_df['ip'] = self.ip_gen.get_sample()
        record_df['driver_license'] = self.driver_license_gen.get_sample()
     
        # Generate Date&Time data
        datetime_registry_gen = GenDateTimeRegistry(
                 rng=self.rng,
                 start=pd.Timestamp(self.yml['start_date_requests']),
                 end=pd.Timestamp(self.yml['end_date_requests']),
                 hour_ranges=[np.arange(0, 7), np.arange(7, 23), np.arange(23, 24)],
                 p=[0.05, 0.92, 0.03],
                 debug=self.debug
        )
        datetime_registry = datetime_registry_gen.get_sample()
        datetime_registry_df = pd.DataFrame.from_dict(datetime_registry, orient='index').T
        record_df = pd.concat([record_df, datetime_registry_df], axis=1)
      
        # Generate Bank data
        bank_info_gen = GenBankInfo(rng=self.rng, p_us=0.973, seed=self.seed)
        [routing_number, bank_account] = bank_info_gen.get_sample()
        record_df['routing_number'] = routing_number
        record_df['bank_account'] = bank_account
      
        # isFraud Flag
        record_df['isFraud'] = 0
      
        return record_df


def create_multiple_duplicates(rng: np.random.mtrand.RandomState,
                               fraud_df: pd.DataFrame, 
                               col_sets: List[List] = None,
                               p_duplicates: float = 0.2,
                               debug: bool = False) -> pd.DataFrame:
    """
    This function creates duplicates of values in a particular column or 
    set of columns of a dataframe, in a random way.
    
    Args:
    col_sets: A list of list of columns to be duplicated. In the case only one set is given, 
        use just a simple list. For example, use col_sets = ['ip'] for a one set case. 
    fraud_df: the original dataframe
    col: a list of the columns to be altered
    p_duplicates: the proportion of data to consider in the duplication process
    
    p_duplicates equal 1 doesn't mean necesarily that all rows are goin to be duplicated.
    It means that if there are 10 rows, five times the algorith will exchange two records
    on the selected column.
    """
    col_sets = ([['ip'],['routing_number'], ['routing_number','bank_account']] 
        if col_sets is None else col_sets)
    # create function for the simple case of just one list of columns
    def create_duplicates(rng: np.random.mtrand.RandomState,
                          fraud_df: pd.DataFrame,
                          n_duplicates: int,
                          col: List = ['ip'],
                          debug: bool = False) -> pd.DataFrame:
     
        if n_duplicates > 0:
            if debug:
                print("entry:", fraud_df[col])
                print("fraud_df.index:", fraud_df.index)
                 
            for i in range(1, 1+int(n_duplicates/2)):
                selection = rng.choice(fraud_df.index, size=2, replace=False)
                  
                if debug: 
                    print(i, col, selection)

                fraud_df.loc[selection[1], col] = fraud_df.loc[selection[0], col]
                
                if debug: 
                    print("exit:", fraud_df[col])
                
        return fraud_df
    
    n_duplicates = int(fraud_df.shape[0] * p_duplicates/2) *2 # Asure that the number is even
    
    if len(col_sets)==1:
        fraud_df = create_duplicates(rng, fraud_df=fraud_df, col=col_sets,
                                     n_duplicates=n_duplicates, debug=debug)
    
    else:
        
        for col in col_sets:
            for i in range(1, 1+int(n_duplicates/2)):
                fraud_df = create_duplicates(rng=rng, fraud_df=fraud_df, n_duplicates=n_duplicates, col=col, debug=debug)
        
        if debug:
            all_cols =  [col for cols in col_sets for col in cols]
            print(fraud_df[all_cols])
    
    return fraud_df

   
class FraudulentFraudRecordGenerator(Source):
    """
    This class generates a record of a fraud case for the fraud 
    machine learning model training, including 
    personal information such as name, address, phone number,
    social security number, driver license, ip-address, 
    bank info such as routing number and bank account, 
    as well as date, time, and elapse time of an online 
    request for a refund or claim.
    """

    def __init__(self,
                 yml: Dict,
                 rng: np.random.mtrand.RandomState = None,
                 src_file: str = None,
                 seed: int = None,
                 debug: bool = False,
                 rec_gen=None, ip_gen=None,
                ):
    
        super().__init__(src_data=(src_file if src_file else yml['src_file_zips_ssn']),
                         rng=rng,seed=seed)
        self.yml = yml
        self.debug = debug
        self.ip_gen, self.rec_gen = ip_gen, rec_gen
        self.ip_gen, self.rec_gen = ip_gen, rec_gen
        self.social_gen = GenSSN(rng=self.rng, return_state=False, 
                            src_data=self.src_data, state_of_sample = None,
                            p_born_in_state = None, debug=False
        )
        
        # Driver License() Generator - since we don't have from other states, will do Maryland
        # But will change proportions of Citizens and non-Citizens 60 half and half
        # and decrease the p_none from to 0, since to do fraud you need education, and probably
        # the criminal would have a driver license
        self.driver_license_gen = GenDriverLicense(rng=self.rng, state=self.yml['state_of_sample'],
                                letters=["S", "L"], p_letter=[0.5, 0.5],
                                p_none=0, length=12
        )
        
        # Date&Time data Generator
        # Will consider uniform the distribution of time (instead of mostly business hours)
        self.datetime_registry_gen = GenDateTimeRegistry(rng=self.rng,
                 start=pd.Timestamp(self.yml['start_date_requests']),
                 end=pd.Timestamp(self.yml['end_date_requests']),
                 hour_ranges=[np.arange(0, 24)],
                 p=[1],
                 seed=self.seed,
                 debug=self.debug
        )
        # Bank Data Generator
        # p_us: 0.973 -> 75%  Increase prob of international bank to 25%
        self.bank_info_gen = GenBankInfo(rng=self.rng, p_us=0.75, seed=self.seed)
        
        
    def get_record(self) -> pd.DataFrame:
        """
        This function generates basic info: name, city, zip code, phoneno, etc.
        It uses datagen.py
        """
        _, basic_info = self.rec_gen.gen_records(num=1, as_df=True)
        record_df = basic_info
        
        # Generate SSN
        # Change state_of_sample from Maryland to None (whole U.S.)
        # so p_born_in_state = None
        
        self.social_gen.fit() # Fit without state_of_sample will take
                         # the 3-digits from zipcodes, but not recalculate probs
        
        record_df['ssn'] = self.social_gen.get_sample()
        
        # Generate ipaddress
        record_df['ip'] = self.ip_gen.get_sample()
        
        # Generate driver license
        record_df['driver_license'] = self.driver_license_gen.get_sample()
        
        # Generate Date&Time data
        datetime_registry = self.datetime_registry_gen.get_sample()
        datetime_registry_df = pd.DataFrame.from_dict(datetime_registry, orient='index').T
        record_df = pd.concat([record_df, datetime_registry_df], axis=1)
        
        # Generate Bank data
        [routing_number, bank_account] = self.bank_info_gen.get_sample()
        record_df['routing_number'] = routing_number
        record_df['bank_account'] = bank_account
        
        # isFraud Flag
        record_df['isFraud'] = 1
        
        return record_df


class FraudDatasetGenerator(object):
    """
    This class generates a dataset of fraud data by concatenating random records.

    Args:
    n_samples: An integer representing the number of records in the dataset. 
    seed: An initial random state
    p_fraud: float. Probability for a record to be fraudulent.
    rng: an numpy random number generator, usually initialized with a seed as:
         rng = np.random.RandomState(seed=seed)
    """

    def __init__(self,
            yml: Dict,
            rng: np.random.mtrand.RandomState = None,
            n_samples: int = 50,
            p_fraud: float = 0.01,
            debug: bool = False,
            export_csv: bool = True,
            seed: int = None, 
            **kwargs):
        self.n_samples = n_samples
        self.seed = (np.random.randint(0,np.iinfo(np.int32).max)
            if (seed is None) and (rng is None) else seed)
        self.rng = (rng if rng else np.random.RandomState(seed=self.seed))
        self.p_fraud = p_fraud
        self.debug = debug
        self.export_csv = export_csv
        self.yml = yml
        # generate these record generator objects one time, not for each record
        self.rec_gen = RecordGenerator(config=self.yml, rng=self.rng, debug=self.debug)
        self.ip_gen = IPv4Address()
        self.legit = LegitFraudRecordGenerator(yml=self.yml, rng=rng,
            debug=self.debug, rec_gen=self.rec_gen, ip_gen=self.ip_gen)  
        self.fraud = FraudulentFraudRecordGenerator(yml=self.yml, 
            rng=rng, debug=self.debug, rec_gen=self.rec_gen, ip_gen=self.ip_gen)


    def get_dataset(self) -> pd.DataFrame:
        dataset_df = pd.DataFrame({})
        for k in range(0, self.n_samples):
            p_selection_of_record_type = self.rng.uniform()
            
            # Decision of generating legit or fraudulent case
            if p_selection_of_record_type > self.p_fraud:
                new_record = self.legit.get_record()
                if self.debug:
                    print('generating legit record', k,
                        "p_selection_of_record_type:", p_selection_of_record_type)

            else:
                new_record = self.fraud.get_record()
                if self.debug:
                    print('generating fraudulent record', k,
                        "p_selection_of_record_type:", p_selection_of_record_type)
          
            
            # Dataset construction
            dataset_df = pd.concat(
                [dataset_df, new_record], axis=0
            )
        print("#######################################################################")
        print(" Fraud data generation succesful")
        print(" Number of legitimate records:", len(dataset_df[dataset_df['isFraud'] == 0]))
        print(" Number of fraudulent records:", len(dataset_df[dataset_df['isFraud'] == 1]))
        print(" Number of legitimate records:", len(dataset_df[dataset_df['isFraud'] == 0]))
        print(" Number of fraudulent records:", len(dataset_df[dataset_df['isFraud'] == 1]))
        print(" Summary of results:")
        print(f" Columns included:{dataset_df.columns.values}")
        print(f" Size of the dataset: {dataset_df.shape}")
        print(f" Columns included:{dataset_df.columns.values}")
        print(f" Size of the dataset: {dataset_df.shape}")

        if self.export_csv:
            path_to_new_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'./tests/fraud_dataset_with_blacklist.csv')
            dataset_df.to_csv(path_to_new_file)
            print("CSV File succesfully exported")
            print(f"Path: {path_to_new_file}")
            
        return dataset_df

if __name__ == '__main__':
    
    path_to_config = os.path.join(os.path.dirname(os.path.abspath(__file__)),'./tests')
    

    yml_headers = yml.lowerkeys().keys()

    # Create an argument parser
    parser = argparse.ArgumentParser(
        description='This code generates random tax fraud data, including blacklist records.')

    # Define the arguments
    parser.add_argument('--n_samples', type=int,
                        help='Number of time series to generate', default=10)
    parser.add_argument('--seed', type=int,
                        help='Seed to start random state', default=19)
    parser.add_argument('--p_fraud', type=float,
                        help='Probability for a record to be fraudulent', default=0.01)
    parser.add_argument('--p_duplicates', type=float,
                        help='What proportion or fraudulent records should have a duplicate ip or bank info', default=0.2)
    parser.add_argument('--export_csv', action='store_true',
                        help='Export to CSV', default=False)
    parser.add_argument('--debug', action='store_true',
                        help='Enable debugging', default=False)


    # Parse the arguments
    args = parser.parse_args()
    
    # Generate the random number generator
    rng = np.random.RandomState(seed=args.seed)
    
    # Generate the dataset
    fraud_dataset_gen = FraudDatasetGenerator(yml=yml,
                                  rng=rng,
                                  n_samples=args.n_samples,
                                  p_fraud=args.p_fraud,
                                  debug=args.debug,
                                  export_csv=args.export_csv,
                                  seed=args.seed
    )
    dataset_df = fraud_dataset_gen.get_dataset()
    dataset_df.reset_index(inplace=True) # I did this because for some weird reason
                                         # the index was repetitions of zero

    # Adding duplicates of ip address, bank accounts, ...
    if args.p_duplicates:
        # List of cols to generate duplicates
        col_sets=[['ip'],['routing_number'], ['routing_number', 'bank_account']]
        fraud_df = dataset_df[dataset_df['isFraud']==1]
        
        # Apply duplicates to each set of columns
        dataset_df[dataset_df['isFraud']==1] = create_multiple_duplicates(rng=rng, fraud_df=fraud_df,
                               col_sets=[['ip'],['routing_number'], ['routing_number', 'bank_account']],
                               p_duplicates=0.2, debug=True
        )
        
        if args.export_csv:
            path_to_new_file2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            './resources/fraud_dataset_with_blacklist_and_dups.csv')
            dataset_df.to_csv(path_to_new_file2)
            print("CSV File succesfully exported")
            print(f"Path: {path_to_new_file2}")
    

    if args.debug:
        print(dataset_df)
    print("####################################################################")

    
# Run code with:
# python fraud_data_generator.py --n_samples=10 --seed=1 --p_fraud=0.01 --p_duplicates=0.2 --export_csv --debug



# Standarization of names. For classes, Gen is used at the beggining for individual
# characterististics, such ssn, driver license, etc.
# Whereas Generator is used at the end for generators of records
# (several individual characteristics), and datasets (several records).
