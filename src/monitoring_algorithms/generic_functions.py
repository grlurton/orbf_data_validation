def get_ecarts(data):
    return sum(data['indicator_claimed_value'] - data['indicator_verified_value']) / sum(data['indicator_claimed_value'])

def get_revenu_gagne(data):
    return sum(data['indicator_montant'])

def get_volume_financier_recupere(data) :
    return sum(data['claimed_payment'] - data['verified_payment'])
