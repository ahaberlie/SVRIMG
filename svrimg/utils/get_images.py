from urllib.request import urlopen
from dateutil.parser import parse
import datetime
import os
import re
import numpy as np 
from urllib.error import HTTPError
import xarray as xr
from imageio import imread

def _parse_str(in_str, url="http://svrimg.org/data/raw_img/"):

    date = parse(in_str)
    yr = date.year
    mo = date.month
    dy = date.day
    hr = date.hour
    mn = date.minute
    
    f_url = "{}/{}/{:02d}/".format(url, yr, mo)
    f_format = "{}{:02d}{:02d}{:02d}{:02d}".format(yr, mo, dy, 
                                                      hr, mn)
                                                      
    return f_url, f_format           
    
def _write_img(p_dir, f_url, i_name):

    file_url = f_url + i_name
    img = urlopen(file_url)
    with open(p_dir + i_name, "wb") as file:
        file.write(img.read())
                
def request_images(input_list, data_dir):

    file_locs = {}
    
    if type(input_list) == list or type(input_list) == np.ndarray:
    
        filename = None
        
        for img_name in input_list:
        
            folder_url, f_format = _parse_str(img_name[:12])
            
            year = img_name[:4]
            parent_dir = "{}/{}/".format(data_dir, year)
            
            if not os.path.exists(parent_dir + img_name + ".png"):
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)

                try:
                    _write_img(parent_dir, folder_url, img_name + ".png")
                    filename = parent_dir + img_name + ".png"
                except HTTPError as e:
                    print(e, parent_dir + img_name + ".png")
                
            else:
                #print(parent_dir + img_name + ".png", "Exists!")
                filename = parent_dir + img_name + ".png"
                
            file_locs[img_name] = filename
            
    return file_locs
    
def get_img_list(id_list):

    loc = request_images(id_list, "../data/tor")
    images = []

    for unid, file in loc.items():
        if file != None:
            images.append(read_image(file))
            
    images = np.array(images)
    
    return images
    
def geo_read_image(row, uid, filename, x_=1399, y_=899):

    im = read_image(filename)
    
    blank = np.zeros(shape=(y_, x_))
    blank[row.ymin:row.ymax+1, row.xmin:row.xmax+1] = im
    
    return blank
    
    
def read_image(filename):

    return imread(filename, pilmode='P')
    
def get_example(data_dir="../data/example/", url="http://svrimg.org/data/"):

    if not os.path.exists("{}/nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir)):
        
        _url = url + "nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc"
        
        img = urlopen(_url)

        with open("{}/nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir), "wb") as file:
            file.write(img.read())
        
        return xr.open_dataset("{}/nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir))
    else:
        #print("{}nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir), "is already downloaded")
        return xr.open_dataset("{}/nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir))