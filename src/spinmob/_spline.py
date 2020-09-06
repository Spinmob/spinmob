import scipy as _scipy                          
import pylab as _pylab
from scipy import interpolate as _interpolate
import spinmob as _s                      
import pylab_helper_standalones as _pylab_help
import time as _time
import spinmob_functions as _fun
import numpy as _numpy

class spline_single:
    # this class is a container for a single spline fit curve
    # initialize it with the results from a spline fit (that array thingy)

    # simply store the fit result on creation    
    def __init__(self, xdata, ydata, smoothing=5000, degree=5, presmoothing=0, plot=True, xlabel="x", ylabel="y", show_derivative=0, xmin="same", xmax="same", simple=0):
        """
        Create a spline object and fit xdata vs ydata with spline
        Set type="interpolate" to simply interpolate the raw data
        """

        # store this stuff for later use
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xdata  = xdata
        self.ydata  = ydata
        self.simple = simple
        self.xmin = min(xdata)
        self.xmax = max(xdata)
        self._path = "(spline not saved)"
        self.smoothing    = smoothing
        self.degree       = degree
        self.presmoothing = presmoothing
        self.plot_flag    = plot
        self.message = ""
                
        
        # if we're not in simple mode, we have to do a spline fit, not just store the data
        if not simple:        
            # self.ydata might be smoothed
            self.ydata_smoothed = list(ydata)

            # if we're supposed to, presmooth the data
            if presmoothing: _fun.smooth_array(self.ydata_smoothed, presmoothing)

            print("presmoothing = ", str(presmoothing))
            print("smoothing = ",    str(smoothing))
            print("degree    = ",    str(degree))
        
            # do the fit
            self.pfit = _interpolate.splrep(xdata, self.ydata_smoothed, s=smoothing, k=degree)


        # now plot if we're supposed to
        if plot:
            fig  = _pylab.gcf()
            fig.clear()
            axes = fig.gca()
            axes.plot(xdata,ydata, "xr")
            axes.set_xlabel(xlabel)
            axes.set_ylabel(ylabel)
            if not simple:
                axes.plot(xdata,self.ydata_smoothed,"+g")
                self.plot(steps=len(xdata)*5, clear=False)
                _pylab_help.set_all_line_attributes("lw", 2)
                if show_derivative: self.plot(steps=len(xdata)*5, clear=False, derivative=show_derivative, yaxis='right')
                _pylab_help.set_all_line_attributes("lw", 1)
                _pylab_help.set_all_line_attributes("color", "r")

            _pylab_help.set_xrange(xmin, xmax)
            fig.canvas.Refresh()
        

        
    # this takes a single value or an array!
    def __call__(self,       x, derivative=0, smooth=0, simple='auto'):
        return self.evaluate(x, derivative,   smooth,   simple)
    def evaluate(self,       x, derivative=0, smooth=0, simple='auto'):
        """
        smooth=0      is how much to smooth the spline data
        simple='auto' is whether we should just use straight interpolation
                      you may want smooth > 0 for this, when derivative=1
        """
        if simple=='auto': simple = self.simple
        
        # make it into an array if it isn't one, and remember that we did
        is_array = True
        if not type(x) == type(_pylab.array([])):
            x = _pylab.array([x])              
            is_array = False

        if simple:
            # loop over all supplied x data, and come up with a y for each
            y = []
            for n in range(0, len(x)):
                # get a window of data around x
                if smooth:
                    [xtemp, ytemp, etemp] = _fun.trim_data(self.xdata, self.ydata, None, [x[n]-smooth, x[n]+smooth])
                else:
                    i1 = _fun.index_nearest(x[n], self.xdata)

                    # if the nearest data point is lower than x, use the next point to interpolate                    
                    if self.xdata[i1] <= x[n] or i1 <= 0: i2 = i1+1
                    else:                                 i2 = i1-1

                    # if we're at the max, extrapolate
                    if i2 >= len(self.xdata):
                        print(x[n], "is out of range. extrapolating")
                        i2 = i1-1

                    x1 = self.xdata[i1]
                    y1 = self.ydata[i1]
                    x2 = self.xdata[i2]
                    y2 = self.ydata[i2]
                    slope = (y2-y1)/(x2-x1)
                                        
                    xtemp = _numpy.array([x[n]])
                    ytemp = _numpy.array([y1 + (x[n]-x1)*slope])
                    
                # calculate the slope based on xtemp and ytemp (if smoothing)
                # or just use the raw slope if smoothing=0
                if derivative == 1:
                    if smooth:
                        y.append((_numpy.average(xtemp*ytemp)-_numpy.average(xtemp)*_numpy.average(ytemp)) /
                                 (_numpy.average(xtemp*xtemp)-_numpy.average(xtemp)**2))
                    else:
                        y.append(slope)
                        
                # otherwise just average (even with one element)
                elif derivative==0:
                    y.append(_numpy.average(ytemp))
    
            if is_array: return _numpy.array(y)
            else:        return y[0]
            
        
        if smooth:
            
            y = []
            for n in range(0, len(x)):
                # take 20 data points from x+/-smooth
                xlow = max(self.xmin,x[n]-smooth)
                xhi  = min(self.xmax,x[n]+smooth)
                xdata = _pylab.linspace(xlow, xhi, 20)
                ydata = _interpolate.splev(xdata, self.pfit, derivative)
                y.append(_numpy.average(ydata))

            if is_array: return _numpy.array(y)
            else:        return y[0]
            
        else:       
            return _interpolate.splev(x, self.pfit, derivative)

    
    def plot(self, derivative=0, xmin="auto", xmax="auto", steps=500, smooth=0, simple='auto', clear=True, yaxis='left'):
        if simple=='auto': simple = self.simple

        # get the min and max
        if xmin=="auto": xmin = self.xmin
        if xmax=="auto": xmax = self.xmax

        # get and clear the figure and axes
        f = _pylab.gcf()
        if clear and yaxis=='left': f.clf()

        # setup the right-hand axis
        if yaxis=='right':  a = _pylab.twinx()
        else:               a = _pylab.gca()

        # define a new simple function to plot, then plot it
        def f(x): return self.evaluate(x, derivative, smooth, simple)
        _pylab_help.plot_function(f, xmin, xmax, steps, clear, axes=a)

        # label it
        th = "th"
        if derivative == 1: th = "st"
        if derivative == 2: th = "nd"
        if derivative == 3: th = "rd"
        if derivative: self.ylabel = str(derivative)+th+" derivative of "+self.ylabel+" spline"
        a.set_xlabel(self.xlabel)
        a.set_ylabel(self.ylabel)
        a.figure.canvas.Refresh()
        

        


                


