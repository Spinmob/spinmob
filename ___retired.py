    def plot_columns(self, start=1, end=-1, yshift=0.0, yshift_every=1, xcolumn=0, legend=None, clear=1, axes="gca", legend_max=30, autoformat=True, tall="auto", **kwargs):
        """
        This does a line plot of a range of columns.

        start=1         Index of the starting column.
        end=-1          Index of the end column, with -1 meaning "all the way"
        yshift=0.0      How much vertical artificial offset to apply
        yshift_every=1  How many traces should sit at the same offset
        xcolumn=0       Index of the x-data column
        legend=None     What header row to use as the legend values. If set to None,
                        use the column ckeys

        legend_max=40   Maximum number of legend entries
        tall=True       When formatting the figure, make it tall.

        **kwargs        Arguments to be sent to "plot". See "plot" for more details!
        """

        # get the axes
        if axes=="gca": axes=_pylab.gca()
        if clear:       axes.clear()

        # set the xdata and ckeys
        self.xdata  = self.c(xcolumn)
        self.xlabel = self.ckeys[xcolumn]
        self.ylabel = self.ckeys[start]

        # get the last index if necessary
        if end < start: end = len(self.columns)-1

        # now loop over the columns
        for n in range(start, end+1):
            # store this trace
            self.ydata = self.c(n)

            self.eydata = None
            if legend == None:  self.legend_string = self.ckeys[n].replace("_","")
            else:               self.legend_string = str(self.h(legend)[n-1]).replace("_","")

            # now plot it
            self.plot(yshift=((n-start)/yshift_every)*yshift, axes=axes, clear=0, autoformat=False, **kwargs)

            # now fix the legend up real nice like
            if   n-start >  legend_max-2 and n != end: axes.get_lines()[-1].set_label('_nolegend_')
            elif n-start == legend_max-2:              axes.get_lines()[-1].set_label('...')


        # fix up the title if there's an offset
        if yshift: self.title = self.path + '\nprogressive y-shift='+str(yshift)+" every "+str(yshift_every)
        axes.set_title(self.title)

        # make it look nice
        if tall=="auto": tall = yshift
        if autoformat: _pt.format_figure(axes.figure, tall=tall)

        # bring it to the front, but keep the command line up too
        _pt.get_figure_window()
        _pt.get_pyshell()

    def get_data(self):
        """
        This function is mostly used for the fitting routine, whose only
        restriction on the data class is that it can load_file(), and get_data()
        storing the results in self.xdata, self.ydata, self.eydata.

        It has no parameters because the fit function doesn't need to know.
        Uses self.xscript, self.yscript, and self.eyscript.
        """

        self.xdata  = self.execute_script(self.xscript)
        self.ydata  = self.execute_script(self.yscript)
        if self.eyscript:   self.eydata = self.execute_script(self.eyscript)
        else:               self.eydata = None
        self.xlabel = self.xscript
        self.ylabel = self.yscript


    def plot(self, xscript=0, yscript=1, eyscript=None, clear=True, autoformat=True, axes="gca", coarsen=0, yshift=0, linestyle='auto', marker='auto', lscript=None, title=None, **kwargs):
        """

        KEYWORDS (can set as arguments or kwargs):

        xscript, yscript, eyscript    These are the scripts to generate the three columns of data

        axes="gca"                  Which set of axes to use. "gca" means use the current axes.
        clear=True                  Clear the axes first?
        autoformat=True             Format the axes/labels/legend/title when done plotting?
        coarsen=0                   Should we coarsen the data?
        yshift=0                    How much vertical artificial offset should we add?

        linestyle="auto"            What type of line should we plot?
                                    "auto" means lines for data with no error and symbols
                                    for data with error (using spinmob style object).
                                    "style" means always use lines from spinmob style cycle

        marker="auto"               What type of markers should we use?
                                    "auto" means markers only for data with error, using spinmob style
                                    "style" means definitely use markers from spinmob style
                                    otherwise just specify a marker

        lscript=None                None means use self.legend_string (usually file name), otherwise,
                                    this runs the script and takes the str() of the result

        title=None                  None means automatically come up with a title.

        kwargs

        """

        # update with the user-supplied/default values with kwargs
        plot_kwargs = {}
        for key in kwargs:
            try:    eval(key + "=" + kwargs[key])
            except: plot_kwargs[key] = kwargs[key]


        # if we're doing a no-script plot
        if xscript==None or yscript==None:
            if self.ydata == None or len(self.ydata) <= 0:
                print "No data to plot! Generate data with xscript and yscript."
                return False

            xdata = self.xdata
            ydata = self.ydata
            eydata= self.eydata

        # if we're doing a scripted plot
        else:

            # use the expected error column if we're supposed to
            if eyscript == "auto": eyscript = yscript+"_error"

            # if eydata doesn't exist and we haven't specified no error
            # try to generate the column
            if  not eyscript in self.columns.keys() \
            and not eyscript==None                  \
            and not type(eyscript) in [int,long]:
                if self.debug: print eyscript, "is not a column"
                eydata = self.execute_script(eyscript)


            [xpression, xvars] = self._parse_script(xscript)
            if xvars == None: return
            [ypression, yvars] = self._parse_script(yscript)
            if yvars == None: return

            if not eyscript == None:
                [spression, svars] = self._parse_script(eyscript)
                if svars == None: eydata = None

            # try to evaluate the data
            self.xdata  = eval(xpression, xvars)
            self.ydata  = eval(ypression, yvars)
            if eyscript == None:  self.eydata = None
            else:                 self.eydata = eval(spression, svars)

            xdata  = self.xdata
            ydata  = self.ydata
            eydata = self.eydata

            self.xlabel = xscript
            self.ylabel = yscript
            if title==None:
                self.title  = self.assemble_title()
            else:
                self.title  = title

        # trump the x and y labels
        if plot_kwargs.has_key('xlabel'): self.xlabel = plot_kwargs.pop('xlabel')
        if plot_kwargs.has_key('ylabel'): self.ylabel = plot_kwargs.pop('ylabel')



        # coarsen the data if we're supposed to
        if coarsen: [xdata, ydata, eydata]=_fun.coarsen_data(xdata, ydata, eydata, coarsen)

        # assumes we've gotten data already
        if axes=="gca": axes = _pylab.gca()
        if clear: axes.clear()

        # modify the legend string
        if lscript == None: label = self.legend_string
        else:                   label = str(self.execute_script(lscript))
        if yshift: label = label + " ("+str(yshift)+")"




        # Now figure out the list of arguments and plotting function



        # default line and marker values
        mec = None
        mfc = None
        line_color = None


        # no eydata.
        if eydata == None:
            # if we're to use the style object to get the line attributes
            if linestyle in ['auto', 'style']:
                # get the linestyle from the style cycle
                linestyle  = _pt.style.get_linestyle(1)
                line_color = _pt.style.get_line_color(1)

            # only make markers without eydata if we're not in auto mode
            if marker in ['auto']:
                marker = ''

            # if we're forcing the use of style
            elif marker in ['style']:
                # get the marker attributes from the style cycle
                marker = _pt.style.get_marker(1)
                mfc    = _pt.style.get_face_color(1)
                mec    = _pt.style.get_edge_color(1)

            # otherwise, marker is already defined. Hopefully **plot_kwargs will override these values

            # handle to plotting function
            plotter = axes.plot

        # we have error bars
        else:
            # if we're in auto mode, NO LINES!
            if linestyle in ['auto']:
                linestyle  = ''
                line_color = 'k'

            # if we're forcing the style object
            elif linestyle in ['style']:
                linestyle  = _pt.style.get_linestyle(1)
                line_color = _pt.style.get_line_color(1)

            # otherwise it's specified. Default to blue and let **plot_kwargs override

            # similarly for markers
            if marker in ['auto', 'style']:
                # get the marker attributes from the style cycle
                marker = _pt.style.get_marker(1)
                mfc    = _pt.style.get_face_color(1)
                mec    = _pt.style.get_edge_color(1)

            # otherwise it's specified

            # handle to plotter and error argument
            plotter = axes.errorbar
            plot_kwargs['yerr']   = eydata
            plot_kwargs['ecolor'] = mec

        # only add these new arguments to plot_kwargs if they don't already exist
        # we want to be able to supercede the style cycle
        if  not plot_kwargs.has_key('color')           \
        and not line_color == None:                     plot_kwargs['color']        = line_color

        if  not plot_kwargs.has_key('linestyle')       \
        and not plot_kwargs.has_key('ls'):              plot_kwargs['linestyle']    = linestyle

        if  not plot_kwargs.has_key('marker'):          plot_kwargs['marker']       = marker

        if  not plot_kwargs.has_key('mec')             \
        and not plot_kwargs.has_key('markeredgecolor') \
        and not mec==None:                              plot_kwargs['mec']          = mec

        if  not plot_kwargs.has_key('mfc')             \
        and not plot_kwargs.has_key('markerfacecolor') \
        and not mfc==None:                              plot_kwargs['mfc']          = mfc

        if  not plot_kwargs.has_key('markeredgewidth') \
        and not plot_kwargs.has_key('mew'):             plot_kwargs['mew']          = 1.0


        # actually do the plotting
        plotter(xdata, ydata + yshift, label=label, **plot_kwargs)
        axes.set_xlabel(self.xlabel)
        axes.set_ylabel(self.ylabel)
        axes.set_title(self.title)

        if autoformat: _pt.format_figure()
        return axes