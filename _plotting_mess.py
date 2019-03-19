import os           as _os
import pylab        as _pylab
import numpy        as _n
import itertools    as _itertools
import time         as _time


try:    from . import _functions as _fun
except:        import _functions as _fun

try:    from . import _pylab_tweaks as _pt
except:        import _pylab_tweaks as _pt

from . import _data as _data

try:    from . import _data as _data
except:        import _data as _data

# expose all the eval statements to all the functions in numpy
from numpy import *
from scipy.special import *

# handle for the colormap so it doesn't immediately close
_colormap = None

def _match_data_sets(x,y):
    """
    Makes sure everything is the same shape. "Intelligently".
    """
    # Handle the None for x or y
    if x is None: 
        # If x is none, y can be either [1,2] or [[1,2],[1,2]]
        if _fun.is_iterable(y[0]):
            # make an array of arrays to match
            x = []
            for n in range(len(y)):
                x.append(list(range(len(y[n]))))
        else: x = list(range(len(y)))
    
    if y is None: 
        # If x is none, y can be either [1,2] or [[1,2],[1,2]]
        if _fun.is_iterable(x[0]):
            # make an array of arrays to match
            y = []
            for n in range(len(x)):
                y.append(list(range(len(x[n]))))
        else: y = list(range(len(x)))
    
    # At this point they should be matched, but may still be 1D
    # Default behavior: if all elements are numbers in both, assume they match
    if _fun.elements_are_numbers(x) and _fun.elements_are_numbers(y):
        x = [x]
        y = [y]
           
    # Second default behavior: shared array [1,2,3], [[1,2,1],[1,2,1]] or vis versa
    if _fun.elements_are_numbers(x) and not _fun.elements_are_numbers(y): x = [x]*len(y)
    if _fun.elements_are_numbers(y) and not _fun.elements_are_numbers(x): y = [y]*len(x)

    # Clean up any remaining Nones
    for n in range(len(x)):
        if x[n] is None: x[n] = list(range(len(y[n])))
        if y[n] is None: y[n] = list(range(len(x[n])))
    
    return x, y

def _match_error_to_data_set(x, ex):
    """
    Inflates ex to match the dimensionality of x, "intelligently". 
    x is assumed to be a 2D array.
    """
    # Simplest case, ex is None or a number
    if not _fun.is_iterable(ex):
        
        # Just make a matched list of Nones
        if ex is None: ex = [ex]*len(x)
        
        # Make arrays of numbers
        if _fun.is_a_number(ex): 
            value = ex # temporary storage
            ex    = []
            for n in range(len(x)): 
                ex.append([value]*len(x[n]))
    
    # Otherwise, ex is iterable
    
    # Default behavior: If the elements are all numbers and the length matches
    # that of the first x-array, assume this is meant to match all the x
    # data sets
    if _fun.elements_are_numbers(ex) and len(ex) == len(x[0]): ex = [ex]*len(x)

    # The user may specify a list of some iterable and some not. Assume
    # in this case that at least the lists are the same length    
    for n in range(len(x)):
        # do nothing to the None's
        # Inflate single numbers to match
        if _fun.is_a_number(ex[n]): ex[n] = [ex[n]]*len(x[n])
        
    return ex    
    

    
        
def complex_data(data, edata=None, draw=True, **kwargs):
    """
    Plots the imaginary vs real for complex data.

    Parameters
    ----------
    data             
        Array of complex data
    edata=None       
        Array of complex error bars
    draw=True
        Draw the plot after it's assembled?
    See spinmob.plot.xy.data() for additional optional keyword arguments.
    """
    _pylab.ioff()

    # generate the data the easy way
    try:
        rdata = _n.real(data)
        idata = _n.imag(data)
        if edata is None:
            erdata = None
            eidata = None
        else:
            erdata = _n.real(edata)
            eidata = _n.imag(edata)

    # generate the data the hard way.
    except:
        rdata = []
        idata = []
        if edata is None:
            erdata = None
            eidata = None
        else:
            erdata = []
            eidata = []

        for n in range(len(data)):
            rdata.append(_n.real(data[n]))
            idata.append(_n.imag(data[n]))

            if not edata is None:
                erdata.append(_n.real(edata[n]))
                eidata.append(_n.imag(edata[n]))

    if 'xlabel' not in kwargs:    kwargs['xlabel'] = 'Real'
    if 'ylabel' not in kwargs:    kwargs['ylabel'] = 'Imaginary'

    xy_data(rdata, idata, eidata, erdata, draw=False, **kwargs)

    if draw:
        _pylab.ion()
        _pylab.draw()
        _pylab.show()




def complex_databoxes(ds, script='d[1]+1j*d[2]', escript=None, **kwargs):
    """
    Uses databoxes and specified script to generate data and send to 
    spinmob.plot.complex_data()


    Parameters
    ----------
    ds            
        List of databoxes
    script='d[1]+1j*d[2]' 
        Complex-valued script for data array.
    escript=None      
        Complex-valued script for error bars

    See spinmob.plot.complex.data() for additional optional keyword arguments.
    See spinmob.data.databox.execute_script() for more information about scripts.
    """
    datas  = []
    labels = []
    if escript is None: errors = None
    else:             errors = []

    for d in ds:
        datas.append(d(script))
        labels.append(_os.path.split(d.path)[-1])
        if not escript is None: errors.append(d(escript))

    complex_data(datas, errors, label=labels, **kwargs)

    if "draw" in kwargs and not kwargs["draw"]: return

    _pylab.ion()
    _pylab.draw()
    _pylab.show()
    
    return ds



