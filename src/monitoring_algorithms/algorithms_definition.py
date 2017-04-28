class monitoring_algorithm(object):
    def __init__(self  , algorithm_name , screening_method , alert_trigger  , implementation_simulation = None ,
                    transversal = False , validation_trail = True) :
        self.algorithm_name = algorithm_name
        self.transversal = transversal
        self.validation_trail = validation_trail
        self.screen = screening_method
        self.alert_trigger = alert_trigger
        self.validation_trail = validation_trail
        self.implementation_simulation = implementation_simulation

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

    def trigger_supervisions(self , mois , **kwargs):
        ## TODO Finalize triggering for the longitudinal case
        self.mois = mois
        alert = self.alert_trigger(self.description_parameters , **kwargs)
        self.supervision_list = alert

    def return_parameters(self):

        if self.transversal == False :
            self.facility_data.description_parameters = self.description_parameters
        if self.transversal == True :
            for facility in self.list_name_facilites :
                fac_obj = get_facility(self.facility_data , facility)
                if facility in self.supervision_list :
                    fac_obj.supervisions = fac_obj.supervisions.append(pd.DataFrame([True] , index = [self.mois] , columns = [self.algorithm_name]))
                if facility not in self.supervision_list :
                    fac_obj.supervisions = fac_obj.supervisions.append(pd.DataFrame([False] , index = [self.mois] , columns = [self.algorithm_name]))
                self.facility_data[self.list_name_facilites.index(facility)] = fac_obj

    def make_training_set(self , facility_data , mois) :
        algorithm_name = self.algorithm_name
        facility_name = facility_data.facility_name
        departement = facility_data.departement
        supervisions = facility_data.supervisions
        reports_months = np.array(list(facility_data.reports.keys()))
        if algorithm_name not in list(supervisions.columns) :
            training_months = sorted(list(reports_months[reports_months < mois]))
            supervisions = supervisions.append(pd.DataFrame(['Initial Training']*len(training_months) , index = training_months , columns = [algorithm_name]))
            if self.transversal == False :
                self.facility_data.supervisions = supervisions
            if self.transversal == True :
                index_fac = self.list_name_facilites.index(facility_name)
                self.facility_data[index_fac].supervisions = supervisions

        if (algorithm_name in list(supervisions.columns)) & (mois in reports_months) :
            training_months =  sorted(list(supervisions.index[~supervisions[algorithm_name].isnull()]))
            validated_data = []
            for month in training_months :
                month_report = facility_data.reports[month].report_data
                try :
                    month_status = supervisions.loc[month , algorithm_name]
                except KeyError :
                    pass ## Some facilities miss some reports. Should be solved when passing to a central DataFrame
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

    def simulate_implementation(self , date_start , date_stop  , data , **kwargs):
        if self.transversal == True :
            def date_range(fac):
                return list(fac.reports.keys())
            dates = list(map(date_range , data))
            dates =  [item for sublist in dates for item in sublist]
            dates = np.array(list(set(dates)))
            months_to_screen = sorted(dates[(dates >= date_start) & (dates <= date_stop)])
        screening_method = self.monitor
        trigger_method = self.trigger_supervisions
        self.implementation_simulation(screening_method , trigger_method , data , months_to_screen, **kwargs)

## TODO When updating the training set, Need to assert it is not already up to date.
## TODO When updating the training set, if there are missing periods, raise a warning
## TODO Extract facility list and some characteristics at start when transversal = True

######


### FOR TESTING ONLY
import pickle
from generic_functions import *
from aedes_algorithm import *
from generic_functions import *
pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()

def simulate_aedes(screening_method , trigger_method , data , dates , **kwargs):
    for date in dates :
        print(date)
        month = date[5:7]
        if month in ['01' , '07']:
            print('Time to make a classification')
            screening_method(data , mois = date , **kwargs)
        aedes_algorithm.trigger_supervisions(date)
        aedes_algorithm.return_parameters()

kwargs = {'perc_risk':.8}
aedes_algorithm = monitoring_algorithm('aedes' , screen_function , draw_supervision_months ,
                                        implementation_simulation = simulate_aedes ,
                                        transversal = True , validation_trail = True)

aedes_algorithm.simulate_implementation('2013-01' , '2016-12', facilities , **kwargs)





get_facility(facilities , 'Dedekpoe Csc').reports

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


## TODO Store Report Data dans un dataFrame by facility
## TODO Add an export and storage of the status in the facility object
