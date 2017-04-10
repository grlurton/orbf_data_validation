import ipyparallel
from facility_monitoring import *

# For warnings
import warnings
warnings.filterwarnings('ignore')

## Create Clusted

#  ipcluster start -n 4

clients = ipyparallel.Client()
dview = clients[:]


store = pd.HDFStore('../../data/processed/orbf_benin.h5')
data_orbf = store['data']
store.close()

mean_supervision_cost = 170000
underfunding_max_risk = 0.5
tarifs = []
for i in data_orbf.indicator_label.unique() :
    tarifs.append(data_orbf.indicator_tarif[data_orbf.indicator_label == i].tolist()[0])
tarifs = pd.Series(tarifs , index = data_orbf.indicator_label.unique())

## Making General Verification Trail :
fac_ids = []
for fac_id in data_orbf.entity_id.unique():
    fac_data = data_orbf[data_orbf.entity_id == fac_id]
    fac_ids.append(fac_data)


def run(fac_id , data_orbf = data_orbf):
    facility_data = data_orbf[data_orbf.entity_id == fac_id]
    min_date = str(min(facility_data.date))
    new_facility = facility(facility_data , tarifs)
    new_facility.initiate_training_set(min_date)
    new_facility.make_supervision_trail(tarifs , mean_supervision_cost , underfunding_max_risk)
    return new_facility

fac_id_test = fac_ids[0:5]

result = dview.map_async(run , fac_id_test)
len(result)

a = result.get()

#import pickle
#out = open('../../data/processed/facilities_data.pkl' , 'wb')
#pickle.dump(facilities, out , pickle.HIGHEST_PROTOCOL)
#out.close()
