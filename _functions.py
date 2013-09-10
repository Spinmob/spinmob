#############################################################
# various functions that I like to use
import numpy                        as _n
import pylab                        as _pylab
import cPickle                      as _cPickle
import os                           as _os
import thread                       as _thread
import shutil                       as _shutil
import wx                           as _wx
import time                         as _time

from scipy.integrate import quad

import _dialogs                    ;reload(_dialogs)
import _pylab_tweaks               ;reload(_pylab_tweaks)
_pt = _pylab_tweaks

# Functions from other libraries
average = _n.average

try:    _prefs
except: _prefs = None

def _print_figures(figures, arguments='', file_format='pdf', target_width=8.5, target_height=11.0, target_pad=0.5):
    """
    figure printing loop designed to be launched in a separate thread.
    """

    for fig in figures:
        # output the figure to postscript
        path = _os.path.join(_prefs.temp_dir,"graph."+file_format)
        
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
            c = _prefs['print_command'] + ' ' + arguments + ' "' + path + '"'
        else:
            c = _prefs['print_command'] + ' "' + path + '"'

        print c
        _os.system(c)


def append_to_file(path, string):
    file = open(path, 'a')
    file.write(string)
    file.close()

def array_shift(a, n, fill="average"):
    """
    This will return an array with all the elements shifted forward in index by n.

    a is the array
    n is the amount by which to shift (can be positive or negative)

    fill="average"      fill the new empty elements with the average of the array
    fill="wrap"         fill the new empty elements with the lopped-off elements
    fill=37.2           fill the new empty elements with the value 37.2
    """

    new_a = _n.array(a)

    if n==0: return new_a

    fill_array = _n.array([])
    fill_array.resize(_n.abs(n))

    # fill up the fill array before we do the shift
    if   fill is "average": fill_array = 0.0*fill_array + _n.average(a)
    elif fill is "wrap" and n >= 0:
        for i in range(0,n): fill_array[i] = a[i-n]
    elif fill is "wrap" and n < 0:
        for i in range(0,-n): fill_array[i] = a[i]
    else:   fill_array = 0.0*fill_array + fill

    # shift and fill
    if n > 0:
        for i in range(n, len(a)): new_a[i] = a[i-n]
        for i in range(0, n):      new_a[i] = fill_array[i]
    else:
        for i in range(0, len(a)+n): new_a[i] = a[i-n]
        for i in range(0, -n):       new_a[-i-1] = fill_array[-i-1]

    return new_a



def assemble_covariance(error, correlation):
    """
    This takes an error vector and a correlation matrix and assembles the covariance
    """

    covariance = []
    for n in range(0, len(error)):
        covariance.append([])
        for m in range(0, len(error)):
            covariance[n].append(correlation[n][m]*error[n]*error[m])
    return _n.array(covariance)
def avg(array):
    return(float(sum(array))/float(len(array)))








def chi_squared(p, f, xdata, ydata):
    return(sum( (ydata - f(p,xdata))**2 ))

def coarsen_array(array, level=1, method='average'):
    """
    Returns a shorter array of binned data (every level+1 data points).
    
    method can be 'average', 'max', 'min', or 'all'
                  'all' returns (average, max, min)
                  
    returns a new array.
    """

    if level is 0 or array==None: return array

    # we do all of them for speed reasons (no string comparison at each step)
    average = _n.array(array[0::level+1])
    maximum = _n.array(array[0::level+1])
    minimum = _n.array(array[0::level+1])
    
    temp = _n.array([0.0]); temp.resize(level+1)

    # loop over 0, 2, 4, ...
    for n in range(0, len(array), level+1):
        
        # loop over this bin
        for m in range(n, n+level+1):
            # make sure we're not past the end of the array
            if m < len(array):    temp[m-n] = array[m]
            # otherwise give it a useful value (the average of the others)
            else:                 temp[m-n] = _n.average(temp[0:m-n])
        
        # append the average to the new array
        average[n/(level+1)] = _n.average(temp)
        maximum[n/(level+1)] = _n.max(temp)
        minimum[n/(level+1)] = _n.min(temp)
        
    if method=="average": return average
    if method=="min"    : return minimum
    if method=="max"    : return maximum
    else                : return average, maximum, minimum



