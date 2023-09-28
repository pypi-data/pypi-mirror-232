import pytest
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])
from TeleMed.telemed_sk.algorithms.utils import * 


## test_train_val_test_split.py ## 
# Helper function to create a sample DataFrame
def create_sample_dataframe():
    data = {
        'unique_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'feature_1': [10, 20, 30, 40, 50, 60, 70, 80, 90],
        'feature_2': [100, 200, 300, 400, 500, 600, 700, 800, 900],
    }
    data = pd.DataFrame(data).set_index('unique_id')
    return data

# Test cases
def test_train_val_test_split():
    # Create a sample DataFrame
    X = create_sample_dataframe()

    # Define val_size and test_size
    val_size = 1
    test_size = 1

    # Call the function to get the splits
    train_df, valid_df, test_df = train_val_test_split(X, val_size, test_size)
    # Assertions to check if the returned objects are DataFrames
    assert isinstance(train_df, pd.DataFrame)
    assert isinstance(valid_df, pd.DataFrame)
    assert isinstance(test_df, pd.DataFrame)

    # Assertions to check the shape of the returned DataFrames
    assert train_df.shape[0] == X.shape[0] - valid_df.shape[0] - test_df.shape[0]

    # Assertions to check if the unique_id index is set correctly
    assert train_df.index.name == 'unique_id'
    assert valid_df.index.name == 'unique_id'
    assert test_df.index.name == 'unique_id'

    # Assertions to check if all unique_ids in the validation and test sets are also present in the train set
    assert set(valid_df.index).union(set(test_df.index)).issubset(set(train_df.index))
  
## test literal_evaluation ##
def test_literal_evaluation():
    # Test case 1: Valid literals
    values_list = ['True', 'False', '42', '3.14', "'hello'", '[1, 2, 3]', '{"a": 1, "b": 2}']
    expected_result = [True, False, 42, 3.14, 'hello', [1, 2, 3], {"a": 1, "b": 2}]
    assert literal_evaluation(values_list) == expected_result

    # Test case 2: Invalid literals (should return the same values as strings)
    values_list = ['invalid_literal_1', 'invalid_literal_2', 'invalid_literal_3']
    expected_result = ['invalid_literal_1', 'invalid_literal_2', 'invalid_literal_3']
    assert literal_evaluation(values_list) == expected_result

    # Test case 3: Empty list
    values_list = []
    expected_result = []
    assert literal_evaluation(values_list) == expected_result

    # Test case 4: Mix of valid and invalid literals
    values_list = ['True', 'invalid_literal', '42', '[1, 2, 3]', 'invalid_literal', '{"a": 1, "b": 2}']
    expected_result = [True, 'invalid_literal', 42, [1, 2, 3], 'invalid_literal', {"a": 1, "b": 2}]
    assert literal_evaluation(values_list) == expected_result

    # Test case 5: Single element list
    values_list = ['True']
    expected_result = [True]
    assert literal_evaluation(values_list) == expected_result

    # Test case 6: List with a nested list
    values_list = ['[1, [2, 3], 4]']
    expected_result = [[1, [2, 3], 4]]
    assert literal_evaluation(values_list) == expected_result

# test_generate_values.py
def test_generate_values():
    # Test case 1: Valid input with specified step
    dictionary = {'min': 1, 'max': 10, 'step': 2}
    default_step = 1
    expected_result = [1, 3, 5, 7, 9, 10]
    assert generate_values(dictionary, default_step) == expected_result

    # Test case 2: Valid input with step set to -1 (min value used as step)
    dictionary = {'min': 5, 'max': 20, 'step': -1}
    default_step = 2
    expected_result = [5, 10, 15, 20]
    assert generate_values(dictionary, default_step) == expected_result

    # Test case 3: Valid input with step set to -1 (default step used as step since min = 0)
    dictionary = {'min': 0, 'max': 10, 'step': -1}
    default_step = 1.5
    expected_result = [0, 1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10]
    assert generate_values(dictionary, default_step) == expected_result

    # Test case 4: Valid input with step set to 'None' (default step used as step)
    dictionary = {'min': 100, 'max': 200, 'step': 'None'}
    default_step = 20
    expected_result = list(np.arange(100, 200 + default_step, default_step))
    assert generate_values(dictionary, default_step) == expected_result

    # Test case 5: Invalid input (missing 'step' key in dictionary)
    dictionary = {'min': 0, 'max': 1}
    default_step = 0.1
    with pytest.raises(Exception):
        generate_values(dictionary, default_step)

    # Test case 6: Invalid input (step greater than values range)
    dictionary = {'min': 1, 'max': 10, 'step': 15}
    default_step = 2
    with pytest.raises(ValueError):
        generate_values(dictionary, default_step)

    # Test case 7: Invalid input (max_value <= min_value)
    dictionary = {'min': 5, 'max': 3, 'step': 1}
    default_step = 1
    with pytest.raises(ValueError):
        generate_values(dictionary, default_step)

