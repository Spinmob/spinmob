import os           as _os
import matplotlib   as _mpl
import pylab

# ignore warnings by default
import warnings
warnings.simplefilter("ignore")



#_qtapp = _qt.qApp
#if _qtapp == None:
#    print "Creating QApplication"
#    _qtapp = _qt.QApplication(_os.sys.argv)

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

try: 
    import PyQt4.QtCore as _qtc
    import PyQt4.Qt     as _qt
    
except:
    print("""
    Warning: PyQt4 not found. Using PyQt5, which limits
    the functionality of spinmob (in particular Easy GUI Generator, 
    which relies on pyqtgraph). We are trying to solve this 
    upgrade issue from several angles, but for now an easy solution 
    is to use Anaconda3-4.1.1 or manually install.
    """)
    import PyQt5.QtCore  as _qtc
    import PyQt5.Qt      as _qt
    import PyQt5.Widgets as _qtw

# make sure we have a valid qt application for dialogs etc...
_qtapp = _qtc.QCoreApplication.instance()
if not _qtapp: _qtapp = _qt.QApplication(_os.sys.argv)

