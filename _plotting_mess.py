import os           as _os
import pylab        as _pylab
import numpy        as _numpy
import itertools    as _itertools
import time         as _time

import _functions as _fun
import _pylab_tweaks as _pt
import spinmob as _s

# for the user to get at
tweaks = _pt
_n = _numpy

# expose all the eval statements to all the functions in numpy
from numpy import *


#
# General plotting routines
#





def complex_data(data, edata=None, **kwargs):
    """
    Plots the X and Y of complex data.

    data             complex data
    edata            complex error
    
    kwargs are sent to spinmob.plot.xy.data()
    """
    # generate the data the easy way
    try:
        rdata = _n.real(data)
        idata = _n.imag(data)
        if edata==None:
            erdata = None
            eidata = None
        else:
            erdata = _n.real(edata)
            eidata = _n.imag(edata)
            
    # generate the data the hard way.            
    except:
        rdata = []
        idata = []
        if edata==None:
            erdata = None
            eidata = None
        else:
            erdata = []
            eidata = []

        for n in range(len(data)):
            rdata.append(_n.real(data[n]))
            idata.append(_n.imag(data[n]))
            
            if not edata == None:
                erdata.append(_n.real(edata[n]))
                eidata.append(_n.imag(edata[n]))

    if not kwargs.has_key('xlabel'):    kwargs['xlabel'] = 'Real'
    if not kwargs.has_key('ylabel'):    kwargs['ylabel'] = 'Imaginary'
    
    return xy_data(rdata, idata, eidata, erdata, **kwargs)



def complex_databoxes(ds, script='c(1)+1j*c(2)', escript=None, **kwargs):
    """
    Use script to generate data and send to harrisgroup.plot.complex_data()    
    
    ds            list of databoxes
    script        complex script
    escript       complex script for error bars
    
    **kwargs are sent to spinmob.plot.complex.data()    
    """
    
    datas  = []
    labels = []
    if escript==None: errors = None
    else:             errors = []
    
    for d in ds: 
        datas.append(d(script))
        labels.append(_os.path.split(d.path)[-1])
        if not escript==None: errors.append(d(escript))
    
    return complex_data(datas, errors, label=labels, **kwargs)



def complex_files(script='c(1)+1j*c(2)', **kwargs):
    """
    Loads and plots complex data in the real-imaginary plane.
    
    **kwargs are sent to spinmob.plot.complex.databoxes()    
    """
    
    ds = _s.data.load_multiple()

    if len(ds) == 0: return
    
    if not kwargs.has_key('title'): kwargs['title'] = _os.path.split(ds[0].path)[0]

    return complex_databoxes(ds, script=script, **kwargs)


def complex_function(f='1.0/(1+1j*x)', xmin=-1, xmax=1, steps=200, p='x', g=None, erange=False, **kwargs):
    """

    Plots the function over the specified range

    f                   complex-valued function or list of functions to plot; 
                        can be string functions
    xmin, xmax, steps   range over which to plot, and how many points to plot
    p                   if using strings for functions, p is the parameter name
    g                   optional dictionary of extra globals. Try g=globals()!
    erange              Use exponential spacing of the x data?

    **kwargs are sent to spinmob.plot.xy.data()
    """
    kwargs2 = dict(xlabel='Real', ylabel='Imaginary')
    kwargs2.update(kwargs)
    return function(f, xmin, xmax, steps, p, g, erange, plotter=xy_data, complex_plane=True, **kwargs2)

