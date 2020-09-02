from urllib.request import urlopen
from dateutil.parser import parse
import datetime
import os
import re
import numpy as np 
from urllib.error import HTTPError
import pandas as pd
import xarray as xr
import glob

def get_index_table(in_str, data_dir, url="http://svrimg.org/data/"):
    r"""Downloads svrimg index table from the given url and returns a pandas
    DataFrame. If the table is already downloaded, it simply returns a pandas
    DataFrame.  Two download options are "all" for the entire 1996 - 2017
    index table, or a datetime-like string, where the index table for the
    month containing the date is returned.  If "all" or a datetime-like
    string is not provided, the function will fail. This assumes that 
    'data_dir' exists.
    
    Parameters
    ----------
    in_str: str
        Either "all" or a datetime-like string to specify the index 
        table period. 
    data_dir: str
        Base directory in which to save the csv file.
    url: str
        Base url directory where the table data is located. 
        Default is "http://svrimg.org/data/".
        
    Returns
    -------
    table_data: DataFrame
        A pandas DataFrame containing svrimg index information.
    """               

    if in_str == 'all':
        if not os.path.exists("{}/96-17_tor_utc_svrimg_index.csv".format(data_dir)):
        
            _url = url + "96-17_tor_utc_svrimg_index.csv"
            
            c = pd.read_csv(_url, index_col='unid')
            c.to_csv("{}/96-17_tor_utc_svrimg_index.csv".format(data_dir))
            return c
        else:
            #print("{}/96-17_tor_utc_svrimg_index.csv".format(data_dir), "is already downloaded")
            return pd.read_csv("{}/96-17_tor_utc_svrimg_index.csv".format(data_dir), index_col='unid')
    else:
        try:
            date = parse(in_str)

            fname = "report_box_indexer_{:02d}.csv".format(date.month)
                                                           
            if not os.path.exists("{}/{}_{}".format(data_dir, date.year, fname)):
                _url = "{}/raw_img/{}/{}".format(url, date.year, fname)
                print(_url)
                c = pd.read_csv(_url, index_col='unid')
                c.to_csv("{}/{}_{}".format(data_dir, date.year, fname))
                return c
            else:
                #print("{}/{}_{}".format(data_dir, date.year, fname), "is already downloaded")
                
                return pd.read_csv("{}/{}_{}".format(data_dir, date.year, fname), index_col='unid')
                
        except Exception as e:
            print(e, "Expected date string or 'all'")

def get_svrgis_table(data_dir, url="http://svrimg.org/data/"):        
    r"""Downloads svrgis index table from the given url and returns a pandas
    DataFrame. If the table is already downloaded, it simply returns a pandas
    DataFrame.  The only download option is the entire 1996 - 2017
    dataset. This assumes that 'data_dir' exists.
    
    Parameters
    ----------
    data_dir: str
        Base directory in which to save the csv file.
    url: str. Base url directory where the table data is located. 
              Default is "http://svrimg.org/data/".
        
    Returns
    -------
    table_data: DataFrame
        A pandas DataFrame A DataFrame containing svrgis severe report
        information.
    """  
  
    if not os.path.exists("{}/96-17_tor_utc_gridrad.csv".format(data_dir)):
        
        _url = url + "96-17_tor_utc_gridrad.csv"
        
        c = pd.read_csv(_url, index_col='uid')
        c.to_csv("{}/96-17_tor_utc_gridrad.csv".format(data_dir))
        return c
    else:
        #print("{}/96-17_tor_utc_gridrad.csv".format(data_dir), "is already downloaded")
        return pd.read_csv("{}/96-17_tor_utc_gridrad.csv".format(data_dir), index_col='uid')            
        
def get_pred_tables(data_dir, url="http://svrimg.org/data/", example=True, 
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
        for fname in glob.glob(data_dir + "*_Table_*.csv"):
        
            print("Reading", fname)
            
            a = pd.read_csv(fname)
            a = a.drop(0)
            a = a.drop_duplicates(subset=["UNID"], keep='last')
            a = a.set_index("UNID")
            csvs.append(a)
        csvs = pd.concat(csvs)
        csvs.to_csv("{}/{}.csv".format(data_dir, csv_name))
            
    return pd.read_csv("{}/{}.csv".format(data_dir, csv_name), index_col='UNID')

def get_geog(data_dir, url="http://svrimg.org/maps/"):
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
        #print("{}/svrimg_geog.nc".format(data_dir), "is already downloaded")
        return xr.open_dataset("{}/svrimg_geog.nc".format(data_dir))
        