class spline_array:
    # this class holds an array of spline curves spline(x) at different values of some
    # "y" parameter, and will provide linear interpolation between them with evaluate()
    # evaluate_uber() is used when you generate y_splines.  I wouldn't use this yet.
    #
    def __init__(self, max_y_splines=100, simple=0):
        # create this class, then add spline curves to it    

        # the splines are stored in a dictionary with the key
        # as the parameter and the value is the spline_single
        self.x_splines = {}   # supplied by you
        self.y_splines = [{},{},{},{},{}] # generated by this class, index is x-derivative
        self.max_y_splines = max_y_splines # this sets the minimum x_parameter spacing of the y-splines
        self.xmin = None      # set the minimum and maximum values over which this is valid
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.xlabel = None
        self.ylabel = None
        self.zlabel = None
        self._path = "(spline array not saved)"
        self.simple=simple

    def add_x_spline(self, y_parameter, x_spline):
        # this function adds a spline to the dictionary
        self.x_splines[y_parameter] = x_spline

        # define or update range of validity
        if self.xmin == None: self.xmin = x_spline.xmin
        if self.xmax == None: self.xmax = x_spline.xmax
        if self.ymax == None: self.ymax = y_parameter
        if self.ymin == None: self.ymin = y_parameter

        if x_spline.xmax > self.xmax: self.xmax = x_spline.xmax
        if x_spline.xmin < self.xmin: self.xmin = x_spline.xmin
        if y_parameter > self.ymax: self.ymax = y_parameter
        if y_parameter < self.ymin: self.ymin = y_parameter

        # add in order to the master list of y_values
        self.y_values = list(self.x_splines.keys())
        self.y_values.sort()
        
    def remove_x_spline(self, y_parameter):
        # this function removes a spline from the dictionary
        try: self.x_splines.pop(y_parameter)
        except: print("Spline with parameter "+str(y_parameter)+" doesn't exist! Stop being a damn FOOL.")

    def __call__(self,       x, y, x_derivative=0, smooth=0, simple='auto'):
        return self.evaluate(x, y, x_derivative,   smooth,   simple)
    def evaluate(self,       x, y, x_derivative=0, smooth=0, simple='auto'):
        """
        this evaluates the 2-d spline by doing linear interpolation of the curves
        """

        if simple=='auto': simple = self.simple
        
        # find which values y is in between
        for n in range(0, len(self.y_values)-1):
            # if it's in between, interpolate!
            if self.y_values[n] <= y and self.y_values[n+1] >= y:
                y1 = self.y_values[n]
                y2 = self.y_values[n+1]
                z1 = self.x_splines[y1].evaluate(x, x_derivative, smooth, simple)
                z2 = self.x_splines[y2].evaluate(x, x_derivative, smooth, simple)
                return z1 + (y-y1)*(z2-z1)/(y2-y1)

        print("YARG! The y value "+str(y)+" is out of interpolation range!")            
        if y >= self.y_values[-1]: return self.x_splines[self.y_values[-1]].evaluate(x, x_derivative, smooth, simple)
        else                     : return self.x_splines[self.y_values[0]].evaluate(x, x_derivative, smooth, simple)

    
    def plot_fixed_x(self, x_values, x_derivative=0, steps=1000, smooth=0, simple='auto', ymin="auto", ymax="auto", format=True, clear=1):
        """
        plots the data at fixed x-value, so z vs x
        """
        if simple=='auto': simple=self.simple
        
        # get the min and max
        if ymin=="auto": ymin = self.ymin
        if ymax=="auto": ymax = self.ymax
        if clear: _pylab.gca().clear()

        if not type(x_values) in [type([]), type(_pylab.array([]))]: x_values = [x_values]

        for x in x_values:
    
            # define a new simple function to plot, then plot it
            def f(y): return self.evaluate(x, y, x_derivative, smooth, simple)
            _pylab_help.plot_function(f, ymin, ymax, steps, 0, False)

            # label it
            a = _pylab.gca()
            a.set_xlabel(self.ylabel)
            if x_derivative: a.set_ylabel(str(x_derivative)+" "+str(self.xlabel)+" derivative of "+self.zlabel)
            else:            a.set_ylabel(self.zlabel)
            a.set_title(self._path+"\nSpline array plot at fixed x = "+self.xlabel)
            a.get_lines()[-1].set_label("x ("+self.xlabel+") = "+str(x))

        if format: _s.format_figure()
        return a
    
    def plot_range_fixed_x(self, xmin="auto", xmax="auto", xsteps=21, ymin="auto", ymax="auto", ysteps=200, clear=True, x_derivative=0):
        if xmin=="auto": xmin=self.xmin
        if xmax=="auto": xmax=self.xmax
        
        self.plot_fixed_x(_pylab.linspace(xmin, xmax, xsteps), x_derivative, ysteps, ymin, ymax, False, clear)
        _s.format_figure()
        
    def plot_fixed_y(self, y_values, x_derivative=0, steps=1000, smooth=0, simple='auto', xmin="auto", xmax="auto", format=True, clear=1):
        """
        plots the data at a fixed y-value, so z vs y
        """
        if simple=='auto': simple=self.simple


        # get the min and max
        if xmin=="auto": xmin = self.xmin
        if xmax=="auto": xmax = self.xmax
        if clear: _pylab.gca().clear()

        if not type(y_values) in [type([]), type(_pylab.array([]))]: y_values = [y_values]

        for y in y_values:
            # define a new simple function to plot, then plot it
            def f(x): return self.evaluate(x, y, x_derivative, smooth, simple)
            _pylab_help.plot_function(f, xmin, xmax, steps, 0, True)

            # label it
            a = _pylab.gca()
            th = "th"
            if x_derivative == 1: th = "st"
            if x_derivative == 2: th = "nd"
            if x_derivative == 3: th = "rd"
            if x_derivative: a.set_ylabel(str(x_derivative)+th+" "+self.xlabel+" derivative of "+self.zlabel+" spline")
            else:            a.set_ylabel(self.zlabel)
            a.set_xlabel(self.xlabel)
            a.set_title(self._path+"\nSpline array plot at fixed y "+self.ylabel)
            a.get_lines()[-1].set_label("y ("+self.ylabel+") = "+str(y))
        if format: _s.format_figure()
        return a
    
    def plot_range_fixed_y(self, ymin="auto", ymax="auto", ysteps=21, xmin="auto", xmax="auto", xsteps=200, clear=True, x_derivative=0):
        if ymin=="auto": ymin=self.ymin
        if ymax=="auto": ymax=self.ymax
        
        self.plot_fixed_y(_pylab.linspace(ymin, ymax, ysteps), x_derivative, xsteps, xmin, xmax, False, clear)
        _s.format_figure()

    def generate_y_values(self):
        self.y_values = list(self.x_splines.keys())
        self.y_values.sort()


