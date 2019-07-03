"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from app1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Menu
    path('', views.index, name='index'),
    path('Incidents/', views.Incidents, name='Incidents'),
    path('Plots/', views.Plots, name='Plots'),
    path('About/', views.About, name='About'),
    # Incident SubPages
    path('Incidents/<incidentNum>', views.incidentSpecific, name = 'incidentSpecific'),
    # Util
    path('Plots/Plotly/<plotName>/', views.Plotly, name = 'Plotly'),
    path('download/<fName>/',views.download, name = 'download'),
    path('viewPDF/<fName>/', views.viewPDF, name = 'viewPDF')]
