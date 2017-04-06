#### This Script builds the framework to monitor individual OpenRBF reports.
## Grégoire Lurton
##
##  v1   - 3/2017 : Creates the reports objects

import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
from datetime import datetime
import matplotlib.pyplot as plt

#store = pd.HDFStore('../../data/processed/orbf_benin.h5')
#data_orbf = store['data']
#store.close()

class report(object):
    """ A report from OperRBF

    A report is a set of indicators that have been reported by a facility on a given month. For each report, a payment is claimed.

    Parameters
    ----------
    data : DataFrame
        A report for a facility month

    Attributes
    -----------
    facility_id : int
        A unique identifier for the facility
    facility_name : str
        The name of the facility
    month : datetime
        The date of the report
    report_data : DataFrame
        The data of the report. For each report, consists in :
            * The claimed value of the indicator
            * The verified value of the indicator
            * The tarif of the indicator
    report_payment : Dictionnary
        The payment for the report. Contains both the claimed payment and the verified payment.
    """

    def __init__(self , data , tarifs):
        self.facility_id = data.entity_id.iloc[0]
        self.facility_name = data.entity_name.iloc[0]
        self.date = data.date.iloc[0]
        self.report_data = data[['indicator_label' , 'indicator_claimed_value' , 'indicator_verified_value' , 'indicator_tarif']]
        self.report_data = self.report_data.set_index('indicator_label')
        self.report_payment = self.compute_report_payment(tarifs)

    def compute_report_payment(self , tarifs):
        """ Reports Summaries

        Computes the reports claimed and verified payments

        Returns
        -------
        report_payments : Dictionnary
            The payment for the report. Contains both the claimed payment and the verified payment.
        """
        claimed_payment = np.nansum(self.report_data.indicator_claimed_value * tarifs)
        verified_payment = np.nansum(self.report_data.indicator_verified_value * tarifs)
        report_payments = {'claimed_payment': claimed_payment, 'verified_payment': verified_payment}
        return report_payments

    def overcost_alarm(self , expected_report , tarifs , mean_supervision_cost, underfunding_max_risk):
        claimed_payment = self.report_payment['claimed_payment']
        expected_payment = np.nansum(expected_report.expected_values * tarifs)
        if expected_payment == 0:
            expected_payment = 1
        alarm = (claimed_payment - expected_payment > mean_supervision_cost) | (claimed_payment / expected_payment  < underfunding_max_risk)
        self.alarm = alarm



#----------------------------------------------------------------------------------------------------------------


def aggregate_data_payment(data):
    """ Reports Summaries

    Computes the reports claimed and verified payments

    Returns
    -------
    report_payments : Dictionnary
        The payment for the report. Contains both the claimed payment and the verified payment.
    """
    claimed_payment = sum(data.indicator_claimed_value * data.indicator_tarif)
    verified_payment = sum(data.indicator_verified_value * data.indicator_tarif)
    report_payments = pd.DataFrame([{'claimed_payment': claimed_payment, 'verified_payment': verified_payment}])
    return report_payments

def create_facility_training_dict(orbf_data, perc_train):
    TS = {}
    indicators = orbf_data.indicator_label.unique()
    months = orbf_data.date.sort_values().unique()
    n_months = len(months)
    n_train_months = int(perc_train * n_months)
    train_months = months[0:n_train_months]
    train_data = orbf_data[orbf_data.date.isin(train_months.tolist())]
    TS['train_months'] = train_months
    TS['indicators'] = {}
    for u in indicators:
        TS['indicators'][u] = {'training_set':  [],
                               'tarif': orbf_data.indicator_tarif[orbf_data.indicator_label == u].tolist()[0],
                               'kept_values': []
                               }
        if len(train_data.indicator_verified_value[orbf_data.indicator_label == u].tolist()) > 0:
            TS['indicators'][u]['training_set'] = train_data.indicator_verified_value[
                train_data.indicator_label == u].tolist()
    return TS


def update_training_set(training_dict, indicator, new_value):
    training_dict['indicators'][indicator]['training_set'].append(new_value)
    training_dict['indicators'][indicator]['kept_values'].append(new_value)
    return training_dict

def data_submit(data, indicator):
    new_values = {'verified_value': np.nan}
    if indicator in data.index:

        dat_ind = data.loc[indicator]
        ## At least one report as two values for one indicator, so filtering for that
        if len(dat_ind.shape) > 1:
            dat_ind = dat_ind.iloc[dat_ind.shape[0] - 1]

        new_values = {'claimed_value': dat_ind['indicator_claimed_value'],
                      'verified_value': dat_ind['indicator_verified_value']}
    return new_values

