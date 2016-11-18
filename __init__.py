import os           as _os
import matplotlib   as _mpl
import pylab

# ignore warnings by default
import warnings
warnings.simplefilter("ignore")

try: 
    import pyqtgraph    as _pyqtgraph
    _qtc = _pyqtgraph.Qt.QtCore
    _qt  = _pyqtgraph.Qt
    _qtw = _pyqtgraph.Qt.QtGui

    # make sure we have a valid qt application for dialogs etc...
    _qtapp = _qtc.QCoreApplication.instance()
    if not _qtapp: _qtapp = _qtw.QApplication(_os.sys.argv)
    
except:
    print("""
    Warning: PyQt4 not found, and this is needed for pyqtgraph and dialogs. 
    We are trying to solve this upgrade issue from several angles, 
    but for now an easy solution is to use Anaconda3-4.1.1 or manually 
    install everything.
    """)
    
    _qtc = None
    _qt  = None
    _qtw = None
    



from . import _settings
settings = _settings.settings()

# some defaults
_mpl.rcParams['figure.facecolor']='w'



from . import _plot             as plot        ; plot._settings    = settings
from . import _data             as data        ; data._settings    = settings
from . import _dialogs          as dialogs     ; dialogs._settings = settings
from . import _pylab_tweaks     as tweaks      ; tweaks._settings  = settings
from . import _functions        as fun         ; fun._settings     = settings

plot.tweaks._pylab_colormap._settings = settings

instaprint = tweaks.instaprint



