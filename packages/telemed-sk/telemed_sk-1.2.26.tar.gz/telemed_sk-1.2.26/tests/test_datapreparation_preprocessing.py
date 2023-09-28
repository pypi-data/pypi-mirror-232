import sys
import pytest
import pandas as pd
import warnings
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])

from TeleMed.telemed_sk.datapreparation.preprocessing import PreprocessingClass


def sample_data_hier():
    data = {
        "date_col": pd.date_range("2023-07-01", periods=5, freq="D"),
        "zone": ["North", "North", "South", "South", "West"],
        "city": ["Milan", "Turin", "Rome", "Naples", "Florence"],
        'target_col': ['a','a','b', 'c', 'd']
    }
    return pd.DataFrame(data)

def test_PreprocessingClass_TCPreprocess():
    # Test PreprocessingClass with TCPreprocess
    usecase = "teleconsulto"
    model = "prophet"

    hierarchy = {
        "level_1": "zone",
        "level_2": "city"
    }

    conversion = {
        "level_1": None,
        "level_2": None
    }

    target_col = "target_col"
    time_granularity = "D"
    date_col = "date_col"
    missing_data_strategy = "mean"

    # Sample data for testing
    df = sample_data_hier()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        preprocessor = PreprocessingClass(
            usecase,
            model,
            hierarchy=hierarchy,
            conversion=conversion,
            target_col=target_col,
            time_granularity=time_granularity,
            date_col=date_col,
            missing_data_strategy=missing_data_strategy
        )

        # Test transform method
        # The checks on these results are already performed in other tests
        Y_df, S_df, tags = preprocessor.transform(df)
        assert type(Y_df) == pd.DataFrame
        assert type(S_df) == pd.DataFrame
        assert type(tags) == dict
 

def test_PreprocessingClass_TVPreprocess():
    # Test PreprocessingClass with TVPreprocess
    # TV doesn't aplly anything, it should only apply Prophet processing

    usecase = "televisita"
    model = "prophet"
    hierarchy = {
        "level_1": "zone",
        "level_2": "city"
    }

    conversion = {
        "level_1": None,
        "level_2": None
    }

    time_granularity = "D"
    date_col = "date_col"
    missing_data_strategy = "mean"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        preprocessor = PreprocessingClass(
                usecase,
                model,
                hierarchy=hierarchy,
                conversion=conversion,
                time_granularity=time_granularity,
                date_col=date_col,
                missing_data_strategy=missing_data_strategy
            )

        df = sample_data_hier()

        # TVPreprocess transform should return the DataFrame unchanged
        Y_df, S_df, tags = preprocessor.transform(df)
    assert type(Y_df) == pd.DataFrame
    assert type(S_df) == pd.DataFrame
    assert type(tags) == dict

def test_PreprocessingClass_TAPreprocess():
    # Test PreprocessingClass with TAPreprocess
    # TV doesn't aplly anything, it should only apply Prophet processing

    usecase = "teleassistenza"
    model = "prophet"
    hierarchy = {
        "level_1": "zone",
        "level_2": "city"
    }

    conversion = {
        "level_1": None,
        "level_2": None
    }

    time_granularity = "D"
    date_col = "date_col"
    missing_data_strategy = "mean"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        preprocessor = PreprocessingClass(
                usecase,
                model,
                hierarchy=hierarchy,
                conversion=conversion,
                time_granularity=time_granularity,
                date_col=date_col,
                missing_data_strategy=missing_data_strategy
            )

        df = sample_data_hier()

        # TAPreprocess transform should return the DataFrame unchanged
        Y_df, S_df, tags = preprocessor.transform(df)
    assert type(Y_df) == pd.DataFrame
    assert type(S_df) == pd.DataFrame
    assert type(tags) == dict

def test_PreprocessingClass_TMPreprocess():
    # Test PreprocessingClass with TMPreprocess
    # TM doesn't aplly anything, it should only apply Prophet processing

    usecase = "telemonitoraggio"
    model = "prophet"
    hierarchy = {
        "level_1": "zone",
        "level_2": "city"
    }

    conversion = {
        "level_1": None,
        "level_2": None
    }

    time_granularity = "D"
    date_col = "date_col"
    missing_data_strategy = "mean"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        preprocessor = PreprocessingClass(
                usecase,
                model,
                hierarchy=hierarchy,
                conversion=conversion,
                time_granularity=time_granularity,
                date_col=date_col,
                missing_data_strategy=missing_data_strategy
            )

        df = sample_data_hier()

        # TMPreprocess transform should return the DataFrame unchanged
        Y_df, S_df, tags = preprocessor.transform(df)
    assert type(Y_df) == pd.DataFrame
    assert type(S_df) == pd.DataFrame
    assert type(tags) == dict


class ExitException(Exception):
    pass

def my_exit(status=None):
    raise ExitException(f"SystemExit with status: {status}")

def test_PreprocessingClass_InvalidUsecase(monkeypatch):
    # Test PreprocessingClass with an invalid usecase

    usecase = "invalid_usecase"
    model = "prophet"

    # Patch sys.exit with a custom function
    monkeypatch.setattr(sys, "exit", my_exit)

    with pytest.raises(Exception):
        PreprocessingClass(usecase, model)

def test_PreprocessingClass_InvalidModel(monkeypatch):
    # Test PreprocessingClass with an invalid model

    usecase = "televisita"
    model = "invalid_model"

    # Patch sys.exit with a custom function
    monkeypatch.setattr(sys, "exit", my_exit)
    with pytest.raises(Exception):
        PreprocessingClass(usecase, model)









