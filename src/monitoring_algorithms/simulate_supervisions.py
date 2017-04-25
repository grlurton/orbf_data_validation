# For warnings
import warnings
warnings.filterwarnings('ignore')
import time
import numpy as np
## Create Cluster to run
import ipyparallel
import subprocess
import pickle
start_cluster_command = 'ipcluster start -n 4'
subprocess.Popen(start_cluster_command)

from aedes_algorithm import *


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

mois = '2012-07'

def get_training_set(data , mois = '2012-07') :
    data.initiate_training_set(mois)
    facility_name = data.facility_name
    ts= data.training_set
    dat = []
    for indic in ts.keys() :
        data_indic = {'facility_name':facility_name ,
                        'indicator_label':indic ,
                        'date':list(ts[indic].index) ,
                        'values':list(ts[indic])}


        add = pd.DataFrame(data_indic)
        if len(dat) > 0 :
            dat = dat.append(add)
        if len(dat) == 0 :
            dat = add
    dat = dat.set_index(['facility_name' , 'indicator_label' , 'date'])
    return dat
    #return pd.DataFrame(ts , index = [fac_id])

len(u)



#def run_aedes(month):
#    if month.dt.month.isin([1 , 6 ]):
#        print('Nouvelle Classification !')
#        classification_data = 
        ### Faire La classification
    ### Faire tirage en janvier
    ### Update Training set
    ### Update date supervision
