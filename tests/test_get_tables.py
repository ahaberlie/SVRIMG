import numpy as np
import os
from numpy.testing import assert_equal, assert_almost_equal

from svrimg.utils.get_tables import (_create_unid, _create_dtime, _preprocess_svrgis_table,
                                     _create_svrgis_table, _create_index_table,
                                     get_table, get_pred_tables)
                                     
test_data_dir = os.environ.get('TEST_DATA_DIR')                                  


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

    d = {'om': [1, 2], 'date': ['2011-04-27', '2011-04-27'], 'time': ['12:00:00', '12:15:00']}
    test_df = pd.DataFrame.from_dict(d)

    test_df = _preprocess_svrgis_table(test_df)
    dts = test_df.date_utc.values

    res = np.array(['2011-04-28T00:00:00.000000000', '2011-04-28T00:15:00.000000000'], dtype='datetime64[ns]')
    assert_equal(dts, res)

    d = {'om': [1, 2], 'date': ['2005-08-17', '2011-04-27', '2017-02-07'],
         'time': ['06:00:00', '12:00:00', '15:15:00']}
    test_df = pd.DataFrame.from_dict(d)

    test_df = _preprocess_svrgis_table(test_df)

    yr = test_df.yr
    mo = test_df.mo
    dy = test_df.dy
    hr = test_df.hr

    assert_equal(yr, [2005, 2011, 2017])

    assert_equal(mo, [8, 4, 2])

    assert_equal(dy, [17, 27, 7])

    assert_equal(hr, [12, 18, 1])


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
# def test_get_pred_tables():
#
