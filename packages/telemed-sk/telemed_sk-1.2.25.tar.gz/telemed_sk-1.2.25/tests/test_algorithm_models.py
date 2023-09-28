from itertools import chain
import pytest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import sys
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])
from TeleMed.telemed_sk.algorithms.models import *
from hierarchicalforecast.methods import BottomUp

# --------- ProphetModel Tests --------- #
## test ProphetModel __init__ ##
# The __init__ test also the method make_grid_params 
@pytest.fixture
def sample_params():
    return {'weekly_seasonality' : ['True'],
            'yearly_seasonality' : ['True']
}

def test_prophet_model_init(sample_params):
    config_path = "./config/config_check"
    max_na_ratio = 0.3
    model = ProphetModel(sample_params, config_path, max_na_ratio)

    assert model.config_path == config_path
    assert model.max_na_ratio == max_na_ratio
    assert model.grid_params is not None
    assert model.grid_params == {'weekly_seasonality' : [True], 
                                 'yearly_seasonality' : [True],
                                 'interval_width' : [0.95]}

##  test ProphetModel fit method ##
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
    return train_data, val_data

def test_prophet_model_fit():
    config_path = "./config/config_check"
    max_na_ratio = 0.3
    params = {'weekly_seasonality' : ['True'],
            'yearly_seasonality' : ['True']}
    reference_params = {'weekly_seasonality' : True, 
                                 'yearly_seasonality' : True,
                                 'interval_width' : 0.95}
    model = ProphetModel(params, config_path, max_na_ratio)

    train_data, val_data = create_data()

    # Specificare il numero di ripetizioni desiderate
    num_repetitions = 20

    # Creazione dei DataFrame con più righe
    train_data = pd.concat([train_data] * num_repetitions)
    val_data = pd.concat([val_data] * num_repetitions)

    train_data = train_data.set_index('unique_id')
    val_data = val_data.set_index('unique_id')
    train_data = train_data.sort_index()
    val_data = val_data.sort_index()

    # Call the fit method
    model.fit(train_data, val_data)

    # Check if models_dict and models_best_params are populated
    assert model.models_dict != {}
    assert model.models_best_params != {}
    for k, best_param in model.models_best_params.items():
        if k != 'a/d':
            assert best_param == reference_params
        else:
            assert best_param == {}

## test ProphetModel refit method ##
def test_prophet_model_refit():
    # first fit
    config_path = "./config/config_check"
    max_na_ratio = 0.3
    params = {'weekly_seasonality' : ['True'],
            'yearly_seasonality' : ['True']}
    reference_params = {'weekly_seasonality' : True, 
                                 'yearly_seasonality' : True,
                                 'interval_width' : 0.95}
    model = ProphetModel(params, config_path, max_na_ratio)

    train_data, val_data = create_data()

    # Specificare il numero di ripetizioni desiderate
    num_repetitions = 20

    # Creazione dei DataFrame con più righe
    train_data = pd.concat([train_data] * num_repetitions)
    val_data = pd.concat([val_data] * num_repetitions)

    train_data = train_data.set_index('unique_id')
    val_data = val_data.set_index('unique_id')
    train_data = train_data.sort_index()
    val_data = val_data.sort_index()

    # Call the fit method
    model.fit(train_data, val_data)

    # Then refit
    model.refit(train_data)

    # Check if models_dict and models_best_params are populated
    assert model.models_dict != {}
    assert model.models_best_params != {}
    for k, best_param in model.models_best_params.items():
        if k != 'a/d':
            assert best_param == reference_params
        else:
            assert best_param == {}

