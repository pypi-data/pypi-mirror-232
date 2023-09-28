import pandas as pd
import pytest
import numpy as np
import sys
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])

from TeleMed.telemed_sk.datapreparation.utils import (Normalizer, ReplacerNA, Detrender, Deseasoner, Differencer, 
                                           OutlierRemover, Smoother, Differentiator, LogTransformer,
                                           map_columns, get_hierarchical_df, get_hierarchical_info, missing_data_imputation, column_to_int, completing_calendar, filter_target_col)
from statsmodels.tsa.seasonal import seasonal_decompose
from TeleMed.telemed_sk.datapreparation.utils import datepart,get_hierarchy_column,divide_by_father,get_lagged_column

### Normalizer ###
@pytest.fixture
def example_data():
    # Example data for testing
    data = pd.DataFrame({'volumes': [10, 20, 30, 40, 50]})
    return data

def test_fit_normalizer(example_data):
    # Create an instance of the Normalizer class
    normalizer = Normalizer()

    # Call the fit method with the example data
    fitted_normalizer = normalizer.fit(example_data)

    # Verify that the output is the same instance of normalizer
    assert fitted_normalizer is normalizer

    # Verify that the min and max values are calculated correctly
    assert normalizer.min == 10
    assert normalizer.max == 50

def test_transform_normalizer(example_data):
    # Create an instance of the Normalizer class
    normalizer = Normalizer()

    # Call the fit method with the example data
    normalizer.fit(example_data)

    # Call the transform method with the example data
    transformed_data = normalizer.transform(example_data)

    # Verify that the output is a DataFrame
    assert isinstance(transformed_data, pd.DataFrame)

    # Verify that the DataFrame has the correct columns
    assert transformed_data.columns.tolist() == ['volumes']

    # Verify that the data is correctly normalized
    assert transformed_data['volumes'].min() == 0
    assert transformed_data['volumes'].max() == 1

def test_inverse_transform_normalizer(example_data):
    normalizer = Normalizer()

    # Call the fit method with the example data
    normalizer.fit(example_data)

    # Call the transform method with the example data
    transformed_data = normalizer.transform(example_data)

    data = normalizer.inverse_transform(transformed_data)
    assert np.min(data) == normalizer.min
    assert np.max(data) == normalizer.max

### ReplacerNA ###
#transform function
@pytest.fixture
def example_data_transform():
    # Example data for testing
    data = pd.DataFrame({'timestamp': [1, 2, 3, 4, 5],
                         'volumes': [10, None, 30, None, 50]})
    return data

def test_fit_replace_na(example_data_transform):
    # Create an instance of the ReplacerNA class with method="mean"
    replacer = ReplacerNA(method="mean")

    # Call the fit method with the example data
    fitted_replacer = replacer.fit(example_data_transform)

    # Verify that the output is the same instance of replacer
    assert fitted_replacer is replacer

    # Verify that the value and method_for_df are calculated correctly
    assert replacer.value == 30.0
    assert replacer.method_for_df is None

def test_transform_replace_na(example_data_transform):
    # Create an instance of the ReplacerNA class with method="zero"
    replacer = ReplacerNA(method="zero")

    # Call the fit method with the example data
    replacer.fit(example_data_transform)

    # Call the transform method with the example data
    transformed_data = replacer.transform(example_data_transform)
    print(transformed_data)
    # Verify that the output is a DataFrame
    assert isinstance(transformed_data, pd.DataFrame)

    # Verify that the transformed data has missing values replaced correctly
    expected_data = pd.DataFrame({'timestamp': [1, 2, 3, 4, 5],
                                  'volumes': [10.0, 0.0, 30.0, 0.0, 50.0]})
    pd.testing.assert_frame_equal(transformed_data, expected_data)

def test_transform__replace_na_ffill(example_data_transform):
    # Create an instance of the ReplacerNA class with method="ffill"
    replacer = ReplacerNA(method="ffill")

    # Call the fit method with the example data
    replacer.fit(example_data_transform)

    # Call the transform method with the example data
    transformed_data = replacer.transform(example_data_transform)

    # Verify that the transformed data has missing values replaced correctly using forward fill
    expected_data = pd.DataFrame({'timestamp': [1, 2, 3, 4, 5],
                                  'volumes': [10.0, 10.0, 30.0, 30.0, 50.0]})
    pd.testing.assert_frame_equal(transformed_data, expected_data)


