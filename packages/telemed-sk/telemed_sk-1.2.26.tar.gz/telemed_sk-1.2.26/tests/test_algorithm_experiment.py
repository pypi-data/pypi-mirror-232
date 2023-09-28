import pytest
import sys
import pandas as pd
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])
from TeleMed.telemed_sk.algorithms.experiment import ExperimentClass
from TeleMed.telemed_sk.algorithms.models import ProphetModel

# This class wraps a model class and performs its methods
# we will just try its behaviour with 'prophet' without checking what it has been checked in test_algorithm_models.py


## test ExperimentClass __init__ ##
def sample_params():
    return {
        'seasonality_prior_scale' :  {'min' : 0.01, 'max' : 10.0, 'step' : 'None'},
        'weekly_seasonality' : ['True']
    }

class ExitException(Exception):
    pass

def my_exit(status=None):
    raise ExitException(f"SystemExit with status: {status}")

def test_prophet_model_creation():
    model = "prophet"
    params = sample_params()
    config_path = "./config/config_check"

    experiment = ExperimentClass(model, params, config_path)

    assert experiment.model_name == "prophet"
    assert experiment.config_path == config_path
    assert isinstance(experiment.Model, ProphetModel)

def test_invalid_model_creation(monkeypatch):
    model = "invalid_model"
    params = sample_params()
    config_path = "./config/config_check"

    # Patch sys.exit with a custom function
    monkeypatch.setattr(sys, "exit", my_exit)

    with pytest.raises(ExitException):
        ExperimentClass(model, params, config_path)
    

## test ExperimentClass fit ##
# In this test, since we already tested the fit method in test_algorithms_models.py
# we can test the check_consistency method
def create_data():
    unique_ids_train = ['a'] * 20 + ['a/b'] * 20 + ['a/c'] * 20 + ['a/d'] * 20
    unique_ids_val = ['a'] * 10 + ['a/b'] * 10 + ['a/c'] * 10 + ['a/d'] * 10

    # Creazione delle date con ripetizioni ogni 20 giorni per train_data e ogni 10 giorni per val_data
    ds_train = pd.date_range(start='2023-01-01', periods=20, freq='20D').repeat(4)
    ds_val = pd.date_range(start='2023-01-06', periods=10, freq='10D').repeat(4)

    y_train = list(range(1, 61))
    y_train += [0]*20
    y_val = list(range(61, 91))
    y_val += [0]*10

    # Creazione dei DataFrame train_data e val_data
    train_data = pd.DataFrame({'unique_id': unique_ids_train, 'ds': ds_train, 'y': y_train})
    val_data = pd.DataFrame({'unique_id': unique_ids_val, 'ds': ds_val, 'y': y_val})

    # Reorder columns
    train_data = train_data[['unique_id', 'ds', 'y']]
    val_data = val_data[['unique_id', 'ds', 'y']]

    train_data = train_data.set_index('unique_id')
    val_data = val_data.set_index('unique_id')
    train_data = train_data.sort_index()
    val_data = val_data.sort_index()
    return train_data, val_data

def test_experiment_fit():
    ## Test correct input for fit
    train_data, val_data = create_data()

    model = "prophet"
    params = sample_params()
    config_path = "./config/config_check"

    experiment = ExperimentClass(model, params, config_path)
    experiment.fit(train_data, val_data)

    ## Test not correct input for fit
    train_data.columns = ['timestamp', 'y']
    with pytest.raises(Exception):
        experiment.fit(train_data, val_data)

## test ExperimentClass predict ##
# we check that the output is a dataframe since its properties are already checked in test_algorithm_models.py
def test_experiment_predict():
    train_data, val_data = create_data()

    model = "prophet"
    params = sample_params()
    config_path = "./config/config_check"

    experiment = ExperimentClass(model, params, config_path)
    experiment.fit(train_data, val_data)
    out = experiment.predict(val_data)
    assert type(out) == pd.DataFrame

## test ExperimentClass score ##
# we check the output format since its properties are already checked in test_algorithm_models.py
def test_experiment_score():
    train_data, val_data = create_data()

    model = "prophet"
    params = sample_params()
    config_path = "./config/config_check"

    experiment = ExperimentClass(model, params, config_path)
    experiment.fit(train_data, val_data)
    val_output = experiment.predict(val_data)

    scores_aggr, scores = experiment.score(val_data, val_output)
    
    assert type(scores_aggr) == pd.Series
    assert type(scores) == pd.DataFrame


## test ExperimentClass create_hyperparameters_table ##
# we check the output format since its properties are already checked in test_algorithm_models.py
def test_create_hyperparameters_table():
    ## Test correct input for fit
    train_data, val_data = create_data()

    model = "prophet"
    params = sample_params()
    config_path = "./config/config_check"

    experiment = ExperimentClass(model, params, config_path)
    experiment.fit(train_data, val_data)

    p = experiment.create_hyperparameters_table(params)

    assert type(p) == dict    
    p['a_d'] = {}
    for idx, param in p.items():
        reference_params = experiment.Model.models_best_params
        assert param == reference_params[idx.replace('_','/')]
       