def magphase_data(xdata, ydata, eydata=None, exdata=None, xscale='linear', mscale='linear', pscale='linear', mlabel='Magnitude', plabel='Phase', phase='degrees', figure='gcf', clear=1,  **kwargs):
    """
    Plots the magnitude and phase of complex ydata.

    xdata               real-valued x-axis data
    ydata               complex-valued y-axis data
    eydata=None         complex-valued y-error
    exdata=None         real-valued x-error
    xscale='linear'     'log' or 'linear'
    mscale='linear'     'log' or 'linear' (only applies to the magnitude graph)
    pscale='linear'     'log' or 'linear' (only applies to the phase graph)
    mlabel='Magnitude'  y-axis label for magnitude plot
    plabel='Phase'      y-axis label for phase plot
    phase='degrees'     'degrees' or 'radians'
    figure='gcf'        figure instance
    clear=1             clear the figure?

    kwargs are sent to plot.xy.data()
    """

    if figure == 'gcf': f = _pylab.gcf()
    if clear: f.clear()

    axes1 = _pylab.subplot(211)
    axes2 = _pylab.subplot(212,sharex=axes1)

    m = _n.abs(ydata)
    p = _n.angle(ydata)
    if phase=='degrees': 
        for n in range(len(ydata)):
            p[n] = p[n]*180.0/_n.pi

    # do the elliptical error transformation
    em = []
    ep = []
    er = []
    ei = []    
    if eydata==None:
        em = None
        ep = None
        er = None
        ei = None
    else:
           
            if eydata[n] == None: 
                em.append(None)
                ep.append(None)
            else:
                er = _n.real(eydata[n])
                ei = _n.imag(eydata[n])
                em.append(0.5*((er+ei) + (er-ei)*_n.cos(p[n]))   )
                ep.append(0.5*((er+ei) - (er-ei)*_n.cos(p[n]))/m[n] )
            
            # convert to degrees
            if phase=='degrees':
                if not ep[n]==None: ep[n] = ep[n]*180.0/_n.pi       
            

    if phase=='degrees':         plabel = plabel + " (degrees)"
    else:                        plabel = plabel + " (radians)"
    if kwargs.has_key('xlabel'): xlabel=kwargs.pop('xlabel')
    else:                        xlabel=''
    if kwargs.has_key('ylabel'): kwargs.pop('ylabel')
    
    if not kwargs.has_key('draw'): kwargs['draw'] = False
    if not kwargs.has_key('tall'): kwargs['tall'] = False
    if not kwargs.has_key('autoformat'):   kwargs['autoformat'] = True

    autoformat = kwargs['autoformat']
    kwargs['autoformat'] = False    
    kwargs['xlabel'] = ''
    xy_data(xdata, m, em, exdata, ylabel=mlabel, axes=axes1, clear=0, xscale=xscale, yscale=mscale, **kwargs)

    kwargs['autoformat'] = autoformat
    kwargs['xlabel'] = xlabel
    xy_data(xdata, p, ep, exdata, ylabel=plabel, axes=axes2, clear=0, xscale=xscale, yscale=pscale, **kwargs)

    axes2.set_title('')
    _pt.auto_zoom(axes=axes1)
    _pylab.draw()


def magphase_databoxes(ds, xscript=0, yscript='c(1)+1j*c(2)', eyscript=None, exscript=None, **kwargs):
    """
    Use script to generate data and plot it. 
    
    ds        list of databoxes
    xscript   script for x data
    yscript   script for y data
    eyscript  script for y error
    exscript  script for x error
    
    **kwargs are sent to spinmob.plot.mag_phase.data()    
    """
    return databoxes(ds, xscript, yscript, eyscript, exscript, plotter=magphase_data, **kwargs)

def magphase_files(xscript=0, yscript='c(1)+1j*c(2)', eyscript=None, exscript=None, **kwargs):
    """
    This will load a bunch of data files, generate data based on the supplied
    scripts, and then plot this data. 
    
    xscript, yscript, eyscript, exscript    scripts to generate x, y, and errors
    
    **kwargs are sent to spinmob.plot.mag_phase.databoxes()
    """
    return files(xscript, yscript, eyscript, exscript, plotter=magphase_databoxes, **kwargs)

