#import wx    as _wx
import numpy   as _n
import os      as _os
import shutil  as _shutil
import spinmob as _s
import cPickle as _cPickle

def coarsen_array(a, level=2, method='mean'):
    """
    Returns a coarsened (binned) version of the data. Currently supports
    any of the numpy array operations, e.g. min, max, mean, std, ...
    
    level=2 means every two data points will be binned.
    level=0 or 1 just returns a copy of the array
    """
    if a==None: return None    
    
    # make sure it's a numpy array
    a = _n.array(a)
    
    # quickest option
    if level in [0,1,False]: return a

    # otherwise assemble the python code to execute
    code = 'a.reshape(-1, level).'+method+'(axis=1)'

    # execute, making sure the array can be reshaped!
    try: return eval(code, dict(a=a[0:int(len(a)/level)*level], level=level))
    except:
        print "ERROR: Could not coarsen array with method "+repr(method)
        return a

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

def is_a_number(s):
    """
    This takes an object and determines whether it's a number or a string
    representing a number.
    """
    if _s.fun.is_iterable(s): return False

    try:
        float(s)
        return 1
    except:
        try: 
            complex(s)
            return 2
        except:            
            try: 
                complex(s.replace('(','').replace(')','').replace('i','j'))
                return 2
            except:            
                return False

def is_iterable(a):
    """
    Determine whether the object is iterable.
    """
    return hasattr(a, '__iter__')



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






def chi_squared(p, f, xdata, ydata):
    return(sum( (ydata - f(p,xdata))**2 ))







def coarsen_matrix(Z, xlevel=0, ylevel=0, method='average'):
    """
    This returns a coarsened numpy matrix.

    method can be 'average', 'maximum', or 'minimum'
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

def elements_are_numbers(array):
    """
    Tests whether the elements of the supplied array are numbers.
    """

    # empty case
    if len(array) == 0: return 0

    output_value = 1
    for x in array:

        # test it and die if it's not a number
        test = is_a_number(x)
        if not test: return False

        # mention if it's complex
        output_value = max(output_value,test)
    
    return output_value

def elements_are_strings(array, start_index=0, end_index=-1):
    if len(array) == 0: return 0

    if end_index < 0: end_index=len(array)-1

    for n in range(start_index, end_index+1):
        if not type(array[n]) == str: return 0
    return 1



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

    ax  = _n.average(x)
    ay  = _n.average(y)
    axx = _n.average(x*x)
    ayx = _n.average(y*x)

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


def get_shell_history():
    """
    This only works with some shells.
    """
    # try for ipython
    if 'get_ipython' in globals():
        a = list(get_ipython().history_manager.input_hist_raw)
        a.reverse()
        return a

    elif _os.environ.has_key('SPYDER_SHELL_ID'):
        try:
            p = _os.path.join(_settings.path_user, ".spyder2", ".history.py")
            a = read_lines(p)
            a.reverse()
            return a
        except:
            pass

    # otherwise try pyshell or pycrust (requires wx)
    else:
        try:
            import wx
            for x in wx.GetTopLevelWindows():
                if type(x) in [wx.py.shell.ShellFrame, wx.py.crust.CrustFrame]:
                    a = x.shell.GetText().split(">>>")
                    a.reverse()
                    return a
        except:
            pass

    return ['shell history not available']


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
    """
    Array search that behaves like I want it to. Totally dumb, I know.
    """
    i = array.searchsorted(value)
    if i == len(array): return -1
    else:               return i

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





def join(array_of_strings, delimiter=' '):
    if array_of_strings == []: return ""

    if delimiter==None: delimiter=' '

    output = str(array_of_strings[0])
    for n in range(1, len(array_of_strings)):
        output += delimiter + str(array_of_strings[n])
    return(output)


def _load_object(path="ask", text="Load a pickled object."):
    if path=="ask": path = _s.dialogs.SingleFile("*.pickle", text=text)
    if path == "": return None

    f = open(path, "r")
    object = _cPickle.load(f)
    f.close()

    object._path = path
    return object



def psd(t, y, pow2=False, window=None):
    """
    Single-sided power spectral density, assuming real valued inputs.

    This goes through the numpy fourier transform process, assembling and returning
    (frequencies, psd) given time and signal data y. Use psdfreq() to get the frequencies.

    powers_of_2     Set this to true if you only want to keep the first 2^n data
                    points (speeds up the FFT substantially)

    window          can be set to any of the windowing functions in numpy,
                    e.g. window="hanning"

    returns frequencies, psd (y^2/Hz)
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

    Fpos = psdfreq(t, pow2=pow2)
    Ppos = P[0:len(P)/2] + P[0:-len(P)/2]
    Ppos[0] = Ppos[0]/2.0

    # get the normalized power in y^2/Hz
    Ppos  = Ppos/(Fpos[1]-Fpos[0])

    return Fpos, Ppos

