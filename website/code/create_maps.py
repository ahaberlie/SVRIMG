import folium
import pandas as pd
from folium.plugins import MarkerCluster
import numpy as np
from folium import IFrame

def create_svrimg_map(svr_tab_loc, year, class_dict, c_lat, c_lon, zoom):
    """Creates a leaflet map for a given year and saves the svrgis information
    for that year to a csv.
    
    :param svr_tab_loc: str.  Location of svrgis csv file.
    :param year: numeric. Year for which you want to create a map.
    :param class_dict: dict. Dictionary of classification code 
                             and classification name
    :param c_lat: numeric. Center latitude of map.
    :param c_lon: numeric. Center longitude of map. 
    :param zoom: numeric. Zoom level of the map.
    :return: None.
    """
    
    leaf_map = folium.Map(location=[c_lat, c_lon], zoom_start=zoom)
    
    marker_cluster = MarkerCluster().add_to(leaf_map)
    
    try:
        svrgis = pd.read_csv(svr_tab_loc)
        svrgis = svrgis[svrgis.yr==year].copy()
        
        #Sorry PR, AK, HI!!
        svrgis = svrgis[~svrgis.st.isin(['PR', 'AK', 'HI'])].copy()
        
        for report_id, report_info in svrgis.iterrows():
        
            prefix = '../data/{}/_thumbspage'.format(report_info.yr)
            link = "{}/{}.png".format(prefix, report_id)

            date = "<p>{} UTC</p>".format(report_info.date_utc)
            mag_str = "<p>F/EF {}</p>".format(report_info.mag)
            
            button = ""
            for cl, clname in class_dict.items():
                button += "<button type=\"button\""
                button += " onclick=\"classify('{}',{})\"".format(rid, cl) 
                button += " id=\"{}\" name=\"{}\">{}</button><br><br>".format(clname, clname, clname)
                
            popup = date + mag_str + button

            try:
                icon = folium.features.CustomIcon(link, icon_size=(110,110))
                folium.Marker([row.slat, row.slon], icon=icon,  popup=popup,              
                       marker_icon='cloud').add_to(marker_cluster)
            except Exception as e:
                folium.Marker([row.slat, row.slon],                
                       marker_icon='cloud').add_to(marker_cluster)

                print(e)
                
        html_string = map_osm.get_root().render()
        html_file = open("{}_map.html".format(year), "w")
        html_file.write(html_string)
        html_file.close()
    
        df_.to_csv("{}_tor_utc_svrimg.csv".format(year))
        
        
if __name__ == "__main__":
        
    #Comment to run example
    pass
    
    ##Uncomment for example
    #classes = {0: "Cell", 1: "QLCS", 2: "Tropical", 3: "Other", 4: "Noise", 5: "Missing"}
    #create_svrimg_map(".../svrimg/data/csvs/96-17_tor_utc_svrimg_index.csv", 1996, classes, 35, -90, 5):
    