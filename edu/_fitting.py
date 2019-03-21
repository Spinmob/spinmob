import spinmob     as _s
import numpy       as _n
import spinmob.egg as _egg
import scipy.stats as _stats
_g = _egg.gui

# For embedding matplotlib figures
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg    as _canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as _navbar
from matplotlib.figure import Figure as _figure


class fitting_statistics_demo():
    
    """
    Graphical interface for generating fake data, fitting, and collecting 
    fit statistics.
    
    Parameters
    ----------
    block_command_line=True
        Whether to block the command line when the window is first shown.
    """
    
    
    def __init__(self, block_command_line=True):
        
        self._build_gui(block_command_line)

    def _build_gui(self, block_command_line=False):
        """
        Builds the GUI for taking fake data.
        """
        # Make a window with a left grid for settings and controls, and
        # a right grid for visualization.
        self.window        = _g.Window('Fake Data Taker', autosettings_path='window.cfg')
        self.grid_controls = self.window.place_object(_g.GridLayout(False))
        self.grid_plotting = self.window.place_object(_g.GridLayout(False), alignment=0)
        
        # Add the acquire button & connect the signal
        self.button_acquire = self.grid_controls.place_object(_g.Button('Acquire'))
        self.button_fit     = self.grid_controls.place_object(_g.Button('Fit'))
        self.button_loop    = self.grid_controls.place_object(_g.Button('Loop', True))
        self.button_acquire.signal_clicked.connect(self.button_acquire_clicked)
        self.button_fit    .signal_clicked.connect(self.button_fit_clicked)
        self.button_loop   .signal_clicked.connect(self.button_loop_clicked)
        # Create an populate the settings tree
        self.grid_controls.new_autorow()
        self.tree_settings  = self.grid_controls.place_object(_g.TreeDictionary(), column_span=3)
        
        self.tree_settings.add_parameter('Data/reality', '1.7*x+1.2')
        self.tree_settings.add_parameter('Data/x_noise',        0)
        self.tree_settings.add_parameter('Data/y_noise',      1.3)
        
        self.tree_settings.add_parameter('Acquisition/xmin',    0)
        self.tree_settings.add_parameter('Acquisition/xmax',   10)
        self.tree_settings.add_parameter('Acquisition/steps', 100, dec=True)
        
        self.tree_settings.add_parameter('Fit/function',   'a*x+b')
        self.tree_settings.add_parameter('Fit/parameters', 'a=0,b=0')
        self.tree_settings.add_parameter('Fit/assumed_ey', 1.3)
        
        self.tree_settings.add_parameter('Stats/bins',        14)
        self.tree_settings.add_parameter('Stats/versus_x',    'a')
        self.tree_settings.add_parameter('Stats/versus_y',    'b')
        self.tree_settings.add_parameter('Stats/plot_theory', False)
        
        # Add the tabs and plotter to the other grid
        self.tabs_plotting = self.grid_plotting.place_object(_g.TabArea('tabs_plotting.cfg'), alignment=0)
        
        # Tab for raw data
        self.tab_raw  = self.tabs_plotting.add_tab('Raw Data')
        self.plot_raw = self.tab_raw.place_object(
                _g.DataboxPlot(autosettings_path='plot_data.cfg', autoscript=4), 
                alignment=0)
        self.plot_raw.autoscript_custom = self._autoscript_raw
        
        # Tab for fit
        self.tab_fit    = self.tabs_plotting.add_tab('Fit')
        
        self.figure_fit = _figure()
        self.canvas_fit = _canvas(self.figure_fit)
        self.navbar_fit = _navbar(self.canvas_fit, self.window._widget)
        
        self.tab_fit.place_object(self.navbar_fit, alignment=0)
        self.tab_fit.new_autorow()
        self.tab_fit.place_object(self.canvas_fit, alignment=0)

        # Fitter object linked to this figure canvas
        self.fitter = _s.data.fitter()
        self.fitter.set(autoplot=False)
        self.fitter.figures = [self.figure_fit]

        # Tab for running total of fit parameters
        self.tab_parameters  = self.tabs_plotting.add_tab('Fit Parameters')
        self.plot_parameters = self.tab_parameters.place_object(
                _g.DataboxPlot(autosettings_path='plot_parameters.cfg'),
                alignment=0)
        # Give it a handle on the fitter for the script
        self.plot_parameters.fitter = self.fitter
        
        # Tab for histograms
        self.tab_stats    = self.tabs_plotting.add_tab('Histograms')
        
        self.figure_stats = _figure()
        self.canvas_stats = _canvas(self.figure_stats)
        self.navbar_stats = _navbar(self.canvas_stats, self.window._widget)
        
        self.tab_stats.place_object(self.navbar_stats, alignment=0)
        self.tab_stats.new_autorow()
        self.tab_stats.place_object(self.canvas_stats, alignment=0)
        
        # Changing tabs can update plots
        self.tabs_plotting.signal_switched.connect(self.tabs_plotting_switched)
        
        # Set up the autosave & load.
        self.tree_settings.connect_any_signal_changed(self.tree_settings.autosave)
        self.tree_settings.connect_any_signal_changed(self.update_all_plots)
        self.tree_settings.load()
        
        # Show the window
        self.window.show(block_command_line)
    
    def _autoscript_raw(self):
        """
        Returns a nice custom autoscript for plotting the raw data.
        """
        return "x = [ d[0] ]\ny = [ d[1] ]\n\nxlabels = 'x'\nylabels = ['y']"
    
    def tabs_plotting_switched(self, *a):
        """
        Someone switched a tab!
        """
        if   a[0]==1: self.update_fit_plot()
        elif a[0]==3: self.update_histograms_plot()
    
    def button_acquire_clicked(self, *a):
        """
        Acquires fake data and dumps it with the header into the plotter.
        """
        
        # Dump the header info
        self.tree_settings.send_to_databox_header(self.plot_raw)
        
        # Generate the data
        x = _n.linspace(self.tree_settings['Acquisition/xmin'], 
                        self.tree_settings['Acquisition/xmax'],
                        self.tree_settings['Acquisition/steps'])
        
        
        d = _s.fun.generate_fake_data(self.tree_settings['Data/reality'], x,
                                      self.tree_settings['Data/y_noise'],
                                      self.tree_settings['Data/x_noise'])
        
        # Dump it to the plotter and plot
        self.plot_raw.copy_columns(d)
        
        # Plot it.
        self.plot_raw.plot()
    
    def button_fit_clicked(self,*a):
        """
        Assuming there is data, run the fit!
        """
        # Set the functions
        self.fitter.set_functions(self.tree_settings['Fit/function'],
                                  self.tree_settings['Fit/parameters'])
        
        # Set the data
        self.fitter.set_data(self.plot_raw[0], self.plot_raw[1], 
                             self.tree_settings['Fit/assumed_ey'])
        
        # Fit!
        self.fitter.fit()
        
        # Draw
        self.figure_fit.canvas.draw()
        self.window.process_events()
        
        # Now append the fit results to the next tab's plotter
        p   = list(self.fitter.results[0])
        e   = list(_n.sqrt(self.fitter.results[1].diagonal()))
        x2  = self.fitter.reduced_chi_squared()
        dof = len(self.fitter.get_processed_data()[0][0])-len(p)
        row = p+e+x2+dof
        pnames = self.fitter.get_pnames()
        
        ckeys = ['reduced_chi2', 'DOF']
        row   = [x2,dof]
        for n in range(len(p)):
            
            # Append the fit parameter
            ckeys.append(pnames[n])
            row  .append(p[n])

            # Append the fit error
            ckeys.append(pnames[n]+'_error')
            row  .append(e[n])
        
        # If the parameters haven't changed, just append the data
        if ckeys == self.plot_parameters.ckeys:
            self.plot_parameters.append_data_point(row)
            self.tree_settings.send_to_databox_header(self.plot_parameters)
            
        # Otherwise, clear it out and rebuild it, and rebuild the histograms plot.
        else:
            # Clear it out and add the first row of data
            self.plot_parameters.clear()
            for n in range(len(ckeys)): 
                self.plot_parameters[ckeys[n]] = [row[n]]

            # Clear the figure and set up the histogram axes
            self.axes_histograms = []
            self.figure_stats.clear()
            
            # Calculate how many rows of plots are needed
            rows = int(_n.ceil(len(p)*0.5)+1)
            
            # Reduced chi^2 histogram
            self.axes_histograms.append(self.figure_stats.add_subplot(rows, 2, 1))
            self.axes_histograms.append(self.figure_stats.add_subplot(rows, 2, 2))
            
            # Parameter histograms
            for n in range(len(p)):
                self.axes_histograms.append(self.figure_stats.add_subplot(rows, 2, n+3))
                
              
        # Update the script
        s = 'x = [None]\ny = [d[0],d[1]'
        for n in range(len(p)):
            s = s+',d['+str(2*n+2)+']'
        
        s = s+']\n\nxlabels = "Iteration"\nylabels = [ d.ckeys[0], d.ckeys[1]'
        for n in range(len(p)):
            s = s+',d.ckeys['+str(2*n+2)+']'
        s = s+']'
        
        # Set to manual script and update the text
        self.plot_parameters.combo_autoscript.set_value(0)
        self.plot_parameters.script.set_text(s)
        
        # Update the parameters plot!
        self.plot_parameters.plot()
        
        # If we're on the fit or stats tab (these are slow to plot)
        if self.tabs_plotting.get_current_tab()==1: self.update_fit_plot()
        if self.tabs_plotting.get_current_tab()==3: self.update_histograms_plot()
        
    def button_loop_clicked(self, value):
        """
        When someone clicks the "loop" button. 
        """
        # If it's enabled, start the loop
        if not value: return
    
        # Run the loop
        while self.button_loop.is_checked():
            
            # Acquire data and fit
            self.button_acquire_clicked(True)
            self.window.process_events()
            self.button_fit_clicked(True)
            self.window.process_events()
    
    def update_fit_plot(self):
        """
        Update the fit plot.
        """
        if not self.tabs_plotting.get_current_tab()==1: return
        
        self.fitter.plot()
        self.window.process_events()
        self.figure_fit.canvas.draw()
        self.window.process_events()
    
    def update_histograms_plot(self):
        """
        Update the histogram plots (actually perform the histogram and plot).
        """
        # Don't bother if we're not looking.
        if not self.tabs_plotting.get_current_tab()==3: return
        
        if len(self.plot_parameters) and len(self.axes_histograms):
            
            # Update the chi^2 histogram histograms
            self.axes_histograms[0].clear()
            N,B,c = self.axes_histograms[0].hist(self.plot_parameters[0], self.tree_settings['Stats/bins'], label='$\chi^2_{reduced}$')
            x = (B[1:]+B[:-1])*0.5
            
            # Include the error bars
            self.axes_histograms[0].errorbar(x, N, _n.sqrt(N), ls='', marker='+')
            
            # Tidy up
            self.axes_histograms[0].set_xlabel('$\chi^2_{reduced}$')
            self.axes_histograms[0].set_ylabel('Counts')
            
            # Plot the expected distribution.
            if self.tree_settings['Stats/plot_theory']:
                x2  = _n.linspace(min(0.5*(B[1]-B[0]),0.02), max(1.5,max(self.plot_parameters[0])), 400)
                dof = self.plot_parameters[1][-1]
                pdf = len(self.plot_parameters[1]) * dof * _stats.chi2.pdf(x2*dof,dof) * (B[1]-B[0])                
                self.axes_histograms[0].plot(x2,pdf,label='Expected ('+str(dof)+ 'DOF)')
                self.axes_histograms[0].legend()
            
            # Include zero, to give a sense of scale.
            self.axes_histograms[0].set_xlim(0,max(1.5,max(self.plot_parameters[0]))*1.05)
            
            
            # Plot the correlations
            self.axes_histograms[1].clear()
            self.axes_histograms[1].plot(self.plot_parameters[self.tree_settings['Stats/versus_x']],
                                         self.plot_parameters[self.tree_settings['Stats/versus_y']],
                                         label=self.tree_settings['Stats/versus_y']+' vs '+self.tree_settings['Stats/versus_x'],
                                         linestyle='', marker='o', alpha=0.3)
            self.axes_histograms[1].set_xlabel(self.tree_settings['Stats/versus_x'])
            self.axes_histograms[1].set_ylabel(self.tree_settings['Stats/versus_y'])
            self.axes_histograms[1].legend()
            
            # Now plot the distributions of the other fit parameters.
            for n in range(len(self.fitter.get_pnames())):
                
                # Plot the histogram
                self.axes_histograms[n+2].clear()
                N,B,c = self.axes_histograms[n+2].hist(self.plot_parameters[2*n+2], self.tree_settings['Stats/bins'], label=self.fitter.get_pnames()[n])
                x = (B[1:]+B[:-1])*0.5
                
                # Include the error bars
                self.axes_histograms[n+2].errorbar(x, N, _n.sqrt(N), ls='', marker='+')
            
                # Tidy up
                self.axes_histograms[n+2].set_xlabel(self.fitter.get_pnames()[n])
                self.axes_histograms[n+2].set_ylabel('Counts')
                
                # Plot the expected distribution, calculated from the mean
                # and fit error bar.
                if self.tree_settings['Stats/plot_theory']:
                    x0  = _n.average(self.plot_parameters[2*n+2]) 
                    ex  = self.plot_parameters[2*n+3][-1]
                    x   = _n.linspace(x0-4*ex, x0+4*ex, 400)
                    pdf = len(self.plot_parameters[1]) * _stats.norm.pdf((x-x0)/ex)/ex * (B[1]-B[0])
                    
                    self.axes_histograms[n+2].plot(x,pdf,label='Expected')
                    self.axes_histograms[n+2].legend()
                
        
        self.figure_stats.canvas.draw()
        self.window.process_events()
        
    def update_all_plots(self, *a):
        """
        Updates the Fit and Stats plots.
        """
        self.update_fit_plot()
        self.update_histograms_plot()
            