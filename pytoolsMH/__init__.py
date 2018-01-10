from . import containers
from . import crossPlatform
from . import filesStreams
from . import math
from . import memProfile
from . import plotColors
from . import string
from . import image
import importlib

from . import _version
__version__ = _version.__version__

## This module uses anaconda, and so assumes numpy, scipy etc are installed.

# Don't load some modules if dependencies are missing
for tN in ['plotting', 'dataio']:
    try:
        globals()[tN] = importlib.import_module('.'+tN, __name__)
    except ImportError as e:
        print("PytoolsMH: Modules missing.  Not loading {mod}.  Message: {msg}"\
              .format(mod=tN, msg=str(e)))


