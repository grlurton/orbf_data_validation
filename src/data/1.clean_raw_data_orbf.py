import pandas as pd
import numpy as np

data = pd.read_csv('../../data/raw/orbf_benin.csv' , delimiter = ';')

## Keep only data with claimed and verified values

print('Length Complete Data :' + str(len(data)))
data = data[(np.isnan(data.indicator_claimed_value) == False) & (np.isnan(data.indicator_verified_value) == False) ]
print('Length Data with claimed and verified complete :' + str(len(data)))



## Formatting facilities names for simplicity
data.entity_name[data.entity_name == 'CNHU-PPC (Centre National Hospitalier Universitaire Pneumo Phtysiologique de Cot CSC'] = "CNHU-PPC"


data.entity_name = data.entity_name.str.title()
## Format Date Variables
u = data['datafile_year'].astype(str) + '-' +  data['datafile_month'].astype(str)
data['date'] = pd.to_datetime(u)
data['period'] = data['date'].dt.to_period('M')
