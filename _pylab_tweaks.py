import sys               as _sys
import os                as _os
import pylab             as _pylab
import time              as _time
import matplotlib        as _mpl
import numpy             as _n

try:
    from . import _functions        as _fun
    from . import _pylab_colormap
except:
    import _functions as _fun
    import _pylab_colormap

import spinmob           as _s

# Python 3 or 2?
if _sys.version_info[0] >= 3: import _thread as _thread
else:                         import  thread as _thread 

image_colormap = _pylab_colormap.colormap_interface

from matplotlib.font_manager import FontProperties as _FontProperties

if __name__ == '__main__':
    from . import _settings
    _settings = _settings.settings()


line_attributes = ["linestyle","linewidth","color","marker","markersize","markerfacecolor","markeredgewidth","markeredgecolor"]
image_undo_list = []




def add_text(text, x=0.01, y=0.01, axes="gca", draw=True, **kwargs):
    """
    Adds text to the axes at the specified position.

    **kwargs go to the axes.text() function.
    """
    if axes=="gca": axes = _pylab.gca()
    axes.text(x, y, text, transform=axes.transAxes, **kwargs)
    if draw: _pylab.draw()

def auto_zoom(zoomx=True, zoomy=True, axes="gca", x_space=0.04, y_space=0.04, draw=True):
    """
    Looks at the bounds of the plotted data and zooms accordingly, leaving some
    space around the data.
    """

    # Disable auto-updating by default.
    _pylab.ioff()

    if axes=="gca": axes = _pylab.gca()

    # get the current bounds
    x10, x20 = axes.get_xlim()
    y10, y20 = axes.get_ylim()

    # Autoscale using pylab's technique (catches the error bars!)
    axes.autoscale(enable=True, tight=True)

    # Add padding
    if axes.get_xscale() == 'linear':
        x1, x2 = axes.get_xlim()
        xc = 0.5*(x1+x2)
        xs = 0.5*(1+x_space)*(x2-x1)
        axes.set_xlim(xc-xs, xc+xs)
    
    if axes.get_yscale() == 'linear':
        y1, y2 = axes.get_ylim()
        yc = 0.5*(y1+y2)
        ys = 0.5*(1+y_space)*(y2-y1)
        axes.set_ylim(yc-ys, yc+ys)
    
    # If we weren't supposed to zoom x or y, reset them
    if not zoomx: axes.set_xlim(x10, x20)
    if not zoomy: axes.set_ylim(y10, y20)
    
    if draw: 
        _pylab.ion()
        _pylab.draw()

##    # get all the lines
##    lines = a.get_lines()
##
##    # get the current limits, in case we're not zooming one of the axes.
##    x1, x2 = a.get_xlim()
##    y1, y2 = a.get_ylim()
##
##    xdata = []
##    ydata = []
##    for n in range(0,len(lines)):
##        # store this line's data
##
##        # build up a huge data array
##        if isinstance(lines[n], _mpl.lines.Line2D):
##            x, y = lines[n].get_data()
##
##            for n in range(len(x)):
##                # if we're not zooming x and we're in range, append
##                if not zoomx and x[n] >= x1 and x[n] <= x2:
##                    xdata.append(x[n])
##                    ydata.append(y[n])
##
##                elif not zoomy and y[n] >= y1 and y[n] <= y2:
##                    xdata.append(x[n])
##                    ydata.append(y[n])
##
##                elif zoomy and zoomx:
##                    xdata.append(x[n])
##                    ydata.append(y[n])
##
##    if len(xdata):
##        xmin = min(xdata)
##        xmax = max(xdata)
##        ymin = min(ydata)
##        ymax = max(ydata)
##
##        # we want a 3% white space boundary surrounding the data in our plot
##        # so set the range accordingly
##        if zoomx: a.set_xlim(xmin-x_space*(xmax-xmin), xmax+x_space*(xmax-xmin))
##        if zoomy: a.set_ylim(ymin-y_space*(ymax-ymin), ymax+y_space*(ymax-ymin))
##
##        if draw:
##            _pylab.ion()
##            _pylab.draw()
#
#    else:
#        return

def click_estimate_slope():
    """
    Takes two clicks and returns the slope.

    Right-click aborts.
    """

    c1 = _pylab.ginput()
    if len(c1)==0:
        return None

    c2 = _pylab.ginput()
    if len(c2)==0:
        return None

    return (c1[0][1]-c2[0][1])/(c1[0][0]-c2[0][0])

def click_estimate_curvature():
    """
    Takes two clicks and returns the curvature, assuming the first click
    was the minimum of a parabola and the second was some other point.

    Returns the second derivative of the function giving this parabola.

    Right-click aborts.
    """

    c1 = _pylab.ginput()
    if len(c1)==0:
        return None

    c2 = _pylab.ginput()
    if len(c2)==0:
        return None

    return 2*(c2[0][1]-c1[0][1])/(c2[0][0]-c1[0][0])**2

def click_estimate_difference():
    """
    Takes two clicks and returns the difference vector [dx, dy].

    Right-click aborts.
    """

    c1 = _pylab.ginput()
    if len(c1)==0:
        return None

    c2 = _pylab.ginput()
    if len(c2)==0:
        return None

    return [c2[0][0]-c1[0][0], c2[0][1]-c1[0][1]]


def copy_figure_to_clipboard(figure='gcf'):
    """
    Copies the specified figure to the system clipboard. Specifying 'gcf'
    will use the current figure.
    """    
    try:
        import pyqtgraph as _p
    
        # Get the current figure if necessary        
        if figure is 'gcf': figure = _s.pylab.gcf() 
        
        # Store the figure as an image
        path = _os.path.join(_s.settings.path_home, "clipboard.png")
        figure.savefig(path)
        
        # Set the clipboard. I know, it's weird to use pyqtgraph, but 
        # This covers both Qt4 and Qt5 with their Qt4 wrapper!
        _p.QtGui.QApplication.instance().clipboard().setImage(_p.QtGui.QImage(path))
        
    except:         
        print("This function currently requires pyqtgraph to be installed.")

def differentiate_shown_data(neighbors=1, fyname=1, **kwargs):
    """
    Differentiates the data visible on the specified axes using
    fun.derivative_fit() (if neighbors > 0), and derivative() otherwise.
    Modifies the visible data using manipulate_shown_data(**kwargs)
    """

    if neighbors:
        def D(x,y): return _fun.derivative_fit(x,y,neighbors)
    else:
        def D(x,y): return _fun.derivative(x,y)

    if fyname==1: fyname = '$\\partial_{x(\\pm'+str(neighbors)+')}$'

    manipulate_shown_data(D, fxname=None, fyname=fyname, **kwargs)

def fit_shown_data(f="a*x+b", p="a=1, b=2", axes="gca", verbose=True, **kwargs):
    """
    Fast-and-loos quick fit:

    Loops over each line of the supplied axes and fits with the supplied
    function (f) and parameters (p). Assumes uniform error and scales this
    such that the reduced chi^2 is 1.

    Returns a list of fitter objects

    **kwargs are sent to _s.data.fitter()
    """

    # get the axes
    if axes=="gca": axes = _pylab.gca()

    # get the range for trimming
    _pylab.sca(axes)
    xmin,xmax = axes.get_xlim()
    ymin,ymax = axes.get_ylim()

    # update the kwargs
    if 'first_figure' not in kwargs: kwargs['first_figure'] = axes.figure.number+1

    # loop over the lines
    fitters = []
    for l in axes.lines:

        # get the trimmed data
        x,y = l.get_data()
        x,y = _s.fun.trim_data_uber([x,y],[xmin<x,x<xmax,ymin<y,y<ymax])

        # create a fitter
        fitters.append(_s.data.fitter(**kwargs).set_functions(f=f, p=p))
        fitters[-1].set_data(x,y)
        fitters[-1].fit()
        fitters[-1].autoscale_eydata().fit()
        if verbose:
            print(fitters[-1])
            print("<click the graph to continue>")
        if not axes.lines[-1] == l: fitters[-1].ginput(timeout=0)

    return fitters

