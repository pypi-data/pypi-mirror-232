"""Contains the IRS Blacklist data Classes Definition for fraud models

The files implemented are:
 - SIR-029 Weekly Individual Questionable
 - SIR-024 Prior Year Individual Confirmed
 - SIR-075-Preparer TIN (PTIN)
 - SIR-027 ITPI ID Theft Indicator
 - SIR-025 PITRF700 Incident file
 - SIR-114(Federal Prisoner Files)
 - PITRF800 ISAC Alerts (SIR-117) & PITRF200 Suspect Email Domains (SIR-118)
 - SIR-073 ITIN by State Code
 - SIR-116 (PITRF500 - IRS EFIN)
 - PITRFGEN (800,801,200)

Main field for fraud are generated. Fields with null values are not 
relevant or will be implemented in the future.

Configuration used for this files are the same as the one used for
fraudulent cases (config_key = 'fraud')

Teh fields 'state' and 'country' have been harcoded because
datagen.py is not providing them along with the addresses. 
However all current datagen samples are from Maryland, 
so MD and US has been hardcoded. Harcoded fields appear as "harcoded'
in the config (yaml) file.
"""


import datetime as dt
from datetime import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Union, Tuple
import os
import yaml
from enum import Enum, auto
import logging
import argparse
import math
from rsidatasciencetools.datautils.mef_data.mef_datagen import (
     DeviceIdGen, gen_money, MefDataGen, calculate_age, 
     EinGen, PtinGen, EtinGen, ItinGen, EfinGen
)
from rsidatasciencetools.datautils.fraud_data.fraud_data_generator import (
    GenDateTimeRegistry, GenBankInfo, IPv4Address, GenSSN
)
from rsidatasciencetools.datautils.datagen import IdSource, Record, RecordGenerator, random_datetimes

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.debug("Defining Classes")


class SIR029WeeklyIndividualQuestionable(Enum):
    primary_tin = auto()
    name_control = auto()
    taxperiod = auto() # Not implemented yet
    secondary_tin = auto()
    name_line1 = auto()
    mail_address = auto()
    city = auto() 
    State = auto()
    zipcode = auto()
    bal_due_amt_comp = auto() 
    routing_trans_num = auto()
    undesirable_bank_acc = auto()
    preparer_ssn_ptin = auto()
    preparer_ein = auto()
    preparer_phone = auto()
    scored_date = auto() # Not implemented yet
    ip_address = auto()
    efin = auto()
    agi_comp = auto()
    device_id_submission = auto()
    device_id_creation = auto()
    email_address = auto()
    email_address_add = auto()
    ip_address_creation = auto() # Not implemented yet
    preparation_time = auto()
    bank_product = auto() # Not implemented yet
    routing_trans_num_ult = auto()
    undesirable_bank_acc_ult = auto()
    cellphone = auto()

    
class SIR024PriorYearIndividualConfirmed(Enum):
    primary_ssn = auto()
    secondary_ssn = auto()
    name_line = auto()
    address = auto()
    city = auto()
    State = auto()
    zipcode = auto()
    taxperiod = auto() # Not implemented yet
    refund_amt = auto() 
    efin = auto()
    preparer_tin = auto()
    routing_trans_num = auto()
    undesirable_bank_acc = auto()
    load_date = auto() # Not implemented yet
    ip_address = auto()
    email_address = auto()
    
class SIR075PreparerTIN(Enum):
    ssn = auto()
    ptin = auto()
    ptin_issue_date = auto()
    ptin_status = auto()
    last_name = auto()
    first_name = auto()
    middle_name = auto()
    suffix = auto()
    birth_date = auto()
    email_addr = auto()
    perm_addr_line1 = auto()
    perm_addr_line2 = auto()
    perm_addr_line3 = auto()
    perm_city = auto()
    perm_state = auto()
    perm_zip = auto()
    perm_country = auto()
    phone = auto()
    ext = auto()
    bus_phone = auto()
    bus_ext = auto()
    ein = auto()
    efin = auto()
    office_own_ind = auto()
    bus_addr_line1 = auto()
    bus_addr_line2 = auto()
    bus_addr_line3 = auto()
    bus_city = auto()
    bus_state = auto()
    bus_zip = auto()
    bus_country = auto()
    bus_name = auto()
    self_rep_felony_ind = auto()
    pers_tax_compl_ind = auto()
    professions = auto()
    paid_prep_1040_ind = auto()
    afsp_tcc_exmp_ind = auto()
    afsp_consent_elect_ind = auto()
    for_future_use1 = auto()
    for_future_use2 = auto()
    afsp_course_exmp_ind = auto()
    prep_dir_opt_out_ind = auto()
    afsp_eff_date = auto()
    aftr_complete_date = auto()
    irs_tax_compl_ind = auto()
    reserved = auto()
    afsp_ineligible_ind = auto()
    ptin_renewal_date = auto()
    
class SIR027ITPIIDTheftIndicator(Enum):
    extract_Identifier = auto()
    primary_tin_validity_digit = auto()
    primary_tin = auto()
    taxpayer_name_line = auto()
    name_control = auto()
    reserved1 = auto()
    address = auto()
    city = auto()
    zipcode = auto()
    State = auto()
    charctercnt_to_lastname = auto()
    charactercnt_in_lastname = auto()
    reserved2 = auto()
    idtheft_protection_inda = auto()
    reserved3 = auto()
    idtheft_protection_indb = auto()
    reserved4 = auto()
    
    
class SIR023CurrentYearIndividualQuestionable(Enum):
    primary_tin = auto()
    name_control = auto()
    tax_period = auto()
    secondary_tin = auto()
    name_line_1 = auto()
    mail_address = auto()
    city = auto()
    state = auto()
    zip_code = auto()
    bal_due_amt_comp = auto()
    bank_account_key = auto()
    bank_account_num = auto()
    preparer_ssn_ptin = auto()
    preparer_ein = auto()
    preparer_phone = auto()
    scored_date = auto()
    ip_address = auto()
    efin = auto()
    agi_comp = auto()
    
class SIR025PITRF700Incidentfile(Enum):
    primary_tin = auto()
    name_control = auto()
    tax_period_year = auto()
    secondary_tin = auto()
    name_line1 = auto()
    mail_address = auto()
    city = auto()
    state = auto()
    zipcode = auto()
    
class SIR114FederalPrisonerFiles(Enum):
    first_name = auto()
    middle_name = auto()
    last_name = auto()
    date_of_birth = auto()
    ssn = auto()
    verified_ssn  = auto()
    offender_number = auto()
    incarceration_date = auto()
    work_release_date= auto()
    release_date = auto()
    institution_code = auto()
    release_date_code = auto()

class SIR117PITRF800SIR118PITRF200ISACAlertsAndSuspectEmailDomains(Enum):
    device_id = auto()
    ip_address = auto()
    email = auto()
    payer_tin = auto()
    efin = auto()

class PITRF500EfinSIR116(Enum):
    efin_irs = auto()
    efin_stat_cd_irs = auto()
    etin_irs = auto()
    etin_irs2 = auto()
    etin_irs3 = auto()
    etin_irs4 = auto()
    etin_irs5 = auto()
    etin_irs6 = auto()
    etin_irs7 = auto()
    legal_name = auto()
    ero_status = auto()
    ero_effdt = auto()
    trmt_status = auto()
    trmt_effdt = auto()
    swdv_status = auto()
    swdv_effdt = auto()
    isp_status = auto()
    isp_effdt = auto()
    olf_status = auto()
    olf_effdt = auto()
    lgxt_status = auto()
    lgxt_effdt = auto()
    tin_type_irs = auto()
    tin_irs = auto()
    last_name = auto()
    first_name = auto()
    middle_name = auto()
    country_code = auto()
    phone = auto()
    email_addr = auto()
    address1 = auto()
    address2 = auto()
    address3 = auto()
    city = auto()
    state = auto()
    postal = auto()
    country = auto()

class SIR073ITINByStateCode(Enum):
    itin = auto()
    mailing_state_province = auto()
    history = auto()
    itin_status_id = auto()
    revoked_reason_code = auto()
    application_reason = auto()
    citizen_alien_first_name = auto()
    citizen_alien_middle_name = auto()
    citizen_alien_last_name = auto()
    treaty_article_number = auto()
    legal_first_name = auto()
    legal_middle_name = auto()
    legal_last_name = auto()
    birth_certificate_first_name = auto()
    birth_certificate_middle_name = auto()
    birth_certificate_last_name = auto()
    mailing_address_line_1 = auto()
    mailing_address_line_2 = auto()
    mailing_city = auto()
    mailing_country_id = auto()
    mailing_zip_code = auto()
    foreign_address_line_1 = auto()
    foreign_address_line_2 = auto()
    foreign_city = auto()
    foreign_state_province = auto()
    foreign_country_id = auto()
    foreign_postal_code = auto()
    birth_date = auto()
    country_of_birth = auto()
    birth_city_state_or_province = auto()
    gender = auto()
    country_of_citizenship = auto()
    previous_tin = auto()
    previous_ein = auto()
    name_of_college_university_or_company = auto()
    college_university_or_company_city = auto()
    college_university_or_company_state = auto()
    college_university_or_company_length_of_stay = auto()
    date_application_signed = auto()
    name_of_delegate = auto()
    phone_number = auto()
    foreign_tax_id = auto()
    passport_expiration_date = auto()
    passport_id_number = auto()
    country_issuing_passport = auto()
    state_issuing_passport = auto()
    us_entry_date = auto()
    documentation_type_id = auto()
    driver_license_expiration_date = auto()
    driver_license_id_number = auto()
    country_issuing_driver_license = auto()
    state_issuing_driver_license = auto()
    us_entry_date_2 = auto()
    documentation_type_id_2 = auto()
    uscis_documentation_expiration_date = auto()
    uscis_documentation_id_number = auto()
    uscis_documentation_issuing_country = auto()
    uscis_documentation_issuing_state = auto()
    us_entry_date_3 = auto()
    documentation_type_id_3 = auto()
    