def fft(t, y, pow2=False, window=None):
    """
    FFT of y, assuming complex or real-valued inputs.

    This goes through the numpy fourier transform process, assembling and returning
    (frequencies, complex fft) given time and signal data y.

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

    # do the actual fft, and normalize
    fft = _n.fft.fft(y) / len(t)

    f = _n.fft.fftfreq(len(t), t[1]-t[0])

    return _n.concatenate([f[len(f)/2+1:],f[0:len(f)/2]]) , _n.concatenate([fft[len(fft)/2+1:],fft[0:len(fft)/2]])

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
        paths = _s.dialogs.MultipleFiles('DIS AND DAT|*.*')
    if paths == []: return

    for path in paths:
        lines = read_lines(path)

        if depth: N=min(len(lines),depth)
        else:     N=len(lines)

        for n in range(0,N):
            if lines[n].find(search) >= 0:
                lines[n] = lines[n].replace(search,replace)
                print path.split(_os.path.pathsep)[-1]+ ': "'+lines[n]+'"'

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
    paths = _s.dialogs.MultipleFiles('DIS AND DAT|*.*')
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

def _save_object(object, path="ask", text="Save this object where?"):
    if path=="ask": path = _s.dialogs.Save("*.pickle", text=text)
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

def trim_data(xmin, xmax, xdata, *args):
    """
    Removes all the data except that in which xdata is between xmin and xmax. 
    This does not mutilate the input arrays, and additional arrays
    can be supplied via args (provided they match xdata in shape)

    xmin and xmax can be None
    """

    # make sure it's a numpy array
    if not isinstance(xdata, _n.ndarray): xdata = _n.array(xdata)

    # make sure xmin and xmax are numbers
    if xmin == None: xmin = min(xdata)
    if xmax == None: xmax = max(xdata)

    # get all the indices satisfying the trim condition
    ns = _n.argwhere((xdata >= xmin) & (xdata <= xmax)).transpose()[0]

    # trim the xdata
    output = []
    output.append(xdata[ns])

    # trim the rest
    for a in args:
        # make sure it's a numpy array
        if not isinstance(a, _n.ndarray): a = _n.array(a)
        output.append(a[ns])

    return output

def trim_data_uber(arrays, conditions):
    """
    Non-destructively selects data from the supplied list of arrays based on 
    the supplied list of conditions. Importantly, if any of the conditions are 
    not met for the n'th data point, the n'th data point is rejected for
    all supplied arrays.

    Example:
      x = numpy.linspace(0,10,20)
      y = numpy.sin(x)
      trim_data_uber([x,y], [x>3,x<9,y<0.7])
      
    This will keep only the x-y pairs in which 3<x<9 and y<0.7, returning
    a list of shorter arrays (all having the same length, of course).
    """    
    # dumb conditions
    if len(conditions) == 0: return arrays
    if len(arrays)     == 0: return []    
    
    # find the indices to keep
    all_conditions = conditions[0]
    for n in range(1,len(conditions)): all_conditions = all_conditions & conditions[n]
    ns = _n.argwhere(all_conditions).transpose()[0]

    # assemble and return trimmed data    
    output = []
    for n in range(len(arrays)): output.append(arrays[n][ns])
    return output
    


def ubersplit(s, delimiters=['\t','\r',' ']):

    # run through the string, replacing all the delimiters with the first delimiter
    for d in delimiters: s = s.replace(d, delimiters[0])
    return s.split(delimiters[0])

def write_to_file(path, string):
    file = open(path, 'w')
    file.write(string)
    file.close()