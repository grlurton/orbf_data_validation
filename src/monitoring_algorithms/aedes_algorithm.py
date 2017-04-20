import pandas as pd
import pickle
import numpy as np

# For warnings
import warnings
warnings.filterwarnings('ignore')

bm_zones =['OUIDAH-KPOMASSE-TORI-BOSSITO', 'BANIKOARA', 'LOKOSSA-ATHIEME' , 'ADJOHOUN-BONOU-DANGBO',       'KOUANDE-OUASSA-PEHUNCO-KEROU','COVE-ZANGNANADO-OUINHI', 'PORTONOVO-AGUEGUES-SEME-PODJI', 'BOHICON-ZAKPOTA-ZOGBODOMEY']

pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()
store = pd.HDFStore('../../data/processed/orbf_benin.h5')
tarifs = store['tarifs']
data = store['data']
store.close()

pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()

data = data.set_index('indicator_label')

data['value_claimed'] = list(data.indicator_claimed_value * tarifs)
data['value_verified'] = list(data.indicator_verified_value * tarifs)

a = data['value_claimed'] - data['value_verified']
data = data[a != max(a)]

u = data.period.apply(str).str[0:4]
print(len(data))
data = data[u == '2016']
print(len(data))
data = data[data.geozone_name.isin(bm_zones)]
print(len(data))

total_recupere = sum(data['value_claimed'] - data['value_verified'])

def get_ecarts(data , total):
    return sum(data['value_claimed'] - data['value_verified']) / total

ecarts = data.groupby(level = 0).apply(get_ecarts , total = total_recupere).sort_values(ascending = False)

## Getting out extreme values

ecarts
ecarts.cumsum()

max(a)


np.nanmax(a[0])
data['value_verified']
data['value_claimed']
