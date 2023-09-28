import pytest
import sys
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])
from TeleMed.telemed_sk.utility.configuration_utils import *
from TeleMed.telemed_sk.utility.exceptions import InputTypeError
import re

project_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(project_path, 'config')

# test get_configuration ##
def test_get_configuration():
    config_file = "unittest_path.toml"  
    # Test reading a valid configuration file
    expected_config =     {'logging': {'logging_folder': 'logs'},
                           'data_paths': {'data_folder': 'tests/data/input', 'experiment_folder': 'tests/experiments/mlruns', 'predict_save_folder': 'tests/data/output/output_predictions', 'predict_real_folder': 'tests/data/models'}, 
                           'data_file': {'data_input_filename': 'unittest_data_placeholder.parquet'}}
    
    config = get_configuration(config_path, config_file)
    assert config == expected_config

    # Test reading an invalid configuration file (file not found)
    non_existent_config_file = "non_existent_config.toml"
    with pytest.raises(Exception) as exc_info:
        get_configuration(config_path, non_existent_config_file)
    assert str(exc_info.value) == f"File {non_existent_config_file} not found in {config_path} please double check that the filename is correct."

## test config_reading ##
def test_config_reading():
    # Prepare test data
    config_dict = {
        'config_path': config_path,  # Replace this with the actual path to your test configuration files
        'config_file': "unittest_prophet.toml"  # Replace this with the actual config file name
    }

    config_dict_parsing = {
        'config_path': config_path,  # Replace this with the actual path to your test configuration files
        'config_file': "unittest_prophet_parsing.toml"  # Replace this with the actual config file name for parsing
    }

    # Test reading two valid configuration files
    config_file, config_file_parsing = config_reading(config_dict, config_dict_parsing)

    assert isinstance(config_file, dict)
    assert isinstance(config_file_parsing, dict)

## test config_key_parsing ##
def test_config_key_parsing():
    config_file = {"key1": "value1", "key2": 42, "key3": [1, 2, 3]}

    config_file_parsing = {"key1": ['value1'], "key2": [42], "key3": [1, 2, 3]}

    # Test for matching keys (should not raise an exception)
    config_key_parsing(config_file, config_file_parsing)

    # Test for non-matching keys (should raise an exception)
    config_file_invalid = {"key1": "value1", "key4": "value4",}

    with pytest.raises(InputTypeError):
        config_key_parsing(config_file_invalid, config_file_parsing)

## test check_usecases ##
def test_check_usecases():
    # Prepare test data
    valid_usecase = "usecase1"
    possible_usecases = ["usecase1", "usecase2", "usecase3"]

    # Test for a valid usecase (should not raise an exception)
    check_usecases(valid_usecase, possible_usecases)

    # Test for an invalid usecase (should raise an exception)
    invalid_usecase = "invalid_usecase"

    with pytest.raises(InputTypeError):
        check_usecases(invalid_usecase, possible_usecases)

## test check_model ##
def test_check_model():
    # Prepare test data
    valid_model_name = "model1"
    valid_reference_model_name = "model1"
    valid_apply_reconciler = 'boosting'
    valid_reference_apply_reconciler = ['boosting', 'hierarchical']

    # Test for valid model and apply_hierarchical (should not raise an exception)
    check_model(valid_model_name, valid_reference_model_name, valid_apply_reconciler, valid_reference_apply_reconciler)

    # Test for invalid model_name (should raise an exception)
    invalid_model_name = "invalid_model"

    with pytest.raises(InputTypeError):
        check_model(invalid_model_name, valid_reference_model_name, valid_apply_reconciler, valid_reference_apply_reconciler)

    # Test for inconsistent model_name and reference_model_name (should raise an exception)
    inconsistent_model_name = "model2"

    with pytest.raises(InputTypeError, match=f"model_name {inconsistent_model_name} MUST be equal to reference_model_name {valid_reference_model_name}"):
        check_model(inconsistent_model_name, valid_reference_model_name, valid_apply_reconciler, valid_reference_apply_reconciler)

    # Test for invalid apply_hierarchical (should raise an exception)
    invalid_apply_hierarchical = "not_a_bool"

    with pytest.raises(InputTypeError):
        check_model(valid_model_name, valid_reference_model_name, invalid_apply_hierarchical, valid_reference_apply_reconciler)