class PITRFGEN800_801_200(Enum):
    undesirable_id_type = auto()
    undesirable_value = auto()

# Corruptible - Not Maintained
class SIR029WeeklyIndividualQuestionableCorruptible(Enum):
    """Class not mainteined, but required to run"""
    name_line1 = auto()

class SIR024PriorYearIndividualConfirmedCorruptible(Enum):
    """Class not mainteined, but required to run"""
    name_line = auto()
    
class SIR075PreparerTINCorruptible(Enum):
    """Class not mainteined, but required to run"""
    name_line1 = auto()
    
class SIR027ITPIIDTheftIndicatorCorruptible(Enum):
    """Class not mainteined, but required to run"""
    taxpayer_name_line = auto()

class SIR023CurrentYearIndividualQuestionableCorruptible(Enum):
    """Class not mainteined, but required to run"""
    name_line1 = auto()
    
class SIR025PITRF700IncidentfileCorruptible(Enum):
    """Class not mainteined, but required to run"""
    name_line1 = auto()

class SIR114FederalPrisonerFilesCorruptible(Enum):
    """Class not mainteined, but required to run"""
    first_name = auto()

class SIR117PITRF800SIR118PITRF200ISACAlertsAndSuspectEmailDomainsCorruptible(Enum):
    """Class not mainteined, but required to run"""
    email = auto()

class PITRF500EfinSIR116Corruptible(Enum):
    """Class not mainteined, but required to run"""
    last_name = auto()
    
class SIR073ITINByStateCodeCorruptible(Enum):
    """Class not mainteined, but required to run"""
    citizen_alien_first_name = auto()
    
class PITRFGEN800_801_200Corruptible(Enum):
    """Class not mainteined, but required to run"""
    undesirable_value = auto()


# Length Changeable - Not Maintained
class SIR029WeeklyIndividualQuestionableLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    name_line1 = auto()

class SIR024PriorYearIndividualConfirmedLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    name_line = auto()
    
class SIR075PreparerTINLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    name_line1 = auto()

class SIR027ITPIIDTheftIndicatorLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    taxpayer_name_line = auto()

class SIR023CurrentYearIndividualQuestionableLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    name_line1 = auto()

class SIR025PITRF700IncidentfileLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    name_line1 = auto()
    
class SIR114FederalPrisonerFilesLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    first_name = auto()
class SIR117PITRF800SIR118PITRF200ISACAlertsAndSuspectEmailDomainsLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    email = auto()
class PITRF500EfinSIR116LengthChangable(Enum):
    """Class not mainteined, but required to run"""
    last_name = auto()

class SIR073ITINByStateCodeLengthChangable(Enum):
    """Class not mainteined, but required to run"""
    citizen_alien_first_name = auto()
    
class PITRFGEN800_801_200LengthChangable(Enum):
    """Class not mainteined, but required to run"""
    undesirable_value = auto()
    
class PrisonerSimulator():
    """
    A class for simulating incarceration, work release, and release dates for prisoners.

    Parameters:
    - min_incarceration_years (int): Minimum number of years for incarceration.
        Defautl to 1
    - max_incarceration_years (int): Maximum number of years for incarceration.
        Default to 40
    Methods:
    - generate_dates(): Generates simulated incarceration, work release, and release dates.
    
    Example usage:

    # Set the minimum and maximum number of years for incarceration
    min_incarceration_years = 2
    max_incarceration_years = 10

    # Create a PrisonerSimulator instance with the specified range
    prisoner_simulator = PrisonerSimulator(min_incarceration_years, max_incarceration_years)

    # Generate simulated incarceration, work release, and release dates
    incarceration_date, work_release_date, release_date = prisoner_simulator.generate_dates()

    # Print the generated dates
    print(f"Incarceration Date: {incarceration_date}")
    print(f"Work Release Date: {work_release_date}")
    print(f"Release Date: {release_date}")
    """
    def __init__(self, rng: np.random.mtrand.RandomState = None, seed:int = None):
        self.seed = seed if seed is None else np.random.randint(0,np.iinfo(np.int32).max)
        self.rng = rng if rng is not None else np.random.mtrand.RandomState(seed=self.seed)

    def get_sample(self, min_incarceration_years=1,
                   max_incarceration_years=40)-> Tuple[str, str, str]:
        today = pd.Timestamp.today()
        incarceration_years = self.rng.randint(min_incarceration_years, max_incarceration_years)
        
        # Generate incarceration date
        incarceration_date = today - pd.DateOffset(years=incarceration_years)
        incarceration_date_str = incarceration_date.strftime('%Y%m%d')
        
        # Generate work release date (1 to 12 months before release)
        work_release_date = incarceration_date + pd.DateOffset(months=self.rng.randint(1, 36))
        work_release_date_str = work_release_date.strftime('%Y%m%d')
        
        # Generate release date (within the last 12 months)
        max_release_date = today - pd.DateOffset(months=1)
        release_date = pd.to_datetime(self.rng.uniform(work_release_date.value, max_release_date.value))
        release_date_str = release_date.strftime('%Y%m%d')
        
        return incarceration_date_str, work_release_date_str, release_date_str

