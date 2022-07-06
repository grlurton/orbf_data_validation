## This script creates all orderings, colormaps, dictionnaries, that will be use throughout analysis and results displays.

import json
import pandas as pd
import numpy as np

store = pd.HDFStore('data/processed/orbf_benin.h5')
data = store['data']
store.close()


colormap_dept = pd.read_csv('references/color_list.csv')['departements'].tolist()
colormap_indicators = pd.read_csv('references/color_list.csv')['indicateurs'].tolist()

color_dico = {}
#### Create color map for Departements
order_zones = pd.DataFrame({'order':np.argsort(data.geozone_name.unique()) , 'departement':data.geozone_name.unique()})
zones = sorted(data.parent_geozone_name.unique().tolist())
for u in range(len(zones)) :
    color_dico[zones[u]] = colormap_dept[u]

#### Create color map for Facility Type
order_types = pd.DataFrame({'order':np.argsort(data.entity_type.unique()) , 'type':data.entity_type.unique()})
zones = sorted(data.entity_type.unique().tolist())
for u in range(len(order_types)) :
    color_dico[zones[u]] = colormap_dept[u]

with open('references/departements_colors.json', 'w') as outfile:
    json.dump(color_dico, outfile)

## Make tarifs as a List
tarifs = []
for i in data_orbf.indicator_label.unique() :
    tarifs.append(data.indicator_tarif[data.indicator_label == i].tolist()[0])
tarifs = pd.Series(tarifs , index = data.indicator_label.unique())

tarifs.to_hdf('data/processed/orbf_benin.h5' , 'tarifs')
