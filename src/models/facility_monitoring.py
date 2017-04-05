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
                    rep_month = pd.Series([report.loc[indic , 'indicator_claimed_value']] , index =[ month])
                    training_set[indic] = training_set[indic].append(rep_month)
        self.training_set = training_set


fac1 = facility(data_orbf[data_orbf.entity_id == 2])
fac1.initiate_training_set('2013-12')



data_orbf.columns
