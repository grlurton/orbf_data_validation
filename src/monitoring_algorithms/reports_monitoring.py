#### This Script builds the framework to monitor individual OpenRBF reports.
## Grégoire Lurton
##
##  v1   - 3/2017 : Creates the reports objects

import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
from datetime import datetime

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

    def overcost_alarm(self , expected_report , tarifs , mean_supervision_cost, underfunding_max_risk):
        claimed_payment = self.report_payment['claimed_payment']
        expected_payment = np.nansum(expected_report.expected_values * tarifs)
        if expected_payment == 0:
            expected_payment = 1
        alarm = (claimed_payment - expected_payment > mean_supervision_cost) | (claimed_payment / expected_payment  < underfunding_max_risk)
        self.alarm = alarm