def coarsen_data(xdata, ydata, yerror=None, level=1):
    """
    This does averaging of the data, returning coarsened (numpy) [xdata, ydata, yerror]
    Errors are averaged in quadrature.
    """

    new_xdata = []
    new_ydata = []
    new_error = []

    # if level = 1, loop over 0, 2, 4, ...
    for n in range(0, len(xdata), level+1):
        count = 0.0
        sumx  = 0.0
        sumy  = 0.0
        sume2 = 0.0 # sum squared

        # if n==2, loop 2, 3
        for m in range(n, n+level+1):
            if m < len(xdata):
                sumx  += xdata[m]
                sumy  += ydata[m]
                try:
                    sume2 += yerror[m]**2
                except:
                    sume2 = 1.0
                count += 1.0

        new_xdata.append(sumx/count)
        new_ydata.append(sumy/count)
        new_error.append(sume2**0.5/count)

    xdata = _n.array(new_xdata)
    ydata = _n.array(new_ydata)
    if not yerror==None: yerror = _n.array(new_error)
    return [xdata,ydata,yerror]




def coarsen_matrix(Z, xlevel=0, ylevel=0, method='average'):
    """
    This returns a coarsened numpy matrix.
    
    method can be 'average', 'max', or 'min'
    """
    
    # coarsen x
    if not ylevel: 
        Z_coarsened = Z
    else:
        temp = []        
        for z in Z: temp.append(coarsen_array(z, ylevel, method))
        Z_coarsened = _n.array(temp)    
    
    # coarsen y
    if xlevel:
        Z_coarsened = Z_coarsened.transpose()
        temp = []
        for z in Z_coarsened: temp.append(coarsen_array(z, xlevel, method))
        Z_coarsened = _n.array(temp).transpose()
    
    return Z_coarsened



    # first coarsen the columns (if necessary)
    if ylevel:
        Z_ycoarsened = []
        for c in Z: Z_ycoarsened.append(coarsen_array(c, ylevel, method))
        Z_ycoarsened = _n.array(Z_ycoarsened)

    # now coarsen the rows
    if xlevel: return coarsen_array(Z_ycoarsened, xlevel, method)
    else:      return _n.array(Z_ycoarsened)

def combine_dictionaries(a, b):
    """
    returns the combined dictionary.  a's values preferentially chosen
    """

    c = {}
    for key in b.keys(): c[key]=b[key]
    for key in a.keys(): c[key]=a[key]
    return c

def data_from_file(path, delimiter=" "):
    lines = read_lines(path)
    x = []
    y = []
    for line in lines:
       s=line.split(delimiter)
       if len(s) > 1:
           x.append(float(s[0]))
           y.append(float(s[1]))
    return([_n.array(x), _n.array(y)])


def data_to_file(path, xarray, yarray, delimiter=" ", mode="w"):
    file = open(path, mode)
    for n in range(0, len(xarray)):
        file.write(str(xarray[n]) + delimiter + str(yarray[n]) + '\n')
    file.close()









def decompose_covariance(c):
    """
    This decomposes a covariance matrix into an error vector and a correlation matrix
    """

    # make it a kickass copy of the original
    c = _n.array(c)

    # first get the error vector
    e = []
    for n in range(0, len(c[0])): e.append(_n.sqrt(c[n][n]))

    # now cycle through the matrix, dividing by e[1]*e[2]
    for n in range(0, len(c[0])):
        for m in range(0, len(c[0])):
            c[n][m] = c[n][m] / (e[n]*e[m])

    return [_n.array(e), _n.array(c)]

def derivative(xdata, ydata):
    """
    performs d(ydata)/d(xdata) with nearest-neighbor slopes
    must be well-ordered, returns new arrays [xdata, dydx_data]

    neighbors:
    """
    D_ydata = []
    D_xdata = []
    for n in range(1, len(xdata)-1):
        D_xdata.append(xdata[n])
        D_ydata.append((ydata[n+1]-ydata[n-1])/(xdata[n+1]-xdata[n-1]))

    return [D_xdata, D_ydata]

