from typing import Dict, Any, Tuple, Union, Callable
import pandas as pd
from fundamentals.consts import *
from fundamentals.calculations import (get_series, get_mean, get_mean_growth, get_median, get_median_growth, get_std, get_std_growth)

CHECKS_CONFIG = {
    "data": [ROI, ROE, ROA, EPS, BVPS, CASH_RATIO, CUR_RATIO, DEBT_RATIO, DEBT_TO_EQUITY, REVENUE, 
               CASH_RATIO, EQUITY, TOTAL_ASSETS, PEG_EARNINGS_RATIO, PEG_EQUITY_RATIO, PEG_REVENUE_RATIO],
    "function": ["mean", "mean_growth", "median", "median_growth", "std",  "std_growth"],
    "check_type": ['above', 'below', 'range', 'beyond']
}

def get_agregation_results(function:str, column: str, df:pd.DataFrame, check_type:str, periods:int, value1:float, value2:float) -> Tuple[Union[float, None], Union[bool, None]]:
    if function == "mean":
        return _get_results(get_mean, column, df,check_type, periods, value1, value2)
    elif function == "mean_growth":
        return _get_results(get_mean_growth, column, df,check_type, periods, value1, value2)
    elif function == "median":
        return _get_results(get_median, column, df,check_type, periods, value1, value2)
    elif function == "median_growth":
        return _get_results(get_median_growth, column, df,check_type, periods, value1, value2)
    elif function == "std":
        return _get_results(get_std, column, df,check_type, periods, value1, value2)
    elif function == "std_growth":
        return _get_results(get_std_growth, column, df,check_type, periods, value1, value2)
    else:
        raise ValueError(f"Unknown function string: {function}")
def _get_results(func: Callable[[pd.Series], Union[float, None]], column: str, df:pd.DataFrame, check_type:str, periods:int, value1:float, value2:float) -> Tuple[Union[float, None], Union[bool, None]]:
    nr = func(get_series(column, df, periods))
    return nr, _check_nr(nr, check_type, value1, value2)
def _check_nr(nr:float, check_type:str, value1:float, value2:float) -> Union[bool, None]:
    if nr is None:
        return None
    elif check_type == "above":
        return nr >= value1
    elif check_type == "below":
        return nr <= value1
    elif check_type == "range":
        return (value1 <= nr <= value2) and value1 < value2
    elif check_type == "beyond":
        return (nr < value1 or nr > value2) and value1 < value2
    else:
        return None

