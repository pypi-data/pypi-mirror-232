
"""This code defines three functions for cleaning up data: 
fix_reals: converts values to integers or floats, 
fix_percent: converts values to floats and adjusts for percentages
fix_lists: converts strings to lists of values.
"""

from typing import List, Any, Union
import pandas as pd
import numpy as np


def fix_reals(v, adjust_prct:bool =False):
    """The fix_reals function takes a value v and an optional boolean 
    flag adjust_prct, and returns the value after performing some
    cleanup operations. If v is already a float or an integer, the
    function returns it unchanged. Otherwise, it removes commas and
    percent signs from the value and tries to convert it to an integer.
    If this fails, it tries to convert the value to a float with 5
    decimal places of precision. 
    The adjust_prct flag is used to signal the value has a percentage
    sign that needs to be removed.

    Args:
        v (float, int, Any): the value to be adjusted to a numeric format
        adjust_prct (bool, optional): if set to True and the value originally
            ended with a percent sign, the function divides the float by 100. 
            If the value contains the string "(S)", the function returns 0.001. 
            Otherwise, it returns a capitalized string with whitespace replaced 
            by a single space. Defaults to False.

    Returns:
        float, int, str: the adjusted value for the input v.
    """
    if isinstance(v,(float,int)):
        return v
    v = v.strip()
    is_percent = v.endswith('%') and adjust_prct
    v = v.replace(',','').replace('%','')
    try:
        return int(v)
    except ValueError:
        try:
            v = np.round(float(v),decimals=5)
            if is_percent:
                return v/100.
            else:
                return v
        except ValueError:
            if '(S)' in v:
                return  0.001
            return ' '.join([el.capitalize() for el in v.strip().split(' ')])
        
        
def fix_percent(*args, adjust_prct=True) -> Union[float, int, Any, str]:
    """This is a wrapper function around fix_reals to adjust percentage to int or float.

    Args:
        adjust_prct (bool): Indicates whether the input has a
        percentage symbol. Defaults to True.

    Returns:
        float | int | Any | LiteralString: the modified percentage
        if the adjuste_prct flag is True as in the fix_reals
        function with True adjust_prct flag.
    """
    return fix_reals(*args, adjust_prct=adjust_prct)


def try_convert_list_to_datetimes(dt_list:list[str], info=True) -> List[pd.Timestamp]:
    try:
        return [pd.Timestamp(o) for o in dt_list]
    except pd._libs.tslibs.parsing.DateParseError as e:
        info and print('unable to convert to datetime')
    return dt_list


def fix_lists(_in,try_datetimes=False) -> List:
    """This function tries to parse a string to a list.
     It takes an input _in, converts it to a string, and checks if
     it contains square brackets or semicolons. 
     - If it contains square brackets, the function returns a list
     of values obtained by removing the brackets, single quotes,
     and whitespace from the string and splitting it on commas.
     - If it contains semicolons, the function returns a list of
     values obtained by splitting the string on semicolons and
     removing whitespace. 
     -If it doesn't contain either brackets or semicolons, the
     function returns a list containing the input value as a single
     element.

    Args:
        _in (str): the input to be converted to a list

    Raises:
        NotImplementedError: when input contains a comma but no
            brackets or semicolons

    Returns:
        List: a list that can be separated by commas, semicolons, 
            or be of a single-element, depending on the input
            original separator, per description above.
    """
    _in = str(_in)
    if '[' in _in:
        out = [v.strip() for v in _in.replace('[','').replace(']','').replace("'",'').split(',')]
        return try_convert_list_to_datetimes(out) if try_datetimes else out
    elif ';' in _in:
        return [v.strip() for v in _in.split(';')]
    else:
        if ',' not in _in:
            out = [_in.strip()]
            return try_convert_list_to_datetimes(out) if try_datetimes else out
        else:
            try:
                out = _in.split(',')
                return try_convert_list_to_datetimes(out) if try_datetimes else out
            except:
                pass
        raise NotImplementedError(f'uncertain how to parse string to list: {_in}')