def derivative_fit(xdata, ydata, neighbors=1):
    """
    loops over the data points, performing a least-squares linear fit of the
    nearest neighbors at each point. Returns an array of x-values and slopes.

    xdata should probably be well-ordered.

    neighbors   How many data point on the left and right to include.
    """

    x    = []
    dydx = []
    nmax = len(xdata)-1

    for n in range(nmax+1):
        # get the indices of the data to fit
        i1 = max(0, n-neighbors)
        i2 = min(nmax, n+neighbors)

        # get the sub data to fit
        xmini = _n.array(xdata[i1:i2+1])
        ymini = _n.array(ydata[i1:i2+1])

        slope, intercept = fit_linear(xmini, ymini)

        # make x the average of the xmini
        x.append(float(sum(xmini))/len(xmini))
        dydx.append(slope)

    return _n.array(x), _n.array(dydx)

def difference(ydata1, ydata2):
    """

    Returns the number you should add to ydata1 to make it line up with ydata2

    """

    y1 = _n.array(ydata1)
    y2 = _n.array(ydata2)

    return(sum(y2-y1)/len(ydata1))




def distort_matrix_X(Z, X, f, new_xmin, new_xmax, subsample=3):
    """
    Applies a distortion (remapping) to the matrix Z (and x-values X) using function f.
    returns new_Z, new_X

    f is an INVERSE function old_x(new_x)

    Z is a matrix. X is an array where X[n] is the x-value associated with the array Z[n].

    new_xmin, new_xmax is the possible range of the distorted x-variable for generating Z

    points is how many elements the stretched Z should have. "auto" means use the same number of bins
    """

    Z = _n.array(Z)
    X = _n.array(X)
    points = len(Z)*subsample


    # define a function for searching
    def zero_me(new_x): return f(new_x)-target_old_x

    # do a simple search to find the new_x that gives old_x = min(X)
    target_old_x = min(X)
    new_xmin = find_zero_bisect(zero_me, new_xmin, new_xmax, _n.abs(new_xmax-new_xmin)*0.0001)
    target_old_x = max(X)
    new_xmax = find_zero_bisect(zero_me, new_xmin, new_xmax, _n.abs(new_xmax-new_xmin)*0.0001)

    # now loop over all the new x values
    new_X = []
    new_Z = []
    bin_width = float(new_xmax-new_xmin)/(points)
    for new_x in frange(new_xmin, new_xmax, bin_width):

        # make sure we're in the range of X
        if f(new_x) <= max(X) and f(new_x) >= min(X):

            # add this guy to the array
            new_X.append(new_x)

            # get the interpolated column
            new_Z.append( interpolate(X,Z,f(new_x)) )

    return _n.array(new_Z), _n.array(new_X)




def distort_matrix_Y(Z, Y, f, new_ymin, new_ymax, subsample=3):
    """
    Applies a distortion (remapping) to the matrix Z (and y-values Y) using function f.
    returns new_Z, new_Y

    f is a function old_y(new_y)

    Z is a matrix. Y is an array where Y[n] is the y-value associated with the array Z[:,n].

    new_ymin, new_ymax is the range of the distorted x-variable for generating Z

    points is how many elements the stretched Z should have. "auto" means use the same number of bins
    """

    # just use the same methodology as before by transposing, distorting X, then
    # transposing back
    new_Z, new_Y = distort_matrix_X(Z.transpose(), Y, f, new_ymin, new_ymax, subsample)
    return new_Z.transpose(), new_Y





def dumbguy_minimize(f, xmin, xmax, xstep):
    """
    This just steps x and looks for a peak

    returns x, f(x)
    """

    prev = f(xmin)
    this = f(xmin+xstep)
    for x in frange(xmin+xstep,xmax,xstep):
        next = f(x+xstep)

        # see if we're on top
        if this < prev and this < next: return x, this

        prev = this
        this = next

    return x, this

def elements_are_numbers(array, start_index=0, end_index=-1):
    if len(array) == 0: return 0

    output_value=1

    if end_index < 0: end_index=len(array)-1
    for n in array:
        try: float(n)
        except:
            try:
                complex(n)
                output_value=2
            except:
                try:
                    complex(n.replace('(','').replace(')',''))
                    output_value=2
                except:
                    return 0
    return output_value

