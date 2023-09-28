## test ProphetPrerocess class ##
# The class is composed by the methods tested in test_datapreparation_utils.py 
# So, we just check if the output of the preprocessing can be the input for a prophet model


import prophet
import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])

from TeleMed.telemed_sk.datapreparation.model_preproc import ProphetPreprocess

from TeleMed.telemed_sk.datapreparation.model_preproc import PreprocessBoosting



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
def test_ProphetPreprocess_df():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hierarchy = {
            "level1": "zone",
            "level2": "city"
        }
        time_granularity = "D"
        date_col = "date_col"
        missing_data_strategy = ''

        # Sample data for testing
        df = sample_data_hier()

        prophet_preproc = ProphetPreprocess(hierarchy, time_granularity, date_col, missing_data_strategy)

        X, S, tags = prophet_preproc.transform(df)
        
        # Check if X is ready to be used for Prophet
        Prophet = prophet.Prophet()
        Prophet.fit(X)


################## Preprocessing Boosting ###########################################
def test_preprocessing_boosting_init():

    PB = PreprocessBoosting(lags = [i for i in range(1,6+1)],n_hier=2,divide_target=True)
    
    assert PB.datepart == True
    assert PB.preds == True
    assert PB.target == True
    assert PB.conf_inter == True
    assert PB.lags == [1,2,3,4,5,6]
    assert PB.n_hier == 2
    assert PB.father_preds == False
    assert PB.sons_preds == False
    assert PB.father_target == False
    assert PB.sons_target == False
    assert PB.divide_target == True

def test_preprocessing_boosting_transform():

    df_real = pd.DataFrame([["A",2022,10],["A/B",2022,5],["A/C",2022,5],["A/B/B1",2022,2],["A/B/B2",2022,3],["A/C/C1",2022,5],
                   ["A/B/B1/B1.1",2022,1],["A/B/B1/B1.2",2022,1],["A/B/B2/B2.1",2022,1],["A/B/B2/B2.2",2022,1],["A/B/B2/B2.3",2022,1]],
                  columns = ["Id","date","y"])

    df_pred = pd.DataFrame([["A",2022,100],["A/B",2022,50],["A/C",2022,50],["A/B/B1",2022,20],["A/B/B2",2022,30],["A/C/C1",2022,50],
                    ["A/B/B1/B1.1",2022,10],["A/B/B1/B1.2",2022,10],["A/B/B2/B2.1",2022,10],["A/B/B2/B2.2",2022,10],["A/B/B2/B2.3",2022,10]],
                    columns = ["Id","date","pred"])

    PB = PreprocessBoosting(datepart=True,preds=True,target=True,conf_inter=False,
                            lags=[1,2],n_hier=3,
                            father_preds=True,sons_preds=False,father_target=True,sons_target=False,
                            divide_target=False)

    # test numero di colonne
    assert len(PB.transform(df_real,df_pred,"date","date","y","pred","Id","Id")[0].columns) == 20
    assert len(PB.transform(df_real,df_pred,"date","date","y","pred","Id","Id")[1].columns) == 16

    # test datepart
    PB = PreprocessBoosting(datepart=True,preds=False,target=False,conf_inter=False,
                            n_hier=3,
                            father_preds=True,sons_preds=False,father_target=True,sons_target=False,
                            divide_target=False)

    df_date = pd.DataFrame([[1,3,1,1970,1,1,True,False]],columns=['dayofmonth', 'dayofweek', 'dayofyear', 'year', 'month', 'quarter',
        'holiday', 'weekend'],index=[2022],dtype=np.int32)
    df_date = df_date.astype(dtype={"holiday":bool,"weekend":bool})

    pd.testing.assert_frame_equal(PB.transform(df_real,None,"date","date","y","pred","Id","Id")[0],df_date)

    # test divide target
    for n in range(2,4+1):
        PB = PreprocessBoosting(datepart=False,preds=False,target=True,conf_inter=False,
                                n_hier=n,
                                father_preds=True,sons_preds=False,father_target=True,sons_target=False,
                                divide_target=True)

        ris = PB.transform(df_real,None,"date","date","y","pred","Id","Id")

        for tab in ris:
                assert tab.iloc[:,1:].sum(axis=1).values == 1

    # test numero di colonne lag
    for n in range(1,10):
        PB = PreprocessBoosting(datepart=False,preds=True,target=True,conf_inter=False,
                                lags=[i for i in range(n)],n_hier=1,
                                father_preds=True,sons_preds=False,father_target=True,sons_target=False,
                                divide_target=False)

        ris = PB.transform(df_real,df_pred,"date","date","y","pred","Id","Id")

        assert len([i for i in PB.transform(df_real,df_pred,"date","date","y","pred","Id","Id")[0].columns if "Lag" in i]) == n

def test_get_X_y():

    df_real = pd.DataFrame([["A",2022,10],["A/B",2022,5],["A/C",2022,5],["A/B/B1",2022,2],["A/B/B2",2022,3],["A/C/C1",2022,5],
                   ["A/B/B1/B1.1",2022,1],["A/B/B1/B1.2",2022,1],["A/B/B2/B2.1",2022,1],["A/B/B2/B2.2",2022,1],["A/B/B2/B2.3",2022,1]],
                  columns = ["Id","date","y"])

    df_pred = pd.DataFrame([["A",2022,100],["A/B",2022,50],["A/C",2022,50],["A/B/B1",2022,20],["A/B/B2",2022,30],["A/C/C1",2022,50],
                    ["A/B/B1/B1.1",2022,10],["A/B/B1/B1.2",2022,10],["A/B/B2/B2.1",2022,10],["A/B/B2/B2.2",2022,10],["A/B/B2/B2.3",2022,10]],
                    columns = ["Id","date","pred"])
     
    PB = PreprocessBoosting(datepart=False,preds=True,target=True,conf_inter=False,
                        lags = [1,2],n_hier=3,
                        father_preds=True,sons_preds=False,father_target=True,sons_target=False,
                        divide_target=False)

    ris = PB.transform(df_real,df_pred,"date","date","y","pred","Id","Id")

    for tab in ris:
         assert all(["Target" in i for i in PB.get_X_y(tab,1)[1].columns])



