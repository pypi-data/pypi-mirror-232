"""Generates MeF data for fraud models
This code below will generate 3 files of MeF in 3 records, and export to csv:
$python mef_datagen.py --n_samples=10 --seed=19 --p_fraud=0.01  --export_csv --debug

The files implemented are:
 - AuthenticationHeader
 - ReturnHeader
 - FinancialTransactions

The fields in green are pending for implementation. 
The fields fi_prim_DateofDeath ad fi_sec_DateofDeath that appear as No Implemented, have code advanced that is commented.
The field STIN needs to be readadressed after age attribute is not available
"""

from rsidatasciencetools.datautils.fraud_data.fraud_data_generator import GenDateTimeRegistry, GenBankInfo, GenDriverLicense
from rsidatasciencetools.datautils.datagen import IdSource, Record, RecordGenerator, NameIdDataType, random_datetimes, IdSource
from rsidatasciencetools.config.baseconfig import YmlConfig
from rsidatasciencetools.datautils.fraud_data.fraud_data_generator import IPv4Address, GenSSN
import datetime as dt
import numpy as np
import pandas as pd
from typing import Dict, List, Union
import os
import yaml
from enum import Enum, auto
import logging
import argparse
import math

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.debug("Defining Classes")

# Obs: No Implemented means No YET Implemented.

class MefAuthenticationHeaderData(Enum):
    td_ini_IPAddress = auto()
    td_ini_MACAddress = auto()
    td_ini_IPTs = auto()
    td_ini_DeviceID = auto()
    td_ini_DeviceTypeCd = auto()
    td_ini_BrowserLanguageTxt = auto() #No Implemented
    td_sub_IPAddress = auto()
    td_sub_MACAddress = auto()
    td_sub_IPTs = auto()
    td_sub_DeviceID = auto()
    td_sub_DeviceTypeCd = auto()
    td_sub_BrowserLanguageTxt = auto() #No Implemented
    td_TotActiveTimePrepSubmissionTs = auto()
    td_TotalPreparationSubmissionTs = auto()
    tc_TrustedCustomerCd = auto()
    tc_OOBSecurityVerificationCd = auto()
    tc_LastSubmissionRqrOOBCd = auto()
    tc_pc_UserNameChangeInd = auto()
    tc_pc_EmailAddressChangeInd = auto()
    tc_pc_CellPhoneNumberChangeInd = auto()
    tc_pc_PasswordChangeInd = auto()
    tc_asc_IdentityAssuranceLevelCd = auto()
    tc_asc_AuthenticatorAssuranceLevelCd = auto()
    tc_asc_FederationAssuranceLevelCd = auto()
    tc_PaymentDeclineCd = auto()
    tc_AuthenticationReviewCd = auto()
    tc_AuthenticationReviewTxt = auto()      #NoImplemented (Crypto)
    is_fraud = auto()

class MefReturnHeaderData(Enum):
    Jurisdiction = auto()	# No Implemented
    ReturnTS = auto()
    TaxPeriodBeginDt = auto()
    TaxPeriodEndDt = auto()
    TaxYr = auto()
    ISPNum = auto()              # No implemented
    pp_SelfEmployedInc = auto()	
    pp_PTIN = auto()
    pp_STIN = auto()             # Semi implemented, but commented - need to add age calculations
    pp_PreparerSSN = auto()	
    pp_PreparerFirmEIN = auto()
    pp_PreparerFirmName = auto() # No Implemented
    pp_PreparerPersNm = auto()	
    pp_us_AddressLine1Txt = auto()	
    pp_us_AddressLine2Txt = auto()	
    pp_us_CityNm = auto()
    pp_us_StateAbbreviationCd = auto()
    pp_us_ZIPCd = auto()
    pp_us_InCareOf = auto()
    pp_fa_AddressLine1Txt = auto()	# No Implemented
    pp_fa_AddressLine2Txt = auto()	# No Implemented
    pp_fa_CityNm = auto()	        # No Implemented
    pp_fa_ProvinceOrStateName = auto()	# No Implemented
    pp_fa_CountryCd = auto()	    # No Implemented
    pp_fa_ForeignPostalCd = auto()	# No Implemented
    pp_fa_InCareOfNm = auto()	
    pp_PhoneNum = auto()
    pp_ForeignPhoneNum = auto()      # No Implemented
    pp_EmailAddress = auto()
    ReturnType = auto()              # No Implemented
    fi_prim_tn_FirstName = auto()
    fi_prim_tn_MiddleInitial = auto()
    fi_prim_tn_LastName = auto()
    fi_prim_TaxpayerSSN = auto()
    fi_prim_DateofBirth = auto()
    fi_prim_DateofDeath = auto()	 # Semi implemented but commented. Need some more checkings
    fi_prim_TaxpayerPIN = auto()
    fi_prim_DataSigned = auto()	
    fi_prim_USPhone = auto()	
    fi_prim_ForeignPhone = auto()	# No Implemented
    fi_sec_tn_FirstName = auto()	
    fi_sec_tn_MiddleInitial = auto()	
    fi_sec_tn_LastName = auto()	
    fi_sec_TaxpayerSSN = auto()
    fi_sec_DateofBirth = auto()
    fi_sec_DateofDeath = auto()  #Not implemented
    fi_sec_DateSigned = auto()
    fi_sec_USPhone = auto()
    fi_sec_ForeignPhone = auto()	#No implemented
    is_fraud = auto()
    
class MefFinancialTransactionsData(Enum):
    sp_Checking = auto()
    sp_Savings = auto()
    sp_RoutingTransitNumber = auto()
    sp_BankAccountNumber = auto()
    sp_PaymentAmount = auto()
    sp_IdentificationNumber = auto()
    sp_AccountHolderName = auto()
    sp_AccountHolderType = auto()
    sp_RequestedPaymentDate = auto()
    sp_NotIATTransaction = auto()
    sp_IsIATTransaction = auto()
    rdd_Checking = auto()
    rdd_Savings = auto()
    rdd_RoutingTransitNumber = auto()
    rdd_BankAccountNumber = auto()
    rdd_Amount = auto()
    rdd_TelephoneNumber = auto()
    rdd_NotIATTransaction = auto()
    rdd_IsIATTransaction = auto()
    rdd_fi_ForeginCountry = auto()         # No Implemented
    rdd_fi_PaymentDetail_DestinationCountry = auto() # No Implemented
    rdd_fi_fd_ForeignDFIName = auto()   # No Implemented
    rdd_fi_fd_ForeignDFIIdentifier = auto()	 # No Implemented
    rdd_fi_fd_ForeignDFICountryCode = auto() # No Implemented
    rdd_fi_r_ReceiverName = auto()        # No Implemented
    rdd_fi_r_ReceiverID = auto()       # No Implemented
    rdd_fi_r_ra_USAddress = auto()       # No Implemented* have several subitems (there is an address in RH)
    rdd_fi_r_ra_ForeignAddress = auto()    # No Implemented have several subitems
    ep_Checking = auto()
    ep_Savings = auto()
    ep_RoutingTransitNumber = auto()
    ep_BankAccountNumber = auto()
    ep_PaymentAmount = auto()
    ep_IdentificationNumber = auto()
    ep_AccountHolderName = auto()
    ep_AccountHolderType = auto()
    ep_RequestedPaymentDate = auto()
    ep_NotIATTransaction = auto()
    ep_IsIATTransaction = auto()
    is_fraud = auto()
    