### Detrender ###
#trend function
@pytest.fixture
def example_data_trend():
    # Example data for testing
    data = pd.DataFrame({'timestamp': [1, 2, 3, 4, 5],
                         'volumes': [10, 20, 30, 40, 50]})
    return data

def test_fit_detrender(example_data_trend):
    # Create an instance of the Detrender class with period=2
    detrender = Detrender(period=2)

    # Call the fit method with the example data
    fitted_detrender = detrender.fit(example_data_trend)

    # Verify that the output is the same instance of detrender
    assert fitted_detrender is detrender

    # Verify that the trend is calculated correctly
    expected_trend = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0], name='trend')
    pd.testing.assert_series_equal(detrender.trend, expected_trend)

def test_transform_detrender(example_data_trend):
    # Create an instance of the Detrender class with period=2
    detrender = Detrender(period=2)

    # Call the fit method with the example data
    detrender.fit(example_data_trend)

    # Call the transform method with the example data
    transformed_data = detrender.transform(example_data_trend)

    # Verify that the output is a DataFrame
    assert isinstance(transformed_data, pd.DataFrame)

    # Verify that the transformed data is detrended correctly
    expected_trend = seasonal_decompose(example_data_trend['volumes'], model='additive', period=2, extrapolate_trend='freq').trend
    expected_data = pd.DataFrame({'timestamp': [1, 2, 3, 4, 5],
                                  'volumes': example_data_trend['volumes'] - expected_trend})
    pd.testing.assert_frame_equal(transformed_data, expected_data)


### Deseasoner ###
#season function
@pytest.fixture
def example_data_season():
    # Example data for testing
    data = pd.DataFrame({'timestamp': [1, 2, 3, 4, 5],
                         'volumes': [10, 20, 30, 40, 50]})
    return data

def test_transform_deseasoner(example_data_season):
    # Create an instance of the Deseasoner class with period=2
    deseasoner = Deseasoner(period=2)

    # Call the fit method with the example data
    deseasoner.fit(example_data_season)

    # Call the transform method with the example data
    transformed_data = deseasoner.transform(example_data_season)

    # Verify that the output is a DataFrame
    assert isinstance(transformed_data, pd.DataFrame)

    # Verify that the transformed data is deseasonalized correctly
    expected_seasonal = seasonal_decompose(example_data_season['volumes'], model='additive', period=2, extrapolate_trend='freq').seasonal
    expected_data = pd.DataFrame({'timestamp': [1, 2, 3, 4, 5],
                                  'volumes': example_data_season['volumes'] - expected_seasonal})
    pd.testing.assert_frame_equal(transformed_data, expected_data)


### Differencer ###
#difference function
@pytest.fixture
def example_data_difference():
    # Example data for testing
    data = pd.DataFrame({'timestamp': [1, 2, 3, 4, 5],
                         'volumes': [10, 20, 30, 40, 50]})
    return data

def test_transform_differencer(example_data_difference):
    # Create an instance of the Differencer class with lag=1
    differencer = Differencer(lag=1)

    # Call the fit method with the example data
    differencer.fit(example_data_difference)

    # Call the transform method with the example data
    transformed_data = differencer.transform(example_data_difference)

    # Verify that the output is a DataFrame
    assert isinstance(transformed_data, pd.DataFrame)

    # Verify that the transformed data is differenced correctly
    expected_data = pd.DataFrame({'timestamp': [2, 3, 4, 5],
                                  'volumes': [10, 10, 10, 10]})
    pd.testing.assert_frame_equal(transformed_data, expected_data)

### OutlierRemover ###
@pytest.fixture
def sample_data_outlier():
    return np.array([10, 15, 20, 25, 30, 100, 200, 300])

def test_outlier_removal(sample_data_outlier):
    lower_threshold_percentile = 5
    upper_threshold_percentile = 95
    outlier_remover = OutlierRemover(lower_threshold_percentile, upper_threshold_percentile)

    # Sample data with outliers
    data = sample_data_outlier

    # Fit the outlier remover on the data
    outlier_remover.fit(data)

    # Transform the data by capping the outliers
    transformed_data = outlier_remover.transform(data)

    # Check if the transformed data has no outliers
    assert np.all(transformed_data >= 10)  # Values are not below the lower threshold
    assert np.all(transformed_data <= 300)  # Values are not above the upper threshold
    assert np.all(transformed_data == data)  # The original non-outlier data remains unchanged


### Smoother ###
@pytest.fixture
def sample_data_smoother():
    # Sample data for testing
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    return pd.Series(data)

