## This script creates all orderings, colormaps, dictionnaries, that will be use throughout analysis and results displays.

import json
import pandas as pd
import numpy as np

store = pd.HDFStore('../../data/processed/orbf_benin.h5')
data = store['data']
store.close()

colormap_dept = pd.read_csv('../../references/color_list.csv')['departements'].tolist()
colormap_indicators = pd.read_csv('../../references/color_list.csv')['indicateurs'].tolist()
color_dico = {}

#### Create color map for Departements
order_zones = pd.DataFrame({'order':np.argsort(data.geozone_name.unique()) , 'departement':data.geozone_name.unique()})
zones = sorted(data.parent_geozone_name.unique().tolist())
for u in range(len(zones)) :
    zone_color_dico[zones[u]] = colormap_dept[u]

#### Create color map for Facility Type
order_types = pd.DataFrame({'order':np.argsort(data.entity_type.unique()) , 'type':data.entity_type.unique()})
zones = sorted(data.entity_type.unique().tolist())
for u in range(len(order_types)) :
    zone_color_dico[zones[u]] = colormap_dept[u]

#### Create color map for Indicators

order_indicators = pd.DataFrame({'order':np.argsort(data.indicator_id.unique()) , 'indicator':data.indicator_id.unique()})
zones = sorted(data.indicator_id.unique().tolist())
for u in range(len(order_indicators)) :
    print(u)
    zone_color_dico[zones[u]] = colormap_indicators[u]

with open('../../references/departements_colors.json', 'w') as outfile:
    json.dump(zone_color_dico, outfile)
