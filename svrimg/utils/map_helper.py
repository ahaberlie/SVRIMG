import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
import matplotlib.patheffects as PathEffects
import numpy as np

def draw_box(lon, lat, tree, pmm_image, out_image, out_shape):
    
    d, pos = tree.query([lon, lat], k=1, distance_upper_bound=.1)
    mid = int((512 / 2) / 2)

    y, x = np.unravel_index(pos, shape=out_shape)

    y_ = y-mid
    x_ = x-mid

    z_pt = np.where(pmm_image>=1)

    x_z = z_pt[1]
    y_z = z_pt[0]

    out_image[y_ + y_z, x_ + x_z] = pmm_image[y_z, x_z] 

def plot_box_stats(ax, grid_count):

    delta = 512000
    y_0 = 860000
    x_0 = -930000

    l_y = 1250000
    l_x = -930000

    i = 1
    for y in range(0, 5):
        for x in range(0, 6):
            txt = ax.text(x_0 + (x*delta), y_0 - (y*delta), "n={}".format(grid_count[i]), fontsize=14, zorder=8)
            txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground='w')])

            txt = ax.text(l_x + (x*delta), l_y - (y*delta), "{}".format(i), fontsize=14, zorder=8)
            txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground='w')])
            i += 1
            
    return ax

def coords(gx, gy):
    r"""Calculate x,y coordinates of each grid cell.
    Parameters
    ----------
    gx: numeric
        x coordinates in meshgrid
    gy: numeric
        y coordinates in meshgrid
    Returns
    -------
    (X, Y) ndarray
        List of coordinates in meshgrid
    """
    return np.vstack([gx.ravel(), gy.ravel()]).T
    
def radar_norm():

    cmap = radar_colormap()
    classes = np.array(list(range(0, 85, 5)))
    norm = BoundaryNorm(classes, ncolors=cmap.N)    
    
    return cmap, norm
    
def radar_colormap():

    nws_reflectivity_colors = [ "#ffffff", # 0
                                "#04e9e7", # 5
                                "#019ff4", # 10
                                "#0300f4", # 15
                                "#02fd02", # 20
                                "#01c501", # 25
                                "#008e00", # 30
                                "#fdf802", # 35
                                "#e5bc00", # 40
                                "#fd9500", # 45
                                "#fd0000", # 50
                                "#d40000", # 55
                                "#bc0000", # 60
                                "#f800fd", # 65
                                "#9854c6", # 70
                                "#4B0082", # 75
                                "#000000"]
                                
    cmap = ListedColormap(nws_reflectivity_colors)
    

    return cmap
    
def draw_box_plot(ax, img):

    cmap, norm = radar_norm()
    mmp = ax.imshow(np.flipud(img), cmap=cmap, norm=norm)
    ax.arrow(125.5, 119, 0, -0.5, head_width=10, head_length=15, fc='k', ec='k', zorder=10)
    ax.text(120, 130, "N", fontsize=35, zorder=10)
    plt.colorbar(mmp, ax=ax, shrink=0.2, pad=0.01)
    ax.set_yticks(list(range(0, 153, 17)))
    ax.set_yticklabels([  0  ,  64, 128 , 192, 256  , 320, 
                        384 , 448, 512])
    ax.set_xticks(list(range(0, 153, 17)))
    ax.set_xticklabels([  0  ,  64, 128 , 192, 256  , 320, 
                        384 , 448, 512])
    ax.set_xlabel("km")
    ax.set_ylabel("km")
    ax.grid()
    
    return ax
    
def draw_geography(ax, geo_data_dir='../data/geo'):
        
    countries_shp = shpreader.natural_earth(resolution='50m',
                                     category='cultural',
                                     name='admin_0_countries')
    
    for country, info in zip(shpreader.Reader(countries_shp).geometries(), 
                             shpreader.Reader(countries_shp).records()):
        if info.attributes['NAME_LONG'] != 'United States':

            ax.add_geometries([country], ccrs.PlateCarree(),
                             facecolor='lightgrey', edgecolor='k', zorder=6)
            
    lakes_shp = shpreader.natural_earth(resolution='50m',
                                     category='physical',
                                     name='lakes')
    
    for lake, info in zip(shpreader.Reader(lakes_shp).geometries(), 
                             shpreader.Reader(lakes_shp).records()):
        name = info.attributes['name']
        if name == 'Lake Superior' or name == 'Lake Michigan' or \
           name == 'Lake Huron' or name == 'Lake Erie' or name == 'Lake Ontario':
            
            ax.add_geometries([lake], ccrs.PlateCarree(),
                             facecolor='lightsteelblue', edgecolor='k', zorder=6)
            
    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'ocean', '50m', edgecolor='face', 
                                                facecolor='lightsteelblue'), zorder=6)
    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'coastline', '50m', edgecolor='face', 
                                                facecolor='None'), zorder=6) 
    

    shapename = geo_data_dir + "/grid512km_latlon.shp"

    for grid, info in zip(shpreader.Reader(shapename).geometries(), shpreader.Reader(shapename).records()):

        ax.add_geometries([grid], ccrs.PlateCarree(),
                              facecolor='white', edgecolor='k')
            
    for grid, info in zip(shpreader.Reader(shapename).geometries(), shpreader.Reader(shapename).records()):

        ax.add_geometries([grid], ccrs.PlateCarree(), linewidth=3,
                              facecolor='None', edgecolor='k', zorder=7)
                              
    shapename = 'admin_1_states_provinces_lakes_shp'
    states_shp = shpreader.natural_earth(resolution='50m',
                                     category='cultural', name=shapename)

    for state, info in zip(shpreader.Reader(states_shp).geometries(), shpreader.Reader(states_shp).records()):
        if info.attributes['admin'] == 'United States of America':

            ax.add_geometries([state], ccrs.PlateCarree(),
                              facecolor='white', edgecolor='k')
            
    for state, info in zip(shpreader.Reader(states_shp).geometries(), shpreader.Reader(states_shp).records()):
        if info.attributes['admin'] == 'United States of America':

            ax.add_geometries([state], ccrs.PlateCarree(),
                              facecolor='None', edgecolor='k', zorder=6)

    return ax