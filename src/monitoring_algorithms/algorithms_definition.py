class monitoring_algorithm(object):
    """ Monitoring Algorithm objects

    Monitoring algorithms are the combination of three sub-algorithms :
    1. A Screening algorithm, that processes the available data and outputs description parameters of this data.
    2. A Triggering algorithm that analyses the description parameters and returns a binary decision, regarding the necessity to go verify the data in reported in a given reported.
    3. A Supervision algorithm, that describes the concrete implementation of the monitoring in the field.

    The combination of these three elements uniquely define a monitoring strategy for a program. At each steps, the facility objects are updated to include the values of the supervision paraemters, and the result of the trigger algorithm.

    The Screening algorithms input can be classified along two dimentsions :
    1. Longitudinal vs Transversal :
        * Longitudinal data : Using only one facility, the algorithm considers the past validated values and infers the characteristics of the next expected values.
        * Transversal data : Using a group of facilities, the algorithm compares the different facilities performances and their values.
    2. Simple reports vs Validation trail :
        * Simple reports : The algorithm uses only the values previously validated in the facilities.
        * Validation trails : The algorithm uses both the reported values and the validated values.

    We need to specify these two dimensions when initiating the algorithm object, to orient the pre-processing of the data. The inputed data is then processed to form an appropriate training set that can be fed in the Screening algorithm.



    Parameters
    -------------
    algorithm_name : string
        The name of the algorithm, to identify the output in the facility objects
    screening_method : function
        The Screening algorithm. More description on its characteristics in the function.
    alert_trigger : function
        The Triggering algorithm. More description on its characteristics in the function.
    implementation_simulation : function
        The Supervision algorithm. More description on its characteristics in the function.
    transversal : boolean
        True if the data is transveral, False if it is longitudinal.
        False by default.
    validation_trail : boolean
        True if the screening method uses a validation trail as input, False if it uses simple reports.
        False by default.
    verbose : boolean
        True if the user wants to have some monitoring prints in different parts of the functions.


    """
    def __init__(self  , algorithm_name , screening_method , alert_trigger  , implementation_simulation = None ,
                    transversal = False , validation_trail = True , verbose = False) :
        self.algorithm_name = algorithm_name
        self.transversal = transversal
        self.validation_trail = validation_trail
        self.screening_method = screening_method
        self.alert_trigger = alert_trigger
        self.validation_trail = validation_trail
        self.implementation_simulation = implementation_simulation
        self.verbose = verbose

    def monitor(self , facility_data , mois , **kwargs):
        if self.transversal == True :
            self.list_facilities_name = get_name_facilities_list(facility_data)
        self.mois = mois
        self.facility_data = facility_data
        if self.transversal == True :
            assert type(self.facility_data) == list , "This algorithm takes a list of facilities"
            if self.verbose == True :
                print('Computing a transversal training set')
            self.list_name_facilites= get_name_facilities_list(self.facility_data)
            self.training_data = self.make_transversal_training_set(self.facility_data , mois)
        if self.transversal == False :
            assert type(self.facility_data) == 'facility_monitoring.facility' , "This algorithm takes a facility as input"
            self.training_data = self.make_training_set(self.facility_data , mois)
        if self.verbose == True :
            print('Screening the data')
        screen_output = self.screening_method(self.training_data  , mois ,  **kwargs)

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

    def make_training_set(self  , facility_data  , mois) :
        algorithm_name = self.algorithm_name
        facility_name = facility_data.facility_name
        departement = facility_data.departement
        supervisions = facility_data.supervisions
        reports_months = facility_data.reports.index.levels[0]
        training_months = reports_months[reports_months < mois]
        if algorithm_name not in list(supervisions.columns) :
            supervisions = supervisions.append(pd.DataFrame(['Initial Training']*len(training_months) , index = training_months , columns = [algorithm_name]))
            if self.transversal == False :
                self.facility_data.supervisions = supervisions
            if self.transversal == True :
                index_fac = self.list_name_facilites.index(facility_name)
                self.facility_data[index_fac].supervisions = supervisions
        if (algorithm_name in list(supervisions.columns)) :
            verified_months =  supervisions.index[supervisions[algorithm_name].isin([True , 'Initial Training'])]
            unverified_months = supervisions.index[supervisions[algorithm_name] == False]
            verified_data =  pd.DataFrame([] , index = [])
            claimed_data =  pd.DataFrame([] , index = [])
            if (len(list(verified_months)) > 0) | (type(verified_months) == 'Period') :
                try :
                    verified_data = facility_data.reports.loc[list(verified_months) , ['indicator_claimed_value'  , 'indicator_verified_value' , 'indicator_tarif']]
                    verified_data.columns = ['indicator_claimed_value' ,'indicator_validated_value' , 'indicator_tarif']
                except KeyError :
                    pass
            if len(list(unverified_months)) > 0 | (type(unverified_months) == 'Period') :
                try :
                    claimed_data = facility_data.reports.loc[list(unverified_months) , ['indicator_claimed_value'  , 'indicator_claimed_value' , 'indicator_tarif']]
                    claimed_data.columns = ['indicator_claimed_value' , 'indicator_validated_value' , 'indicator_tarif']

                except( KeyError , TypeError ):
                    pass

        validated_data = verified_data.append(claimed_data)
        validated_data['facility_name'] = facility_name
        validated_data['departement'] = departement
        if len(validated_data) > 0 :
            try :
                validated_data = validated_data.reset_index().set_index(['departement' , 'facility_name' , 'period'  , 'indicator_label']).reorder_levels(['departement' , 'facility_name' , 'period' , 'indicator_label']).sort_index()
            except KeyError :
                pass
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
                return fac.reports.index.levels[0]
            full_dates = list(map(date_range , data))
            dates = full_dates[0]
            for n in range(1,len(full_dates)):
                dates.union(full_dates[n])
            months_to_screen = sorted(dates[(dates >= date_start) & (dates <= date_stop)])
        screening_method = self.monitor
        trigger_method = self.trigger_supervisions
        self.implementation_simulation(self.monitor , self.trigger_supervisions ,  self.return_parameters , data , months_to_screen, **kwargs)


## TODO When updating the training set, Need to assert it is not already up to date.
## TODO When updating the training set, if there are missing periods, raise a warning => for now, try except
## TODO les routines de description se font a partir des facility objects


######


### FOR TESTING ONLY
import pickle
from generic_functions import *
from aedes_algorithm import *
from generic_functions import *
pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()

def simulate_aedes(screening_method , trigger_supervisions , return_parameters , data , dates , **kwargs):
    for date in dates :
        month = date.month
        if month in [1 ,7]:
            screening_method(data , mois = date , **kwargs)
        trigger_supervisions(date)
        return_parameters()

kwargs = {'perc_risk':.8}
aedes_algorithm = monitoring_algorithm('aedes' , screen_function , draw_supervision_months ,
                                        implementation_simulation = simulate_aedes ,
                                        transversal = True , validation_trail = True)

%%time
aedes_algorithm.simulate_implementation('2012-07' , '2016-12', facilities , **kwargs)

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
