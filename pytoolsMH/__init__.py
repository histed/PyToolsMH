from . import containers
from . import crossPlatform
from . import filesStreams
from . import math
from . import memProfile
from . import plotColors
from . import string
from . import image

from . import _version
__version__ = _version.__version__

## This module uses anaconda, and so assumes numpy, scipy etc are installed.

# Don't load some modules if dependencies are missing
try:
    from . import plotting
except ImportError:
    print("Modules missing.  Is statsmodels installed?  Not loading plotting")

try:
    from . import dataio
except ImportError:
    print("Modules missing.  Is pandas installed?  Not loading dataio")
