# For warnings
import warnings
warnings.filterwarnings('ignore')
import time

## Create Cluster to run
import ipyparallel
import subprocess
import pickle
start_cluster_command = 'ipcluster start -n 4'
subprocess.Popen(start_cluster_command)


print('Starting Cluster')
for i in range(0,100):
    while True:
        try:
            clients = ipyparallel.Client()
            dview = clients[:]
        except:
            time.sleep(5)
            continue
        break

print('Loading Data')
import pandas as pd

pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()
store = pd.HDFStore('../../data/processed/orbf_benin.h5')
tarifs = store['tarifs']
store.close()


## Load the facility_monitoring module
from facility_monitoring import *

## Loading the data
store = pd.HDFStore('../../data/processed/orbf_benin.h5')
data_orbf = store['data']
tarifs = store['tarifs']
store.close()

mean_supervision_cost = 170000
underfunding_max_risk = 0.5

## Making List of facliities General Verification Trail :
fac_ids = []
for fac_id in data_orbf.entity_id.unique():
    fac_data = data_orbf[data_orbf.entity_id == fac_id]
    fac_ids.append(fac_data)

def run(fac_data , tarifs = tarifs):
    import facility_monitoring
    facility_data = facility_monitoring.facility(fac_data , tarifs)
    return facility_data

facilities = dview.map_sync(run , fac_ids)
subprocess.Popen('ipcluster stop')


import pickle
out = open('../../data/processed/facilities.pkl' , 'wb')
pickle.dump(facilities, out , pickle.HIGHEST_PROTOCOL)
out.close()
