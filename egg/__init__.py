# home-made code also sets the backend (important!)
import spinmob as _spinmob
#_spinmob.plot.xy.data([1,2,3],[1,2,1], autoformat=False)

# existing libraries (install these)
import pyqtgraph
import numpy  as _n

try:    from . import _gui as gui
except:        import _gui as gui

dialogs           = _spinmob.dialogs
data              = _spinmob.data
settings          = _spinmob.settings
gui._settings     = settings
dialogs._settings = settings

clear_egg_settings = gui.clear_egg_settings