def complex_files(script='d[1]+1j*d[2]', escript=None, paths=None, **kwargs):
    """
    Loads files and plots complex data in the real-imaginary plane.

    Parameters
    ----------
    script='d[1]+1j*d[2]'       
        Complex-valued script for data array.
    escript=None       
        Complex-valued script for error bars
    paths=None
        List of paths to open. None means use a dialog

    See spinmob.plot.complex.data() for additional optional keyword arguments.
    See spinmob.data.databox.execute_script() for more information about scripts.
    
    Common additional parameters
    ----------------------------
    filters="*.*" 
        Set the file filters for the dialog.

    """
    ds = _data.load_multiple(paths=paths)

    if len(ds) == 0: return

    if 'title' not in kwargs: kwargs['title'] = _os.path.split(ds[0].path)[0]

    return complex_databoxes(ds, script=script, **kwargs)


def complex_function(f='1.0/(1+1j*x)', xmin=-1, xmax=1, steps=200, p='x', g=None, erange=False, **kwargs):
    """
    Plots function(s) in the complex plane over the specified range.

    Parameters
    ----------
    f='1.0/(1+1j*x)'                 
        Complex-valued function or list of functions to plot. 
        These can be string functions or single-argument python functions;
        additional globals can be supplied by g.
    xmin=-1, xmax=1, steps=200   
        Range over which to plot and how many points to plot
    p='x'
        If using strings for functions, p is the independent parameter name.
    g=None               
        Optional dictionary of extra globals. Try g=globals()!
    erange=False              
        Use exponential spacing of the x data?

    See spinmob.plot.xy.data() for additional optional keyword arguments.
    """
    kwargs2 = dict(xlabel='Real', ylabel='Imaginary')
    kwargs2.update(kwargs)
    function(f, xmin, xmax, steps, p, g, erange, plotter=xy_data, complex_plane=True, draw=True, **kwargs2)

def magphase_data(xdata, ydata, eydata=None, exdata=None, xscale='linear', mscale='linear', pscale='linear', mlabel='Magnitude', plabel='Phase', phase='degrees', figure='gcf', clear=1, draw=True,  **kwargs):
    """
    Plots the magnitude and phase of complex ydata vs xdata.

    Parameters
    ----------
    xdata               
        Real-valued x-axis data
    ydata               
        Complex-valued y-axis data
    eydata=None         
        Complex-valued y-error
    exdata=None         
        Real-valued x-error
    xscale='linear'     
        'log' or 'linear' scale of the x axis
    mscale='linear'     
        'log' or 'linear' scale of the magnitude axis
    pscale='linear'     
        'log' or 'linear' scale of the phase axis
    mlabel='Magnitude'  
        y-axis label for magnitude plot
    plabel='Phase'      
        y-axis label for phase plot
    phase='degrees'     
        'degrees' or 'radians' for the phase axis
    figure='gcf'        
        Plot on the specified figure instance or 'gcf' for current figure.
    clear=1             
        Clear the figure?
    draw=True
        Draw the figure when complete?

    See spinmob.plot.xy.data() for additional optional keyword arguments.
    """
    _pylab.ioff()
    
    # set up the figure and axes
    if figure == 'gcf': f = _pylab.gcf()
    if clear: f.clear()
    axes1 = _pylab.subplot(211)
    axes2 = _pylab.subplot(212,sharex=axes1)

    # Make sure the dimensionality of the data sets matches
    xdata, ydata = _match_data_sets(xdata, ydata)
    exdata = _match_error_to_data_set(xdata, exdata)
    eydata = _match_error_to_data_set(ydata, eydata)

    # convert to magnitude and phase
    m  = []
    p  = []
    em = []
    ep = []
    
    # Note this is a loop over data sets, not points.
    for l in range(len(ydata)):
        m.append(_n.abs(ydata[l]))
        p.append(_n.angle(ydata[l]))
        # get the mag - phase errors
        if eydata[l] is None:
            em.append(None)
            ep.append(None)
        else:
            er = _n.real(eydata[l])
            ei = _n.imag(eydata[l])
            em.append(0.5*((er+ei) + (er-ei)*_n.cos(p[l]))      )
            ep.append(0.5*((er+ei) - (er-ei)*_n.cos(p[l]))/m[l] )

        # convert to degrees
        if phase=='degrees': 
            p[-1] = p[-1]*180.0/_n.pi
            if not ep[l] is None: 
                ep[l] = ep[l]*180.0/_n.pi


    if phase=='degrees':         plabel = plabel + " (degrees)"
    else:                        plabel = plabel + " (radians)"
    if 'xlabel' in kwargs: xlabel=kwargs.pop('xlabel')
    else:                        xlabel=''
    if 'ylabel' in kwargs: kwargs.pop('ylabel')

    if 'autoformat' not in kwargs: kwargs['autoformat'] = True

    autoformat = kwargs['autoformat']
    kwargs['autoformat'] = False
    kwargs['xlabel'] = ''
    xy_data(xdata, m, em, exdata, ylabel=mlabel, axes=axes1, clear=0, xscale=xscale, yscale=mscale, draw=False, **kwargs)

    kwargs['autoformat'] = autoformat
    kwargs['xlabel'] = xlabel
    xy_data(xdata, p, ep, exdata, ylabel=plabel, axes=axes2, clear=0, xscale=xscale, yscale=pscale, draw=False, **kwargs)

    axes2.set_title('')

    if draw:
        _pylab.ion()
        _pylab.draw()
        _pylab.show()