## test ProphetModel predict method ##
# The function checks also the method prepare_output
def test_prophet_model_predict():
    # first fit
    config_path = "./config/config_check"
    max_na_ratio = 0.3
    params = {'weekly_seasonality' : ['True'],
            'yearly_seasonality' : ['True']}
   
    model = ProphetModel(params, config_path, max_na_ratio)

    train_data, val_data = create_data()

    # Specificare il numero di ripetizioni desiderate
    num_repetitions = 20

    # Creazione dei DataFrame con più righe
    train_data = pd.concat([train_data] * num_repetitions)
    val_data = pd.concat([val_data] * num_repetitions)

    train_data = train_data.set_index('unique_id')
    val_data = val_data.set_index('unique_id')
    train_data = train_data.sort_index()
    val_data = val_data.sort_index()

    # Call the fit method
    model.fit(train_data, val_data)

    # Then predict
    output = model.predict(val_data)

    # Assert output columns
    assert np.all(output.columns == ['timestamp', 'id_pred' , 'pred_mean'  ,'sigma',  'pi_lower_95' , 'pi_upper_95'])
    
    # Assert id_pred consistency
    assert np.all(output['id_pred'].unique() == ['a', 'a/b', 'a/c', 'a/d'])

    # Assert predictions for 'a/d'
    for col in ['pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']:
        assert  np.all(output[output['id_pred'] == 'a/d'][col] == 0)

## test ProphetModel score method ## 
def test_prophet_model_score():
    # Obtain predictions
    config_path = "./config/config_check"
    max_na_ratio = 0.3
    params = {'weekly_seasonality' : ['True'],
            'yearly_seasonality' : ['True']}
   
    model = ProphetModel(params, config_path, max_na_ratio)

    train_data, val_data = create_data()

    # Specificare il numero di ripetizioni desiderate
    num_repetitions = 20

    # Creazione dei DataFrame con più righe
    train_data = pd.concat([train_data] * num_repetitions)
    val_data = pd.concat([val_data] * num_repetitions)

    train_data = train_data.set_index('unique_id')
    val_data = val_data.set_index('unique_id')
    train_data = train_data.sort_index()
    val_data = val_data.sort_index()

    # Call the fit method
    model.fit(train_data, val_data)

    # Then predict
    df_pred = model.predict(val_data)

    # Then score
    score = model.score(val_data, df_pred)
    
    # Assert score columns
    assert np.all(score.columns == ['id_pred', 'MAE', 'MAPE', 'RMSE', 'MSE', 'R2', 'Percentage Coverage'])


# --------- HierarchicalReconcileMethod Tests --------- #
## test HierarchicalReconcileMethod __init__ ##
def sample_data():
    model_name = "test_model"
    S = pd.DataFrame({
        "column1": [1, 2, 3, 4, None],
        "column2": [10, 20, None, 40, 50]
    })
    tags = {"tag1": ["column1", "column2"]}
    reconciler = None
    max_na_ratio = 0.5

    return model_name, S, tags, reconciler, max_na_ratio

def test_init_with_none_reconciler():
    model_name, S, tags, reconciler, max_na_ratio = sample_data()
    model = HierarchicalReconcileModel(model_name, S, tags, reconciler, max_na_ratio)

    assert model.model_name == model_name
    assert model.S.equals(S)
    assert model.tags == tags
    assert model.max_na_ratio == max_na_ratio

def test_init_with_custom_reconciler():
    model_name, S, tags, reconciler, max_na_ratio = sample_data()
    reconciler = BottomUp()
    model = HierarchicalReconcileModel(model_name, S, tags, reconciler, max_na_ratio)

    assert model.model_name == model_name
    assert model.S.equals(S)
    assert model.tags == tags
    assert len(model.reconciler) == 1
    assert model.max_na_ratio == max_na_ratio


## test HierarchicalReconcileMethod prepare_dataframe_to_hf ##
def prepare_data():
    X_pred = pd.DataFrame({
        'timestamp': ['2023-07-20', '2023-07-21'],
        'pred_mean': [10, 15],
        'id_pred': [1, 2]
    })
    X_true = pd.DataFrame({
        'timestamp': ['2023-07-20', '2023-07-21'],
        'y': [8, 12]
    })

    return X_pred, X_true

def test_prepare_dataframe_to_hf_with_X_true():
    X_pred, X_true = prepare_data()
    model_name, S, tags, reconciler, max_na_ratio = sample_data()
    model = HierarchicalReconcileModel(model_name, S, tags, reconciler, max_na_ratio)

    result = model.prepare_dataframe_to_hf(X_pred, model_name, X_true)

    expected_columns = ['ds', 'Test_Model', 'y']
    assert result.columns.tolist() == expected_columns
    assert result.index.tolist() == [1, 2]
    assert result['Test_Model'].tolist() == [10, 15]
    assert result['y'].tolist() == [8, 12]

def test_prepare_dataframe_to_hf_without_X_true():
    X_pred, _ = prepare_data()
    model_name, S, tags, reconciler, max_na_ratio = sample_data()
    model = HierarchicalReconcileModel(model_name, S, tags, reconciler, max_na_ratio)

    result = model.prepare_dataframe_to_hf(X_pred, model_name)

    expected_columns = ['ds', 'Test_Model']
    assert result.columns.tolist() == expected_columns
    assert result.index.tolist() == [1, 2]
    assert result['Test_Model'].tolist() == [10, 15]


## test HierarchicalReconcileMethod fit ##
def test_HierarchicalReconcileMethod_fit():
    X_pred, X_true = prepare_data()
    model_name, S, tags, reconciler, max_na_ratio = sample_data()
    model = HierarchicalReconcileModel(model_name, S, tags, reconciler, max_na_ratio)

    updated_self = model.fit(X_true, X_pred, X_pred)

    assert updated_self.X.columns.tolist() == [ 'ds', 'Test_Model', 'y']  
    assert updated_self.X_hat.columns.tolist() == [ 'ds', 'Test_Model']  


## test HierarchicalReconcileMethod predict ##
# The test checks also the prepare_output method
from hierarchicalforecast.utils import aggregate
import warnings

def prepare_data_reconcile():
    df = pd.DataFrame(columns = ['level0',	'level1',	'ds',	'y'])
    df['ds'] = ['2023-07-20', '2023-07-21', '2023-07-22']*2
    df['y'] = 1
    df['level0'] = 'a'
    df['level1'] =  ['b', 'b', 'b', 'c', 'c', 'c']
    spec = [['level0'], ['level0', 'level1'],]

    Y_df, S_df, tags = aggregate(df=df, spec=spec)
    Y_df = Y_df.reset_index()
    return Y_df, S_df, tags 

def prepare_input_reconcile():
    X_pred = pd.DataFrame({
        'timestamp': ['2023-07-20', '2023-07-21', '2023-07-22', '2023-07-23',
                      '2023-07-24', '2023-07-25', '2023-07-26', '2023-07-27']*3,
        'pred_mean': [10] * 8 + [4] * 8 + [2] * 8,
        'id_pred': ['a'] * 8 + ['a/b'] * 8 + ['a/c'] * 8,
        'pi_upper_95': [11] * 8 + [5] * 8 + [3] * 8,
        'pi_lower_95': [9] * 8 + [3] * 8 + [2] * 8

    })

    X_true = pd.DataFrame({
        'ds': ['2023-07-20', '2023-07-21', '2023-07-22', '2023-07-23',
                      '2023-07-24', '2023-07-25', '2023-07-26', '2023-07-27']*3,
        'y': [2] * 8 + [1] * 8 + [1] * 8,
        'unique_id':  ['a'] * 8 + ['a/b'] * 8 + ['a/c'] * 8
    }).set_index('unique_id')

    X_future_pred = pd.DataFrame({
        'timestamp': ['2023-07-28', '2023-07-29', '2023-07-30']*3,
        'pred_mean': [10, 10, 10, 4, 4, 2, 5, 5, 2],
        'id_pred': ['a', 'a', 'a', 'a/b', 'a/b', 'a/b', 'a/c', 'a/c', 'a/c']
    })

    return X_true, X_pred, X_future_pred

def test_HierarchicalReconcileMethod_predict():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        _, S_df, tags = prepare_data_reconcile()
        X_true, X_pred, X_future_pred = prepare_input_reconcile()
        h_model = HierarchicalReconcileModel(model_name = 'test_model', S = S_df, tags = tags,
                                            reconciler = [TopDown(method = 'average_proportions')])
        h_model.fit(X_true, X_pred, X_future_pred)

        Y_rec = h_model.predict(as_output = True)

    # Assert if Y_rec is consistent with as_output = True
    assert Y_rec.columns.tolist() == ['timestamp', 'id_pred', 'pred_mean', 'sigma', 'pi_lower_95','pi_upper_95']
    # Assert if the reconciliation is logically correct
    for ds in Y_rec['timestamp'].unique():
        check_df = Y_rec[Y_rec['timestamp'] == ds].reset_index()
        assert check_df['pred_mean'][0] == check_df['pred_mean'][1:].sum()


