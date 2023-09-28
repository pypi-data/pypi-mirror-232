import pandas as pd
import sys
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])

from TeleMed.telemed_sk.datapreparation.uc_preproc import TCPreprocess, TVPreprocess, TAPreprocess, TMPreprocess

def sample_data():
    # Sample data for testing
    data = {
        "column_a": [1, 2, 3],
        "column_b": [4, 5, 6],
        "column_c": [7, 8, 9],
        'target_col': ['a','a','b'],
        'date_col': ['21-10-2020', '22-10-2020', '23-10-2020']
    }
    return pd.DataFrame(data)

def sample_dataTV():
    # Sample data for testing
    data = {
        "column_a": [1, 2, 3],
        "column_b": [4, 5, 6],
        "column_c": ['7', '8', '9'],
        'target_col': ['a','a','b'],
        'date_col': ['21-10-2020', '22-10-2020', '23-10-2020']
    }
    return pd.DataFrame(data)

def test_TCPreprocess():

    hierarchy = {
        "level_1": "column_a",
        "level_2": "column_b",
        "level_3": "column_c"
    }
    conversion = {
        "level_1": None,
        "level_2": None,
        "level_3": "{7: 'seven', 8: 'eight', 9: 'nine'}"
    }

    target_col = "target_col"
    date_col = 'date_col'

    # Sample data for testing
    df = sample_data()
    preprocess = TCPreprocess(hierarchy, conversion, target_col, date_col)

    # Test fit method
    preprocess_fit = preprocess.fit()

    # fit() should return the same instance of the TCPreprocess object
    assert preprocess_fit is preprocess

    # Test transform method
    transformed_data = preprocess.transform(df)

    # Check if the columns are correctly mapped from the hierarchy and conversion dictionaries
    for value in transformed_data['column_c']:
        assert value in ['seven', 'eight', 'nine']

    # Check if the target col has been filtered
    assert transformed_data.shape[0] == 2
   
def test_TVPreprocess():

    hierarchy = {
        "level_1": "column_a",
        "level_2": "column_b",
        "level_3": "column_c"
    }
    conversion = {
        "level_1": None,
        "level_2": None,
        "level_3": "{7: 'seven', 8: 'eight', 9: 'nine'}"
    }

    date_col = 'date_col'
    # Sample data for testing
    df = sample_dataTV()
    preprocess = TVPreprocess(hierarchy, conversion, date_col)

    # Test fit method
    preprocess_fit = preprocess.fit()

    # fit() should return the same instance of the TVPreprocess object
    assert preprocess_fit is preprocess

    # Test transform method
    transformed_data = preprocess.transform(df)

    # Check if the columns are correctly mapped from the hierarchy and conversion dictionaries
    for value in transformed_data['column_c']:
        assert value in ['seven', 'eight', 'nine']

    # Check if the target col has NOT been filtered
    assert transformed_data.shape[0] == 3

def test_TMPreprocess():
    hierarchy = {
        "level_1": "column_a",
        "level_2": "column_b",
        "level_3": "column_c"
    }
    conversion = {
        "level_1": None,
        "level_2": None,
        "level_3": "{7: 'seven', 8: 'eight', 9: 'nine'}"
    }

    date_col = 'date_col'
    # Sample data for testing
    df = sample_data()

    preprocess = TMPreprocess(hierarchy, conversion, date_col)

    # Test fit method
    preprocess_fit = preprocess.fit()

    # fit() should return the same instance of the TMPreprocess object
    assert preprocess_fit is preprocess

    # Test transform method
    transformed_data = preprocess.transform(df)

   # Check if the columns are correctly mapped from the hierarchy and conversion dictionaries
    for value in transformed_data['column_c']:
        assert value in ['seven', 'eight', 'nine']

    # Check if the target col has been filtered
    assert transformed_data.shape[0] == 3

def test_TAPreprocess():
    hierarchy = {
        "level_1": "column_a",
        "level_2": "column_b",
        "level_3": "column_c"
    }
    conversion = {
        "level_1": None,
        "level_2": None,
        "level_3": "{7: 'seven', 8: 'eight', 9: 'nine'}"
    }

    date_col = 'date_col'
    # Sample data for testing
    df = sample_data()
    preprocess = TAPreprocess(hierarchy, conversion, date_col)

    # Test fit method
    preprocess_fit = preprocess.fit()

    # fit() should return the same instance of the TAPreprocess object
    assert preprocess_fit is preprocess

    # Test transform method
    transformed_data = preprocess.transform(df)

    # Check if the columns are correctly mapped from the hierarchy and conversion dictionaries
    for value in transformed_data['column_c']:
        assert value in ['seven', 'eight', 'nine']

    # Check if the target col has been filtered
    assert transformed_data.shape[0] == 3