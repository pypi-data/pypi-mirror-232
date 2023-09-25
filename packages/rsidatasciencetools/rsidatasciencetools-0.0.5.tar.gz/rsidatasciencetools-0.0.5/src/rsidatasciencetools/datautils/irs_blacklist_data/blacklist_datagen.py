"""Generates IRS Blacklist data for fraud models
This code below will generate files of IRS Blacklist, and export to csv:
$python blacklist_datagen.py --file='SIR029' --n_samples=10 --seed=19  --export_csv --debug

The files implemented are:
 - SIR-029 Weekly Individual Questionable
 - SIR-024 Prior Year Individual Confirmed
 - SIR-075-Preparer TIN (PTIN)
 - SIR-027 ITPI ID Theft Indicator
 - SIR-023-Current Year Individual Questionable
 - SIR-025 PITRF700 Incident file
 - SIR-114(Federal Prisoner Files)
 - PITRF800 ISAC Alerts (SIR-117) &  PITRF200 Suspect Email Domains (SIR-118) 
 - SIR-116 (PITRF500 - IRS EFIN)

The fields in green are pending for implementation. 
The field STIN needs to be readadressed since age attribute is no longer available

Configuration used for this files are the same as the one used for fraudulent cases (config_key = 'fraud')

The State have been harcoded as 'MD' because datagen.py is not providing the state, and all addresses are in Maryland.
"""


import datetime as dt
from datetime import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Union
import os
import yaml
from enum import Enum, auto
import logging
import argparse
import math

from rsidatasciencetools.datautils.datagen import Record, RecordGenerator
from rsidatasciencetools.config.baseconfig import YmlConfig
from rsidatasciencetools.datautils.irs_blacklist_data.blacklist_file_classes import (
    SIR029RecGen, SIR024RecGen, SIR075RecGen, SIR027RecGen, SIR023RecGen,
    SIR025RecGen, SIR114RecGen, PITRF800RecGen, PITRF500RecGen, SIR073RecGen,
    PITRFGEN800_801_200RecGen
)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.debug("Generating Files")

class BlacklistFileGenerator(object):
    """This class generates an IRS blacklist dataset
    with several records, with option to get a dataframe
    and/or export its csv file.
    """
    logging.debug("Initializing the Blacklist Dataset Generator")
    
    # Dictionary to map file_code to corresponding generator class
    FILE_CODE_TO_CLASS = {
        'SIR029': SIR029RecGen,
        'SIR024': SIR024RecGen,
        'SIR075': SIR075RecGen,
        'SIR027': SIR027RecGen,
        'SIR023': SIR023RecGen,
        'SIR025': SIR025RecGen,
        'SIR114': SIR114RecGen,
        'PITRF800': PITRF800RecGen, # same as  'PITRF200', 'SIR117', 'SIR118'
        'PITRF500': PITRF500RecGen, # PITRF500 same as SIR116
        'SIR073': SIR073RecGen, # SIR073 same as SIR136
        'PITRFGEN800_801_200': PITRFGEN800_801_200RecGen,
    }
    
    def __init__(self, 
                 file_code:str, 
                 config:str, rng=None, 
                 seed=None, debug=False, 
                 as_df=True,
                 export_csv=True,
    ):
        self.file = file_code
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.yml=config
        self.debug=debug
        self.as_df = as_df
        self.export_csv=export_csv

        if self.file in self.FILE_CODE_TO_CLASS:
            generator_class = self.FILE_CODE_TO_CLASS[self.file]
            self.file_gen = generator_class(self.yml)

    def gen_records(self,num):
        """Generates a `num` number of records for the required file"""
        logging.debug("Generating records...")
        recs=[]

        for _ in range (num):
            new_recs = self.file_gen.get_record()
            recs.append(new_recs)

        logging.info(f"IRS Blacklist {self.file} file generated")


        if self.as_df or self.export_csv:
        # Convert records into dataframes
            recs_df = Record.as_dataframe(recs)

        if self.export_csv:
            recs_df.to_csv(f"{self.file}.csv", index=False)
            logging.info(f"CSV file for {self.file} succesfully exported")

        if self.as_df:
            return recs_df
        else:
            return recs


#############################################
if __name__ == '__main__':
       
    path_to_config = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../tests')
    yml = YmlConfig(path_to_config, read_all=True, ext='yaml', auto_update_paths=True)
    
    # Define the arguments
    parser = argparse.ArgumentParser(
    description='''
This code generates fake IRS Blacklist files and or data.

Example command line call:
    python blacklist_datagen.py --n_samples=10 --seed=19  --export_csv --debug    
''')
    parser.add_argument('--file', type=str,
                        help="File code. Implemented: 'SIR029', 'SIR024', \
                             'SIR075', 'SIR027', 'SIR023','SIR025', 'SIR114',\
                            'PITRF800','PITRF500','SIR073','PITRFGEN800_801_200'", default='SIR029')
    parser.add_argument('--n_samples', type=int,
                        help='Number of records to generate', default=10)
    parser.add_argument('--seed', type=int,
                        help='Seed to start random state', default=19)
    parser.add_argument('--export_csv', action='store_true',
                        help='Export to CSV', default=True)
    parser.add_argument('--debug', action='store_true',
                        help='Enable debugging', default=False)

    # Parse the arguments
    args = parser.parse_args()
    
    # Generate the random number generator
    rng = np.random.RandomState(seed=args.seed)

    # IRS File Generation
    blacklist_df_generator = BlacklistFileGenerator(
                            config=yml,
                            file_code=args.file,
                            seed=args.seed, 
                            export_csv=args.export_csv,
                            debug=args.debug
    )

    recs  = blacklist_df_generator.gen_records(num=args.n_samples)