import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class facility(object):
    """ A Facility currently under monitoring

    """

    def __init__(self , data) :
        self.validated_data = data

    def monitor_new_report(self) :
        out = np.random.choice(['Validate' , 'Supervise - Data' , 'Supervise - Services' , 'Supervise - Data and Quality'])
        return out


u = facility('a')

u.monitor_new_report()
