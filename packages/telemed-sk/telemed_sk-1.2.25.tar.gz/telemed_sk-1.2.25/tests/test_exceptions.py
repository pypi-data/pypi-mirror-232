import pytest
import pandas as pd
from tabulate import tabulate
import sys
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])

from TeleMed.telemed_sk.utility.exceptions import InputTypeError, ColumnNotFound, ConversionError

### InputTypeError ###
def test_input_type_error_message():
    func_name = "my_function"
    error_message = "Wrong input types have been given to the function."
    error = InputTypeError(func_name)
    assert str(error) == f"{func_name} encountered an error: {error_message}"

def test_input_type_error_custom_message():
    func_name = "my_function"
    custom_message = "Invalid input provided."
    error = InputTypeError(func_name, custom_message)
    assert str(error) == f"{func_name} encountered an error: {custom_message}"

def test_column_not_found_exception():
    # Sample data
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

    # Check if the ColumnNotFound exception is raised
    with pytest.raises(ColumnNotFound) as exc_info:
        raise ColumnNotFound(func='my_function', column='C', data=df)

    # Verify the exception message
    expected_message = f"my_function encountered an error: The following column is not in the data columns list -> C\n\n{tabulate(df, headers='keys', tablefmt='psql')}"
    assert str(exc_info.value) == expected_message

def test_conversion_error_default_message():
    func_name = "test_function"
    with pytest.raises(ConversionError) as exc_info:
        raise ConversionError(func_name)

    assert str(exc_info.value) == f"{func_name} encountered an error: The object cannot be converted"

def test_conversion_error_custom_message():
    func_name = "test_function"
    custom_message = "This is a custom error message."
    with pytest.raises(ConversionError) as exc_info:
        raise ConversionError(func_name, custom_message)

    assert str(exc_info.value) == f"{func_name} encountered an error: {custom_message}"