def elements_are_strings(array, start_index=0, end_index=-1):
    if len(array) == 0: return 0

    if end_index < 0: end_index=len(array)-1

    for n in range(start_index, end_index+1):
        if not type(array[n]) == str: return 0
    return 1

def erange(start, end, steps):
    """
    Returns a numpy array over the specified range taking geometric steps.

    See also numpy.logspace()
    """
    if start == 0:
        print "Nothing you multiply zero by gives you anything but zero. Try picking something small."
        return None
    if end == 0:
        print "It takes an infinite number of steps to get to zero. Try a small number?"
        return None

    # figure out our multiplication scale
    x = (1.0*end/start)**(1.0/(steps-1))

    # now generate the array
    ns = _n.array(range(0,steps))
    a =  start*_n.power(x,ns)

    # tidy up the last element (there's often roundoff error)
    a[-1] = end

    return a


def find_N_peaks(array, N=4, max_iterations=100, rec_max_iterations=3, recursion=1):
    """
    This will run the find_peaks algorythm, adjusting the baseline until exactly N peaks are found.
    """

    if recursion<0: return None

    # get an initial guess as to the baseline
    ymin = min(array)
    ymax = max(array)

    for n in range(max_iterations):

        # bisect the range to estimate the baseline
        y1 = (ymin+ymax)/2.0

        # now see how many peaks this finds. p could have 40 for all we know
        p, s, i = find_peaks(array, y1, True)

        # now loop over the subarrays and make sure there aren't two peaks in any of them
        for n in range(len(i)):
            # search the subarray for two peaks, iterating 3 times (75% selectivity)
            p2 = find_N_peaks(s[n], 2, rec_max_iterations, rec_max_iterations=rec_max_iterations, recursion=recursion-1)

            # if we found a double-peak
            if not p2==None:
                # push these non-duplicate values into the master array
                for x in p2:
                    # if this point is not already in p, push it on
                    if not x in p: p.append(x+i[n]) # don't forget the offset, since subarrays start at 0


        # if we nailed it, finish up
        if len(p) == N: return p

        # if we have too many peaks, we need to increase the baseline
        if len(p) > N: ymin = y1

        # too few? decrease the baseline
        else:          ymax = y1

    return None

def find_peaks(array, baseline=0.1, return_subarrays=False):
    """
    This will try to identify the indices of the peaks in array, returning a list of indices in ascending order.

    Runs along the data set until it jumps above baseline. Then it considers all the subsequent data above the baseline
    as part of the peak, and records the maximum of this data as one peak value.
    """

    peaks = []

    if return_subarrays:
        subarray_values  = []
        subarray_indices = []

    # loop over the data
    n = 0
    while n < len(array):
        # see if we're above baseline, then start the "we're in a peak" loop
        if array[n] > baseline:

            # start keeping track of the subarray here
            if return_subarrays:
                subarray_values.append([])
                subarray_indices.append(n)

            # find the max
            ymax=baseline
            nmax = n
            while n < len(array) and array[n] > baseline:
                # add this value to the subarray
                if return_subarrays:
                    subarray_values[-1].append(array[n])

                if array[n] > ymax:
                    ymax = array[n]
                    nmax = n

                n = n+1

            # store the max
            peaks.append(nmax)

        else: n = n+1

    if return_subarrays: return peaks, subarray_values, subarray_indices
    else:                return peaks


def find_two_peaks(data, remove_background=True):
    """

    Returns two indicies for the two maxima

    """

    y  = _n.array( data            )
    x  = _n.array( range(0,len(y)) )

    # if we're supposed to, remove the linear background
    if remove_background:
        [slope, offset] = fit_linear(x,y)
        y = y - slope*x
        y = y - min(y)

    # find the global maximum
    max1   = max(y)
    n1     = index(max1, y)

    # now starting at n1, work yourway left and right until you find
    # the left and right until the data drops below a 1/2 the max.
    # the first side to do this gives us the 1/2 width.
    np = n1+1
    nm = n1-1
    yp = max1
    ym = max1
    width = 0
    while 0 < np < len(y) and 0 < nm < len(y):
        yp = y[np]
        ym = y[nm]

        if yp <= 0.5*max1 or ym <= 0.5*max1:
            width = np - n1
            break

        np += 1
        nm -= 1



    # if we didn't find it, we pooped out
    if width == 0:
        return [n1,-1]

    # this means we have a valid 1/2 width.  Find the other max in the
    # remaining data
    n2 = nm
    while 1 < np < len(y)-1 and 1 < nm < len(y)-1:
        if y[np] > y[n2]:
            n2 = np
        if y[nm] > y[n2]:
            n2 = nm
        np += 1
        nm -= 1

    return([n1,n2])





