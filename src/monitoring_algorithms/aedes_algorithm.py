import pandas as pd
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt

from IPython.display import set_matplotlib_formats
plt.rcParams['figure.autolayout'] = True
plt.rcParams['figure.figsize'] = 12, 6
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['axes.titlesize'] = 20
plt.rcParams['font.size'] = 16
plt.rcParams['lines.linewidth'] = 2.0
plt.rcParams['lines.markersize'] = 8
plt.rcParams['legend.fontsize'] = 14

plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = "serif"
plt.rcParams['font.serif'] = "cm"

import warnings
warnings.filterwarnings('ignore')


bm_zones =['OUIDAH-KPOMASSE-TORI-BOSSITO', 'BANIKOARA', 'LOKOSSA-ATHIEME' , 'ADJOHOUN-BONOU-DANGBO' ,
           'KOUANDE-OUASSA-PEHUNCO-KEROU','COVE-ZANGNANADO-OUINHI', 'PORTONOVO-AGUEGUES-SEME-PODJI',
           'BOHICON-ZAKPOTA-ZOGBODOMEY']

################################################################################################
######### Functions ###########################

def get_ecarts(data):
    return sum(data['indicator_claimed_value'] - data['indicator_verified_value']) / sum(data['indicator_claimed_value'])

def get_revenu_gagne(data):
    return sum(data['indicator_montant'])

def get_volume_financier_recupere(data) :
    return sum(data['claimed_payment'] - data['verified_payment'])

def make_first_table(data):
    col1 = data.groupby(level = 0).apply(get_ecarts)
    col2 = data.groupby(level = 0).apply(get_revenu_gagne)
    col3 = data.groupby(level = 0).apply(get_volume_financier_recupere)
    col4 = col3 / get_volume_financier_recupere(data)
    output = col1.to_frame()
    output.columns = ['Ecarts']
    output['Revenus Totaux Gagnés'] = col2
    output['Volume Financier Récupéré'] = col3
    output['% Volume Financier Récupéré'] = col4

    output = output.sort_values('% Volume Financier Récupéré' , ascending = False)
    output['% Cumulé'] = output['% Volume Financier Récupéré'].cumsum()
    return output

def make_weights(ecarts):
    out = ecarts / max(ecarts)
    return out


def get_ecart_pondere(data , ponderation):
    ecarts = data.groupby('indicator_label').apply(get_ecarts)
    pond = 0
    for indic in list(ecarts.index) :
        pond = (pond  +  np.nan_to_num(ecarts[indic]*ponderation[indic]))

    ## There happens to be a few outliers, I just standardize them on 2
    if np.abs(pond) > 2:
        pond = np.sign(pond)*2
    revenu = get_revenu_gagne(data)
    out = ecarts.append(pd.Series([pond] , index = ['Ecart Moyen Pondéré']))
    out = out.append(pd.Series([revenu] , index = ['Montant']))
    return out


def make_cadran(ecart_moyen_pondere):
    q4_rev = ecart_moyen_pondere['Montant'].quantile(0.4)
    max_em = max(ecart_moyen_pondere['Ecart Moyen Pondéré'])
    max_rev = max(ecart_moyen_pondere['Montant'])
    min_em = min(ecart_moyen_pondere['Ecart Moyen Pondéré'])
    plt.fill_between(np.array([0,q4_rev]) , np.array([max_em,max_em]) , facecolor='orange')
    plt.fill_between(np.array([q4_rev, max_rev]) , np.array([max_em,max_em]) , facecolor='red')
    plt.fill_between(np.array([0,q4_rev]) , np.array([min_em,min_em]), np.array([.1,.1]) , facecolor='green')
    plt.fill_between(np.array([q4_rev, max_rev]) ,np.array([min_em,min_em]),np.array([.1,.1]) , facecolor='orange')
    plt.plot(list(ecart_moyen_pondere['Montant']) , list(ecart_moyen_pondere['Ecart Moyen Pondéré']) , 'ok')

def make_facilities_classification(data , ponderation , perc_risk):

    data['claimed_payment'] = list(data.indicator_claimed_value * data['indicator_tarif'])
    data['verified_payment'] = list(data.indicator_verified_value * data['indicator_tarif'])

    if sum(data['claimed_payment'] - data['verified_payment']) != 0 :
        data = data.set_index('indicator_label')
        table_1 = make_first_table(data)

        indicateurs_critiques = list(table_1[table_1['% Cumulé'] <= perc_risk].index)

        data_classif = data.loc[indicateurs_critiques]
        data_classif = data_classif.reset_index()

        ecart_moyen_pondere = data_classif.groupby(['entity_name']).apply(get_ecart_pondere , ponderation = ponderation)
        ecart_moyen_pondere = classify_facilities(ecart_moyen_pondere)
        return ecart_moyen_pondere
