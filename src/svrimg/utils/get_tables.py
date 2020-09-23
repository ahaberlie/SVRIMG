from urllib.request import urlopen
from dateutil.parser import parse
import os
from urllib.error import HTTPError
import pandas as pd
import xarray as xr
import glob
from datetime import timedelta


def _create_unid(x, haz_type=""):
    r"""Creates a unique id for each svrgis report.
    
    Parameters
    ----------
    x: Series
        A single row from a pandas DataFrame
    haz_type: str
        Optional additional identifier to add to unid. Default is "".     
        
    Returns
    -------
    unid: str
        A unique id based on the information in a given pandas DataFrame row.
    """  

    unid = "{}{:02d}{:02d}{:02d}{:02d}z{:09d}_{}"
    unid = unid.format(x['date_utc'].year, x['date_utc'].month, 
                       x['date_utc'].day, x['date_utc'].hour,
                       x['date_utc'].minute, x['om'], haz_type)                                         
    return unid   


def _create_dtime(x, utc):
    r"""Generates datetimes from given DataFrame row columns date
    and time. If UTC=True, add 6 hours to this time.
    
    Parameters
    ----------
    x: Series
        A single row from a pandas DataFrame
    utc: str
        If true, add 6 hours to the dtime.  
        Note: This only works with CST.     
        
    Returns
    -------
    unid: str
        A unique id based on the information in a given pandas DataFrame row.
    """  

    dstr = "{}-{}".format(x['date'], x['time'])
    dtime = parse(dstr)
    
    if utc:
        dtime += timedelta(hours=6)
    
    return dtime     


def _create_svrgis_table(in_name, out_name, haz_type, data_dir="../data/csvs", 
                         start_year=1996, end_year=2017, 
                         utc=True):
    r"""Opens a given svrgis table from data_dir + in_name and returns a pandas
    DataFrame. If the table is already created, nothing will happe. Otherwise,
    it saves data_dir + out_name. This function assumes that 'data_dir' exists.
    
    NOTE: If UTC is true, all report times are incremented by 6 hours. This
    is because SPC stores the dates as central standard time (CST) for every 
    day of the year.
    
    Parameters
    ----------
    in_name: str
        Name of original svrgis csv file that you downloaded from SPC.
    out_name: str
        Name of output csv file.   
    haz_type: str
        Optionally add this string to the end of the unid.         
    data_dir: str
        Location where the original svrgis csv file is and where the 
        new file will be saved. Default is "../data/csvs/"
    start_year: int
        First year from which to return data. Default is 1996.
    end_year: int
        Last year from which to return data. Default is 2017.
    utc: bool.
        Whether or not to convert the svrgis time (CST) to UTC.
        Default is True.
        
    Returns
    -------
    td: DataFrame
        A pandas DataFrame containing the formatted svrgis data.
    """  

    out_filename = "{}/{}".format(data_dir, out_name)
    in_filename = "{}/{}".format(data_dir, in_name)
    
    if os.path.exists(out_filename):
        print("File exists!", out_filename)
        
    else:
        td = pd.read_csv(in_filename)
        td['CST_date'] = td['date']
        td['CST_time'] = td['time']
        td['date_utc'] = td.apply(lambda x: _create_dtime(x, utc), axis=1)
        td = td.drop(['date', 'time', 'yr', 'mo', 'dy'], axis=1)
        td['yr'] = td['date_utc'].dt.year
        td['mo'] = td['date_utc'].dt.month
        td['dy'] = td['date_utc'].dt.day
        td['hr'] = td['date_utc'].dt.hour
        td = td[(td.yr >= start_year) & (td.yr <= end_year)]
        td['uid'] = td.apply(lambda x: _create_unid(x, haz_type), axis=1)
        td = td.set_index('uid')
        td.to_csv(out_filename)
        return td


def _create_index_table(out_name, haz_type, data_dir="../data/csvs", 
                        url="https://svrimg.org/data/raw_img/", start_year=1996,
                        end_year=2017):
    r"""Attempts to download and concatenate monthly tables from svrimg for
    a given hazard type.  If the file doesn't exist, saves result out_name 
    in data_dir.  Otherwise, just returns DataFrame from existing file.
    
    Parameters
    ----------
    out_name: str
        Name of output csv file.     
    haz_type: str
        Optionally add this string to the end of the unid.
    data_dir: str
        Location where the original svrgis csv file is and where the 
        new file will be saved. Default is "../data/csvs"
    url: str
        Base url directory where the table data is located. 
        Default is "http://svrimg.org/data/".
    start_year: int
        First year from which to return data. Default is 1996.
    end_year: int
        Last year from which to return data. Default is 2017.
        
    Returns
    -------
    td: DataFrame
        A pandas DataFrame containing the formatted svrimg index data.
    """   
    
    out_filename = "{}/{}".format(data_dir, out_name)
    
    if os.path.exists(out_filename):
    
        return pd.read_csv(out_filename, index_col='unid')

    else:
        csvs = []
        
        for year in range(start_year, end_year+1):
        
            for month in range(1, 13):
                csv_name = "report_box_indexer_{:02d}.csv".format(month)
                file_url = "{}/{}/{}/{}".format(url, haz_type, 
                                                year, csv_name)
                try:
                    tmp_csv = pd.read_csv(file_url, index_col='unid')
                    csvs.append(tmp_csv)
                except HTTPError as e:
                    print(e, file_url)
                
        csvs = pd.concat(csvs)
        csvs.to_csv(out_filename)
        
        return csvs