def find_zero_bisect(f, xmin, xmax, xprecision):
    """
    This will bisect the range and zero in on zero.
    """
    if f(xmax)*f(xmin) > 0:
        print "find_zero_bisect(): no zero on the range",xmin,"to",xmax
        return None

    temp = min(xmin,xmax)
    xmax = max(xmin,xmax)
    xmin = temp

    xmid = (xmin+xmax)*0.5
    while xmax-xmin > xprecision:
        y = f(xmid)

        # pick the direction with one guy above and one guy below zero
        if y > 0:
            # move left or right?
            if f(xmin) < 0: xmax=xmid
            else:           xmin=xmid

        # f(xmid) is below zero
        elif y < 0:
            # move left or right?
            if f(xmin) > 0: xmax=xmid
            else:           xmin=xmid

        # yeah, right
        else: return xmid

        # bisect again
        xmid = (xmin+xmax)*0.5

    return xmid


def fit_linear(xdata, ydata):
    """

    Returns slope and intercept of line of best fit, excluding data
    outside the range defined by xrange

    """
    x = xdata
    y = ydata

    ax  = avg(x)
    ay  = avg(y)
    axx = avg(x*x)
    ayy = avg(y*y)
    ayx = avg(y*x)

    slope     = (ayx - ay*ax) / (axx - ax*ax)
    intercept = ay - slope*ax

    return slope, intercept






def frange(start, end, inc=1.0):
    """
    A range function, that accepts float increments and reversed direction.

    See also numpy.linspace()
    """

    start = 1.0*start
    end   = 1.0*end
    inc   = 1.0*inc

    # if we got a dumb increment
    if not inc: return _n.array([start,end])

    # if the increment is going the wrong direction
    if 1.0*(end-start)/inc < 0.0:
        inc = -inc

    # get the integer steps
    ns = _n.array(range(0, int(1.0*(end-start)/inc)+1))

    return start + ns*inc


def imax(array):
    """
    Returns the index of the maximum of array.
    """
    return index(max(array), array)

def imin(array):
    """
    Returns the index of the minimum of array.
    """
    return index(min(array), array)

def index(value, array):
    for n in range(0,len(array)):
        if value == array[n]:
            return(n)
    return(-1)

def index_nearest(value, array):
    """
    expects a _n.array
    returns the global minimum of (value-array)^2
    """

    a = (array-value)**2
    return index(a.min(), a)

def index_next_crossing(value, array, starting_index=0, direction=1):
    """
    starts at starting_index, and walks through the array until
    it finds a crossing point with value

    set direction=-1 for down crossing
    """

    for n in range(starting_index, len(array)-1):
        if  (value-array[n]  )*direction >= 0         \
        and (value-array[n+1])*direction <  0: return n

    # no crossing found
    return -1




def insert_ordered(value, array):
    """
    This will insert the value into the array, keeping it sorted, and returning the
    index where it was inserted
    """

    index = 0

    # search for the last array item that value is larger than
    for n in range(0,len(array)):
        if value >= array[n]: index = n+1

    array.insert(index, value)
    return index

def integrate(f, x1, x2):
    """
    f(x) = ...
    integrated from x1 to x2
    """

    return quad(f, x1, x2)[0]

def integrate2d(f, x1, x2, y1, y2):
    """
    f(x,y) = ...
    integrated from x1 to x2, y1 to y2
    """
    def fx(y):
        def g(x): return f(x,y)
        return integrate(g, x1, x2)

    return quad(fx, y1, y2)[0]

def integrate3d(f, x1, x2, y1, y2, z1, z2):
    """
    f(x,y,z) = ...
    integrated from x1 to x2, y1 to y2, z1 to z2
    """

    def fxy(z):
        def g(x,y): return f(x,y,z)
        return(integrate2d(g, x1, x2, y1, y2))

    return quad(fxy, z1, z2)[0]