def format_figure(figure=None, tall=False, draw=True, modify_geometry=True):
    """
    This formats the figure in a compact way with (hopefully) enough useful
    information for printing large data sets. Used mostly for line and scatter
    plots with long, information-filled titles.

    Chances are somewhat slim this will be ideal for you but it very well might
    and is at least a good starting point.

    figure=None     specify a figure object. None will use gcf()

    """
    _pylab.ioff()

    if figure == None: figure = _pylab.gcf()

    if modify_geometry:
        if tall: set_figure_window_geometry(figure, (0,0), (550,700))
        else:    set_figure_window_geometry(figure, (0,0), (550,400))

    legend_position=1.01

    # first, find overall bounds of all axes.
    ymin = 1.0
    ymax = 0.0
    xmin = 1.0
    xmax = 0.0
    for axes in figure.get_axes():
        (x,y,dx,dy) = axes.get_position().bounds
        if y    < ymin: ymin = y
        if y+dy > ymax: ymax = y+dy
        if x    < xmin: xmin = x
        if x+dx > xmax: xmax = x+dx

    # Fraction of the figure's width and height to use for all the plots.
    w = 0.55
    h = 0.75

    # buffers on left and bottom edges
    bb = 0.15
    bl = 0.15

    xscale = w / (xmax-xmin)
    yscale = h / (ymax-ymin)

    # save this for resetting
    current_axes = _pylab.gca()

    # loop over the axes
    for axes in figure.get_axes():

        # Get the axes bounds
        (x,y,dx,dy) = axes.get_position().bounds
        y  = bb + (y-ymin)*yscale
        dy = dy * yscale

        x  = bl + (x-xmin)*xscale
        dx = dx * xscale

        axes.set_position([x,y,dx,dy])

        # set the position of the legend
        _pylab.axes(axes) # set the current axes
        if len(axes.lines)>0:
            _pylab.legend(loc=[legend_position, 0], borderpad=0.02, prop=_FontProperties(size=7))

        # set the label spacing in the legend
        if axes.get_legend():
            axes.get_legend().labelsep = 0.01
            axes.get_legend().set_visible(1)

        # set up the title label
        axes.title.set_horizontalalignment('right')
        axes.title.set_size(8)
        axes.title.set_position([1.5,1.02])
        axes.title.set_visible(1)
        #axes.yaxis.label.set_horizontalalignment('center')
        #axes.xaxis.label.set_horizontalalignment('center')

    _pylab.axes(current_axes)

    if draw:
        _pylab.ion()
        _pylab.draw()

def get_figure_window(figure='gcf'):
    """
    This will search through the windows and return the one containing the figure
    """

    if figure == 'gcf': figure = _pylab.gcf()
    return figure.canvas.GetParent()

def get_figure_window_geometry(fig='gcf'):
    """
    This will currently only work for Qt4Agg and WXAgg backends.
    Returns position, size

    postion = [x, y]
    size    = [width, height]

    fig can be 'gcf', a number, or a figure object.
    """

    if type(fig)==str:          fig = _pylab.gcf()
    elif _fun.is_a_number(fig): fig = _pylab.figure(fig)

    # Qt4Agg backend. Probably would work for other Qt stuff
    if _pylab.get_backend().find('Qt') >= 0:
        size = fig.canvas.window().size()
        pos  = fig.canvas.window().pos()
        return [[pos.x(),pos.y()], [size.width(),size.height()]]

    else:
        print("get_figure_window_geometry() only implemented for QtAgg backend.")
        return None


def image_format_figure(figure=None, draw=True):
    """
    This formats the figure in a compact way with (hopefully) enough useful
    information for printing large data sets. Used mostly for line and scatter
    plots with long, information-filled titles.

    Chances are somewhat slim this will be ideal for you but it very well might
    and is at least a good starting point.

    figure=None     specify a figure object. None will use gcf()

    """
    _pylab.ioff()

    if figure == None: figure = _pylab.gcf()

    set_figure_window_geometry(figure, (0,0), (550,470))

    axes = figure.axes[0]

    # set up the title label
    axes.title.set_horizontalalignment('right')
    axes.title.set_size(8)
    axes.title.set_position([1.27,1.02])
    axes.title.set_visible(1)

    if draw:
        _pylab.ion()
        _pylab.draw()

def impose_legend_limit(limit=30, axes="gca", **kwargs):
    """
    This will erase all but, say, 30 of the legend entries and remake the legend.
    You'll probably have to move it back into your favorite position at this point.
    """
    if axes=="gca": axes = _pylab.gca()

    # make these axes current
    _pylab.axes(axes)

    # loop over all the lines_pylab.
    for n in range(0,len(axes.lines)):
        if n >  limit-1 and not n==len(axes.lines)-1: axes.lines[n].set_label("_nolegend_")
        if n == limit-1 and not n==len(axes.lines)-1: axes.lines[n].set_label("...")

    _pylab.legend(**kwargs)


def image_autozoom(axes="gca"):

    if axes=="gca": axes = _pylab.gca()

    # get the extent
    extent = axes.images[0].get_extent()

    # rezoom us
    axes.set_xlim(extent[0],extent[1])
    axes.set_ylim(extent[2],extent[3])

    _pylab.draw()

def image_coarsen(xlevel=0, ylevel=0, image="auto", method='average'):
    """
    This will coarsen the image data by binning each xlevel+1 along the x-axis
    and each ylevel+1 points along the y-axis

    type can be 'average', 'min', or 'max'
    """
    if image == "auto": image = _pylab.gca().images[0]

    Z = _n.array(image.get_array())

    # store this image in the undo list
    global image_undo_list
    image_undo_list.append([image, Z])
    if len(image_undo_list) > 10: image_undo_list.pop(0)

    # images have transposed data
    image.set_array(_fun.coarsen_matrix(Z, ylevel, xlevel, method))

    # update the plot
    _pylab.draw()


def image_neighbor_smooth(xlevel=0.2, ylevel=0.2, image="auto"):
    """
    This will bleed nearest neighbor pixels into each other with
    the specified weight factors.
    """
    if image == "auto": image = _pylab.gca().images[0]

    Z = _n.array(image.get_array())

    # store this image in the undo list
    global image_undo_list
    image_undo_list.append([image, Z])
    if len(image_undo_list) > 10: image_undo_list.pop(0)

    # get the diagonal smoothing level (eliptical, and scaled down by distance)
    dlevel = ((xlevel**2+ylevel**2)/2.0)**(0.5)

    # don't touch the first column
    new_Z = [Z[0]*1.0]

    for m in range(1,len(Z)-1):
        new_Z.append(Z[m]*1.0)
        for n in range(1,len(Z[0])-1):
            new_Z[-1][n] = (Z[m,n] + xlevel*(Z[m+1,n]+Z[m-1,n]) + ylevel*(Z[m,n+1]+Z[m,n-1])   \
                                   + dlevel*(Z[m+1,n+1]+Z[m-1,n+1]+Z[m+1,n-1]+Z[m-1,n-1])   )  \
                                   / (1.0+xlevel*2+ylevel*2 + dlevel*4)

    # don't touch the last column
    new_Z.append(Z[-1]*1.0)

    # images have transposed data
    image.set_array(_n.array(new_Z))

    # update the plot
    _pylab.draw()