def magphase_databoxes(ds, xscript=0, yscript='d[1]+1j*d[2]', eyscript=None, exscript=None, g=None, **kwargs):
    """
    Use databoxes and scripts to generate data and plot the complex magnitude
    and phase versus xdata.

    Parameters
    ----------
    ds        
        List of databoxes
    xscript=0 
        Script for x data
    yscript='d[1]+1j*d[2]'  
        Script for y data
    eyscript=None  
        Script for y error
    exscript=None
        Script for x error
    g=None
        Optional dictionary of globals for the scripts

    See spinmob.plot.magphase.data() for additional optional keyword arguments.
    See spinmob.data.databox.execute_script() for more information about scripts.
    """
    databoxes(ds, xscript, yscript, eyscript, exscript, plotter=magphase_data, g=g, **kwargs)

def magphase_files(xscript=0, yscript='d[1]+1j*d[2]', eyscript=None, exscript=None, paths=None, g=None, **kwargs):
    """
    This will load a bunch of data files, generate data based on the supplied
    scripts, and then plot the ydata's magnitude and phase versus xdata.

    Parameters
    ----------
    xscript=0 
        Script for x data
    yscript='d[1]+1j*d[2]'  
        Script for y data
    eyscript=None  
        Script for y error
    exscript=None
        Script for x error
    paths=None
        List of paths to open.
    g=None                                    
        Optional dictionary of globals for the scripts

    See spinmob.plot.magphase.data() for additional optional arguments.
    See spinmob.data.databox.execute_script() for more information about scripts.
    
    Common additional parameters
    ----------------------------
    filters="*.*" 
        Set the file filters for the dialog.

    """
    return files(xscript, yscript, eyscript, exscript, plotter=magphase_databoxes, paths=paths, g=g, **kwargs)

def magphase_function(f='1.0/(1+1j*x)', xmin=-1, xmax=1, steps=200, p='x', g=None, erange=False, **kwargs):
    """
    Plots function(s) magnitude and phase over the specified range.

    Parameters
    ----------
    f='1.0/(1+1j*x)'                 
        Complex-valued function or list of functions to plot. 
        These can be string functions or single-argument python functions;
        additional globals can be supplied by g.
    xmin=-1, xmax=1, steps=200   
        Range over which to plot and how many points to plot
    p='x'
        If using strings for functions, p is the independent parameter name.
    g=None               
        Optional dictionary of extra globals. Try g=globals()!
    erange=False              
        Use exponential spacing of the x data?

    See spinmob.plot.xy.data() for additional optional keyword arguments.
    """
    function(f, xmin, xmax, steps, p, g, erange, plotter=magphase_data, **kwargs)





def realimag_data(xdata, ydata, eydata=None, exdata=None, xscale='linear', rscale='linear', iscale='linear', rlabel='Real', ilabel='Imaginary', figure='gcf', clear=1, draw=True, **kwargs):
    """
    Plots the real and imaginary parts of complex ydata vs xdata.

    Parameters
    ----------
    xdata
        Real-valued x-axis data
    ydata               
        Complex-valued y-axis data
    eydata=None         
        Complex-valued y-error
    exdata=None         
        Real-valued x-error
    xscale='linear'     
        'log' or 'linear' scale of the x axis
    rscale='linear'     
        'log' or 'linear' scale of the real axis
    iscale='linear'     
        'log' or 'linear' scale of the imaginary axis
    rlabel='Magnitude'  
        y-axis label for real value plot
    ilabel='Phase'      
        y-axis label for imaginary value plot
    figure='gcf'        
        Plot on the specified figure instance or 'gcf' for current figure.
    clear=1             
        Clear the figure?
    draw=True
        Draw the figure when completed?

    See spinmob.plot.xy.data() for additional optional keyword arguments.
    """
    _pylab.ioff()

    # Make sure the dimensionality of the data sets matches
    xdata, ydata = _match_data_sets(xdata, ydata)
    exdata = _match_error_to_data_set(xdata, exdata)
    eydata = _match_error_to_data_set(ydata, eydata)
    
    # convert to real imag, and get error bars
    rdata = []
    idata = []
    erdata = []
    eidata = []    
    for l in range(len(ydata)):
        rdata.append(_n.real(ydata[l]))
        idata.append(_n.imag(ydata[l]))

        if eydata[l] is None:
            erdata.append(None)
            eidata.append(None)
        else:
            erdata.append(_n.real(eydata[l]))
            eidata.append(_n.imag(eydata[l]))

    # set up the figure and axes
    if figure == 'gcf': f = _pylab.gcf()
    if clear: f.clear()
    axes1 = _pylab.subplot(211)
    axes2 = _pylab.subplot(212,sharex=axes1)

    if 'xlabel' in kwargs  : xlabel=kwargs.pop('xlabel')
    else:                          xlabel=''
    if 'ylabel' in kwargs  : kwargs.pop('ylabel')

    if 'tall' not in kwargs:         kwargs['tall'] = False
    if 'autoformat' not in kwargs:   kwargs['autoformat'] = True

    autoformat = kwargs['autoformat']
    kwargs['autoformat'] = False
    kwargs['xlabel'] = ''
    xy_data(xdata, rdata, eydata=erdata, exdata=exdata, ylabel=rlabel, axes=axes1, clear=0, xscale=xscale, yscale=rscale, draw=False, **kwargs)

    kwargs['autoformat'] = autoformat
    kwargs['xlabel'] = xlabel
    xy_data(xdata, idata, eydata=eidata, exdata=exdata, ylabel=ilabel, axes=axes2, clear=0, xscale=xscale, yscale=iscale, draw=False, **kwargs)

    axes2.set_title('')

    if draw:
        _pylab.ion()
        _pylab.draw()
        _pylab.show()


