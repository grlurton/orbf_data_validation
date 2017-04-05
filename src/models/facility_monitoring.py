import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from reports_monitoring import *

store = pd.HDFStore('../../data/processed/orbf_benin.h5')
data_orbf = store['data']
store.close()

class facility(object):
    """ A Facility currently under monitoring

    """

    def __init__(self , data) :
        self.facility_id = data.entity_id.iloc[0]
        self.facility_name = data.entity_name.iloc[0]
        self.reports = self.make_reports(data)
        self.indicators = list(data.indicator_label.unique())

    def monitor_new_report(self) :
        out = np.random.choice(['Validate' , 'Supervise - Data' , 'Supervise - Services' , 'Supervise - Data and Quality'])
        return out

    def make_reports(self , data):
        reports = {}
        for month in list(data.date.unique()) :
            reports[str(month)[:7]] = report(data[data.date == month])
        return reports

    def initiate_training_set(self , date):
        training_set = {}
        report_months = pd.Series(list(self.reports.keys()))
        training_months = list(pd.Series(list(self.reports.keys()))[report_months < date])
        for indic in self.indicators :
            training_set[indic] = pd.Series([])
            for month in training_months :
                report = self.reports[month].report_data
                if indic in report.index:
                    rep_month = pd.Series([report.loc[indic , 'indicator_claimed_value']] , index =[datetime.strptime(str(month) , '%Y-%d')])
                    training_set[indic] = training_set[indic].append(rep_month)
        self.training_set = training_set

    def arima_report_payment(self):
        expected_values = []
        std_vals = []
        for indicator in list(self.training_set.keys()):
            training_set = self.training_set[indicator]
            yhat = np.nan
            standard_dev = np.nan
            try:
                model_fit = ARIMA(training_set, order=(1, 0, 0)).fit(disp=0)
                prediction = model_fit.forecast()
                standard_dev = model_fit.resid.std()
                yhat = prediction[0][0]
            except (ValueError , np.linalg.linalg.LinAlgError , IndexError) :
                yhat = np.mean(training_set)
            expected_values.append(yhat)
            std_vals.append(standard_dev)
        expected_values = pd.Series(expected_values, index=list(self.training_set.keys()))
        std_vals = pd.Series(std_vals, index=list(self.training_set.keys()))
        arima_forecast = {'expected_values':expected_values , 'std_vals':std_vals}
        self.arima_forecast = arima_forecast


fac1 = facility(data_orbf[data_orbf.entity_id == 2])
fac1.initiate_training_set('2013-12')
fac1.arima_report_payment()

fac1.arima_forecast



ARIMA(fac1.training_set[indic], order=(1, 0, 0)).fit(disp=0)

indic = 'Accouchement eutocique assiste'

fac1.training_set