def image_undo():
    """
    Undoes the last coarsen or smooth command.
    """
    if len(image_undo_list) <= 0:
        print("no undos in memory")
        return

    [image, Z] = image_undo_list.pop(-1)
    image.set_array(Z)
    _pylab.draw()


def image_set_aspect(aspect=1.0, axes="gca"):
    """
    sets the aspect ratio of the current zoom level of the imshow image
    """
    if axes is "gca": axes = _pylab.gca()

    e = axes.get_images()[0].get_extent()
    axes.set_aspect(abs((e[1]-e[0])/(e[3]-e[2]))/aspect)

def image_set_extent(x=None, y=None, axes="gca"):
    """
    Set's the first image's extent, then redraws.

    Examples:
    x = [1,4]
    y = [33.3, 22]
    """
    if axes == "gca": axes = _pylab.gca()

    # get the current plot limits
    xlim = axes.get_xlim()
    ylim = axes.get_ylim()

    # get the old extent
    extent = axes.images[0].get_extent()

    # calculate the fractional extents
    x0     = extent[0]
    y0     = extent[2]
    xwidth = extent[1]-x0
    ywidth = extent[3]-y0
    frac_x1 = (xlim[0]-x0)/xwidth
    frac_x2 = (xlim[1]-x0)/xwidth
    frac_y1 = (ylim[0]-y0)/ywidth
    frac_y2 = (ylim[1]-y0)/ywidth


    # set the new
    if not x == None:
        extent[0] = x[0]
        extent[1] = x[1]
    if not y == None:
        extent[2] = y[0]
        extent[3] = y[1]


    # get the new zoom window
    x0     = extent[0]
    y0     = extent[2]
    xwidth = extent[1]-x0
    ywidth = extent[3]-y0

    x1 = x0 + xwidth*frac_x1
    x2 = x0 + xwidth*frac_x2
    y1 = y0 + ywidth*frac_y1
    y2 = y0 + ywidth*frac_y2

    # set the extent
    axes.images[0].set_extent(extent)

    # rezoom us
    axes.set_xlim(x1,x2)
    axes.set_ylim(y1,y2)

    # draw
    image_set_aspect(1.0)


def image_scale(xscale=1.0, yscale=1.0, axes="gca"):
    """
    Scales the image extent.
    """
    if axes == "gca": axes = _pylab.gca()

    e = axes.images[0].get_extent()
    x1 = e[0]*xscale
    x2 = e[1]*xscale
    y1 = e[2]*yscale
    y2 = e[3]*yscale

    image_set_extent([x1,x2],[y1,y2], axes)



def image_click_xshift(axes = "gca"):
    """
    Takes a starting and ending point, then shifts the image y by this amount
    """
    if axes == "gca": axes = _pylab.gca()

    try:
        p1 = _pylab.ginput()
        p2 = _pylab.ginput()

        xshift = p2[0][0]-p1[0][0]

        e = axes.images[0].get_extent()

        e[0] = e[0] + xshift
        e[1] = e[1] + xshift

        axes.images[0].set_extent(e)

        _pylab.draw()
    except:
        print("whoops")

def image_click_yshift(axes = "gca"):
    """
    Takes a starting and ending point, then shifts the image y by this amount
    """
    if axes == "gca": axes = _pylab.gca()

    try:
        p1 = _pylab.ginput()
        p2 = _pylab.ginput()

        yshift = p2[0][1]-p1[0][1]

        e = axes.images[0].get_extent()

        e[2] = e[2] + yshift
        e[3] = e[3] + yshift

        axes.images[0].set_extent(e)

        _pylab.draw()
    except:
        print("whoops")

def image_shift(xshift=0, yshift=0, axes="gca"):
    """
    This will shift an image to a new location on x and y.
    """

    if axes=="gca": axes = _pylab.gca()

    e = axes.images[0].get_extent()

    e[0] = e[0] + xshift
    e[1] = e[1] + xshift
    e[2] = e[2] + yshift
    e[3] = e[3] + yshift

    axes.images[0].set_extent(e)

    _pylab.draw()



def image_set_clim(zmin=None, zmax=None, axes="gca"):
    """
    This will set the clim (range) of the colorbar.

    Setting zmin or zmax to None will not change them.
    Setting zmin or zmax to "auto" will auto-scale them to include all the data.
    """
    if axes=="gca": axes=_pylab.gca()

    image = axes.images[0]

    if zmin=='auto': zmin = _n.min(image.get_array())
    if zmax=='auto': zmax = _n.max(image.get_array())

    if zmin==None: zmin = image.get_clim()[0]
    if zmax==None: zmax = image.get_clim()[1]

    image.set_clim(zmin, zmax)

    _pylab.draw()

def image_sliders(image="top", colormap="_last"):
    return "NO!"


def image_ubertidy(figure="gcf", aspect=1.0, fontsize=18, fontweight='bold', fontname='Arial', ylabel_pad=0.007, xlabel_pad=0.010, colorlabel_pad=0.1, borderwidth=3.0, tickwidth=2.0, window_size=(550,500)):

    if figure=="gcf": figure = _pylab.gcf()

    # do this to both axes
    for a in figure.axes:
        _pylab.axes(a)

        # remove the labels
        a.set_title("")
        a.set_xlabel("")
        a.set_ylabel("")

        # thicken the border
        # we want thick axis lines
        a.spines['top'].set_linewidth(borderwidth)
        a.spines['left'].set_linewidth(borderwidth)
        a.spines['bottom'].set_linewidth(borderwidth)
        a.spines['right'].set_linewidth(borderwidth)
        a.set_frame_on(True) # adds a thick border to the colorbar

        # these two cover the main plot
        _pylab.xticks(fontsize=fontsize, fontweight=fontweight, fontname=fontname)
        _pylab.yticks(fontsize=fontsize, fontweight=fontweight, fontname=fontname)

        # thicken the tick lines
        for l in a.get_xticklines(): l.set_markeredgewidth(tickwidth)
        for l in a.get_yticklines(): l.set_markeredgewidth(tickwidth)

    # set the aspect and window size
    _pylab.axes(figure.axes[0])
    image_set_aspect(aspect)
    get_figure_window().SetSize(window_size)

    # we want to give the labels some breathing room (1% of the data range)
    for label in _pylab.xticks()[1]: label.set_y(-xlabel_pad)
    for label in _pylab.yticks()[1]: label.set_x(-ylabel_pad)

    # need to draw to commit the changes up to this point. Annoying.
    _pylab.draw()


    # get the bounds of the first axes and come up with corresponding bounds
    # for the colorbar
    a1 = _pylab.gca()
    b  = a1.get_position()
    aspect = figure.axes[1].get_aspect()

    pos = []
    pos.append(b.x0+b.width+0.02)   # lower left x
    pos.append(b.y0)                # lower left y
    pos.append(b.height/aspect)     # width
    pos.append(b.height)            # height

    # switch to the colorbar axes
    _pylab.axes(figure.axes[1])
    _pylab.gca().set_position(pos)

    for label in _pylab.yticks()[1]: label.set_x(1+colorlabel_pad)


    # switch back to the main axes
    _pylab.axes(figure.axes[0])

    _pylab.draw()


def integrate_shown_data(scale=1, fyname=1, autozero=0, **kwargs):
    """
    Numerically integrates the data visible on the current/specified axes using
    scale*fun.integrate_data(x,y). Modifies the visible data using
    manipulate_shown_data(**kwargs)

    autozero is the number of data points used to estimate the background
    for subtraction. If autozero = 0, no background subtraction is performed.
    """

    def I(x,y):
        xout, iout = _fun.integrate_data(x, y, autozero=autozero)
        print("Total =", scale*iout[-1])
        return xout, scale*iout

    if fyname==1: fyname = "$"+str(scale)+"\\times \\int dx$"

    manipulate_shown_data(I, fxname=None, fyname=fyname, **kwargs)