def integrate_data(xdata, ydata, xmin=None, xmax=None, autozero=0):
    """
    Numerically integrates up the ydata using the trapezoid approximation.
    estimate the bin width (scaled by the specified amount).
    Returns (xdata, integrated ydata).

    autozero is the number of data points to use as an estimate of the background
    (then subtracted before integrating).
    """

    # sort the arrays and make sure they're numpy arrays
    [xdata, ydata] = sort_matrix([xdata,ydata],0)
    xdata = _n.array(xdata)
    ydata = _n.array(ydata)

    if xmin==None: xmin = min(xdata)
    if xmax==None: xmax = max(xdata)

    # find the index range
    imin = xdata.searchsorted(xmin)
    imax = xdata.searchsorted(xmax)

    xint = [xdata[imin]]
    yint = [0]

    # get the autozero
    if autozero >= 1:
        zero = _n.average(ydata[imin:imin+int(autozero)])
        ydata = ydata-zero

    for n in range(imin+1,imax):
        if len(yint):
            xint.append(xdata[n])
            yint.append(yint[-1]+0.5*(xdata[n]-xdata[n-1])*(ydata[n]+ydata[n-1]))
        else:
            xint.append(xdata[n])
            yint.append(0.5*(xdata[n]-xdata[n-1])*(ydata[n]+ydata[n-1]))

    return _n.array(xint), _n.array(yint)

def interpolate(xarray, yarray, x, rigid_limits=True):
    """

    returns the y value of the linear interpolated function
    y(x). Assumes increasing xarray!

    rigid_limits=False means when x is outside xarray's range,
    use the endpoint as the y-value.

    """
    if not len(xarray) == len(yarray):
        print "lengths don't match.", len(xarray), len(yarray)
        return None
    if x < xarray[0] or x > xarray[-1]:
        if rigid_limits:
            print "x=" + str(x) + " is not in " + str(min(xarray)) + " to " + str(max(xarray))
            return None
        else:
            if x < xarray[0]: return yarray[0]
            else:             return yarray[-1]

    # find the index of the first value in xarray higher than x
    for n2 in range(1, len(xarray)):
        if x >= min(xarray[n2], xarray[n2-1]) and x <= max(xarray[n2], xarray[n2-1]):
            break
        if n2 == len(xarray):
            print "couldn't find x anywhere."
            return None
    n1 = n2-1

    # now we have the indices surrounding the x value
    # interpolate!

    return yarray[n1] + (x-xarray[n1])*(yarray[n2]-yarray[n1])/(xarray[n2]-xarray[n1])



def invert_increasing_function(f, f0, xmin, xmax, tolerance, max_iterations=100):
    """
    This will try try to qickly find a point on the f(x) curve between xmin and xmax that is
    equal to f0 within tolerance.
    """

    for n in range(max_iterations):
        # start at the middle
        x = 0.5*(xmin+xmax)

        df = f(x)-f0
        if _n.fabs(df) < tolerance: return x

        # if we're high, set xmin to x etc...
        if df > 0: xmin=x
        else:      xmax=x

    print "Couldn't find value!"
    return 0.5*(xmin+xmax)

def is_a_number(s):
    try: float(s); return True
    except:
        try: complex(s); return True
        except: return False


def is_close(x, array, fraction=0.0001):
    """

    compares x to all of the values in array.  If it's fraction close to
    any, returns true

    """

    result = False
    for n in range(0,len(array)):
        if array[n] == 0:
            if x == 0:
                result = True
        elif abs((x-array[n])/array[n]) < fraction:
            result = True

    return(result)

def is_iterable(a):
    """
    Test if something is iterable.
    """
    return hasattr(a, '__iter__')



def join(array_of_strings, delimiter=' '):
    if array_of_strings == []: return ""

    if delimiter==None: delimiter=' '

    output = str(array_of_strings[0])
    for n in range(1, len(array_of_strings)):
        output += delimiter + str(array_of_strings[n])
    return(output)


def load_object(path="ask", text="Load a pickled object."):
    if path=="ask": path = _dialogs.SingleFile("*.pickle", text=text)
    if path == "": return None

    f = open(path, "r")
    object = _cPickle.load(f)
    f.close()

    object._path = path
    return object