# BlackList Record Generators
class SIR029RecGen(RecordGenerator):
    """Generates a record of the SIR029WeeklyIndividualQuestionable data record.
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
    """
    logging.debug("Initializing SIR029RecGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='fraud', debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.debug = debug
        
        # General
        self.min_date_request = pd.Timestamp(self.yml['min_date_requests']).floor(freq='S')
        self.max_date_request = pd.Timestamp(self.yml['max_date_requests']).floor(freq='S')
        self.tin_gen = IdSource(rng=self.rng, is_num=True, length=9)
        self.taxpayer_indiv_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        self.yml_ah = self.yml['AuthenticationHeader'][self.yml_key]
        self.harcoded = self.yml['hardcoded']
        
        # Initialization
        self.gen_ip4 = IPv4Address(rng=self.rng, join_char=':')
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
        # Fields also in MeF ReturnHeader - Initialization - Use MeF config (yml file)
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]
        self.src_file_ssn = self.yml['src_file_zips_ssn']
        self.social_gen = GenSSN(src_data=self.src_file_ssn,
                             rng=self.rng, return_state=False,
                             state_of_sample=None,
                             debug=self.debug,
                             return_as_int=True
         )
        self.social_gen.fit()
        self.active_time_factor:Dict = self.yml_ah['active_time_preparation_factor']
        
        # Financial Data
        self.yml_ft = self.yml['FinancialTransactions'][self.yml_key]
        self.p_bank_account_in_us = self.yml_ft['p_bank_account_in_us']
        self.bank_info_gen = GenBankInfo(rng=self.rng,
                                    p_us=self.p_bank_account_in_us,
                                    seed=self.seed,
                                    return_is_intl=True
                                    )
        self.efin_gen = IdSource(rng=self.rng, is_num=True, length=6)
        self.ein_gen = EinGen(rng=self.rng,return_int=True)
        self.ptin_gen = PtinGen(rng=self.rng)
    
   
    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        primary_tin = self.tin_gen.get_sample()
        secondary_tin = self.tin_gen.get_sample()
        taxperiod = np.nan	
        prim_taxpayer = self.taxpayer_indiv_data_gen.get_record()
        sec_taxpayer = self.taxpayer_indiv_data_gen.get_record()
        name_line1 = prim_taxpayer.compositename
        name_control = prim_taxpayer.lastname[0:4]
        mail_address = prim_taxpayer.streetno + " " + prim_taxpayer.streetname
        city = prim_taxpayer.city
        State = self.harcoded['state']
        zipcode = prim_taxpayer.zipcode
        bal_due_amt_comp = round(gen_money(rng=self.rng))
        [routing_trans_num, undesirable_bank_acc, _ ] = self.bank_info_gen.get_sample()	
        scored_date = np.nan
        ip_address = self.gen_ip4.get_sample()
        efin = self.rng.choice([np.nan, self.efin_gen.get_sample()], p=[0.25, 0.75])
        agi_comp = np.nan
        device_id_submission = np.nan
        device_id_creation = np.nan
        email_address = prim_taxpayer.email
        email_address_add = self.rng.choice([np.nan,sec_taxpayer.email], p=[0.5, 0.5])
        ip_address_creation = np.nan
        
        # preparation_time
        TaxYr = self.rng.randint(low=self.min_date_request.year, high=self.max_date_request.year)
        tax_sub_end = dt.datetime(year=TaxYr+1, month=12, day=31).date()
        fi_prim_DataSigned = random_datetimes(
            start= pd.to_datetime(str(TaxYr+1) + '-02-01'),
            end=pd.to_datetime(str(TaxYr+1)+'-4-30'), 
            out_format='datetime', 
            rng=self.rng, n=1
            ).date()
        submission_timeline = self.gen_submission_timeline.get_sample(
            start=pd.Timestamp(fi_prim_DataSigned),end=pd.Timestamp(tax_sub_end))
        td_TotalPreparationSubmissionTs = MefDataGen.convert_to_min(
            submission_timeline['elapse time of submission']
        )
        preparation_time = str(int(round(
            (self.rng.uniform(**self.active_time_factor) * td_TotalPreparationSubmissionTs),0)
        ))

        # Bank Product:
        # 0 - Did not select Bank Product Option
        # 1 - Selected Debit Card Option
        # 2 - Selected Direct Deposit to the Bank
        # 3 - Requested a Check
        bank_product = self.rng.choice([0, 1, 2, 3], p=[0.1, 0.2, 0.4, 0.3])
        [routing_trans_num_ult, undesirable_bank_acc_ult, _ ] = self.bank_info_gen.get_sample()	
        cellphone =  int(prim_taxpayer.phoneno) if prim_taxpayer.phoneno is not None else np.nan 
        cellphone = str(cellphone).split('.')[0] if cellphone is not np.nan else cellphone
        
        # Preparer
        p_preparer = 0.6
        rand_prep = self.rng.rand()
        if rand_prep < p_preparer:
            preparer = self.taxpayer_indiv_data_gen.get_record()
            preparer_ssn_ptin = self.rng.choice([self.social_gen.get_sample(), self.ptin_gen.get_sample()], p=[0.5, 0.5])
            preparer_ein = self.rng.choice([np.nan, self.ein_gen.get_sample()], p=[0.5, 0.5])
            preparer_phone = int(preparer.phoneno) if preparer.phoneno is not None else np.nan
        else:
            preparer_ssn_ptin = preparer_ein = preparer_phone = np.nan
        
        rec = Record(datatype=SIR029WeeklyIndividualQuestionable, 
                    corruptible=SIR029WeeklyIndividualQuestionableCorruptible,
                    lenth_changable=SIR029WeeklyIndividualQuestionableLengthChangable,autopop={},
                        rng=self.rng,
                        primary_tin=primary_tin,
                        name_control=name_control,
                        taxperiod=taxperiod,
                        secondary_tin=secondary_tin,
                        name_line1=name_line1,
                        mail_address=mail_address,
                        city=city,
                        State=State,
                        zipcode=zipcode,
                        bal_due_amt_comp=bal_due_amt_comp,
                        routing_trans_num=routing_trans_num,
                        undesirable_bank_acc=undesirable_bank_acc,
                        preparer_ssn_ptin=preparer_ssn_ptin,
                        preparer_ein=preparer_ein,
                        preparer_phone=preparer_phone,
                        scored_date=scored_date,
                        ip_address=ip_address,
                        efin=efin,
                        agi_comp=agi_comp,
                        device_id_submission=device_id_submission,
                        device_id_creation=device_id_creation,
                        email_address=email_address,
                        email_address_add=email_address_add,
                        ip_address_creation=ip_address_creation,
                        preparation_time=preparation_time,
                        bank_product=bank_product,
                        routing_trans_num_ult=routing_trans_num_ult,
                        undesirable_bank_acc_ult=undesirable_bank_acc_ult,
                        cellphone=cellphone
                    )
        return rec
    
class SIR024RecGen(RecordGenerator):
    """Generates a record of the SIR024PriorYearIndividualConfirmed data record.
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
    """
    logging.debug("Initializing SIR024RecGen record generator object")
    def __init__(self,config:Dict,rng=None,seed=None,config_key='fraud', debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.debug = debug
        
        # General
        self.min_date_request = pd.Timestamp(self.yml['min_date_requests']).floor(freq='S')
        self.max_date_request = pd.Timestamp(self.yml['max_date_requests']).floor(freq='S')
        self.tin_gen = IdSource(rng=self.rng, is_num=True, length=9)
        self.taxpayer_indiv_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        self.yml_ah = self.yml['AuthenticationHeader'][self.yml_key]
        
        # Initialization
        self.gen_ip4 = IPv4Address(rng=self.rng, join_char=':')
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
        # Fields also in MeF ReturnHeader - Initialization - Use MeF config (yml file)
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]
        self.src_file_ssn = self.yml['src_file_zips_ssn']
        self.social_gen = GenSSN(src_data=self.src_file_ssn,
                             rng=self.rng, return_state=False,  
                             state_of_sample = None,
                             debug=self.debug,
                             return_as_int=True
         )
        self.social_gen.fit()
        self.hardcoded = self.yml['hardcoded']
        
        # Financial Data
        self.yml_ft = self.yml['FinancialTransactions'][self.yml_key]
        self.p_bank_account_in_us = self.yml_ft['p_bank_account_in_us']
        self.bank_info_gen = GenBankInfo(rng=self.rng,
                                    p_us=self.p_bank_account_in_us,
                                    seed=self.seed,
                                    return_is_intl=True
                                    )
        self.efin_gen = IdSource(rng=self.rng, is_num=True, length=6)
        self.ein_gen = EinGen(rng=self.rng, return_int=True)
    
    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        prim_taxpayer = self.taxpayer_indiv_data_gen.get_record()
        primary_ssn = self.social_gen.get_sample()
        secondary_ssn = self.social_gen.get_sample()

        name_line = prim_taxpayer.compositename
        address = prim_taxpayer.streetno + " " + prim_taxpayer.streetname
        city = prim_taxpayer.city
        State = self.hardcoded['state']
        zipcode = prim_taxpayer.zipcode
        taxperiod = np.nan	
        refund_amt = round(gen_money(rng=self.rng))
        efin = self.rng.choice([np.nan, self.efin_gen.get_sample()], p=[0.25, 0.75])
        preparer_tin = self.rng.choice([np.nan, self.social_gen.get_sample()], p=[0.5, 0.5])
        [routing_trans_num, undesirable_bank_acc, _ ] = self.bank_info_gen.get_sample()
        load_date = np.nan
        ip_address = self.gen_ip4.get_sample()
        email_address = prim_taxpayer.email

        rec = Record(datatype=SIR024PriorYearIndividualConfirmed, 
                    corruptible=SIR024PriorYearIndividualConfirmedCorruptible,
                    lenth_changable=SIR024PriorYearIndividualConfirmedLengthChangable,autopop={},
                        rng=self.rng,
                        primary_ssn=primary_ssn,
                        secondary_ssn=secondary_ssn,
                        name_line=name_line,
                        address=address,
                        city=city,
                        State=State,
                        zipcode=zipcode,
                        taxperiod=taxperiod,
                        refund_amt=refund_amt,
                        efin=efin,
                        preparer_tin=preparer_tin,
                        routing_trans_num=routing_trans_num,
                        undesirable_bank_acc=undesirable_bank_acc,
                        load_date=load_date,
                        ip_address=ip_address,
                        email_address=email_address
                    )
        return rec
    
class SIR075RecGen(RecordGenerator):
    """Generates a record of the SIR-075-Preparer TIN (PTIN) data record.
    
    Args:
    config:Dict. Yaml file which contains paths to source files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
    """
    logging.debug("Initializing SIR075RecGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='fraud', debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.debug = debug
        
        # General
        self.min_date_request = pd.Timestamp(self.yml['min_date_requests']).floor(freq='S')
        self.max_date_request = pd.Timestamp(self.yml['max_date_requests']).floor(freq='S')
        self.tin_gen = IdSource(rng=self.rng, is_num=True, length=9)
        self.taxpayer_indiv_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        self.yml_ah = self.yml['AuthenticationHeader'][self.yml_key]
        self.harcoded = self.yml['hardcoded']
        
        # Initialization
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
        # Fields also in MeF ReturnHeader - Initialization - Use MeF config (yml file)
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]
        self.src_file_ssn = self.yml['src_file_zips_ssn']
        self.social_gen = GenSSN(src_data=self.src_file_ssn,
                             rng=self.rng, return_state=False,  
                             state_of_sample = None,
                             debug=self.debug,
                             return_as_int=True
         )
        self.social_gen.fit()
        self.active_time_factor:Dict = self.yml_ah['active_time_preparation_factor']
            
        self.efin_gen = IdSource(rng=self.rng, is_num=True, length=6)
        self.ein_gen = EinGen(rng=self.rng,return_int=True)
        self.ptin_gen = PtinGen(rng=self.rng)    
  
    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        preparer = self.taxpayer_indiv_data_gen.get_record()
        ssn = self.social_gen.get_sample()
        ptin = self.ptin_gen.get_sample()                
        ptin_issue_date = np.nan   
        ptin_status_list = ['Active', 'Suspended-IRS', 'Revoked', 
                                'Decease','Expired', 'Vol. Inactive', 
                                'Withdrawn', 'Expired-DNRW',
                                'Perm Expire', 'Perm Retire']
        ptin_status_prob = [
                            0.70, 0.05, 0.01, 
                            0.02, 0.10, 0.03, 
                            0.02, 0.05,
                            0.01, 0.01
                           ]

        ptin_status = self.rng.choice(ptin_status_list, p = ptin_status_prob)
        
        # Active = PTIN Approved. Test passed or not required. 
        # Suspended-IRS = PTIN suspended by IRS. Period of suspension may/may
        #      not be specifically identified. 
        # Revoked = PTIN permanently revoked. Deceased = PTIN holder is deceased.
        # Expired = Tax preparer has been issued a PTIN and fails to complete the
        #      renewal process for the following calendar year by the start of the new year
        # Vol. Inactive = Tax preparer has been issued a PTIN and subsequently
        #      completes the voluntarily inactivation process. (NOTE: This process
        #      allows a preparer to skip a year of practice without their PTIN expiring")
        # Withdrawn = Individual has been issued a PTIN and informs the IRS that
        #      they obtained their PTIN in error.)
        # Expired-DNRW = Never renewed for previous year and does not have any open
        #      renewal for current year.
        # Perm Expire = PTIN is in expired state for more than three years without any activity.
        # Perm Retire - PTIN is in voluntary inactive state for more than three years
        #      without any activity.
        
        last_name = preparer.lastname
        first_name = preparer.firstname
        middle_name = preparer.middlename
        suffix = np.nan
        birth_date = preparer.birthday.strftime("%Y%m%d")
        email_addr = preparer.email
        perm_addr_line1 = str(preparer.streetno) + " " + preparer.streetname
        # Apartment number
        aptno = preparer.aptno
        apto = "" if (aptno is None) or (
                    isinstance(aptno, float) and np.isnan(aptno)) or (aptno <= 0) else aptno
        
        perm_addr_line2 = "" if apto == "" else (
             self.rng.choice(["Apt. ","Suite ", ""], p=[0.35, 0.6, 0.05]) + str(aptno))
            
        perm_addr_line3 = np.nan
        perm_city = preparer.city
        perm_state = self.harcoded['state']
        perm_zip = preparer.zipcode
        country = self.harcoded['country']
        perm_country = np.nan if country == "USA" else country
        phone = int(preparer.phoneno) if preparer.phoneno is not None  else np.nan
        phone = str(phone).split('.')[0] if phone is not np.nan else phone
        ext = np.nan
        efin = self.efin_gen.get_sample()
        
        p_is_business = 0.6
        rand_is_bus = self.rng.rand()
        if rand_is_bus < p_is_business:
            # Case when preparer is a business
            office_own_ind = "Y"     
            preparer_bus = self.taxpayer_indiv_data_gen.get_record()
            ein = self.ein_gen.get_sample()
            bus_addr_line1 = preparer_bus.streetno
            bus_addr_line2 = preparer_bus.aptno
            bus_addr_line3 = np.nan
            bus_city = preparer_bus.city
            bus_state = self.harcoded['state']
            bus_zip = preparer_bus.zipcode
            bus_country = self.harcoded['country']
            bus_name = np.nan
            bus_phone = int(preparer_bus.phoneno) if preparer_bus.phoneno is not None else preparer_bus.phoneno
            bus_phone = str(bus_phone).split('.')[0] if bus_phone is not np.nan else bus_phone
            bus_ext = np.nan
        else:
            office_own_ind = self.rng.choice(["", "N"], p=[0.5, 0.5])
            bus_phone = bus_ext = ein = bus_addr_line1 = bus_addr_line2 = bus_addr_line3 = \
                bus_city = bus_state = bus_zip  = bus_country = bus_name = np.nan
                
        # H: hybrid means person reports no now, but yes in the past
        # Y = Yes   N = No, or H. 
        # Y = I have been convicted of a felony in the past 10 years. 
        # H = hybrid: The preparer responded they have not been convicted of a felony in the most recently approved registration, 
        # but in an application within the past 10 yrs., the preparer reported a past felony conviction. May be blank.
        self_rep_felony_ind = self.rng.choice(["", "Y", "N", "H"], p=[0.10, 0.10, 0.75, 0.05]) 
        
        # pers_tax_compliance: File appears to have an error in the long description. Based on the possible values provided.
        pers_tax_compl_ind = self.rng.choice(["Y","N",""], p=[0.45, 0.5, 0.05])
        professions = np.nan
        paid_prep_1040_ind = self.rng.choice(["", "Y", "N"], p=[0.1, 0.45, 0.45])
        afsp_tcc_exmp_ind = self.rng.choice(["","Y", "N"], p=[0.1, 0.4, 0.5]) # Preparer except from the afsp exam?
        prep_dir_opt_out_ind = np.nan  #This field is not in the original IRS file but in RPE only
        # O/A/Blank(O = Open & A = Approved) 
        afsp_consent_elect_ind = self.rng.choice(["O", "A", ""], p=[0.45, 0.45, 0.1])
        for_future_use1 = np.nan
        for_future_use2 = np.nan
        afsp_course_exmp_ind = self.rng.choice(["","Y"], p=[0.5, 0.5]) # Preparer except from the afsp exam?
        afsp_eff_date = np.nan
        aftr_complete_date = np.nan
        irs_tax_compl_ind = self.rng.choice(["","P","F"],p=[0.10, 0.70, 0.20])
        reserved = np.nan
        afsp_ineligible_ind = self.rng.choice(["", "Y", "N"], p=[0.2, 0.2, 0.6])
        ptin_renewal_date = np.nan 

        rec = Record(datatype=SIR075PreparerTIN, 
                    corruptible=SIR075PreparerTINCorruptible,
                    lenth_changable=SIR075PreparerTINLengthChangable,autopop={},
                        rng=self.rng,
                        ssn=ssn,
                        ptin=ptin,
                        ptin_issue_date=ptin_issue_date,
                        ptin_status=ptin_status,
                        last_name=last_name,
                        first_name=first_name,
                        middle_name=middle_name,
                        suffix=suffix,
                        birth_date=birth_date,
                        email_addr=email_addr,
                        perm_addr_line1=perm_addr_line1,
                        perm_addr_line2=perm_addr_line2,
                        perm_addr_line3=perm_addr_line3,
                        perm_city=perm_city,
                        perm_state=perm_state,
                        perm_zip=perm_zip,
                        perm_country=perm_country,
                        phone=phone,
                        ext=ext,
                        bus_phone=bus_phone,
                        bus_ext=bus_ext,
                        ein=ein,
                        efin=efin,
                        office_own_ind=office_own_ind,
                        bus_addr_line1=bus_addr_line1,
                        bus_addr_line2=bus_addr_line2,
                        bus_addr_line3=bus_addr_line3,
                        bus_city=bus_city,
                        bus_state=bus_state,
                        bus_zip=bus_zip,
                        bus_country=bus_country,
                        bus_name=bus_name,
                        self_rep_felony_ind=self_rep_felony_ind,
                        pers_tax_compl_ind=pers_tax_compl_ind,
                        professions=professions,
                        paid_prep_1040_ind=paid_prep_1040_ind,
                        afsp_tcc_exmp_ind=afsp_tcc_exmp_ind,
                        afsp_consent_elect_ind=afsp_consent_elect_ind,
                        prep_dir_opt_out_ind=prep_dir_opt_out_ind,
                        for_future_use1=for_future_use1,
                        for_future_use2=for_future_use2,
                        afsp_course_exmp_ind=afsp_course_exmp_ind,
                        afsp_eff_date=afsp_eff_date,
                        aftr_complete_date=aftr_complete_date,
                        irs_tax_compl_ind=irs_tax_compl_ind,
                        reserved=reserved,
                        afsp_ineligible_ind=afsp_ineligible_ind,
                        ptin_renewal_date=ptin_renewal_date
                    )
        return rec
    
    