def realimag_databoxes(ds, xscript=0, yscript="d[1]+1j*d[2]", eyscript=None, exscript=None, g=None, **kwargs):
    """
    Use databoxes and scripts to generate data and plot the real and 
    imaginary ydata versus xdata.

    Parameters
    ----------
    ds        
        List of databoxes
    xscript=0 
        Script for x data
    yscript='d[1]+1j*d[2]'  
        Script for y data
    eyscript=None  
        Script for y error
    exscript=None
        Script for x error
    g=None
        Optional dictionary of globals for the scripts

    See spinmob.plot.realimag.data() for additional optional keyword arguments.
    See spinmob.data.databox.execute_script() for more information about scripts.
    """
    databoxes(ds, xscript, yscript, eyscript, exscript, plotter=realimag_data, g=g, **kwargs)

def realimag_files(xscript=0, yscript="d[1]+1j*d[2]", eyscript=None, exscript=None, paths=None, g=None, **kwargs):
    """
    This will load a bunch of data files, generate data based on the supplied
    scripts, and then plot the ydata's real and imaginary parts versus xdata.

    Parameters
    ----------
    xscript=0 
        Script for x data
    yscript='d[1]+1j*d[2]'  
        Script for y data
    eyscript=None  
        Script for y error
    exscript=None
        Script for x error
    paths=None
        List of paths to open.
    g=None                                    
        Optional dictionary of globals for the scripts

    See spinmob.plot.realimag.data() for additional optional arguments.
    See spinmob.data.databox.execute_script() for more information about scripts.
    
    Common additional parameters
    ----------------------------
    filters="*.*" 
        Set the file filters for the dialog.
    """
    return files(xscript, yscript, eyscript, exscript, plotter=realimag_databoxes, paths=paths, g=g, **kwargs)


def realimag_function(f='1.0/(1+1j*x)', xmin=-1, xmax=1, steps=200, p='x', g=None, erange=False, **kwargs):
    """
    Plots function(s) real and imaginary parts over the specified range.

    Parameters
    ----------
    f='1.0/(1+1j*x)'                 
        Complex-valued function or list of functions to plot. 
        These can be string functions or single-argument python functions;
        additional globals can be supplied by g.
    xmin=-1, xmax=1, steps=200   
        Range over which to plot and how many points to plot
    p='x'
        If using strings for functions, p is the independent parameter name.
    g=None               
        Optional dictionary of extra globals. Try g=globals()!
    erange=False              
        Use exponential spacing of the x data?

    See spinmob.plot.xy.data() for additional optional keyword arguments.
    """
    function(f, xmin, xmax, steps, p, g, erange, plotter=realimag_data, **kwargs)