## test grid_values_hyperparameters ##
# the function wraps the ones above so we will test only its result
def get_config_hyperparameters():
    config_hyperparameters = {
        'changepoint_prior_scale' : {'min': 10, 'max' : 20, 'step' : 5},
        'seasonality_prior_scale' :  {'min': 10, 'max' : 20, 'step' : 5},
        'weekly_seasonality' : ['True'],
        'yearly_seasonality' : ['True']}
    return config_hyperparameters

def test_grid_values_hyperparameters():
    # Good configuration
    config_hyperparameters = get_config_hyperparameters()
    expected_result = {
        'changepoint_prior_scale' : [10, 15, 20],
        'seasonality_prior_scale' :  [10, 15, 20],
        'weekly_seasonality' : [True],
        'yearly_seasonality' : [True]}
    default_steps = {'changepoint_prior_scale' : 0.1,
                     'seasonality_prior_scale' : 1.0}
    assert grid_values_hyperparameters(config_hyperparameters, default_steps) == expected_result

## create_zero_dataframe ##
def test_create_zero_dataframe():
    # Test case 1: Check if the DataFrame is created with correct shape and zero values
    columns = ['A', 'B', 'C']
    n_rows = 5
    df = create_zero_dataframe(columns, n_rows)

    # Check DataFrame shape
    assert df.shape == (n_rows, len(columns))

    # Check if all values are zero
    assert (df.values == 0).all()

    # Test case 2: Check for an empty DataFrame
    columns = []
    n_rows = 0
    df = create_zero_dataframe(columns, n_rows)

    # Check if the DataFrame is empty
    assert df.empty

    # Test case 3: Check for a single-column DataFrame with zero rows
    columns = ['A']
    n_rows = 0
    df = create_zero_dataframe(columns, n_rows)

    # Check DataFrame shape and if the column is present
    assert df.shape == (n_rows, len(columns))
    assert 'A' in df.columns

## test write_dataframe_locally ##
def test_write_dataframes_locally(tmpdir):
    # Convert tmpdir to a str for the test case
    save_data_folder = str(tmpdir)

    # Test case 1: Write a single DataFrame
    df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    file_name1 = 'file1.csv'
    to_save = [(df1, file_name1)]
    write_dataframes_locally(to_save, save_data_folder)

    # Check if the file was written
    file_path1 = os.path.join(save_data_folder, file_name1)
    assert os.path.exists(file_path1)
    assert os.path.isfile(file_path1)

    # Test case 2: Write multiple DataFrames
    df2 = pd.DataFrame({'C': [7, 8, 9], 'D': [10, 11, 12]})
    file_name2 = 'file2.csv'
    df3 = pd.DataFrame({'E': [13, 14, 15], 'F': [16, 17, 18]})
    file_name3 = 'file3.csv'
    to_save = [(df2, file_name2), (df3, file_name3)]
    write_dataframes_locally(to_save, save_data_folder)

    # Check if the files were written
    file_path2 = os.path.join(save_data_folder, file_name2)
    assert os.path.exists(file_path2)
    assert os.path.isfile(file_path2)

    file_path3 = os.path.join(save_data_folder, file_name3)
    assert os.path.exists(file_path3)
    assert os.path.isfile(file_path3)

