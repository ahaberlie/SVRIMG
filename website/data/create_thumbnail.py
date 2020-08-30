import os
import pandas as pd
from shutil import copyfile
import matplotlib.pyplot as plt
from imageio import imread
from PIL import Image
    
import os
import pandas as pd
from shutil import copyfile
import matplotlib.pyplot as plt
from imageio import imread
from PIL import Image
    
def create_thumnail(year, svrgis, cls):
    """Create a thumbnail for and image that has already been 
    downloaded for a given datetime.
    
    :param dtime: datetime.  Datetime of the thumbnail to save.
    :param svrimg: pandas DataFrame. svrimg index csv file.
    :return: None.
    """    
    folder = "sort/{}/".format(cls)
    
    if not os.path.exists(folder):
        os.makedirs(folder)

    for rid, row in svrgis.iterrows():
        infile = "../data/tor/{}/".format(year) + rid + ".png"
        img = imread(infile, pilmode='P')
        
        outfile = folder + "{}.png".format(rid)
        
        cmap = plt.cm.gist_ncar
        norm = plt.Normalize(vmin=1, vmax=80)

        image = cmap(norm(img))

        plt.imsave(outfile, np.flipud(image))
        
if __name__ == "__main__":       
        
    #Comment to run example
    pass   
    
    ##Uncomment for example
    # actual = get_pred_tables(data_dir="../data/csvs/", example=True, remove_first_row=True)

    # svrgis = get_svrgis_table(data_dir="../data/csvs/")

    # actual = actual.join(svrgis)

    # for cls in ['Cellular', 'QLCS', 'Tropical', 'Other', 'Noise', 'Missing']:
        
            # class_ = actual[actual["Class Name"]==cls].copy()
            # class_['date_utc'] = pd.to_datetime(class_.date_utc)
            
            # for yid, year in class_.groupby('yr'):
                # create_thumnail(yid, year, cls)