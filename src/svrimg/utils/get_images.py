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

def _parse_str(in_str, url="http://svrimg.org/data/raw_img"):
    r"""Attempts to parse a string assuming it has some form 
    of datetime format. Returns a formatted base url directory 
    for monthly files. Function will fail if in_str is not 
    datetime-like. Formats that work include YYYYMMDDHHmm
    and YYYYMMDD.
    
    Parameters
    ----------
    in_str: str
        String with date information.
    url: dictionary
        Base url from which to access files. 
        Default = "http://svrimg.org/data/raw_img/"
    Returns
    -------
    file_url: str
        Base url for monthly file directory.
    """

    date = parse(in_str)
    yr = date.year
    mo = date.month
    
    file_url = "{}/{}/{:02d}/".format(url, yr, mo)
                                                      
    return file_url           
    
def _write_img(save_dir, url_dir, img_name):
    r"""Downloads an image from a given url and saves it 
    in a specified directory.
    
    Parameters
    ----------
    save_dir: str
        Directory in which to save the image.
    url_dir: str
        Base url from which to access files.
    img_name: str
        Image filename.
    """
    
    file_url = url_dir + img_name
    img = urlopen(file_url)
    with open(save_dir + img_name, "wb") as file:
        file.write(img.read())
                
def request_images(id_list, data_dir):
    r"""Downloads images and saves them based on a list of unique identifiers. 
    If the images are already downloaded, this function just returns the file 
    location of the image. This assumes that 'data_dir' exists.
    
    Parameters
    ----------
    id_list: list
        List of unique svrimg identifiers.
    data_dir: str
        Base url from which to access files. 
        Default is "http://svrimg.org/data/raw_img/"
    Returns
    -------
    loc: dict
        A dictionary of unique identifiers and where the 
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
    r"""Downloads images and saves them based on a list of unique identifiers. 
    If the images are already downloaded, the file is not downloaded. The
    function then takes the images and puts them into a list. The order is 
    not guaranteed to be the same as the input list. This assumes that 
    'data_dir' exists.  If keep_missing is true, insert blank image into
    the stack.
    
    Parameters
    ----------
    id_list: list
        List of unique svrimg identifiers.
    data_dir: str
        Base directory in which to save the images. 
    Returns
    -------
    images: (N, Y, X) ndarray
        A list of images corresponding to the given
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
    r"""Read an image based on a unique identifier, and place the image
    within the original grid.  Requires an svrimg index table that 
    can be accessed from the function get_index_tables in utils.get_tables.
    
    Parameters
    ----------
    index: DataFrame
        A svrimg index table that contains information
        on the requested image.
    locator: dict
        Lookup table for file locations based on a given
        unique svrimg id.
    uid: str
        Unique svrimg id.
    x_: int
        Size of x dimension of original grid. Default is 1399.
    y_: int
        Size of y dimension of original grid. Default is 899.
    Returns
    -------
    canvas: (y_, x_) ndarray
        A ndarray of the dimensions of (y_, x_) with all zeroes 
        except the location where the image identified with
        'uid' was extracted from.
    """

    row = index.loc[uid]
    im = read_image(locator[uid])
    canvas = np.zeros(shape=(y_, x_))
    canvas[row.ymin:row.ymax+1, row.xmin:row.xmax+1] = im
    
    return canvas
    
def get_example_data(data_type, data_dir="../data/pkls/", 
                     url="http://svrimg.org/data/classifications/"):
    r"""Returns training, validation, or testing data, depending on the
    value of 'data_type'.  This function attempts to download the data
    if the file does not exist in 'data_dir'.  Returns x and y data
    for each subset.
    
    Parameters
    ----------
    data_type: str
        Request 'training', 'validation', or 'testing' data.
    data_dir: str
        Base directory in which to save the netcdf file. Default
        is "../data/pkls/".
    url: str
        Base url directory where the example data are located. Default
        is "http://svrimg.org/data/classifications/".
    x_: int
        Size of x dimension of original grid. Default is 1399.
    y_: int
        Size of y dimension of original grid. Default is 899.
    Returns
    -------
    x_y_data: ndarray
        A ndarray where the first dimension is a list of images, 
        and the second dimension is a list of classifications.
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
        if not os.path.exists(loc):
            _url = url + "2012_2013_validation.pkl"
            pkl = urlopen(_url)
            with open(loc, "wb") as file:
                file.write(pkl.read())
      
    elif data_type == 'testing':
        loc = "{}/2014_2017_test.pkl".format(data_dir)
        if not os.path.exists(loc):
            _url = url + "2014_2017_test.pkl"
            pkl = urlopen(_url)
            with open(loc, "wb") as file:
                file.write(pkl.read())
    else:
        print("Expected training, validation, or testing")
        return None
    return pickle.load(open(loc, "rb"))   


def read_image(filename):
    r"""Read and return raw image information based on a given filename.
    pilmode is "P", which allows the retrieval of actual data and not
    RGB intensity information.
    
    Parameters
    ----------
    filename: str
        File from which to read image information.

    Returns
    -------
    image: (M, N) ndarray
        An ndarray representation of the image
    """

    return imread(filename, pilmode='P')
    
def get_example(data_dir="../data/example/", url="http://svrimg.org/data/"):
    r"""Downloads an interpolated GridRad (gridrad.org) file from a url and
    returns an xarray dataset representation from April 27th at 1900 UTC.  
    If the file is already downloaded, it simply returns an xarray dataset 
    representation. This assumes that 'data_dir' exists.
    
    Parameters
    ----------
    data_dir: str
        Base directory in which to save the netcdf file. Default
        is "../data/example/".
    url: str
        Base url directory where the example data is located. Default
        is "http://svrimg.org/data/".

    Returns
    -------
    gridrad: dataset
        An xarray dataset representation of interpolated GridRad 
        data on April 27th at 1900 UTC.
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