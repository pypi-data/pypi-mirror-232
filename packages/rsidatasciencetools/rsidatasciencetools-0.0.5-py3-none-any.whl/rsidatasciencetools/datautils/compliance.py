# Code to generate compliance records
# @TODO adding generation of Obligations of Individuals

import argparse
from os import listdir, environ, path
import numpy as np
from scipy import stats
import pandas as pd

from enum import Enum, auto
from typing import List, Any, Union, Dict

from rsidatasciencetools.datautils.datagen import (record_enum_names, 
    Record, Source, gen_records_from_data, TaxPayerType)

    
class CorpTaxIdType(Enum):
    taxpayertype = auto()
    firstname = auto()
    lastname = auto()
    middlename = auto()
    companyname = auto()
    numlocations = auto()
    establishdate = auto()
    taxid = auto()
    compositeaddress = auto()
    streetno = auto()
    aptno = auto()
    streetname = auto()
    city = auto()
    zip = auto()
    phoneno = auto()
    email = auto()


class CorpTaxObligationType(Enum):
    taxid = auto()
    period = auto()
    periodnum = auto()
    grossincome = auto()
    taxableincome = auto()
    deductions = auto()
    totaldeduc = auto()
    exemptions = auto()
    

class RecordCC(object):
    """data record for corporate compliance"""
    def __init__(self, datatype=CorpTaxObligationType, **kwargs) -> None: 
        super().__init__(datatype=datatype, **kwargs)


class Deduction(object):
    """The Deduction class represents tax deductions and is
    initialized with a dictionary of deduction types and amounts.

    Args:
        **deduc_list: dictionary of keyword arguments. For example,
            if the Deduction instance is initialized with the
            following dictionary:
            `deductions = Deduction(tax=100, insurance=50, charity=25)`
             Then **deduc_list would be equal to 
             {'tax': 100, 'insurance': 50, 'charity': 25}.        
    """
    
    def __init__(self, **deduc_list) -> None:
        self.deducs: dict[str, Any]  = deduc_list

    @property
    def total(self) -> int:
        """This method return the aggregation of all deduction
        amounts
        """
        return sum([d['amount'] for d in self.deducs.values])

# example
# ded = Deduction({
#     'deduc1':{'desc': 'deduc type 1', 'amount': 1000},
#     'deduc2':{'desc': 'deduc type 2', 'amount': 3000}})

###### CorpTaxObligations NEEDS TO BE FINALIZED ########
## IT NEEDS TO ADD ANNUAL PERIOD ##
### IT WILL NEED IMPORTANT ADAPTATIONS TO SET UP REQUIRED FIELDS, YML CONFIGURATION AND ARGUMENTSs##
class CorpTaxObligationsSource(Source):
    """This class generated records of annual tax obligations for individuals

    Args:
        Source (_type_): _description_
    """
    def __init__(self, yml, outlier=False, furl=None, rng=None, seed=None) -> None:
        super().__init__(furl, rng, seed)
        self.config = yml
        # self.mean, self.std = mean, std

    def get_sample(self):
        return self.rng.normal(self.mean, self.std)

