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

print("\nWelcome to the Sankey Lab Easy Gui Generator!")
print("  See example scripts for basic usage.\n")
print("To learn more about pyqtgraph, use:")
print("  >>> import pyqtgraph.examples")
print("  >>> import pyqtgraph.examples.run()\n")


