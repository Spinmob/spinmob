import spinmob     as _s
import numpy       as _n
import spinmob.egg as _egg
_g = _egg.gui



class fake_data_taker():
    
    
    def __init__(self):
        
        self._build_gui()

    def _build_gui(self):
        """
        Builds the GUI for taking fake data.
        """
        # Make a window with a left grid for settings and controls, and
        # a right grid for visualization.
        self.window        = _g.Window('Fake Data Taker', autosettings_path='window.cfg')
        self.grid_controls = self.window.place_object(_g.GridLayout(False))
        self.grid_plotting = self.window.place_object(_g.GridLayout(False), alignment=0)
        
        # Add the acquire button & connect the signal
        self.button_acquire = self.grid_controls.place_object(_g.Button('Acquire Fake Data'))
        self.button_acquire.signal_clicked.connect(self.button_acquire_clicked)
        
        # Create an populate the settings tree
        self.grid_controls.new_autorow()
        self.tree_settings  = self.grid_controls.place_object(_g.TreeDictionary())
        self.tree_settings.add_parameter('Data/Reality', '1.7*x+1.2', type='str')
        self.tree_settings.add_parameter('Data/x_noise',        0,    type='float')
        self.tree_settings.add_parameter('Data/y_noise',      3.2,    type='float')
        self.tree_settings.add_parameter('Acquisition/xmin',  -10,    type='float')
        self.tree_settings.add_parameter('Acquisition/xmax',   10,    type='float')
        self.tree_settings.add_parameter('Acquisition/steps', 100,    type='int')
        
        
        # Add the plotter to the other grid
        self.plot_data = self.grid_plotting.place_object(_g.DataboxPlot(autosettings_path='plot_data.cfg'), alignment=0)
        
        # Show the window
        self.window.show()
    
    def button_acquire_clicked(self, *a):
        """
        Acquires fake data and dumps it with the header into the plotter.
        """
        # Dump the header info
        self.tree_settings.send_to_databox_header(self.plot_data)
        
        # Generate the data
        x = _n.linspace(self.tree_settings['Acquisition/xmin'], 
                        self.tree_settings['Acquisition/xmax'],
                        self.tree_settings['Acquisition/steps'])
        
        d = _s.fun.generate_fake_data(self.tree_settings['Data/Reality'], x,
                                      self.tree_settings['Data/y_noise'],
                                      self.tree_settings['Data/x_noise'])
        
        # Dump it to the plotter and plot
        self.plot_data.copy_columns(d)
        
        # Plot it.
        self.plot_data.plot()
