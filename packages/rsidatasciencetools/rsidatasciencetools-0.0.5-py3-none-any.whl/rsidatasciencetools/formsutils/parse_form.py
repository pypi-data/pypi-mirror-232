'''utilities for reading form .json data and returning ML-usable training data'''
import numpy as np
import pandas as pd
import json

def parse_form_json(jsonfile,debug=0):
    """ parse_form_json.py - parses iText outputted .json forms schema file
        Inputs: jsonfile, debug
        Returns: pandas.DataFrame with columns: 
            Section,Field,FieldText,isCalc,isPII,isCheckbox,isCode
    """
    with open(jsonfile,'r') as f:
        data = json.load(f)

    df = pd.DataFrame({'Section':[],'Field':[],'FieldText':[],
        'isCalc':np.array([],dtype=bool),
        'isPII':np.array([],dtype=bool),
        'isCode':np.array([],dtype=bool),
        'isCheckbox': np.array([],dtype=bool),
        'isMultipleChoice': np.array([],dtype=bool)
    })
    for form in data['Forms']:
        if debug:
            print('\n\n\n')
        for k,v in form['Form'].items():
            if k == 'BusinessSections':
                for el in form['Form']['BusinessSections']:
                    if debug:
                        print(f"\n{el['SectionName']}")
                    for field in el['Field']:
                        values = ([fv['Value'] for fv in field['FieldValue']] 
                                if len(field['FieldValue']) else '<no values>')
                        if debug:
                            print(f"{field['BaseField']['FieldName']} "
                                f"({field['BaseField']['FieldDisplayName']}): "
                                f"{values} [{field['BaseField']['FieldType']}]")
                        df.loc[len(df.index)] = [
                            el['SectionName'],
                            field['BaseField']['FieldName'],
                            field['BaseField']['FieldDisplayName'], 
                            # for importing known "Calculated" fields, perhaps later will be 
                            # adjusted to allow model prediction to update this type
                            field['BaseField']['FieldType'] == "Calculated", # or len(field['FieldValue'])==0  # isCalc  
                            any([(check in field['BaseField']['FieldDisplayName'].lower()) 
                                for check in ['last name', 'identification', 'security', 'ssn', 'address']]) and (
                                'String' in field['BaseField']['FieldValueType']),
                            ('code' in field['BaseField']['FieldDisplayName'].lower() and (  # isCode
                                'String' in field['BaseField']['FieldValueType'])),
                            (len(field['BaseField']['FieldDisplayName']) == 0 or ( # isCheckbox
                                'Boolean' in field['BaseField']['FieldValueType'])),
                            len(field['BaseField']['PossibleValues']) > 0  # isMultipleChoice
                        ]
            elif debug:
                if not(isinstance(v,(dict,list))):
                    print(k,v)
                elif isinstance(v,dict):
                    print(k,'dict(...)')
                else:
                    print(k,'list(...)')
    return df