def xy_data(xdata, ydata, eydata=None, exdata=None, label=None, xlabel='', ylabel='',               \
            title='', shell_history=0, xshift=0, yshift=0, xshift_every=1, yshift_every=1,        \
            coarsen=0, style=None,  clear=True, axes=None, xscale='linear', yscale='linear', grid=False,       \
            legend='best', legend_max=20, autoformat=True, autoformat_window=True, tall=False, draw=True, **kwargs):
    """
    Plots specified data.

    Parameters
    ----------
    xdata, ydata        
        Arrays (or arrays of arrays) of data to plot
    eydata=None, exdata=None     
        Arrays of x and y errorbar values
    label=None         
        String or array of strings for the line labels
    xlabel=''           
        Label for the x-axis
    ylabel=''           
        Label for the y-axis
    title=''            
        Title for the axes; set to None to have nothing.
    shell_history=0     
        How many commands from the pyshell history to include with the title
    xshift=0, yshift=0  
        Progressive shifts on the data, to make waterfall plots
    xshift_every=1      
        Perform the progressive shift every 1 or n'th line.
    yshift_every=1      
        perform the progressive shift every 1 or n'th line.
    style=None            
        style cycle object.
    clear=True          
        If no axes are specified (see below), clear the figure, otherwise clear just the axes.
    axes=None           
        Which matplotlib axes to use, or "gca" for the current axes
    xscale='linear', yscale='linear'      
        'linear' or 'log' x and y axis scales.
    grid=False          
        Should we draw a grid on the axes?
    legend='best'       
        Where to place the legend (see pylab.legend() for options)
        Set this to None to ignore the legend.
    legend_max=20
        Number of legend entries before it's truncated with '...'
    autoformat=True     
        Should we format the figure for printing?
    autoformat_window=True
        Should we resize and reposition the window when autoformatting?
    tall=False               
        Should the format be tall?
    draw=True           
        Whether or not to draw the plot after plotting.

    See matplotlib's errorbar() function for additional optional keyword arguments.
    """
    _pylab.ioff()
    
    # Make sure the dimensionality of the data sets matches
    xdata, ydata = _match_data_sets(xdata, ydata)
    exdata = _match_error_to_data_set(xdata, exdata)
    eydata = _match_error_to_data_set(ydata, eydata)
    
    # check that the labels is a list of strings of the same length
    if not _fun.is_iterable(label): label = [label]*len(xdata)
    while len(label) < len(ydata):  label.append(label[0])
    
    # concatenate if necessary
    if len(label) > legend_max:
        label[legend_max-2] = '...'
        for n in range(legend_max-1,len(label)-1): label[n] = "_nolegend_"

    # clear the figure?
    if clear and not axes: _pylab.gcf().clear() # axes cleared later

    # setup axes
    if axes=="gca" or axes is None: axes = _pylab.gca()

    # if we're clearing the axes
    if clear: axes.clear()

    # set the current axes
    _pylab.axes(axes)

    # now loop over the list of data in xdata and ydata
    for n in range(0,len(xdata)):
        # get the label
        if label[n]=='_nolegend_':
            l = '_nolegend_'
        else:
            l = str(n)+": "+str(label[n])
        
        # calculate the x an y progressive shifts
        dx = xshift*(n/xshift_every)
        dy = yshift*(n/yshift_every)
        
        # if we're supposed to coarsen the data, do so.
        x  = _fun.coarsen_array(xdata[n],  coarsen)
        y  = _fun.coarsen_array(ydata[n],  coarsen)
        ey = _fun.coarsen_array(eydata[n], coarsen, 'quadrature')
        ex = _fun.coarsen_array(exdata[n], coarsen, 'quadrature')

        # update the style
        if not style is None: kwargs.update(next(style))
        axes.errorbar(x+dx, y+dy, label=l, yerr=ey, xerr=ex, **kwargs)

    _pylab.xscale(xscale)
    _pylab.yscale(yscale)
    if legend: axes.legend(loc=legend)
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)

    # for some arguments there should be no title.
    if title in [None, False, 0]:
        axes.set_title('')

    # add the commands to the title
    else:
        title = str(title)
        history = _fun.get_shell_history()
        for n in range(0, min(shell_history, len(history))):
            title = title + "\n" + history[n].split('\n')[0].strip()

        title = title + '\nPlot created ' + _time.asctime()
        axes.set_title(title)

    if grid: _pylab.grid(True)

    if autoformat:
        _pt.format_figure(draw=False, modify_geometry=autoformat_window)
        _pt.auto_zoom(axes=axes, draw=False)

    # update the canvas
    if draw:
        _pylab.ion()
        _pylab.draw()
        _pylab.show()

    return axes

def xy_databoxes(ds, xscript=0, yscript='d[1]', eyscript=None, exscript=None, g=None, **kwargs):
    """
    Use databoxes and scripts to generate and plot ydata versus xdata.

    Parameters
    ----------
    ds        
        List of databoxes
    xscript=0 
        Script for x data
    yscript='d[1]' 
        Script for y data
    eyscript=None  
        Script for y error
    exscript=None
        Script for x error
    g=None
        Optional dictionary of globals for the scripts

    See spinmob.plot.xy.data() for additional optional keyword arguments.
    See spinmob.data.databox.execute_script() for more information about scripts.
    
    """
    databoxes(ds, xscript, yscript, eyscript, exscript, plotter=xy_data, g=g, **kwargs)


def xy_files(xscript=0, yscript='d[1]', eyscript=None, exscript=None, paths=None, g=None, **kwargs):
    """
    This will load a bunch of data files, generate data based on the supplied
    scripts, and then plot the ydata versus xdata.

    Parameters
    ----------
    xscript=0 
        Script for x data
    yscript='d[1]'  
        Script for y data
    eyscript=None  
        Script for y error
    exscript=None
        Script for x error
    paths=None
        List of paths to open.
    g=None                                    
        Optional dictionary of globals for the scripts

    See spinmob.plot.xy.data() for additional optional arguments.
    See spinmob.data.databox.execute_script() for more information about scripts.
    
    
    Common additional parameters
    ----------------------------
    filters="*.*" 
        Set the file filters for the dialog.
    """
    return files(xscript, yscript, eyscript, exscript, plotter=xy_databoxes, paths=paths, g=g, **kwargs)

def xy_function(f='sin(x)', xmin=-1, xmax=1, steps=200, p='x', g=None, erange=False, **kwargs):
    """
    Plots function(s) over the specified range.

    Parameters
    ----------
    f='sin(x)'                 
        Function or list of functions to plot. 
        These can be string functions or single-argument python functions;
        additional globals can be supplied by g.
    xmin=-1, xmax=1, steps=200   
        Range over which to plot and how many points to plot
    p='x'
        If using strings for functions, p is the independent parameter name.
    g=None               
        Optional dictionary of extra globals. Try g=globals()!
    erange=False              
        Use exponential spacing of the x data?

    See spinmob.plot.xy.data() for additional optional keyword arguments.
    """
    function(f, xmin, xmax, steps, p, g, erange, plotter=xy_data, **kwargs)






