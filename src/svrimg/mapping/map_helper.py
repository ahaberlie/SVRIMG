import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
    
def radar_norm():
    r"""Return a colormap and normalization that allow you to represent
    radar data with colors every 5 dBZ that mimics the official NWS
    radar images.
    
    Parameters
    ----------
        
    Returns
    -------
    cmap: ListedColormap
        NWS-like radar colormap.
    norm: BoundaryNorm
        Normalization for 5 dBZ levels (0-80).
    """ 

    cmap = radar_colormap()
    classes = np.array(list(range(0, 85, 5)))
    norm = BoundaryNorm(classes, ncolors=cmap.N)    
    
    return cmap, norm
    
def radar_colormap():
    r"""Returns an NWS colormap.
    
      Color      dBZ

    "#04e9e7"    5
    
    "#019ff4"    10
    
    "#0300f4"    15
    
    "#02fd02"    20
    
    "#01c501"    25
    
    "#008e00"    30
    
    "#fdf802"    35
    
    "#e5bc00"    40
    
    "#fd9500"    45
    
    "#fd0000"    50
    
    "#d40000"    55
    
    "#bc0000"    60
    
    "#f800fd"    65
    
    "#9854c6"    70
    
    "#4B0082"    75
    
    "#000000"    80
    
    Parameters
    ----------
        
    Returns
    -------
    cmap: ListedColormap. NWS-like radar colormap.
    """ 
 
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
    
def draw_box_plot(ax, img, cbar_shrink=0.35):
    r"""Creates a pre-packaged display for indidivual or summary
    svrimg images.  Modifies an input axis.
    
    Parameters
    ----------
    ax: matplotlib.pyplot.axes.Axes
        Modifiable matplotlib.pyplot axis.
    cbar_shrink: numeric
        Value between 0 - 1.  This will be replacedwith kwargs in 
        future for more customization. Default is 0.35.
    Returns
    -------
    ax: matplotlib.pyplot.axes.Axes
        Modified matplotlib.pyplot axis.
    """ 

    cmap, norm = radar_norm()
    mmp = ax.imshow(np.flipud(img), cmap=cmap, norm=norm)
    ax.arrow(125.5, 119, 0, -0.0001, head_width=10, head_length=15, fc='k', ec='k', zorder=10)
    ax.text(121, 130, "N", fontsize=35, zorder=10)
    
    plt.colorbar(mmp, ax=ax, shrink=cbar_shrink, pad=0.01)
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
    
def draw_geography(ax):
    r"""Creates a pre-packaged display for United States geography.  
    Modifies an input axis.
    
    Parameters
    ----------
    ax: matplotlib.pyplot.axes.Axes
        Modifiable matplotlib.pyplot axis.
        
    Returns
    -------
    ax: matplotlib.pyplot.axes.Axes
        Modified matplotlib.pyplot axis.
    """ 
        
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