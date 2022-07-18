import json
import pandas as pd
from collections import OrderedDict
import plotly.express as px
# reading the JSON data using json.load()
data = {}
data['lat'] = []
data['long'] = []
data['city'] = []
data['state'] = []
data['country'] = []
input_path = 'opiates_2020_3_1_.txt'
with open(input_path, 'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        jo = json.loads(line, object_pairs_hook=OrderedDict)
        try:
            data['long'].append(jo['place']['bounding_box']['coordinates'][0][0][0])
            data['lat'].append(jo['place']['bounding_box']['coordinates'][0][0][1])
            data['city'].append(jo['place']['full_name'].split(',')[0])
            data['state'].append(jo['place']['full_name'].split(',')[1])
            data['country'].append(jo['place']['country_code'])
        except TypeError:
            data['long'].append(None)
            data['lat'].append(None)
            data['city'].append(None)
            data['state'].append(None)
            data['country'].append(None)

# data_df = pd.DataFrame.from_dict(data).dropna()
# px.set_mapbox_access_token('pk.eyJ1IjoidGFubW95c3IiLCJhIjoiY2s5aDc2cjZoMHMzMTNscGhtcTA0MHZkOSJ9.ElGEgw3N2aEk1hFLjB7vng')
# # df = px.data.carshare()
# # fig = px.scatter_mapbox(df, lat="centroid_lat", lon="centroid_lon",     color="peak_hour", size="car_hours",
# #                   color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
#
# fig = px.scatter_mapbox(data_df, lat="lat", lon="long",color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
# fig.show()