def is_a_number(s):
    try: eval(s); return 1
    except:       return 0




def manipulate_shown_data(f, input_axes="gca", output_axes=None, fxname=1, fyname=1, clear=1, pause=False, **kwargs):
    """
    Loops over the visible data on the specified axes and modifies it based on
    the function f(xdata, ydata), which must return new_xdata, new_ydata

    input_axes  which axes to pull the data from
    output_axes which axes to dump the manipulated data (None for new figure)

    fxname      the name of the function on x
    fyname      the name of the function on y
                1 means "use f.__name__"
                0 or None means no change.
                otherwise specify a string

    **kwargs are sent to axes.plot
    """

    # get the axes
    if input_axes == "gca": a1 = _pylab.gca()
    else:                   a1 = input_axes



    # get the xlimits
    xmin, xmax = a1.get_xlim()

    # get the name to stick on the x and y labels
    if fxname==1: fxname = f.__name__
    if fyname==1: fyname = f.__name__

    # get the output axes
    if output_axes == None:
        _pylab.figure(a1.figure.number+1)
        a2 = _pylab.axes()
    else:
        a2 = output_axes

    if clear: a2.clear()

    # loop over the data
    for line in a1.get_lines():

        # if it's a line, do the manipulation
        if isinstance(line, _mpl.lines.Line2D):

            # get the data
            x, y = line.get_data()

            # trim the data according to the current zoom level
            x, y = _fun.trim_data(xmin, xmax, x, y)

            # do the manipulation
            new_x, new_y = f(x,y)

            # plot the new
            _s.plot.xy.data(new_x, new_y, clear=0, label=line.get_label().replace("_", "-"), axes=a2, **kwargs)

            # pause after each curve if we're supposed to
            if pause:
                _pylab.draw()
                input("<enter> ")

    # set the labels and title.
    if fxname in [0,None]:  a2.set_xlabel(a1.get_xlabel())
    else:                   a2.set_xlabel(fxname+"("+a1.get_xlabel()+")")

    if fyname in [0,None]:  a2.set_ylabel(a1.get_ylabel())
    else:                   a2.set_ylabel(fyname+"("+a1.get_ylabel()+")")

    _pylab.draw()

def manipulate_shown_xdata(fx, fxname=1, **kwargs):
    """
    This defines a function f(xdata,ydata) returning fx(xdata), ydata and
    runs manipulate_shown_data() with **kwargs sent to this. See
    manipulate_shown_data() for more info.
    """
    def f(x,y): return fx(x), y
    f.__name__ = fx.__name__
    manipulate_shown_data(f, fxname=fxname, fyname=None, **kwargs)

def manipulate_shown_ydata(fy, fyname=1, **kwargs):
    """
    This defines a function f(xdata,ydata) returning xdata, fy(ydata) and
    runs manipulate_shown_data() with **kwargs sent to this. See
    manipulate_shown_data() for more info.
    """
    def f(x,y): return x, fy(y)
    f.__name__ = fy.__name__
    manipulate_shown_data(f, fxname=None, fyname=fyname, **kwargs)

def _print_figures(figures, arguments='', file_format='pdf', target_width=8.5, target_height=11.0, target_pad=0.5):
    """
    figure printing loop designed to be launched in a separate thread.
    """

    for fig in figures:

        # get the temp path
        temp_path = _os.path.join(_settings.path_home, "temp")

        # make the temp folder
        _settings.MakeDir(temp_path)

        # output the figure to postscript
        path = _os.path.join(temp_path, "graph."+file_format)

        # get the dimensions of the figure in inches
        w=fig.get_figwidth()
        h=fig.get_figheight()

        # we're printing to 8.5 x 11, so aim for 7.5 x 10
        target_height = target_height-2*target_pad
        target_width  = target_width -2*target_pad

        # depending on the aspect we scale by the vertical or horizontal value
        if 1.0*h/w > target_height/target_width:
            # scale down according to the vertical dimension
            new_h = target_height
            new_w = w*target_height/h
        else:
            # scale down according to the hozo dimension
            new_w = target_width
            new_h = h*target_width/w

        fig.set_figwidth(new_w)
        fig.set_figheight(new_h)

        # save it
        fig.savefig(path, bbox_inches=_pylab.matplotlib.transforms.Bbox(
            [[-target_pad, new_h-target_height-target_pad],
             [target_width-target_pad, target_height-target_pad]]))

        # set it back
        fig.set_figheight(h)
        fig.set_figwidth(w)


        if not arguments == '':
            c = _settings['instaprint'] + ' ' + arguments + ' "' + path + '"'
        else:
            c = _settings['instaprint'] + ' "' + path + '"'

        print(c)
        _os.system(c)


def instaprint(figure='gcf', arguments='', threaded=False, file_format='pdf'):
    """
    Quick function that saves the specified figure as a postscript and then
    calls the command defined by spinmob.prefs['instaprint'] with this
    postscript file as the argument.

    figure='gcf'    can be 'all', a number, or a list of numbers
    """

    global _settings

    if 'instaprint' not in _settings.keys():
        print("No print command setup. Set the user variable settings['instaprint'].")
        return

    if   figure=='gcf': figure=[_pylab.gcf().number]
    elif figure=='all': figure=_pylab.get_fignums()
    if not getattr(figure,'__iter__',False): figure = [figure]

    print("figure numbers in queue:", figure)

    figures=[]
    for n in figure: figures.append(_pylab.figure(n))

    # now run the ps printing command
    if threaded:
        # store the canvas type of the last figure
        canvas_type = type(figures[-1].canvas)

        # launch the aforementioned function as a separate thread
        _thread.start_new_thread(_print_figures, (figures,arguments,file_format,))

        # wait until the thread is running
        _time.sleep(0.25)

        # wait until the canvas type has returned to normal
        t0 = _time.time()
        while not canvas_type == type(figures[-1].canvas) and _time.time()-t0 < 5.0:
            _time.sleep(0.1)
        if _time.time()-t0 >= 5.0:
            print("WARNING: Timed out waiting for canvas to return to original state!")

        # bring back the figure and command line
        _pylab.draw()

    else:
        _print_figures(figures, arguments, file_format)
        _pylab.draw()


def shift(xshift=0, yshift=0, progressive=0, axes="gca"):
    """

    This function adds an artificial offset to the lines.

    yshift          amount to shift vertically
    xshift          amount to shift horizontally
    axes="gca"      axes to do this on, "gca" means "get current axes"
    progressive=0   progressive means each line gets more offset
                    set to 0 to shift EVERYTHING

    """

    if axes=="gca": axes = _pylab.gca()

    # get the lines from the plot
    lines = axes.get_lines()

    # loop over the lines and trim the data
    for m in range(0,len(lines)):
        if isinstance(lines[m], _mpl.lines.Line2D):
            # get the actual data values
            xdata = _n.array(lines[m].get_xdata())
            ydata = _n.array(lines[m].get_ydata())

            # add the offset
            if progressive:
                xdata += m*xshift
                ydata += m*yshift
            else:
                xdata += xshift
                ydata += yshift

            # update the data for this line
            lines[m].set_data(xdata, ydata)

    # zoom to surround the data properly

    auto_zoom()

def raise_figure_window(f=0):
    """
    Raises the supplied figure number or figure window.
    """
    if _fun.is_a_number(f): f = _pylab.figure(f)
    f.canvas.manager.window.raise_()


