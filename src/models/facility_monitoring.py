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
        self.validated_data = data

    def monitor_new_report(self) :
        out = np.random.choice(['Validate' , 'Supervise - Data' , 'Supervise - Services' , 'Supervise - Data and Quality'])
        return out

    def make_reports(self):
        reports = {}
        for month in list(data.date.unique()) :
            reports[str(month)[:7]] = report(data[data.date == month])
        self.reports = reports
        return reports
