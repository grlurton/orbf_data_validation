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

    def __init__(self , data , tarifs) :
        self.facility_id = data.entity_id.iloc[0]
        self.facility_name = data.entity_name.iloc[0]
        self.reports = self.make_reports(data , tarifs)
        self.indicators = list(data.indicator_label.unique())
        self.arima_forecast = []

    def make_reports(self , data , tarifs):
        reports = {}
        for month in list(data.date.unique()) :
            reports[str(month)[:7]] = report(data[data.date == month] , tarifs)
        return reports

    def initiate_training_set(self , date):
        training_set = {}
        report_months = pd.Series(list(self.reports.keys()))
        training_months = list(report_months[report_months <= date])
        for indic in self.indicators :
            training_set[indic] = pd.Series([])
            for month in training_months :
                report = self.reports[month].report_data
                if indic in report.index:
                    rep_month = pd.Series([report.loc[indic , 'indicator_claimed_value']] , index =[datetime.strptime(str(month) , '%Y-%d')])
                    training_set[indic] = training_set[indic].append(rep_month)
        self.training_set = training_set
        self.date_training_set = date

    def arima_report_payment(self):
        arima_forecast = pd.DataFrame([] , index = [])
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
            out = pd.DataFrame([{'expected_values':yhat , 'std_vals':standard_dev}] , index=[indicator])
            arima_forecast = arima_forecast.append(out)
        self.arima_forecast.append(arima_forecast)

    def update_training_set(self , new_report):
        training_set = {}
        for indic in self.indicators :
            if indic in new_report.report_data.index:
                if new_report.alarm == False :
                    update = pd.Series([new_report.report_data.loc[indic , 'indicator_claimed_value']] , index =[new_report.date])
                if new_report.alarm == True :
                    update = pd.Series([new_report.report_data.loc[indic , 'indicator_verified_value']] , index =[new_report.date])
                self.training_set[indic] = self.training_set[indic].append(update)
        self.date_training_set = new_report.date

    def make_supervision_trail(self , tarifs , mean_supervision_cost , underfunding_max_risk):
        report_months = pd.Series(list(self.reports.keys()))
        training_months = list(report_months[report_months > str(self.date_training_set)])
        for date in sorted(training_months):
            self.arima_report_payment()
            self.reports[date].overcost_alarm(self.arima_forecast[len(self.arima_forecast) - 1] , tarifs , mean_supervision_cost , underfunding_max_risk)
            self.update_training_set(self.reports[date])

    def plot_supervision_trail(self , tarifs):
        claimed = []
        verified = []
        alarms = []
        expected = []
        for month in sorted(list(self.reports.keys())) :
            claimed.append(self.reports[month].report_payment['claimed_payment'])
            verified.append(self.reports[month].report_payment['verified_payment'])
            alarms.append(self.reports[month].alarm)
        for i in range(len(self.arima_forecast)):
            expected.append(np.nansum(self.arima_forecast[i].expected_values * tarifs))
        training_set = pd.DataFrame(self.training_set).stack()

        def validated_payments(data):
            data = data.reset_index(level = 0 , drop = True)
            out = np.nansum(data * tarifs)
            return out

        validated = training_set.groupby(level = 0).apply(mult_tarifs)
        validated = list(validated)
        plt.plot(claimed , '--' , alpha = 0.6 , label = 'Claimed Payment')
        plt.plot(expected , '-.g' , alpha = 0.7  , label = 'Forecasted Payment')
        plt.plot(verified , '--r' , alpha = 0.6 , label = 'Verified Payment')
        plt.plot(validated  , 'k' , alpha = 0.4 , label = 'Validated Payment')
        plt.plot(pd.Series(validated)[alarms] , 'ro' , label = 'Verification Triggered')
        plt.plot(pd.Series(validated)[~pd.Series(alarms)] , 'bo' , label = 'No Verification Triggered')
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.show()



mean_supervision_cost = 170000
underfunding_max_risk = 0.5
tarifs = []
for i in data_orbf.indicator_label.unique() :
    tarifs.append(data_orbf.indicator_tarif[data_orbf.indicator_label == i].tolist()[0])
tarifs = pd.Series(tarifs , index = data_orbf.indicator_label.unique())


fac1 = facility(data_orbf[data_orbf.entity_id == 180] , tarifs)
fac1.initiate_training_set('2012-01')
fac1.arima_report_payment()
fac1.make_supervision_trail(tarifs , mean_supervision_cost , underfunding_max_risk)
fac1.plot_supervision_trail(tarifs)


##TODO Store all ouputs + specific graphs on supervision. May be a new special object for that ?