class FinancialData(Enum):
    Checking = auto()
    Savings = auto()
    RoutingTransitNumber = auto()
    BankAccountNumber = auto()
    PaymentAmount = auto()
    IdentificationNumber = auto()
    AccountHolderName = auto()
    AccountHolderType = auto()
    NotIATTransaction = auto()
    IsIATTransaction = auto()

class MefAuthenticationHeaderDataCorruptible(Enum):
    """Class not mainteined, but required to run"""
    ah_td_ini_IPv4Address = auto()
    ah_td_ini_IPv6Address = auto()
    ah_td_ini_MACAddress = auto()
    ah_td_ini_DeviceID = auto()
    ah_td_ini_DeviceTypeCd = auto()
    ah_td_ini_BrowserLanguageTxt = auto()
    ah_td_sub_IPv4Address = auto()
    ah_td_sub_IPv6Address = auto()
    ah_td_sub_MACAddress = auto()
    ah_td_sub_DeviceID = auto()
    ah_td_sub_DeviceTypeCd = auto()
class MefAuthenticationHeaderDataLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    ah_td_ini_DeviceID = auto()
    ah_td_sub_DeviceID = auto()
class MefReturnHeaderDataCorruptible(Enum):
    """Class not mainteined, but required to run"""
    fi_sec_tn_FirstName	= auto()
    fi_sec_tn_MiddleInitial	= auto()    
class MefReturnHeaderDataLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    fi_prim_tn_FirstName= auto()
    fi_prim_tn_MiddleInitial= auto()
    fi_prim_tn_LastName = auto()
class MefFinancialTransactionsDataCorruptible(Enum):
    """Class not mainteined, but required to run"""    
    ep_BankAccountNumber = auto()

# NOTE: this was the way this class was inheriting:    
#   class FinAccountRecord(GenBankInfo, Record, RecordGenerator):
# which is inappropriate; just b/c you use a class as 
# a class variable, does not mean you should inherit from it
class FinAccountRecord(object):

    """Generates a MeF financial account record
    Args:
    holdername: a string containing the name of the owner
        of the account. For example "James G. Smith"
        
    Content additional specifications:
    AccountHolderType: refers to the quality or 1:Business or 2:Personal account
    """
    def __init__(self, rng: np.random.mtrand.RandomState = None, seed:int = None, 
                 identification: str = None, return_is_intl: bool = True, p_us : float = 0.973, _type=FinancialData):
        self.seed = seed if seed is None else np.random.randint(0,np.iinfo(np.int32).max)
        self.rng = rng if rng is not None else np.random.mtrand.RandomState(seed=self.seed)
        # TODO: need to understand why settings `return_is_intl` in a fixed 
        # manner is necessary
        self.bank_info_gen = GenBankInfo(rng,return_is_intl=True,p_us=p_us)
        self._type = _type
        self.driver_lic_gen = GenDriverLicense(self.rng)
        
        
    def get_record(self,holdername=None):  

        if self._type == FinancialData:
            is_check = self.rng.choice([0,1], p=[0.75, 0.25])
            Checking = str(is_check)
            Savings = str(1-is_check)
            [RoutingTransitNumber, BankAccountNumber, is_intl] = self.bank_info_gen.get_sample()
            
            acc_holder_type = self.rng.choice( ["1","2"], p=[0.20, 0.80])
            identification = self.driver_lic_gen.get_sample()
    
            return Record(datatype=FinancialData,
                    corruptible=FinancialDataCorruptible,
                    lenth_changable=FinancialDataLengthChangable,
                    autopop={},
                    rng=self.rng,
                    Checking=Checking,
                    Savings=Savings,
                    RoutingTransitNumber=RoutingTransitNumber,
                    BankAccountNumber=BankAccountNumber,
                    IdentificationNumber=identification,
                    AccountHolderName=holdername, 
                    AccountHolderType=str(acc_holder_type),
                    NotIATTransaction=str(1-is_intl),
                    IsIATTransaction=str(is_intl)
        )
        else:
            raise NotImplementedError(f'{self._type} is not currently implemented')

    
class FinancialDataCorruptible(Enum):
    AccountHolderName = auto()

class FinancialDataLengthChangable(Enum):
    AccountHolderName = auto()
class MefFinancialTransactionsDataLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    ep_BankAccountNumber = auto()

class MACAddress(IdSource):
    """Generates a random MAC address as string"""
    def __init__(self, furl=None, rng=None, seed=None, base=16, join_char='', length=12,
                 group_size=2, is_alpha=True) -> None:
        super().__init__(furl, rng, seed, base, join_char,
                         is_num=True, is_alpha=is_alpha,
                         repeating=1, check_unique=True, length=length)
        self.group_size = group_size

    # @TODO It would be good to add a parameter in IdSource for the sizes of the groups.
    
    def get_sample(self, return_int=False) -> str:
        """Generate the MACAddress by separating the 12-digit ID in two characters"""
        mac_digits = super().get_sample(return_int=return_int)
        mac_groups = ':'.join(mac_digits[i:i+self.group_size] for i in range(0, self.length, self.group_size))
        return mac_groups

class IPv6Address(MACAddress):
    """Generates IPV6address as string"""
    def __init__(self, rng=None,seed=None,base=16,length=32,group_size=4) -> None:
        super(IPv6Address,self).__init__(rng=rng, seed=seed,length=length,
                                         base=base,group_size=group_size)
        
class DeviceIdGen(IdSource):
    """ 
    This class generates the DeviceId following the specifications
    of the MeF IRS data, which in summary translates in the result of a 
    Sha1 algorithm, which are 40 hexagesimal digits.
    
    Args:
        rng (optional)
        seed (optional)

    Sample usage:
        device_gen = DeviceIdGen()
        device_id = device_gen.get_sample()

    Details at the end:
    For the "MeF" process, "two specific pieces of unique information,
    namely the SMBIOS UUID and the primary hard drive serial number,
    are requested. These pieces of information are combined without
    any separators, and the resultant string undergoes the
    SHA-1 algorithm. 
    The resulting hash is then designated as the Device ID.
    This Device ID is inserted into the return and subsequently
    submitted to the IRS within the return header.
    """
    def __init__(self, furl=None, rng=None, seed=None, base=16, 
                  join_char='', length=40, is_alpha=True) -> None:
        super().__init__(furl, rng, seed, base, join_char,
                         is_num=True, is_alpha=is_alpha,
                         check_unique=True, length=length)
        self.raw_id = IdSource(rng=self.rng, length=self.length)
        
class EinGen(IdSource):
    """Generates an MVP EIN"""
    def __init__(self, rng=None, seed=None,
                 return_int=False) -> None:
            super().__init__(rng=rng, seed=seed, 
                        is_num=True, check_unique=True, length=9)
            self.raw_id = IdSource(rng=self.rng, length=self.length)
            self.return_int = return_int
    def get_sample(self):
        ein = str(self.raw_id.get_sample())
        if self.return_int:
            return ein
        
        else: ein = ein[0:2] + '-' + ein[2:]
        return ein

