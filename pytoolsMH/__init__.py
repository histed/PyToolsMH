from . import containers
from . import crossPlatform
from . import filesStreams
from . import math
from . import memProfile
from . import plotColors
from . import string

# note: requires statsmodels and pandas
try:
    from . import plotting
    from . import dataio
except ImportError:
    print("Modules missing, not loading plotting, dataio - needs fixing")

