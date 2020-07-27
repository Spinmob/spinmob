import os           as _os
import sys          as _sys
import matplotlib   as _mpl
import pylab

# Try to run the qt magic first
try:
    if not pylab.get_backend()[0:2] == 'Qt':
        get_ipython().run_line_magic('matplotlib', 'qt')
except: pass

import traceback    as _traceback
_sys.excepthook = _traceback.print_exception


# ignore warnings by default
import warnings as _warnings
_warnings.simplefilter("ignore")
_qtapp = None

# Import databox first
from . import _data      as data
from . import _functions as fun
from . import _settings
settings = _settings.settings()
fun._settings  = settings
data._settings = settings


def _warn(*args):
    if settings['ignore_warnings']: return

    args = list(args)
    print('\nWarning:', args.pop(0))
    for a in args: print('  ', a)
    print("To disable warnings, set spinmob.settings['ignore_warnings']='True'")


try:
    import pyqtgraph    as _pyqtgraph
    _qtc = _pyqtgraph.Qt.QtCore
    _qt  = _pyqtgraph.Qt
    _qtw = _pyqtgraph.Qt.QtGui

    # make sure we have a valid qt application for dialogs etc...
    _qtapp = _qtc.QCoreApplication.instance()
    if not _qtapp: _qtapp = _qtw.QApplication([])

    # Set the dpi scaling
    _qtapp.setAttribute(_qtc.Qt.AA_EnableHighDpiScaling, True)

except:
    _warn("pyqtgraph version 0.10 or higher is required (use a conda or pip install) if you wish to use dialogs or egg.")

    _qtc = None
    _qt  = None
    _qtw = None

if _qtapp is not None: _qtapp.setStyle('Fusion')

# some defaults
_mpl.rcParams['figure.facecolor']='w'


if _sys.version[0] == '2':
    _warn("Spinmob no longer supports Python 2.7 or below (which itself will not be maintained after Jan 1, 2020). USE AT YOUR OWN RISK!")


from . import _plot           as plot        ; plot._settings    = settings
from . import _dialogs        as dialogs     ; dialogs._settings = settings
from . import _pylab_tweaks   as tweaks      ; tweaks._settings  = settings

plot.tweaks._pylab_colormap._settings = settings

instaprint = tweaks.instaprint