def databoxes(ds, xscript=0, yscript=1, eyscript=None, exscript=None, g=None, plotter=xy_data, transpose=False, **kwargs):
    """
    Plots the listed databox objects with the specified scripts.

    ds        list of databoxes
    xscript   script for x data
    yscript   script for y data
    eyscript  script for y error
    exscript  script for x error
    plotter   function used to do the plotting
    transpose applies databox.transpose() prior to plotting
    g         optional dictionary of globals for the supplied scripts

    **kwargs are sent to plotter()
    """
    if not _fun.is_iterable(ds): ds = [ds]

    if 'xlabel' not in kwargs: kwargs['xlabel'] = str(xscript)
    if 'ylabel' not in kwargs: kwargs['ylabel'] = str(yscript)

    # First make sure everything is a list of scripts (or None's)
    if not _fun.is_iterable(xscript): xscript = [xscript]
    if not _fun.is_iterable(yscript): yscript = [yscript]
    if not _fun.is_iterable(exscript): exscript = [exscript]
    if not _fun.is_iterable(eyscript): eyscript = [eyscript]

    # make sure exscript matches shape with xscript (and the same for y)
    if len(exscript)   < len(xscript):
        for n in range(len(xscript)-1): exscript.append(exscript[0])
    if len(eyscript)   < len(yscript):
        for n in range(len(yscript)-1): eyscript.append(eyscript[0])

    # Make xscript and exscript match in shape with yscript and eyscript
    if len(xscript)    < len(yscript):
        for n in range(len(yscript)-1):
            xscript.append(xscript[0])
            exscript.append(exscript[0])

    # check for the reverse possibility
    if len(yscript)    < len(xscript):
        for n in range(len(xscript)-1):
            yscript.append(yscript[0])
            eyscript.append(eyscript[0])

    # now check for None's (counting scripts)
    for n in range(len(xscript)):
        if xscript[n] is None and yscript[n] is None:
            print("Two None scripts? But why?")
            return
        if xscript[n] is None:
            if type(yscript[n])==str: xscript[n] = 'range(len('+yscript[n]+'))'
            else:                     xscript[n] = 'range(len(c('+str(yscript[n])+')))'
        if yscript[n] is None:
            if type(xscript[n])==str: yscript[n] = 'range(len('+xscript[n]+'))'
            else:                     yscript[n] = 'range(len(c('+str(xscript[n])+')))'

    xdatas  = []
    ydatas  = []
    exdatas = []
    eydatas = []
    labels  = []


    # Loop over all the data boxes
    for i in range(len(ds)):
        
        # Reset the default globals
        all_globals = dict(n=i,m=len(ds)-1-i)
        
        # Update them with the user-specified globals
        if not g==None: all_globals.update(g)
        
        # For ease of coding
        d = ds[i]
        
        # Take the transpose if necessary
        if transpose: d = d.transpose()
        
        # Generate the x-data; returns a list of outputs, one for each xscript
        xdata = d(xscript, all_globals)
        
        # Loop over each xdata, appending to the master list, and generating a label
        for n in range(len(xdata)):
            xdatas.append(xdata[n])
            if len(xdata)>1: labels.append(str(n)+": "+_os.path.split(d.path)[-1])
            else:            labels.append(_os.path.split(d.path)[-1])

        # Append the other data sets to their master lists
        for y in d( yscript, all_globals):  ydatas.append(y)
        for x in d(exscript, all_globals): exdatas.append(x)
        for y in d(eyscript, all_globals): eydatas.append(y)

    if "label" in kwargs: labels = kwargs.pop("label")

    plotter(xdatas, ydatas, eydatas, exdatas, label=labels, **kwargs)

def files(xscript=0, yscript=1, eyscript=None, exscript=None, g=None, plotter=xy_databoxes, paths=None, **kwargs):
    """
    This will load a bunch of data files, generate data based on the supplied
    scripts, and then plot this data using the specified databox plotter.

    xscript, yscript, eyscript, exscript    scripts to generate x, y, and errors
    g                                       optional dictionary of globals

    optional: filters="*.*" to set the file filters for the dialog.

    **kwargs are sent to plotter()
    """
    if 'delimiter' in kwargs: delimiter = kwargs.pop('delimiter')
    else:                           delimiter = None

    if 'filters' in kwargs: filters = kwargs.pop('filters')
    else:                         filters = '*.*'

    ds = _data.load_multiple(paths=paths, delimiter=delimiter, filters=filters)
    if ds is None or len(ds) == 0: return

    # generate a default title (the directory)
    if 'title' not in kwargs: kwargs['title']=_os.path.split(ds[0].path)[0]

    # run the databox plotter
    plotter(ds, xscript=xscript, yscript=yscript, eyscript=eyscript, exscript=exscript, g=g, **kwargs)
    
    return ds

