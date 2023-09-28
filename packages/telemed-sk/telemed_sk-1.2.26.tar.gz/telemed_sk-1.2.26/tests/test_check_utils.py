from typing import Any, Iterable
import pytest
import pandas as pd

import sys
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])
from TeleMed.telemed_sk.utility.check_utils import check_not_isinstance, check_not_in_iterable, check_datatype_convertible, check_dates_complete
from TeleMed.telemed_sk.utility.exceptions import InputTypeError, ConversionError
from TeleMed.telemed_sk.utility.tele_logger import logger

## check_not_isinstance ##
def check_not_isinstance(obj, data_type, func):
    if not isinstance(obj, data_type):
        logger.error(f"Type input obj {type(obj)} must be {data_type}")
        raise InputTypeError(func)

@pytest.mark.parametrize(
    "obj, data_type, func",
    [
        (5, str, "function1"),
        ("string", int, "function2"),
        ([1, 2, 3], dict, "function3"),
    ]
)

def test_check_not_isinstance(obj, data_type, func):
    with pytest.raises(InputTypeError):
        check_not_isinstance(obj, data_type, func)

@pytest.mark.parametrize(
    "obj, data_type, func",
    [
        (5, int, "function1"),
        ("string", str, "function2"),
        ([1, 2, 3], list, "function3"),
    ]
)

def test_check_not_isinstance_OK(obj, data_type, func):
    check_not_isinstance(obj, data_type, func)

## check_not_in_iterable ##
def check_not_in_iterable(obj: Any, iterable: Iterable, func: str):
    if obj not in iterable:
        logger.error(f"Invalid value for {obj}. It must be in {iterable}")
        raise InputTypeError(func)

@pytest.mark.parametrize(
    "obj, iterable, func",
    [
        (5, [1, 2, 3], "function1"),
        ("string", ["abc", "def", "ghi"], "function2"),
        (False, [True, True, None], "function3"),
    ]
)
def test_check_not_in_iterable(obj, iterable, func):
    with pytest.raises(InputTypeError):
        check_not_in_iterable(obj, iterable, func)

@pytest.mark.parametrize(
    "obj, iterable, func",
    [
        (5, [1, 2, 5], "function1"),
        ("string", ["abc", "string", "ghi"], "function2"),
        (False, [True, False, None], "function3"),
    ]
)

def test_check_not_in_iterable_OK(obj, iterable, func):
    check_not_in_iterable(obj, iterable, func)

## check_datatype_convertible ##
def check_datatype_convertible(obj: Any, data_type_conversion: Any, func: str): 
    try:
        data_type_conversion(obj)
    except (ValueError, TypeError):
        raise ConversionError(func = func)

def test_check_datatype_convertible():
    # Test a valid conversion
    obj = "123"
    data_type_conversion = int
    func = "test_check_datatype_convertible"
    assert check_datatype_convertible(obj, data_type_conversion, func) == None

    # Test an invalid conversion
    obj = "abc"
    data_type_conversion = int
    func = "test_check_datatype_convertible"
    with pytest.raises(ConversionError):
        check_datatype_convertible(obj, data_type_conversion, func)


## check_dates_complete ##
# Test case 1: Complete daily date series
def test_complete_daily_dates():
    date_series = pd.Series(pd.date_range(start='2023-01-01', end='2023-01-05', freq='D'))
    assert check_dates_complete(date_series, freq='D') == True

# Test case 2: Incomplete daily date series
def test_incomplete_daily_dates():
    date_series = pd.Series(['2023-08-01', '2023-08-02', '2023-08-04'])  # Missing '2023-08-03'
    assert check_dates_complete(date_series, freq='D') == False

# Test case 3: Complete weekly date series
def test_complete_weekly_dates():
    date_series = pd.Series(pd.date_range(start='2023-01-01', end='2023-01-15', freq='W'))
    assert check_dates_complete(date_series, freq='W') == True
