#### This Script builds the framework to monitor individual series from OpenRBF and gives a first shot at some outputs.
## Grégoire Lurton
##
##  v1   - 3/2017 : Creates the serie objects + methods for diagnostic. Simple algorith = median + 2sd



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time

%matplotlib inline

class serie(object):
    """ A Serie currently being monitored

    Parameters
    ----------
    data : DataFrame
        The full OpenRBF data
    facility : int
        The ID of the monitored facility
    indicator : str
        The name of the monitored indicator

    Attributes
    ----------
    facility : int
        the ID of the monitored facility
    indicator : str
        the name of the indicator serie
    """

    def __init__(self, data, facility, indicator):
        self.facility = facility
        self.indicator = indicator
        self.alarms = []
        self.current_state = False
        self.training_set = []
        self.observed_set = []
        self.zone_up = []
        self.zone_down = []
        self.serie = data[(data.indicator_label == indicator) & (
            data.entity_id == facility)].sort_values(by='date')

    def make_training_set(self, new_value, verified_value):
        """ Building the training set

        Iteratively builds a training set based on the date at which the serie is being monitored

        Parameters
        ----------
        new_value : int
            A new value that is being tested as next value in the serie
        verified_value : int
            A new verified value to include in case an alarm has been raised
        Returns
        -------
        training_set : DataFrame
            The updated training data
        """
        if self.current_state == False:
            self.training_set.append(new_value)
        if self.current_state == True:
            self.training_set.append(verified_value)
        return self

    def make_credible_zone(self):
        """ Define the credible distribution

        Define a credible range for incoming data based on past validated data

        Returns
        -------
        credible_zone : List
            A list with limits of a range for the credible values for the serie
        """
        if len(self.training_set) > 0:
            central = np.median(self.training_set)
            sd = np.std(self.training_set)
            self.credible_zone = [max(central - sd * 2, 0), central + sd * 2]
            self.zone_up.append(self.credible_zone[1])
            self.zone_down.append(self.credible_zone[0])
        elif len(self.training_set) == 0:
            self.credible_zone = [- np.inf, np.inf]
        return self

    def raise_alarm(self, new_value, verified_value=None):
        """ Screens a new value for the serie for being unexpected

        Screens a new incoming value.
        * If the value is confirmed, adds it to the training set
        * If the value appears out, raises and alarm, and adds the verified value to the training set if on is provided

        Parameters
        ----------
        new_value : int
            A new value that is being tested as next value in the serie
        verified_value : int
            A new verified value to include in case an alarm has been raised
        Returns
        -------
        alarm : Bool
            True if an alarm is raised
        alarms : list
            Updates a list of all alarms status for past submitted indicator values
        training_set :
            Updated training set
        """
        self.observed_set.append(new_value)
        alarm = ((new_value < self.credible_zone[0]) | (
            new_value > self.credible_zone[1]))
        self.alarms.append(alarm)
        self.current_state = alarm
        if verified_value == None:
            verified_value = new_value
        self.make_training_set(new_value, verified_value)
        return self

    def simulate_verification(self):
        ''' Simulate a progressive verification of the data

        Using __raise_alarm__ , progressively validates and updates the training set as defined by  __make_credible_zone__

        '''
        for date in self.serie.date:
            self.make_credible_zone()
            new_value = self.serie.indicator_claimed_value[
                self.serie.date == date]
            verified_value = self.serie.indicator_verified_value[
                self.serie.date == date]
            self.raise_alarm(new_value.iloc[0], verified_value.iloc[0])
        return self

    def plot_surveillance(self):
        return "Not Built Yet"

    def compute_diagnostic_results(self):
        full_verification = np.sum(self.serie.indicator_claimed_value) - np.sum(self.serie.indicator_verified_value)
        algorithmic_verification = np.sum(self.serie.indicator_claimed_value) - np.sum(self.training_set)
        sensitivity = sum((pd.Series(self.serie.indicator_claimed_value == self.serie.indicator_verified_value).reset_index(drop = True)  == True) & (pd.Series(self.alarms)==False) ) / sum((pd.Series(self.serie.indicator_claimed_value == self.serie.indicator_verified_value).reset_index(drop = True)  == True))
        specificity = sum((pd.Series(self.serie.indicator_claimed_value == self.serie.indicator_verified_value).reset_index(drop = True)  == False) & (pd.Series(self.alarms)==True) ) / sum((pd.Series(self.serie.indicator_claimed_value == self.serie.indicator_verified_value).reset_index(drop = True)  == False))
        diagnostic = {'full_verification':full_verification , 'algorithmic_verification':algorithmic_verification ,
                        'sensitivity':sensitivity , 'specificity':specificity , 'fac_id':self.facility , 'indicator':self.indicator}
        self.diagnostic = diagnostic
        return self

data.indicator_label

a = serie(data , 2 , 'Enfants completement vaccines')

################################################################################
######### Run a validation process on all facilities for an indicator ##########
################################################################################
def make_complete_diag(data):
    fac = data.entity_id.unique()[0]
    indic = data.indicator_label.unique()[0]
    full_serie = serie(data , fac , indic).simulate_verification().compute_diagnostic_results().compute_diagnostic_results()
    return full_serie.diagnostic

out = data.groupby(['entity_id' , 'indicator_label']).apply(make_complete_diag)
df_diag = pd.DataFrame(out.tolist())

## heatmaps for sensitivity and specificity
heatmap_data = df_diag.pivot("fac_id" , "indicator" , "sensitivity")
ax = sns.heatmap(heatmap_data , cmap="YlGnBu")

#### Timelines for alerts log
a = serie(data , 2 , 'Accouchement eutocique assiste' ).simulate_verification()

dat_1 = a.serie
valid_date = dat_1.date[
    dat_1.indicator_claimed_value == dat_1.indicator_verified_value]
valid = dat_1.indicator_claimed_value[
    dat_1.indicator_claimed_value == dat_1.indicator_verified_value]

correct_date = dat_1.date[
    ~(dat_1.indicator_claimed_value == dat_1.indicator_verified_value)]
correct = dat_1.indicator_claimed_value[
    ~(dat_1.indicator_claimed_value == dat_1.indicator_verified_value)]

alarm_date_evol = a.serie.date[a.alarms]
alarm_evol = pd.Series(a.observed_set)[a.alarms]

validate_date_evol = a.serie.date[
    (pd.Series(a.alarms) == False).tolist()]
validate_evol = pd.Series(a.observed_set)[(
    pd.Series(a.alarms) == False).tolist()]

plt.figure(1)
plt.subplot(221)
plt.plot(correct_date, correct, "r^",
         valid_date, valid, "o")
plt.subplot(222)
plt.plot(dat_1.date, dat_1.indicator_verified_value, "g")

plt.subplot(223)
plt.plot(alarm_date_evol, alarm_evol, "r^",
         validate_date_evol, validate_evol, "o",
         a.serie.date[1:len(a.serie.date)], a.zone_up, 'k',
         a.serie.date[1:len(a.serie.date)], a.zone_down, 'k')
plt.subplot(224)
plt.plot(dat_1.date, a.training_set, "g")


# Regarder l'evolution des economies agregees avec le temps
# Suivre le risque d'underfunding

# Sortir l'algorithme de screening de la classe pour etre entree de facon ad-hoc
# Evolution de sensibilite / specificity dnas le temps / nbre de data points
