import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, FileResponse
from wsgiref.util import FileWrapper
from code import incidents_df,lookup_address,get_nearby_df,gen_stat_df
incidents_df.sort_values(by=['Date'],inplace=True,ascending=False)

# Menu
def index(request):
    if request.method == "POST": return incidentSearch(request,str(request.POST['address']),radius = float(request.POST['radius']))  
    incidents = incidents_df[['Date','City','Zip','County']].iloc[:4,:]
    incidents = incidents.to_html(index=False,classes="table table-striped table-dark")
    return render(request, 'index.html', {'incidents': incidents})
def Incidents(request):
    if request.method == "POST": return incidentSearch(request,str(request.POST['address']),radius = float(request.POST['radius']))  
    incidents = incidents_df[['Date','City','Zip','County','People Injured','People Hospitalized','People Deceased']].iloc[:49,:]
    incidents = incidents.to_html(index=False,classes="table table-striped table-dark")
    return render(request, 'Incidents/Incidents.html', {'incidents': incidents})
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
    nearby_df = get_nearby_df(addr_lat,addr_lng,incidents_df,radius=radius)
    nearby_stats_df = gen_stat_df(
    df=nearby_df,
    categories=['Units Destroyed','Units Major', 'Units Minor', 'Units Affected',
        'People Injured', 'People Hospitalized', 'People Deceased',
        'Adults', 'Children', 'Families','Assistance'],
    stats=['total','min_f','max_f','mean_f','std_f'])
    '''
    gen_figure(
        pltType = 'scatter',
        title = 'Fire_Injuries_Casualities_by_Adults_Present',
        xlabel = 'Adults',
        ylabel = 'Outcome',
        data_x = nearby_df['Adults'].values,
        data_y = {'Hospitalized':nearby_df['People Hospitalized'].values,
                'Deceased':nearby_df['People Deceased'].values},
        output = True,show=True)
    '''
    nearbyIncidents = nearby_df[['Date','Address','Zip','lat','lng','People Injured','People Hospitalized','People Deceased']].to_html(index=False,classes="table table-striped table-dark")
    nearbyIncidentsStats = nearby_stats_df.to_html(index=False,classes="table table-striped table-dark")
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