def magphase_function(f='1.0/(1+1j*x)', xmin=-1, xmax=1, steps=200, p='x', g=None, erange=False, **kwargs):
    """

    Plots the function over the specified range

    f                   function or list of functions to plot; can be string functions
    xmin, xmax, steps   range over which to plot, and how many points to plot
    p                   if using strings for functions, p is the parameter name
    g                   optional dictionary of extra globals. Try g=globals()!
    erange              Use exponential spacing of the x data?

    **kwargs are sent to plot.mag_phase.data()
    """
    return function(f, xmin, xmax, steps, p, g, erange, plotter=magphase_data, **kwargs)





def realimag_data(xdata, ydata, eydata=None, exdata=None, xscale='linear', rscale='linear', iscale='linear', rlabel='Real', ilabel='Imaginary', figure='gcf', clear=1, **kwargs):
    """
    Plots the magnitude and phase of complex ydata.

    xdata               real-valued x-data
    ydata               complex-valued y-data
    eydata              complex-valued error on y-data
    exdata              real-valued error on x-data
    xscale='linear'     'log' or 'linear'
    rscale='linear'     'log' or 'linear' for the real yscale
    iscale='linear'     'log' or 'linear' for the imaginary yscale
    rlabel='Real'       y-axis label for magnitude plot
    ilabel='Imaginary'  y-axis label for phase plot
    figure='gcf'        figure instance
    clear=1             clear the figure?

    kwargs are sent to plot.xy.data()
    """

    if figure == 'gcf': f = _pylab.gcf()
    if clear: f.clear()

    axes1 = _pylab.subplot(211)
    axes2 = _pylab.subplot(212,sharex=axes1)

    rdata = _n.real(ydata)
    idata = _n.imag(ydata)

    # HACK!!    
    if eydata==None or eydata[0]==None: 
        erdata = None
        eidata = None
    else:
        erdata = _n.real(eydata)
        eidata = _n.imag(eydata)

    if kwargs.has_key('xlabel')  : xlabel=kwargs.pop('xlabel')
    else:                          xlabel=''
    if kwargs.has_key('ylabel')  : kwargs.pop('ylabel')    
    
    if not kwargs.has_key('draw'):         kwargs['draw'] = False
    if not kwargs.has_key('tall'):         kwargs['tall'] = False
    if not kwargs.has_key('autoformat'):   kwargs['autoformat'] = True

    autoformat = kwargs['autoformat']
    kwargs['autoformat'] = False    
    kwargs['xlabel'] = ''
    xy_data(xdata, rdata, eydata=erdata, exdata=exdata, ylabel=rlabel, axes=axes1, clear=0, xscale=xscale, yscale=rscale, **kwargs)

    kwargs['autoformat'] = autoformat
    kwargs['xlabel'] = xlabel
    xy_data(xdata, idata, eydata=eidata, exdata=exdata, ylabel=ilabel, axes=axes2, clear=0, xscale=xscale, yscale=iscale, **kwargs)

    axes2.set_title('')
    _pylab.draw()

def realimag_databoxes(ds, xscript=0, yscript='c(1)+1j*c(2)', eyscript=None, exscript=None, **kwargs):
    """
    Use script to generate data and plot it.    
    
    ds        list of databoxes
    xscript   script for x data
    yscript   script for y data
    eyscript  script for y error
    exscript  script for x error
    
    **kwargs are sent to spinmob.plot.real_imag.data()    
    """
    return databoxes(ds, xscript, yscript, eyscript, exscript, plotter=realimag_data, **kwargs)

def realimag_files(xscript=0, yscript='c(1)+1j*c(2)', eyscript=None, exscript=None, **kwargs):
    """
    This will load a bunch of data files, generate data based on the supplied
    scripts, and then plot this data. 
    
    xscript, yscript, eyscript, exscript    scripts to generate x, y, and errors
    
    **kwargs are sent to spinmob.plot.real_imag.databoxes()
    """
    return files(xscript, yscript, eyscript, exscript, plotter=realimag_databoxes, **kwargs)


