import numpy as np
import os
from numpy.testing import assert_equal, assert_almost_equal

from svrimg.utils.get_tables import (_create_unid, _create_dtime, _preprocess_svrgis_table,
                                     _create_svrgis_table, _create_index_table,
                                     get_table, get_pred_tables)                                

test_data_dir = "data/test/"

def test_create_unid():

    import pandas as pd

    d = {'om': [1, 2], 'date': ['2011-04-27', '2011-04-27'], 'time': ['12:00:00', '12:15:00']}
    test_unid = pd.DataFrame.from_dict(d)

    test_unid['date_utc'] = test_unid.apply(lambda x: _create_dtime(x), axis=1)
    test_unid['uid'] = test_unid.apply(lambda x: _create_unid(x, "tor"), axis=1)
    unids = test_unid.uid.values

    assert_equal(unids, ['201104271800z000000001_tor', '201104271815z000000002_tor'])

    test_unid['date_utc'] = test_unid.apply(lambda x: _create_dtime(x), axis=1)
    test_unid['uid'] = test_unid.apply(lambda x: _create_unid(x, "hail"), axis=1)
    unids = test_unid.uid.values

    assert_equal(unids, ['201104271800z000000001_hail', '201104271815z000000002_hail'])


def test_create_dtime():

    import pandas as pd

    d = {'om': [1, 2], 'date': ['2011-04-27', '2011-04-27'], 'time': ['18:00:00', '18:15:00']}
    test_dtime = pd.DataFrame.from_dict(d)

    test_dtime['date_utc'] = test_dtime.apply(lambda x: _create_dtime(x), axis=1)
    dts = test_dtime.date_utc.values

    res = np.array(['2011-04-28T00:00:00.000000000', '2011-04-28T00:15:00.000000000'], dtype='datetime64[ns]')
    assert_equal(dts, res)

    d = {'om': [1, 2], 'date': ['2011-12-31', '2011-12-31'], 'time': ['18:00:00', '18:15:00']}
    test_dtime = pd.DataFrame.from_dict(d)

    test_dtime['date_utc'] = test_dtime.apply(lambda x: _create_dtime(x), axis=1)
    dts = test_dtime.date_utc.values

    res = np.array(['2012-01-01T00:00:00.000000000', '2012-01-01T00:15:00.000000000'], dtype='datetime64[ns]')
    assert_equal(dts, res)


def test_preprocess_svrgis_table():

    import pandas as pd

    d = {'om': [1, 2], 'date': ['2011-04-27', '2011-04-27'], 'time': ['12:00:00', '18:15:00']}
    test_df = pd.DataFrame.from_dict(d)

    test_df = _preprocess_svrgis_table(test_df)
    dts = test_df.date_utc.values

    res = np.array(['2011-04-27T18:00:00.000000000', '2011-04-28T00:15:00.000000000'], dtype='datetime64[ns]')
    assert_equal(dts, res)

    d = {'om': [1, 2, 3], 'date': ['2005-08-17', '2011-04-27', '2017-02-07'],
         'time': ['18:00:00', '12:00:00', '15:15:00']}
    test_df = pd.DataFrame.from_dict(d)

    test_df = _preprocess_svrgis_table(test_df)

    yr = test_df.yr
    mo = test_df.mo
    dy = test_df.dy
    hr = test_df.hr

    assert_equal(yr, np.array([2005, 2011, 2017]))

    assert_equal(mo, np.array([8, 4, 2]))

    assert_equal(dy, np.array([18, 27, 7]))

    assert_equal(hr, np.array([0, 18, 21]))

def test_get_pred_tables():

    import pandas as pd

    data_dir = "{}/preds/".format(test_data_dir)

    ids = pd.read_csv(data_dir + "ids.csv")
    classes = pd.read_csv(data_dir + "class.csv")
    class_names = pd.read_csv(data_dir + "class_name.csv")
    
    eg_table = get_pred_tables(data_dir)
        
    assert_equal(ids['UNID'].values, eg_table.index.values)
    assert_equal(classes['Class Code'].values, eg_table['Class Code'].values)
    assert_equal(class_names['Class Name'].values, eg_table['Class Name'].values)
    
    eg_table = get_pred_tables(data_dir, example=False, default_name="*_table_*.csv", remove_first_row=True)
    
    assert_equal(ids['UNID'].values, eg_table.index.values)
    assert_equal(classes['Class Code'].values, eg_table['Class Code'].values)
    assert_equal(class_names['Class Name'].values, eg_table['Class Name'].values)

# def _create_svrgis_table():
#
# def test_create_index_table():
#
#
#
# def test_get_table():
#
#
#
# 
#