class PtinGen(IdSource):
    """
    Generates an MVP PTIN
    PTIN 
    """
    def __init__(self, rng=None, seed=None) -> None:
            super().__init__(rng=rng, seed=seed, 
                        is_num=True, check_unique=True, length=8)
            self.raw_id = IdSource(rng=self.rng, length=self.length)
    def get_sample(self):
        ptin = str(self.raw_id.get_sample())
        return "P" + str(ptin)
    
class ItinGen(IdSource):
    """
    Generates a random ITIN
    
    Args:
        rng (np.random.Generator, optional): The random number generator.
        seed (int, optional): A seed for the random state.
        return_int (bool, optional): If True, returns the 9 digits as an integer.
            If False, returns the format '9XX-XX-XXXX'. Default is True.

    The generated ITIN follows the IRS structure:
        "An ITIN will always start with a “9”, and the 4th and 5th digits may be 
        “50-65”, ”70-88”, “90-92”, or “94-99”, i.e. 9xx-95-xxxx. Although middle 
        digits 50-65 have been identified for ITIN assignment, no ITINs have been 
        assigned using these middle digits yet. 
        Please note that 999-99-9999 is not a valid ITIN. " 
        Source IRS Documentation, 2021
        In our implementation, 50-65 has been included.
    """
    def __init__(self, rng=None, seed=None, return_int=True) -> None:
            super().__init__(rng=rng, seed=seed, 
                        is_num=True, check_unique=True, length=6)
            self.return_int = return_int
            self.raw_id = IdSource(rng=self.rng, length=self.length)
    def get_sample(self):
        itin_6 = str(self.raw_id.get_sample())
        itin_middle = str(self.rng.choice(
              list(range(50,66)) 
            + list(range(70,89))
            + list(range(90,93))
            ) )
        itin = "9" + itin_6[0:2] + itin_middle + itin_6[2:]
        if self.return_int:     
            return int(itin) 
        else:
            return itin[0:3] + "-" + itin[3:5] + '-' + itin[5:]

    
class EtinGen(IdSource):
    """ 
    ETIN: Electronic Transmitter Identification Number
    ETIN is a 5-digit identification number issued to Electronic Return Originators (EROs), 
    Electronic Transmitters (ETs), and intermediate service providers that transmit
    tax return data electronically to the IRS.
    """
    def __init__(self, furl=None, rng=None, seed=None, base=10, 
                  join_char='', length=5, is_alpha=False) -> None:
        
        super().__init__(furl, rng, seed, base, join_char,
                         is_num=True, is_alpha=is_alpha,
                         check_unique=True, length=length)
        self.raw_id = IdSource(rng=self.rng, length=self.length)
        
class EfinGen(IdSource):
    """ 
    EFIN: Electronic Filing Identification Number
    EFIN is a unique identification number issued by the IRS to tax professionals,
    including tax preparers, Certified Public Accountants (CPAs), and tax firms,
    who wish to electronically file federal tax returns on behalf of their clients.

    The core EFIN (Electronic Filing Identification Number) typically consists of 6 digits, 
    variations may include the addition of suffixes or extra characters in certain cases. These variations
    can occur for a variety of reasons, including the need to distinguish between different offices
    or locations of the same tax professional or firm.
    
    MVP version considers core 6 digits.
    
    Method:
        get_sample(): return the Efin 6-digit id.
        
    Args of get_sample method:
        return_int(bool): if set to True will return an integer. 
            Default to False, so return a string. 
    
    Returns:
    Efin
    """
    def __init__(self, furl=None, rng=None, seed=None, base=10, 
                  join_char='', length=6, is_alpha=False) -> None:
        
        super().__init__(furl, rng, seed, base, join_char,
                         is_num=True, is_alpha=is_alpha,
                         check_unique=True, length=length)
        self.raw_id = IdSource(rng=self.rng, length=self.length)

    
def gen_money(rng=None, seed=None, mean=40000, stdev=24000):
    """Generate tax amounts, or income, as dollars and cents.
    Args:
    Mean:float. The average of the tax amount 
    stdev:float. The standard deviation of the tax amount or income.
    """
    seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
    rng = (rng if rng is not None else np.random.RandomState(seed=seed))
    random_num = rng.normal(loc=mean, scale=stdev)
    
    # Ensure the value is non negative
    random_num = max(0.00, random_num)
    
    # Round the value to 2 decimal places
    random_num = round(random_num, 2)
    
    return random_num

def calculate_age(date_of_birth, reference_date=None) -> int:
    """
    Calculate the age of a person based on their date of birth and a reference date.

    Parameters:
    - date_of_birth (datetime.date): The date of birth of the person.
    - reference_date (datetime.date): The reference date to calculate the age.

    Returns:
    - int: The age of the person in years.
    
    # Example usage
        date_of_birth = datetime.date(1990, 5, 15)  # Replace with the person's date of birth
        reference_date = datetime.date(2023, 9, 5)  # Replace with the reference date

        age = calculate_age(date_of_birth, reference_date)
        print(f"Age: {age} years")
    """
    if reference_date is None:
        reference_date = pd.Timestamp.today()
    age = reference_date.year - date_of_birth.year - ((reference_date.month, reference_date.day) < (date_of_birth.month, date_of_birth.day))
    return age




