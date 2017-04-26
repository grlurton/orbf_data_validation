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
    reported_months = np.array(list(facility_data.reports.keys()))
    validation_set_months = sorted(reported_months[reported_months <= mois])
    data_out = []
    if (facility_data.last_supervision is None) & (len(validation_set_months) > 0):
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
        data_out = data_out.sort_index()
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






### FOR TESTING ONLY
import pickle
from generic_functions import *
from aedes_algorithm import *
from generic_functions import *


pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()

data_for_test = make_full_supervision_trail(facilities , '2016-01')

def screen_function(data , perc_risk):
    data = get_payments(data)
    table_1 = make_first_table(data)
    ponderation = table_1['Volume Financier Récupéré'] / max(table_1['Volume Financier Récupéré'])
    indicateurs_critiques = list(table_1[table_1['% Cumulé'] <= perc_risk].index)
    if min(table_1['% Cumulé']) > perc_risk :
        indicateurs_critiques = table_1.index[0]
    if indicateurs_critiques == []:
        pass
    data = data.sort_index()
    data_classif = data.loc[pd.IndexSlice[:,:,: ,indicateurs_critiques] , :]
    try :
        ecart_moyen_pondere = data_classif.groupby(level=1).apply(get_ecart_pondere , ponderation = ponderation)
        ecart_moyen_pondere = classify_facilities(ecart_moyen_pondere)
    except KeyError :
        ecart_moyen_pondere = None
    return ecart_moyen_pondere


u = data_for_test.groupby(level = 0).apply(screen_function , perc_risk = .8)

%matplotlib inline

def bar_cols(col_data , order_cols = ['green' , 'orange' , 'red']):
    o = []
    for col in order_cols:
        try :
            n = col_data.loc[col]
            o.append(n)
        except KeyError :
            o.append(0)

    plt.bar([0,1,2], o , color = order_cols)
    plt.xticks([0,1,2] , order_cols)

classes_counts = u.groupby(level = 0).Class.value_counts()
fig=plt.figure(figsize=(18, 16) , dpi= 80, facecolor='w', edgecolor='k')
for i in range(1,17):
    plt.subplot(4,4,i)
    departement = list(classes_counts.index.levels[0])[i-1]
    bar_cols(classes_counts.loc[departement])
    departement =departement.replace('’' , "'")
    plt.title(departement , fontsize=15)