def realimag_function(f='1.0/(1+1j*x)', xmin=-1, xmax=1, steps=200, p='x', g=None, erange=False, **kwargs):
    """

    Plots the function over the specified range

    f                   function or list of functions to plot; can be string functions
    xmin, xmax, steps   range over which to plot, and how many points to plot
    p                   if using strings for functions, p is the parameter name
    g                   optional dictionary of extra globals. Try g=globals()!
    erange              Use exponential spacing of the x data?

    **kwargs are sent to spinmob.plot.real_imag.data()

    """
    return function(f, xmin, xmax, steps, p, g, erange, plotter=realimag_data, **kwargs)

    


def xy_data(xdata, ydata, eydata=None, exdata=None, label=None, xlabel='', ylabel='',               \
            title='', pyshell_history=1, xshift=0, yshift=0, xshift_every=1, yshift_every=1,        \
            coarsen=0, style=None,  clear=True, axes=None, xscale='linear', yscale='linear', grid=False,       \
            legend='best', autoformat=True, tall=False, draw=True, **kwargs):
    """
    Plots specified data.

    xdata, ydata        Arrays (or arrays of arrays) of data to plot
    eydata, exdata      Arrays of x and y errorbar values    
    label               string or array of strings for the line labels
    xlabel=''           label for the x-axis
    ylabel=''           label for the y-axis
    title=''            title for the axes; set to None to have nothing.
    pyshell_history=1   how many commands from the pyshell history to include 
                        with the title
    xshift=0, yshift=0  progressive shifts on the data, to make waterfall plots
    xshift_every=1      perform the progressive shift every 1 or n'th line.
    yshift_every=1      perform the progressive shift every 1 or n'th line.
    style               style cycle object.
    clear=True          if no axes are specified, clear the figure, otherwise
                        clear just the axes.
    axes=None           which axes to use, or "gca" for the current axes
    xscale,yscale       'linear' by default. Set either to 'log' for log axes
    grid=False          Should we draw a grid on the axes?
    legend='best'       where to place the legend (see pylab.legend())
                        Set this to None to ignore the legend.
    autoformat=True     Should we format the figure for printing?
    False          Should the format be tall?
    draw=True           whether or not to draw the plot after plotting
    
    **kwargs are sent to pylab.errorbar()
    """

    # make sure everything is at least iterable.
    if not _fun.is_iterable(xdata):  xdata  = [xdata]
    if not _fun.is_iterable(exdata): exdata = [exdata]
    if not _fun.is_iterable(ydata):  ydata  = [ydata]
    if not _fun.is_iterable(eydata): eydata = [eydata]
    
    # make sure at least xdata and ydata are 2-D
    if _fun.is_a_number(xdata[0]): xdata = [xdata]
    if _fun.is_a_number(ydata[0]): ydata = [ydata]

    # make sure the number of data sets agrees
    N = max(len(xdata),len(ydata))
    for n in range(N-len( xdata)):  xdata.append( xdata[0])
    for n in range(N-len( ydata)):  ydata.append( ydata[0])
    for n in range(N-len(exdata)): exdata.append(exdata[0])
    for n in range(N-len(eydata)): eydata.append(eydata[0])
    
    # loop over each x and y data set, making sure None's are all converted
    # to counting arrays
    for n in range(N):
        
        # clean up the [None]'s
        if _fun.is_iterable(xdata[n]) and xdata[n][0] == None: xdata[n] = None
        if _fun.is_iterable(ydata[n]) and ydata[n][0] == None: ydata[n] = None

        if xdata[n] == None and ydata[n] == None: 
            print "ERROR: "+str(n)+"'th data set is (None, None)."
            return 
            
        if xdata[n] == None: xdata[n] = _n.arange(len(ydata[n]))
        if ydata[n] == None: ydata[n] = _n.arange(len(xdata[n]))
    
    # check that the labels is a list of strings of the same length
    if not _fun.is_iterable(label): label = [label]    
    if len(label) < len(ydata):
        for n in range(len(ydata)-1): label.append(label[0])

    

    # clear the figure?
    if clear and not axes: _pylab.gcf().clear()

    # setup axes
    if axes=="gca" or axes==None: axes = _pylab.gca()
    
    # if we're clearing the axes
    if clear: axes.clear()

    # set the current axes    
    _pylab.axes(axes)

    # now loop over the list of data in xdata and ydata
    for n in range(0,len(xdata)):
        # get the label
        if label: l = str(label[n])
        else:     l = str(n)

        # calculate the x an y progressive shifts
        dx = xshift*(n/xshift_every)
        dy = yshift*(n/yshift_every)

        # if we're supposed to coarsen the data, do so.
        x = _s.fun.coarsen_array(xdata[n], coarsen)
        y = _s.fun.coarsen_array(ydata[n], coarsen)
        ey = _s.fun.coarsen_array(eydata[n], coarsen)
        ex = _s.fun.coarsen_array(exdata[n], coarsen)
        
        # update the style
        if not style==None: kwargs.update(style.next())
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
        if pyshell_history:
            title = 'Plot created ' + _time.asctime() + '\n' + title
            for n in range(pyshell_history): 
                if not title == '': title = _pt.get_pyshell_command(n) + "\n" + title
                else:               title = _pt.get_pyshell_command(n)
        axes.set_title(title)
    
    if grid: _pylab.grid(True)

    if autoformat: _pt.format_figure(tall=tall, draw=False)

    # update the canvas
    if draw: _pylab.draw()
    
    return axes

