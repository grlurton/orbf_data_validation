import pandas as pd
import sys
sys.path.insert(0, '../monitoring_algorithms/')
from facility_monitoring import *
from generic_functions import *


import pickle
pkl_file = open( '../../data/processed/TEMP_facilities_aedes.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()




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


## FIXME Need different supervision cost depending on the facility type

mean_supervision_cost = 170000

## TODO Have a classification of reports as in or out of control :
## IDEA Need more brainstorm on what in and out of control
## TODO this script should be standalone to get all simulated algorithms and return a dataframe with all plotting data


## Functions to compute indicator level characteristics
def get_interesting_quantities(validated_path):
    validated_path['claimed_payment'] = validated_path['indicator_claimed_value'] * validated_path['indicator_tarif']
    validated_path['validated_payment'] = validated_path['indicator_validated_value'] * validated_path['indicator_tarif']
    validated_path['verified_payment'] = validated_path['indicator_verified_value'] * validated_path['indicator_tarif']
    validated_path['net_saved_payment'] = validated_path['claimed_payment'] - validated_path['validated_payment']
    validated_path['undue_payment_made'] = validated_path['validated_payment'] - validated_path['verified_payment']
    return validated_path

## Functions to compute Report Level characteristics
def make_monthly_report_payments(indicator_data):
    indicator_payments = indicator_data[['claimed_payment' , 'validated_payment' , 'verified_payment' , 'net_saved_payment' , 'undue_payment_made']]
    report_payments = indicator_payments.sum(0)
    report_payments['trigger'] = indicator_data['trigger'].iloc[0]
    return report_payments

def spot_out_of_control(data_report , supervision_cost):
    ooc = data_report['claimed_payment'] - data_report['verified_payment'] > supervision_cost
    return ooc

def make_report_desc(validated_path , supervision_cost):
    validated_path = get_interesting_quantities(validated_path)
    monthly_payment = validated_path.groupby(level = [0,1,2,3]).apply(make_monthly_report_payments)
    ooc = spot_out_of_control(monthly_payment , supervision_cost)
    monthly_payment['ooc'] = ooc
    return monthly_payment

t =  make_report_desc(aedes_data , mean_supervision_cost)
## Functions to compute Month Level characteristics
def count_supervisions(validated_path):
    supervisions = validated_path[validated_path.trigger.isin([True , 'Initial Training'])]
    n_supervisions = supervisions.reset_index()['facility_name'].nunique()
    return n_supervisions

def sensitivity(report_description):
    sensib = sum((report_description.ooc == True) & (report_description.trigger.isin([True , 'Initial Training']))) / sum(report_description.ooc == True)
    return sensib


def npv(report_description):
    denom = max(sum(report_description.trigger == False) , 1)
    npv = sum((report_description.ooc == False) & (report_description.trigger == False)) / denom
    return npv

def make_plot_dataset(validation_trail , mean_supervision_cost):
    reports_payment = make_report_desc(validation_trail , mean_supervision_cost)
    monthly_verifications = validation_trail.groupby(level = [0 , 3]).apply(count_supervisions)


    monthly_payment = reports_payment.groupby(level = [0 , 3]).apply(make_monthly_report_payments)

    ## Aggregate at Month Level

    data_out = pd.DataFrame(monthly_verifications , columns = ['monthly_verifications'])
    data_out['supervision_costs'] = data_out['monthly_verifications'] * mean_supervision_cost
    data_out['total_payment'] = monthly_payment['validated_payment']
    data_out['share_supervision_cost'] = data_out['supervision_costs'] / data_out['total_payment']
    data_out['undue_payment_made'] = monthly_payment['undue_payment_made']
    data_out['sensitivity'] = reports_payment.groupby(level = [0 , 3]).apply(sensitivity)
    data_out['npv'] = reports_payment.groupby(level = [0 , 3]).apply(npv)
    return data_out

data_out = make_plot_dataset(aedes_data , mean_supervision_cost)

out = open('../../data/processed/TEMP_aedes_pltdata.pkl' , 'wb')
pickle.dump(data_out , out , pickle.HIGHEST_PROTOCOL)
out.close()

out = open('../../data/processed/TEMP_full_data.pkl' , 'wb')
pickle.dump(aedes_data , out , pickle.HIGHEST_PROTOCOL)
out.close()
