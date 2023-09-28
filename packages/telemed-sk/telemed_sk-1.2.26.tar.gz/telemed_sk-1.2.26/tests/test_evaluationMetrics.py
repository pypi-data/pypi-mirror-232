import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])

from TeleMed.telemed_sk.analytics.evaluationMetrics import EvaluateModel
from TeleMed.telemed_sk.utility.exceptions import InputTypeError, ColumnNotFound

def test_evaluate_model_init():
    # Correct input data
    date_true = "timestamp_true"
    date_pred = "timestamp_pred"
    y_true = "target_true"
    y_pred = "target_pred"
    upper_95 = "upper_ci_95"
    lower_95 = "lower_ci_95"

    # Check if the class initializes correctly with correct input data
    model = EvaluateModel(date_true, date_pred, y_true, y_pred, upper_95, lower_95)
    assert model.date_true == date_true
    assert model.date_pred == date_pred
    assert model.y_true == y_true
    assert model.y_pred == y_pred
    assert model.upper_95 == upper_95
    assert model.lower_95 == lower_95

    # Incorrect input data - Using integers instead of strings
    # with pytest.raises(TypeError):
    with pytest.raises(InputTypeError):
        EvaluateModel(2023, "timestamp_pred", "target_true", "target_pred", "upper_ci_95", "lower_ci_95")

    # Incorrect input data - Using booleans instead of strings
    # with pytest.raises(TypeError):
    with pytest.raises(InputTypeError):
        EvaluateModel("timestamp_true", "timestamp_pred", True, "target_pred", "upper_ci_95", "lower_ci_95")


def test_make_evaluation_column_not_found():
    # Create a sample DataFrame for testing
    df_real = pd.DataFrame({
        "timestamp_true": pd.date_range(start='2023-01-01', periods=5),
        "target_true": [1, 2, 3, 4, 5]
    })

    # This DataFrame is mispelling the 'target_pred' column
    df_pred = pd.DataFrame({
        "timestamp_pred": pd.date_range(start='2023-01-01', periods=5)
    })

    model = EvaluateModel("timestamp_true", "timestamp_pred", "target_true", "target_pred", "upper_ci_95", "lower_ci_95")

    # Check if the method raises the ColumnNotFound exception
    with pytest.raises(ColumnNotFound):
        model.make_evaluation(df_real, df_pred, "id_pred")


def test_make_evaluation_correct_input():
    # Create a sample DataFrame for testing
    df_real = pd.DataFrame({
        "timestamp_true": pd.date_range(start='2023-01-01', periods=5),
        "target_true": [1, 2, 3, 4, 5],
        'upper_ci_95' : [3, 4, 5, 6, 7],
        'lower_ci_95' : [0, 1, 2, 3, 4]
    })

    df_pred = pd.DataFrame({
        "timestamp_pred": pd.date_range(start='2023-01-01', periods=5),
        "target_pred": [1, 2, 2.5, 4, 5.5],
        'upper_ci_95' : [3, 4, 5, 6, 7],
        'lower_ci_95' : [0, 1, 2, 3, 4]
    })

    model = EvaluateModel("timestamp_true", "timestamp_pred", "target_true", "target_pred", "upper_ci_95", "lower_ci_95")

    # Call the method and get the evaluation DataFrame
    evaluation_df = model.make_evaluation(df_real, df_pred, "id_pred", verbose=False)

    # Check if the evaluation DataFrame has the correct columns
    assert all(col in evaluation_df.columns for col in ['id_pred', 'MAE', 'MAPE', 'RMSE', 'MSE', 'R2', 'Percentage Coverage'])

    # Check if the 'id_pred' column contains the correct value
    assert evaluation_df['id_pred'][0] == 'id_pred'

    # Check if the evaluation metrics are calculated correctly (assuming you know the expected results)
    assert np.isclose(evaluation_df['MAE'][0], 0.2, atol=1e-2)
    assert np.isclose(evaluation_df['MAPE'][0], 0.05, atol=1e-2)
    assert np.isclose(evaluation_df['RMSE'][0], 0.32, atol=1e-2)
    assert np.isclose(evaluation_df['MSE'][0], 0.1, atol=1e-2)
    assert np.isclose(evaluation_df['R2'][0], 0.95, atol=1e-2)

    print(evaluation_df['Percentage Coverage'][0])

    # Assuming you have the expected percentage coverage value for this specific example
    # Replace 'expected_percentage_coverage' with the actual expected value for your data
    expected_percentage_coverage = 100  # For example, 100%
    assert np.isclose(evaluation_df['Percentage Coverage'][0], expected_percentage_coverage, atol=1e-2)









