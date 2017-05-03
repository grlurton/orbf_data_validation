# For warnings
import warnings
warnings.filterwarnings('ignore')
import time
import numpy as np
## Create Cluster to run
import ipyparallel
import subprocess
import pickle
import pandas as pd

start_cluster_command = 'ipcluster start -n 4'
subprocess.Popen(start_cluster_command)

#from generic_functions import *
from aedes_algorithm import *
from algorithms_definition import *


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
pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()

### Run Aedes Algorithm
kwargs = {'perc_risk':.8}
aedes_algorithm = monitoring_algorithm('aedes' , screen_function , draw_supervision_months ,
                                        implementation_simulation = simulate_aedes ,
                                        transversal = True , validation_trail = True)

aedes_algorithm.simulate_implementation('2012-07' , '2016-12', facilities , **kwargs)

out = open('../../data/processed/TEMP_facilities_aedes.pkl' , 'wb')
pickle.dump(facilities , out , pickle.HIGHEST_PROTOCOL)
out.close()

## Making parameters
mean_supervision_cost = 170000
underfunding_max_risk = 0.5

## Making List of facliities General Verification Trail :

def run(fac , tarifs = tarifs ,  mean_supervision_cost = mean_supervision_cost , underfunding_max_risk = underfunding_max_risk):
    min_date = min(list(fac.reports.keys()))
    fac.initiate_training_set(min_date)
    fac.make_supervision_trail(tarifs , mean_supervision_cost , underfunding_max_risk)
    return fac

## Benchmark : 4/10/27 - 4 cores, 77mins
result = dview.map_sync(run , facilities)
subprocess.Popen('ipcluster stop')

out = open('../../data/processed/facilities_supervision_trails.pkl' , 'wb')
pickle.dump(result, out , pickle.HIGHEST_PROTOCOL)
out.close()
