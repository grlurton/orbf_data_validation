import pandas as pd
import numpy as np
import json as json
import os
from dotenv import load_dotenv, find_dotenv

# find .env automagically by walking up directories until it's found
dotenv_path = find_dotenv()

# load up the entries as environment variables
load_dotenv(dotenv_path)

benin_path = os.environ.get("data_benin")



data = pd.read_csv(benin_path + 'orbf_benin.csv' , delimiter = ';')

#import codecs
#indicators_names = pd.read_json(codecs.open(benin_path + 'pbf_indicatorstranslations.json' , encoding = 'utf-8'))
indicators_names = pd.read_json(benin_path + 'pbf_indicatorstranslations.json')

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

## Dropping some Reports
to_drop = ['Evaluation Trimestrielle Qualite PMA' , 'Evaluation Trimestrielle Qualite PCA' , 'Quantites CHD' ,  'FBR Communautaire Quantité' , 'Facture Mensuelle PCA']
data = data[~(data.filetype_name.isin(to_drop))]

## Dropping some reports
to_drop = ["Distribution des MII (femme enceinte)" , "Femmes enceintes VAT completement vaccinees (VAT 2-5)" , "Deuxieme prise de Sulfadoxine femme enceinte" , "Planification Familiale" , "Consultation Postnatale" , "Activites generales" ]
data = data[~(data.indicator_label.isin(to_drop))]



## dropping facility months with no correction

drop_no_correction = False


def make_fac_desc(data) :
    data['correction'] = (data.indicator_claimed_value == data.indicator_verified_value)
    perc_right = sum(data['correction']) / len(data)

    return pd.DataFrame([perc_right])

fac_desc = data.groupby(['entity_name' , 'period']).apply(make_fac_desc).reset_index()
fac_desc.columns = ['entity_name' ,'period' , 'level_1'  , 'percent_right']

full_data = fac_desc[fac_desc.percent_right < 1]
full_data = full_data[['entity_name' ,'period']]

dat_to_keep = data

if drop_no_correction == True :
    dat_to_keep = pd.merge(data , full_data , on = ['entity_name' ,'period'])

to_export = ['entity_id' , 'entity_name' , 'entity_type' , 'parent_geozone_name' , 'geozone_name' , 'entity_fosa_id' ,  'content' , 'entity_status' , 'entity_active' , 'filetype_name' , 'filetype_id' , 'datafile_total' , 'datafile_author_id' , 'indicator_id' , 'indicator_label' , 'indicator_claimed_value' , 'indicator_verified_value' ,   'indicator_tarif' , 'indicator_montant' , 'entity_pop' , 'entity_pop_year' , 'geozone_pop' , 'geozone_pop_year' , 'parent_geozone_pop' , 'parent_geozone_pop_year' , 'period' , 'date']

data_out = dat_to_keep[to_export]

print('Final Length of data : ' , str(len(data_out)))
print('Exporting the Data in HD5 file')

store = pd.HDFStore('data/processed/orbf_benin.h5')
store['data'] = data_out
store.close()