def xy_databoxes(ds, xscript=0, yscript=1, eyscript=None, exscript=None, **kwargs):
    """
    Use script to generate data and plot it.   
    
    ds        list of databoxes
    xscript   script for x data (xscript = None for counting script)
    yscript   script for y data (yscript = None for counting script)
    eyscript  script for y error
    exscript  script for x error
    
    **kwargs are sent to spinmob.plot.xy.data()    
    """
    return databoxes(ds, xscript, yscript, eyscript, exscript, plotter=xy_data, **kwargs)
    

def xy_files(xscript=0, yscript=1, eyscript=None, exscript=None, **kwargs):
    """
    This will load a bunch of data files, generate data based on the supplied
    scripts, and then plot this data. 
    
    xscript, yscript, eyscript, exscript    scripts to generate x, y, and errors
    
    **kwargs are sent to spinmob.plot.xy.databoxes()
    """
    return files(xscript, yscript, eyscript, exscript, plotter=xy_databoxes, **kwargs)

def xy_function(f='sin(x)', xmin=-1, xmax=1, steps=200, p='x', g=None, erange=False, **kwargs):
    """

    Plots the function over the specified range

    f                   function or list of functions to plot; can be string functions
    xmin, xmax, steps   range over which to plot, and how many points to plot
    p                   if using strings for functions, p is the parameter name
    g                   optional dictionary of extra globals. Try g=globals()!
    erange              Use exponential spacing of the x data?

    **kwargs are sent to spinmob.plot.xy.data()

    """

    return function(f, xmin, xmax, steps, p, g, erange, plotter=xy_data, **kwargs)






