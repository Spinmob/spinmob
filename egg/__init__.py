# existing libraries (install these)
import pyqtgraph
import numpy  as _n

# home-made code
import spinmob as _spinmob

try:    from . import _gui as gui
except:        import _gui as gui

dialogs           = _spinmob.dialogs
data              = _spinmob.data
settings          = _spinmob.settings
gui._settings     = settings
dialogs._settings = settings

clear_egg_settings = gui.clear_egg_settings

