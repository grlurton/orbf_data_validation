import pandas as pd
import pickle

import sys
sys.path.insert(0, '../monitoring_algorithms/')
from facility_monitoring import *
from generic_functions import *

pkl_file = open( '../../data/processed/TEMP_facilities_aedes.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()

def get_verification_path(facility_data , algorithm_name):
    supervisions = facility_data.supervisions.copy()
    facility_name = facility_data.facility_name
    departement = facility_data.departement
#
    if algorithm_name not in list(supervisions.columns) :
        print('Algorithm ' + algorithm_name + ' does not seem to have been run on ' + facility_name)

    if (algorithm_name in list(supervisions.columns)) :
        verified_months =  supervisions.index[supervisions[algorithm_name].isin([True , 'Initial Training'])]
        unverified_months = supervisions.index[supervisions[algorithm_name] == False]
        verified_data =  pd.DataFrame([] , index = [])
        claimed_data =  pd.DataFrame([] , index = [])
        if (len(list(verified_months)) > 0) | (type(verified_months) == 'Period') :
            try :
                verified_data = facility_data.reports.loc[list(verified_months) , ['indicator_claimed_value'  , 'indicator_verified_value' , 'indicator_tarif' , 'indicator_verified_value']]
                verified_data.columns = ['indicator_claimed_value' ,'indicator_validated_value' , 'indicator_tarif'  , 'indicator_verified_value']
            except KeyError :
                pass
        if len(list(unverified_months)) > 0 | (type(unverified_months) == 'Period') :
            try :
                claimed_data = facility_data.reports.loc[list(unverified_months) , ['indicator_claimed_value'  , 'indicator_claimed_value' , 'indicator_tarif'  , 'indicator_verified_value']]
                claimed_data.columns = ['indicator_claimed_value' , 'indicator_validated_value' , 'indicator_tarif'  , 'indicator_verified_value']
            except ( KeyError , TypeError ):
                pass

        validated_data = verified_data.append(claimed_data)
        validated_data['facility_name'] = facility_name
        validated_data['departement'] = departement

        supervisions.index = pd.DataFrame(supervisions).index.rename('period')
        supervisions.columns = ['trigger']
        supervisions['algorithm'] = algorithm_name
        try :
            validated_data = pd.merge(validated_data , supervisions , left_index = True , right_index = True)
            if len(validated_data) > 0 :
                try :
                    validated_data = validated_data.reset_index().set_index(['algorithm' , 'departement' , 'facility_name' , 'period'  , 'indicator_label']).reorder_levels(['algorithm' , 'departement' , 'facility_name' ,  'period' , 'indicator_label']).sort_index()
                except KeyError :
                    pass
            return validated_data
        except :
            pass

## FIXME Drop altogteher facilities for which at which one algorithm does not come through.
## TODO groupby this so it can extract different algorithms pathes
## TODO Need to add a default full supervision path

def valid_param(fac):
    return get_verification_path(fac , 'aedes')
validation_path = list(map(valid_param , facilities))

full_data = validation_path[0].append(validation_path[1:len(validation_path)])

out = open('../../data/processed/TEMP_aedes_fulldata.pkl' , 'wb')
pickle.dump(full_data , out , pickle.HIGHEST_PROTOCOL)
out.close()




## Additional function for interesting parameters
def count_supervisions(validated_path):
    supervisions = validated_path[validated_path.trigger.isin([True , 'Initial Training'])]
    n_supervisions = supervisions.reset_index()['facility_name'].nunique()
    return n_supervisions

def get_interesting_quantities(validated_path):
    validated_path['claimed_payment'] = validated_path['indicator_claimed_value'] * validated_path['indicator_tarif']
    validated_path['validated_payment'] = validated_path['indicator_validated_value'] * validated_path['indicator_tarif']
    validated_path['verified_payment'] = validated_path['indicator_verified_value'] * validated_path['indicator_tarif']
    validated_path['net_saved_payment'] = validated_path['claimed_payment'] - validated_path['validated_payment']
    validated_path['undue_payment_made'] = validated_path['validated_payment'] - validated_path['verified_payment']
    return validated_path

count_supervisions(full_data)

supervision_costs = full_data.groupby(level = [0 , 3]).apply(count_supervisions)
with_iq = get_interesting_quantities(every)

def ttt(data) :
    return data.reset_index()['facility']

facilities[660].facility_name
facilities[660].departement
facilities[660].supervisions


monthly_verifications = full_data.groupby(level = 3).apply(count_supervisions)

######
import matplotlib.pyplot as plt

%matplotlib inline

undue_payment_made = with_iq.validated_payment.groupby(level = [0 , 3]).sum()
total_payment = undue_payment_made + supervision_costs
total_payment  = total_payment[total_payment < 1e9]
list(sorted(total_payment.index.levels[1]))
share_supervision_cost = supervision_costs / total_payment
share_supervision_cost.plot()
