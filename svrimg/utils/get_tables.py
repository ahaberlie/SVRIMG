from urllib.request import urlopen
from dateutil.parser import parse
import datetime
import os
import re
import numpy as np 
from urllib.error import HTTPError
import pandas as pd
import xarray as xr

def get_index_tables(in_str, data_dir="../data/csvs/", 
                     url="http://svrimg.org/data/"):

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
           
        
def get_geog(data_dir="../data/geog/", url="http://svrimg.org/maps/"):

    if not os.path.exists("{}/svrimg_geog.nc".format(data_dir)):
        
        _url = url + "svrimg_geog.nc"
        
        img = urlopen(_url)

        with open("{}/svrimg_geog.nc".format(data_dir), "wb") as file:
            file.write(img.read())
        
        return xr.open_dataset("{}/svrimg_geog.nc".format(data_dir))
    else:
        #print("{}/svrimg_geog.nc".format(data_dir), "is already downloaded")
        return xr.open_dataset("{}/svrimg_geog.nc".format(data_dir))
        
def get_svrgis_table(data_dir="../data/csvs/", url="http://svrimg.org/data/"):        

    if not os.path.exists("{}/96-17_tor_utc_gridrad.csv".format(data_dir)):
        
        _url = url + "96-17_tor_utc_gridrad.csv"
        
        c = pd.read_csv(_url, index_col='uid')
        c.to_csv("{}/96-17_tor_utc_gridrad.csv".format(data_dir))
        return c
    else:
        #print("{}/96-17_tor_utc_gridrad.csv".format(data_dir), "is already downloaded")
        return pd.read_csv("{}/96-17_tor_utc_gridrad.csv".format(data_dir), index_col='uid')