import pandas as pd
import numpy as np
import json as json


data = pd.read_csv('../../data/raw/orbf_benin.csv' , delimiter = ';')

import codecs
indicators_names = pd.read_json(codecs.open('../../data/raw/pbf_indicatorstranslations.json' , encoding = 'utf-8'))

## Keep only data with claimed and verified values
print('Length Complete Data :' + str(len(data)))
data = data[(np.isnan(data.indicator_claimed_value) == False) & (np.isnan(data.indicator_verified_value) == False)]
print('Length Data with claimed and verified complete :' + str(len(data)))

## Formatting facilities names for simplicity
data.entity_name[data.entity_name == 'CNHU-PPC (Centre National Hospitalier Universitaire Pneumo Phtysiologique de Cot CSC'] = "CNHU-PPC"
data.entity_name = data.entity_name.str.title()




## Format Date Variables
u = data['datafile_year'].astype(str) + '-' +  data['datafile_month'].astype(str)
data['date'] = pd.to_datetime(u)
data['period'] = data['date'].dt.to_period('M')

## Label Indicator names
indicators_list_names = indicators_names.loc[indicators_names.indicator_language == 'en' , ['indicator_id' , 'indicator_title']]
indicators_list_names.columns = ['indicator_id' , 'indicator_label']

data = pd.merge(data , indicators_list_names)

## Dropping some indicators
to_drop = ["Laboratoire" , "Planning familial" , "Salles d’hospitalisation" , "Consultation Externe / Urgences" , "Plan d’action" , "Hygiène & stérilisation" , "Bloc opératoire" , "Gestion du budget, des comptes et des biens" , "Indicateurs généraux" , "Gestion du malade" , "Médicaments traceurs" , "Nombre de patients contre-référés"]

data = data[~(data.indicator_label.isin(to_drop))]

to_export = ['entity_id' , 'entity_name' , 'entity_type' , 'parent_geozone_name' , 'geozone_name' , 'entity_fosa_id' ,  'content' , 'entity_status' , 'entity_active' , 'filetype_name' , 'filetype_id' , 'datafile_total' , 'datafile_author_id' , 'indicator_id' , 'indicator_label' , 'indicator_claimed_value' , 'indicator_verified_value' ,   'indicator_tarif' , 'indicator_montant' , 'entity_pop' , 'entity_pop_year' , 'geozone_pop' , 'geozone_pop_year' , 'parent_geozone_pop' , 'parent_geozone_pop_year' , 'period' , 'date']

data_out = data[to_export]


print('Final Length of data : ' , str(len(data_out)))
print('Exporting the Data in HD5 file')

store = pd.HDFStore('../../data/processed/orbf_benin.h5')
store['data'] = data_out
store.close()