def test_smoother_transform(sample_data_smoother):
    window_size = 3
    smoother = Smoother(window_size)

    # Sample data for testing
    data = sample_data_smoother

    # Fit the smoother (not necessary in this case)
    smoother.fit(data)

    # Transform the data using the moving average window
    transformed_data = smoother.transform(data)

    # Expected smoothed data using the given window size (calculated manually)
    expected_smoothed_data = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

    # Check if the transformed data matches the expected smoothed data
    assert np.allclose(transformed_data, expected_smoothed_data)

### Differenciator ###
@pytest.fixture
def sample_data_diff():
    # Sample data for testing
    data = np.array([1, 4, 6, 9, 12, 15])
    return pd.Series(data)

def test_differentiator_transform(sample_data_diff):
    order = 2
    differentiator = Differentiator(order)

    # Sample data for testing
    data = sample_data_diff

    # Fit the differentiator (not necessary in this case)
    differentiator.fit(data)

    # Transform the data by taking differences between consecutive values (twice in this case)
    transformed_data = differentiator.transform(data)

    # Expected differentiated data using the given order (calculated manually)
    expected_transformed_data = [0., 0., -1., 1., 0., 0.]

    # Check if the transformed data matches the expected differentiated data
    assert np.allclose(transformed_data, expected_transformed_data)


### LogTransformer ###
@pytest.fixture
def sample_data_log():
    # Sample data for testing
    data = np.array([1, 2, 3, 4, 5])
    return data

def test_log_transformer_transform(sample_data_log):
    transformer = LogTransformer()

    # Sample data for testing
    data = sample_data_log

    # Fit the transformer (not necessary in this case)
    transformer.fit(data)

    # Transform the data using the logarithmic transformation
    transformed_data = transformer.transform(data)

    # Expected transformed data (calculated manually)
    expected_transformed_data = [0.69314718, 1.09861229, 1.38629436, 1.60943791, 1.79175947]

    # Check if the transformed data matches the expected transformed data
    assert np.allclose(transformed_data, expected_transformed_data)

def test_log_transformer_inverse_transform(sample_data_log):
    transformer = LogTransformer()

    # Sample transformed data for testing
    transformed_data = [0.69314718, 1.09861229, 1.38629436, 1.60943791, 1.79175947]

    # Fit the transformer (not necessary in this case)
    transformer.fit(sample_data_log)

    # Inverse transform the data using the inverse logarithmic transformation
    reconstructed_data = transformer.inverse_transform(transformed_data)

    # Check if the reconstructed data matches the original data
    assert np.allclose(reconstructed_data, sample_data_log)



### Test Other Utils ###

## test map_columns ##
def sample_data():
    # Sample data for testing
    data = {
        "column_a": [1, 2, 3],
        "column_b": [4, 5, 6],
        "column_c": [7, 8, 9]
    }
    return pd.DataFrame(data)

def test_map_columns():
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

    # Sample data for testing
    df = sample_data()

    # Map the columns using the given hierarchy and conversion dictionaries
    mapped_df = map_columns(hierarchy, df, conversion)

    # Check if the mapped DataFrame has the correct column names
    assert "column_a" in mapped_df.columns
    assert "column_b" in mapped_df.columns
    assert "column_c" in mapped_df.columns

    # Check if the columns were correctly mapped based on the conversion dictionary
    assert mapped_df["column_c"].tolist() == ['seven', 'eight', 'nine']

## test column_to_int
def sample_data_():
    # Sample data for testing
    data = {
        "column_a": [1, 2, 3],
        "column_b": [4, 5, 6],
        "column_c": ['7', '8', '9']
    }
    return pd.DataFrame(data)

def test_column_to_int():

    hierarchy = {
        "level_1": "column_a",
        "level_2": "column_b",
        "level_3": "column_c"
    }
    conversion = {
        "level_1": None,
        "level_2": None,
        "level_3": "{'7': 'seven', '8': 'eight', '9': 'nine'}"
    }

    # Sample data for testing
    df = sample_data_()

    out_df = column_to_int(hierarchy, df, conversion)
    assert out_df['column_c'].dtype == int

## test get_hierarchical_df ##
def sample_data_hier():
    # Sample data for testing
    data = {
        "date_col": pd.date_range("2023-07-01", periods=5, freq="D"),
        "zone": ["North", "North", "South", "South", "West"],
        "city": ["Milan", "Turin", "Rome", "Naples", "Florence"]
    }
    return pd.DataFrame(data)

