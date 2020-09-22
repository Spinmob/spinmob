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
_p = _traceback.print_last

# ignore warnings by default
import warnings as _warnings
_warnings.simplefilter("ignore")
_qtapp = None

# Import databox first
from . import _data      as data
from . import _functions as fun
from . import _thread    as thread
from . import _settings
settings = _settings.settings()
fun._settings  = settings
data._settings = settings

# Get the version
try: exec(fun.read_lines(_os.path.join(__path__[0],'setup.py'))[0])
except: __version__ = 'unknown'


def _warn(*args):
    if settings['ignore_warnings']: return

    args = list(args)
    print('\nWarning:', args.pop(0))
    for a in args: print('  ', a)
    print("  To disable warnings, set spinmob.settings['ignore_warnings']=True")


try:
    import pyqtgraph as _pyqtgraph
    _pyqtgraph_ok = float('.'.join(_pyqtgraph.__version__.split('.')[0:2])) > 0.1

    if not _pyqtgraph_ok: _warn('Spinmob requires pyqtgraph version 0.11 or higher. Previous versions are no longer supported.')

    _qtc = _pyqtgraph.Qt.QtCore
    _qt  = _pyqtgraph.Qt
    _qtw = _pyqtgraph.Qt.QtGui

    # make sure we have a valid qt application for dialogs etc...
    _qtapp = _qtc.QCoreApplication.instance()
    if not _qtapp: _qtapp = _qtw.QApplication([])

    # Set the dpi scaling
    _qtapp.setAttribute(_qtc.Qt.AA_EnableHighDpiScaling, True)

    # Standard Fusion light theme
    _qtapp.setStyle('Fusion')

    # Dark theme
    if settings['dark_theme_qt']: from . import _theme_fusion_dark


except:
    _warn("pyqtgraph version 0.11 or higher is required (use a conda or pip install).")

    _qtc = None
    _qt  = None
    _qtw = None
    _qtapp = None


# Try importing lmfit
try: import lmfit as _lm
except:
    _warn("spinmob.data.fitter() now requires lmfit, which is available via pip.")
    _lm = None


if _sys.version[0] == '2':
    _warn("Spinmob no longer supports Python 2.7 or below (which itself will not be maintained after Jan 1, 2020). USE AT YOUR OWN RISK!")


from . import _plot           as plot        ; plot._settings    = settings
from . import _dialogs        as dialogs     ; dialogs._settings = settings
from . import _pylab_tweaks   as tweaks      ; tweaks._settings  = settings

plot.tweaks._pylab_colormap._settings = settings

instaprint = tweaks.instaprint

# Default settings
_defaults = dict(
    dark_theme_qt         = False,
    dark_theme_figures    = False,
    font_size             = 12,
    font_size_legend      = 9,
    egg_pen_width         = 1,
    egg_use_opengl        = False,)

# Loop over defaults and set them if they don't already exist
for _k in _defaults:
    if not _k in settings.keys():
        settings[_k] = _defaults[_k]

# Touch the keys that affect visuals
for _k in [
    'font_size',
    'dark_theme_figures',
    'egg_use_opengl'
    ]:
    settings[_k] = settings[_k]








