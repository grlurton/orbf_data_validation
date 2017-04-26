def extract_training_set(facility_data , mois) :

    facility_name = facility_data.facility_name
    departement = facility_data.departement
    ## Get a training set for the facility
    ## IDEA Check that the training is up to date with the right algorithm.
    try :
        training_set = facility_data.training_set
    except AttributeError :
        facility_data.initiate_training_set(mois)
        training_set = facility_data.training_set

    data_out = []
    for indic in training_set.keys() :
        data_indic = {'departement':departement ,
                        'facility_name':facility_name ,
                        'indicator_label':indic ,
                        'date':list(training_set[indic].index) ,
                        'values':list(training_set[indic])}

        add = pd.DataFrame(data_indic)
        if len(data_out) > 0 :
            data_out = data_out.append(add)
        if len(data_out) == 0 :
            data_out = add
    data_out = data_out.set_index(['departement' , 'facility_name' , 'indicator_label' , 'date'])
    return data_out

def make_transveral_training_set(data , mois):
    def get_training_set(facility_data , mois = mois):
        return extract_training_set(facility_data , mois)

    transversal_training_set = list(map(get_training_set , data))
    transversal_training_set = pd.concat(transversal_training_set)
    return transversal_training_set

def make_validation_trail(facility_data , mois):
    facility_name = facility_data.facility_name
    departement = facility_data.departement
    reported_months = np.array(list(u.reports.keys()))
    validation_set_months = sorted(reported_months[reported_months <= mois])
    data_out = []
    if facility_data.last_supervision is None :
        month = validation_set_months[0]
        for month in validation_set_months :
            month_data = facility_data.reports[month].report_data
            month_data['date'] = month
            month_data['facility_name'] = facility_name
            month_data['departement'] = departement
            month_data = month_data.set_index(['departement' , 'facility_name' , 'date'] , append= True).reorder_levels(['departement' , 'facility_name' , 'date' , 'indicator_label'])
            if len(data_out) > 0 :
                data_out = data_out.append(month_data)
            if len(data_out) == 0 :
                data_out = month_data
        return data_out

def make_full_supervision_trail(data , mois):
    def get_training_set(facility_data , mois = mois):
        return make_validation_trail(facility_data , mois)

    transversal_training_set = list(map(get_training_set , data))
    transversal_training_set = pd.concat(transversal_training_set)
    return transversal_training_set


class monitoring_algorithm(object):
    def __init__(self  , screening_method , alert_trigger , description = None , transversal = False) :
        self.transversal = transversal
        self.screen = screening_method
        self.alert_trigger = alert_trigger
        self.description = description

    def monitor(self , data , **kwargs):
        if self.transversal == True :
            print('Computing a transversal training set')
            training_data = make_transveral_training_set(data , kwargs['mois'])
        screen_output = self.screen(data , kwargs)
        self.description_parameters = screen_output['description_parameters']
        ## Mettre parametres pour redistribuer les description parametres dans les facilites, avec methodes d'aggregation et de description
        self.trigger_parameters = screen_output['trigger_parameters']

    def raise_alert(self , **kwargs):
        alert = self.alert_trigger(self.trigger_parameters , kwargs)
        self.description_parameters.update(alert['description_parameters'])
        return alert
        ## si type = transversal : redistribuer les alertes dans les facilties une a une

    def implementation_simulation(self , data , date_start):
        pass
        # TODO Just a placeholder. Way to make the simulation will vary by algorithm



from generic_functions import *
from aedes_algorithm import *
from generic_functions import *

def make_first_table(data):
    col1 = data.groupby(level = 2).apply(get_ecarts)
    col2 = data.groupby(level = 2).apply(get_revenu_gagne)
    col3 = data.groupby(level = 2).apply(get_volume_financier_recupere)
    col4 = col3 / get_volume_financier_recupere(data)
    output = col1.to_frame()
    output.columns = ['Ecarts']
    output['Revenus Totaux Gagnés'] = col2
    output['Volume Financier Récupéré'] = col3
    output['% Volume Financier Récupéré'] = col4

    output = output.sort_values('% Volume Financier Récupéré' , ascending = False)
    output['% Cumulé'] = output['% Volume Financier Récupéré'].cumsum()
    return output

##


### FOR TESTING ONLY

import pickle

pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()

data_for_test = make_full_supervision_trail(facilities[0:1] , '2012-07')
print(len(data_for_test))
print(data_for_test.head())

def screen_function(data):
    data = get_payments(data)
    table1 = make_first_table(data)
    print(table_1)

screen_function(data_for_test)