import warnings
def test_get_hierarchical_df():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hierarchy = {
            "level1": "zone",
            "level2": "city"
        }
        time_granularity = "D"
        date_col = "date_col"

        # Sample data for testing
        df = sample_data_hier()

        # Generate the hierarchical DataFrame using the given hierarchy and time_granularity
        hierarchical_df = get_hierarchical_df(df, hierarchy, time_granularity, date_col)

    # Check if the hierarchical DataFrame has the expected columns
    expected_columns = ["ds", "y", "level0", "level1", "level2"]
    for col in hierarchical_df.columns:
        assert col in expected_columns

    # Check if level0 is set as "Italia" for all observations
    assert hierarchical_df["level0"].unique() == ["Italia"]

    # Check if y is set as 1 for all observations
    assert hierarchical_df["y"].unique() == [1]

    # Check if the time_granularity is correctly applied
    assert pd.infer_freq(hierarchical_df["ds"]) == time_granularity


## test get_hierarchical_INFO ##
def test_get_hierarchical_info():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hierarchy = {
            "level1": "zone",
            "level2": "city"
        }
        time_granularity = "D"
        date_col = "date_col"

        # Sample data for testing
        df = sample_data_hier()

        # Generate the hierarchical DataFrame using the given hierarchy and time_granularity
        hierarchical_df = get_hierarchical_df(df, hierarchy, time_granularity, date_col)
        Y_df, S_df, tags = get_hierarchical_info(hierarchical_df)

        
        # Check the tags consistency
        reference_tags = {'level0': np.array(['Italia'], dtype=object), 'level0/level1': np.array(['Italia/North', 'Italia/South', 'Italia/West'], dtype=object), 
         'level0/level1/level2': np.array(['Italia/North/Milan', 'Italia/North/Turin', 'Italia/South/Naples', 'Italia/South/Rome', 'Italia/West/Florence'])}
        for k,v in tags.items():
            assert np.all(v == reference_tags[k])

        # Check is S_df is a binary matrix
        S_array = S_df.to_numpy()
        assert np.all(np.logical_or(S_array == 0, S_array == 1))

        # Check Y_df consistency
        # the number of rows must be given by len(date_col) * (num_possible_hierarchies + 1 (Italy))
        assert Y_df.shape[0] == len(hierarchical_df['ds']) * S_df.shape[0]


## test missing_data_imputation ##
def sample_data_missing():
    # Sample data for testing
    data = {
        "date_col": pd.date_range("2023-07-01", periods=5, freq="D"),
        "y": [1, None, 3, 4, None],
        "other_column": [5, 6, None, 8, 9],
    }
    return pd.DataFrame(data)

def test_missing_data_imputation_mean():
    # Test missing data imputation with strategy "mean"

    strategy = "mean"

    # Sample data for testing
    df = sample_data_missing()

    # Impute missing values using the mean strategy
    imputed_df = missing_data_imputation(strategy, df)
    # Check if missing values in the 'y' column are replaced with the mean
    assert np.allclose(np.array(imputed_df["y"],dtype='float'), [1, 2.67, 3, 4, 2.67], rtol = 0.01)

def test_missing_data_imputation_spline():
    # Test missing data imputation with strategy "spline"

    strategy = {"interpolation": "spline", "order": 2}

    # Sample data for testing
    df = sample_data_missing()

    # Impute missing values using the spline strategy
    imputed_df = missing_data_imputation(strategy, df)
    
    # Check if the 'y' column is correctly imputed using the spline method
    assert np.allclose(np.array(imputed_df["y"],dtype='float'), [1, 2, 3, 4, 5], rtol = 0.01)

