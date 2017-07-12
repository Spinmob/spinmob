# existing libraries (install these)
import pyqtgraph
import numpy as _n

# home-made code
import spinmob as _spinmob
from . import _gui      as gui

dialogs           = _spinmob.dialogs
data              = _spinmob.data
settings          = _spinmob.settings
gui._settings     = settings
dialogs._settings = settings

print("\nWelcome to the Sankey Lab Easy Gui Generator! See Spinmob Wiki and example scripts for basic usage. Note to IPython users: You may need to set the graphics backend to 'Qt5' prior to running.\n")
print("To learn more about pyqtgraph widgets, use:")
print("  >>> import pyqtgraph.examples")
print("  >>> import pyqtgraph.examples.run()\n")


