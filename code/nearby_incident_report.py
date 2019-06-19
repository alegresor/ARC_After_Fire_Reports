from collections import OrderedDict
from numpy import sqrt,nansum,nanmin,nanmax,nanmean,nanmean,nanstd,abs
import pandas as pd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

stat_fs = OrderedDict({
    'total': lambda x: nansum(x),
    'min_f': lambda x: nanmin(x),
    'max_f': lambda x: nanmax(x),
    'mean_f': lambda x: nanmean(x),
    'std_f': lambda x: nanstd(x),
    'zStat_f': lambda x: (x-nanmean(x))/nanstd(x),
    'uStat_f': lambda x: x/(nanmax(x)-nanmin(x))})
ll_dist2 = lambda ll1,ll2: sqrt((ll1[0]-ll2[0])**2+(ll1[1]-ll2[1])**2)

def lookup_address(addr_str,geolocator=Nominatim()):
    addr_p = geolocator.geocode(addr_str)
    return addr_p,(addr_p.latitude,addr_p.longitude)


def get_nearby_df(this_lat,this_lng,df,radius=.01):
    return df[ll_dist2((this_lat,this_lng),(df['lat'],df['lng'])) <= radius]

def gen_figure(pltType,title,xlabel,ylabel,data_x,data_y,output,show):
    if pltType == 'scatter':
        fig, ax = plt.subplots()
        fig.suptitle(title,color='blue')
        ax.set_xlabel(xlabel,color='blue')
        ax.set_ylabel(ylabel,color='blue')
        for name,(trend,color) in data_y.items():
            plt.scatter(data_x,trend,color=color,label=name)
        plt.legend()
        if output: plt.savefig('output/Figures/%s.png'%(title),dpi=150) 
        if show: plt.show()

def gen_stat_df(df,categories,stats):
    new_df = {'category':categories}
    for stat in stats:
        new_df[stat] = [stat_fs[stat](df[cat].values) for cat in categories]
    return pd.DataFrame(new_df)

if __name__ == '__main__':
    ''' Example use of functions '''
    # Create example address (str)
    incidents_df = pd.read_csv('data/Incidents_Clean.csv')
    fire1 = incidents_df.loc[0]
    addr_str_raw = '%s %s %s %d %s'%(fire1['address'],fire1['city'],fire1['state'],fire1['zip'],fire1['county'])
    print('\nLookUp Address: %s \n\tlat,lng: (%-.3f,%-.3f)'%(addr_str_raw,fire1['lat'],fire1['lng']))
    # Look up example address
    addr_str_clean,(addr_lat,addr_lng) = lookup_address(addr_str_raw)
    print('GeoCoded Address: %s \n\tlat,lng: (%-.3f,%-.3f)'%(addr_str_clean,addr_lat,addr_lng))
    # Get nearby incidents
    nearby_df = get_nearby_df(addr_lat,addr_lng,incidents_df)
    print('\nNearby Incidents DataFrame:\n',nearby_df.head())
    # Create scatter plot
    gen_figure(
        pltType = 'scatter',
        title = 'Fire Injuries and Casualities by Adults Present',
        xlabel = 'Adults',
        ylabel = 'Outcome',
        data_x = nearby_df['num_adults'].values,
        data_y = {'Hospitalized':(nearby_df['num_people_hospitalized'].values,'green'),
                'Deceased':(nearby_df['num_people_deceased'].values,'red')},
        output = True,show=True)
    # Get stats of nearby incidents
    nearby_stats_df = gen_stat_df(
        df=nearby_df,
        categories=['units_destroyed','units_major', 'units_minor', 'units_affected',
              'num_people_injured', 'num_people_hospitalized', 'num_people_deceased',
              'num_adults', 'num_children', 'num_families','assistance_given'],
        stats=['total','min_f','max_f','mean_f','std_f'])
    print('\nStats of Nearby DataFrame\n',nearby_stats_df)
    