def copy_spline_array(a):
    """
    This returns an instance of a new spline_array with all the fixins, and the data from a.
    """

    b = spline_array()

    b.x_splines = a.x_splines
    b.y_splines = a.y_splines
    b.max_y_splines = a.max_y_splines
    b.xmin = a.xmin     
    b.xmax = a.xmax
    b.ymin = a.ymin
    b.ymax = a.ymax
    b.xlabel = a.xlabel
    b.ylabel = a.ylabel
    b.zlabel = a.zlabel
    b.simple = a.simple
    

    b.generate_y_values()    

    return b    

    
def load_spline_array(path=None, text="Give me a spline array to load, jerkface! No, YOU'RE the jerkface."):
    a = _s.load_object(path, text)

    b = copy_spline_array(a)
    b._path = a._path
    _s.save_object(b, b._path)

    return b    
            
def generate_spline_array(data, y_parameter="field", smoothing=5000, degree=5, presmoothing=0, coarsen=0, autosave=True, show_derivative=1, text="Give me some files to make a spline with.", simple=0):
    """

    Asks for a bunch of data files, plots and spline-fits the data (verifying at each step),
    and generates a spline_2d object instance filled with the results.

    """

    # create an instance of the spline_2d class
    s = spline_array()

    s.ylabel = y_parameter
    
    # have the user select a file
    paths = _s.DialogMultipleFiles('DIS AND DAT|*.dat', text=text, default_directory=data.directory)
    if paths == []: return

    # loop over each data file, fit it, plot it, ask if it's okay, and move on
    for n in range(0,len(paths)):
        print("spline "+str(n+1)+"/"+str(len(paths)+1))

        # fill up the xdata, ydata, and key            
        data.get_data(paths[n])

        print("y_parameter = "+str(data.constants[y_parameter]))

        # if this is just a simple interpolator, make a simple one
        if simple:
            x_spline = spline_single(data.xdata, data.ydata, plot=True, xlabel=data.xlabel, ylabel=data.ylabel, xmin="same", xmax="same", simple=1)

            a = input("ya: ")
            if a in ["quit", "q"]: return s
            if a in ["y", "yes", "\n"]: s.add_x_spline(data.constants[y_parameter], x_spline)

        # otherwise, we have to do the whole spline plot/fitting thingy
        else:
            data.plot(coarsen=coarsen)
            x_spline = splot("gca", smoothing, degree, presmoothing, interactive=True, show_derivative=show_derivative, simple=simple)
            
            if x_spline.message == "quit": return s
            if x_spline.message == "good": s.add_x_spline(data.constants[y_parameter], x_spline)

        s.xlabel = x_spline.xlabel
        s.zlabel = x_spline.ylabel

        # update the parameters as specified by the user
        presmoothing = x_spline.presmoothing
        smoothing    = x_spline.smoothing
        degree       = x_spline.degree

    print("Complete! "+str(len(paths))+" file and "+str(len(s.x_splines))+" successful splines.")

    s.simple = simple
    if autosave: _s.save_object(s)
    return s    



