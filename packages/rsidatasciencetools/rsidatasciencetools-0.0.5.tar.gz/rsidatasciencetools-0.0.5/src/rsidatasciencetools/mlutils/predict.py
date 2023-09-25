import os
import pickle
from turtle import rt
from warnings import warn
from glob import glob
import numpy as np
from os import environ, path
from .multi_model import MultipleOutputModel
from .model_io import ModelManager

if 'RSI_CONFIG_PATH' not in environ:
    environ['RSI_CONFIG_PATH'] = path.dirname(path.dirname(path.realpath(__file__)))
# this is an example - it will utilize the about config path
mm = ModelManager() 


def run_nlp_model_azure(text_df, test=False, model=None, model_name=None, MM=None,
        ambiguous_range=[0.3,0.7], predict_types=['isPII', 'isCalc', 'isSection'], debug=0):
    if model is None:
        if MM is None:
            MM = mm
        model, _ = MM.load_model(model_name, _from='azure')
    # assert isinstance(model,MultipleOutputModel), f"model must be of type {type(MultipleOutputModel)}"
    isMultModel = isinstance(model, MultipleOutputModel)
    
    if 'spacy' in str(type(model)):
        docs = list(model.pipe(text_df['FieldText']) )
        pred_proba = [[doc.cats['PII'], doc.cats['CALC']] for doc in docs ]
        pred_proba = np.array(pred_proba)
        predictions = {k: pred_proba[:,i] for i, k in enumerate(['isPII', 'isCalc'])}
    elif not(isMultModel):
        predict_types = ['pred']
        predictions = {'pred': model.predict_proba(text_df)}
    else:
        # original sklearn model predictions
        predictions = {k: pred for k, pred in model.predict_proba(text_df).items()}
    
    if isMultModel and 'isPII' in model and 'isCalc' in model:
        either_high_prob = (predictions['isPII'] > ambiguous_range[-1]) | (predictions['isCalc'] > ambiguous_range[-1])
        both_high_prob = (predictions['isPII'] > ambiguous_range[-1]) & (predictions['isCalc'] > ambiguous_range[-1])
        
        if any(either_high_prob):
            if any(both_high_prob):
                warn("predicted PII and calc field probability are both high, "
                    "skipping override of class labeling")
            
            to_update = {k: p[either_high_prob & ~both_high_prob] for k, p in predictions.items()}
            
            override = (to_update['isPII'] > ambiguous_range[-1]) & (to_update['isCalc'] < ambiguous_range[1])
            to_update['isCalc'][override] = 0.0
            override = (to_update['isPII'] < ambiguous_range[1]) & (to_update['isCalc'] > ambiguous_range[-1])
            to_update['isPII'][override] = 0.0
            for _type in ['isPII', 'isCalc']:
                predictions[_type][either_high_prob & ~both_high_prob] = to_update[_type]
    rtn_df = text_df.copy()
    # return {k+'_predict': p for k,p in predictions}
    for k, p in predictions.items():  
        rtn_df[k] = p
    for k in predict_types:
        if k not in rtn_df:
            rtn_df[k] = -1.0  # put placeholder value for missing model predictions
        rtn_df[k] = rtn_df[k].apply(lambda x: (-1.0 if x is None else x))
    return rtn_df 