## test write_json_locally ## 
def test_write_json_locally(tmpdir):
    # Convert tmpdir to a str for the test case
    save_data_folder = str(tmpdir)

    # Test case 1: Write a single JSON
    json_data1 = {'param1': [1, 2, 3], 'param2': ['a', 'b', 'c']}
    file_name1 = 'file1.json'
    to_save = [(json_data1, file_name1)]
    write_json_locally(to_save, save_data_folder)

    # Check if the file was written
    file_path1 = os.path.join(save_data_folder, file_name1)
    assert os.path.exists(file_path1)
    assert os.path.isfile(file_path1)

    # Read the content of the written JSON file and compare with the original data
    with open(file_path1, 'r') as f:
        loaded_json1 = json.load(f)

    assert loaded_json1 == json_data1

    # Test case 2: Write multiple JSONs
    json_data2 = {'param3': [4, 5, 6], 'param4': ['x', 'y', 'z']}
    file_name2 = 'file2.json'
    json_data3 = {'param5': [7, 8, 9], 'param6': ['m', 'n', 'o']}
    file_name3 = 'file3.json'
    to_save = [(json_data2, file_name2), (json_data3, file_name3)]
    write_json_locally(to_save, save_data_folder)

    # Check if the files were written
    file_path2 = os.path.join(save_data_folder, file_name2)
    assert os.path.exists(file_path2)
    assert os.path.isfile(file_path2)

    file_path3 = os.path.join(save_data_folder, file_name3)
    assert os.path.exists(file_path3)
    assert os.path.isfile(file_path3)

## test remove_folder_locally ## 
def test_remove_folder_locally(tmpdir):
    # Convert tmpdir to a str for the test case
    folder_to_remove = str(tmpdir)

    # Create some test data in the temporary folder
    file_path1 = os.path.join(folder_to_remove, 'file1.txt')
    file_path2 = os.path.join(folder_to_remove, 'file2.txt')

    with open(file_path1, 'w') as f1, open(file_path2, 'w') as f2:
        f1.write("Test file 1")
        f2.write("Test file 2")

    # Ensure the folder exists before removing
    assert os.path.exists(folder_to_remove)

    # Test the remove_folder_locally function
    remove_folder_locally(folder_to_remove)

    # Check if the folder was removed
    assert not os.path.exists(folder_to_remove)

    # Check if the test data files are not present anymore
    assert not os.path.exists(file_path1)
    assert not os.path.exists(file_path2)

## test prepare_dataframe_to_hf ##
def test_prepare_dataframe_to_hf():
    # Sample input DataFrames
    columns = ['timestamp', 'pred_mean', 'id_pred']
    data_pred = {
        'timestamp': ['2023-07-01', '2023-07-02', '2023-07-03'],
        'pred_mean': [10, 20, 30],
        'id_pred': ['A', 'B', 'C']
    }

    data_true = {
        'timestamp': ['2023-07-01', '2023-07-02', '2023-07-03'],
        'y': [8, 18, 25]
    }

    X_pred = pd.DataFrame(data_pred, columns=columns)
    X_true = pd.DataFrame(data_true)

    # Test the prepare_dataframe_to_hf function
    model_name = 'my_model'
    result_df = prepare_dataframe_to_hf(X_true, X_pred, model_name)

    # Check if the resulting DataFrame has the correct columns
    expected_columns = ['ds', 'my_model'.title(), 'y']
    assert list(result_df.columns) == expected_columns

    # Check if the 'my_model' column is correctly populated
    assert list(result_df['my_model'.title()]) == [10, 20, 30]

    # Check if the 'y' column is correctly populated
    assert list(result_df['y']) == [8, 18, 25]

    # Check if 'unique_id' index is set
    assert 'unique_id' not in result_df.columns
    assert result_df.index.name == 'unique_id'

## test mlflow_log_artifact ## 
# Sample data for DataFrames and JSON
df_data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
df = pd.DataFrame(df_data)
json_data = {'param1': [1, 2, 3], 'param2': ['a', 'b', 'c']}

def test_mlflow_log_artifact(tmpdir):
    # Convert tmpdir to a str for the test case
    predict_real_folder = str(tmpdir)

    # Test case 1: Log DataFrames
    experiment_name = 'test_experiment'
    df_filename = 'test_dataframe'
    df_to_save = [(df, df_filename)]

    project_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    test_mlruns_folder = os.path.join(project_path, 'tests', 'mlruns')
    mlflow.set_tracking_uri(test_mlruns_folder)
    mlflow.set_experiment(experiment_name = experiment_name)

    with mlflow.start_run():
        mlflow_log_artifact(predict_real_folder = predict_real_folder, experiment_name = experiment_name, df_to_save = df_to_save)

        # Test case 2: Log JSONs
        json_filename = 'test_json'
        json_to_save = [(json_data, json_filename)]

        mlflow_log_artifact(predict_real_folder, experiment_name, json_to_save=json_to_save)

        # Test case 3: Log both DataFrames and JSONs
        df_to_save = [(df, df_filename)] 
        json_to_save = [(json_data, json_filename)]

        mlflow_log_artifact(predict_real_folder, experiment_name, df_to_save=df_to_save, json_to_save=json_to_save)

    shutil.rmtree(test_mlruns_folder)