def reverse_draw_order(axes="current"):
    """

    This function takes the graph and reverses the draw order.

    """

    if axes=="current": axes = _pylab.gca()

    # get the lines from the plot
    lines = axes.get_lines()

    # reverse the order
    lines.reverse()

    for n in range(0, len(lines)):
        if isinstance(lines[n], _mpl.lines.Line2D):
            axes.lines[n]=lines[n]

    _pylab.draw()


def scale_x(scale, axes="current"):
    """

    This function scales lines horizontally.

    """

    if axes=="current": axes = _pylab.gca()

    # get the lines from the plot
    lines = axes.get_lines()

    # loop over the lines and trim the data
    for line in lines:
        if isinstance(line, _mpl.lines.Line2D):
            line.set_xdata(_pylab.array(line.get_xdata())*scale)

    # update the title
    title = axes.title.get_text()
    title += ", x_scale="+str(scale)
    axes.title.set_text(title)

    # zoom to surround the data properly
    auto_zoom()

def scale_y(scale, axes="current", lines="all"):
    """

    This function scales lines vertically.
    You can specify a line index, such as lines=0 or lines=[1,2,4]

    """

    if axes=="current": axes = _pylab.gca()

    # get the lines from the plot
    lines = axes.get_lines()

    # loop over the lines and trim the data
    for line in lines:
        if isinstance(line, _mpl.lines.Line2D):
            line.set_ydata(_pylab.array(line.get_ydata())*scale)

    # update the title
    title = axes.title.get_text()
    if not title == "":
        title += ", y_scale="+str(scale)
        axes.title.set_text(title)


    # zoom to surround the data properly
    auto_zoom()

def scale_y_universal(average=[1,10], axes="current"):
    """

    This function scales lines vertically.

    average=[1,10]    indices of average universal point

    """

    if axes=="current": axes = _pylab.gca()

    # get the lines from the plot
    lines = axes.get_lines()

    # loop over the lines and trim the data
    for m in range(0,len(lines)):
        if isinstance(lines[m], _mpl.lines.Line2D):

            # get the actual data values
            xdata = lines[m].get_xdata()
            ydata = lines[m].get_ydata()

            # figure out the scaling factor
            s=0
            for n in range(average[0], average[1]+1): s += ydata[n]
            scale = 1.0*s/(average[1]-average[0]+1.0)

            # loop over the ydata to scale it
            for n in range(0,len(ydata)): ydata[n] = ydata[n]/scale

            # update the data for this line
            lines[m].set_data(xdata, ydata)

    # update the title
    title = axes.title.get_text()
    title += ", universal scale"
    axes.title.set_text(title)

    # zoom to surround the data properly
    auto_zoom()

def set_title(axes="current", title=""):
    if axes=="current": axes = _pylab.gca()
    axes.title.set_text(title)
    _pylab.draw()


def set_figure_window_geometry(fig='gcf', position=None, size=None):
    """
    This will currently only work for Qt4Agg and WXAgg backends.

    postion = [x, y]
    size    = [width, height]

    fig can be 'gcf', a number, or a figure object.
    """

    if type(fig)==str:          fig = _pylab.gcf()
    elif _fun.is_a_number(fig): fig = _pylab.figure(fig)

    # Qt4Agg backend. Probably would work for other Qt stuff
    if _pylab.get_backend().find('Qt') >= 0:
        w = fig.canvas.window()

        if not size == None:
            w.resize(size[0],size[1])

        if not position == None:
            w.move(position[0], position[1])

    # WXAgg backend. Probably would work for other Qt stuff.
    elif _pylab.get_backend().find('WX') >= 0:
        w = fig.canvas.Parent

        if not size == None:
            w.SetSize(size)

        if not position == None:
            w.SetPosition(position)

def set_xrange(xmin="same", xmax="same", axes="gca"):
    if axes == "gca": axes = _pylab.gca()

    xlim = axes.get_xlim()

    if xmin == "same": xmin = xlim[0]
    if xmax == "same": xmax = xlim[1]

    axes.set_xlim(xmin,xmax)
    _pylab.draw()

def set_yrange(ymin="same", ymax="same", axes="gca"):
    if axes == "gca": axes = _pylab.gca()

    ylim = axes.get_ylim()

    if ymin == "same": ymin = ylim[0]
    if ymax == "same": ymax = ylim[1]

    axes.set_ylim(ymin,ymax)
    _pylab.draw()


def set_yticks(start, step, axes="gca"):
    """
    This will generate a tick array and apply said array to the axis
    """
    if axes=="gca": axes = _pylab.gca()

    # first get one of the tick label locations
    xposition = axes.yaxis.get_ticklabels()[0].get_position()[0]

    # get the bounds
    ymin, ymax = axes.get_ylim()

    # get the starting tick
    nstart = int(_pylab.floor((ymin-start)/step))
    nstop  = int(_pylab.ceil((ymax-start)/step))
    ticks = []
    for n in range(nstart,nstop+1): ticks.append(start+n*step)

    axes.set_yticks(ticks)

    # set the x-position
    for t in axes.yaxis.get_ticklabels():
        x, y = t.get_position()
        t.set_position((xposition, y))

    _pylab.draw()

def set_xticks(start, step, axes="gca"):
    """
    This will generate a tick array and apply said array to the axis
    """
    if axes=="gca": axes = _pylab.gca()

    # first get one of the tick label locations
    yposition = axes.xaxis.get_ticklabels()[0].get_position()[1]

    # get the bounds
    xmin, xmax = axes.get_xlim()

    # get the starting tick
    nstart = int(_pylab.floor((xmin-start)/step))
    nstop  = int(_pylab.ceil((xmax-start)/step))
    ticks = []
    for n in range(nstart,nstop+1): ticks.append(start+n*step)

    axes.set_xticks(ticks)

    # set the y-position
    for t in axes.xaxis.get_ticklabels():
        x, y = t.get_position()
        t.set_position((x, yposition))

    _pylab.draw()


def invert(axes="current"):
    """

    inverts the plot

    """
    if axes=="current": axes = _pylab.gca()
    scale_y(-1,axes)

def set_markers(marker="o", axes="current"):
    if axes == "current": axes = _pylab.gca()
    set_all_line_attributes("marker", marker, axes)

def set_all_line_attributes(attribute="lw", value=2, axes="current", refresh=True):
    """

    This function sets all the specified line attributes.

    """

    if axes=="current": axes = _pylab.gca()

    # get the lines from the plot
    lines = axes.get_lines()

    # loop over the lines and trim the data
    for line in lines:
        if isinstance(line, _mpl.lines.Line2D):
            _pylab.setp(line, attribute, value)

    # update the plot
    if refresh: _pylab.draw()

def set_line_attribute(line=-1, attribute="lw", value=2, axes="current", refresh=True):
    """

    This function sets all the specified line attributes.

    """

    if axes=="current": axes = _pylab.gca()

    # get the lines from the plot
    line = axes.get_lines()[-1]
    _pylab.setp(line, attribute, value)

    # update the plot
    if refresh: _pylab.draw()

def smooth_line(line, smoothing=1, trim=True, draw=True):
    """

    This takes a line instance and smooths its data with nearest neighbor averaging.

    """

    # get the actual data values
    xdata = list(line.get_xdata())
    ydata = list(line.get_ydata())

    _fun.smooth_array(ydata, smoothing)

    if trim:
        for n in range(0, smoothing):
            xdata.pop(0); xdata.pop(-1)
            ydata.pop(0); ydata.pop(-1)

    # don't do anything if we don't have any data left
    if len(ydata) == 0:
        print("There's nothing left in "+str(line)+"!")
    else:
        # otherwise set the data with the new arrays
        line.set_data(xdata, ydata)

    # we refresh in real time for giggles
    if draw: _pylab.draw()


