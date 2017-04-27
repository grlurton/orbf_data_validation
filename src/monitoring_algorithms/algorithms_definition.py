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
    validation_set_months = sorted(reported_months[reported_months < mois])
    data_out = []
    if (facility_data.last_supervision is None) & (len(validation_set_months) >= 0):
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
    def __init__(self  , screening_method , alert_trigger , input_type , description = None ,
                    transversal = False , validation_trail = True) :
        self.transversal = transversal
        self.validation_trail = validation_trail
        self.screen = screening_method
        self.alert_trigger = alert_trigger
        self.description = description
        self.input_type = input_type

    def monitor(self , data , mois):
        self.input_data = data
        self.mois = mois
        if self.transversal == True :
            assert type(self.input_data) == list , "This algorithm takes a list of facilities"
            print('Computing a transversal training set')
            training_data = make_transveral_training_set(self.input_data , mois)
            supervision_trail = make_full_supervision_trail(self.input_data , mois)
        if self.transversal == False :
            assert type(self.input_data) == 'facility_monitoring.facility' , "This algorithm takes a facility as input"

        print('Screening the data')
        if self.input_type == 'validated_data' :
            screen_output = self.screen(training_data  , **kwargs)
        if self.input_type == 'verification_trail' :
            screen_output = self.screen(supervision_trail  , **kwargs)
        self.description_parameters = screen_output['description_parameters']

    def trigger_supervisions(self , **kwargs):
        alert = self.alert_trigger(self.description_parameters , **kwargs)
        self.trigger_parameters = alert
        return alert
        ## si type = transversal : redistribuer les alertes dans les facilties une a une

    def return_parameters(self , alert):
        if self.transversal == False :
            self.input_data.description_parameters = self.description_parameters
        if self.transversal == True :
            for


    def implementation_simulation(self , data , date_start):
        pass
        # TODO Just a placeholder. Way to make the simulation will vary by algorithm


def screen_function(data , **kwargs):
    perc_risk = kwargs['perc_risk']
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
    return {'description_parameters':ecart_moyen_pondere}

def draw_supervision_months(description_parameters , **kwargs):
    green_fac = description_parameters[description_parameters['Class'] == 'green']
    orange_fac = description_parameters[description_parameters['Class'] == 'orange']

    green_sample = list(green_fac.sample(frac = 0.2).index)
    orange_sample = list(orange_fac.sample(frac = 0.8).index)
    red_sample = list(description_parameters[description_parameters['Class'] == 'red'].index)

    return {'green_sample':green_sample , 'orange_sample':orange_sample , 'red_sample':red_sample}

kwargs = {'perc_risk':.8}
aedes_algorithm = monitoring_algorithm(screen_function , draw_supervision_months , 'verification_trail' ,
                                        transversal = True)
aedes_algorithm.monitor(facilities , **kwargs)

a = aedes_algorithm.trigger_supervisions()
a['green_sample']





### FOR TESTING ONLY
import pickle
from generic_functions import *
from aedes_algorithm import *
from generic_functions import *
pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()


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
