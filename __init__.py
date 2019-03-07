import os           as _os
import matplotlib   as _mpl
import pylab

# ignore warnings by default
import warnings as _warnings
_warnings.simplefilter("ignore")

try: 
    import pyqtgraph    as _pyqtgraph
    _qtc = _pyqtgraph.Qt.QtCore
    _qt  = _pyqtgraph.Qt
    _qtw = _pyqtgraph.Qt.QtGui

    # make sure we have a valid qt application for dialogs etc...
    _qtapp = _qtc.QCoreApplication.instance()
    if not _qtapp: _qtapp = _qtw.QApplication([])
    
except:
    print("Warning: pyqtgraph version 0.10 or higher is required (use a pip install).")
    
    _qtc = None
    _qt  = None
    _qtw = None
    

from . import _settings
settings = _settings.settings()

# some defaults
_mpl.rcParams['figure.facecolor']='w'



from . import _plot           as plot        ; plot._settings    = settings
from . import _data           as data        ; data._settings    = settings
from . import _dialogs        as dialogs     ; dialogs._settings = settings
from . import _pylab_tweaks   as tweaks      ; tweaks._settings  = settings
from . import _functions      as fun         ; fun._settings     = settings

plot.tweaks._pylab_colormap._settings = settings

instaprint = tweaks.instaprint