class SIR027RecGen(RecordGenerator):
    """Generates a record of the SIR-027 ITPI ID Theft Indicator data record.
    
    Args:
    config:Dict. Yaml file which contains paths to source files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
        
    Key Fields:
        idtheft_protection_inda: (ID Theft Protection Indicator A) This field idtheft_protection_inda  will be populated with the number “1” or "0" in one or two positions
            - first: the taxpayer is at potential risk for identity theft (e.g. has reported an incident that could lead to identity theft) or 
            - second: this taxpayer has experienced identity theft which impacted a tax record or tax records. 
            The identity theft indicator is not associated with a tax year it is associated with the individual.
    """
    logging.debug("Initializing SIR027RecGen record generator object")
    
    def __init__(self,config,rng=None,seed=None,config_key='fraud', debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.debug = debug
        
        # General
        self.tin_gen = IdSource(rng=self.rng, is_num=True, length=9)
        self.taxpayer_indiv_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        self.yml_ah = self.yml['AuthenticationHeader'][self.yml_key]
        self.harcoded = self.yml['hardcoded']
        
        # Initialization
        # Fields also in MeF ReturnHeader - Initialization - Use MeF config (yml file)
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]  #NEEDED???
    
   
    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        person = self.taxpayer_indiv_data_gen.get_record()
        extract_Identifier = "IT"
        primary_tin_validity_digit = self.rng.choice(["0", "1"], p=[0.75, 0.25]) # 0:valid ssn or itin, 1: invalid
        primary_tin = self.tin_gen.get_sample()
        taxpayer_name_line = person.compositename
        name_control = person.lastname[:4]
        reserved1 = np.nan
        address = person.streetno + person.streetname
        city = person.city
        zipcode = person.zipcode
        State = self.harcoded["state"] 
        charctercnt_to_lastname = person.compositename.find(person.lastname)
        charactercnt_in_lastname = len(person.lastname)
        reserved2 = np.nan
        
        # ID Theft Protection Indicator A will be populated with the number “1” or "0" in one or two positions
        # first: the taxpayer is at potential risk for identity theft (e.g. has reported an incident that could lead to identity theft) or 
        # second: this taxpayer has experienced identity theft which impacted a tax record or tax records. 
        # The identity theft indicator is not associated with a tax year it is associated with the individual.
        conditional_probabilities = {
            0: {0: 0.9, 1: 0.1},  # If first digit is 0
            1: {0: 0.3, 1: 0.7}   # If first digit is 1
        }
        first_digit = self.rng.choice([0, 1])

        # Generate the second digit based on the conditional probabilities
        second_digit = self.rng.choice([0, 1], p=[conditional_probabilities[first_digit][0], conditional_probabilities[first_digit][1]])

        # Combine the digits to form the field value
        idtheft_protection_inda = str(first_digit) + str(second_digit)
        reserved3 = np.nan
        
        # ID Theft Protection Indicator B give more details regarding the ID theft. 
        # They are also 8 individual digits putting next to each other.
        #    1.	Employment related identity theft - Return/W-2 TIN mismatch
        #    2.	Locked Account, TP deceased/no filing requirements
        #    3.	Reserved Field will be zero filled (0)
        #    4.	ID Theft claim – not yet verified
        #    5.	ID Theft: IRS Identified, tax administration impact
        #    6.	ID Theft: Data Loss
        #    7.	ID Theft: Taxpayer Self-Identified, no tax administration impact
        #    8.	ID Theft: Taxpayer Self-Identified, tax administration impact
        b1 = self.rng.choice(['0', '1'], p=[0.5, 0.5])
        b2 = self.rng.choice(['0', '1'], p=[0.5, 0.5])
        b3 = '0'
        b4 = self.rng.choice(['0', '1'], p=[0.75, 0.25])
        b5 = self.rng.choice(['0', '1'], p=[0.25, 0.75])
        b6 = self.rng.choice(['0', '1'], p=[0.25, 0.75])
        b7 = self.rng.choice(['0', '1'], p=[0.25, 0.75])
        b8 = self.rng.choice(['0', '1'], p=[0.5, 0.5])
        # Non-contradiction conditions
        if b8=='1':
            b7='0'
            
        if (b7 == '1') or (b8 == '1') or (b5 == '1'):
            b4 = '0'
        
        idtheft_protection_indb = b1 + b2 + b3 + b4 + b5 + b6 + b7 + b8
        reserved4 = np.nan


        rec = Record(datatype=SIR027ITPIIDTheftIndicator, 
                        corruptible=SIR027ITPIIDTheftIndicatorCorruptible,
                        lenth_changable=SIR027ITPIIDTheftIndicatorLengthChangable,autopop={},
                        rng=self.rng,
                        extract_Identifier=extract_Identifier,
                        primary_tin_validity_digit=primary_tin_validity_digit,
                        primary_tin=primary_tin,
                        taxpayer_name_line=taxpayer_name_line,
                        name_control=name_control,
                        reserved1=reserved1,
                        address=address,
                        city=city,
                        zipcode=zipcode,
                        State=State,
                        charctercnt_to_lastname=charctercnt_to_lastname,
                        charactercnt_in_lastname=charactercnt_in_lastname,
                        reserved2=reserved2,
                        idtheft_protection_inda=idtheft_protection_inda,
                        reserved3=reserved3,
                        idtheft_protection_indb=idtheft_protection_indb,
                        reserved4=reserved4
                    )
        return rec

class SIR023RecGen(RecordGenerator):
    """Generates a record of the SIR023CurrentYearIndividualQuestionable data record.
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
    """
    logging.debug("Initializing SIR023RecGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='fraud', debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.debug = debug
        
        # General
        self.min_date_request = pd.Timestamp(self.yml['min_date_requests']).floor(freq='S')
        self.max_date_request = pd.Timestamp(self.yml['max_date_requests']).floor(freq='S')
        self.tin_gen = IdSource(rng=self.rng, is_num=True, length=9)
        self.taxpayer_indiv_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        self.yml_ah = self.yml['AuthenticationHeader'][self.yml_key]
        self.harcoded = self.yml['hardcoded']
        
        # Initialization
        self.gen_ip4 = IPv4Address(rng=self.rng, join_char=':')
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
        # Fields also in MeF ReturnHeader - Initialization - Use MeF config (yml file)
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]
        self.src_file_ssn = self.yml['src_file_zips_ssn']
        self.social_gen = GenSSN(src_data=self.src_file_ssn,
                             rng=self.rng, return_state=False,  
                             state_of_sample = None,
                             debug=self.debug,
                             return_as_int=True
         )
        self.social_gen.fit()
        self.active_time_factor:Dict = self.yml_ah['active_time_preparation_factor']
        
        # Financial Data
        self.yml_ft = self.yml['FinancialTransactions'][self.yml_key]
        self.p_bank_account_in_us = self.yml_ft['p_bank_account_in_us']
        self.bank_info_gen = GenBankInfo(rng=self.rng,
                                    p_us=self.p_bank_account_in_us,
                                    seed=self.seed,
                                    return_is_intl=True
                                    )
        self.efin_gen = IdSource(rng=self.rng, is_num=True, length=6)
        self.ein_gen = EinGen(rng=self.rng,return_int=True)
        self.ptin_gen = PtinGen(rng=self.rng)
    
   
    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        prim_taxpayer = self.taxpayer_indiv_data_gen.get_record()
        
        primary_tin = self.tin_gen.get_sample()
        name_control = prim_taxpayer.lastname[0:4]
        tax_period = self.rng.randint(self.min_date_request.year, self.max_date_request.year)
        secondary_tin = self.tin_gen.get_sample()
        name_line1 = prim_taxpayer.compositename
        mail_address = prim_taxpayer.streetno + " " + prim_taxpayer.streetname
        city = prim_taxpayer.city
        state = self.harcoded['state']
        zip_code = prim_taxpayer.zipcode
        
        bal_due_amt_comp = round(gen_money(rng=self.rng))
        [bank_account_key, bank_account_num, _ ] = self.bank_info_gen.get_sample()	

        # Preparer
        p_preparer = 0.6
        rand_prep = self.rng.rand()
        if rand_prep < p_preparer:
            preparer = self.taxpayer_indiv_data_gen.get_record()
            preparer_ssn_ptin = self.rng.choice([self.social_gen.get_sample(), self.ptin_gen.get_sample()], p=[0.5, 0.5])
            preparer_ein = self.rng.choice([np.nan, self.ein_gen.get_sample()], p=[0.5, 0.5])
            preparer_phone = int(preparer.phoneno) if preparer.phoneno is not None else np.nan
        else:
            preparer_ssn_ptin = preparer_ein = preparer_phone = np.nan
            
        scored_date = np.nan
        ip_address = self.gen_ip4.get_sample()
        efin = self.rng.choice([np.nan, self.efin_gen.get_sample()], p=[0.25, 0.75])
        agi_comp = np.nan
        
        rec = Record(
                datatype=SIR023CurrentYearIndividualQuestionable, 
                corruptible=SIR023CurrentYearIndividualQuestionableCorruptible,
                lenth_changable=SIR023CurrentYearIndividualQuestionableLengthChangable,autopop={},
                primary_tin=primary_tin,
                name_control=name_control,
                tax_period=tax_period,
                secondary_tin=secondary_tin,
                name_line_1=name_line1,
                mail_address=mail_address,
                city=city,
                state=state,
                zip_code=zip_code,
                bal_due_amt_comp=bal_due_amt_comp,
                bank_account_key=bank_account_key,
                bank_account_num=bank_account_num,
                preparer_ssn_ptin=preparer_ssn_ptin,
                preparer_ein=preparer_ein,
                preparer_phone=preparer_phone,
                scored_date=scored_date,
                ip_address=ip_address,
                efin=efin,
                agi_comp=agi_comp
        )
        return rec
    
