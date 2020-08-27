from urllib.request import urlopen
from dateutil.parser import parse
import datetime
import os
import re
import numpy as np 
from urllib.error import HTTPError
import pandas as pd
import xarray as xr

def get_index_table(in_str, data_dir, url="http://svrimg.org/data/"):
    """Downloads svrimg index table from the given url and returns a pandas
    DataFrame. If the table is already downloaded, it simply returns a pandas
    DataFrame.  Two download options are "all" for the entire 1996 - 2017
    index table, or a datetime-like string, where the index table for the
    month containing the date is returned.  If "all" or a datetime-like
    string is not provided, the function will fail. This assumes that 
    'data_dir' exists.
    
    :param in_str: str. Either "all" or a datetime-like string.
    :param data_dir: str. Base directory in which to save the csv file.
    :param url: str. Base url directory where the table data is located. 
                     Default is "http://svrimg.org/data/".
    :return: table_data: pandas DataFrame. A DataFrame containing svrimg
                                           index information.
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
    """Downloads svrgis index table from the given url and returns a pandas
    DataFrame. If the table is already downloaded, it simply returns a pandas
    DataFrame.  The only download option is the entire 1996 - 2017
    dataset. This assumes that 'data_dir' exists.

    :param data_dir: str. Base directory in which to save the csv file.
    :param url: str. Base url directory where the table data is located. 
                     Default is "http://svrimg.org/data/".
    :return: table_data: pandas DataFrame. A DataFrame containing svrgis
                                           severe report information.
    """   
    if not os.path.exists("{}/96-17_tor_utc_gridrad.csv".format(data_dir)):
        
        _url = url + "96-17_tor_utc_gridrad.csv"
        
        c = pd.read_csv(_url, index_col='uid')
        c.to_csv("{}/96-17_tor_utc_gridrad.csv".format(data_dir))
        return c
    else:
        #print("{}/96-17_tor_utc_gridrad.csv".format(data_dir), "is already downloaded")
        return pd.read_csv("{}/96-17_tor_utc_gridrad.csv".format(data_dir), index_col='uid')            
        
def get_geog(data_dir, url="http://svrimg.org/maps/"):
    """Downloads svrimg geography netcdf file from the given url and returns
    an xarray dataset. If the netcdf file is already downloaded, it simply 
    returns an xarray dataset.  This assumes that 'data_dir' exists.
    
    :param data_dir: str. Base directory in which to save the csv file.
    :param url: str. Base url directory where the table data is located. 
                     Default is "http://svrimg.org/data/".
    :return: geog. xarray dataset.  An xarray dataset representation of
                                    the svrimg geography grid.
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
        