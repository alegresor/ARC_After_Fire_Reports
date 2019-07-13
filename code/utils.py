from collections import OrderedDict
from numpy import sqrt,nansum,nanmin,nanmax,nanmean,nanmean,nanstd,abs,sin,cos
from math import radians,atan2
import pandas as pd
import matplotlib.pyplot as matplotlib_plt
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster,HeatMap
# Plotly
from plotly.offline import plot as plotly_plt
from plotly import graph_objs
from plotly import tools
tools.set_credentials_file(username='alegresor', api_key='Z3RQvJzooCh3ib7nBNPg')

stat_fs = OrderedDict({
    'total': lambda x: nansum(x),
    'min_f': lambda x: nanmin(x),
    'max_f': lambda x: nanmax(x),
    'mean_f': lambda x: nanmean(x),
    'std_f': lambda x: nanstd(x),
    'zStat_f': lambda x: (x-nanmean(x))/nanstd(x),
    'uStat_f': lambda x: x/(nanmax(x)-nanmin(x))})

def ll_dist2(lat1,lng1,lat2,lng2):
    ''' Distance between 2 lat-lng points '''
    R = 6373
    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    C = 2 * atan2(sqrt(a), sqrt(1 - a))
    dist = R*C*0.621371
    return dist

def lookup_address(addr_str,geolocator=Nominatim()):
    addr_p = geolocator.geocode(addr_str)
    return addr_p,(addr_p.latitude,addr_p.longitude)

def get_nearby_df(this_lat,this_lng,df,radius=15):
    return df[df.apply(lambda row: ll_dist2(this_lat,this_lng,row['lat'],row['lng']),axis=1) <= radius]
    
def gen_stat_df(df,categories,stats):
    new_df = {'category':categories}
    for stat in stats:
        new_df[stat] = [stat_fs[stat](df[cat].values) for cat in categories]
    return pd.DataFrame(new_df)

def gen_figure(pltType,title,xlabel,ylabel,data_x,data_y,fname):
    if pltType == 'scatter':
        data = [graph_objs.Scatter(x=data_x,y=trend,name=name,mode ='markers') for name,trend in data_y.items()]
        layout = graph_objs.Layout(
            title= title,
            hovermode= 'closest',
            xaxis= dict(
                title = xlabel,
                ticklen = 5,
                zeroline = False,
                gridwidth = 2),
            yaxis=dict(
                title= ylabel,
                ticklen= 5,
                gridwidth= 2),
            showlegend = True)
        fig = graph_objs.Figure(data=data,layout=layout) 
        plotly_plt(fig,filename='templates/iframes/%s.html'%(fname),auto_open=False)
    if pltType == 'multipleBar':
        #total_adults_by_county = pd.pivot_table(incidents_df, values='Adults', index='County',aggfunc='sum')
        pass

def create_map(incidents_df,stations_df,location,zoom_start,outputName):
    # Construct Map
    incident_map = folium.Map(
        location = location,
        tiles = 'Stamen Toner',
        zoom_start = zoom_start,
        control_scale = True,
        prefer_canvas = True)
    # Shape Overlays
    #    Chicago Zip Codes
    folium.GeoJson(
        data = 'data/Chicago_ZipCodes.geojson',
        style_function = lambda x: {'fillColor':'#0d00ff','weight':2},
        name = 'Chicago Zip Code Shapes',
        show = False).add_to(incident_map)
    #    Chicago Neighborhoods
    folium.GeoJson(
        data = 'data/Chicago_Neighborhoods.geojson',
        style_function = lambda x: {'fillColor':'#00ffe1','weight':2},
        name = ' Chicago Neighborhood Shapes',
        show = False).add_to(incident_map)
    # Incidents
    incident_locations = incidents_df[['lat','lng']].values
    MarkerCluster(
        locations = incident_locations,
        icons = [folium.Icon(color='red',icon_color='white',icon='fire', prefix="fa",) for _ in range(len(incident_locations))],
        name = 'Incident Markers',
        show = True).add_to(incident_map)
    HeatMap(incident_locations,name='Incidents HeatMap',show=True).add_to(incident_map)
    # Fire Stations
    station_locations = stations_df[['lat','lng']].values
    MarkerCluster(
        locations = station_locations,
        icons = [folium.Icon(color='red',icon_color='white',icon='fire-extinguisher', prefix="fa",) for _ in range(len(station_locations))],
        name = 'Fire Station Markers',
        show = False).add_to(incident_map)
    HeatMap(station_locations,name='Fire Stations HeatMap',show=False).add_to(incident_map)
    # Layer Control
    folium.LayerControl().add_to(incident_map)
    # Save Map
    incident_map.save(outfile='templates/iframes/%s.html'%outputName)

if __name__ == '__main__':
    # Global DataFrames
    #    Incidents
    incidents_df_dirty = pd.read_csv('data/Incidents_Clean.csv')
    incidents_df_dirty.Zip = incidents_df_dirty.Zip.map(lambda zipStr: str(zipStr).split('.')[0])
    incidents_df = incidents_df_dirty.dropna(subset=['lat','lng'])
    #   Fire Stations
    stations_df = pd.read_csv('Data/Fire_Stations_Clean.csv')

    ''' Example Use of Functions '''
    # Create example address (str)
    fire1 = incidents_df.loc[0]
    addr_str_raw = '%s %s %s %s %s'%(fire1['Address'],fire1['City'],fire1['State'],fire1['Zip'],fire1['County'])
    print('\nLookUp Address: %s \n\tlat,lng: (%-.3f,%-.3f)'%(addr_str_raw,fire1['lat'],fire1['lng']))
    # Look up example address
    addr_str_clean,(addr_lat,addr_lng) = lookup_address(addr_str_raw)
    print('GeoCoded Address: %s \n\tlat,lng: (%-.3f,%-.3f)'%(addr_str_clean,addr_lat,addr_lng))
    # Get nearby incidents
    nearby_df = get_nearby_df(addr_lat,addr_lng,incidents_df,radius=15)
    print('\nNearby Incidents DataFrame (head):\n',nearby_df.head())
    
    ''' Generate Statics HTML files'''
    # Create scatter plot
    gen_figure(
        pltType = 'scatter',
        title = 'Fire_Injuries_Casualities_by_Adults_Present',
        xlabel = 'Adults',
        ylabel = 'Outcome',
        data_x = nearby_df['Adults'].values,
        data_y = {'Hospitalized':nearby_df['People Hospitalized'].values,
                'Deceased':nearby_df['People Deceased'].values},
        fname = 'plotly_Scatter_Static')
    # Get stats of nearby incidents
    nearby_stats_df = gen_stat_df(
        df=nearby_df,
        categories=['Units Destroyed','Units Major', 'Units Minor', 'Units Affected',
              'People Injured', 'People Hospitalized', 'People Deceased',
              'Adults', 'Children', 'Families','Assistance'],
        stats=['total','min_f','max_f','mean_f','std_f'])
    print('\nStats of Nearby DataFrame\n',nearby_stats_df)
    
    # Generate Folium Map
    create_map(incidents_df,stations_df,(41.8349,-87.6270),15,'folium_Map_Static')
    
    
    



