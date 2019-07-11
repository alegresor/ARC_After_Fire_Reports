from collections import OrderedDict
from numpy import sqrt,nansum,nanmin,nanmax,nanmean,nanmean,nanstd,abs,sin,cos,arctan2
import pandas as pd
import matplotlib.pyplot as matplotlib_plt
from geopy.geocoders import Nominatim
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

def ll_dist2(ll1,ll2):
    ''' Distance between 2 lat-lng points '''
    dlat = ll1[0]  - ll2[0] 
    dlon = ll1[1] - ll2[1]
    a = sin(dlat/2)**2 + cos(ll1[0])*cos(ll2[0])*sin(dlon/2)**2 
    return 2*3958.8*arctan2(sqrt(a),sqrt(1-a)) 

def lookup_address(addr_str,geolocator=Nominatim()):
    addr_p = geolocator.geocode(addr_str)
    return addr_p,(addr_p.latitude,addr_p.longitude)

def get_nearby_df(this_lat,this_lng,df,radius=.01):
    return df[ll_dist2((this_lat,this_lng),(df['lat'],df['lng'])) <= radius]

def gen_figure(pltType,title,xlabel,ylabel,data_x,data_y,output,show):
    # defines plot type
    if pltType == 'scatter':
        # 
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
        plotly_plt(fig,filename='templates/Incidents/Plotly/%s.html'%(title))

def gen_stat_df(df,categories,stats):
    new_df = {'category':categories}
    for stat in stats:
        new_df[stat] = [stat_fs[stat](df[cat].values) for cat in categories]
    return pd.DataFrame(new_df)

incidents_df = pd.read_csv('data/Incidents_Clean.csv')

total_adults_by_county = pd.pivot_table(incidents_df, values='Adults', index='County',aggfunc='sum')



if __name__ == '__main__':
    ''' Example use of functions '''
    # Create example address (str)
    fire1 = incidents_df.loc[0]
    addr_str_raw = '%s %s %s %d %s'%(fire1['Address'],fire1['City'],fire1['State'],fire1['Zip'],fire1['County'])
    print('\nLookUp Address: %s \n\tlat,lng: (%-.3f,%-.3f)'%(addr_str_raw,fire1['lat'],fire1['lng']))
    # Look up example address
    addr_str_clean,(addr_lat,addr_lng) = lookup_address(addr_str_raw)
    print('GeoCoded Address: %s \n\tlat,lng: (%-.3f,%-.3f)'%(addr_str_clean,addr_lat,addr_lng))
    # Get nearby incidents
    nearby_df = get_nearby_df(addr_lat,addr_lng,incidents_df)
    print('\nNearby Incidents DataFrame (head):\n',nearby_df.head())
    # Create scatter plot
    gen_figure(
        pltType = 'scatter',
        title = 'Fire_Injuries_Casualities_by_Adults_Present',
        xlabel = 'Adults',
        ylabel = 'Outcome',
        data_x = nearby_df['Adults'].values,
        data_y = {'Hospitalized':nearby_df['People Hospitalized'].values,
                'Deceased':nearby_df['People Deceased'].values},
        output = True,show=True)
    # Get stats of nearby incidents
    nearby_stats_df = gen_stat_df(
        df=nearby_df,
        categories=['Units Destroyed','Units Major', 'Units Minor', 'Units Affected',
              'People Injured', 'People Hospitalized', 'People Deceased',
              'Adults', 'Children', 'Families','Assistance'],
        stats=['total','min_f','max_f','mean_f','std_f'])
    print('\nStats of Nearby DataFrame\n',nearby_stats_df)
    



