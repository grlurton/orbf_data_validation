bm_zones =['OUIDAH-KPOMASSE-TORI-BOSSITO', 'BANIKOARA', 'LOKOSSA-ATHIEME' , 'ADJOHOUN-BONOU-DANGBO' ,
           'KOUANDE-OUASSA-PEHUNCO-KEROU','COVE-ZANGNANADO-OUINHI', 'PORTONOVO-AGUEGUES-SEME-PODJI',
           'BOHICON-ZAKPOTA-ZOGBODOMEY']

################################################################################################
######### Functions ###########################

def make_first_table(data):
    col1 = data.groupby(level = 3).apply(get_ecarts)
    col2 = data.groupby(level = 3).apply(get_revenu_gagne)
    col3 = data.groupby(level = 3).apply(get_volume_financier_recupere)
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
    ecarts = data.groupby(level=3).apply(get_ecarts)
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

def classify_facilities(ecart_moyen_pondere):
    q4_rev = ecart_moyen_pondere['Montant'].quantile(0.4)
    ecart_moyen_pondere['Class'] = 'red'
    ecart_moyen_pondere.loc[(ecart_moyen_pondere['Montant'] <= q4_rev) &
                            (ecart_moyen_pondere['Ecart Moyen Pondéré'] <= 0.1) , 'Class'] = 'green'
    ecart_moyen_pondere.loc[(ecart_moyen_pondere['Montant'] <= q4_rev) &
                            (ecart_moyen_pondere['Ecart Moyen Pondéré'] > 0.1) , 'Class'] = 'orange'
    ecart_moyen_pondere.loc[(ecart_moyen_pondere['Montant'] > q4_rev) &
                            (ecart_moyen_pondere['Ecart Moyen Pondéré'] <= 0.1), 'Class'] = 'orange'
    ecart_moyen_pondere = ecart_moyen_pondere.sort('Class')
    return ecart_moyen_pondere

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

def screen_function(data , mois , **kwargs):
    perc_risk = kwargs['perc_risk']
    data = get_payments(data)
    table_1 = make_first_table(data)
    ponderation = table_1['Volume Financier Récupéré'] / max(table_1['Volume Financier Récupéré'])
    indicateurs_critiques = list(table_1[table_1['% Cumulé'] <= perc_risk].index)
    if min(table_1['% Cumulé']) > perc_risk :
        indicateurs_critiques = table_1.index[0]
    if indicateurs_critiques == []:
        pass
    data = data.sort_index()
    data_classif = data.loc[pd.IndexSlice[:,:,: ,indicateurs_critiques] , :]
    try :
        ecart_moyen_pondere = data_classif.groupby(level=1).apply(get_ecart_pondere , ponderation = ponderation)
        ecart_moyen_pondere = classify_facilities(ecart_moyen_pondere)
    except KeyError :
        ecart_moyen_pondere = None
    return {'description_parameters':ecart_moyen_pondere}

def draw_supervision_months(description_parameters , **kwargs):
    green_fac = description_parameters[description_parameters['Class'] == 'green']
    orange_fac = description_parameters[description_parameters['Class'] == 'orange']

    green_sample = list(green_fac.sample(frac = 0.2).index)
    orange_sample = list(orange_fac.sample(frac = 0.8).index)
    red_sample = list(description_parameters[description_parameters['Class'] == 'red'].index)

    return green_sample + orange_sample + red_sample

def simulate_aedes(screening_method , trigger_supervisions , return_parameters , data , dates , **kwargs):
    for date in dates :
        month = date.month
        if month in [1 ,7]:
            screening_method(data , mois = date , **kwargs)
        trigger_supervisions(date)
        return_parameters()