def coarsen_line(line, level=2, exponential=False, draw=True):
    """
    Coarsens the specified line (see spinmob.coarsen_data() for more information).
    
    Parameters
    ----------
    line
        Matplotlib line instance.
    level=2
        How strongly to coarsen.
    exponential=False
        If True, use the exponential method (great for log-x plots).
    draw=True
        Redraw when complete.
    """

    # get the actual data values
    xdata = line.get_xdata()
    ydata = line.get_ydata()

    xdata,ydata = _fun.coarsen_data(xdata, ydata, level=level, exponential=exponential)
    
    # don't do anything if we don't have any data left
    if len(ydata) == 0: print("There's nothing left in "+str(line)+"!")

    # otherwise set the data with the new arrays
    else: line.set_data(xdata, ydata)

    # we refresh in real time for giggles
    if draw: _pylab.draw()

def smooth_selected_trace(trim=True, axes="gca"):
    """

    This cycles through all the lines in a set of axes, highlighting them,
    and asking for how much you want to smooth by (0 or <enter> is valid)

    """

    if axes=="gca": axes = _pylab.gca()

    # get all the lines
    lines = axes.get_lines()

    for line in lines:

        if isinstance(line, _mpl.lines.Line2D):
            # first highlight it
            fatten_line(line)

            # get the smoothing factor
            ready = 0
            while not ready:
                response = input("Smoothing Factor (<enter> to skip): ")
                try:
                    int(response)
                    ready=1
                except:
                    if response=="\n": ready = 1
                    else:              print("No!")

            if not response == "\n":
                smooth_line(line, int(response), trim)

            # return the line to normal
            unfatten_line(line)

def smooth_all_traces(smoothing=1, trim=True, axes="gca"):
    """

    This function does nearest-neighbor smoothing of the data

    """
    if axes=="gca": axes=_pylab.gca()

    # get the lines from the plot
    lines = axes.get_lines()

    # loop over the lines and trim the data
    for line in lines:
        if isinstance(line, _mpl.lines.Line2D):
            smooth_line(line, smoothing, trim, draw=False)
    _pylab.draw()

def coarsen_all_traces(level=2, exponential=False, axes="all", figure=None):
    """
    This function does nearest-neighbor coarsening of the data. See 
    spinmob.fun.coarsen_data for more information.
    
    Parameters
    ----------
    level=2
        How strongly to coarsen.
    exponential=False
        If True, use the exponential method (great for log-x plots).
    axes="all"
        Which axes to coarsen.
    figure=None
        Which figure to use.
    
    """
    if axes=="gca": axes=_pylab.gca()
    if axes=="all":
        if not figure: f = _pylab.gcf()
        axes = f.axes

    if not _fun.is_iterable(axes): axes = [axes]

    for a in axes:
        # get the lines from the plot
        lines = a.get_lines()

        # loop over the lines and trim the data
        for line in lines:
            if isinstance(line, _mpl.lines.Line2D):
                coarsen_line(line, level, exponential, draw=False)
    _pylab.draw()

def line_math(fx=None, fy=None, axes='gca'):
    """
    applies function fx to all xdata and fy to all ydata.
    """

    if axes=='gca': axes = _pylab.gca()

    lines = axes.get_lines()

    for line in lines:
        if isinstance(line, _mpl.lines.Line2D):
            xdata, ydata = line.get_data()
            if not fx==None: xdata = fx(xdata)
            if not fy==None: ydata = fy(ydata)
            line.set_data(xdata,ydata)

    _pylab.draw()

def trim(xmin="auto", xmax="auto", ymin="auto", ymax="auto", axes="current"):
    """

    This function just removes all data from the plots that
    is outside of the [xmin,xmax,ymin,ymax] range.

    "auto" means "determine from the current axes's range"

    """

    if axes=="current": axes = _pylab.gca()

    # if trim_visible is true, use the current plot's limits
    if xmin=="auto": (xmin, dummy) = axes.get_xlim()
    if xmax=="auto": (dummy, xmax) = axes.get_xlim()
    if ymin=="auto": (ymin, dummy) = axes.get_ylim()
    if ymax=="auto": (dummy, ymax) = axes.get_ylim()


    # get the lines from the plot
    lines = axes.get_lines()

    # loop over the lines and trim the data
    for line in lines:
        # get the actual data values
        old_xdata = line.get_xdata()
        old_ydata = line.get_ydata()

        # loop over the xdata and trim if it's outside the range
        new_xdata = []
        new_ydata = []
        for n in range(0, len(old_xdata)):
            # if it's in the data range
            if  old_xdata[n] >= xmin and old_xdata[n] <= xmax \
            and old_ydata[n] >= ymin and old_ydata[n] <= ymax:
                # append it to the new x and y data set
                new_xdata.append(old_xdata[n])
                new_ydata.append(old_ydata[n])

        # don't do anything if we don't have any data left
        if len(new_xdata) == 0:
            print("There's nothing left in "+str(line)+"!")
        else:
            # otherwise set the data with the new arrays
            line.set_data(new_xdata, new_ydata)


    # loop over the collections, where the vertical parts of the error bars are stored
    for c in axes.collections:

        # loop over the paths and pop them if they're bad
        for n in range(len(c._paths)-1,-1,-1):

            # loop over the vertices
            naughty = False
            for v in c._paths[n].vertices:
                # if the path contains any vertices outside the trim box, kill it!
                if v[0] < xmin or v[0] > xmax or v[1] < ymin or v[1] > ymax:
                    naughty=True

            # BOOM
            if naughty: c._paths.pop(n)

    # zoom to surround the data properly
    auto_zoom()

def xscale(scale='log'):
    _pylab.xscale(scale)
    _pylab.draw()

def yscale(scale='log'):
    _pylab.yscale(scale)
    _pylab.draw()

