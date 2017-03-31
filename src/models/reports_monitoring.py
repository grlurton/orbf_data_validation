import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARIMA
from datetime import datetime

#%matplotlib inline


def aggregate_data_payment(orbf_data):
    claimed_payment = sum(
        orbf_data.indicator_claimed_value * orbf_data.indicator_tarif)
    verified_payment = sum(
        orbf_data.indicator_verified_value * orbf_data.indicator_tarif)
    return pd.DataFrame([{'claimed_payment': claimed_payment, 'verified_payment': verified_payment}])


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
        expected_payments / claimed_payment > underfunding_max_risk)
    return alarm


def make_output(data , expectation, validated, alarms):
    out = {'claimed': data['indicator_claimed_value'], 'verified': data['indicator_verified_value'],
                       'expected': expectation, 'validated':validated['value_updated'] ,  'alarm':alarms}
    return out

def collapse_output(result , tarifs):
    date = []
    claimed = []
    verified = []
    expected = []
    validated = []
    alarms = []
    for month in sorted(result.keys()) :
        date.append(datetime.strptime(month , '%Y-%d'))
        claimed.append(np.nansum(result[month]['claimed']*tarifs ))
        verified.append(np.nansum(result[month]['verified']*tarifs))
        expected.append(np.nansum(result[month]['expected']*tarifs))
        validated.append(np.nansum(result[month]['validated']*tarifs))
        alarms.append(result[month]['alarm'])
    return {'date':date , 'claimed':claimed , 'verified':verified , 'expected':expected , 'validated':validated , 'alarms':alarms}

def plot_monitoring(collapsed_output):
    plt.plot(collapsed_output['claimed'] , '--' , alpha=0.6 , label = 'Claimed Payment')
    plt.plot(collapsed_output['verified'] , '--r' , alpha=0.6 , label = 'Verified Payment')
    plt.plot(collapsed_output['expected'] , '-.g' , alpha = 0.7 , label = 'Expected Payment')
    plt.plot(pd.Series(collapsed_output['validated']) , 'k' , alpha = 0.4 , label = 'Validated Payment')
    plt.plot(pd.Series(collapsed_output['validated'])[collapsed_output['alarms']] , 'ro' , label = 'Verification Triggered')
    plt.plot(pd.Series(collapsed_output['validated'])[(pd.Series(collapsed_output['alarms']) == False)] , 'bo' , label = 'No Verification')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()


import fuzzy
