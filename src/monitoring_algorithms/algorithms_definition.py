def extract_training_set(facility_data , mois) :
    facility_name = facility_data.facility_name
    ## Get a training set for the facility
    ## IDEA Check that the training is up to date with the right algorithm.
    try :
        training_set = facility_data.training_set
    except AttributeError :
        facility_data.initiate_training_set(mois)
        training_set = facility_data.training_set

    data_out = []
    for indic in training_set.keys() :
        data_indic = {'facility_name':facility_name ,
                        'indicator_label':indic ,
                        'date':list(training_set[indic].index) ,
                        'values':list(training_set[indic])}

        add = pd.DataFrame(data_indic)
        if len(data_out) > 0 :
            data_out = data_out.append(add)
        if len(data_out) == 0 :
            data_out = add
    data_out = data_out.set_index(['facility_name' , 'indicator_label' , 'date'])
    return data_out

def make_training_set(data , mois):
    def get_training_set(facility_data , mois = mois):
        return extract_training_set(facility_data , mois)

    transversal_training_set = list(map(get_training_set , data))
    transversal_training_set = pd.concat(transversal_training_set)
    return transversal_training_set


pkl_file = open('../../data/processed/facilities.pkl', 'rb')
facilities = pickle.load(pkl_file)
pkl_file.close()

a = make_training_set(facilities , '2012-07')

class monitoring_algorithm(object):
    def __init__(self , monitoring_type , screening_method , alert_trigger , description = None) :
        self.type = monitoring_type
        self.screen = screening_method
        self.alert_trigger = alert_trigger
        self.description = description

    def monitor(self , data , **kwargs):
        screen_output = self.screen(data , kwargs)
        self.description_parameters = screen_output['description_parameters']
        self.trigger_parameters = screen_output['trigger_parameters']

    def raise_alert(self , **kwargs):
        alert = self.alert_trigger(self.trigger_parameters , kwargs)
        self.description_parameters.update(alert['description_parameters'])
        return alert ## si type = transversal : redistribuer les alertes dans les facilties une a une





help(map)






get_transversal_training_set(facilities[4] , '2012-07')
