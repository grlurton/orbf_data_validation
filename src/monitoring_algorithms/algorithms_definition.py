class monitoring_algorithm(object):
    def __init__(self  , algorithm_name , screening_method , alert_trigger  , description = None ,
                    transversal = False , validation_trail = True) :
        self.algorithm_name = algorithm_name
        self.transversal = transversal
        self.validation_trail = validation_trail
        self.screen = screening_method
        self.alert_trigger = alert_trigger
        self.description = description
        self.validation_trail = validation_trail

    def monitor(self , facility_data , mois , **kwargs):
        if self.transversal == True :
            self.list_facilities_name = get_name_facilities_list(facility_data)
        self.mois = mois
        self.facility_data = facility_data
        if self.transversal == True :
            assert type(self.facility_data) == list , "This algorithm takes a list of facilities"
            print('Computing a transversal training set')
            self.list_name_facilites= get_name_facilities_list(self.facility_data)
            training_data = self.make_transversal_training_set(self.facility_data , mois)
        if self.transversal == False :
            assert type(self.facility_data) == 'facility_monitoring.facility' , "This algorithm takes a facility as input"
            training_data = self.make_training_set(self.facility_data , mois)
        print('Screening the data')
        screen_output = self.screen(training_data  , mois ,  **kwargs)
        self.description_parameters = screen_output['description_parameters']

    def trigger_supervisions(self , **kwargs):
        alert = self.alert_trigger(self.description_parameters , **kwargs)
        self.supervision_list = alert

    def return_parameters(self):
        if self.transversal == False :
            self.facility_data.description_parameters = self.description_parameters
        if self.transversal == True :
            for facility in self.list_name_facilites :
                sup =  facility in self.supervision_list
                fac_obj = get_facility(self.facility_data , facility)
                fac_obj.supervisions = fac_obj.supervisions.append(pd.DataFrame([True] , index = [self.mois] , columns = [self.algorithm_name]))
                self.facility_data[self.list_name_facilites.index(facility)] = fac_obj

    def make_training_set(self , facility_data , mois) :
        algorithm_name = self.algorithm_name
        facility_name = facility_data.facility_name
        departement = facility_data.departement
        supervisions = facility_data.supervisions
        reports_months = np.array(list(facility_data.reports.keys()))
        if algorithm_name not in list(supervisions.columns) :
            training_months = list(reports_months[reports_months < mois])
            supervisions = supervisions.append(pd.DataFrame(['Initial Training']*len(training_months) , index = training_months , columns = [algorithm_name]))
            if self.transversal == False :
                self.facility_data.supervisions = supervisions
            if self.transversal == True :
                index_fac = self.list_name_facilites.index(facility_name)
                self.facility_data[index_fac].supervisions = supervisions

        if (algorithm_name in list(supervisions.columns)) & (mois in reports_months) :
            training_months = list(supervisions.index[~supervisions[algorithm_name].isnull()])
            validated_data = []
            for month in training_months :
                month_report = facility_data.reports[month].report_data
                month_status = supervisions.loc[month , algorithm_name]
                if month_status in [True , 'Initial Training']  :
                    month_data = month_report[['indicator_verified_value' , 'indicator_tarif']]
                if month_status == False :
                    month_data = month_report[['indicator_claimed_value' , 'indicator_tarif']]
                month_data.columns = ['indicator_validated_value' , 'indicator_tarif']
                if self.validation_trail == True :
                    month_data['indicator_claimed_value'] = month_report['indicator_claimed_value']
                    month_data['verification_status'] = month_status
                month_data['date'] = month
                month_data['facility_name'] = facility_name
                month_data['departement'] = departement
                month_data = month_data.set_index(['departement' , 'facility_name' , 'date'] , append= True).reorder_levels(['departement' , 'facility_name' , 'date' , 'indicator_label'])
                if len(validated_data) > 0 :
                    validated_data = validated_data.append(month_data)
                if len(validated_data) == 0 :
                    validated_data = month_data
            validated_data = validated_data.sort_index()
            return validated_data

    def make_transversal_training_set(self , data , mois):
        def get_training_set(facility_data , mois = mois):
            return self.make_training_set(facility_data , mois)
        transversal_training_set = list(map(get_training_set , data))
        transversal_training_set = pd.concat(transversal_training_set)
        return transversal_training_set

    def implementation_simulation(self , data , date_start):
        pass
        # TODO Just a placeholder. Way to make the simulation will vary by algorithm



######
def screen_function(data , mois , **kwargs):
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

    return green_sample + orange_sample + red_sample

kwargs = {'perc_risk':.8}
aedes_algorithm = monitoring_algorithm('aedes' , screen_function , draw_supervision_months , transversal = True ,
validation_trail = True)
aedes_algorithm.monitor(facilities  , mois = '2012-07'  , **kwargs)
aedes_algorithm.trigger_supervisions()
aedes_algorithm.return_parameters()

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