## test check_hyperparameters ##
def test_check_hyperparameters():
    # Prepare test data
    valid_hyperparameters = ["param1", "param2", "param3"]
    valid_possible_hyperparameters = ["param1", "param2", "param3", "param4"]

    # Test for valid hyperparameters (should not raise an exception)
    check_hyperparameters(valid_hyperparameters, valid_possible_hyperparameters)

    # Test for invalid hyperparameter type (should raise an exception)
    invalid_hyperparameters = "not_a_list"

    with pytest.raises(Exception):
        check_hyperparameters(invalid_hyperparameters, valid_possible_hyperparameters)

    # Test for invalid type hyperparameter (should raise an exception)
    invalid_hyperparameter = 5

    with pytest.raises(InputTypeError):
        check_hyperparameters([invalid_hyperparameter], valid_possible_hyperparameters)

## test check_hyperparameters_value ##
def test_check_hyperparameters_value():
    # Prepare test data with valid hyperparameters
    valid_hyperparameters = {"param1": [1, 2, 3],
                             "param2": {"subparam1": 42, "subparam2": 3.14}}

    # Test for valid hyperparameters (should not raise an exception)
    check_hyperparameters_value(valid_hyperparameters)

    # Prepare test data with invalid hyperparameters
    invalid_hyperparameters = {"param1": "not_a_list_or_dict",
                               "param2": 42,}

    # Test for invalid hyperparameters (should raise an exception)
    with pytest.raises(InputTypeError, match="The hyperparameters to specify must be List or Dict"):
        check_hyperparameters_value(invalid_hyperparameters)

## test check_missing_data_strategy ##
def test_check_missing_data_strategy():
    # Prepare test data with valid missing_data_strategy
    valid_string_strategy = "strategy1"
    valid_dict_strategy = {"interpolation": "linear", "order": 1}

    # Prepare valid lists of possible strategies, dictionary keys, and interpolation methods
    valid_possible_strategies = ["strategy1", "strategy2", "strategy3"]
    valid_possible_dictionary_keys = ["interpolation", "order"]
    valid_possible_interpolation_methods = ["linear", "spline"]

    # Test for valid missing_data_strategy (should not raise an exception)
    check_missing_data_strategy(valid_string_strategy, valid_possible_strategies, 
                                valid_possible_dictionary_keys, valid_possible_interpolation_methods)

    check_missing_data_strategy(valid_dict_strategy, valid_possible_strategies, 
                                valid_possible_dictionary_keys, valid_possible_interpolation_methods)

    # Prepare invalid test data
    invalid_type_strategy = tuple("invalid_strategy",)
    with pytest.raises(TypeError, match="Invalid type for 'missing_data_strategy' in 'configuration_utils.check_missing_data_strategy'. It must be str or int or dict"):
        check_missing_data_strategy(invalid_type_strategy, valid_possible_strategies, 
                                    valid_possible_dictionary_keys, valid_possible_interpolation_methods)
    # Prepare invalid test data
    invalid_int_strategy = 10
    with pytest.raises(TypeError, match="Invalid value for missing_data_strategy. It must be equal to 0"):
        check_missing_data_strategy(invalid_int_strategy, valid_possible_strategies, 
                                    valid_possible_dictionary_keys, valid_possible_interpolation_methods)
    
    # Prepare invalid test data
    invalid_string_strategy = "invalid_strategy"
    with pytest.raises(InputTypeError):
        check_missing_data_strategy(invalid_string_strategy, valid_possible_strategies, 
                                    valid_possible_dictionary_keys, valid_possible_interpolation_methods)

    # Prepare invalid test data
    invalid_dict_strategy1 = {"not_interpolation_or_order": "value1", "order": 3}
    invalid_dict_strategy2 = {"interpolation": "invalid_method", "order": 3}
    invalid_dict_strategy3 = {"interpolation": "linear", "order": '3'}
    
    with pytest.raises(InputTypeError):
        check_missing_data_strategy(invalid_dict_strategy1, valid_possible_strategies, 
                                    valid_possible_dictionary_keys, valid_possible_interpolation_methods)

    with pytest.raises(InputTypeError):
            check_missing_data_strategy(invalid_dict_strategy2, valid_possible_strategies, 
                                        valid_possible_dictionary_keys, valid_possible_interpolation_methods)
            
    with pytest.raises(InputTypeError):
            check_missing_data_strategy(invalid_dict_strategy3, valid_possible_strategies, 
                                        valid_possible_dictionary_keys, valid_possible_interpolation_methods)

## test check_time_granularity ##
def test_check_time_granularity():
    # Prepare test data with valid time_granularity
    valid_time_granularity = "hourly"
    valid_possible_time_granularities = ["hourly", "daily", "weekly", "monthly"]

    # Test for valid time_granularity (should not raise an exception)
    check_time_granularity(valid_time_granularity, valid_possible_time_granularities)

    invalid_possible_time_granularities = "not_a_list"


    # Test for invalid time_granularity type (should raise an exception)
    # with pytest.raises(TypeError):
    with pytest.raises(InputTypeError):
        check_time_granularity(123.45, valid_possible_time_granularities)

    # Test for invalid possible_time_granularities type (should raise an exception)
    # with pytest.raises(TypeError):
    with pytest.raises(InputTypeError):
        check_time_granularity(valid_time_granularity, invalid_possible_time_granularities)

## test check_preprocessing ##
def test_check_preprocessing():
    # Prepare test data with valid target_col and date_col
    valid_target_col = "target_column"
    valid_date_col = "date_column"

    # Test for valid target_col and date_col (should not raise an exception)
    check_preprocessing(valid_target_col, valid_date_col)

    # Prepare invalid test data
    invalid_target_col = 123.45
    invalid_date_col = ["date_column"]

    # Test for invalid target_col type (should raise an exception)
    # with pytest.raises(TypeError):
    with pytest.raises(InputTypeError):
        check_preprocessing(invalid_target_col, valid_date_col)

    # Test for invalid date_col type (should raise an exception)
    # with pytest.raises(TypeError):
    with pytest.raises(InputTypeError):
        check_preprocessing(valid_target_col, invalid_date_col)

## test check_split_forecasting ##
def test_check_split_forecasting():
    # Prepare test data with valid input
    valid_time_granularity = "D"
    valid_validation_obs = 20
    valid_test_obs = 10
    valid_num_forecast_periods = 5
    valid_start_date = "2023-07-20"

    # Test for valid input (should not raise an exception)
    check_split_forecasting(valid_time_granularity, valid_validation_obs, valid_test_obs,
                            valid_num_forecast_periods, valid_start_date)

    # Prepare invalid test data
    invalid_time_granularity = 123
    invalid_validation_obs = 0
    invalid_num_forecast_periods = 0

    # Test for invalid time_granularity type (should raise an exception)
    # with pytest.raises(TypeError):
    with pytest.raises(InputTypeError):
        check_split_forecasting(invalid_time_granularity, valid_validation_obs, valid_test_obs,
                                valid_num_forecast_periods, valid_start_date)

    # Test for invalid validation_obs value (should raise an exception)
    with pytest.raises(InputTypeError):
        check_split_forecasting(valid_time_granularity, invalid_validation_obs, valid_test_obs,
                            valid_num_forecast_periods, valid_start_date)

    # Test for invalid num_forecast_periods value (should raise an exception)
    with pytest.raises(InputTypeError):
        check_split_forecasting(valid_time_granularity, valid_validation_obs, valid_test_obs,
                            invalid_num_forecast_periods, valid_start_date)

    # Test for invalid start_date type (should raise an exception)
    # with pytest.raises(TypeError):
    with pytest.raises(InputTypeError):
        check_split_forecasting(valid_time_granularity, valid_validation_obs, valid_test_obs,
                                valid_num_forecast_periods, 123.45)

## test check_hierarchy ##
def test_check_hierarchy():
    # Prepare test data with valid hierarchy
    valid_hierarchy = {"level1": "category1", "level2": "category2", "level3": "category3"}

    # Test for valid hierarchy (should not raise an exception)
    check_hierarchy(valid_hierarchy)

    # Prepare invalid test data
    invalid_hierarchy = {"level1": 123, "level2": "category2", "level3": "category3"}

    # Test for invalid hierarchy (should raise an exception)
    with pytest.raises(InputTypeError):
        check_hierarchy(invalid_hierarchy)

## test check_conversion ##
def test_check_conversion():
    # Prepare test data with valid conversion
    valid_conversion = {"value1": "converted1", "value2": "converted2", "value3": "converted3"}

    # Test for valid conversion (should not raise an exception)
    check_conversion(valid_conversion)

    # Prepare invalid test data
    invalid_conversion = {"value1": 123, "value2": "converted2", "value3": "converted3"}

    # Test for invalid conversion (should raise an exception)
    with pytest.raises(InputTypeError):
        check_conversion(invalid_conversion)

## test config_parsing ##
# The function config_parsing is an ensamble of the functions above
# It's test will consider only its good execution for the config files: unittest_prophet_parsing.toml, unittest_prophet.toml since it's tested already in its sunfunctions
def test_config_parsing():
    config_filename = 'unittest_prophet.toml'
    config_filename_parsing = 'unittest_prophet_parsing.toml'
    config_parsing(config_path, config_filename, config_filename_parsing)