class SIR025RecGen(RecordGenerator):
    """Generates a record of the SIR-025 PITRF700 Incident file data record.
    Data names and types corresponds to RPE.
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
    """
    logging.debug("Initializing SIR025RecGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='fraud', debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.debug = debug
        
        # General
        self.min_date_request = pd.Timestamp(self.yml['min_date_requests'])
        self.max_date_request = pd.Timestamp(self.yml['max_date_requests'])
        self.tin_gen = IdSource(rng=self.rng, is_num=True, length=9)
        self.taxpayer_indiv_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        self.yml_ah = self.yml['AuthenticationHeader'][self.yml_key]
        self.harcoded = self.yml['hardcoded']
        
        # Initialization
        self.gen_ip4 = IPv4Address(rng=self.rng, join_char=':')
        
        # Fields also in MeF ReturnHeader - Initialization - Use MeF config (yml file)
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]
        self.src_file_ssn = self.yml['src_file_zips_ssn']
        self.social_gen = GenSSN(src_data=self.src_file_ssn,
                             rng=self.rng, return_state=False,  
                             state_of_sample=None,
                             debug=self.debug,
                             return_as_int=True
         )
        self.social_gen.fit()
        self.active_time_factor:Dict = self.yml_ah['active_time_preparation_factor']
        
        # Financial Data
        self.efin_gen = IdSource(rng=self.rng, is_num=True, length=6)
        self.ein_gen = EinGen(rng=self.rng,return_int=True)
        self.ptin_gen = PtinGen(rng=self.rng)
    
    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        prim_taxpayer = self.taxpayer_indiv_data_gen.get_record()
        
        primary_tin = self.tin_gen.get_sample()
        name_control = prim_taxpayer.lastname[0:4]
        tax_period_year = self.rng.randint(self.min_date_request.year, self.max_date_request.year)
        secondary_tin = self.tin_gen.get_sample()
        name_line1 = prim_taxpayer.compositename
        mail_address = prim_taxpayer.streetno + " " + prim_taxpayer.streetname
        city = prim_taxpayer.city
        state = self.harcoded['state']
        zipcode = prim_taxpayer.zipcode
        
        rec = Record(
                datatype=SIR025PITRF700Incidentfile, 
                corruptible=SIR025PITRF700IncidentfileCorruptible,
                lenth_changable=SIR025PITRF700IncidentfileLengthChangable,autopop={},
                primary_tin=primary_tin,
                name_control=name_control,
                tax_period_year=tax_period_year,
                secondary_tin=secondary_tin,
                name_line1=name_line1,
                mail_address=mail_address,
                city=city,
                state=state,
                zipcode=zipcode
        )
        return rec
    
class SIR114RecGen(RecordGenerator):
    """Generates a record of the SIR-114(Federal Prisoner Files) data record.
    Data names and types corresponds to RPE.
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
    """
    logging.debug("Initializing SIR114RecGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='fraud', debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.debug = debug
        self.ofender_number_gen = IdSource(rng=self.rng, is_alpha=True, length=8)
        self.institution_code_gen = IdSource(rng=self.rng, is_alpha=True, length=5)
        self.prisoner_simulator_gen = PrisonerSimulator(rng=self.rng)
        
        # General
        self.min_date_request = pd.Timestamp(self.yml['min_date_requests'])
        self.max_date_request = pd.Timestamp(self.yml['max_date_requests'])
        self.tin_gen = IdSource(rng=self.rng, is_num=True, length=9)
        self.taxpayer_indiv_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        self.yml_ah = self.yml['AuthenticationHeader'][self.yml_key]
        self.harcoded = self.yml['hardcoded']
        
        # Fields also in MeF ReturnHeader - Initialization - Use MeF config (yml file)
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]
        self.src_file_ssn = self.yml['src_file_zips_ssn']
        self.social_gen = GenSSN(src_data=self.src_file_ssn,
                             rng=self.rng, return_state=False,
                             state_of_sample=None,
                             debug=self.debug,
                             return_as_int=True
         )
        self.social_gen.fit()
        
        # Financial Data
        self.efin_gen = IdSource(rng=self.rng, is_num=True, length=6)
        self.ein_gen = EinGen(rng=self.rng,return_int=True)
        self.ptin_gen = PtinGen(rng=self.rng)
    
    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        prisoner = self.taxpayer_indiv_data_gen.get_record()
        first_name = prisoner.firstname
        middle_name = prisoner.middlename
        last_name = prisoner.lastname
        date_of_birth = prisoner.birthday.strftime("%Y%m%d")
        ssn = self.social_gen.get_sample()
        
        # Verified - 1 Alpha char. X:verified by SSA, Blank not verified, D: deceased 
        verified_ssn = self.rng.choice(["X","","D"], p=[0.90, 0.01 ,0.09])
        
        offender_number = self.ofender_number_gen.get_sample()

        # Create a PrisonerSimulator instance with a custom max_incarceration_years value
        max_incarceration_years = min(1, calculate_age(prisoner.birthday) - 18)
        self.prisoner_simulator_gen.max_incarceration_years = max_incarceration_years

        # Generate simulated incarceration, work release, and release dates
        incarceration_date, work_release_date, release_date = self.prisoner_simulator_gen.get_sample()
        institution_code = self.institution_code_gen.get_sample()
        
        # ReleaseDateCode - 1 Alpha/Numeric char.character:
        #    Blank – No data available. 0 - Data is unavailable. 
        #    9 - Life/Death sentence. 8 - Escaped
        release_date_code = self.rng.choice(["","0","9","8"], p=[0.75, 0.19, 0.05, 0.01])
        if (release_date_code == "0") or (release_date_code == "8"):
            pass # Will keep the release_date

        if release_date_code == "9":
            release_date = "99999999"

        # @TODO DATE OF DEATH -- consider as part of code ""

        rec = Record(
                datatype=SIR114FederalPrisonerFiles, 
                corruptible=SIR114FederalPrisonerFilesCorruptible,
                lenth_changable=SIR114FederalPrisonerFilesLengthChangable,autopop={},
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                ssn=ssn,
                verified_ssn=verified_ssn, 
                offender_number=offender_number,
                incarceration_date=incarceration_date,
                work_release_date=work_release_date,
                release_date=release_date,
                institution_code=institution_code,
                release_date_code=release_date_code
        )
        
        return rec
    
