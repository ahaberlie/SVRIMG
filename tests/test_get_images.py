import logging
from imageio import imread
import numpy as np
from numpy.testing import assert_equal, assert_almost_equal, assert_array_almost_equal, assert_array_equal

from svrimg.utils.get_images import (_parse_str, _write_img, request_images, 
                                     get_img_list, geo_read_image, get_example_data, 
                                     read_image, get_example)
                                     
                                     

def test_parse_str():

    input_str = "199601010101"
    
    result = _parse_str(input_str)
    
    assert_equal(result, "http://svrimg.org/data/raw_img/1996/01/")
    
    input_str = "19960101"
    
    result = _parse_str(input_str)
    
    assert_equal(result, "http://svrimg.org/data/raw_img/1996/01/")


def test_write_image():

    test_img = np.load("test_imgs.npy")[3]
    
    save_dir = "./write_img/"
    url_dir = "http://svrimg.org/data/raw_img/2011/04/"
    img_name = "201104041350z000282677.png"
    
    _write_img(save_dir, url_dir, img_name)
    
    img = read_image(save_dir + img_name)
    
    assert_almost_equal(img, test_img)


def test_request_images():
    id_list = ['201104041310z000282671',
               '201104041338z000282673',
               '201104041340z000282676',
               '201104041350z000282677',
               '201104041408z000282156']
               
    data_dir = "./req_img/"
    
    img1, img2, img3, img4, img5 = np.load("test_imgs.npy")
    
    img_list = [img5, img4, img3, img2, img1]
    
    f_dict = request_images(id_list, data_dir)
    
    for id, filename in f_dict.items():
    
        img_tmp = read_image(filename)
        
        assert_almost_equal(img_tmp, img_list.pop())


def test_get_img_list():

    id_list = ['201104041310z000282671',
               '201104041338z000282673',
               '201104041340z000282676',
               '201104041350z000282677',
               '201104041408z000282156']
    
    data_dir = "./img_list/"
    
    test_img_list = np.load("test_imgs.npy")
    img_list = get_img_list(id_list, data_dir)
    assert_almost_equal(img_list, test_img_list)

    id_list = ['201104041310z000282671',
               '199001010101z000000000',
               '201104041340z000282676',
               '201104041350z000282677',
               '201104041408z000282156']

    test_img_list[1] = np.zeros(shape=(136, 136), dtype=np.uint8)
    img_list = get_img_list(id_list, data_dir, keep_missing=True)
    assert_almost_equal(img_list, test_img_list)
    
    test_img_list = np.delete(test_img_list, 1, axis=0)
    img_list = get_img_list(id_list, data_dir)
    assert_almost_equal(img_list, test_img_list)

def test_geo_read_image():

    import pandas as pd
    
    d = {'UNID':["201104271836z000303011"], 'xmax':[961], 
         'xmin':[826], 'ymax':[397], 'ymin':[262]}

    test_index = pd.DataFrame.from_dict(d)
    test_index = test_index.set_index("UNID")
    
    f_dict = request_images(["201104271836z000303011"], "./georead/")

    test_img = np.load("geo_img.npy")
    
    g_img = geo_read_image(test_index, f_dict, "201104271836z000303011")
    
    assert_almost_equal(test_img, g_img)


def test_read_image():

    test_img = imread("test_img.png", pilmode='P')
    
    img = read_image("test_img.png")
    
    assert_almost_equal(img, test_img)