def ubertidy(figure="gcf", zoom=True, width=None, height=None, font_name='Arial', font_size=12, font_weight='normal',
             border_width=1.2, tick_width=1, ticks_point="in", xlabel_pad=0.010, ylabel_pad=0.005, window_size=[550,400],
             keep_axis_labels=False, axis_label_font_size=14, axis_label_font_weight='normal', keep_legend=True):
    """

    This guy performs the ubertidy, which some of us use to prep a figure
    for talks or papers.

    figure="gcf"                    Which figure to tidy.
    zoom=True                       Whether to auto-zoom on the data
    width=None                      Width of the axes (relative to window)
    height=None                     Height of the axes (relative to window)
    font_name='Arial'               Must be installed on system
    font_size=12                    Font size for all but axis labels
    font_weight='normal'            Could be 'bold'
    border_width=1.2                Thickness of the axes border
    tick_width=1                    Thickness of ticks
    ticks_point="in"                Whether ticks point "in" or "out" of axis
    xtick_label_pad=0.010           Padding on x-tick labels
    ytick_label_pad=0.008           Padding on y-tick labels
    window_size=[550,400]           Size of window in pixels
    keep_axis_labels=False          Whether to keep the axis labels
    axis_label_font_size=14         Font size for axis labels
    axis_label_font_weight='normal' Could be 'bold'
    keep_legend=False               Whether to keep the legend

    """

    if figure=="gcf": f = _pylab.gcf()
    else:             f = figure

    # set the window to a standard size
    set_figure_window_geometry(fig=f, size=window_size)

    for n in range(len(f.axes)):

        # get the axes
        a = f.axes[n]

        # set the current axes
        _pylab.axes(a)

        # we want thick axis lines
        a.spines['top']     .set_linewidth(border_width)
        a.spines['left']    .set_linewidth(border_width)
        a.spines['bottom']  .set_linewidth(border_width)
        a.spines['right']   .set_linewidth(border_width)

        # get the tick lines in one big list
        xticklines = a.get_xticklines()
        yticklines = a.get_yticklines()

        # set their marker edge width
        _pylab.setp(xticklines+yticklines, mew=tick_width)

        # set what kind of tickline they are (outside axes)
        if ticks_point=="out":
            for n in range(len(xticklines)):
                if not n%2: xticklines[n].set_marker(_mpl.lines.TICKDOWN)
                else:       xticklines[n].set_marker(_mpl.lines.TICKUP)
            for n in range(len(yticklines)):
                if not n%2: yticklines[n].set_marker(_mpl.lines.TICKLEFT)
                else:       yticklines[n].set_marker(_mpl.lines.TICKRIGHT)
        else:
            for n in range(len(xticklines)):
                if n%2: xticklines[n].set_marker(_mpl.lines.TICKDOWN)
                else:   xticklines[n].set_marker(_mpl.lines.TICKUP)
            for n in range(len(yticklines)):
                if n%2: yticklines[n].set_marker(_mpl.lines.TICKLEFT)
                else:   yticklines[n].set_marker(_mpl.lines.TICKRIGHT)


        # we want bold fonts
        _pylab.xticks(fontsize=font_size, fontweight=font_weight, fontname=font_name)
        _pylab.yticks(fontsize=font_size, fontweight=font_weight, fontname=font_name)

        # we want to give the labels some breathing room (1% of the data range)
        for label in _pylab.xticks()[1]: label.set_y(-xlabel_pad)
        for label in _pylab.yticks()[1]: label.set_x(-ylabel_pad)

        # get rid of tick label offsets
        #a.ticklabel_format(style='plain')

        # set the position/size of the axis in the window
        p = a.get_position().bounds
        if width:  a.set_position([0.15,p[1],0.15+width*0.5,p[3]])
        p = a.get_position().bounds
        if height: a.set_position([p[0],0.17,p[2],0.17+height*0.5])

        # set the axis labels to empty (so we can add them with a drawing program)
        a.set_title('')
        if not keep_axis_labels:
            a.set_xlabel('')
            a.set_ylabel('')
        else:
            _pylab.xlabel(a.get_xlabel(), fontsize=axis_label_font_size, fontweight=axis_label_font_weight, fontname=font_name)
            _pylab.ylabel(a.get_ylabel(), fontsize=axis_label_font_size, fontweight=axis_label_font_weight, fontname=font_name)

        # kill the legend
        if not keep_legend: a.legend_ = None

        # zoom!
        if zoom: auto_zoom(axes=a)

def make_inset(figure="current", width=1, height=1):
    """

    This guy makes the figure thick and small, like an inset.
    Currently assumes there is only one set of axes in the window!

    """

    # get the current figure if we're not supplied with one
    if figure == "current": figure = _pylab.gcf()

    # get the window
    w = figure.canvas.GetParent()

    # first set the size of the window
    w.SetSize([220,300])

    # we want thick axis lines
    figure.axes[0].get_frame().set_linewidth(3.0)

    # get the tick lines in one big list
    xticklines = figure.axes[0].get_xticklines()
    yticklines = figure.axes[0].get_yticklines()

    # set their marker edge width
    _pylab.setp(xticklines+yticklines, mew=2.0)

    # set what kind of tickline they are (outside axes)
    for l in xticklines: l.set_marker(_mpl.lines.TICKDOWN)
    for l in yticklines: l.set_marker(_mpl.lines.TICKLEFT)

    # get rid of the top and right ticks
    figure.axes[0].xaxis.tick_bottom()
    figure.axes[0].yaxis.tick_left()

    # we want bold fonts
    _pylab.xticks(fontsize=20, fontweight='bold', fontname='Arial')
    _pylab.yticks(fontsize=20, fontweight='bold', fontname='Arial')

    # we want to give the labels some breathing room (1% of the data range)
    figure.axes[0].xaxis.set_ticklabels([])
    figure.axes[0].yaxis.set_ticklabels([])


    # set the position/size of the axis in the window
    figure.axes[0].set_position([0.1,0.1,0.1+0.7*width,0.1+0.7*height])

    # set the axis labels to empty (so we can add them with a drawing program)
    figure.axes[0].set_title('')
    figure.axes[0].set_xlabel('')
    figure.axes[0].set_ylabel('')

    # set the position of the legend far away
    figure.axes[0].legend=None

    # zoom!
    auto_zoom(figure.axes[0], 0.07, 0.07)


def export_figure(dpi=200, figure="gcf", path=None):
    """
    Saves the actual postscript data for the figure.
    """
    if figure=="gcf": figure = _pylab.gcf()

    if path==None: path = _s.dialogs.Save("*.*", default_directory="save_plot_default_directory")

    if path=="":
        print("aborted.")
        return

    figure.savefig(path, dpi=dpi)

def save_plot(axes="gca", path=None):
    """
    Saves the figure in my own ascii format
    """

    global line_attributes

    # choose a path to save to
    if path==None: path = _s.dialogs.Save("*.plot", default_directory="save_plot_default_directory")

    if path=="":
        print("aborted.")
        return

    if not path.split(".")[-1] == "plot": path = path+".plot"

    f = file(path, "w")

    # if no argument was given, get the current axes
    if axes=="gca": axes=_pylab.gca()

    # now loop over the available lines
    f.write("title="  +axes.title.get_text().replace('\n', '\\n')+'\n')
    f.write("xlabel="+axes.xaxis.label.get_text().replace('\n','\\n')+'\n')
    f.write("ylabel="+axes.yaxis.label.get_text().replace('\n','\\n')+'\n')

    for l in axes.lines:
        # write the data header
        f.write("trace=new\n")
        f.write("legend="+l.get_label().replace('\n', '\\n')+"\n")

        for a in line_attributes: f.write(a+"="+str(_pylab.getp(l, a)).replace('\n','')+"\n")

        # get the data
        x = l.get_xdata()
        y = l.get_ydata()

        # loop over the data
        for n in range(0, len(x)): f.write(str(float(x[n])) + " " + str(float(y[n])) + "\n")

    f.close()

def save_figure_raw_data(figure="gcf", **kwargs):
    """
    This will just output an ascii file for each of the traces in the shown figure.

    **kwargs are sent to dialogs.Save()
    """

    # choose a path to save to
    path = _s.dialogs.Save(**kwargs)
    if path=="": return "aborted."

    # if no argument was given, get the current axes
    if figure=="gcf": figure = _pylab.gcf()

    for n in range(len(figure.axes)):
        a = figure.axes[n]

        for m in range(len(a.lines)):
            l = a.lines[m]

            x = l.get_xdata()
            y = l.get_ydata()

            p = _os.path.split(path)
            p = _os.path.join(p[0], "axes" + str(n) + " line" + str(m) + " " + p[1])
            print(p)

            # loop over the data
            f = open(p, 'w')
            for j in range(0, len(x)):
                f.write(str(x[j]) + "\t" + str(y[j]) + "\n")
            f.close()


