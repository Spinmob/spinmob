import os as _os
_os.sys.path.append(_os.path.realpath('..'))

from numpy import *
import numpy as _n
import scipy.optimize    as _opt
import pylab             as _pylab
import textwrap          as _textwrap

import _useful_functions as _fun
import _pylab_tweaks     as _pt
import _plot




class fitter():
    
    _f  = None    # list of functions
    _bg = None    # list of background functions (for subtracting etc)    
    
    _f_raw  = None # raw argument passed to set_functions()
    _bg_raw = None # raw argument passed to set_functions() 
    
    xdata  = None # internal storage of data sets
    ydata  = None
    eydata = None
    
    _xdata_massaged  = None # internal storage of trimmed data sets (used for fitting)
    _ydata_massaged  = None
    _eydata_massaged = None
    
    _settings = None   # dictionary containing all the fitter settings
    
    results = None  # full output from the fitter.
    
    def __init__(self, f=['a*x*cos(b*x)+c', 'a*x+c'], p='a=1.5, b, c=-2', c=None, bg=None, **kwargs):
        """
        Creates an object for fitting data to nonlinear curves.

        f  = function or list of functions
        p  = comma-delimited list of fit parameters
        c  = comma-delimited list of constants 
        bg = optional background function or list of functions
        
        f, p, bg are sent to set_functions()
        
        **kwargs are sent to settings
        
        Typical workflow:
            my_fitter = fitter('a*x+b', 'a,b')      # creates the fitter object
            my_fitter.set_data([1,2,3],[1,2,1])     # sets the data to be fit
            my_fitter.fit_leastsq()                 # does the fitting
            my_fitter.plot()
            
        Tips:

            Do not set data directly; use set_data(), which clears the fit 
            results. Otherwise the fit results will not match the existing data.
            
            When errors are completely unknown, try autoscale_errors_and_fit()
            repeatedly until the reduced chi squareds of all the data sets
            are approximately 1. This is one way to more-or-less estimate 
            the error from the data itself.            
        """
        
        # make sure all the awesome stuff from numpy is visible.
        self._globals  = globals()  
        
        self._pnames    = []
        self._cnames    = []
        self._fnames    = []
        self._bgnames   = []
        self._pguess    = []
        self._constants = []       
        
        # default settings
        self._settings = dict(silent        = True,    # if True, no plotting!                        
                              plot_fit      = True,     # include f in plots?
                              plot_bg       = False,    # include bg in plots?
                              plot_ey       = True,     # include error bars?
                              plot_guess    = True,     # include the guess?
                              subtract_bg   = True,     # subtract bg from plots?
                              fpoints       = 1000,     # number of points to use when plotting f
                              xmin          = None,     # list of truncation values
                              xmax          = None,     # list of truncation values
                              coarsen       = 0,        # how much to coarsen the data
                              
                              # styles of plots
                              style_data   = _plot.style(marker='o', color='b', ls=''),
                              style_fit    = _plot.style(marker='', color='r', ls='-'),
                              style_guess  = _plot.style(marker='', color='0.25', ls='-'),
                              style_bg     = _plot.style(marker='', color='k', ls='-'))
        
        # settings that don't require a re-fit
        self._safe_settings =list(['bg_names', 'fpoints', 'f_names',
                                   'plot_bg', 'plot_ey', 'plot_guess', 'plot_fit', 
                                   'silent', 'style_bg', 'style_data', 'style_guess',
                                   'style_fit', 'subtract_bg'])
        
        # settings that should not be lists in general (i.e. not one per data set)
        self._single_settings = list(['silent'])
        
        # set the functions
        self.set_functions(f, p, c, bg)

        # update the default settings
        self.set(**kwargs)
        
        # turn on plot updates
        self['silent'] = False
    

    def set(self, **kwargs):
        """
        Changes a setting or multiple settings. Can also call self() or
        change individual parameters with self['parameter'] = value
        """
        for k in kwargs.keys(): self[k] = kwargs[k]
        return self
    
    
    __call__ = set    
    
    def __setitem__(self, key, value): 

        # special case: setting a _pguess
        if key in self._pnames: self._pguess[self._pnames.index(key)] = value

        # special case: setting a _constants
        elif key in self._cnames: 
            self._constants[self._cnames.index(key)] = value
            self._update_functions()

        # special case: single-valued keys
        elif key in self._single_settings: 
            self._settings[key] = value
            
        # everything else should have a value for each data set or plot
        elif self._settings.has_key(key): 
            
            # make sure it's a list.
            if not _fun.is_iterable(value) or isinstance(value, _plot.style): 
                value = [value]            
            
            # make sure it matches the data.
            while len(value) < len(self._f): value.append(value[0])     
            
            # set the value
            self._settings[key] = value
        
        # yell.        
        else: self._error("'"+key+"' is not a valid setting, pname or cname.")
    
        # if it isn't a "safe" key, invalidate the previous fit results.
        if not key in self._safe_settings: self._clear_results()
            
        
    
    def __repr__(self):
        """
        prints out the current settings.
        """
        keys = self._settings.keys()
        keys.sort()
        
        s = "\nSETTINGS\n"
        for k in keys: s = s+"  {:15s} {:s}\n".format(k, str(self[k]))
        
        s = s + "\nCONSTANTS\n"
        for c in self._cnames: s = s + "  {:10s} = {:s}\n".format(c, str(self[c]))

        s = s + "\nGUESS\n"
        for p in self._pnames: s = s + "  {:10s} = {:s}\n".format(p, str(self[p])) 
        
        if self.xdata==None: s = s + "\nNO DATA\n"
        
        else:
            if self.results and not self.results[1]==None:            
                s = s + "\nFIT RESULTS (reduced chi squared = {:s})\n".format(str(self.reduced_chi_squareds()))
                for n in range(len(self._pnames)): 
                    s = s + "  {:10s} = {:G} +/- {:G}\n".format(self._pnames[n], self.results[0][n], _n.sqrt(self.results[1][n][n]))
            
            elif self.results and self.results[1] == None: 
                s = s + "\nFIT DID NOT CONVERGE\n"
                for n in range(len(self._pnames)): 
                    s = s + "  {:10s} = {:G} (meaningless)\n".format(self._pnames[n], self.results[0][n])
            
            else: s = s + "\nNO FIT RESULTS\n"

        return s
    
    def __getitem__(self, key): 
        if key in self._pnames: return self._pguess   [self._pnames.index(key)]        
        if key in self._cnames: return self._constants[self._cnames.index(key)]                
        return self._settings[key]
      
    def _error(self, message): print "ERROR: "+str(message)

    def set_functions(self,  f=['a*x*cos(b*x)+c', 'a*x+c'], p='a=1.5, b, c=-2', c=None, bg=None):
        """
        Sets the function(s) used to describe the data.

        f='a*cos(b*x)'  This can be a string function, a defined function 
                        my_function(x,a,b), or a list of some combination
                        of these two types of objects. The length of such
                        a list must be equal to the number of data sets 
                        supplied to the fit routine.
        
        p='a=1.5, b'    This must be a comma-separated string list of 
                        parameters used to fit. If an initial guess value is
                        not specified, 1.0 will be used.
                        
                        If a function object is supplied, it is assumed that 
                        this string lists the parameter names in order.
        
        c=None          Fit _constants; like p, but won't be allowed to float 
                        during the fit. This can also be None.
                        
        bg=None         Can be functions in the same format as f describing a 
                        background (which can be subtracted during fits, etc)
        """

        # initialize everything
        self._pnames    = []
        self._cnames    = []
        self._pguess    = []
        self._constants = []
        
        # store these for later
        self._f_raw  = f
        self._bg_raw = bg
        
        # break up the constant names and initial values.
        if c:
            for s in c.split(','):
                
                # split by '=' and see if there is an initial value
                s = s.split('=')
    
                # add the name to the list            
                self._cnames.append(s[0].strip())
    
                # if there is a guess value, add this (or 1.0) 
                if len(s) > 1: self._constants.append(float(s[1]))
                else:          self._constants.append(1.0)
        
        
        # break up the parameter names and initial values.
        for s in p.split(','):
            
            # split by '=' and see if there is an initial value
            s = s.split('=')

            # add the name to the list            
            self._pnames.append(s[0].strip())

            # if there is a guess value, add this (or 1.0)            
            if len(s) > 1: self._pguess.append(float(s[1]))
            else:          self._pguess.append(1.0)
        

        # use the internal settings we just set to create the functions
        self._update_functions()
        return self
        
        
    def _update_functions(self):
        """
        Uses internal settings to update the functions.
        """
        
        self._f      = []
        self._bg     = []
        self._fnames  = []        
        self._bgnames = [] 
               
        f  = self._f_raw
        bg = self._bg_raw             
        
        # make sure f and bg are lists of matching length
        if not _fun.is_iterable(f) : f  = [f]
        if not _fun.is_iterable(bg): bg = [bg]
        while len(bg) < len(f): bg.append(None)        
        
        # get a comma-delimited string list of parameter names
        pstring = _fun.join(self._pnames, ', ')        
        pstring = 'x, ' + pstring
        
        # update the globals for the functions
        # the way this is done, we must redefine the functions
        # every time we change a constant
        for cname in self._cnames: self._globals[cname] = self[cname]
        
        # loop over all the functions and create the master list
        for n in range(len(f)):
        
            # if f[n] is a string, define a function on the fly.
            if isinstance(f[n], str): 
                self._f.append( eval('lambda ' + pstring + ': ' + f[n],  self._globals))
                self._fnames.append(f[n])
            else:                     
                self._f.append(f[n])
                self._fnames.append(f[n].__name__)
            
            # if bg[n] is a string, define a function on the fly.
            if isinstance(bg[n], str): 
                self._bg.append(eval('lambda ' + pstring + ': ' + bg[n], self._globals))
                self._bgnames.append(bg[n])
            else:                      
                self._bg.append(bg[n])
                if bg[n] == None: self._bgnames.append("None")
                else:             self._bgnames.append(bg[n].__name__)
        
        # update the format of all the settings
        for k in self._settings.keys(): self[k] = self[k]        
        
        # make sure we don't think our fit results are valid!        
        self._clear_results()
    
    
    def set_data(self, xdata=[1,2,3,4,5], ydata=[[1,2,1,2,1],[3,2,3,4,3]], eydata=None, plot=True):
        """
        This will handle the different types of supplied data and put everything
        in a standard format for processing.
        
        xdata, ydata      These can be a single array of data or a list of data
                            arrays. If one is an array# assemble the arguments for the function
        args = (xdata,) + tuple(p)    and the other is a list
                            of arrays, copies of the first will be made to pair
                            with the other's data. Their lengths must match.
                            
        eydata             Error bars. These can be None (for auto error) or 
                            data matching the dimensionality of xdata and ydata

        Results will be stored in self.xdata, self.ydata, self.eydata
        """
        
        # make sure xdata and ydata are lists of data sets
        if not _fun.is_iterable(xdata[0]): xdata = [xdata]
        if not _fun.is_iterable(ydata[0]): ydata = [ydata]
        
        # make sure these lists are the same length
        while len(ydata) < len(xdata): ydata.append(ydata[0])
        while len(xdata) < len(ydata): xdata.append(xdata[0])
        
        # poop out of the number of ydata sets doesn't match the number of
        # functions
        if not len(ydata) == len(self._f):
            return self._error("Naughty! There are more data sets than functions! If you want to fit many data sets simultaneously with one function, make a list of duplicated functions in set_functions().")
        
        # assemble the errors
        # example eydata: None, [1,2,1,2,1], or [None, [1,2,1,2,1]]
        if not _fun.is_iterable(eydata):    eydata = [eydata]
        if not _fun.is_iterable(eydata[0]): eydata = [eydata]        
        
        # make sure the lengths match        
        # example eydata: [None], [1,2,1,2,1], or [None, [1,2,1,2,1]]
        while len(eydata) < len(ydata): eydata.append(eydata[0])
        
        # make sure everything is a list of numpy arrays
        for n in range(len(xdata)):
            
            xdata[n]  = _n.array( xdata[n]) *1.0
            ydata[n]  = _n.array( ydata[n]) *1.0
            
            # take a reasonable guess at the error
            if eydata[n] == [None] or eydata == None: 
                eydata[n] = _n.ones(len(xdata[n])) * (max(ydata[n])-min(ydata[n]))/20.
            
            # use constant error bars            
            elif _fun.is_a_number(eydata[n]):
                eydata[n] = _n.ones(len(xdata[n])) * eydata[n]
            
            eydata[n] = _n.array(eydata[n]) *1.0
        
        # store the data and errors internally
        self.xdata  = xdata
        self.ydata  = ydata
        self.eydata = eydata
        
        # reset the massaged data
        self._xdata_massaged  = xdata
        self._ydata_massaged  = ydata
        self._eydata_massaged = eydata

        # make sure we don't think our fit results are valid!
        self._clear_results()
        
        # plot if not in silent mode
        if not self['silent'] and plot: self.plot()
    
        return self    
    
    def _massage_data(self):
        """
        This will trim and coarsen the data sets according to self._settings:
            coarsen = 0     # can be an integer
            xmin    = None  # can be a number
            xmax    = None  # can be a number
            
        Results are stored in self._xdata_massaged, ...
        """
        
        self._xdata_massaged  = []
        self._ydata_massaged  = []
        self._eydata_massaged = []        
        
        N = 0 # total number of data points
        
        for n in range(len(self.xdata)):
            
            # trim the data
            x, y, ey = _fun.trim_data(self['xmin'][n], self['xmax'][n], 
                                      self.xdata[n], self.ydata[n], self.eydata[n])
            
            # coarsen the data
            x  = _fun.coarsen_array(x,  self['coarsen'][n], 'average')
            y  = _fun.coarsen_array(y,  self['coarsen'][n], 'average')
            ey = _fun.coarsen_array(ey, self['coarsen'][n], 'quadrature')

            # store the result
            self._xdata_massaged.append(x)
            self._ydata_massaged.append(y)
            self._eydata_massaged.append(ey)
            
            # keep track of the number of data points
            N += len(x)


    
    def fit(self, pguess=None, method='leastsq', **kwargs):
        """
        This will try to determine fit parameters using scipy.optimize's leastsq
        algorithm. This function relies on a previous call of set_data()
        
        pguess        If None, this will set the internal guess values
        
        results of the fit are stored in self.results        
        
        kwargs are sent to self.set()
        """
        if self.xdata == None or self.ydata == None: 
            self._error("No data. Please use set_data() prior to fitting.")
        
        self.set(**kwargs)
        
        # massage the data
        self._massage_data()                
        
        # set the initial values if specified
        if not pguess == None: self._pguess = pguess
        
        # do the actual optimization
        self.results = _opt.leastsq(self._residuals_concatenated, self._pguess, full_output=1)
    
        # plot if necessary
        if not self['silent']: self.plot()
        
        return self
    
    def fix(self, pname):
        """
        Turns a parameter in to a constant.
        """
        if not pname in self._pnames: 
            self._error("Naughty. '"+pname+"' is not a valid fit parameter name.")
            return

        n = self._pnames.index(pname)
        
        # use the fit result if it exists
        if self.results: value = self.results[0][n]

        # otherwise use the guess value
        else: value = self._pguess[n]
    
        # make the switcheroo
        self._pnames.pop(n)
        self._pguess.pop(n)            
        self._constants.append(value)
        self._cnames.append(pname)
        
        # update
        self._update_functions()        

        return self        
        
    def free(self, cname):
        """
        Turns a constant into a parameter.
        """
        if not cname in self._cnames: 
            self._error("Naughty. '"+cname+"' is not a valid constant name.")
            return

        n = self._cnames.index(cname)
        
        # make the switcheroo
        self._pnames.append(self._cnames.pop(n))
        self._pguess.append(self._constants.pop(n))            
        
        # update
        self._update_functions()     
    
        return self
    
    def _clear_results(self):
        """
        Removes any fit results that may be lingering.
        """
        self.results = None
        
    def _evaluate_all_functions(self, xdata, p=None):
        """
        This returns a list of function outputs given the stored data sets.
        This function relies on a previous call of set_data().
        
        p=None means use the fit results
        """
        if p==None: p = self.results[0]
        
        output = []
        for n in range(len(self._f)): 
            output.append(self._evaluate_f(n, self._xdata_massaged[n], p) )

        return output

    def _evaluate_f(self, n, xdata, p=None):
        """
        Evaluates a single function n for arbitrary xdata and p.
        
        p=None means use the fit results
        """
        if p==None: p = self.results[0]
        
        # assemble the arguments for the function
        args = (xdata,) + tuple(p)                        
    
        # evaluate this function.            
        return self._f[n](*args) 
    
    def _evaluate_bg(self, n, xdata, p=None):
        """
        Evaluates a single background function n for arbitrary xdata and p.
        
        p=None means use the fit results
        """
        if p==None: p = self.results[0]
        
        # evaluate this function.            
        if self._bg[n] == None: return None
        
        # assemble the arguments for the function
        args = (xdata,) + tuple(p)   
        return self._bg[n](*args) 
    
    def _residuals(self, p=None):
        """
        This function returns a list of vectors of the differences between the
        model and ydata_massaged, scaled by the error. This function relies 
        on a previous call to set_data().
        
        p=None means use the fit results
        """
        if p==None: 
            if not self.results:
                self._error("Can't call _residuals(None) without a fit result.")
                return
            p = self.results[0]
        
        # evaluate the function for all the data, returns a list!
        f = self._evaluate_all_functions(self._xdata_massaged, p)

        # get the full residuals list
        r = []
        for n in range(len(f)): 
            r.append((self._ydata_massaged[n]-f[n]) / _n.absolute(self._eydata_massaged[n]))
        return r

    def _residuals_concatenated(self, p=None):
        """
        This function returns a big long list of residuals so leastsq() knows
        what to do with it. This function relies on a previous call to set_data()
        
        p=None means use the fit results
        """
        if p==None: p = self.results[0]
        return _n.concatenate(self._residuals(p))

    def _chi_squareds(self, p=None):
        """
        returns a list of chi squared for each data set. Also uses ydata_massaged.
        
        p=None means use the fit results
        """
        if p==None: p = self.results[0]
        
        # get the residuals
        rs = self._residuals(p)
        
        # square em and sum em.        
        cs = []
        for r in rs: cs.append(sum(r**2))
        return cs
    
    def reduced_chi_squared(self,p=None):
        """
        returns the reduced chi squared given p.
        
        p=None means use the fit results.
        """
        r = self._residuals_concatenated(p)
        return sum(r**2) / (len(r)-len(self._pnames))

    def reduced_chi_squareds(self, p=None):
        """
        Returns the reduced chi squared for each data set. Degrees of freedom
        of each data point are reduced.
        
        p=None means use the fit results.
        """
        if p==None: p = self.results[0]
        r = self._residuals(p)
        
        # degrees of freedom
        dof_per_point = 1.0*(_n.size(r)-len(self._pnames))/_n.size(r)
        
        for n in range(len(r)):
            r[n] = sum(r[n]**2)/(len(r[n])*dof_per_point)
        
        return r

    def autoscale_eydata(self):
        """
        Rescales the error so the next fit will give reduced chi squareds of 1.
        
        Each data set will be scaled independently. 
        """
        if not self.results: 
            self._error("You must complete a fit first.")
        
        r = self.reduced_chi_squareds()

        # loop over the eydata and rescale        
        for n in range(len(r)):
            self.eydata[n] = self.eydata[n] * _n.sqrt(r[n])

        # the fit is no longer valid
        self._clear_results()
        
        # replot
        if not self['silent']: self.plot()

        return self
        
    def autoscale_eydata_and_fit(self):
        """
        Shortcut to 
        
        >>> self.autoscale_eydata()
        >>> self.fit_leastsq(_pguess=self.results[0])
        """
        if not self.results: 
            self._error("You must complete a fit first.")

        # use the fit as a guess        
        self._pguess = self.results[0]
        
        self.autoscale_eydata()
        self.fit(pguess=self._pguess)
        return self

    def plot(self, p=None, **kwargs):
        """
        This will plot the data (with error) for inspection.
        
        p = None    Specifying p will         
        
        kwargs are sent to self.set()
        """
        if self.xdata == None or self.ydata == None: 
            self._error("No data. Please use set_data() prior to plotting.")
            return 
        
        self.set(**kwargs)        
        
        # update the massaged data
        self._massage_data()
        
        # turn off interactive mode        
        _pylab.ioff()
        
        # get the residuals
        r = None
        if not self.results==None: r = self._residuals(self.results[0])       
        
        # make a new plot for each data set
        for n in range(len(self.xdata)):
            
            # get the next figure
            fig = _pylab.figure(n)
            fig.clear()
            
            # set up two axes. One for data and one for residuals.
            a1 = _pylab.subplot(211)
            a2 = _pylab.subplot(212, sharex=a1)
            a1.set_position([0.15, 0.75, 0.75, 0.15])
            a2.set_position([0.15, 0.15, 0.75, 0.55])
            
            # get the xdata for the curves
            if self['fpoints'][n] == None: 
                x = self._xdata_massaged[n]
            else:                        
                x = _n.linspace(min(self._xdata_massaged[n]), 
                                max(self._xdata_massaged[n]), 
                                self['fpoints'][n])
           
            # get the thing to subtract from ydata
            if self['subtract_bg'] and not self._bg[n]==None:
                
                # if we have a fit, use that.
                if self.results:
                    dy_data = self._evaluate_bg(n, self._xdata_massaged, self.results[0])
                    dy_func = self._evaluate_bg(n, x,                   self.results[0])

                # otherwise, use the _pguess background
                else:          
                    dy_data = self._evaluate_bg(n, self._xdata_massaged, self._pguess)
                    dy_func = self._evaluate_bg(n, x,                   self._pguess)
            else:
                dy_data = 0*self._xdata_massaged[n]
                dy_func = 0*x
            
            
            # add the data to the plot
            if self['plot_ey'][n]: 
                a2.errorbar(self._xdata_massaged[n], 
                            self._ydata_massaged[n]-dy_data, 
                            self._eydata_massaged[n], 
                            **self['style_data'][n].next())
            else:               
                a2.plot(    self._xdata_massaged[n], 
                            self.ydata_massage[n]-dy_data,                           
                            **self['style_data'][n].next())
            
            # add the _pguess curves
            if self['plot_guess'][n]:
                
                # plot the _pguess background curve                
                if self['plot_bg'][n]:
                    a2.plot(x, self._evaluate_bg(n,x,self._pguess)-dy_func, **self['style_guess'][n].next()) 
             
                # plot the _pguess main curve
                a2.plot(x, self._evaluate_f(n,x,self._pguess)-dy_func, **self['style_guess'][n].next())
             
            # add the fit curves (if we have a fit)
            if self['plot_fit'] and self.results:
                
                # plot the background curve
                if self['plot_bg'][n]:
                    a2.plot(x, self._evaluate_bg(n,x,self.results[0])-dy_func, **self['style_fit'][n].next())
                
                # plot the pfit main curve
                a2.plot(x, self._evaluate_f(n,x,self.results[0])-dy_func, **self['style_fit'][n].next())
            
            
            
            # plot the residuals
            if not r==None: 
                a1.errorbar(self._xdata_massaged[n], r[n], _n.ones(len(r[n])), **self['style_data'][n].next())           
                a1.plot([min(self._xdata_massaged[n]),max(self._xdata_massaged[n])],[0,0], **self['style_fit'][n].next())
                
            # tidy up
            _pt.auto_zoom(axes=a1, draw=False)
            _pt.auto_zoom(axes=a2, draw=False)
            _pylab.xlabel('xdata['+str(n)+']')
            _pylab.ylabel('ydata['+str(n)+']')
            a1.set_ylabel('residuals')

            # Assemble the title  
            wrap = 80
            indent = '      '
            t = _textwrap.fill('Function ('+str(n)+'/'+str(len(self.ydata)-1)+'): y = '+self._fnames[n], wrap, subsequent_indent=indent)
            
            if len(self._cnames):
                t1 = "Constants: "                
                for i in range(len(self._cnames)):
                    t1 = t1 + self._cnames[i] + "={:G}, ".format(self._constants[i])
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)
            
            if self.results and not self.results[1]==None:
                t1 = "Fit: "                
                for i in range(len(self._pnames)):
                    t1 = t1 + self._pnames[i] + "={:G}$\pm${:G}, ".format(self.results[0][i], _n.sqrt(self.results[1][i][i]))
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)
                
            elif self.results:
                t1 = t1 + "Fit did not converge: "
                for i in range(len(self._pnames)):
                    t1 = t1 + self._pnames[i] + "={:8G}$, "
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)
                
            a1.set_title(t, fontsize=10, ha='left', position=(0,1))

            _pt.set_figure_window_geometry('gcf',[0,0],[550,670])       
       
        # turn back to interactive and show the plots.
        _pylab.ion()
        _pylab.draw()
        _pylab.show()
        
        # for some reason, it's necessary to touch every figure, too
        for n in range(len(self.xdata)-1,-1,-1): _pylab.figure(n)  
        
        return self

    def trim(self, n='all'):
        """
        This will set xmin and xmax based on the current zoom-level of the
        figures.
        
        n='all'     Which figure to use for setting xmin and xmax.
                    'all' means all figures. You may also specify a list.
        """
        if self.xdata == None or self.ydata == None: 
            self._error("No data. Please use set_data() and plot() prior to trimming.")
            return
                
        
        if   _fun.is_a_number(n): n = [n]
        elif isinstance(n,str):   n = range(len(self.xdata))
        
        # loop over the specified plots
        for i in n:
            try:    
                xmin, xmax = _pylab.figure(i).axes[1].get_xlim()
                self['xmin'][i] = xmin
                self['xmax'][i] = xmax                
            except: 
                self._error("Data "+str(i)+" is not currently plotted.")
        
        # now show the update.
        self._clear_results()
        if not self['silent']: self.plot()    
    
        return self    
    
    def zoom(self, n='all', factor=2.0):
        """
        This will scale the x range of the chosen plot.
        
        n='all'     Which figure to zoom out. 'all' means all figures, or 
                    you can specify a list.         
        """
        if self.xdata == None or self.ydata == None: 
            self._error("No data. Please use set_data() and plot() prior to zooming.")
            return
        
        if   _fun.is_a_number(n): n = [n]
        elif isinstance(n,str):   n = range(len(self.xdata))
        
        # loop over the specified plots
        for i in n:
            try:  
                xmin, xmax = _pylab.figure(i).axes[1].get_xlim()
                xc = 0.5*(xmin+xmax)
                xs = 0.5*abs(xmax-xmin)
                self['xmin'][i] = xc - factor*xs
                self['xmax'][i] = xc + factor*xs
            except: 
                self._error("Data "+str(i)+" is not currently plotted.")
        
        # now show the update.
        self._clear_results()
        if not self['silent']: self.plot()
    
        return self    
    
    def ginput(self, figure_number=0, **kwargs):
        """
        Pops up the n'th figure and lets you click it. Returns value from pylab.ginput().
        
        args and kwargs are sent to pylab.ginput()
        """
        _pt.raise_figure_window(figure_number)
        return _pylab.ginput(**kwargs)
        

#f = su.fit.fitter('a*exp(-x/b)+c', 'a=1, b=10e-6, c=0'); d = su.data.load(); f['a']=max(d[0]-min(d[0])); f['c']=d[0][-1]; f.set_data(d[1],d[0])
    
######################
## Example Code
######################
if __name__ == '__main__': 
    f = fitter('a*b*x+c', 'a,c', 'b=2')
    f.set_data([1,2,3,4,5,6,7],[1,2,1,3,1,4,2])
    f(b=1).plot()    
    print f.fit()
    