def printer(figure='gcf', arguments='', threaded=False, file_format='pdf'):
    """
    Quick function that saves the specified figure as a postscript and then
    calls the command defined by spinmob.prefs['print_command'] with this
    postscript file as the argument.

    figure='gcf'    can be 'all', a number, or a list of numbers
    """

    global _prefs

    if not _prefs.has_key('print_command'):
        print "No print command setup. Set the user variable prefs['print_command']."
        return

    if   figure=='gcf': figure=[_pylab.gcf().number]
    elif figure=='all': figure=_pylab.get_fignums()
    if not getattr(figure,'__iter__',False): figure = [figure]

    print "figure numbers in queue:", figure

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
            print "WARNING: Timed out waiting for canvas to return to original state!"

        # bring back the figure and command line
        _pylab.draw()
        _pylab_tweaks.get_pyshell()

    else:   
        _print_figures(figures, arguments, file_format)
        _pylab.draw()


def psd(t, y, pow2=False, window=None):
    """
    Single-sided power spectral density, assuming real valued inputs.

    This goes through the numpy fourier transform process, assembling and returning
    (frequencies, psd) given time and signal data y. Use psdfreq() to get the frequencies.

    powers_of_2     Set this to true if you only want to keep the first 2^n data
                    points (speeds up the FFT substantially)

    window          can be set to any of the windowing functions in numpy,
                    e.g. window="hanning"
    """
    # make sure they're numpy arrays
    y = _n.array(y)

    # if we're doing the power of 2, do it
    if pow2:
        keep  = 2**int(_n.log2(len(y)))

        # now resize the data
        y.resize(keep)
        t.resize(keep)

    # try to get the windowing function
    w = None
    if window:
        try:
            w = eval("_n."+window, globals())
        except:
            print "ERROR: Bad window!"
            return

    # apply the window
    if w:
        a = w(len(y))
        y = len(y) * a * y / sum(a)

    # do the actual fft, and normalize the power
    fft = _n.fft.fft(y)
    P = _n.real(fft*fft.conj())
    P = P / len(y)**2

    Fpos = psdfreq(t, pow2=False)
    Ppos = P[0:len(P)/2] + P[0:-len(P)/2]
    Ppos[0] = Ppos[0]/2.0

    # get the normalized power in y^2/Hz
    Ppos  = Ppos/(Fpos[1]-Fpos[0])

    return Fpos, Ppos

def psdfreq(t, pow2=False):
    """
    Given time array t, returns the positive frequencies of the FFT, including zero.
    """
    # if we're doing the power of 2, do it
    if pow2:
        keep  = 2**int(_n.log2(len(t)))
        t.resize(keep)

    # get the frequency array
    F = _n.fft.fftfreq(len(t), t[1]-t[0])

    # now add the positive and negative frequency components
    return F[0:len(F)/2]


def read_lines(path):
    f = open(path, 'rU')
    a = f.readlines()
    f.close()

    return(a)



def replace_in_files(search, replace, depth=0, paths="ask", confirm=True):
    """
    Does a line-by-line search and replace, but only up to the "depth" line.
    """

    # have the user select some files
    if paths=="ask":
        paths = _dialogs.MultipleFiles('DIS AND DAT|*.*')
    if paths == []: return

    for path in paths:
        lines = read_lines(path)

        if depth: N=min(len(lines),depth)
        else:     N=len(lines)

        for n in range(0,N):
            if lines[n].find(search) >= 0:
                lines[n] = lines[n].replace(search,replace)
                print path.split(_os.path.pathsep)[-1]+ ': "'+lines[n]+'"'
                _wx.Yield()

        # only write if we're not confirming
        if not confirm:
            _os.rename(path, path+".backup")
            write_to_file(path, join(lines, ''))

    if confirm:
        if raw_input("yes? ")=="yes":
            replace_in_files(search,replace,depth,paths,False)

    return