## test HierarchicalReconcileMethod score ##
def test_HierarchicalReconcileMethod_score():
    import math
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        _, S_df, tags = prepare_data_reconcile()
        X_true, X_pred, X_future_pred = prepare_input_reconcile()
        h_model = HierarchicalReconcileModel(model_name = 'test_model', S = S_df, tags = tags,
                                            reconciler = [TopDown(method = 'average_proportions')])
        h_model.fit(X_true, X_pred, X_future_pred)

        # Check score NOT equal values
        # just check the columns
        Y_rec = h_model.predict(as_output = True)
        X_future_true = X_future_pred
        X_future_true.rename(columns = {'id_pred': 'unique_id'}, inplace= True)
        X_future_true = X_future_true.set_index('unique_id')
        X_future_true.columns = ['ds', 'y'] 
        _, scores = h_model.score(X_true = X_future_true, X_pred = Y_rec, check_model_pred = Y_rec.set_index('id_pred'), hierarchical_output = False)

        assert scores.columns.tolist() == ['id_pred', 'MAE', 'MAPE', 'RMSE', 'MSE', 'R2', 'Percentage Coverage']

        # Check score equal values
        # check the expected results
        X_future_true['y'] = list(Y_rec['pred_mean'])
        scores_aggr, _ = h_model.score(X_true = X_future_true, X_pred = Y_rec, check_model_pred = Y_rec.set_index('id_pred'), hierarchical_output = False)
        expected_scores = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        for i, (x, y) in enumerate(zip(scores_aggr.values, expected_scores)):
            if math.isnan(x):
                assert math.isnan(y)
            else:
                assert x == y

## test HierarchicalReconcileMethod best_reconciler ##
def test_HierarchicalReconcileMethod_best_reconciler():
    with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, S_df, tags = prepare_data_reconcile()
            X_true, X_pred, X_future_pred = prepare_input_reconcile()
            h_model = HierarchicalReconcileModel(model_name = 'test_model', S = S_df, tags = tags,
                                                reconciler = [TopDown(method = 'average_proportions')])
            h_model.fit(X_true, X_pred, X_future_pred)

            X_future_true = X_future_pred.copy()
            X_future_true.rename(columns = {'id_pred': 'unique_id'}, inplace= True)
            X_future_true = X_future_true.set_index('unique_id')
            X_future_true.columns = ['ds', 'y']

            h_model.best_reconciler(X_true=X_true, X_pred=X_pred, X_future_true = X_future_true, X_future_pred=X_future_pred)
            reconciler_string = str(h_model.reconciler).split(' ')[0]
            top_down_string = reconciler_string.split('.')[2]
            assert top_down_string == 'TopDown'

########### XGBoost ###########
def test_xgboost_default_init():
    model = XGBoost()
    assert isinstance(model.cat_features, list)
    assert isinstance(model.params, dict)
    assert isinstance(model.regression, bool)


def test_xgboost_custom_init():
    params =  {"learning_rate": 0.03,
                "subsample": 0.8,
                "colsample_bytree": 0.8}
    cat_features = ["dayofweek", "month"]
    model = XGBoost(params=params, regression=True, cat_features=cat_features)
    for param, value in params.items():
        assert model.params[param] == value
    assert model.cat_features == cat_features
    assert model.regression == True


@pytest.fixture
def xgboost_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    X, y = load_iris(return_X_y=True)

    y = OneHotEncoder().fit_transform(y.reshape(-1, 1)).toarray()
    y += 0.1
    y = y / y.sum(axis=1, keepdims=True)

    X, y = pd.DataFrame(X), pd.DataFrame(y)

    return train_test_split(X, y)

