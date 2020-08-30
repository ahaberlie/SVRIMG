from urllib.request import urlopen
from dateutil.parser import parse
import datetime
import os
import re
import numpy as np 
from urllib.error import HTTPError
import xarray as xr
from imageio import imread
import pickle

def _parse_str(in_str, url="http://svrimg.org/data/raw_img/"):
    """Attempts to parse a string assuming it has some form 
    of datetime format. Returns a formatted base url directory 
    for monthly files. Function will fail if in_str is not 
    datetime-like.
    
    :param in_str: str.  String with date information.
    :param url: str. Base url from which to access files. 
                Default = "http://svrimg.org/data/raw_img/"
    :return: f_url: str. base url for monthly file directory.
    """

    date = parse(in_str)
    yr = date.year
    mo = date.month
    
    f_url = "{}/{}/{:02d}/".format(url, yr, mo)
                                                      
    return f_url           
    
def _write_img(p_dir, f_url, i_name):
    """Downloads an image from a given url and saves it 
    in a specified directory.
    
    :param p_dir: str. Directory in which to save the image.
    :param f_url: str. Base url from which to access files.
    :param i_name: str. Image filename.
    :return: None
    """
    
    file_url = f_url + i_name
    img = urlopen(file_url)
    with open(p_dir + i_name, "wb") as file:
        file.write(img.read())
                
def request_images(id_list, data_dir):
    """Downloads images and saves them based on a list of unique identifiers. 
    If the images are already downloaded, this function just returns the file 
    location of the image. This assumes that 'data_dir' exists.
    
    :param id_list: list or ndarray. List of unique svrimg identifiers.
    :param data_dir: str. Base directory in which to save the images.
    :return: loc: dict. A dictionary of unique identifiers and where the 
                        affiliated file was saved.
    """
    
    file_locs = {}
    
    if type(id_list) == list or type(id_list) == np.ndarray:

        for img_name in id_list:

            folder_url = _parse_str(img_name[:12])
            
            year = img_name[:4]
            parent_dir = "{}/{}/".format(data_dir, year)
            
            if not os.path.exists(parent_dir + img_name + ".png"):
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
                try:
                    _write_img(parent_dir, folder_url, img_name + ".png")
                    file_locs[img_name] = parent_dir + img_name + ".png"
                except HTTPError as e:
                    print(e, parent_dir + img_name + ".png")
                    file_locs[img_name] = "Missing"
            else:
                #print(parent_dir + img_name + ".png", "Exists!")
                file_locs[img_name] = parent_dir + img_name + ".png"

    return file_locs
    
def get_img_list(id_list, data_dir, keep_missing=False):
    """Downloads images and saves them based on a list of unique identifiers. 
    If the images are already downloaded, the file is not downloaded. The
    function then takes the images and puts them into a list. The order is 
    not guaranteed to be the same as the input list. This assumes that 
    'data_dir' exists.  If keep_missing is true, insert blank image into
    the stack.
    
    :param id_list: list or ndarray. List of unique svrimg identifiers.
    :param data_dir: str. Base directory in which to save the images.
    :return: images: ndarray. A list of images corresponding to the given
                              id_list.
    """
    loc = request_images(id_list, data_dir)
    images = []

    for unid, file in loc.items():
        if file != "Missing":
            images.append(read_image(file))
        else:
            if keep_missing:
                images.append(np.zeros((136, 136), dtype=np.uint8))
                print(unid, " is missing an image file. Inserted blank image because keep_missing is True.")
            else:
                print(unid, " is missing an image file. Did not insert blank image because keep_missing is False.")
            
    images = np.array(images)
    
    return images
    
def geo_read_image(index, locator, uid, x_=1399, y_=899):
    """Read an image based on a unique identifier, and place the image
    within the original grid.  Requires an svrimg index table that 
    can be accessed from the function get_index_tables in utils.get_tables.
    
    :param index: DataFrame.  A svrimg index table that contains information
                              on the requested image.
    :param locator: dict. Lookup table for file locations based on a given
                          unique svrimg id.
    :param uid: str. Unique svrimg id.
    :param x_: int. Size of x dimension of original grid.
    :param y_: int. Size of y dimension of original grid.
    :return: canvas: (y_, x_) ndarray. A ndarray of the same dimensions as the
                                       original grid with all zeroes except the
                                       location where the image identified with
                                       'uid' was extracted from.
    """
    row = index.loc[uid]
    im = read_image(locator[uid])
    canvas = np.zeros(shape=(y_, x_))
    canvas[row.ymin:row.ymax+1, row.xmin:row.xmax+1] = im
    
    return canvas
    
def get_example_data(data_type, data_dir="../data/pkls/", 
                     url="http://svrimg.org/data/classifications/"):
    """Returns training, validation, or testing data, depending on the
    value of 'data_type'.  This function attempts to download the data
    if the file does not exist in 'data_dir'.  Returns x and y data
    for each subset.
    
    :param data_type: str. Request 'training', 'validation', or 'testing' data.
    :param data_dir: str. Base directory in which to save the netcdf file. Default
                          is "../data/pkls/".
    :param url: str. Base url directory where the example data are located. Default
                          is "http://svrimg.org/data/classifications/".
    :return: x_y_data: (X, Y) ndarray. A ndarray where the first dimension is a list
                                       of images, and the second dimension is a list
                                       of classifications.
    """
    if data_type == 'training':
        loc = "{}/1996_2011_train.pkl".format(data_dir)
        if not os.path.exists(loc):
            _url = url + "1996_2011_train.pkl"
            pkl = urlopen(_url)
            with open(loc, "wb") as file:
                file.write(pkl.read())
    elif data_type == 'validation':
        loc = "{}/2012_2013_validation.pkl".format(data_dir)
        _url = url + "2012_2013_validation.pkl"
        pkl = urlopen(_url)
        with open(loc, "wb") as file:
            file.write(pkl.read())
      
    elif data_type == 'testing':
        loc = "{}/2014_2017_test.pkl".format(data_dir)
        _url = url + "2014_2017_test.pkl"
        pkl = urlopen(_url)
        with open(loc, "wb") as file:
            file.write(pkl.read())
    else:
        print("Expected training, validation, or testing")
        return None
    return pickle.load(open(loc, "rb"))   


def read_image(filename):
    """Read and return raw image information based on a given filename.
    
    :param index: filename. str. File from which to read image information.
    :return: image: (M, N) ndarray.  An ndarray representation of the image.
    """
    return imread(filename, pilmode='P')
    
def get_example(data_dir="../data/example/", url="http://svrimg.org/data/"):
    """Downloads an interpolated GridRad (gridrad.org) file from a url and returns an xarray 
    dataset representation from April 27th at 1900 UTC.  If the file is already downloaded, 
    it simply returns an xarray dataset representation. This assumes that 'data_dir' exists.
    
    :param data_dir: str. Base directory in which to save the netcdf file. Default
                          is "../data/example/".
    :param url: str. Base url directory where the example data is located. Default
                          is "http://svrimg.org/data/".
    :return: gridrad. xarray dataset.  an xarray dataset representation of
                                       interpolated GridRad data on April 27th 
                                       at 1900 UTC.
    """
    if not os.path.exists("{}/nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir)):
        
        _url = url + "nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc"
        
        img = urlopen(_url)

        with open("{}/nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir), "wb") as file:
            file.write(img.read())
        
        return xr.open_dataset("{}/nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir))
    else:
        #print("{}nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir), "is already downloaded")
        return xr.open_dataset("{}/nexrad_REFC_COL_MAX_INTERP_v3_1_20110427T190000Z.nc".format(data_dir))