## test model_tuning ##  
# mock_classes.py
class MockModel:
    def __init__(self, **params):
        self.params = params

    def fit(self, train_df):
        # Mock the model training process
        pass

    def predict(self, validation_df):
        # Mock the model prediction process
        return pd.DataFrame({'predictions': [1, 2, 3], 'id_pred': ['a', 'b', 'c']})

class MockEvaluator:
    @staticmethod
    def make_evaluation(df_real, df_pred, id_pred, verbose):
        # Mock the evaluation process and return a sample evaluation DataFrame
        return pd.DataFrame({'RMSE': [0.1], 'MAE': [0.2], 'Percentage Coverage': [0.3], 'id_pred': ['AAA']})

def test_model_tuning():
    # Sample data
    train_data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
    validation_data = {'A': [7, 8, 9], 'B': [10, 11, 12]}
    train_df = pd.DataFrame(train_data)
    validation_df = pd.DataFrame(validation_data)

    # Grid parameters for testing
    grid_params = {'param1': [3], 'param2': [False], 'param3': [0.2]}
    best_params = model_tuning(MockModel, MockEvaluator, 'id_pred', grid_params, train_df, validation_df)
    reference_best_params = {'param1': 3, 'param2': False, 'param3': 0.2}
    
    assert best_params == reference_best_params


@pytest.fixture
def to_category_data():
    data = {
        "Name": ["John", "Mary", "Peter", "Lucy", "David"],
        "Age": [25, 31, 28, 42, 19],
        "Gender": ["Male", "Female", "Male", "Female", "Male"],
        "Education": ["Bachelor", "Master", "Bachelor", "PhD", "Bachelor"],
        "Income": [50000, 75000, 60000, 95000, 40000],
    }
    return pd.DataFrame(data)

def test_to_category_returns_new_dataframe(to_category_data):
    columns = ["Gender", "Education"]
    result = to_category(to_category_data, columns)

    assert isinstance(result, pd.DataFrame)
    assert not id(result) == id(to_category_data)


def test_to_category_converts_specified_columns_to_categorical(to_category_data):
    columns = ["Gender", "Education"]
    result = to_category(to_category_data, columns)

    for c in columns:
        assert result[c].dtype.name == "category"


def test_to_category_raises_error_when_column_name_is_not_in_dataframe(to_category_data):
    columns = ["Gender", "Education", "Country"]

    with pytest.raises(KeyError):
        to_category(to_category_data, columns)



def test_format_metric_dataframe():
    dict_to_test = {'MSE': 100, 'RMSE': 10, 'MAPE': 5, 'MAE': 5, 'Percentage Coverage': 91}
    output = format_metric_dataframe(dict_to_test)

    for col in output.columns:
        assert col in ['metric', 'value']
    for metric_name in output['metric']:
        assert metric_name in ['MSE', 'RMSE', 'MAPE', 'MAE', 'Percentage Coverage']

def test_format_output_dataframe():
    dict_to_test = {'timestamp': {0: '2022-12-02 00:00:00', 1:'2022-12-03 00:00:00', 2:'2022-12-04 00:00:00', 3: '2022-12-05 00:00:00',},
                    'id_pred': {0: 'Italia/Veneto', 1: 'Italia/Lombardia', 2: 'Italia/Veneto/X', 3: 'Italia/Lombardia/Y'},
                    'pred_mean': {0: 150, 1: 25, 2: 57, 3: 144}, 'sigma': {0: 19, 1: 19, 2: 19, 3: 21}, 
                    'pi_Lower_95': {0: 113, 1: 0, 2: 19, 3: 103},
                    'pi_Upper_95': {0: 187, 1: 62, 2: 95, 3: 184}}
    
    dataframe_to_test = pd.DataFrame(dict_to_test)
    dataframe_to_test['timestamp'] = pd.to_datetime(dataframe_to_test['timestamp'])
    hierarchy = {'level1' : "codice_regione_erogazione", 'level2': 'altro_parametro'}
    output = format_output_dataframe(dataframe_to_test, hierarchy)
    expected_columns = ['timestamp_pred', 'codice_regione_erogazione', 'altro_parametro',
       'pred_mean', 'pred_sigma', 'pi_Lower_95', 'pi_Upper_95', 'anno',
       'mese']
    for col_name in output.columns:
        assert col_name in expected_columns
