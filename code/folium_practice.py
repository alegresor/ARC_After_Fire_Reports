'''Sources
    https://blog.dominodatalab.com/creating-interactive-crime-maps-with-folium/
    https://www.jpytr.com/post/analysinggeographicdatawithfolium/
'''
import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Get Dataframes
incidents_df = pd.read_csv('Data/Incidents_Clean.csv')
incidents_df.Zip = incidents_df.Zip.map(lambda zipStr: str(zipStr).split('.')[0])
incidents_df.dropna(subset=['lat','lng'],inplace=True)
stations_df = pd.read_csv('Data/Fire_Stations_Clean.csv')
# Construct Map
incident_map = folium.Map(location=(41.8349,-87.6270), tiles='Stamen Toner', zoom_start=15)

# Individual Markers
def add_individual_markers(df):
    # Would need to rename stations headers for it to work on that df
    for i,row in df.iterrows():
        this_LatLng = [row['lat'],row['lng']]
        this_address = '%s,\n%s, %s, %s, %s'%\
            (row['Address'],row['City'],row['State'],str(row['Zip']).split('.')[0],row['County'])
        incident_map.add_child(folium.Marker(this_LatLng, popup=this_address))

# Incident and Station Locations
def add_cluster_markers(df,iconName):
    locations = list(zip(df.lat, df.lng))
    icons = [folium.Icon(color='red',icon_color='white',icon=iconName, prefix="fa",) for _ in range(len(locations))]
    incident_map.add_child(MarkerCluster(locations=locations, icons=icons))

if __name__ == '__main__':
    add_cluster_markers(incidents_df,'fire')
    #add_cluster_markers(stations_df,'fire-extinguisher')

    
    folium.Choropleth(
        geo_data = 'data/Chicago_ZipCodes.geojson',
        data = incidents_df,
        columns = ['Zip', 'People Injured'],
        key_on = 'feature.properties.zip',
        fill_color = 'YlGn',
        legend_name='Total Assistance Given').add_to(incident_map)

    incident_map.save(outfile='templates/iframes/test_map.html')