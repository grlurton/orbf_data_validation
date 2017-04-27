def get_ecarts(data):
    return sum(data['indicator_claimed_value'] - data['indicator_verified_value']) / sum(data['indicator_claimed_value'])

def get_revenu_gagne(data):
    return sum(data['verified_payment'])

def get_volume_financier_recupere(data) :
    return sum(data['claimed_payment'] - data['verified_payment'])

def get_payments(data):
    data['claimed_payment'] = list(data.indicator_claimed_value * data['indicator_tarif'])
    data['verified_payment'] = list(data.indicator_verified_value * data['indicator_tarif'])
    return data

def get_facilities_name(facility):
    return facility.facility_name

def get_name_facilities_list(list_facilities):
    return list(map(get_facilities_name , list_facilities))

def get_facility(list_facilities , list_name_facilites , facility_name):
    return list_facilities[list_name_facilites.index(facility_name)]