def summary_cost(payments, verification_cost):
    total_cost = payments + verification_cost
    perc_supervision = verification_cost / total_cost
    return {'total_cost': total_cost, 'perc_supervision': perc_supervision, 'payments': payments}


def make_training_set(TS, data_month, alarm):
    payment_made = 0
    updates = []
    for indicator in TS['indicators'].keys():
        new_values = data_submit(data_month, indicator)
        value_update = new_values['verified_value']
        if len(new_values) > 1:
            value_update = new_values['claimed_value'] * \
                (1 - alarm) + new_values['verified_value'] * alarm
            TS = update_training_set(TS, indicator, value_update)
            payment_made = payment_made + value_update * \
                TS['indicators'][indicator]['tarif']
        updates.append(value_update)
    updates = pd.Series(updates, index=list(TS['indicators'].keys()))
    return {'payment_made': payment_made, 'value_updated': updates}


def arima_report_payment(dat_month, TS):
    expected_values = []
    std_vals = []
    for indicator in TS['indicators'].keys():
        training_set = TS['indicators'][indicator]['training_set']
        yhat = np.nan
        standard_dev = np.nan
        if len(set(training_set)) > 1:
            try:
                model_fit = ARIMA(training_set, order=(1, 0, 0)).fit(disp=0)
                prediction = model_fit.forecast()
                standard_dev = model_fit.resid.std()
                yhat = prediction[0][0]
            except ValueError:
                yhat = np.mean(training_set)
        expected_values.append(yhat)
        std_vals.append(standard_dev)
    expected_values = pd.Series(
        expected_values, index=list(TS['indicators'].keys()))
    std_vals = pd.Series(std_vals, index=list(TS['indicators'].keys()))
    return {'expected_values':expected_values ,
            'std_vals':std_vals}


def overcost_alarm(claimed_values, expected_values, tarifs, mean_supervision_cost, underfunding_max_risk):
    claimed_payment = np.nansum(claimed_values * tarifs)
    expected_payments = np.nansum(tarifs * expected_values)
    if claimed_payment == 0:
        claimed_payment = 1
    alarm = (claimed_payment - expected_payments > mean_supervision_cost) | (
        claimed_payment / expected_payments  < underfunding_max_risk)
    return alarm


def make_output(data , expectation, validated, alarms):
    out = {'claimed': data['indicator_claimed_value'], 'verified': data['indicator_verified_value'],
                       'expected': expectation, 'validated':validated['value_updated'] ,  'alarm':alarms}
    return out

def collapse_output(result , tarifs):
    output = {}
    fac_id = list(result.keys())[0]
    date = []
    claimed = []
    verified = []
    expected = []
    validated = []
    alarms = []
    for month in sorted(result[fac_id].keys()) :
        date.append(datetime.strptime(str(month) , '%Y-%d'))
        #date.append(month)
        claimed.append(np.nansum(result[fac_id][month]['claimed']*tarifs ))
        verified.append(np.nansum(result[fac_id][month]['verified']*tarifs))
        expected.append(np.nansum(result[fac_id][month]['expected']*tarifs))
        validated.append(np.nansum(result[fac_id][month]['validated']*tarifs))
        alarms.append(result[fac_id][month]['alarm'])
    out = {'date':date , 'claimed':claimed , 'verified':verified , 'expected':expected , 'validated':validated , 'alarms':alarms}
    output[fac_id] = out
    return output

def plot_monitoring(collapsed_output):
    plt.plot(collapsed_output['claimed'] , '--' , alpha=0.6 , label = 'Claimed Payment')
    plt.plot(collapsed_output['verified'] , '--r' , alpha=0.6 , label = 'Verified Payment')
    plt.plot(collapsed_output['expected'] , '-.g' , alpha = 0.7 , label = 'Expected Payment')
    plt.plot(pd.Series(collapsed_output['validated']) , 'k' , alpha = 0.4 , label = 'Validated Payment')
    plt.plot(pd.Series(collapsed_output['validated'])[collapsed_output['alarms']] , 'ro' , label = 'Verification Triggered')
    plt.plot(pd.Series(collapsed_output['validated'])[(pd.Series(collapsed_output['alarms']) == False)] , 'bo' , label = 'No Verification')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()


## TODO Add the alarms as different types, for later averaging