def splinteractive(xdata, ydata, smoothing=5000, degree=5, presmoothing=0, spline_class=spline_single, xlabel="x", ylabel="y", show_derivative=1, boost_factor=1.1, xmin="same", xmax="same"):
    """

    Give this function x and y data to spline fit and it will fit it, returning an instance of
    spline_single.  It will also ask you if it's okay and you can play with parameters.

    """    

    while True:        
        # fit it
        x_spline = spline_class(xdata, ydata, smoothing, degree, presmoothing, True, xlabel, ylabel, show_derivative, xmin=xmin, xmax=xmax)
        
        # ask if it's okay
        if x_spline.message == "": command = input("What now? ")
        else:                      command = x_spline.message
        
        try:
            float(command)
            command = "s="+command
        except:
            print("parsing...")

        # deal with simple commands
        if   command in ["y", "Y", "yes"]:
            x_spline.message = "good"
            smoothing = x_spline.smoothing
            return x_spline
        elif command in ["n", "N", "no"]:
            x_spline.message = "no"
            smoothing = x_spline.smoothing
            return x_spline
        elif command in ["q", "Q", "quit", "exit"]:
            x_spline.message = "quit"
            smoothing = x_spline.smoothing
            return x_spline
        elif command in ["l", "L", "line"]:
            x_spline.message = "line"
            smoothing = x_spline.smoothing
            x_spline.plot()
            input("(press <enter> when done looking)")
        elif command in ["d", "D", "derivative", "\n"]:
            x_spline.message = "derivative"
            smoothing = x_spline.smoothing
            x_spline.plot(derivative=1)
            input("(press <enter> when done looking)")
        elif command in ["dd", "DD"]:
            x_spline.message = "derivative 2"
            x_spline.plot(derivative=2)
            smoothing = x_spline.smoothing
            input("(press <enter> when done looking)")
        elif command in ["p", "P", "print", "printer"]:
            x_spline.message = "print"
            smoothing = x_spline.smoothing
            _s.printer()
        elif command == "[":
            x_spline.message = "unboost smoothing"
            smoothing = smoothing / boost_factor
        elif command == "]":
            x_spline.message = "boost smoothing"
            smoothing = smoothing * boost_factor

        # deal with parameter changes
        elif command.split("=")[0].strip() in ["s", "smoothing"]:
            try: smoothing = eval(command.split("=")[1].strip())
            except: print("Surely you can give me a better number than THAT piece of shit.")

        elif command.split("=")[0].strip() in ["d", "degree"]:
            try: degree = int(eval(command.split("=")[1].strip()))
            except: print("Nice try, ass.  Learn how to enter data.")

        elif command.split("=")[0].strip() in ["p", "pre", "presmoothing"]:
            try: presmoothing = int(eval(command.split("=")[1].strip()))
            except: print("Nice work.  Yeah, not really.")

        elif command.split("=")[0].strip() in ["b", "boost"]:
            try: boost_factor = float(eval(command.split("=")[1].strip()))
            except: print("Nice try smelly fart.")

        # idiot at the controls
        else:
            print("You need help.\n")
            print("------- COMMAND EXAMPLES -------\n")
            print("y        Yes, it looks good, move on.")
            print("n        No, and there's no hope.  Ignore and move on.")
            print("q        Quit.")
            print("s=1000   Set the smoothing to 10")
            print("d=3      Set the degree to 3")
            print("p=5      Set the presmoothing to 5")
            print("l        Show me the spline without data")
            print("d        Show me the derivative")
            print("]        Boost the smoothing")
            print("[        Reduce the smoothing")
            print("b=1.2    Set the boost factor to 1.2")

            smoothing = x_spline.smoothing


def splot(axes="gca", smoothing=5000, degree=5, presmoothing=0, plot=True, spline_class=spline_single, interactive=True, show_derivative=1):
    """
    
    gets the data from the plot and feeds it into splint
    returns an instance of spline_single

    axes="gca"                  which axes to get the data from.
    smoothing=5000              spline_single smoothing parameter
    presmoothing=0              spline_single data presmoothing factor (nearest neighbor)
    plot=True                   should we plot the result?
    spline_class=spline_single  which data class to use?
    interactive=False           should we spline fit interactively or just make a spline_single?
    
    """

    if   axes=="gca": axes = _pylab.gca()

    xlabel = axes.xaxis.label.get_text()
    ylabel = axes.yaxis.label.get_text()
    
    xdata = axes.get_lines()[0].get_xdata()
    ydata = axes.get_lines()[0].get_ydata()

    if interactive:
        return splinteractive(xdata, ydata, smoothing, degree, presmoothing, spline_class, xlabel, ylabel)
    else:
        return spline_class(xdata, ydata, smoothing, degree, presmoothing, plot, xlabel, ylabel)    