def test_xgboost_fit(xgboost_data):
    X_train, X_val, y_train, y_val = xgboost_data
    model = XGBoost().fit(X_train, y_train, X_val, y_val)
    assert isinstance(model, XGBoost)
    assert model.clf is not None
    assert isinstance(model.clf.best_iteration, int)


def test_xgboost_refit(xgboost_data):
    X_train, X_val, y_train, y_val = xgboost_data
    model = XGBoost().fit(X_train, y_train, X_val, y_val)
    model = model.refit(X_train, y_train)
    assert isinstance(model, XGBoost)
    assert model.clf is not None


def test_xgboost_predict(xgboost_data):
    X_train, X_val, y_train, y_val = xgboost_data
    model = XGBoost().fit(X_train, y_train, X_val, y_val)
    y_pred = model.predict(X_val)

    assert np.allclose(y_pred.sum(axis=1), np.array([1.] * y_pred.shape[0]))
    assert y_pred.shape[0] == X_val.shape[0]


def test_xgboost_score(xgboost_data):
    X_train, X_val, y_train, y_val = xgboost_data
    for regression in [True, False]:
        model = XGBoost(regression=regression).fit(X_train, y_train, X_val, y_val)
        score = model.score(X_val, y_val)
        assert isinstance(score, float)
        assert score > -1e-6


########### Boosting Reconciler ###########
def test_boosting_reconciler_default_init():
    model = BoostingReconcileModel()
    assert isinstance(model.cat_features, list)
    assert isinstance(model.xgb_params, dict)
    assert isinstance(model.preprocess_params, dict)


def test_boosting_reconciler_custom_init():
    xgb = {"learning_rate": 0.2, "n_iterations": 4}
    preproc = {"father_target": True, "father_preds": False}
    cat_features = ["dayofweek", "month"]
    model = BoostingReconcileModel(
        params_xgb=xgb,
        params_preprocess=preproc,
        cat_features=cat_features
        )
    assert model.xgb_params == xgb
    assert model.preprocess_params == preproc
    assert model.cat_features == cat_features


@pytest.fixture
def boosting_reconciler_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    X_pred, X_true, _ = prepare_input_reconcile()
    X_pred["sigma"] = 2

    return X_pred, X_true


def test_boosting_reconciler_fit(boosting_reconciler_data):
    X_true, X_pred = boosting_reconciler_data
    model = BoostingReconcileModel()
    model.fit(X_true, X_true, X_pred, X_pred)
    assert len(model._models) == 2
    assert "reg_a" in model._models
    assert "class_a" in model._models


def test_boosting_reconciler_refit(boosting_reconciler_data):
    X_true, X_pred = boosting_reconciler_data
    model = BoostingReconcileModel()
    model.fit(X_true, X_true, X_pred, X_pred)
    model.refit(X_true, X_pred)
    assert len(model._models) == 2
    assert "reg_a" in model._models
    assert "class_a" in model._models


def check_output_df(df: pd.DataFrame):
    cols = ['id_pred', 'pi_lower_95', 'pi_upper_95', 'pred_mean', 'sigma',
       'timestamp']
    for col in cols:
        assert col in df
    
    assert len(set(df["id_pred"].value_counts())) == 1


def test_boosting_reconciler_predict(boosting_reconciler_data):
    X_true, X_pred = boosting_reconciler_data
    model = BoostingReconcileModel()
    model.fit(X_true, X_true, X_pred, X_pred)
    output = model.predict(X_pred)

    check_output_df(output)
    assert output.shape[0] == X_pred.shape[0]
    assert output["id_pred"].nunique() == 3
    assert set(X_pred["id_pred"]) == set(output["id_pred"])


def test_boosting_reconciler_score(boosting_reconciler_data):
    X_true, X_pred = boosting_reconciler_data
    model = BoostingReconcileModel()
    model.fit(X_true, X_true, X_pred, X_pred)
    output = model.predict(X_pred)
    _, scores = model.score(X_true=X_true,
                            X_pred=output,
                            check_model_pred=output.set_index('id_pred'),
                            full_scoring=True)

    assert scores.columns.tolist() == ['id_pred', 'MAE', 'MAPE', 'RMSE', 'MSE', 'R2', 'Percentage Coverage']
    assert scores.shape[0] == 3
    