import os           as _os
import matplotlib   as _mpl
import pylab

# Start the QApplication. Not sure why it has to be done this way.
import PyQt4.QtCore as _qtc
import PyQt4.Qt     as _qt

# make sure we have a valid qt application for dialogs etc...
_qtapp = _qtc.QCoreApplication.instance()
if not _qtapp: _qtapp = _qt.QApplication(_os.sys.argv)


#_qtapp = _qt.qApp
#if _qtapp == None:
#    print "Creating QApplication"
#    _qtapp = _qt.QApplication(_os.sys.argv)

import _settings
settings = _settings.settings()

# some defaults
_mpl.rcParams['figure.facecolor']='w'



import _plot             as plot        ; plot._settings    = settings
import _data             as data        ; data._settings    = settings
import _dialogs          as dialogs     ; dialogs._settings = settings
import _pylab_tweaks     as tweaks      ; tweaks._settings  = settings
import _functions        as fun         ; fun._settings     = settings

plot.tweaks._pylab_colormap._settings = settings

instaprint = tweaks.instaprint
