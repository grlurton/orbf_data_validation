import pickle
pkl_file = open( '../../data/processed/TEMP_facilities_aedes.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()


import pandas as pd
import sys
sys.path.insert(0, '../monitoring_algorithms/')
from facility_monitoring import *
from generic_functions import *


def get_verification_path(facility_data , algorithm_name):
    supervisions = facility_data.supervisions.copy()
    facility_name = facility_data.facility_name
    departement = facility_data.departement
    if algorithm_name not in list(supervisions.columns) :
        pass
        #print('Algorithm ' + algorithm_name + ' does not seem to have been run on ' + facility_name)

    if (algorithm_name in list(supervisions.columns)) :
        supervisions = pd.DataFrame(supervisions[algorithm_name])
        supervisions = supervisions[~pd.isnull(supervisions[algorithm_name])]
        verified_months =  supervisions.index[supervisions[algorithm_name].isin([True , 'Initial Training'])]
        unverified_months = supervisions.index[supervisions[algorithm_name] == False]
        print(unverified_months)
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
            print('Did not Work')
            pass


## FIXME Drop altogteher facilities for which at which one algorithm does not come through.
## TODO groupby this so it can extract different algorithms pathes
## TODO Need to add a default full supervision path

## TODO Have a classification of reports as in or out of control :
## IDEA Need more brainstorm on what in and out of control

facilities[2].supervisions

def valid_param(fac):
    return get_verification_path(fac , 'aedes_50')
validation_path = list(map(valid_param , facilities))
aedes_data_50 = validation_path[0].append(validation_path[1:len(validation_path)])


def valid_param(fac):
    return get_verification_path(fac , 'aedes_80')
validation_path = list(map(valid_param , facilities))

aedes_data_80 = validation_path[0].append(validation_path[1:len(validation_path)])

aedes_data = aedes_data_50.append(aedes_data_80)

out = open('../../data/processed/TEMP_aedes_fulldata.pkl' , 'wb')
pickle.dump(aedes_data , out , pickle.HIGHEST_PROTOCOL)
out.close()

aedes_data


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

mean_supervision_cost = 170000

payments_description= get_interesting_quantities(aedes_data)

aedes_monthly_verifications = aedes_data.groupby(level = 3).apply(count_supervisions)
data_out = pd.DataFrame(aedes_monthly_verifications , columns = ['monthly_verifications'])
data_out['supervision_costs'] = data_out['monthly_verifications'] * mean_supervision_cost
aedes_total_payment = payments_description['validated_payment'].groupby(level = 3).sum()
data_out['total_payment'] = payments_description['validated_payment'].groupby(level = 3).sum()
data_out['share_supervision_cost'] = data_out['supervision_costs'] / data_out['total_payment']
data_out['undue_payment'] = payments_description['undue_payment_made'].groupby(level = 3).sum()

data_out = data_out[data_out['total_payment'] < 1e9]

import matplotlib.pyplot as plt

%matplotlib inline
plt.plot(data_out['supervision_costs'].tolist() , data_out['undue_payment'].tolist() , 'o')

######