def databoxes(ds, xscript=0, yscript=1, eyscript=None, exscript=None, plotter=xy_data, **kwargs):
    """
    Use script to generate data and send to harrisgroup.plot.complex_data()    
    
    ds        list of databoxes
    xscript   script for x data
    yscript   script for y data
    eyscript  script for y error
    exscript  script for x error
    plotter   function used to do the plotting
    
    **kwargs are sent to plotter()    
    """
    if not _fun.is_iterable(ds): ds = [ds]  
    
    if not kwargs.has_key('xlabel'): kwargs['xlabel'] = str(xscript)
    if not kwargs.has_key('ylabel'): kwargs['ylabel'] = str(yscript)
    
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
        if xscript[n] == None and yscript[n] == None: 
            print "Two None scripts? But why?"
            return
        if xscript[n] == None: 
            if type(yscript[n])==str: xscript[n] = 'range(len('+yscript[n]+'))'
            else:                     xscript[n] = 'range(len(c('+str(yscript[n])+')))'               
        if yscript[n] == None: 
            if type(xscript[n])==str: yscript[n] = 'range(len('+xscript[n]+'))'
            else:                     yscript[n] = 'range(len(c('+str(xscript[n])+')))'
        
    xdatas  = []
    ydatas  = []
    exdatas = []
    eydatas = []
    labels  = []
    
    for d in ds: 
        
        xdata = d(xscript)
        for n in range(len(xdata)):  
            xdatas.append(xdata[n])
            if len(xdata)>1: labels.append(str(n)+": "+_os.path.split(d.path)[-1])
            else:            labels.append(_os.path.split(d.path)[-1])
        
        for y in d(yscript):  ydatas.append(y)
        for x in d(exscript): exdatas.append(x)
        for y in d(eyscript): eydatas.append(y)
    
    # allow for custom labels
    if kwargs.has_key('label'): labels = kwargs.pop('label')
    return plotter(xdatas, ydatas, eydatas, exdatas, label=labels, **kwargs)

def files(xscript=0, yscript=1, eyscript=None, exscript=None, plotter=xy_databoxes, paths='ask', **kwargs): 
    """
    This will load a bunch of data files, generate data based on the supplied
    scripts, and then plot this data using the specified databox plotter. 
    
    xscript, yscript, eyscript, exscript    scripts to generate x, y, and errors

    **kwargs are sent to plotter()    
    """
    if kwargs.has_key('delimiter'): delimiter = kwargs.pop('delimiter')
    else:                           delimiter = None    
    
    ds = _s.data.load_multiple(paths=paths, delimiter = delimiter)
    if ds==None or len(ds) == 0: return
    
    # generate a default title (the directory)
    if not kwargs.has_key('title'): kwargs['title']=_os.path.split(ds[0].path)[0]

    # run the databox plotter
    return plotter(ds, xscript=xscript, yscript=yscript, eyscript=eyscript, exscript=exscript, **kwargs)

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
    for k in globals().keys():
        if not g.has_key(k): g[k] = globals()[k]

    # if the x-axis is a log scale, use erange
    if erange: x = _fun.erange(xmin, xmax, steps)
    else:      x = _numpy.linspace(xmin, xmax, steps)

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

    if not kwargs.has_key('xlabel'): kwargs['xlabel'] = p
    if not kwargs.has_key('label'):  kwargs['label']  = labels

    # plot!
    if complex_plane:    return plotter(real(ydatas),imag(ydatas), **kwargs)
    else:                return plotter(xdatas, ydatas, **kwargs)




def image_data(Z, X=[0,1.0], Y=[0,1.0], aspect=1.0, zmin=None, zmax=None, clear=1, **kwargs):
    """
    Generates an image or 3d plot

    X                       1-d array of x-values
    Y                       1-d array of y-values
    Z                       2-d array of z-values

    X and Y can be something like [0,2] or an array of X-values
    """

    fig = _pylab.gcf()
    if clear: 
        fig.clear()
        _pylab.axes()

    # generate the 3d axes
    X = _numpy.array(X)
    Y = _numpy.array(Y)
    Z = _numpy.array(Z)

    # assume X and Y are the bin centers and figure out the bin widths
    x_width = abs(float(X[-1] - X[0])/(len(Z[0])-1))
    y_width = abs(float(Y[-1] - Y[0])/(len(Z)-1))
    
    # reverse the Z's
    Z = Z[-1::-1]
    
    # get rid of the label and title kwargs
    xlabel=''
    ylabel=''
    title =''
    if kwargs.has_key('xlabel'): xlabel = kwargs.pop('xlabel')
    if kwargs.has_key('ylabel'): ylabel = kwargs.pop('ylabel')
    if kwargs.has_key('title'):  title  = kwargs.pop('title')
    
    _pylab.imshow(Z, extent=[X[0]-x_width/2.0, X[-1]+x_width/2.0,
                             Y[0]-y_width/2.0, Y[-1]+y_width/2.0], **kwargs)    
    _pylab.colorbar()
    _pt.image_set_clim(zmin,zmax)
    _pt.image_set_aspect(aspect)
    
    a = _pylab.gca()
    a.set_title(title)
    a.set_xlabel(xlabel)
    a.set_ylabel(ylabel)
    
    _pt.close_sliders()
    _pt.image_sliders()

    _pt.raise_figure_window()
    _pt.raise_pyshell()
    _pylab.draw()
    
    return _pylab.gca()



