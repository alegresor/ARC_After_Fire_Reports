'''Sources
    https://blog.dominodatalab.com/creating-interactive-crime-maps-with-folium/
    https://www.jpytr.com/post/analysinggeographicdatawithfolium/
'''
import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Get Dataframes
incidents_df = pd.read_csv('Data/Incidents_Clean.csv')
stations_df = pd.read_csv('Data/Fire_Stations_Clean.csv')
sub_incidents_df = incidents_df.iloc[:100,:] # Temp
# Construct Map
incident_map = folium.Map(location=(41.8781,-87.6298), tiles='Stamen Toner', zoom_start=10)

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
    icons = [folium.Icon(icon=iconName, prefix="fa",) for _ in range(len(locations))]
    incident_map.add_child(MarkerCluster(locations=locations, icons=icons))


if __name__ == '__main__':
    add_cluster_markers(sub_incidents_df,'fire')
    #add_cluster_markers(stations_df,'fire-extinguisher')

    incident_map.save(outfile='templates/iframes/test_map.html')