class MefDataGen(GenBankInfo, RecordGenerator):
    """Parent class that generates per default a legit MeF fraud-relevant data record.
    The record comprises 3 records (dataframes) for each of the more relevant files.
    The structure could expand using the same cronstruction to additional files.
    Fields constructed are included in Enum dataclasses.
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files as well as different parameters for 'fraud' and 'legit'
        records.
    config_key: The type of record to be generated. Per default is
        'legit', a non-fraudulent record. When 'fraud' it generates
        a fraudulent record (changing some parameters in the config
        (yml) file)
    Returns:
        A list of three individual Record objects in a list:
        [rec_ah , rec_rh, rec_ft], containing the
        AuthenticationHeader, ReturnHeader, and FinancialTransactions
        simulated random records, of the type indicate in the config_key.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.

    """
    logging.debug("Initializing main MefDataGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='legit',debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key = config_key
        self.debug = debug
        
        # General
        self.min_date_request = pd.Timestamp(self.yml['min_date_requests']).floor(freq='S')
        self.max_date_request = pd.Timestamp(self.yml['max_date_requests']).floor(freq='S')
        self.src_file_zips_ssn = self.yml['src_file_zips_ssn']
        self.taxpayer_indiv_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        
        # AuthenticationHeader Initialization
        self.gen_ip4 = IPv4Address(rng=self.rng)
        self.gen_ip6 = IPv6Address(rng=self.rng)
        self.gen_mac = MACAddress(rng=self.rng)  
        self.gen_deviceid = DeviceIdGen(rng=self.rng)
        # Flag self.yml_key distinguish `fraud`` from `legit`
        self.yml_ah = self.yml['AuthenticationHeader'][self.yml_key]  
        self.gen_submission_timeline = GenDateTimeRegistry(rng=self.rng, 
                                                start=self.min_date_request,
                                                end=self.max_date_request,
                                                hour_ranges=self.yml_ah['hour_ranges'],
                                                p=self.yml_ah['p_hour_range'],
                                                elapse_mean_days=self.yml_ah['total_time_preparation_in_days'].get('mean'),
                                                elapse_std_days=self.yml_ah['total_time_preparation_in_days'].get('std'),
                                                seed=self.seed,
                                                debug=self.debug
                                                )
        self.active_time_factor:Dict = self.yml_ah['active_time_preparation_factor']
        self.p_last_ip_matches_current_ip = self.yml_ah['p_last_ip_matches_current_ip']
        self.p_change_credential = self.yml_ah['p_change_credential']
        self.p_identity_assurance = self.yml_ah['p_identity_assurance']
        self.p_authenticator_assurance = self.yml_ah['p_authenticator_assurance']
        self.p_federal_assurance = self.yml_ah['p_federal_assurance']
        self.p_payment_decline = self.yml_ah['p_payment_decline']
        
        # ReturnHeader Initialization
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]
        self.state_of_sample = self.yml_rh['state_of_sample']
        self.p_born_in_state = self.yml_rh['p_born_in_state']
        self.src_file_ssn = self.src_file_zips_ssn
        self.social_gen = GenSSN(src_data=self.src_file_ssn,
                             rng=self.rng, return_state=False,  
                             state_of_sample = self.state_of_sample,
                             p_born_in_state = self.p_born_in_state, 
                             debug=self.debug
         )
        self.social_gen.fit()
        
        # FinancialTransactions File Initialization
        self.yml_ft = self.yml['FinancialTransactions'][self.yml_key]
        self.p_bank_account_in_us = self.yml_ft['p_bank_account_in_us']
        self.bank_info_gen = GenBankInfo(rng=self.rng,
                                    p_us=self.p_bank_account_in_us,
                                    seed=self.seed,
                                    return_is_intl=True
                                    )
        self.fin_gen = FinAccountRecord()
        self.pin_gen = IdSource(rng=self.rng, is_num=True, length=5)
        self.ptin_gen = PtinGen(rng=self.rng)
        self.stin_gen = IdSource(rng=self.rng, is_num=True, length=8)
        self.ein_gen = EinGen(rng=self.rng)
        

    @staticmethod                                                
    def convert_to_min(elapse_time, as_str=False)-> Union[str, int]:
        """Convert a datetime.timedelta object to minutes.
        In MeF the type appear (TextType)"""
        elapse_minutes = int( elapse_time.total_seconds() // 60) + 2
        if as_str: 
            return(str(elapse_minutes))
        return(elapse_minutes)
    
   
    def get_record(self,_type=None):
        """Generates fields for the AuthenticationHeader, 
        ReturnHeader, and FinancialTransactions file of MeF"""
        
        TaxYr = self.rng.randint(low=self.min_date_request.year, high=self.max_date_request.year)
        
        fi_prim_DataSigned = random_datetimes(
            start= pd.to_datetime(str(TaxYr+1) + '-02-01'),
            end=pd.to_datetime(str(TaxYr+1)+'-4-30'), 
            out_format='datetime', 
            rng=self.rng, n=1
            ).date()
        
        tax_sub_end = dt.datetime(year=TaxYr+1, month=12, day=31).date()
        
        # 1. AuthenticationHeader File
        # 1.1 TransmissionDetails (td_) section
        ini_IPv4Address = self.gen_ip4.get_sample()
        ini_IPv6Address = self.gen_ip6.get_sample()
        sub_IPv4Address = self.gen_ip4.get_sample()
        sub_IPv6Address = self.gen_ip6.get_sample()
        td_ini_MACAddress = self.rng.choice(
            ["",self.gen_mac.get_sample()], p=[0.25, 0.75]
        )
        td_ini_IPAddress = self.rng.choice(
            [ini_IPv4Address,ini_IPv6Address], p=[0.5,0.5]
        )
        td_sub_IPAddress = self.rng.choice(
            [sub_IPv4Address,sub_IPv6Address,td_ini_IPAddress], 
            p=[0.15,0.15,0.7]
        )
        td_sub_MACAddress = self.rng.choice(
            ["",self.gen_mac.get_sample(),td_ini_MACAddress], 
            p=[0.05,0.1,0.85]
        )
        
        td_ini_DeviceID = self.gen_deviceid.get_sample()
        choices = ["Desktop", "Browser-based", ""]
        td_ini_DeviceTypeCd = self.rng.choice(choices, p=[0.4, 0.55, 0.05])
        td_sub_DeviceID = self.rng.choice(
            [td_ini_DeviceID,self.gen_deviceid.get_sample()], p=[0.8, 0.2]
            )
        choices = [td_ini_DeviceTypeCd , "Desktop", "Browser-based", ""]
        td_sub_DeviceTypeCd = self.rng.choice(choices, p=[0.6, 0.2, 0.15, 0.05])
        
        
        submission_timeline = self.gen_submission_timeline.get_sample(
            start=pd.Timestamp(fi_prim_DataSigned),end=pd.Timestamp(tax_sub_end))
        td_TotalPreparationSubmissionTs = MefDataGen.convert_to_min(
            submission_timeline['elapse time of submission']
        )
        td_TotActiveTimePrepSubmissionTs = str(int(round(
            (self.rng.uniform(**self.active_time_factor) * td_TotalPreparationSubmissionTs),0)
        ))
        td_TotalPreparationSubmissionTs = str(td_TotalPreparationSubmissionTs)
        td_ini_IPTs = pd.Timestamp(submission_timeline['datetime open online request']).floor(freq='S')
        td_sub_IPTs = pd.Timestamp(submission_timeline['datetime submission online request']).floor(freq='S')
        
        # 1.2 TrustedCustomer (tc_) section
        # TrustedCustomerCd
        # '': no value (allowed)
        # 0: new taxpayer, 1: returning taxpayer online, 
        # 2:Returning taxpayer to the same tax preparer, 
        # 3: Returning tax-payer to the same pro-software
        tc_TrustedCustomerCd = str(self.rng.choice(["",0,1,2,3], p=[0.1, 0.2, 0.2, 0.2, 0.3]))
        
        # OOBSecurityVerificationCd
        # 00 = Can't send email 
        # 01 = Bounced email
        # 02 = Sent email one way
        # 03 = Full Out of Band - Email
        # 04 = Can't send Text 
        # 05 = Bounced Text
        # 06 = Delivered Text - one-way
        # 07 = Full Out of Band - Text
        # 08 = Random 3rd Party Security Questions 
        # 09 = Security Questions established byIndustry
        # 10 = Security Questions established by Customer
        # 11 = Other Pass
        # 12 = Other Fail
        tc_OOBSecurityVerificationCd=str(self.rng.choice([""] + [str(i).zfill(2) for i in range(0, 13)]))
        
        # LastSubmissionRqrOOBCd: bool
        # Does the IP Address at final submission match prior login IP?
        tc_LastSubmissionRqrOOBCd = self.rng.choice(["","0","1"],p=self.p_last_ip_matches_current_ip)
        tc_pc_UserNameChangeInd = self.rng.choice(["","0","1"],p=self.p_change_credential)
        tc_pc_EmailAddressChangeInd = self.rng.choice(["",0,1],p=self.p_change_credential)
        tc_pc_CellPhoneNumberChangeInd = self.rng.choice(["","0","1"],p=self.p_change_credential)
        tc_pc_PasswordChangeInd = self.rng.choice(["","0","1"],p=self.p_change_credential)
        
        # IdentityAssuranceLevelCd: str, max 10 characters
        # IAL 1 (Some confidence), IAL 2 (High confidence), IAL 3 (Very high confidence)
        tc_asc_IdentityAssuranceLevelCd=self.rng.choice(
            ["","IAL1","IAL2","IAL3"], p=self.p_identity_assurance
        )
        tc_asc_AuthenticatorAssuranceLevelCd=self.rng.choice(
            ["","AAL1","AAL2","AAL3"],p=self.p_authenticator_assurance
        )
        tc_asc_FederationAssuranceLevelCd=self.rng.choice(
            ["","FAL1","FAL2","FAL3"], p=self.p_federal_assurance
        )
        
        # PaymentDeclineCd - "String2Type"
        #   0 = DECLINED MORE THAN TWICE BEFORE APPROVED
        #   1 = APPROVED ON THE FIRST OR SECOND ATTEMPT
        #   2 = UNABLE TO VERIFY
        tc_PaymentDeclineCd=self.rng.choice(["","0","1","2"],p=self.p_payment_decline)
        
        # AuthenticationReviewCd @TODO maybe more analysis here
        # ONLY OPTIONS 5, 6 AND 7 ARE BEING USED
        # 5 = AUTHENTICATION - the software is using advanced authentication
        #     techniques AND the taxpayer has opted in to using an advanced
        #     technique (unrestricted factor).
        # 6 = SSN DUP -  the primary and/or secondary SSN 
        #     is being used in a new account in
        #     the current year that was used by a different account
        #     in the previous year.
        # 7 = OTHER OR when the refund disbursement is utilizing 
        #     cryptocurrency and NoUBADisbursementCdSubmit is equal to "5".
        tc_AuthenticationReviewCd=self.rng.choice(["","5","6","7"])

        
        # 2. ReturnHeader File
        # 2.1 General fields
        ReturnTS = td_sub_IPTs
        TaxPeriodBeginDt = dt.datetime(year=TaxYr, month=1, day=1).date()
        TaxPeriodEndDt = dt.datetime(year=TaxYr, month=12, day=31).date()
        # 2.2 PaidPreparerInformationGrp section
        p_preparer = 0.3
        rand_prep = self.rng.rand()
        if rand_prep < p_preparer:
            preparer_flag = 1
            pp_SelfEmployedInc = self.rng.choice([0,1], p=[0.7, 0.3])
            pp_PreparerSSN = self.social_gen.get_sample()
            pp_PTIN = self.ptin_gen.get_sample()
            pp_PreparerFirmEIN = self.rng.choice(["",self.ein_gen.get_sample()])
            preparer = self.taxpayer_indiv_data_gen.get_record()
            record2 = self.taxpayer_indiv_data_gen.get_record()
            pp_PreparerPersNm = preparer.compositename
            pp_us_AddressLine1Txt = preparer.streetno \
                + " " + preparer.streetname
            pp_us_AddressLine2Txt = preparer.aptno \
                if preparer.aptno is not None else ""
            pp_us_CityNm = preparer.city
            pp_us_StateAbbreviationCd = self.state_of_sample
            pp_us_ZIPCd = preparer.zipcode
            pp_us_InCareOf = self.rng.choice(
                ["", record2.compositename, pp_PreparerPersNm], 
                p=[0.3, 0.3, 0.4]
            )
            pp_PhoneNum = preparer.phoneno 
            pp_EmailAddress = preparer.email
        else:
            preparer_flag = 0
            pp_SelfEmployedInc = pp_PTIN = pp_PreparerSSN = pp_PreparerFirmEIN = ""
            preparer = None
            pp_PreparerPersNm = pp_us_AddressLine1Txt = pp_us_AddressLine2Txt = \
                pp_us_CityNm = pp_us_StateAbbreviationCd = pp_us_ZIPCd = \
                pp_us_InCareOf = pp_PhoneNum = pp_EmailAddress = ""

    
        # 2.3 Filer section
        # Filer sec appear in jointly filing
        # Filer fraud appear in cases of fraudulent accounts (or different
        # accounts in refund than payments that are no fraudulent, but uncommon)
        filer_prim = self.taxpayer_indiv_data_gen.get_record()
        filer_sec = self.rng.choice(
            [0, self.taxpayer_indiv_data_gen.get_record()]
        )
        filer_fraud = self.taxpayer_indiv_data_gen.get_record()
        fi_prim_tn_FirstName = filer_prim.firstname
        fi_prim_tn_MiddleInitial = filer_prim.middlename[0]
        fi_prim_tn_LastName = filer_prim.lastname
        fi_prim_TaxpayerSSN = self.social_gen.get_sample()
        fi_prim_DateofBirth = filer_prim.birthday.date()
        fi_prim_USPhone = str(filer_prim.phoneno)
        fi_prim_TaxpayerPIN = self.pin_gen.get_sample()
        

        if filer_sec !=	0:
            fi_sec_tn_FirstName = filer_sec.firstname	
            fi_sec_tn_MiddleInitial = filer_sec.middlename[0]
            fi_sec_tn_LastName = filer_sec.lastname
            fi_sec_TaxpayerSSN = self.social_gen.get_sample()
            fi_sec_DateofBirth = filer_sec.birthday.date()

            few_days_diff = dt.timedelta(days=self.rng.randint(low=-7, high=7))
            fi_sec_DateSigned = max(pd.Timestamp(fi_prim_DataSigned + few_days_diff), td_sub_IPTs)

            fi_sec_USPhone = str(filer_sec.phoneno)
        if filer_sec == 0:
            fi_sec_tn_FirstName = fi_sec_tn_MiddleInitial = \
            fi_sec_tn_LastName = fi_sec_TaxpayerSSN = fi_sec_DateofBirth = \
            fi_sec_DateofDeath = fi_sec_TaxpayerPIN = fi_sec_DateSigned = \
            fi_sec_USPhone = None
            
            filer_sec = Record(datatype=NameIdDataType, autopop={},
                taxpayertype="",
                firstname="",
                lastname="",
                middlename="",
                ethnicity="",
                compositename="",
                maidenname="",
                birthday="",
                taxid="",
                compositeaddress="",
                streetno="",
                aptno=0,
                streetname="",
                city="",
                zipcode=0,
                phoneno=0,
                email="",
                metric_id=""
                )
            
            # STIN: preparer identification number for elderly
        # pp_STIN = ""
        # if rand_prep < p_preparer:
        #     if filer_sec == 0:
        #         if filer_prim.age >= 60:
        #             pp_STIN == self.rng.choice(["", "S" + str(self.stin_gen.get_sample())], p=[0.75, 0.25])
        #     else:
        #         if filer_prim.age >= 60 or filer_sec.age >= 60:
        #             pp_STIN == self.rng.choice(["", "S" + str(self.stin_gen.get_sample())], p=[0.75, 0.25])

        # 3. FinancialTransactions File
        # 3.1 StatePayment section
        # Generate two accounts, since bank accounts must be 
        # from primer or secundary filer
        # AccontHolderType: 1: Business 2: Personal
        
        date_in_after_calendar_year = random_datetimes(start= pd.to_datetime(str(TaxYr+1) + '-01-01'),
            end=pd.to_datetime(str(TaxYr+1)+'-12-31'),
            out_format='datetime', rng=self.rng, n=1
        )

        # Most of people prefer April 15th, which is the last possible date without interest
        sp_RequestedPaymentDate = self.rng.choice(
            [pd.to_datetime(str(TaxYr+1)+'-04-15').date(), 
                date_in_after_calendar_year], 
            p=[0.80, 0.20]
        )

        # Primary
        filer_prim_fin = self.fin_gen.get_record(
            holdername=filer_prim.compositename
            )
        
        # Managing the jointly/non jointly cases
        if filer_sec == 0 :
            [p_prim, p_sec] = [1, 0]
        else: [p_prim, p_sec] = [0.75, 0.25]
        
        is_prim = self.rng.choice([True, False], p=[p_prim, p_sec])
        
        # If it is a jointly filing        
        if filer_sec != 0:
           #Create bank accout for spouse:
           filer_sec_fin = self.fin_gen.get_record(
               holdername=filer_sec.compositename)
        
        if is_prim:
            # Prefer to list all characteristics to be flexible and avoid errors
            # of eventual data that may be missing
             sp_Checking = filer_prim_fin.Checking
             sp_Savings = filer_prim_fin.Savings
             sp_RoutingTransitNumber = filer_prim_fin.RoutingTransitNumber
             sp_BankAccountNumber = filer_prim_fin.BankAccountNumber
             sp_AccountHolderName = filer_prim_fin.AccountHolderName
             sp_AccountHolderType = filer_prim_fin.AccountHolderType
             sp_NotIATTransaction = filer_prim_fin.NotIATTransaction
             sp_IsIATTransaction = filer_prim_fin.IsIATTransaction
             sp_IdentificationNumber = filer_prim_fin.IdentificationNumber

              
        else:
             sp_Checking = filer_sec_fin.Checking
             sp_Savings = filer_sec_fin.Savings
             sp_RoutingTransitNumber = filer_sec_fin.RoutingTransitNumber
             sp_BankAccountNumber = filer_sec_fin.BankAccountNumber
             sp_AccountHolderName = filer_sec_fin.AccountHolderName
             sp_AccountHolderType = filer_sec_fin.AccountHolderType
             sp_NotIATTransaction = filer_sec_fin.NotIATTransaction
             sp_IsIATTransaction = filer_sec_fin.IsIATTransaction

             sp_IdentificationNumber = filer_sec_fin.IdentificationNumber
        
        sp_PaymentAmount = gen_money(rng=self.rng)

        
        # 3.2 RefundDirectDeposit section
        # Other account is possible, in case there is a change in the bank account. Low probability.
        # But may be a higher prob in case of fraud, and someone creating a 
        # fraudulent account in the filer's name(s)

        filer_fraud_fin = self.fin_gen.get_record(
            holdername=[self.rng.choice([filer_prim.compositename, 
                filer_sec.compositename], p=[p_prim, p_sec])]
            )
        
        # We make a distinction between accounts if it is or not fraud
        if self.yml_key =='fraud':
            [p_prim_rdd, p_sec_rdd, p_fraud_rdd] = [0.25, 0.25, 0.5]
            if filer_sec == 0:
                [p_prim_rdd, p_sec_rdd, p_fraud_rdd] = [0.5, 0, 0.5]
        else:
            [p_prim_rdd, p_sec_rdd, p_fraud_rdd] = [0.70, 0.25, 0.05]
            if filer_sec == 0:
                [p_prim_rdd, p_sec_rdd, p_fraud_rdd] = [0.95, 0, 0.05]
        
        prim_sec_other = self.rng.choice(["prim", "sec", "other"],
            p=[p_prim_rdd, p_sec_rdd, p_fraud_rdd])

        if prim_sec_other == "prim":
            rdd_Checking = filer_prim_fin.Checking
            rdd_Savings = filer_prim_fin.Savings
            rdd_RoutingTransitNumber = filer_prim_fin.RoutingTransitNumber
            rdd_BankAccountNumber = filer_prim_fin.BankAccountNumber
            rdd_AccountHolderName = filer_prim_fin.AccountHolderName
            rdd_NotIATTransaction = filer_prim_fin.NotIATTransaction
            rdd_IsIATTransaction = filer_prim_fin.IsIATTransaction

            rdd_TelephoneNumber = self.rng.choice(
                [filer_prim.phoneno, filer_sec.phoneno], p=[0.8,0.2]
            )

        elif prim_sec_other == "sec":
            rdd_Checking = filer_sec_fin.Checking
            rdd_Savings = filer_sec_fin.Savings
            rdd_RoutingTransitNumber = filer_sec_fin.RoutingTransitNumber
            rdd_BankAccountNumber = filer_sec_fin.BankAccountNumber
            rdd_AccountHolderName = filer_sec_fin.AccountHolderName
            rdd_NotIATTransaction = filer_sec_fin.NotIATTransaction
            rdd_IsIATTransaction = filer_sec_fin.IsIATTransaction

            rdd_TelephoneNumber = self.rng.choice([filer_prim.phoneno, filer_sec.phoneno], p=[0.2,0.8])

        # Higher probability on fraud case
        else: 
            rdd_Checking = filer_fraud_fin.Checking
            rdd_Savings = filer_fraud_fin.Savings
            rdd_RoutingTransitNumber = filer_fraud_fin.RoutingTransitNumber
            rdd_BankAccountNumber = filer_fraud_fin.BankAccountNumber
            rdd_AccountHolderName = filer_fraud_fin.AccountHolderName
            rdd_NotIATTransaction = filer_fraud_fin.NotIATTransaction
            rdd_IsIATTransaction = filer_fraud_fin.IsIATTransaction

            # In case of fraud, we may expect to have a phone that is not from the filers
            rdd_TelephoneNumber = self.rng.choice(
                [filer_prim.phoneno,filer_sec.phoneno,filer_fraud.phoneno], p=[p_prim_rdd, p_sec_rdd, p_fraud_rdd]
            )
                
        # In case of preparer, the telephone number will be from it with high probability
        if preparer_flag:
            if filer_sec == 0:
                rdd_TelephoneNumber = self.rng.choice([preparer.phoneno, filer_prim.phoneno], p=[0.85, 0.15]
                )
            else:
                rdd_TelephoneNumber = self.rng.choice(
                    [preparer.phoneno, filer_prim.phoneno, filer_sec.phoneno], p=[0.8, 0.15, 0.05]
                )

        rdd_Amount = abs(sp_PaymentAmount - self.rng.uniform(0, abs(math.floor(sp_PaymentAmount))))


        # 3.3 EstimatedPayments section (they can be several (usually 4) in one year)
        # Similarly to the Refund, usually the accounts will be the same.
        # However, since money is not coming in, fraudulent activity
        # should not come from here
        # Will just consider one payment, that usually will be for about 0.25 
        # Of the payment of the prior year
        is_prim = self.rng.choice([True, False], p=[p_prim, p_sec])
        
        date_in_calendar_year = random_datetimes(start = pd.to_datetime(str(TaxYr)+'-01-01'),
            end = pd.to_datetime(str(TaxYr)+'-12-31'),
            out_format='datetime', rng=self.rng, n=1
        )
        # Deadlines are on April 15th, June 15th, Sept 15th and Jan 15th
        # Will do just one case
        ep_RequestedPaymentDate = self.rng.choice(
             [pd.to_datetime(str(TaxYr)+'-06-15').date(), 
              pd.to_datetime(str(TaxYr)+'-09-15').date(),
              pd.to_datetime(str(TaxYr+1)+'-01-15').date(),
              date_in_calendar_year.date()], p=[0.30,0.30,0.30,0.10]
        )
        
        if is_prim:
             ep_Checking = filer_prim_fin.Checking
             ep_Savings = filer_prim_fin.Savings
             ep_RoutingTransitNumber = filer_prim_fin.RoutingTransitNumber
             ep_BankAccountNumber = filer_prim_fin.BankAccountNumber
             ep_AccountHolderName = filer_prim_fin.AccountHolderName
             ep_AccountHolderType = filer_prim_fin.AccountHolderType
             ep_NotIATTransaction = filer_prim_fin.NotIATTransaction
             ep_IsIATTransaction = filer_prim_fin.IsIATTransaction
             ep_IdentificationNumber = filer_prim_fin.IdentificationNumber
            
        else:
             ep_Checking = filer_sec_fin.Checking, 
             ep_Savings = filer_sec_fin.Savings, 
             ep_RoutingTransitNumber = filer_sec_fin.RoutingTransitNumber
             ep_BankAccountNumber = filer_sec_fin.BankAccountNumber
             ep_AccountHolderName = filer_sec_fin.AccountHolderName
             ep_AccountHolderType = filer_sec_fin.AccountHolderType
             ep_NotIATTransaction = filer_sec_fin.NotIATTransaction
             ep_IsIATTransaction = filer_sec_fin.IsIATTransaction
             ep_IdentificationNumber = filer_sec_fin.IdentificationNumber
        
        ep_PaymentAmount = gen_money(rng=self.rng,
                                          mean=(sp_PaymentAmount/4),
                                          stdev=sp_PaymentAmount/10
        )
        
        # Flag to indicate fraudulent status
        is_fraud=(1 if self.yml_key=='fraud' else 0)
        
        rec_ah = Record(datatype=MefAuthenticationHeaderData, 
                        corruptible=MefAuthenticationHeaderDataCorruptible,
                        lenth_changable=MefAuthenticationHeaderDataLengthChangable,autopop={},
                        rng=self.rng,
                        td_ini_IPAddress=td_ini_IPAddress,
                        td_ini_MACAddress=td_ini_MACAddress,
                        td_ini_IPTs=td_ini_IPTs,
                        td_ini_DeviceID=td_ini_DeviceID, 
                        td_ini_DeviceTypeCd=td_ini_DeviceTypeCd,
                        td_ini_BrowserLanguageTxt=np.nan,
                        td_sub_IPAddress=td_sub_IPAddress,
                        td_sub_MACAddress= td_sub_MACAddress,
                        td_sub_IPTs=td_sub_IPTs,
                        td_sub_DeviceID=td_sub_DeviceID,
                        td_sub_DeviceTypeCd=td_sub_DeviceTypeCd,
                        td_sub_BrowserLanguageTxt=np.nan,
                        td_TotActiveTimePrepSubmissionTs = td_TotActiveTimePrepSubmissionTs,
                        td_TotalPreparationSubmissionTs= td_TotalPreparationSubmissionTs,
                        tc_TrustedCustomerCd=tc_TrustedCustomerCd,
                        tc_OOBSecurityVerificationCd=tc_OOBSecurityVerificationCd,
                        tc_LastSubmissionRqrOOBCd=tc_LastSubmissionRqrOOBCd,
                        tc_pc_UserNameChangeInd=tc_pc_UserNameChangeInd,
                        tc_pc_EmailAddressChangeInd=tc_pc_EmailAddressChangeInd,
                        tc_pc_CellPhoneNumberChangeInd=tc_pc_CellPhoneNumberChangeInd,
                        tc_pc_PasswordChangeInd=tc_pc_PasswordChangeInd,
                        tc_asc_IdentityAssuranceLevelCd=tc_asc_IdentityAssuranceLevelCd,
                        tc_asc_AuthenticatorAssuranceLevelCd=tc_asc_AuthenticatorAssuranceLevelCd,
                        tc_asc_FederationAssuranceLevelCd=tc_asc_FederationAssuranceLevelCd,
                        tc_PaymentDeclineCd=tc_PaymentDeclineCd,
                        tc_AuthenticationReviewCd=tc_AuthenticationReviewCd,
                        tc_AuthenticationReviewTxt=np.nan,
                        is_fraud=is_fraud
                        )
        rec_rh = Record(datatype=MefReturnHeaderData, 
                        corruptible=MefReturnHeaderDataCorruptible,
                        lenth_changable=MefReturnHeaderDataLengthChangable,autopop={},
                        rng=self.rng,
                        ReturnTS = ReturnTS,
                        TaxYr=TaxYr,
                        TaxPeriodBeginDt=TaxPeriodBeginDt, 
                        TaxPeriodEndDt=TaxPeriodEndDt,
                        pp_SelfEmployedInc=pp_SelfEmployedInc,
                        pp_PTIN=pp_PTIN,
                        pp_PreparerSSN=pp_PreparerSSN,
                        pp_PreparerFirmEIN=pp_PreparerFirmEIN,
                        pp_PreparerPersNm=pp_PreparerPersNm,
                        pp_us_AddressLine1Txt=pp_us_AddressLine1Txt,
                        pp_us_AddressLine2Txt=pp_us_AddressLine2Txt,
                        pp_us_CityNm=pp_us_CityNm,
                        pp_us_StateAbbreviationCd=pp_us_StateAbbreviationCd,
                        pp_us_ZIPCd=pp_us_ZIPCd,
                        pp_us_InCareOf=pp_us_InCareOf,
                        pp_PhoneNum=pp_PhoneNum,
                        pp_EmailAddress=pp_EmailAddress,
                        fi_prim_tn_FirstName=fi_prim_tn_FirstName,
                        fi_prim_tn_MiddleInitial=fi_prim_tn_MiddleInitial,
                        fi_prim_tn_LastName=fi_prim_tn_LastName,
                        fi_prim_TaxpayerPIN=fi_prim_TaxpayerPIN,
                        fi_prim_TaxpayerSSN=fi_prim_TaxpayerSSN,
                        fi_prim_DateofBirth=fi_prim_DateofBirth,
                        fi_prim_DataSigned=fi_prim_DataSigned,
                        fi_prim_USPhone=fi_prim_USPhone,
                        fi_sec_tn_FirstName=fi_sec_tn_FirstName	,
                        fi_sec_tn_MiddleInitial=fi_sec_tn_MiddleInitial,
                        fi_sec_tn_LastName=fi_sec_tn_LastName,
                        fi_sec_TaxpayerSSN=fi_sec_TaxpayerSSN,
                        fi_sec_DateofBirth=fi_sec_DateofBirth,
                        fi_sec_DateSigned=fi_sec_DateSigned,
                        fi_sec_USPhone=fi_sec_USPhone,
                        is_fraud=is_fraud
                    )
        
        rec_ft = Record(datatype=MefFinancialTransactionsData, 
                        corruptible=MefFinancialTransactionsDataCorruptible,
                        lenth_changable=MefFinancialTransactionsDataLengthChangable,autopop={},
                        rng=self.rng,
                        sp_Checking=sp_Checking,
                        sp_Savings=sp_Savings,
                        sp_RoutingTransitNumber=sp_RoutingTransitNumber,
                        sp_BankAccountNumber=sp_BankAccountNumber,
                        sp_PaymentAmount=sp_PaymentAmount,
                        sp_IdentificationNumber=sp_IdentificationNumber,
                        sp_AccountHolderType=sp_AccountHolderType,
                        sp_RequestedPaymentDate = sp_RequestedPaymentDate,
                        sp_NotIATTransaction=sp_NotIATTransaction,
                        sp_IsIATTransaction=sp_IsIATTransaction,
                        rdd_Checking=rdd_Checking,
                        rdd_Savings=rdd_Savings,
                        rdd_RoutingTransitNumber=rdd_RoutingTransitNumber,
                        rdd_BankAccountNumber=rdd_BankAccountNumber,
                        rdd_Amount=rdd_Amount,
                        rdd_TelephoneNumber=rdd_TelephoneNumber,
                        rdd_NotIATTransaction=rdd_NotIATTransaction,
                        rdd_IsIATTransaction=rdd_IsIATTransaction,
                        ep_Checking=ep_Checking,
                        ep_Savings=ep_Savings,
                        ep_RoutingTransitNumber=ep_RoutingTransitNumber,
                        ep_BankAccountNumber=ep_BankAccountNumber,
                        ep_PaymentAmount=ep_PaymentAmount,
                        ep_IdentificationNumber=ep_IdentificationNumber,
                        ep_AccountHolderName=ep_AccountHolderName,
                        ep_AccountHolderType=ep_AccountHolderType,
                        ep_RequestedPaymentDate=ep_RequestedPaymentDate,
                        ep_NotIATTransaction=ep_NotIATTransaction,
                        ep_IsIATTransaction=ep_IsIATTransaction,
                        is_fraud=is_fraud
            )

        return [rec_ah , rec_rh, rec_ft] 

class FraudMefDataGen(MefDataGen):
    def __init__(self,config,rng=None,seed=None,config_key='fraud',debug=False): 
        super(FraudMefDataGen,self).__init__(config,rng=rng,seed=seed,config_key=config_key,debug=debug) 

class MefDatasetGenerator(object):
    logging.debug("Initializing the Mef Dataset Generator")
    def __init__(self, config, rng=None, p_fraud=0.01,
                 seed=None, debug=False, 
                 as_df=True,
                 export_csv=True
    ):
        self.p_fraud = p_fraud
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml=config
        self.debug=debug
        self.legit_gen = MefDataGen(config=self.yml,rng=self.rng)
        self.fraud_gen = FraudMefDataGen(config=self.yml,rng=self.rng)
        self.as_df = as_df
        self.export_csv=export_csv

    def gen_records(self,num):
        """Generates records for three MeF files:
        AutenthicationHeader,
        ReturnHeader,
        FinancialTransactions."""
        logging.debug("Generating records...")
        recs_ah=[]
        recs_rh=[]
        recs_ft=[]
        for _ in range (num):
            is_fraud = (self.rng.uniform() < self.p_fraud)
            
            if is_fraud:
                [new_recs_ah , new_recs_rh, new_recs_ft] = self.fraud_gen.get_record()
            else:
                [new_recs_ah , new_recs_rh, new_recs_ft] = self.legit_gen.get_record()
                
            recs_ah.append(new_recs_ah)
            recs_rh.append(new_recs_rh)
            recs_ft.append(new_recs_ft)
        
        logging.info('MeF tax fraud generated')


        if self.as_df or self.export_csv:
        # Convert records into dataframes
            recs_ah_df = Record.as_dataframe(recs_ah)
            recs_rh_df = Record.as_dataframe(recs_rh)
            recs_ft_df = Record.as_dataframe(recs_ft)

        if self.export_csv:
            recs_ah_df.to_csv("mef_authentication_header.csv")
            recs_rh_df.to_csv("mef_return_header.csv")
            recs_ft_df.to_csv("mef_financial_transactions.csv")
            logging.info("CSV Files succesfully exported")

        if self.as_df:
            return [recs_ah_df, recs_rh_df, recs_ft_df]
        else:
            return [recs_ah, recs_rh, recs_ft]




#############################################
if __name__ == '__main__':
    
    path_to_config = os.path.join(os.path.dirname(os.path.abspath(__file__)),'./tests')
    yml = YmlConfig(path_to_config, read_all=True, ext='yaml', auto_update_paths=True)
    
    # Define the arguments
    parser = argparse.ArgumentParser(
    description='''
This code generates random MeF data, including fraudulent records.

Example command line call:
    python mef_datagen.py --n_samples=10 --seed=19 --p_fraud=0.01  --export_csv --debug    
''')
    
    parser.add_argument('--n_samples', type=int,
                        help='Number of records to generate', default=10)
    parser.add_argument('--seed', type=int,
                        help='Seed to start random state', default=19)
    parser.add_argument('--p_fraud', type=float,
                        help='Probability for a record to be fraudulent', default=0.01)
    # parser.add_argument('--p_duplicates', type=float,
    #                     help='What proportion or fraudulent records should have a duplicate ip or bank info', default=0.2)
    parser.add_argument('--export_csv', action='store_true',
                        help='Export to CSV', default=True)
    parser.add_argument('--debug', action='store_true',
                        help='Enable debugging', default=False)

    # Parse the arguments
    args = parser.parse_args()
    
    # Generate the random number generator
    rng = np.random.RandomState(seed=args.seed)

    # MeF 3 Dataframes Generation
    
    mef_df_generator = MefDatasetGenerator(
                            config=yml, 
                            seed=args.seed, 
                            p_fraud=args.p_fraud,
                            export_csv=args.export_csv,
                            debug=args.debug
    )

    [mef_recs_ah_df, mef_recs_rh_df, mef_recs_ft_df]  = \
        mef_df_generator.gen_records(num=args.n_samples)


    
#@TODO: addition of duplicates using the duplicates function