## test completing_calendar ##
def test_complete_calendar_daily():
    data = {'ds': pd.date_range(start='2023-01-01', end='2023-01-05', freq='D'),
            'y': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    
    result_df = completing_calendar(df, time_granularity='D')
    
    expected_dates = pd.date_range(start='2023-01-01', end='2023-01-05', freq='D')
    assert result_df['ds'].tolist() == expected_dates.tolist()
    assert result_df['y'].tolist() == [1, 2, 3, 4, 5]

def test_incomplete_calendar_daily():
    data = {'ds': pd.to_datetime(['2023-08-01', '2023-08-03', '2023-08-04']),
            'y': [10, 20, 30],
            'unique_id' : ['a']*3}
    df = pd.DataFrame(data)
    df = df.set_index('unique_id')
    result_df = completing_calendar(df, time_granularity='D')
    
    expected_dates = pd.date_range(start='2023-08-01', end='2023-08-04', freq='D')
    assert result_df['ds'].tolist() == expected_dates.tolist()
  

##test filter_target_col ##
def test_filter_target_col():
    data = {'A': [1, 2, 3, 1, 2],
            'B': [10, 20, 30, 40, 50]}
    df = pd.DataFrame(data)
    
    result_df = filter_target_col(df, target_col='A')
    
    expected_data = {'A': [1, 2, 3],
                     'B': [10, 20, 30]}
    expected_df = pd.DataFrame(expected_data)
    
    pd.testing.assert_frame_equal(result_df, expected_df)
    
######## Test for xgboost pre-processing ##########################
@pytest.fixture
def datepart_data():

    dates = pd.Series(['2022-01-01 12:00:00', '2022-01-02 18:00:00'])

    dates_true = pd.DataFrame([[1,5,1,2022,1,1,True,True],[2,6,2,2022,1,1,False,True]],
                               columns=["dayofmonth","dayofweek","dayofyear","year","month","quarter","holiday","weekend"],
                               index=['2022-01-01 12:00:00', '2022-01-02 18:00:00'],dtype=np.int32)
    dates_true = dates_true.astype(dtype={"holiday":bool,"weekend":bool})

    return [(dates,dates_true)]

def test_datepart(datepart_data):

    for dates,df in datepart_data:
        assert datepart(dates).equals(df)


@pytest.mark.parametrize('n, length', [(1,1),(2,1),(3,2)])
def test_get_hierarchy_column(n,length):

    df = pd.DataFrame([["A",2022,10],["A/B",2022,5],["A/C",2022,5],["A/B/B1",2022,2],["A/B/B2",2022,3],["A/C/C1",2022,5],
                   ["A/B/B1/B1.1",2022,1],["A/B/B1/B1.2",2022,1],["A/B/B2/B2.1",2022,1],["A/B/B2/B2.2",2022,1],["A/B/B2/B2.3",2022,1]],
                  columns = ["Id","date","pred"])
    
    # livello con father == livello precedente con figli
    lev1 = get_hierarchy_column(df,"date","pred","Id",n+1,sons=False,father=True,type_="COL")
    lev2 = get_hierarchy_column(df,"date","pred","Id",n,sons=True,father=False,type_="COL")
    for i,j in zip(lev1,lev2):
        assert i.equals(j)

    # lunghezza lista (se primo livello -- len sempre 1)
    assert len(get_hierarchy_column(df,"date","pred","Id",n,sons=False,father=True,type_="COL")) == length
    assert len(get_hierarchy_column(df,"date","pred","Id",1,sons=True,father=True,type_="COL")) == 1

    data = get_hierarchy_column(df,"date","pred","Id",n,sons=False,father=True,type_="COL")
    data_real = []

    check_df = []
    for i,j in zip(data,data_real):
        check_df += [i.equals(j)]
    
    assert all(check_df)


@pytest.fixture
def divide_by_father_data():
    
    data = {'A/B': [3, 3, 3], 'A/C': [4, 5, 6], 'A': [7, 8, 9]}
    df = pd.DataFrame(data)

    df_real = pd.DataFrame([[0.428571,0.571429,7],[0.375000,0.625000,8],[0.333333,0.666667,9]],
                           columns=["A/B","A/C","A"])
    
    return [(df,df_real)]
    
def test_divide_by_father(divide_by_father_data):

    for df,df_real in divide_by_father_data:
        df_div = divide_by_father(df)
        pd.testing.assert_frame_equal(df_div,df_real)
        pd.testing.assert_series_equal(df_div.iloc[:,:-1].sum(axis=1),pd.Series([1. for i in range(df.shape[0])]))

@pytest.fixture
def get_lagged_column_data():
    
    data = {'A': [1, 2, 3, 4], 'B': [5, 6, 7, 8]}
    df = pd.DataFrame(data)

    df_real = pd.DataFrame([[np.nan,np.nan],[1,np.nan],[2,1],[3,2]],
                           columns=["Lag1_A","Lag2_A"])
    
    return [(df,df_real)]
    
def test_get_lagged_column(get_lagged_column_data):

    for df,df_real in get_lagged_column_data:
        df_lag = get_lagged_column(df,[1,2],"A")
        pd.testing.assert_frame_equal(df_lag,df_real)