def get_table(which, haz_type, data_dir="../data/csvs", 
              url="https://svrimg.org/data/"):
    r"""Downloads svrimg index or svrgis report table from the given url 
    and returns a pandas DataFrame. If the table is already downloaded, 
    it simply returns a pandas DataFrame. This assumes that 'data_dir' 
    exists.
    
    Parameters
    ----------
    which: str
        Either 'svrimg' for image indexes or 'svrgis' for report attributes. 
    haz_type: str
        Identify what hazard key to request. Expecting 'tor', 'hail', 
        or 'wind'.  
    data_dir: str
        Base directory in which to save the csv file. Default is 
        "../data/csv/".
    url: str
        Base url directory where the table data is located. 
        Default is "http://svrimg.org/data/".
        
    Returns
    -------
    table_data: DataFrame
        A pandas DataFrame containing svrimg index information.
    """               

    if which == 'svrimg':
        csv_name = "96-17_{}_utc_svrimg_index.csv".format(haz_type)
        id_col = 'unid'
        
    elif which == 'svrgis':
        csv_name = "96-17_{}_utc_gridrad.csv".format(haz_type)
        id_col = 'uid'
        
    else:
        raise ValueError("Expected 'svrimg' or 'svrgis', not {}.".format(which))
        
    file_url = "{}/{}".format(url, csv_name)
    file_name = "{}/{}".format(data_dir, csv_name)

    if not os.path.exists(file_name):
        tmp_csv = pd.read_csv(file_url, index_col=id_col)
        tmp_csv.to_csv(file_name)

        return tmp_csv
        
    else:

        return pd.read_csv(file_name, index_col=id_col)          


def get_pred_tables(data_dir, url="https://svrimg.org/data/", example=True, 
                    default_name="*_Table_*.csv", csv_name="eg_classes_96-17",
                    remove_first_row=False):
    r"""Either downloads example predictions if 'example' is true, or combines your prediction
    tables in 'data_dir' into one table using the default naming format of 
    '*_Table_*.csv' or whatever is passed into default_name. This will
    attempt to grab every year from 1996 - 2017, but will not fail if a year is missing. 
    By default, the first row in every year's table is example data on svrimg.org, and 
    it can be removed as long as 'remove_first_row' is True. By default, if there is a 
    repeated UNID, the last one is kept.  The theory here is that if you accidentally 
    clicked something, you would go back and fix it.  Thus, the nth time is likely 
    more accurate.
    
    Parameters
    ----------
    data_dir: str
        Base directory in which to save the csv file.
    url: str
        Base url directory where the table data is located. 
        Default is "http://svrimg.org/data/".
    example: bool
        If True, download example data.  If false, look for local 
        yearly tables. Default is True.
    default_name: str
        Naming format for local csv files. Stars are used as wildcards.
        Default is '*_Table_*.csv'.
    csv_name: str
        Default name of new csv file containing classifications.
    remove_first_row: bool
        Removes first row from each year of local table data if True, ignores 
        first row if false. Default is False.   
        
    Returns
    -------
    csv: DataFrame
        A pandas DataFrame of UNIDs and their predictions.
    """ 
 
    if example:
        if not os.path.exists("{}/{}.csv".format(data_dir, csv_name)):
            _url = url + "sample_classifications_96-17.csv"
            c = pd.read_csv(_url, index_col='UNID')
            c.to_csv("{}/{}.csv".format(data_dir, csv_name))
    else:
        csvs = []
        for fname in glob.glob(data_dir + default_name):
        
            print("Reading", fname)
            
            a = pd.read_csv(fname)

            if remove_first_row:
                a = a.drop(0)

            a = a.drop_duplicates(subset=["UNID"], keep='last')
            a = a.set_index("UNID")
            csvs.append(a)
        csvs = pd.concat(csvs)
        csvs.to_csv("{}/{}.csv".format(data_dir, csv_name))
            
    return pd.read_csv("{}/{}.csv".format(data_dir, csv_name), index_col='UNID')


def get_geog(data_dir="../data/geog/", url="https://svrimg.org/maps/"):
    r"""Downloads svrimg geography netcdf file from the given url and returns
    an xarray dataset. If the netcdf file is already downloaded, it simply 
    returns an xarray dataset.  This assumes that 'data_dir' exists.
    
    Parameters
    ----------
    data_dir: str
        Base directory in which to save the csv file.
    url: str
        Base url directory where the table data is located. 
        Default is "http://svrimg.org/maps/".
  
    Returns
    -------
    geog: dataset
        An xarray dataset representation of the svrimg geography grid.
    """  

    if not os.path.exists("{}/svrimg_geog.nc".format(data_dir)):
        
        _url = url + "svrimg_geog.nc"
        
        img = urlopen(_url)

        with open("{}/svrimg_geog.nc".format(data_dir), "wb") as file:
            file.write(img.read())
        
        return xr.open_dataset("{}/svrimg_geog.nc".format(data_dir))
    else:
        return xr.open_dataset("{}/svrimg_geog.nc".format(data_dir))