def replace_lines_in_files(search_string, replacement_line):
    """
    Finds lines containing the search string and replaces the whole line with
    the specified replacement string.
    """


    # have the user select some files
    paths = _dialogs.MultipleFiles('DIS AND DAT|*.*')
    if paths == []: return

    for path in paths:
        _shutil.copy(path, path+".backup")
        lines = read_lines(path)
        for n in range(0,len(lines)):
            if lines[n].find(search_string) >= 0:
                print lines[n]
                lines[n] = replacement_line.strip() + "\n"
        write_to_file(path, join(lines, ''))

    return

def reverse(array):
    """
    returns a reversed numpy array
    """
    l = list(array)
    l.reverse()
    return _n.array(l)

def save_object(object, path="ask", text="Save this object where?"):
    if path=="ask": path = _dialogs.Save("*.pickle", text=text)
    if path == "": return

    if len(path.split(".")) <= 1 or not path.split(".")[-1] == "pickle":
        path = path + ".pickle"

    object._path = path

    f = open(path, "w")
    _cPickle.dump(object, f)
    f.close()

def shift_feature_to_x0(xdata, ydata, x0=0, feature=imax):
    """
    Finds a feature in the the ydata and shifts xdata so the feature is centered
    at x0. Returns shifted xdata, ydata. Try me with plot.tweaks.manipulate_shown_data()!

    xdata,ydata     data set
    x0=0            where to shift the peak
    feature=imax    function taking an array/list and returning the index of said feature
    """
    i = feature(ydata)
    return xdata-xdata[i]+x0, ydata



def smooth(array, index, amount):
    """

    Returns the average of the data at the specified index +/- amount

    """

    sum = array[index]
    count = 1.

    for n in range(1, amount+1):
        if index+n >= len(array):
            break
        sum   += array[index+n]
        count += 1.

    for n in range(1, amount+1):
        if index-n < 0:
            break
        sum   += array[index-n]
        count += 1.

    return(sum/count)


def smooth_array(array, amount=1):
    """

    Returns the nearest-neighbor (+/- amount) smoothed array.
    This does not modify the array or slice off the funny end points.

    """
    if amount==0: return array

    # we have to store the old values in a temp array to keep the
    # smoothing from affecting the smoothing
    new_array = _n.array(array)

    for n in range(len(array)):
        new_array[n] = smooth(array, n, amount)

    return new_array


def smooth_data(xdata, ydata, yerror, amount=1):
    """
    Returns smoothed [xdata, ydata, yerror]. Does not destroy the input arrays.
    """

    new_xdata  = smooth_array(_n.array(xdata), amount)
    new_ydata  = smooth_array(_n.array(ydata), amount)
    if yerror == None:  new_yerror = None
    else:               new_yerror = smooth_array(_n.array(yerror), amount)

    return [new_xdata, new_ydata, new_yerror]



def sort_matrix(a,n=0):
    """
    This will rearrange the array a[n] from lowest to highest, and
    rearrange the rest of a[i]'s in the same way. It is dumb and slow.

    Returns a numpy array.
    """
    a = _n.array(a)
    return a[:,a[n,:].argsort()] # this is magic.


def submatrix(matrix,i1,i2,j1,j2):
    """
    returns the submatrix defined by the index bounds i1-i2 and j1-j2

    Endpoints included!
    """

    new = []
    for i in range(i1,i2+1):
        new.append(matrix[i][j1:j2+1])
    return _n.array(new)






def trim_data(xdata, ydata, yerror, xrange):
    """
    Removes all the data except that between min(xrange) and max(xrange)
    This does not destroy the input arrays.
    """

    if xrange == None: return [_n.array(xdata), _n.array(ydata), _n.array(yerror)]

    xmax = max(xrange)
    xmin = min(xrange)

    x = []
    y = []
    ye= []
    for n in range(0, len(xdata)):
        if xdata[n] >= xmin and xdata[n] <= xmax:
            x.append(xdata[n])
            y.append(ydata[n])
            if not yerror == None: ye.append(yerror[n])

    if yerror == None: ye = None
    else: ye = _n.array(ye)
    return [_n.array(x), _n.array(y), ye]

def ubersplit(s, delimiters=['\t','\r',' ']):

    # run through the string, replacing all the delimiters with the first delimiter
    for d in delimiters: s = s.replace(d, delimiters[0])
    return s.split(delimiters[0])

def write_to_file(path, string):
    file = open(path, 'w')
    file.write(string)
    file.close()
