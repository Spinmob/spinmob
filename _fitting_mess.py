import pylab as _pylab
import matplotlib as _mpl
import spinmob as _s


import _functions as _fun           ; reload(_fun)
import _pylab_tweaks as _tweaks     ; reload(_tweaks)
import _models                      ; reload(_models)
import _dialogs                     ; reload(_dialogs)
import _data_types                  ; reload(_data_types)

from numpy import *

#
# Fit function based on the model class
#

def fit_databoxes(ds, xscript=0, yscript=1, eyscript=None, f='a*sin(x)+b', p='a=1.5, b', bg=None, a=None, command="", settings={}, g={}, **kwargs):
    """
    Create a model based on the supplied string and fit the supplied list of databoxes. 
    
    f is a string (or list of string) of the curve to fit, or a 
    function / lis of functions f(x,a,b,..) that you have defined.

    p is a comma-delimited string of parameters (with default values if
    you're into that)

    bg is the background function should you want to use it (leaving it as None
    sets it equal to f).
    
    g is a list of additional globals, for example if you have defined your
    own functions and you want these to be visible to the function string when evaluated.

    This routine just generates a model based on this input. For more information
    about what the arguments should be, see spinmob.models.curve().
    """

    globals().update(g)

    # generate the model
    model = _s.models.curve(f=f, p=p, bg=bg, a=a, globs=globals())
    result = fit_databoxes_model(ds=ds, model=model, xscript=xscript, yscript=yscript, eyscript=eyscript, command=command, settings=settings, **kwargs)

    settings = g = dict()
    return result


def fit_files(xscript=0, yscript=1, eyscript=None, f='a*sin(x)+b', p='a=1.5, b', bg=None, a=None, command="", settings={}, g={}, **kwargs):
    """
    Load a bunch of data files and fit them. kwargs are sent to "data.load_multiple()" which
    are then sent to "data.standard()". Useful ones to keep in mind:

    for loading: paths, default_directory

    See the above mentioned functions for more information.

    f is a string of the curve to fit or a function f(x,a,b,..) that you have defined.

    p is a comma-delimited string of parameters (with default values if
    you're into that)

    bg is the background function should you want to use it (leaving it as None
    sets it equal to f).
    
    g is a list of additional globals, for example if you have defined your
    own functions and you want these to be visible to the function string when evaluated.

    This routine just generates a model based on this input. For more information
    about what the arguments should be, see spinmob.models.curve().
    """

    globals().update(g)

    # generate the model
    model = _s.models.curve(f=f, p=p, bg=bg, a=a, globs=globals())
    result = fit_files_model(model=model, xscript=xscript, yscript=yscript, eyscript=eyscript, command=command, settings=settings, **kwargs)

    settings = g = dict()
    return result



def fit_files_model(model, xscript=0, yscript=1, eyscript=None, command="", settings={}, **kwargs):
    """
    Load a bunch of data files and fit them using fit_databoxes_model(). 
    
    kwargs are sent to "data.load_multiple()" which
    are then sent to "data.databox()". Useful ones to keep in mind:

    for loading:                paths, default_directory
    for generating data to fit: xscript, yscript, eyscript

    See the above mentioned functions for more information.
    """

    # Have the user select a bunch of files.
    ds = _s.data.load_multiple(**kwargs)
    result = fit_databoxes_model(ds=ds, model=model, xscript=xscript, yscript=yscript, eyscript=eyscript, command=command, settings=settings, **kwargs)

    settings = dict()
    return result



def fit_databoxes_model(ds, model, xscript=0, yscript=1, eyscript=None, command="", settings={}, **kwargs):
    """
    Loops over the supplied databoxe(s) and fits them using the supplied model    
    
    kwargs are sent to "data.load_multiple()" which
    are then sent to "data.standard()". Useful ones to keep in mind:

    for loading:                paths, default_directory
    for generating data to fit: xscript, yscript, eyscript

    See the above mentioned functions for more information.
    """
    if not ds: return
    if not _s.fun.is_iterable: ds = [ds]

    results = []
    
    for d in ds:
        print '\n\n\nFILE:', ds.index(d)+1, '/', len(ds)
        print str(d.path)
        model.fit_parameters = None
        settings["xscript"]  = xscript
        settings["yscript"]  = yscript
        settings["eyscript"] = eyscript

        # do the interactive fit.
        results.append(model.fit(d, command, settings))
        results[-1]['databox'] = d
        
        # make sure we didn't quit.
        if results[-1]['command'] == 'q': break

        # prepare for the next file.
        command=''
        if results[-1].has_key('settings'): settings = results[-1]['settings']

    # clean up
    settings = dict()
    return results
    

def fit_shown_data(f='a*sin(x)+b', p='a=1.5, b', bg=None, a=None, command="", settings={}, axes="gca", **kwargs):
    """
    Loops over the shown data, performing a fit in a separate figure.
    Loops over the shown data, performing a fit in a separate figure.
    ***kwargs are sent to fit()
    """

    # get the axes
    if axes == "gca": axes = _pylab.gca()

    xlabel=axes.get_xlabel()
    ylabel=axes.get_ylabel()
    if xlabel == '' :
        xlabel='x'
    if ylabel == '' :
        ylabel='y'

    # get the xlimits
    xmin, xmax = axes.get_xlim()

    # get the output axes
    fn0 = axes.figure.number
    
    # create the data object for fitting
    d = _s.data.standard(xlabel,ylabel,None)

    # generate the model
    model = _s.models.curve(f=f, p=p, bg=bg, a=a, globs=globals())

    # loop over the data
    lines = axes.get_lines()
    results = []
    for n in range(len(lines)):
        line = lines[n]
        if isinstance(line, _mpl.lines.Line2D):
            # get the trimmed data from the line
            x, y    = line.get_data()
            x, y, e = _fun.trim_data(x,y,None,[xmin,xmax])

            # put together a data object with the right parameters
            d.path = "Line: "+line.get_label()
            d[xlabel] = x
            d[ylabel] = y
            settings['xscript'] = xlabel
            settings['yscript'] = ylabel

            # do the fit
            print '\n\n\nLINE:', n+1, '/', len(lines)
            model.fit_parameters = None
            settings['autopath'] = False
            settings['figure']   = axes.figure.number+1
            results.append(model.fit(d, command, settings))
            results[-1]['databox'] = d

            # make sure we didn't quit.
            if results[-1]['command'] == 'q': break

            # prepare for the next file.
            command=''
            if results[-1].has_key('settings'): settings = results[-1]['settings']

    # clean up
    settings = dict()
    _pylab.figure(fn0)
    return results











