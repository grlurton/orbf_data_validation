class monitoring_algorithm(object):
    def __init__(self , monitoring_type , screening_method , alert_trigger , description = None) :
        self.type = monitoring_type
        self.screen = screening_method
        self.alert_trigger = alert_trigger
        self.description = description

    def monitor(self , data , **kwargs):
        screen_output = self.screen(data , kwargs)
        self.description_parameters = screen_output['description_parameters']
        self.trigger_parameters = screen_output['trigger_parameters']

    def raise_alert(self , **kwargs):
        alert = self.alert_trigger(self.trigger_parameters , kwargs)
        self.description_parameters.update(alert['description_parameters'])
        return alert ## si type = transversal : redistribuer les alertes dans les facilties une a une
