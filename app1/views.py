import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, FileResponse
from wsgiref.util import FileWrapper
from code import incidents_df
incidents_df.sort_values(by=['date'],inplace=True,ascending=False)

# Menu
def index(request):
    incidents = incidents_df[['date','city','zip','county']].iloc[:4,:]
    incidents = incidents.to_html(index=False,classes="table table-striped table-dark")
    maps = ['USA']
    return render(request, 'index.html', {'incidents': incidents, 'maps':maps})
def Incidents(request):
    incidents = incidents_df[['date','city','zip','county','num_people_injured','num_people_hospitalized','num_people_deceased']].iloc[:49,:]
    incidents = incidents.to_html(index=False,classes="table table-striped table-dark")
    return render(request, 'Incidents/Incidents.html', {'incidents': incidents})
def Maps(request):
    maps = ['USA']
    return render(request, 'Maps/Maps.html', {'maps':maps})
def About(request):
    return render(request, 'About.html')

# Incident SubPages
def incidentSpecific(request,incidentNum):
    thisIncident = incidents_df.loc[incidents_df['incident_number'] == incidentNum]
    return render(request, 'incidentSpecific.html', {'incident': thisIncident})
def incidentSearch(request):
    if request.method == "POST":
        address = request.POST['address']
        radius = request.POST['radius']
        raise Exception("Incomplete Address Lookup View")         
    else: raise Http404

# Util
def QGIS(request, mapName):
    return render(request, 'Maps/QGIS/%s.html'%mapName)
def Plotly(request,plotName):
    return render(request, 'Incidents/Plotly/%s.html'%plotName)
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




