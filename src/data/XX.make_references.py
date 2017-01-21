## This script creates all orderings, colormaps, dictionnaries, that will be use throughout analysis and results displays.

import json
import pandas as pd
import numpy as np

store = pd.HDFStore('../../data/processed/orbf_benin.h5')
data = store['data']
store.close()


colormap = pd.read_csv('../../references/color_list.csv')['color_list'].tolist()


#### Create color map for Departements

order_zones = pd.DataFrame({'order':np.argsort(data.geozone_parentid.unique()) , 'zone_id':data.geozone_parentid.unique()})
zones = sorted(data.parent_geozone_name.unique().tolist())
zone_color_dico = {}
for u in range(len(zones)) :
    zone_color_dico[zones[u]] = colormap[u]

with open('../../references/departements_colors.json', 'w') as outfile:
    json.dump(zone_color_dico, outfile)
