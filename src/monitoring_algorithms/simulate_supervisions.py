# For warnings
import warnings
warnings.filterwarnings('ignore')

## Create Cluster to run
import ipyparallel
import subprocess
import pickle
start_cluster_command = 'ipcluster start -n 4'
subprocess.Popen(start_cluster_command)
clients = ipyparallel.Client()
dview = clients[:]

pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)

## Load the facility_monitoring module
from facility_monitoring import *

## Loading the data
store = pd.HDFStore('../../data/processed/orbf_benin.h5')
data_orbf = store['data']
tarifs = store['tarifs']
store.close()

## Making parameters
mean_supervision_cost = 170000
underfunding_max_risk = 0.5

## Making List of facliities General Verification Trail :

def run(fac , data_orbf = data_orbf , tarifs = tarifs ,  mean_supervision_cost = mean_supervision_cost , underfunding_max_risk = underfunding_max_risk):
    min_date = min(list(fac.reports.keys()))
    fac.initiate_training_set(min_date)
    fac.make_supervision_trail(tarifs , mean_supervision_cost , underfunding_max_risk)
    return fac

#%%time
## Benchmark : 4/10/27 - 4 cors, 77mins
result = dview.map_sync(run , facilities)
subprocess.Popen('ipcluster stop')

out = open('../../data/processed/facilities_supervision_trails.pkl' , 'wb')
pickle.dump(result, out , pickle.HIGHEST_PROTOCOL)
out.close()
