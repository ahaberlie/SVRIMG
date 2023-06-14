import numpy as np
import os
from numpy.testing import assert_equal, assert_almost_equal

from svrimg.utils.get_images import (_parse_str, request_images,
                                     get_img_list, geo_read_image,
                                     read_image)
                                     
test_data_dir = "data/test/"                                  


def test_parse_str():

    input_str = "199601010101"
    
    result = _parse_str(input_str, "tor")
    
    assert_equal(result, "https://nimbus.niu.edu/svrimg/data/tor/1996/01/")
    
    input_str = "19960101"
    
    result = _parse_str(input_str, "tor")
    
    assert_equal(result, "https://nimbus.niu.edu/svrimg/data/tor/1996/01/")


def test_request_images():
    id_list = ['201104041310z000282671',
               '201104041338z000282673',
               '201104041340z000282676',
               '201104041350z000282677',
               '201104041408z000282156']
               
    data_dir = test_data_dir + "req_img/"
    
    img1, img2, img3, img4, img5 = np.load(test_data_dir + "test_imgs.npy")
    
    img_list = [img5, img4, img3, img2, img1]
    
    f_dict = request_images(id_list, haz_type="tor", data_dir=data_dir)
    
    for _, filename in f_dict.items():
    
        img_tmp = read_image(filename)
        
        assert_almost_equal(img_tmp, img_list.pop())


def test_get_img_list():

    id_list = ['201104041310z000282671',
               '201104041338z000282673',
               '201104041340z000282676',
               '201104041350z000282677',
               '201104041408z000282156']
    
    data_dir = test_data_dir + "/img_list/"
    
    test_img_list = np.load(test_data_dir + "test_imgs.npy")
    img_list = get_img_list(id_list, haz_type="tor", data_dir=data_dir)
    assert_almost_equal(img_list, test_img_list)

    id_list = ['201104041310z000282671',
               '199001010101z000000000',
               '201104041340z000282676',
               '201104041350z000282677',
               '201104041408z000282156']

    test_img_list[1] = np.zeros(shape=(136, 136), dtype=np.uint8)
    img_list = get_img_list(id_list, haz_type="tor", data_dir=data_dir, keep_missing=True)
    assert_almost_equal(img_list, test_img_list)
    
    test_img_list = np.delete(test_img_list, 1, axis=0)
    img_list = get_img_list(id_list, haz_type="tor", data_dir=data_dir)
    assert_almost_equal(img_list, test_img_list)


def test_geo_read_image():

    import pandas as pd
    
    d = {'UNID': ["201104271836z000303011"], 'xmax': [961],
         'xmin': [826], 'ymax': [397], 'ymin': [262]}

    test_index = pd.DataFrame.from_dict(d)
    test_index = test_index.set_index("UNID")
    
    f_dict = request_images(["201104271836z000303011"], "tor", test_data_dir + "georead/")

    test_img = np.load(test_data_dir + "geo_img.npy")
    
    g_img = geo_read_image(test_index, f_dict, "201104271836z000303011")
    
    assert_almost_equal(test_img, g_img)
