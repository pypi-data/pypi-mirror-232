''' Utilities for ML models '''
import numpy as np
import json
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator
from rsidatasciencetools.mlutils.multi_model import MultipleOutputModel


def jstringify_model_object(mdl, string=False, simple_jsonify=False):
    if isinstance(mdl,MultipleOutputModel):
        output = {tag: jstringify_model_object(model, string=string, simple_jsonify=simple_jsonify) 
            for tag, model in mdl.items()}
        if string:
            output = str(output)
        return output
    if isinstance(mdl,Pipeline):
        terms = []
        order = {}
        for i, step in enumerate(mdl.steps):
            if string:
                term = ' '.join([el.strip() for el in str(step).split('\n')])
            else:
                term = {f'step_{i}_{step[0]}': jstringify_model_object(
                    step[1], string=string, simple_jsonify=simple_jsonify)}
            if not(simple_jsonify) and ((step[1].__class__.__name__ in ['TfidfVectorizer', 'CountVectorizer'])  or
                    isinstance(step[1], BaseEstimator)):

                comp, _order = make_dict_from_obj(step[1], order=order, remove_keys=['_stop_words_id'])
                order.update(_order)
                if string:
                    term = ' '.join([str(step[0]).strip(), str(comp)])
                else:
                    term = {f'step_{i}_{step[0]}': comp}
            terms.append(term)
        if string:
            return ' --> '.join(terms)
        else:
            return terms
    else:
        comp, _ = make_dict_from_obj(mdl)
        if string:
            comp = str(comp)
        return comp


def make_dict_from_obj(obj, order={}, remove_keys=[], skip_private=True,
    obfuscate=['password', 'pw', 'token'], recur=0, max_recur=5):
    ''' Attempt to create a approx JSON-able  
        representation of the input object.
    '''
    d = {}
    keys_sort_idx = {}
    for k, v in obj.__dict__.items():
        if (k in remove_keys) or (skip_private and (k.startswith('__'))):
            continue
        elif isinstance(v, np.ndarray):
            try:
                d[k] = v.round(6).tolist()
            except TypeError:
                d[k] = v.tolist()
        elif isinstance(v,dict):
            ndict = {}
            keys = list(v.keys())
            if (k in order) and isinstance(order[k],list) and (len(order[k]) == len(keys)):
                order = order[k]
            else:
                order = np.argsort(keys).tolist()
            for kk in [keys[o] for o in order]:
                try:
                    json.dumps(v[kk])
                    convert = v[kk]
                except TypeError:
                    convert = None
                    try:
                        if recur < max_recur:
                            convert = make_dict_from_obj(v[kk],recur=recur+1, max_recur=max_recur)[0]
                    except (TypeError,AttributeError):
                        pass
                ndict[kk] = ((str(v[kk]) if convert is None else convert) 
                    if not(any((obf in kk.lower()) for obf in obfuscate)) else '****')
            d[k] = ndict
            keys_sort_idx[k] = order
        else:
            try:
                json.dumps(v)
                convert = v
            except TypeError:
                convert = None
                try:
                    if recur < max_recur:
                        convert = make_dict_from_obj(v,recur=recur+1, max_recur=max_recur)[0]
                except (TypeError,AttributeError):
                    pass
                d[k] = ((str(v) if convert is None else convert) 
                    if not(any((obf in k.lower()) for obf in obfuscate)) else '****')
    return d, keys_sort_idx
