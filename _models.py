import os
import scipy as _scipy
import scipy.optimize    # don't listen to spyder. 

import numpy as _n
import pylab as _pylab
from matplotlib.font_manager import FontProperties as _FontProperties
import spinmob as _s
import _dialogs

_st = _s.plot.tweaks

import _functions as _fun
import wx as _wx


# This is completely a hack, but it works very well. I'd like to rewrite this as
#
# 1. a class-based object to interact with on the command line (so no input loop)
# 2. something that can handle multiple functions or a single function with 
#    multiple outputs (i.e. returning an array)
# 3. something more general? No need for "x"? Something that can handle many
#    parameters, only some of which are fit (specified by you)?



#
# Classes
#
class model_base:

    # this is something the derived classes must do, to define
    # their fit variables
    pnames          = []
    function_string = None
    D               = None
    
    # this function just creates a p0 array based on the size of the pnames array
    def __init__(self):
        # get a numpy array and then resize it
        self.p0     = _n.array([])
        self.p0.resize(len(self.pnames))

    def __call__(self, p, x):
        self.evaluate(p,x)

    # This function is to be overridden.
    # this is where you define the shape of your function
    # in terms of parameters p at value x
    def evaluate(self, p, x): return(p[0]*0.0*x) # example

    # this is another overridden function
    # used to get just the bacgkround, given p and value x
    def background(self, p, x): return(p[0]*0.0*x) # example

    # this is another overridden function
    # use this to guess the intial values p0 based on data
    # xbi1 and 2 are the indices used to estimate the background
    def guess(self, xdatas, ydatas, xbi1=0, xbi2=-1):
        # first get the appropriate size array
        p=self.p0
        p[0] = xdatas[0][xbi2] # example
        self.write_to_p0(p)
        return


    #
    #
    #  These functions are generally not overwritten
    #
    #

    def optimize(self, xdatas, ydatas, eydatas, p0="internal"):
        """
        This actually performs the optimization on xdata and ydata.
        p0="internal"   is the initial parameter guess, such as [1,2,44.3].
                        "internal" specifies to use the model's internal guess result
                        but you better have guessed!
        returns the fit p from scipy.optimize.leastsq()
        """
        if p0 == "internal": p0 = self.p0
        if self.D == None: return _scipy.optimize.leastsq(self.residuals_concatenated, p0, args=(xdatas,ydatas,eydatas,), full_output=1)
        else:              return _scipy.optimize.leastsq(self.residuals_concatenated, p0, args=(xdatas,ydatas,eydatas,), full_output=1, Dfun=self.jacobian, col_deriv=1)

    def residuals(self, p, xdatas, ydatas, eydatas):
        """
        This function returns a list of vectors of the differences between the
        model and ydata, scaled by the error
        """

        # evaluate the function for all the data, returns a list!
        f = self.evaluate(p,xdatas)

        # get the full residuals list
        rs = []
        for n in range(len(xdatas)): rs.append((ydatas[n]-f[n])/_n.absolute(eydatas[n]))
        return rs

    def residuals_concatenated(self, p, xdatas, ydatas, eydatas):
        """
        This function returns a big long list of residuals so leastsq() knows
        what to do with it.
        """
        return _n.concatenate(self.residuals(p, xdatas, ydatas, eydatas))


    def residuals_variance(self, p, xdatas, ydatas, eydatas):
        """
        This returns a list of the variance of the residuals, or chi^2/DOF.
        """

        # get the chi^2 list
        c2s = self.chi_squared(p, xdatas, ydatas, eydatas)

        # get the number of data points
        N = 1.0 * len(_n.concatenate(xdatas))

        # get the degrees of freedom
        dof = 1.0*len(p)

        # get the reduced chi squareds assuming the parameters are
        # weighted evenly among the individual data points
        rc2s = []
        for n in range(len(c2s)):
            weight = 1.0*len(xdatas[n]) / N                     # fraction of total data points
            rc2s.append(c2s[n] / (len(xdatas[n])-weight*dof))   # chi^2 / dof
        return rc2s

    def chi_squared(self, p, xdatas, ydatas, eydatas):
        """
        This returns a list of numbers that are the chi squareds for the
        given set of parameters p

        This is currently not in use for the optimization.  That uses residuals.
        """

        rs = self.residuals(p, xdatas, ydatas, eydatas)
        c2s = []
        for r in rs: c2s.append(sum(r*r))

        return c2s

    # this returns the jacobian given the xdata.  Derivatives across rows, data down columns.
    # (so jacobian[len(xdata)-1] is len(p) wide)
    def jacobian(self, p, xdata, ydata):
        """
        This returns the jacobian of the system, provided self.D is defined
        """

        if not type(p)     == type(_n.array([0])): p     = _n.array(p)
        if not type(xdata) == type(_n.array([0])): xdata = _n.array(xdata)

        return self.D(p,xdata)


    def set_parameter(self, name, value):
        """
        This functions sets a parameter named "name" to a value.
        """

        try:
            # if we enter something like "min=x", get a click from the user
            if value in ['x','y']:
                # get the click
                print "Please click somewhere to get the "+value+" value."
                _st.raise_figure_window()
                click = _pylab.ginput()

                # use the click value.
                if    len(click)>0 and value=='x': value = click[0][0]
                elif  len(click)>0 and value=='y': value = click[0][1]
                else:
                    print "\nCLICK ABORTED.\n"
                    return

            elif value in ['dx', 'dy', 'slope']:
                # get two clicks
                print "Please click twice to use the "+value+" value."
                _st.raise_figure_window()
                clicks = _pylab.ginput(2)

                # make sure we got two clicks
                if len(clicks) == 2:
                    dx = clicks[1][0]-clicks[0][0]
                    dy = clicks[1][1]-clicks[0][1]
                    if value=='dx': value = dx
                    if value=='dy': value = dy
                    if value=='slope': value = dy/dx

                else:
                    print "\nCLICKS ABORTED.\n"
                    return


            i = self.pnames.index(name)
            self.p0[i] = float(value)
            return True

        except:
            print "ERROR:", name, "is not a valid variable or", value, "is not a valid value."
            return False

    def write_to_p0(self, p):
        """
        This function checks p's against a possible
        variable self.already_guessed and stores only those
        not in already_guessed.
        """

        try:
            # loop over all the p0's, storing p's if necessary
            for n in range(0, len(self.p0)):
                # if the pname of this p0 is not on the guessed list
                print self.pnames[n]+"POOP"+str(self.guessed_list.index(self.pnames[n]))
                if self.guessed_list.index(self.pnames[n])<0:
                    self.p0[n] = p[n]
        except: # an error occurred, likely due to no guessed_list
            self.p0 = p






    ######################################
    ## Interactive fitting routine
    ######################################

    def fit(self, data, command="", settings={}):
        """
        This generates xdata, ydata, and eydata from the three scripts
        (or auto-sets the error and updates it depending on the fit),
        fits the data, stores the results (and scripts) in the data file's header
        and saves the data in a new file.

        data            instance of a data class
        command         initial interactive fit command
        interactive     set to False to automatically fit without confirmation
        """

        iterable_settings = ["min", "max", "xb1", "xb2", "auto_error", "subtract",
                             "smooth", "coarsen", "show_guess", "show_error",
                             "show_background", "plot_all", "xscript", "yscript",
                             "eyscript"]

        # dictionary of settings like "min" and "skip"
        default_settings = {"min"               : None,
                            "max"               : None,
                            "xb1"               : 0,
                            "xb2"               : -1,
                            "auto_error"        : False,
                            "subtract"          : False,
                            "smooth"            : 0,
                            "coarsen"           : 0,
                            "show_guess"        : False,
                            "show_error"        : True,
                            "show_background"   : True,
                            "plot_all"          : False,
                            "eyscript"          : None,
                            "output_path"       : None,
                            "output_columns"    : None,

                            "skip"              : True,
                            "guess"             : None,
                            "save_file"         : True,
                            "file_tag"          : 'fit_',
                            "figure"            : 0,
                            "autofit"           : False,
                            "fullsave"          : False,
                            }
        if not settings.has_key('eyscript'): default_settings["auto_error"] = True

        # fill in the non-supplied settings with defaults
        for k in default_settings.keys():
            if not k in settings.keys():
                settings[k] = default_settings[k]

        # determine the number of parallel fits from the yscript
        if _s.fun.is_iterable(settings['yscript']): number_of_fits = len(settings['yscript'])
        else:                                       number_of_fits = 1

        # In general we're going to have a list of datas and scripts etc, so make
        # sure we're in a position to do this.
        if not _s.fun.is_iterable(data): data = [data]

        # fill out the arrays so they match the number of fits
        while len(data) < number_of_fits: data.append(data[-1])

        # make sure the various settings are lists too
        for k in iterable_settings:

            # make them all iterable
            if not _s.fun.is_iterable(settings[k]):
                settings[k] = [settings[k]]

            # make sure they're all the right length
            while len(settings[k]) < number_of_fits: settings[k].append(settings[k][-1])

        # Initialize the fit_parameters (we haven't any yet!)
        fit_parameters = None
        fit_errors     = None
        
        format_figures = True

        # set up the figures
        axes2s = []
        axes1s = []
        figs  = []
        for n in range(len(data)):
            figs.append(_pylab.figure(settings["figure"]+n))
            figs[n].clear()
            axes2s.append(_pylab.subplot(211))
            axes1s.append(_pylab.subplot(212, sharex=axes2s[n]))
            axes2s[n].set_position([0.15, 0.78, 0.70, 0.13])
            axes1s[n].set_position([0.15, 0.08, 0.70, 0.64])

        # Now keep trying to fit until the user says its okay or gives up.
        hold_plot=False
        while True:

            # Plot everything.
            if hold_plot:
                hold_plot=False
            else:
                if settings["skip"]: print "Plotting but not optimizing... (<enter> to fit)"
                else:                print "Beginning fit routine..."

                # assemble all the data
                xdatas  = []
                ydatas  = []
                eydatas = []
                xs      = []
                ys      = []
                eys     = []
                for n in range(len(data)):
                    # get the data based on the scripts
                    xdatas.append(data[n](settings["xscript"][n]))
                    ydatas.append(data[n](settings["yscript"][n]))
                    if settings["eyscript"][n] == None: eydatas.append(xdatas[n]*0.0 + (max(ydatas[n])-min(ydatas[n]))/20.0)
                    else:                               eydatas.append(data[n](settings["eyscript"][n]))

                    # now sort the data in case it's jaggy!
                    matrix_to_sort = _n.array([xdatas[n], ydatas[n], eydatas[n]])
                    sorted_matrix  = _fun.sort_matrix(matrix_to_sort, 0)
                    xdatas[n]  = sorted_matrix[0]
                    ydatas[n]  = sorted_matrix[1]
                    eydatas[n] = sorted_matrix[2]

                    # now trim all the data based on xmin and xmax
                    xmin = settings["min"][n]
                    xmax = settings["max"][n]
                    if xmin==None: xmin = min(xdatas[n])-1
                    if xmax==None: xmax = max(xdatas[n])+1
                    [x, y, ey] = _fun.trim_data(xdatas[n], ydatas[n], eydatas[n], [xmin, xmax])

                    # smooth and coarsen
                    [x,y,ey] = _fun.smooth_data( x,y,ey,settings["smooth"][n])
                    [x,y,ey] = _fun.coarsen_data(x,y,ey,settings["coarsen"][n])

                    # append to the temporary trimmed data sets.
                    xs.append(x)
                    ys.append(y)
                    eys.append(ey)



                # now do the first optimization. Start by guessing parameters from
                # the data's shape. This writes self.p0
                if settings["guess"]==None:
                    self.guess(xs, ys, settings["xb1"], settings["xb2"])
                else:
                    self.write_to_p0(settings['guess'])

                print "\n  FUNCTION:"
                for s in self.function_string:
                    print "    "+s
                print "\n  GUESS:"
                for n in range(len(self.pnames)):
                    print "    "+self.pnames[n]+" = "+str(self.p0[n])
                print


                # now do the first optimization
                if not settings["skip"]:

                    # actually do the least-squares optimization
                    fit_output = self.optimize(xs, ys, eys, self.p0)

                    # optimize puts out a float if there's only one parameter. Annoying.
                    if not _s.fun.is_iterable(fit_output[0]):
                            fit_parameters = _n.array([fit_output[0]])
                    else:   fit_parameters = fit_output[0]

                    # If we're doing auto error, now we should scale the error so that
                    # the reduced xi^2 is 1
                    if settings["auto_error"]:

                        # guess the correction to the y-error we're fitting (sets the reduced chi^2 to 1)
                        rms = _n.sqrt(self.residuals_variance(fit_parameters,xs,ys,eys))
                        print "  initial reduced chi^2 =", list(rms**2)
                        print "  scaling errors by", list(rms), "and re-optimizing..."
                        for n in range(len(eys)):
                            eys[n]     = rms[n] * eys[n]
                            eydatas[n] = rms[n] * eydatas[n]

                        # optimize with new improved errors, using the old fit to start
                        fit_output = self.optimize(xs,ys,eys,p0=fit_parameters)

                        # optimize puts out a float if there's only one parameter. Annoying.
                        if not _s.fun.is_iterable(fit_output[0]):
                              fit_parameters = _n.array([fit_output[0]])
                        else: fit_parameters = fit_output[0]

                    # Now that the fitting is done, show the output

                    # grab all the information from fit_output
                    fit_covariance = fit_output[1]
                    fit_reduced_chi_squared = list(self.residuals_variance(fit_parameters,xs,ys,eys))
                    if not fit_covariance == None:
                        # get the error vector and correlation matrix from (scaled) covariance
                        [fit_errors, fit_correlation] = _fun.decompose_covariance(fit_covariance)
                    else:
                        print "  WARNING: No covariance matrix popped out of model.optimize()"
                        fit_errors      = fit_parameters
                        fit_correlation = None

                    print "  reduced chi^2 is now", fit_reduced_chi_squared

                    # print the parameters
                    print "\n  FUNCTION:"
                    for s in self.function_string:
                        print "    "+s
                    print "\n  FIT:"
                    for n in range(0,len(self.pnames)): print "    "+self.pnames[n]+" =", fit_parameters[n], "+/-", fit_errors[n]
                    print


                # get the data to plot and plot it.
                for n in range(len(axes1s)):

                    if settings["plot_all"][n]:
                        x_plot  = xdatas[n]
                        y_plot  = ydatas[n]
                        ey_plot = eydatas[n]
                        [x_plot, y_plot, ey_plot] = _fun.smooth_data (x_plot, y_plot, ey_plot, settings["smooth"][n])
                        [x_plot, y_plot, ey_plot] = _fun.coarsen_data(x_plot, y_plot, ey_plot, settings["coarsen"][n])

                    else:
                        # this data is already smoothed and coarsened before the fit.
                        x_plot  = xs[n]
                        y_plot  = ys[n]
                        ey_plot = eys[n]

                    # now plot everything

                    # set up the axes
                    axes1 = axes1s[n]
                    axes2 = axes2s[n]
                    _pylab.hold(True)
                    axes1.clear()
                    axes2.clear()

                    # by default, the thing to subtract is 0.
                    thing_to_subtract = y_plot*0.0

                    # get the fit data if we're supposed to so we can know the thing to subtract
                    if not fit_parameters==None:
                        # get the fit and fit background for plotting (so we can subtract it!)
                        y_fit            = self.evaluate  (fit_parameters, x_plot, n)
                        y_fit_background = self.background(fit_parameters, x_plot, n)
                        if settings["subtract"][n]: thing_to_subtract = y_fit_background

                    # plot the guess
                    if settings["show_guess"][n]:
                        y_guess = self.evaluate(self.p0, x_plot, n)
                        axes1.plot(x_plot, y_guess-thing_to_subtract, color='gray', label='guess')
                        if settings["show_background"]:
                            y_guess_background = self.background(self.p0, x_plot, n)
                            axes1.plot(x_plot, y_guess_background-thing_to_subtract, color='gray', linestyle='--', label='guess background')

                    # Plot the data
                    if settings["show_error"][n]:
                        axes1.errorbar(x_plot, y_plot-thing_to_subtract, ey_plot, linestyle='', marker='D', mfc='blue', mec='w', ecolor='b', label='data')
                    else:
                        axes1.plot(    x_plot, y_plot-thing_to_subtract,              linestyle='', marker='D', mfc='blue', mec='w', label='data')

                    # plot the fit
                    if not fit_parameters == None and not settings["skip"]:
                        axes1.plot(    x_plot, y_fit-thing_to_subtract,            color='red', label='fit')
                        if settings["show_background"][n]:
                            axes1.plot(x_plot, y_fit_background-thing_to_subtract, color='red', linestyle='--', label='fit background')

                        # plot the residuals in the upper graph
                        axes2.errorbar(x_plot, (y_plot-y_fit)/ey_plot, ey_plot*0.0+1.0, linestyle='',  marker='o', mfc='blue', mec='w', ecolor='b')
                        axes2.plot    (x_plot, 0*x_plot,                                linestyle='-', color='k')

                    # come up with a title
                    title1 = data[n].path

                    # second line of the title is the model
                    title2 = "eyscript="+str(settings["eyscript"][n])+", model: " + str(self.function_string[n])

                    # third line is the fit parameters
                    title3 = ""
                    if not settings["skip"] and not fit_parameters==None:
                        t = []
                        for i in range(0,len(self.pnames)):
                            t.append(self.pnames[i]+"=%.4g+/-%.2g" % (fit_parameters[i], fit_errors[i]))
                        title3 = title3+_fun.join(t[0:4],", ")
                        if len(t)>3: title3 = title3+'\n'+_fun.join(t[4:],", ")
                    else:
                        title3 = title3+"(no fit performed)"

                    # Start by formatting the previous plot
                    axes2.set_title(title1+"\n"+title2+"\nFit: "+title3)
                    axes1.set_xlabel(settings["xscript"][n])
                    axes1.set_ylabel(settings["yscript"][n])

                    # set the position of the legend
                    axes1.legend(loc=[1.01,0], borderpad=0.02, prop=_FontProperties(size=7))

                    # set the label spacing in the legend
                    axes1.get_legend().labelsep = 0.01

                    # set up the title label
                    axes2.title.set_horizontalalignment('right')
                    axes2.title.set_size(8)
                    axes2.title.set_position([1.0,1.010])

                    fig = _pylab.figure(axes1.get_figure().number)
                    if format_figures: _st.format_figure(fig)
                    _st.auto_zoom(axes1)
                    _pylab.draw()
                    _wx.Yield()
            
            format_figures = False
            
            _st.raise_figure_window()
            _wx.Yield()
            _st.raise_pyshell()

            # the only way we optimize is if we hit enter.
            if settings["autofit"]: settings["skip"] = False
            else:                   settings["skip"] = True








            # If last command is None, this is the first time. Parse the initial
            # command but don't ask for one.
            if command == "":
                if len(settings['min'])==1: print "min=" + str(settings['min'][0]) + "\nmax="+str(settings['max'][0])
                else                      : print "min=" + str(settings['min'])    + "\nmax="+str(settings['max'])

                if settings["autofit"]:
                    if fit_parameters==None:    command = ""
                    else:                       command = "y"
                else:
                    command = raw_input("-------> ").strip()

            clower = command.lower().strip()




            
            # first check and make sure the command isn't one of the simple ones
            if clower in ['']:
                settings["skip"] = False

            elif clower in ['h', 'help']:
                print
                print "COMMANDS"
                print "  <enter>    Run the fit or do more iterations."
                print "  g          Guess and show the guess."
                print "  o          Choose and output summary file."
                print "  n          No, this is not a good fit. Move on."
                print "  p          Call the printer() command."
                print "  q          Quit."
                print "  u          Same as 'y' but use fit as the next guess."
                print "  t          Just transfer these fit results to the guess."
                print "  y          Yes, this is a good fit. Move on."
                print "  z          Use current zoom to set xmin and xmax."
                print "  zN         Use current zoom from N'th figure (e.g. z3)."
                print "  zo         Zoom out xrange by a factor of 2."
                print "  zoN        Zoom out the N'th figure."
                print
                print "SETTINGS"

                keys = settings.keys()
                keys.sort()
                for key in keys: print "  "+key+" =", settings[key]

                print
                print "SETTING PARAMETER GUESS VALUES"
                print "  <parameter>=<value>"
                print "              sets the parameter guess value."
                print
                print "  <parameter>=x|y|dx|dy|slope"
                print "              sets the parameter guess value to the"
                print "              clicked x, y, dx, dy, or slope value."
                print 
                print "  <parameter> lists the curent parameter value."
                print

                command=""
                hold_plot=True

            elif clower in ['q', 'quit', 'exit']:
                return {'command':'q','settings':settings}

            elif clower in ['g', 'guess']:
                settings['guess'] = None
                settings['show_guess'] = True

            elif clower in ['o', 'output']:
                # print all the header elements of the current databox
                # and have the user choose as many as they want.
                print "\n\nChoose which header elements to include as columns in the summary file:"
                for n in range(len(data[0].hkeys)):
                    print "  "+str(n)+": "+str(data[0].hkeys[n])

                # get a list of numbers from the user
                key_list = raw_input("pick headers by number: ").split(',')
                if not settings['output_columns']==None:
                      old_output_columns = list(settings['output_columns'])
                else: old_output_columns = None
                
                try:
                    # get the list of keys.
                    settings['output_columns'] = []
                    for n in key_list: settings['output_columns'].append(data[0].hkeys[int(n.strip())])

                    # now have the user select a file
                    settings['output_path'] = _dialogs.Save()
                    if not settings['output_path']==None:
                        # write the column names
                        f = open(settings['output_path'], 'w')
                        f.write('function_string\t'+str(self.function_string)+
                                '\nmodel\t'+str(self.__class__)+
                                '\nxscript\t'+str(settings["xscript"])+
                                '\nyscript\t'+str(settings["yscript"])+
                                '\neyscript\t'+str(settings["eyscript"])+'\n\n')
                        for k in settings['output_columns']: f.write(k+'\t')
                        for n in self.pnames: f.write(n+'\t'+n+'_error\t')
                        f.write('reduced_chi_squared\n')
                        f.close()

                        # all set. It will now start appending to this file.

                except:
                    print "\nOops! Aborting."
                    settings['output_columns'] = old_output_columns
                    
                hold_plot=True

            elif clower in ['y', 'yes','u','use']:

                if fit_parameters==None or fit_errors==None:
                    print "\nERROR: Cannot say a fit is good with no fit!"

                else:
                    if settings['save_file']:

                        # write the fit results to the header
                        for d in data:
                            # If this is a good fit. Add relevant information to the header then save
                            d.insert_header("fit_model", str(self.__class__).split()[0][0:])
                            d.insert_header("fit_function", str(self.function_string))
                            for n in range(len(self.pnames)):
                                d.insert_header("fit_"+self.pnames[n], [fit_parameters[n], fit_errors[n]])
                            d.insert_header("fit_reduced_chi_squared",fit_reduced_chi_squared)

                            # build the correlations array (not a 2-d array)
                            d.insert_header("fit_correlations",       fit_correlation)

                            d.insert_header("fit_min",      settings['min'])
                            d.insert_header("fit_max",      settings['max'])
                            d.insert_header("fit_smooth",   settings['smooth'])
                            d.insert_header("fit_coarsen",  settings['coarsen'])

                            # auto-generate the new file name
                            if settings['fullsave'] in [1, True, 'auto']:
                                directory, filename = os.path.split(d.path)
                                new_path = directory + os.sep + settings['file_tag'] + filename
                                if new_path: d.save_file(new_path)

                            elif settings['fullsave'] in [2, 'ask']:
                                new_path = _dialogs.SingleFile()
                                if new_path: d.save_file(new_path)

                        # append to the summary file
                        if settings['output_path']:
                            f = open(settings['output_path'],'a')
                            for k in settings['output_columns']:
                                f.write(str(d.h(k))+'\t')
                            for n in range(len(fit_parameters)):
                                f.write(str(fit_parameters[n])+'\t'+str(fit_errors[n])+'\t')
                            f.write(str(sum(fit_reduced_chi_squared)/len(fit_reduced_chi_squared))+'\n')
                            f.close()


                    # Return the information
                    return_value = {"command"                   :'y',
                                    "fit_parameters"            :fit_parameters,
                                    "fit_errors"                :fit_errors,
                                    "fit_reduced_chi_squared"   :fit_reduced_chi_squared,
                                    "fit_covariance"            :fit_covariance,
                                    "settings"                  :settings,
                                    "function_string"           :self.function_string,
                                    "pnames"                    :self.pnames}
                                    
                    if clower in ['u', 'use']:
                        return_value['command'] = 'u'
                        return_value['settings']['guess'] = fit_parameters
                    return return_value
                            
            elif clower in ['t', 'transfer']:

                if fit_parameters==None or fit_errors==None:
                    print "\nERROR: Nothing to transfer!"

                else:
                    for n in range(len(fit_parameters)):
                        self.p0[n] = fit_parameters[n]

            elif clower in ['n', 'no', 'next']:
                return {'command':'n','settings':settings}

            elif clower in ['p', 'print']:
                _s.printer()
                hold_plot = True

            elif clower in ['zo', 'zoomout']:                
                # if we haven't set the min and max yet, use the axes bounds.                
                if not settings['min']: 
                    settings['min'] = []                    
                    for a in axes1s: settings['min'].append(a.get_xlim()[0])
                    
                if not settings['max']:
                    settings['max'] = []
                    for a in axes1s: settings['max'].append(a.get_xlim()[1])
                                    
                x0 = _n.array(settings['min'])
                x1 = _n.array(settings['max'])
                xc = 0.5*(x0+x1)
                xs = x1-x0
                settings['min'] = list(xc-xs)
                settings['max'] = list(xc+xs)

            elif clower in ['z', 'zoom']:
                settings['min'] = []
                settings['max'] = []
                for a in axes1s:
                    settings['min'].append(a.get_xlim()[0])
                    settings['max'].append(a.get_xlim()[1])

            elif clower[0] == "z" and len(clower.split('=')) == 1:
                try:
                    if clower[1] == 'o':    
                        n = int(clower[2:].strip()) - settings['figure']
                        
                        print "Zooming out figure", n+settings['figure']
                        x0, x1 = axes1s[n].get_xlim()
                        xc = 0.5*(x0+x1)
                        xs = x1-x0
                        settings['min'][n] = xc-xs
                        settings['max'][n] = xc+xs
                    else:    
                        
                        n = int(clower[1:].strip()) - settings['figure']                        

                        print "Zooming figure", n+settings['figure']                                                
                        settings['min'][n] = axes1s[n].get_xlim()[0]
                        settings['max'][n] = axes1s[n].get_xlim()[1]
                        
                except:
                    print "ERROR: could not zoom according to the specified figure"
            
            # just display the value
            elif clower in settings.keys():
                print                
                print clower,'=',settings[clower]
                hold_plot = True

            else:
                # now parse it (it has the form "min=2; max=4; plot_all=True")
                s = command.split(';')
                for c in s:
                    try:
                        # get the key and value
                        [key, value] = c.split('=')
                        key   = key.strip()
                        value = value.strip()

                        # if this is a setting
                        if settings.has_key(key):

                            # execute the string to get the value
                            evalue = eval(value)

                            # if this is an iterable setting, make sure it's a list
                            if key in iterable_settings:

                                # if it's a single value, set all the values to this
                                if not _s.fun.is_iterable(evalue):
                                    for i in range(len(settings[key])):
                                        settings[key][i] = evalue

                                # otherwise, the lengths must match
                                elif len(evalue)==len(settings[key]):
                                    settings[key] = evalue

                                # lengths don't match
                                else:
                                    print "\nERROR: length of "+key+" does not match."

                            # if it's not an iterable setting
                            else: settings[key] = eval(value)

                        # otherwise we've specified a parameter guess
                        else:
                            self.set_parameter(key, value)
                            settings['guess'] = self.p0

                    except:
                        print "ERROR: '"+str(c)+"' is an invalid command."

            # make sure we don't keep doing the same command over and over!
            command = ""
            print


