# from generic_functions import *
import pandas as pd

class monitoring_algorithm(object):
    """ Monitoring Algorithm objects

    Parameters
    ----------
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

    def __init__(self, algorithm_name, screening_method, alert_trigger, implementation_simulation=None, transversal=False, validation_trail=True, verbose=False):
        self.algorithm_name = algorithm_name
        self.transversal = transversal
        self.validation_trail = validation_trail
        self.screening_method = screening_method
        self.alert_trigger = alert_trigger
        self.validation_trail = validation_trail
        self.implementation_simulation = implementation_simulation
        self.verbose = verbose

    def monitor(self, facility_data, mois, **kwargs):
        """ Monitoring function

        This function is the workhorse of the algorithm. It extracts the training set from the facility data, and performs the appropriate screening for the month indicated.

        Parameters
        -----------
        facility_data : DataFrame
            The data collected in the OpenRBF system. It does not need to be the subset of the data on which to fit algorithm for the observed month.
        mois : The month for which the algorithm is fit.
        **kwargs : Additional arguments necessary for the specific algorithm
        """
        if self.transversal is True:
            self.list_facilities_name = get_name_facilities_list(facility_data,
                                                                 mois)
        self.facility_data = facility_data
        if self.transversal is True:
            assert type(self.facility_data) == list, "This algorithm takes a list of facilities"
            if self.verbose is True:
                print('Computing a transversal training set')
            self.list_name_facilites = get_name_facilities_list(facility_data,
                                                                mois)
            self.training_data = self.make_transversal_TS(self.facility_data,
                                                          mois)
        if self.transversal is False:
            assert type(self.facility_data) == 'facility_monitoring.facility', "This algorithm takes a facility as input"
            self.training_data = self.make_training_set(self.facility_data,
                                                        mois)
        if self.verbose is True:
            print('Screening the data')
        screen_output = self.screening_method(self.training_data, mois,
                                              **kwargs)

        self.description_parameters = screen_output['description_parameters']

    def trigger_supervisions(self, mois, **kwargs):
        """ Raising an alarm if the description parameters computed by the monitoring function are problematic according to the `alert_trigger` function.

        Parameters
        ----------
        mois : The month for which the algorithm is fit.
        **kwargs : Additional arguments necessary for the specific algorithm


        """
        # TODO Finalize triggering for the longitudinal case
        print(mois)
        self.mois = mois
        alert = self.alert_trigger(self.description_parameters, **kwargs)
        self.supervision_list = alert

    def return_parameters(self):
        if self.transversal is False:
            self.facility_data.description_parameters = self.description_parameters
        if self.transversal is True:
            for facility in self.list_facilities_name:
                try:
                    fac_obj = get_facility(self.facility_data, facility)
                    if (facility in self.supervision_list):
                        sup = pd.DataFrame([True], index=[self.mois],
                                           columns=[self.algorithm_name])
                        fac_obj.supervisions = fac_obj.supervisions.append(sup)
                    if ((facility not in self.supervision_list) &
                       (facility in self.training_data.index.levels[1])):
                        nosup = pd.DataFrame([False], index=[self.mois],
                                             columns=[self.algorithm_name])
                        fac_obj.supervisions = fac_obj.supervisions.append(nosup)
                    if ((facility not in self.supervision_list) &
                       (facility not in self.training_data.index.levels[1])):
                        IT = pd.DataFrame(['Initial Training'],
                                          index=[self.mois],
                                          columns=[self.algorithm_name])
                        fac_obj.supervisions = fac_obj.supervisions.append()
                    self.facility_data[self.list_name_facilites.index(facility)] = fac_obj
                except ValueError:
                    pass  # eg : Akadja Mi seems to be out...

    def make_training_set(self, facility_data, mois):
        """ Preparing the training set to be fed in the algorithm data processing routine. The processing varies depending if the algorithm uses longitudinal or transversal data. For the rest, it essentially takes all the data collected before the processing month and keeps the claimed or the verified data depending on the supervision status for the given month.

        Parameters
        ----------
        facility_data : DataFrame
            The data collected in the OpenRBF system. It does not need to be the subset of the data on which to fit algorithm for the observed month.
        mois : The month for which the algorithm is fit.

        """
        algorithm_name = self.algorithm_name
        facility_name = facility_data.facility_name
        departement = facility_data.departement
        supervisions = facility_data.supervisions
        reports_months = facility_data.reports.index.levels[0]
        training_months = reports_months[reports_months < mois].unique()
        if len(training_months) > 0:
            if (algorithm_name not in list(supervisions.columns)):
                supervisions = pd.DataFrame(['Initial Training']*len(training_months), index=training_months, columns=[algorithm_name])
                if self.transversal is False:
                    self.facility_data.supervisions = self.facility_data.supervisions.append(supervisions)
                if self.transversal is True:
                    index_fac = self.list_name_facilites.index(facility_name)
                    self.facility_data[index_fac].supervisions = self.facility_data[index_fac].supervisions.append(supervisions)
            if (algorithm_name in list(supervisions.columns)):
                verified_months = supervisions.index[supervisions[algorithm_name].isin([True, 'Initial Training'])]
                unverified_months = supervisions.index[supervisions[algorithm_name] is False]
                verified_data = pd.DataFrame([], index=[])
                claimed_data = pd.DataFrame([], index=[])
                if (len(list(verified_months)) > 0) | (type(verified_months) == 'Period'):
                    try:
                        verified_data = facility_data.reports.loc[list(verified_months), ['indicator_claimed_value', 'indicator_verified_value', 'indicator_tarif']]
                        verified_data.columns = ['indicator_claimed_value', 'indicator_validated_value', 'indicator_tarif']
                    except KeyError:
                        pass
                if len(list(unverified_months)) > 0 | (type(unverified_months) == 'Period'):
                    try:
                        claimed_data = facility_data.reports.loc[list(unverified_months), ['indicator_claimed_value', 'indicator_claimed_value', 'indicator_tarif']]
                        claimed_data.columns = ['indicator_claimed_value', 'indicator_validated_value', 'indicator_tarif']

                    except(KeyError, TypeError):
                        pass

                valid_data = verified_data.append(claimed_data)
                valid_data['facility_name'] = facility_name
                valid_data['departement'] = departement
                if len(valid_data) > 0:
                    try:
                        valid_data = valid_data.reset_index()
                        valid_data = valid_data.set_index(['departement',
                                                          'facility_name',
                                                           'period',
                                                           'indicator_label'])
                        valid_data = valid_data.reorder_levels(['departement',
                                                                'facility_name',
                                                                'period',
                                                                'indicator_label'])
                        valid_data = valid_data.sort_index()
                    except KeyError:
                        pass
            return valid_data

    def make_transversal_TS(self, data, mois):
        def get_training_set(facility_data, mois=mois):
            return self.make_training_set(facility_data, mois)
        to_include = get_name_facilities_list(data, mois)
        data = [get_facility(data, x) for x in to_include]
        transversal_training_set = list(map(get_training_set, data))
        transversal_training_set = pd.concat(transversal_training_set)
        return transversal_training_set

    def simulate_implementation(self, date_start, date_stop, data, **kwargs):
        """ Simulates the implementation of the algorithm. Runs the data processing and triggering rules, and applies the supervision rule, then saves the supervision status of the reporting month for each facility.

        Parameters
        ----------
        date_start : Start date of the simulation
        date_stop : Finish date of the simulation
        data : Full open rbf data formatted in facilities objects
        **kwargs : Additional arguments necessary for the specific algorithm
        """
        if self.transversal is True:
            def date_range(fac):
                return fac.reports.index.levels[0]
            full_dates = list(map(date_range, data))
            dates = full_dates[0]
            for n in range(1, len(full_dates)):
                dates.union(full_dates[n])
            months_to_screen = sorted(dates[(dates >= date_start) & (dates <= date_stop)])
        self.implementation_simulation(self.monitor, self.trigger_supervisions, self.return_parameters, data, months_to_screen, **kwargs)


# TODO assert training set not already before updating
# TODO les routines de description se font a partir des facility objects
