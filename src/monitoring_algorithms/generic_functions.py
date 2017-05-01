def get_ecarts(data , ):
    return sum(data['indicator_claimed_value'] - data['indicator_validated_value']) / sum(data['indicator_claimed_value'])

def get_revenu_gagne(data):
    return sum(data['verified_payment'])

def get_volume_financier_recupere(data) :
    return sum(data['claimed_payment'] - data['verified_payment'])

def get_payments(data):
    data['claimed_payment'] = list(data.indicator_claimed_value * data['indicator_tarif'])
    data['verified_payment'] = list(data.indicator_validated_value * data['indicator_tarif'])
    return data
## FIXME 'verified_payment' should be 'validated_payment'. Check where this is used eleswhere.

def get_facilities_name(facility):
    return facility.facility_name

def get_name_facilities_list(list_facilities):
    return list(map(get_facilities_name , list_facilities))

def get_facility(list_facilities , facility_name):
    list_name_facilites = get_name_facilities_list(list_facilities)
    return list_facilities[list_name_facilites.index(facility_name)]