class PITRF800RecGen():
    """Generates a record of the 
    PITRF800 ISAC Alerts (SIR-117) & PITRF200 Suspect Email Domains (SIR-118)
    data record.
    Data names and types corresponds to RSI, since RPE were not available in the source files.
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
    """
    logging.debug("Initializing PITRF800RecGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='fraud',debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.debug = debug
        
        # Initialization of classes
        self.tin_gen = IdSource(rng=self.rng, is_num=True, length=9)
        self.taxpayer_indiv_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        self.gen_ip4 = IPv4Address(rng=self.rng, join_char='.')
        self.efin_gen = IdSource(rng=self.rng, is_num=True, length=6)
        self.device_gen = DeviceIdGen()

    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        device_id = self.device_gen.get_sample()
        ip_address = self.gen_ip4.get_sample()
        
        taxpayer = self.taxpayer_indiv_data_gen.get_record()
        email = taxpayer.email
        
        payer_tin = self.tin_gen.get_sample()
        efin = self.rng.choice([np.nan, self.efin_gen.get_sample()], p=[0.05, 0.95])
        
        rec = Record(
                datatype=SIR117PITRF800SIR118PITRF200ISACAlertsAndSuspectEmailDomains, 
                corruptible=SIR117PITRF800SIR118PITRF200ISACAlertsAndSuspectEmailDomainsCorruptible,
                lenth_changable=SIR117PITRF800SIR118PITRF200ISACAlertsAndSuspectEmailDomainsLengthChangable,autopop={},
                device_id=device_id,
                ip_address=ip_address,
                email=email,
                payer_tin=payer_tin,
                efin=efin
        )
        return rec
 
class PITRF500RecGen():
    """Generates a record of the PITRF500 EFIN (SIR-116) data record, with .
    Data names and types corresponds to RSI, since RPE were not available in the source files.
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
        
    Overview:
        "The PITRF500 EFIN interface is responsible for loading EFIN
        table weekly.  
        Providers need an Electronic Filing Identification Number
        (EFIN) to electronically file tax returns. 
        IRS assigns an EFIN to identify firms that have completed the
        IRS e-file application to become an authorized IRS e-file provider. 
        An EFIN is compromised when it is used by an unauthorized user.
        If an EFIN is compromised, IRS will inactivate the EFIN, issue
        a new EFIN and notify the firm in writing.
        IRS e-file participant extracts one file with all six provider options per record.
        A record for each active and inactive EFIN where at least one provider option is:
            ERO, 
            Transmitter, 
            Online Filer, 
            Software Developer, 
            ISP or 
            Large Taxpayer 
        and the provider status of at least one provider option listed above is not applied status."

    """
    logging.debug("Initializig PITRF500RecGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='fraud',debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.hardcoded = self.yml['hardcoded']
        self.debug = debug
        
        # Initialization of classes
        self.efin_gen = IdSource(rng=self.rng, is_num=True, length=6)
        self.etin_gen = EtinGen()
        self.ein_gen = EinGen()
        self.primary_contact_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )
        self.min_date_request = pd.Timestamp(self.yml['min_date_requests'])
        self.max_date_request = pd.Timestamp(self.yml['max_date_requests'])
        
        # Social security initialization
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]
        self.src_file_ssn = self.yml['src_file_zips_ssn']
        self.social_gen = GenSSN(src_data=self.src_file_ssn,
                             rng=self.rng, return_state=False,
                             state_of_sample=None,
                             debug=self.debug,
                             return_as_int=True
         )
        self.social_gen.fit()
        
    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan may not been implemented yet
        """
        efin_irs = self.rng.choice([np.nan, self.efin_gen.get_sample()], p=[0.05, 0.95])
        
        # V = Valid/Active, I = Inactive, D = Dropped
        efin_stat_cd_irs = self.rng.choice(['V','I','D'], p=[0.5, 0.3, 0.2])
        
        # etin_irs_i has 6 categories depending on the source, and only
        # some are populated.
        # Define the categories as a list
        categories = [1, 2, 3, 4, 5, 6, 7]

        # Choose a random number of categories (e.g., between 1 and 7)
        num_categories = self.rng.choice([1, 2, 3, 4, 5, 6, 7], p=[0.3, 0.3, 0.2, 0.1, 0.05, 0.04, 0.01])
        
        # Randomly select num_categories from the list of categories
        selected_categories = self.rng.choice(categories, size=num_categories, replace=False)

        # Create a dictionary to store the ETINs
        etin_irs_dict = {}
        
        # Status and dates of the statuses will also be populated here
        # 1 = Applied, 2 = Accepted, 3 = Rejected, 4 = Dropped, 
        # 5 = Testing, 6 = Non Compliance, 7 = Non-compliance (8453 only), 
        # 8 = Non-compliance (Field Monitoring only)), otherwise leave blank
        etin_status_dict = {}
        etin_effective_dates_dict = {}

        # Generate an ETIN for each selected category and store it in the dictionary
        for category in selected_categories:
            etin_irs_dict[category] = self.etin_gen.get_sample()
            etin_status_dict[category] = self.rng.choice(list(range(1,8)))
            etin_effective_dates_dict[category] = random_datetimes(
                start=self.min_date_request,
                end=self.max_date_request).strftime('%Y%m%d')

        # Create a list of ETIN variables, with null values for the ones not chosen
        etin_irs_list = [etin_irs_dict.get(category, "") for category in range(1, 8)]
        etin_status_list = [etin_status_dict.get(category, "") for category in range(1, 8)]
        etin_efftdt_list = [etin_effective_dates_dict.get(category, "") for category in range(1,8)]

        # Access the individual ETINs with proper column name
        [etin_irs, etin_irs2, etin_irs3, etin_irs4, etin_irs5, etin_irs6, etin_irs7] = etin_irs_list
        [ero_status, trmt_status, swdv_status, isp_status, olf_status, lgxt_status, _ ] = etin_status_list 
        [ero_effdt, trmt_effdt, swdv_effdt, isp_effdt, olf_effdt, lgxt_effdt, _ ] = etin_efftdt_list

        legal_name = np.nan
        tin_type_irs = self.rng.choice([0, 1], p=[0.5, 0.5])
        
        # tin_type 0:ssn 1:ein
        if tin_type_irs == 0:
            tin_irs = self.social_gen.get_sample()
        else:
            tin_irs = self.ein_gen.get_sample()
        
        prim_contact = self.primary_contact_gen.get_record()
        last_name = prim_contact.lastname
        first_name = prim_contact.firstname
        middle_name = prim_contact.middlename
        country_code = self.hardcoded['country']
        phone = prim_contact.phoneno
        email_addr = prim_contact.email
        address1 = prim_contact.streetno + " " + prim_contact.streetname
        
        # Apartment number
        aptno = prim_contact.aptno
        apto = "" if (aptno is None) or (
                    isinstance(aptno, float) and np.isnan(aptno)) or (aptno <= 0) else aptno
        
        address2 = "" if apto == "" else (
            self.rng.choice(["Apt. ","Suite ", ""], p=[0.6, 0.1, 0.3]) + str(aptno))
        address3 = np.nan
        
        city = prim_contact.city
        state = self.hardcoded['state']
        postal = prim_contact.zipcode
        country = self.hardcoded['country']
    
        rec = Record(
                datatype=PITRF500EfinSIR116, 
                corruptible=PITRF500EfinSIR116Corruptible,
                lenth_changable=PITRF500EfinSIR116LengthChangable,autopop={},
                efin_irs=efin_irs,
                efin_stat_cd_irs=efin_stat_cd_irs,
                etin_irs=etin_irs,
                etin_irs2=etin_irs2,
                etin_irs3=etin_irs3,
                etin_irs4=etin_irs4,
                etin_irs5=etin_irs5,
                etin_irs6=etin_irs6,
                etin_irs7=etin_irs7,
                legal_name=legal_name,
                ero_status=ero_status,
                ero_effdt=ero_effdt,
                trmt_status=trmt_status,
                trmt_effdt=trmt_effdt,
                swdv_status=swdv_status,
                swdv_effdt=swdv_effdt,
                isp_status=isp_status,
                isp_effdt=isp_effdt,
                olf_status=olf_status,
                olf_effdt=olf_effdt,
                lgxt_status=lgxt_status,
                lgxt_effdt=lgxt_effdt,
                tin_type_irs=tin_type_irs,
                tin_irs=tin_irs,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                country_code=country_code,
                phone=phone,
                email_addr=email_addr,
                address1=address1,
                address2=address2,
                address3=address3,
                city=city,
                state=state,
                postal=postal,
                country=country
        )
        return rec

class SIR073RecGen(RecordGenerator):
    """Generates a record of the SIR-073 ITIN by State Code data record.
    Data names and types corresponds to RSI, since RPE were not available in the source files.
    MVP version has several fields not completed, particularly related to
    foreign information.
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
        
    Overview:
        The ITIN By State Code and ITIN by TIN interface is responsible for
        loading the ITIN table weekly. 
        Individual Taxpayer Identification Numbers (ITIN) are issued by IRS
        for taxpayers who do not qualify for a Social Security Number, but
        who still need a nine-digit identification number used by the IRS to
        process a Form 1040 and other tax schedules.

        The information will be extracted from the IRS ITIN database which
        contains information captured from the Form W-7 application.
    """
    logging.debug("Initializing SIR073RecGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='fraud',debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.hardcoded = self.yml['hardcoded']
        self.debug = debug
        
        # Initialization of classes
        self.itin_gen = ItinGen()
        self.ein_gen = EinGen()
        self.alien_data_gen = RecordGenerator(
            config=self.yml, rng=self.rng, seed=self.seed, debug=self.debug
        )

    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        alien1 = self.alien_data_gen.get_record()
        alien2 = self.alien_data_gen.get_record()
        alien3 = self.alien_data_gen.get_record()

        itin = self.itin_gen.get_sample()
        mailing_state_province = np.nan
        history = np.nan #YYYYMMDD
        # 1 – Active Record, 2 – Inactive Record, 3 – Revoked Record 
        itin_status_id = self.rng.choice(["1", "2", "3"], p=[0.8, 0.1, 0.1])
        #CODE	Definition 
        # R11	Applicant/Deceased 
        # R14	Has been assigned multiple ITIN’s 
        # R15	Has been assigned a SSN 
        # R07	A U.S. citizen or has a U.S. Work Visa 
        # R26	Assigned ITIN is invalid
        choices = ["R11", "R14", "R15", "R07", "R26"]
        prob = [0.1, 0.2, 0.5, 0.1, 0.1]
        revoked_reason_code = self.rng.choice(choices, p=prob)
        
        # Reason for submitting W-7 
        # Form W-7 checkboxes “a” through “h.” 
        # a. Nonresident alien required to get ITIN to claim tax treaty benefit. 
        # b. Nonresident alien filing a US tax return. 
        # c. US resident alien filing a US tax return. 
        # d. Dependent of US citizen/resident alien. 
        # e. Spouse of US citizen/resident alien. 
        # f. Nonresident alien student, professor, or researcher filing a US tax return or claiming an exception. 
        # g. Dependent/spouse of a nonresident alien holding a US visa. 
        # h. Other.
        choices = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        application_reason = self.rng.choice(choices)
        
        citizen_alien_first_name = alien1.firstname
        citizen_alien_middle_name = alien1.middlename
        citizen_alien_last_name = alien1.lastname
        treaty_article_number = np.nan
        
        choices = [citizen_alien_first_name, alien2.firstname]
        prob = [0.8, 0.2]
        legal_first_name = self.rng.choice(choices, p=prob)
        
        choices = [citizen_alien_middle_name, alien2.middlename]
        legal_middle_name = self.rng.choice(choices, p=prob)
        
        choices = [citizen_alien_last_name, alien2.lastname]
        legal_last_name = self.rng.choice(choices, p=prob)
        
        choices = [citizen_alien_first_name, alien3.firstname]
        prob = [0.95, 0.05]
        birth_certificate_first_name = self.rng.choice(choices, p=prob)
        choices = [citizen_alien_middle_name, alien3.middlename]
        birth_certificate_middle_name = self.rng.choice(choices, p=prob)
        choices = [citizen_alien_last_name, alien3.lastname]
        birth_certificate_last_name = self.rng.choice(choices, p=prob)
        
        mailing_address_line_1 = alien1.streetno + " " + alien1.streetname
        
        # Apartment number
        aptno = alien1.aptno
        apto = "" if (aptno is None) or (
                    isinstance(aptno, float) and np.isnan(aptno)) or (aptno <= 0) else aptno
        
        mailing_address_line_2 = "" if apto == "" else (
            self.rng.choice(["Apt. ","Suite ", ""], p=[0.7, 0.25, 0.05]) + str(aptno))
        
        mailing_city = alien1.city
        mailing_country_id = self.hardcoded['country']
        mailing_zip_code = alien1.zipcode
        
        foreign_address_line_1 = np.nan
        foreign_address_line_2 = np.nan
        foreign_city = np.nan
        foreign_state_province = np.nan
        foreign_country_id = np.nan
        foreign_postal_code = np.nan
        
        birth_date = alien1.birthday
        country_of_birth = np.nan
        birth_city_state_or_province = np.nan
        # M	Male, F	Female, U Unknown

        gender = self.rng.choice(["F", "M", "U"], p=[0.45, 0.45, 0.1])
        
        country_of_citizenship = np.nan
        previous_tin = self.itin_gen.get_sample()
        previous_ein = self.ein_gen.get_sample()
        
        name_of_college_university_or_company = np.nan
        college_university_or_company_city = np.nan
        college_university_or_company_state = np.nan
        college_university_or_company_length_of_stay = np.nan
        date_application_signed = np.nan
        
        name_of_delegate = alien3.compositename
        phone_number = alien3.phoneno
        
        foreign_tax_id = np.nan
        passport_expiration_date = np.nan
        passport_id_number = np.nan
        country_issuing_passport = np.nan
        state_issuing_passport = np.nan
        us_entry_date = np.nan
        
         # 1 – Passport, 3 – Driver’s License, 13 – USCIS Or blank
        choices = ["1", "3", "13", ""]
        prob = [0.4, 0.4, 0.1, 0.1]
        documentation_type_id = self.rng.choice(choices, p=prob)
        
        driver_license_expiration_date = np.nan
        driver_license_id_number = np.nan
        country_issuing_driver_license = np.nan
        state_issuing_driver_license = np.nan
        
        us_entry_date_2 = np.nan
        documentation_type_id_2 = np.nan
        uscis_documentation_expiration_date = np.nan
        uscis_documentation_id_number = np.nan
        uscis_documentation_issuing_country = np.nan
        uscis_documentation_issuing_state = np.nan
        us_entry_date_3 = np.nan
        
        choices = ["1", "3", "13", ""]
        prob = [0.4, 0.4, 0.1, 0.1]
        documentation_type_id_3 = self.rng.choice(choices, p=prob)


        rec = Record(datatype=SIR073ITINByStateCode,
                    corruptible=SIR073ITINByStateCodeCorruptible,
                    lenth_changable=SIR073ITINByStateCodeLengthChangable,autopop={},
                    itin=itin,
                    mailing_state_province=mailing_state_province,
                    history=history,
                    itin_status_id=itin_status_id,
                    revoked_reason_code=revoked_reason_code,
                    application_reason=application_reason,
                    citizen_alien_first_name=citizen_alien_first_name,
                    citizen_alien_middle_name=citizen_alien_middle_name,
                    citizen_alien_last_name=citizen_alien_last_name,
                    treaty_article_number=treaty_article_number,
                    legal_first_name=legal_first_name,
                    legal_middle_name=legal_middle_name,
                    legal_last_name=legal_last_name,
                    birth_certificate_first_name=birth_certificate_first_name,
                    birth_certificate_middle_name=birth_certificate_middle_name,
                    birth_certificate_last_name=birth_certificate_last_name,
                    mailing_address_line_1=mailing_address_line_1,
                    mailing_address_line_2=mailing_address_line_2,
                    mailing_city=mailing_city,
                    mailing_country_id=mailing_country_id,
                    mailing_zip_code=mailing_zip_code,
                    foreign_address_line_1=foreign_address_line_1,
                    foreign_address_line_2=foreign_address_line_2,
                    foreign_city=foreign_city,
                    foreign_state_province=foreign_state_province,
                    foreign_country_id=foreign_country_id,
                    foreign_postal_code=foreign_postal_code,
                    birth_date=birth_date,
                    country_of_birth=country_of_birth,
                    birth_city_state_or_province=birth_city_state_or_province,
                    gender=gender,
                    country_of_citizenship=country_of_citizenship,
                    previous_tin=previous_tin,
                    previous_ein=previous_ein,
                    name_of_college_university_or_company=name_of_college_university_or_company,
                    college_university_or_company_city=college_university_or_company_city,
                    college_university_or_company_state=college_university_or_company_state,
                    college_university_or_company_length_of_stay=college_university_or_company_length_of_stay,
                    date_application_signed=date_application_signed,
                    name_of_delegate=name_of_delegate,
                    phone_number=phone_number,
                    foreign_tax_id=foreign_tax_id,
                    passport_expiration_date=passport_expiration_date,
                    passport_id_number=passport_id_number,
                    country_issuing_passport=country_issuing_passport,
                    state_issuing_passport=state_issuing_passport,
                    us_entry_date=us_entry_date,
                    documentation_type_id=documentation_type_id,
                    driver_license_expiration_date=driver_license_expiration_date,
                    driver_license_id_number=driver_license_id_number,
                    country_issuing_driver_license=country_issuing_driver_license,
                    state_issuing_driver_license=state_issuing_driver_license,
                    us_entry_date_2=us_entry_date_2,
                    documentation_type_id_2=documentation_type_id_2,
                    uscis_documentation_expiration_date=uscis_documentation_expiration_date,
                    uscis_documentation_id_number=uscis_documentation_id_number,
                    uscis_documentation_issuing_country=uscis_documentation_issuing_country,
                    uscis_documentation_issuing_state=uscis_documentation_issuing_state,
                    us_entry_date_3=us_entry_date_3,
                    documentation_type_id_3=documentation_type_id_3
                )
        return rec


class PITRFGEN800_801_200RecGen(RecordGenerator):
    """Generates a record of the PITRFGEN800_801_200 data record.
    Data names and types corresponds to RSI, since RPE were not available in the source files,
    moreover, few data descriptions were available.
    MVP version considering the known tins is implemented, knowingly:
    ITIN, EIN, SSN, EFIN, PTIN, TIN, and ip_address
    
    Args:
    config:Dict. It is a yaml file which contains paths to source
        files
    Returns:
        The individual Record object.
        A Record object contains a list of keys and associated values.
        The first key is `Record`, and contains the enum class name that
        governs the record, 
        The second key is `is_length_changable`: with a not maintained list,
        The thirds key and going forward list the 'key:value' 
        pairs of fields contained in the Record datatype.
    """
    logging.debug("Initializing PITRFGEN800_801_200RecGen record generator object")
    def __init__(self,config,rng=None,seed=None,config_key='fraud', debug=False): 
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml = config
        self.yml_key= config_key
        self.debug = debug
        
        # Initialization
        self.yml_rh = self.yml['ReturnHeader'][self.yml_key]
        self.src_file_ssn = self.yml['src_file_zips_ssn']
        self.social_gen = GenSSN(src_data=self.src_file_ssn,
                             rng=self.rng, return_state=False,
                             state_of_sample=None,
                             debug=self.debug,
                             return_as_int=True
         )
        self.social_gen.fit()
        
        self.itin_gen = ItinGen(rng=self.rng)
        self.ein_gen = EinGen(rng=self.rng, return_int=True)
        self.efin_gen = EfinGen(rng=self.rng)
        self.ptin_gen = PtinGen(rng=self.rng)
        self.tin_gen = IdSource(rng=self.rng, is_num=True, length=9)
        self.gen_ip4 = IPv4Address(rng=self.rng, join_char=':')



    def get_record(self,_type=None):
        """Generates fields for the IRS file involved
           Fields with value np.nan have not been implemented yet
        """
        # Create a dictionary mapping ID type names to generator functions
        id_generators = {
                "SSN": self.social_gen,
                "ITIN": self.itin_gen,
                "EIN": self.ein_gen,
                "EFIN": self.efin_gen,
                "PTIN": self.ptin_gen,
                "TIN": self.tin_gen,
                "IP_address": self.gen_ip4

        # Add more ID types and their generator methods as needed
        }

        undesirable_id_type = self.rng.choice(list(id_generators.keys()))
        undesirable_value = str(id_generators[undesirable_id_type].get_sample())
    
        rec = Record(datatype=PITRFGEN800_801_200,
                    corruptible=PITRFGEN800_801_200Corruptible,
                    lenth_changable=PITRFGEN800_801_200LengthChangable,autopop={},
                    undesirable_id_type=undesirable_id_type,
                    undesirable_value=undesirable_value
            )
        return rec