class curve(model_base):

    globs={} # globals such as sin and cos...

    def __init__(self, f='a+b*x+c*x**2', p='a=1.5, b, c=1.5', bg=None, a=None, globs={}):
        """
        This class takes the function string you specify and generates
        a model based on it.

        f can be either a string or a function f(x,a,b,..) that you have defined.

        p is a comma-delimited string
        
        bg is a background function.
        
        a is a comma-delimited string of additional args to send to the function.

        globs is a list of globals should you wish to have these visible to f.

        If the function is a string it will be evaluated knowing about all the
        globals specified by the globs argument.

        If it is a function, it can have as many arguments as you like, so long
        as the x data is the first argument, and each of the subsequent argument
        slots has a corresponding element in the list p.

        If you want to do something a little more fancy with a guessing algorithm,
        it's relatively straightforward to write one of the model classes similar
        to the examples given in spinmob.models
        
        If you want, you can specify a list of functions, a string of parameters,
        a matching list of background functions, and a matching list of additional
        arguments to fit more than one dataset simultaneously.
        """

        # make sure we have lists
        if not _s.fun.is_iterable(f) :   f    = [f]
        if not _s.fun.is_iterable(bg):   bg   = [bg]
        
        # make sure the background has as many elements as the function list
        if not len(f)==len(bg):
            x  = bg[0]
            bg = list(f)
            for n in range(len(bg)): bg[n]=x
            
        # start by parsing the p string. This is the same for both f's
        p_split = p.split(',')

        # Loop over the parameters, get their names and possible default values
        self.pnames     = []
        self.defaults   = []
        for parameter in p_split:
            parameter_split = parameter.split('=')

            self.pnames.append(parameter_split[0].strip())

            if len(parameter_split)==2: self.defaults.append(float(parameter_split[1]))
            else:                       self.defaults.append(1.0)

        # set up the guess
        self.p0 = _n.array(self.defaults)

        # store the globals
        self.globs = dict(globs)
        
        self.f  = []
        self.bg = []
        self.function_string   = []
        self.background_string = []
        self.additional_args   = []

        # loop over the supplied list of functions
        for n in range(len(f)):

            # now do different things depending on the type of function
            if type(f[n])==str:
                # get the function strings
                self.function_string.append(f[n])
                if bg[n]==None: self.background_string.append(f[n])
                else:           self.background_string.append(bg[n])

                # override the function and background
                args = 'x,'+_fun.join(self.pnames,',')
                if a==None or a[n]==None: 
                    self.additional_args.append(None)
                else:                    
                    args = args + "," + str(a[n])
                    self.additional_args.append(eval('['+str(a[n])+']', self.globs))
                
                self.f.append( eval('lambda ' + args + ': ' +   self.function_string[n], self.globs))
                self.bg.append(eval('lambda ' + args + ': ' + self.background_string[n], self.globs))

            else:
                if bg[n]==None: bg[n] = f[n]
                self.function_string.append(   f[n].__name__ +"(x, "+p+")")
                self.background_string.append(bg[n].__name__ +"(x, "+p+")")

                # override the function and background
                self.f.append(f[n])
                self.bg.append(bg[n])


    # override the evaluate and background functions used by the base class.
    def evaluate(self, p, x, n=None):
        if n==None:
            results = []
            for n in range(len(self.f)):
                if self.additional_args[n]==None: results.append(self.f[n](x[n],*p))
                else:                             results.append(self.f[n](x[n],*(list(p)+self.additional_args[n])))
        
        else: 
            if self.additional_args[n]==None: results = self.f[n](x,*p)
            else:                             results = self.f[n](x,*(list(p)+self.additional_args[n]))
        return results

    def background(self, p, x, n=None):
        if n==None:
            results = []
            for n in range(len(self.bg)):
                if self.additional_args[n]==None: results.append(self.bg[n](x[n],*p))
                else:                             results.append(self.bg[n](x[n],*(list(p)+self.additional_args[n])))
        
        else: 
            if self.additional_args[n]==None: results = self.bg[n](x,*p)
            else:                             results = self.bg[n](x,*(list(p)+self.additional_args[n]))
        return results

    # You can override this if you want the guess to be something fancier.
    def guess(self, xdata, ydata, xbi1=0, xbi2=-1):
        """
        This function takes the supplied data (and two indices from which to
        estimate the background should you want them) and returns a best guess
        of the parameters, then stores this guess in p0.
        """

        self.write_to_p0(self.defaults)
        return




class quartic(model_base):

    function_string = "p[0] + p[1]*x + p[2]*x*x + p[3]*x*x*x + p[4]*x*x*x*x"
    pnames = ["a0", "a1", "a2", "a3", "a4"]

    # this must return an array!
    def background(self, p, x):
        return self.evaluate(p,x)

    def evaluate(self, p, x):
        return p[0] + p[1]*x + p[2]*x*x + p[3]*x*x*x + p[4]*x*x*x*x

    def guess(self, xdata, ydata, xbi1=0, xbi2=-1):
        # first get the appropriate size array
        p=self.p0

        # guess the slope and intercept
        p[0] = ydata[0][len(xdata[0])/2]
        p[1] = (ydata[0][xbi2]-ydata[0][xbi1])/(xdata[0][xbi2]-xdata[0][xbi1])
        p[2] = 0.0
        p[3] = 0.0
        p[4] = 0.0

        # write these values to self.p0, but avoid the guessed_list
        self.write_to_p0(p)


