#%% Load pdss data
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv('data/raw/pdss_data/compiled.csv')

#%%
def compute_payment(data):
    claimed = sum(data.claimed_value * data.tarif)
    validated = sum(data.validated_value * data.tarif)
    return pd.DataFrame({"claimed":[claimed], "validated":[validated]})

payments = data.groupby(["province","zone","aire","fosa","year","quarter","month"]).apply(compute_payment)
payments["correction"] = payments.validated - payments.claimed
payments = payments.reset_index()

payments_low_correction = payments[payments.claimed / payments.validated < 10]
plt.plot(payments_low_correction.validated, payments_low_correction.claimed/payments_low_correction.validated, "or")

#%%
payments.month = payments.month.astype(str)
payments.month[payments.month.isin(["1","2","3",'4',"5","6","7","8","9"])] = "0"+payments.month[payments.month.isin(["1","2","3",'4',"5","6","7","8","9"])]

payments["period"] = payments.year.astype(str) + payments.month.astype(str)
def compute_advance_payments(data, rule):
    advance_payments = []
    periods = data.period.unique()
    periods.sort()
    for period in periods[1:]:
        data_ante = data[data.period < period]
        advance_payment = rule(data_ante.validated)
        advance_payments.append(advance_payment)
    print(advance_payment)
    out = pd.DataFrame.from_dict({"period":periods[1:], 
                                  "advance_payments":advance_payments})
    return out

def simulate_advance_payments(data, rule):
    simulation = data.groupby(["province","zone","aire","fosa"]).apply(compute_advance_payments, rule)
    simulation = simulation.reset_index()
    out = data.merge(simulation)
    return out

def benchmark(simulated):
    simulated = simulated.dropna()
    advance_ratio = simulated.advance_payments / simulated.validated
    underfin = sum(advance_ratio < .25) / len(advance_ratio)
    overfin_val = sum(simulated.advance_payments[simulated.advance_payments > simulated.validated] - simulated.validated[simulated.advance_payments > simulated.validated])
    overfin_ratio = overfin_val / sum(simulated.validated.dropna())
    return (underfin, overfin_ratio)

#%%
simulate_min = simulate_advance_payments(payments, min)


#%%
benchmark(simulate_min)


#%%

simulate_min.advance_payments / simulate_min.validated

#%%
print(benchmark(all.advance_min, all.validated))
print(benchmark(all.advance_med_2sd, all.validated))
print(benchmark(all.min_2_advances, all.validated))


#%%
plt.plot(benchmark(all.advance_min, all.validated)[0], benchmark(all.advance_min, all.validated)[2], "or", )
plt.plot(benchmark(all.advance_med_2sd, all.validated)[0], benchmark(all.advance_med_2sd, all.validated)[2], "ob")
plt.plot(benchmark(all.min_2_advances, all.validated)[0], benchmark(all.min_2_advances, all.validated)[2], "oy")

#%%
