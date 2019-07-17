import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, FileResponse
from wsgiref.util import FileWrapper
import pandas as pd
# Local Imports
from code import lookup_address,get_nearby_df,gen_stat_df,create_map,gen_figure

# Global DataFrames
#    Incidents
incidents_df_dirty = pd.read_csv('data/Incidents_Clean.csv')
incidents_df_dirty.Zip = incidents_df_dirty.Zip.map(lambda zipStr: str(zipStr).split('.')[0])
incidents_df = incidents_df_dirty.dropna(subset=['lat','lng'])
incidents_df.sort_values(by=['Date'],inplace=True,ascending=False)
#   Fire Stations
stations_df = pd.read_csv('Data/Fire_Stations_Clean.csv')

# Menu
def index(request): return render(request, 'index.html')
def Incidents(request):
    if request.method == "POST": return incidentSearch(request,str(request.POST['address']),radius = float(request.POST['radius']))  
    incidents = incidents_df[['Date','City','Zip','County','People Injured','People Hospitalized','People Deceased']].iloc[:49,:]
    incidents = incidents.to_html(index=False,classes="table table-striped table-dark")
    return render(request, 'Incidents.html', {'incidents': incidents})
def Plots(request):
    return render(request,'Plots.html')
def About(request):
    return render(request, 'About.html')

# Incident SubPages
def incidentSpecific(request,incidentNum):
    thisIncident = incidents_df.loc[incidents_df['Incident Number'] == incidentNum]
    return render(request, 'incidentSpecific.html', {'incident': thisIncident})
def incidentSearch(request,address,radius):
    parsedAddress,(addr_lat,addr_lng) = lookup_address(address)
    nearby_incidents_df = get_nearby_df(addr_lat,addr_lng,incidents_df,radius=radius)
    nearby_stations_df = get_nearby_df(addr_lat,addr_lng,stations_df,radius=radius)
    if len(nearby_incidents_df)==0 or len(nearby_stations_df)==0:
        return render(request,'Incidents/incidentSearchError.html')
    # Get Stats
    nearby_stats_df = gen_stat_df(
        df=nearby_incidents_df,
        categories=['Units Destroyed','Units Major', 'Units Minor', 'Units Affected',
            'People Injured', 'People Hospitalized', 'People Deceased',
            'Adults', 'Children', 'Families','Assistance'],
        stats=['total','min_f','max_f','mean_f','std_f'])
    # Gen Map
    create_map(nearby_incidents_df,nearby_stations_df,(addr_lat,addr_lng),16,'folium_Map_TMP')
    # Gen Plots
    gen_figure(
        pltType = 'scatter',
        title = 'Fire Injuries and Casualities by Adults Present',
        xlabel = 'Adults',
        ylabel = 'Outcome',
        data_x = nearby_incidents_df['Adults'].values,
        data_y = {'Hospitalized':nearby_incidents_df['People Hospitalized'].values,
                'Deceased':nearby_incidents_df['People Deceased'].values},
        fname='plotly_Scatter_TMP')
    xaxis = 'County'
    total_injured_by_county = pd.pivot_table(nearby_incidents_df,values='People Injured',index=xaxis,aggfunc='sum')
    total_unitsAffected_by_county = pd.pivot_table(nearby_incidents_df,values='Units Affected',index=xaxis,aggfunc='sum')
    gen_figure(
        pltType = 'multiBar',
        title = 'People and Units Affected by County',
        xlabel = 'County',
        ylabel = 'Affects',
        data_x = total_injured_by_county.index.values,
        data_y = {
            'People Injured':total_injured_by_county.values.flatten(),
            'Units Affected':total_unitsAffected_by_county.values.flatten()},
        fname = 'plotly_MultiBar_TMP')
    # Convert incidents and stats dataframes to HTML
    nearbyIncidents = nearby_incidents_df[['Date','Address','Zip','lat','lng','People Injured','People Hospitalized','People Deceased']].to_html(index=False,classes="table table-striped table-dark")
    nearbyIncidentsStats = nearby_stats_df.to_html(index=False,classes="table table-striped table-dark")
    nearbyIncidentsStats.columns = ['Category','Total','Min','Max','Average','Standard Deviation']
    return render(request,'Incidents/incidentSpecific.html',
            {'parsedAddress': parsedAddress,
            'nearbyIncidents': nearbyIncidents,
            'nearbyIncidentsStats': nearbyIncidentsStats})
# Util
def iframe(request,plotName):
    return render(request, 'iframes/%s.html'%plotName)
def download(request, fName):
    fPath = os.path.join(settings.MEDIA_ROOT, fName)
    if os.path.exists(fPath):
        with open(fPath, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(fPath)
            return response
    raise Http404
def viewPDF(request, fName):
    fPath = os.path.join(settings.MEDIA_ROOT, fName)
    try:
        return FileResponse(open(fPath, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()




