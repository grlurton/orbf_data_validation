import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from bokeh.plotting import figure, output_notebook, show, gridplot
from bokeh.models import (
    BasicTicker,
    ColumnDataSource,
    Grid, LinearAxis,
    PanTool,
    WheelZoomTool)
from bokeh.embed import components

import warnings
from datetime import datetime
from IPython.display import set_matplotlib_formats
import sys

sys.path.insert(0, '../../src/monitoring_algorithms/')
from generic_functions import *

# Import the monitoring scripts
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

warnings.filterwarnings('ignore')