def load_plot(clear=1, offset=0, axes="gca"):
    # choose a path to load the file from
    path = _s.dialogs.SingleFile("*.*", default_directory="save_plot_default_directory")

    if path=="": return

    # read the file in
    lines = _fun.read_lines(path)

    # if no argument was given, get the current axes
    if axes=="gca": axes=_pylab.gca()

    # if we're supposed to, clear the plot
    if clear:
        axes.figure.clear()
        _pylab.gca()

    # split by space delimiter and see if the first element is a number
    xdata  = []
    ydata  = []
    line_stuff = []
    legend = []
    title  = 'reloaded plot with no title'
    xlabel = 'x-data with no label'
    ylabel = 'y-data with no label'
    for line in lines:

        s = line.strip().split('=')

        if len(s) > 1: # header stuff

            if s[0].strip() == 'title':
                # set the title of the plot
                title = ""
                for n in range(1,len(s)): title += " "+s[n].replace('\\n', '\n')

            elif s[0].strip() == 'xlabel':
                # set the title of the plot
                xlabel = ""
                for n in range(1,len(s)): xlabel += " "+s[n].replace('\\n', '\n')

            elif s[0].strip() == 'ylabel':
                # set the title of the plot
                ylabel = ""
                for n in range(1,len(s)): ylabel += " "+s[n].replace('\\n', '\n')

            elif s[0].strip() == 'legend':
                l=""
                for n in range(1,len(s)): l += " " + s[n].replace('\\n', '\n')
                legend.append(l)

            elif s[0].strip() == 'trace':
                # if we're on a new plot
                xdata.append([])
                ydata.append([])
                line_stuff.append({})

            elif s[0].strip() in line_attributes:
                line_stuff[-1][s[0].strip()] = s[1].strip()


        else: # data
            s = line.strip().split(' ')
            try:
                float(s[0])
                float(s[1])
                xdata[-1].append(float(s[0]))
                ydata[-1].append(float(s[1])+offset)
            except:
                print("error s=" + str(s))

    for n in range(0, len(xdata)):
        axes.plot(xdata[n], ydata[n])
        l = axes.get_lines()[-1]
        l.set_label(legend[n])
        for key in line_stuff[n]:
            try:    _pylab.setp(l, key, float(line_stuff[n][key]))
            except: _pylab.setp(l, key,       line_stuff[n][key])

    axes.set_title(title)
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    format_figure(axes.figure)




def modify_legend(axes="gca"):
    # get the axes
    if axes=="gca": axes = _pylab.gca()

    # get the lines
    lines = axes.get_lines()

    # loop over the lines
    for line in lines:
        if isinstance(line, _mpl.lines.Line2D):

            # highlight the line
            fatten_line(line)

            # get the label (from the legend)
            label = line.get_label()

            print(label)

            new_label = input("New Label: ")
            if new_label == "q" or new_label == "quit":
                unfatten_line(line)
                return

            if not new_label == "\n": line.set_label(new_label)

            unfatten_line(line)
            format_figure()


def fatten_line(line, william_fatner=2.0):
    size  = line.get_markersize()
    width = line.get_linewidth()
    line.set_markersize(size*william_fatner)
    line.set_linewidth(width*william_fatner)
    _pylab.draw()

def unfatten_line(line, william_fatner=0.5):
    fatten_line(line, william_fatner)


def legend(location='best', fontsize=16, axes="gca"):
    if axes=="gca": axes = _pylab.gca()

    axes.legend(loc=location, prop=_mpl.font_manager.FontProperties(size=fontsize))
    _pylab.draw()




#
# Style cycle, available for use in plotting
#
class style_cycle:

    def __init__(self, linestyles=['-'], markers=['s','^','o'], colors=['k','r','b','g','m'], line_colors=None, face_colors=None, edge_colors=None):
        """
        Set up the line/marker rotation cycles.

        linestyles, markers, and colors need to be lists, and you can override
        using line_colors, and face_colors, and edge_colors (markeredgecolor) by
        setting them to a list instead of None.
        """

        # initial setup, assuming all the overrides are None
        self.linestyles     = linestyles
        self.markers        = markers
        self.line_colors    = colors
        self.face_colors    = colors
        self.edge_colors    = colors

        # Apply the override colors
        if not line_colors == None: self.line_colors = line_colors
        if not face_colors == None: self.face_colors = face_colors
        if not edge_colors == None: self.edge_colors = edge_colors

        self.line_colors_index  = 0
        self.markers_index      = 0
        self.linestyles_index   = 0
        self.face_colors_index  = 0
        self.edge_colors_index  = 0

    # binding for the user to easily re-initialize
    initialize = __init__

    def reset(self):
        self.line_colors_index  = 0
        self.markers_index      = 0
        self.linestyles_index   = 0
        self.face_colors_index  = 0
        self.edge_colors_index  = 0

    def get_line_color(self, increment=1):
        """
        Returns the current color, then increments the color by what's specified
        """

        i = self.line_colors_index

        self.line_colors_index += increment
        if self.line_colors_index >= len(self.line_colors):
            self.line_colors_index = self.line_colors_index-len(self.line_colors)
            if self.line_colors_index >= len(self.line_colors): self.line_colors_index=0 # to be safe

        return self.line_colors[i]

    def set_all_colors(self, colors=['k','k','r','r','b','b','g','g','m','m']):
        self.line_colors=colors
        self.face_colors=colors
        self.edge_colors=colors
        self.reset()

    def get_marker(self, increment=1):
        """
        Returns the current marker, then increments the marker by what's specified
        """

        i = self.markers_index

        self.markers_index += increment
        if self.markers_index >= len(self.markers):
            self.markers_index = self.markers_index-len(self.markers)
            if self.markers_index >= len(self.markers): self.markers_index=0 # to be safe

        return self.markers[i]

    def set_markers(self, markers=['o']):
        self.markers=markers
        self.reset()

    def get_linestyle(self, increment=1):
        """
        Returns the current marker, then increments the marker by what's specified
        """

        i = self.linestyles_index

        self.linestyles_index += increment
        if self.linestyles_index >= len(self.linestyles):
            self.linestyles_index = self.linestyles_index-len(self.linestyles)
            if self.linestyles_index >= len(self.linestyles): self.linestyles_index=0 # to be safe

        return self.linestyles[i]

    def set_linestyles(self, linestyles=['-']):
        self.linestyles=linestyles
        self.reset()

    def get_face_color(self, increment=1):
        """
        Returns the current face, then increments the face by what's specified
        """

        i = self.face_colors_index

        self.face_colors_index += increment
        if self.face_colors_index >= len(self.face_colors):
            self.face_colors_index = self.face_colors_index-len(self.face_colors)
            if self.face_colors_index >= len(self.face_colors): self.face_colors_index=0 # to be safe

        return self.face_colors[i]

    def set_face_colors(self, colors=['k','none','r','none','b','none','g','none','m','none']):
        self.face_colors=colors
        self.reset()

    def get_edge_color(self, increment=1):
        """
        Returns the current face, then increments the face by what's specified
        """

        i = self.edge_colors_index

        self.edge_colors_index += increment
        if self.edge_colors_index >= len(self.edge_colors):
            self.edge_colors_index = self.edge_colors_index-len(self.edge_colors)
            if self.edge_colors_index >= len(self.edge_colors): self.edge_colors_index=0 # to be safe

        return self.edge_colors[i]

    def set_edge_colors(self, colors=['k','none','r','none','b','none','g','none','m','none']):
        self.edge_colors=colors
        self.reset()


    def apply(self, axes="gca"):
        """
        Applies the style cycle to the lines in the axes specified
        """

        if axes == "gca": axes = _pylab.gca()
        self.reset()
        lines = axes.get_lines()

        for l in lines:
            l.set_color(self.get_line_color(1))
            l.set_mfc(self.get_face_color(1))
            l.set_marker(self.get_marker(1))
            l.set_mec(self.get_edge_color(1))
            l.set_linestyle(self.get_linestyle(1))

        _pylab.draw()

    def __call__(self, increment=1):
        return self.get_line_color(increment)

# this is the guy in charge of keeping track of the rotation of colors and symbols for plotting
style = style_cycle(colors     = ['k','r','b','g','m'],
                    markers    = ['o', '^', 's'],
                    linestyles = ['-'])


