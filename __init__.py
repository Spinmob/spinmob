#######################################################################
# Set up the wx and matplotlib environment for use with pyshell/pycrust
#######################################################################

import wx as _wx

# setup matplotlib and wx so it works well with pyshell/pycrust
import matplotlib as _mpl
if not _mpl.get_backend() == 'WXAgg': _mpl.use('wxAgg') # set the backend (must do this first)
_mpl.rcParams['figure.facecolor']='w'

import pylab
pylab.ion()          # turn on interactive mode

import scipy
import numpy

# now get the global application
_app = _wx.GetApp()
if _app == None: _app = _wx.PySimpleApp()

#############################
# Spinmob stuff
#############################

# create the user preferences object (sets up prefs directory and stuff)
import _prefs
prefs = _prefs.Prefs()



import _dialogs as dialogs; reload(dialogs); dialogs._prefs       = prefs
import _pylab_colorslider              ;_pylab_colorslider._prefs = prefs
import _plot as plot                   ;plot._prefs               = prefs
import _functions as fun               ;fun._prefs                = prefs
import _models as models               ;models._prefs             = prefs
import _fitting as fit                 ;fit._prefs                = prefs
import _data as data                   ;data._prefs               = prefs

data._data_types._prefs = prefs

# pull some of the common functions to the top
import scipy.constants
printer   = fun.printer
constants = scipy.constants


xscale = plot.tweaks.xscale
yscale = plot.tweaks.yscale

# now do the big reload chain.