def function(f='sin(x)', xmin=-1, xmax=1, steps=200, p='x', g=None, erange=False, plotter=xy_data, complex_plane=False, **kwargs):
    """

    Plots the function over the specified range

    f                   function or list of functions to plot; can be string functions
    xmin, xmax, steps   range over which to plot, and how many points to plot
    p                   if using strings for functions, p is the parameter name
    g                   optional dictionary of extra globals. Try g=globals()
    erange              Use exponential spacing of the x data?
    plotter             function used to plot the generated data
    complex_plane       plot imag versus real of f?

    **kwargs are sent to spinmob.plot.real_imag.data()

    """

    if not g: g = {}
    # do the opposite kind of update()
    for k in list(globals().keys()):
        if k not in g: g[k] = globals()[k]

    # if the x-axis is a log scale, use erange
    if erange: x = _fun.erange(xmin, xmax, steps)
    else:      x = _n.linspace(xmin, xmax, steps)

    # make sure it's a list so we can loop over it
    if not type(f) in [type([]), type(())]: f = [f]

    # loop over the list of functions
    xdatas = []
    ydatas = []
    labels = []
    for fs in f:
        if type(fs) == str:
            a = eval('lambda ' + p + ': ' + fs, g)
            a.__name__ = fs
        else:
            a = fs

        # try directly evaluating
        try: y = a(x)

        # do it the slow way.
        except:
            y = []
            for z in x: y.append(a(z))

        xdatas.append(x)
        ydatas.append(y)
        labels.append(a.__name__)

    if 'xlabel' not in kwargs: kwargs['xlabel'] = p
    if 'label' not in kwargs:  kwargs['label']  = labels

    # plot!
    if complex_plane: plotter(_n.real(ydatas),_n.imag(ydatas), **kwargs)
    else:             plotter(xdatas, ydatas, **kwargs)




def image_data(Z, X=[0,1.0], Y=[0,1.0], aspect=1.0, zmin=None, zmax=None, clear=1, clabel='z', autoformat=True, colormap="Last Used", shell_history=0, **kwargs):
    """
    Generates an image plot.
    
    Parameters
    ----------
    Z   
        2-d array of z-values
    X=[0,1.0], Y=[0,1.0]
        1-d array of x-values (only the first and last element are used)
    
    See matplotlib's imshow() for additional optional arguments. 
    """
    global _colormap
    
    # Set interpolation to something more relevant for every day science
    if not 'interpolation' in kwargs.keys(): kwargs['interpolation'] = 'nearest'

    _pylab.ioff()

    fig = _pylab.gcf()
    if clear:
        fig.clear()
        _pylab.axes()

    # generate the 3d axes
    X = _n.array(X)
    Y = _n.array(Y)
    Z = _n.array(Z)

    # assume X and Y are the bin centers and figure out the bin widths
    x_width = abs(float(X[-1] - X[0])/(len(Z[0])-1))
    y_width = abs(float(Y[-1] - Y[0])/(len(Z)-1))

    # reverse the Z's
    # Transpose and reverse
    Z = Z.transpose()
    Z = Z[-1::-1]
    
    
    # get rid of the label and title kwargs
    xlabel=''
    ylabel=''
    title =''
    if 'xlabel' in kwargs: xlabel = kwargs.pop('xlabel')
    if 'ylabel' in kwargs: ylabel = kwargs.pop('ylabel')
    if 'title' in kwargs:  title  = kwargs.pop('title')

    _pylab.imshow(Z, extent=[X[0]-x_width/2.0, X[-1]+x_width/2.0,
                             Y[0]-y_width/2.0, Y[-1]+y_width/2.0], **kwargs)
    cb = _pylab.colorbar()
    _pt.image_set_clim(zmin,zmax)
    _pt.image_set_aspect(aspect)
    cb.set_label(clabel)

    a = _pylab.gca()
    a.set_xlabel(xlabel)
    a.set_ylabel(ylabel)

    #_pt.close_sliders()
    #_pt.image_sliders()

    # title
    history = _fun.get_shell_history()
    for n in range(0, min(shell_history, len(history))):
        title = title + "\n" + history[n].split('\n')[0].strip()

    title = title + '\nPlot created ' + _time.asctime()
    a.set_title(title.strip())

    if autoformat: _pt.image_format_figure(fig)

    _pylab.ion()
    _pylab.show()
    #_pt.raise_figure_window()
    #_pt.raise_pyshell()
    _pylab.draw()

    # add the color sliders
    if colormap:
        if _colormap: _colormap.close()
        _colormap = _pt.image_colormap(colormap, image=a.images[0])




def image_function(f='sin(5*x)*cos(5*y)', xmin=-1, xmax=1, ymin=-1, ymax=1, xsteps=100, ysteps=100, p='x,y', g=None, **kwargs):
    """
    Plots a 2-d function over the specified range

    Parameters
    ----------
    f='sin(5*x)*cos(5*y)'                   
        Takes two inputs and returns one value. Can also
        be a string function such as sin(x*y)
    xmin=-1, xmax=1, ymin=-1, ymax=1     
        Range over which to generate/plot the data
    xsteps=100, ysteps=100
        How many points to plot on the specified range
    p='x,y'
        If using strings for functions, this is a string of parameters.
    g=None
        Optional additional globals. Try g=globals()!
        
    See spinmob.plot.image.data() for additional optional keyword arguments.
    """

    default_kwargs = dict(clabel=str(f), xlabel='x', ylabel='y')
    default_kwargs.update(kwargs)

    # aggregate globals
    if not g: g = {}
    for k in list(globals().keys()):
        if k not in g: g[k] = globals()[k]

    if type(f) == str:
        f = eval('lambda ' + p + ': ' + f, g)


    # generate the grid x and y coordinates
    xones = _n.linspace(1,1,ysteps)
    x     = _n.linspace(xmin, xmax, xsteps)
    xgrid = _n.outer(xones, x)

    yones = _n.linspace(1,1,xsteps)
    y     = _n.linspace(ymin, ymax, ysteps)
    ygrid = _n.outer(y, yones)

    # now get the z-grid
    try:
        # try it the fast numpy way. Add 0 to assure dimensions
        zgrid = f(xgrid, ygrid) + xgrid*0.0
    except:
        print("Notice: function is not rocking hardcore. Generating grid the slow way...")
        # manually loop over the data to generate the z-grid
        zgrid = []
        for ny in range(0, len(y)):
            zgrid.append([])
            for nx in range(0, len(x)):
                zgrid[ny].append(f(x[nx], y[ny]))

        zgrid = _n.array(zgrid)

    # now plot!
    image_data(zgrid.transpose(), x, y, **default_kwargs)


