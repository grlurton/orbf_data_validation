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
    if (algorithm_name in list(supervisions.columns)) :
        supervisions = pd.DataFrame(supervisions[algorithm_name])
        supervisions = supervisions[~pd.isnull(supervisions[algorithm_name])]
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
            print('Did not Work')
            pass

def valid_param(fac):
    return get_verification_path(fac , 'aedes_50')
validation_path_5 = list(map(valid_param , facilities))
aedes_data_50 = pd.concat(validation_path_5)

def valid_param(fac):
    return get_verification_path(fac , 'aedes_80')
validation_path_8 = list(map(valid_param , facilities))
aedes_data_80 = pd.concat(validation_path_8)

def make_full_verif(facility_data):
    facility_name = facility_data.facility_name
    departement = facility_data.departement
    data = facility_data.reports[['indicator_claimed_value'  , 'indicator_verified_value' , 'indicator_tarif' , 'indicator_verified_value']]
    data.columns = ['indicator_claimed_value' ,'indicator_validated_value' , 'indicator_tarif'  , 'indicator_verified_value']
    data['facility_name'] = facility_name
    data['departement'] = departement
    data['trigger'] = True
    data['algorithm'] = 'full_verification'
    data = data.reset_index().set_index(['algorithm' , 'departement' , 'facility_name' , 'period'  , 'indicator_label']).reorder_levels(['algorithm' , 'departement' , 'facility_name' ,  'period' , 'indicator_label']).sort_index()
    return data


full_data = list(map(make_full_verif , facilities))
full_data_df = pd.concat(full_data)
aedes_data = full_data_df.append(aedes_data_80).append(aedes_data_50)
aedes_data.sortlevel(inplace = True)
print(len(aedes_data))


def keep_only_full_facilities(df_algos) :
    idx = pd.IndexSlice
    full_facs = list(df_algos.index.levels[2])
    print(len(full_facs))
    for algo in list(df_algos.index.levels[0]) :
        algo_data  = df_algos.loc[algo].reset_index()
        facs = list(algo_data['facility_name'].unique())
        full_facs = [x for x in full_facs if x in facs]
    df_full = df_algos.loc[idx[:, :, full_facs] , :]
    return df_full

aedes_data = keep_only_full_facilities(aedes_data)

aedes_data = aedes_data.reset_index().set_index(['algorithm' , 'departement' , 'facility_name' , 'period'])


## TODO Have a classification of reports as in or out of control :
## IDEA Need more brainstorm on what in and out of control
## TODO this script should be standalone to get all simulated algorithms and return a dataframe with all plotting data


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

## FIXME Need different supervision cost depending on the facility type

mean_supervision_cost = 170000

def make_plot_dataset(aedes_data , mean_supervision_cost):
    payments_description= get_interesting_quantities(aedes_data)
    aedes_monthly_verifications = aedes_data.groupby(level = 3).apply(count_supervisions)
    data_out = pd.DataFrame(aedes_monthly_verifications , columns = ['monthly_verifications'])
    data_out['supervision_costs'] = data_out['monthly_verifications'] * mean_supervision_cost
    aedes_total_payment = payments_description['validated_payment'].groupby(level = 3).sum()
    data_out['total_payment'] = payments_description['validated_payment'].groupby(level = 3).sum()
    data_out['share_supervision_cost'] = data_out['supervision_costs'] / data_out['total_payment']
    data_out['undue_payment'] = payments_description['undue_payment_made'].groupby(level = 3).sum()
    return data_out

data_out = aedes_data.groupby(level = 0).apply(make_plot_dataset , mean_supervision_cost)

out = open('../../data/processed/TEMP_aedes_pltdata.pkl' , 'wb')
pickle.dump(data_out , out , pickle.HIGHEST_PROTOCOL)
out.close()

out = open('../../data/processed/TEMP_full_data.pkl' , 'wb')
pickle.dump(aedes_data , out , pickle.HIGHEST_PROTOCOL)
out.close()

len(aedes_data.index.levels[2])

### Plotting

import matplotlib.pyplot as plt

%matplotlib inline

plt.plot(data_out.loc['full_verification' , 'share_supervision_cost'].tolist() , data_out.loc['full_verification' , 'undue_payment'].tolist() , 'o')
plt.plot(data_out.loc['aedes_50' , 'share_supervision_cost'].tolist() , data_out.loc['aedes_50' , 'undue_payment'].tolist() , 'o')
plt.plot(data_out.loc['aedes_80' , 'share_supervision_cost'].tolist() , data_out.loc['aedes_80' , 'undue_payment'].tolist() , 'or')

######
