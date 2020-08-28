import os
import pandas as pd
from shutil import copyfile
import matplotlib.pyplot as plt
from imageio import imread
from PIL import Image
    
def create_thumnail(dtime, svrimg):
    """Create a thumbnail for and image that has already been 
    downloaded for a given datetime.
    
    :param dtime: datetime.  Datetime of the thumbnail to save.
    :param svrimg: pandas DataFrame. svrimg index csv file.
    :return: None.
    """    
    folder = "sort/{}/".format(dtime.year)
    svrimg = svrimg[(svrimg.report_time.dt.year==dtime.year) & (svrimg.report_time.dt.month==dtime.month) & (svrimg.report_time.dt.day==dtime.day)].copy()
    
    if not os.path.exists(folder):
        os.makedirs(folder)

    for rid, row in svrimg.iterrows():
        infile = row.filename.split("/tor/")[-1]
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
    #svrimg_indexer = pd.read_csv(".../svrimg/data/csv/96-17_tor_utc_svrimg_index.csv")
    #start_date = '1996-01-01'
    #end_date = '1996-12-31'
    
    #for date_time in pd.date_range(start=start_date, end=end_date, freq='1D'):
    #    create_thumbnail(date_time, svrimg_indexer)