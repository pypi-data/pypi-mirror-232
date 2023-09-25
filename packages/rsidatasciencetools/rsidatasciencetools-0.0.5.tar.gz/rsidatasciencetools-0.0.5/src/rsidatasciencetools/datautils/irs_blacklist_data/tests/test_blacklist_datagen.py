"Testing for IRS file generation pending"
from typing import Dict
import pandas as pd
import numpy as np
import pytest
import os
import time


from rsidatasciencetools.datautils.irs_blacklist_data.blacklist_datagen import (
        BlacklistFileGenerator
)
from rsidatasciencetools.datautils.irs_blacklist_data.blacklist_file_classes import (
        SIR029WeeklyIndividualQuestionable,
        SIR024PriorYearIndividualConfirmed,
        SIR075PreparerTIN,
        SIR027ITPIIDTheftIndicator,
        SIR023CurrentYearIndividualQuestionable,
        SIR025PITRF700Incidentfile,
        SIR114FederalPrisonerFiles,
        SIR117PITRF800SIR118PITRF200ISACAlertsAndSuspectEmailDomains,
        PITRF500EfinSIR116,
        SIR073ITINByStateCode,
        PITRFGEN800_801_200,
        PrisonerSimulator)
from rsidatasciencetools.config.baseconfig import YmlConfig


seed = 19
num_recs = 15
rng = np.random.RandomState(seed)
path_to_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tests')
yml = YmlConfig(path_to_config, base_str='mef_rec_gen', read_all=True,ext='yaml',auto_update_paths=True)

enum_classes = {
    'SIR029': SIR029WeeklyIndividualQuestionable,
    'SIR024': SIR024PriorYearIndividualConfirmed,
    'SIR075': SIR075PreparerTIN,
    'SIR027': SIR027ITPIIDTheftIndicator,
    'SIR023': SIR023CurrentYearIndividualQuestionable,
    'SIR025': SIR025PITRF700Incidentfile,
    'SIR114': SIR114FederalPrisonerFiles,
    'PITRF800': SIR117PITRF800SIR118PITRF200ISACAlertsAndSuspectEmailDomains,
    'PITRF500': PITRF500EfinSIR116,
    'SIR073': SIR073ITINByStateCode,
    'PITRFGEN800_801_200': PITRFGEN800_801_200
}


# Use pytest.mark.parametrize to loop over enum_classes.keys()
@pytest.mark.parametrize("file_code", enum_classes.keys())
def test_records_in_enums(file_code):
    """
    Test that all records belong to the enumerator classes
    """
    
    blacklist_df_generator = BlacklistFileGenerator(
                            rng=rng,
                            config=yml,
                            file_code=file_code,
                            export_csv=False,
                            debug=False
    )
    rec = blacklist_df_generator.gen_records(num=num_recs)

    for k in rec:
        assert k in enum_classes[file_code].__members__.keys(), \
            f"{k} does not belong to {enum_classes[file_code]} file in IRS Blacklist"



@pytest.mark.parametrize("file_code", enum_classes.keys())
def test_enums_in_records(file_code):
    """
    Test that all fields listed in the enum classes are part of the record.
    Obs: some record may have np.nan in the value, but still must be included
    in the record.
    """
    blacklist_df_generator = BlacklistFileGenerator(
        rng=rng,
        config=yml,
        file_code=file_code,
        export_csv=False,
        debug=False
    )

    rec = blacklist_df_generator.gen_records(num=num_recs)

    # Get the enum class for the current file_code
    enum_class = enum_classes[file_code]

    # Create a set of enum member names
    enum_member_names = {member.name for member in enum_class}

    # Check if each enum member name is in the records
    for member_name in enum_member_names:
        assert member_name in rec, \
            f"{member_name} from {enum_class} is not present in the records."
            

@pytest.mark.parametrize("file_code", enum_classes.keys())
def test_generate_files_with_content(file_code):
    """
    Test that files are exported and have content.
    The export is made by checking that the files exist and
    have been generated recently (less than a minute)
    """
    blacklist_df_generator = BlacklistFileGenerator(
        rng=rng,
        config=yml,
        file_code=file_code,
        export_csv=True,
        debug=False
    )

    # Generate the records and export to CSV
    blacklist_df_generator.gen_records(num=num_recs)

    # Define the file name with the timestamp
    expected_file_name = f"{file_code}.csv"

    # Check if the file exists
    assert os.path.exists(expected_file_name), f"File {expected_file_name} does not exist."

    # Check if the file has a non-zero size (contains content)
    file_size = os.path.getsize(expected_file_name)
    assert file_size > 0, f"File {expected_file_name} is empty."

    # Check if the file is recent (modified within the last X seconds, adjust X as needed)
    recent_threshold = 60 #secs
    current_time = time.time()
    file_modification_time = os.path.getmtime(expected_file_name)
    assert (current_time - file_modification_time) <= recent_threshold, \
        f"File {expected_file_name} is not recent, so it was probably not generated."
        
# Use pytest.mark.parametrize to loop over enum_classes.keys()
@pytest.mark.parametrize("file_code", enum_classes.keys())
def test_generated_records_count(file_code):
    """
    Test the number of generated records
    """
    blacklist_df_generator = BlacklistFileGenerator(
        rng=rng,
        config=yml,
        file_code=file_code,
        export_csv=False,
        debug=False
    )

    # Generate the records
    rec = blacklist_df_generator.gen_records(num=num_recs)
    
    # Check if the number of generated records matches the requested value (10)
    assert len(rec) == num_recs, f"Number of generated records in {file_code} does not match the requested value ({num_recs})."





    