def image_file(path=None, zscript='self[1:]', xscript='[0,1]', yscript='d[0]', g=None, **kwargs):
    """
    Loads an data file and plots it with color. Data file must have columns of the
    same length!

    Parameters
    ----------
    path=None
        Path to data file.
    zscript='self[1:]' 
        Determines how to get data from the columns
    xscript='[0,1]', yscript='d[0]' 
        Determine the x and y arrays used for setting the axes bounds
    g=None   
        Optional dictionary of globals for the scripts

    See spinmob.plot.image.data() for additional optional keyword arguments.
    See spinmob.data.databox.execute_script() for more information about scripts.
    """
    if 'delimiter' in kwargs: delimiter = kwargs.pop('delimiter')
    else:                           delimiter = None

    d = _data.load(paths=path, delimiter = delimiter)
    if d is None or len(d) == 0: return

    # allows the user to overwrite the defaults
    default_kwargs = dict(xlabel = str(xscript),
                          ylabel = str(yscript),
                          title  = d.path,
                          clabel = str(zscript))
    default_kwargs.update(kwargs)


    # get the data
    X = d(xscript, g)
    Y = d(yscript, g)
    Z = _n.array(d(zscript, g))
#    Z = Z.transpose()

    # plot!
    image_data(Z, X, Y, **default_kwargs)





def parametric_function(fx='sin(t)', fy='cos(t)', tmin=-1, tmax=1, steps=200, p='t', g=None, erange=False, **kwargs):
    """
    Plots the parametric function over the specified range

    Parameters
    ----------
    fx='sin(t)', fy='cos(t)'              
        Functions or (matching) lists of functions to plot; 
        can be string functions or python functions taking one argument
    tmin=-1, tmax=1, steps=200   
        Range over which to plot, and how many points to plot
    p='t'
        If using strings for functions, p is the parameter name
    g=None
        Optional dictionary of extra globals. Try g=globals()!
    erange=False
        Use exponential spacing of the t data?

    See spinmob.plot.xy.data() for additional optional keyword arguments.
    """

    if not g: g = {}
    for k in list(globals().keys()):
        if k not in g: g[k] = globals()[k]

    # if the x-axis is a log scale, use erange
    if erange: r = _fun.erange(tmin, tmax, steps)
    else:      r = _n.linspace(tmin, tmax, steps)

    # make sure it's a list so we can loop over it
    if not type(fy) in [type([]), type(())]: fy = [fy]
    if not type(fx) in [type([]), type(())]: fx = [fx]

    # loop over the list of functions
    xdatas = []
    ydatas = []
    labels = []
    for fs in fx:
        if type(fs) == str:
            a = eval('lambda ' + p + ': ' + fs, g)
            a.__name__ = fs
        else:
            a = fs

        x = []
        for z in r: x.append(a(z))

        xdatas.append(x)
        labels.append(a.__name__)

    for n in range(len(fy)):
        fs = fy[n]
        if type(fs) == str:
            a = eval('lambda ' + p + ': ' + fs, g)
            a.__name__ = fs
        else:
            a = fs

        y = []
        for z in r: y.append(a(z))

        ydatas.append(y)
        labels[n] = labels[n]+', '+a.__name__


    # plot!
    xy_data(xdatas, ydatas, label=labels, **kwargs)



class plot_style_cycle(dict):

    iterators = {}

    def __init__(self, **kwargs):
        """
        Supply keyword arguments that would be sent to pylab.plot(), except
        as a list so there is some order to follow. For example:

        style = plot_style_cycle(color=['k','r','b'], marker='o')

        """
        self.iterators = {}

        # make sure everything is iterable
        for key in kwargs:
            if not getattr(kwargs[key],'__iter__',False): kwargs[key] = [kwargs[key]]

        # The base class is a dictionary, so update our own elements!
        self.update(kwargs)

        # create the auxiliary iterator dictionary
        self.reset()

    def __repr__(self): return '{style}'

    def __next__(self):
        """
        Returns the next dictionary of styles to send to plot as kwargs.
        For example:

        pylab.plot([1,2,3],[1,2,1], **style.next())
        """
        s = {}
        for key in list(self.iterators.keys()): s[key] = next(self.iterators[key])
        return s

    def reset(self):
        """
        Resets the style cycle.
        """
        for key in list(self.keys()): self.iterators[key] = _itertools.cycle(self[key])
        return self



if __name__ == '__main__':
    xy_files(0, 'd[1]*2**n', yscale='log')