def image_function(f='sin(x)*cos(y)', xmin=-1, xmax=1, ymin=-1, ymax=1, xsteps=100, ysteps=100, p="x,y", g=None, **kwargs):
    """
    Plots a 2-d function over the specified range

    f                       takes two inputs and returns one value. Can also
                            be a string function such as sin(x*y)
    xmin,xmax,ymin,ymax     range over which to generate/plot the data
    xsteps,ysteps           how many points to plot on the specified range
    p                       if using strings for functions, this is a string of parameters.
    g                       Optional additional globals. Try g=globals()!
    """

    # aggregate globals
    if not g: g = {}
    for k in globals().keys():
        if not g.has_key(k): g[k] = globals()[k]

    if type(f) == str:
        f = eval('lambda ' + p + ': ' + f, g)


    # generate the grid x and y coordinates
    xones = _numpy.linspace(1,1,ysteps)
    x     = _numpy.linspace(xmin, xmax, xsteps)
    xgrid = _numpy.outer(xones, x)

    yones = _numpy.linspace(1,1,xsteps)
    y     = _numpy.linspace(ymin, ymax, ysteps)
    ygrid = _numpy.outer(y, yones)

    # now get the z-grid
    try:
        # try it the fast numpy way. Add 0 to assure dimensions
        zgrid = f(xgrid, ygrid) + xgrid*0.0
    except:
        print "Notice: function is not rocking hardcore. Generating grid the slow way..."
        # manually loop over the data to generate the z-grid
        zgrid = []
        for ny in range(0, len(y)):
            zgrid.append([])
            for nx in range(0, len(x)):
                zgrid[ny].append(f(x[nx], y[ny]))

        zgrid = _numpy.array(zgrid)

    # now plot!
    return image_data(zgrid, x, y, **kwargs)






def parametric_function(fx='sin(t)', fy='cos(t)', tmin=-1, tmax=1, steps=200, p='t', g=None, erange=False, **kwargs):
    """

    Plots the parametric function over the specified range

    fx, fy              function or list of functions to plot; can be string functions
    xmin, xmax, steps   range over which to plot, and how many points to plot
    p                   if using strings for functions, p is the parameter name
    g                   optional dictionary of extra globals. Try g=globals()!
    erange              Use exponential spacing of the t data?

    **kwargs are sent to spinmob.plot.xy.data()

    """

    if not g: g = {}
    for k in globals().keys():
        if not g.has_key(k): g[k] = globals()[k]

    # if the x-axis is a log scale, use erange
    if erange: r = _fun.erange(tmin, tmax, steps)
    else:      r = _numpy.linspace(tmin, tmax, steps)

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
    return xy_data(xdatas, ydatas, label=labels, **kwargs)



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

    def next(self):
        """
        Returns the next dictionary of styles to send to plot as kwargs.
        For example:

        pylab.plot([1,2,3],[1,2,1], **style.next())
        """
        s = {}
        for key   in self.iterators.keys():
            s[key] = self.iterators[key].next()
        return s

    def reset(self):
        """
        Resets the style cycle.
        """
        for key in self.keys(): self.iterators[key] = _itertools.cycle(self[key])
        return self

