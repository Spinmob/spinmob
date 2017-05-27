from gnuradio import gr  as _gr
from gnuradio import uhd as _uhd

import thread      as _thread
import time        as _time
import numpy       as _n

import spinmob     as _s
import spinmob.egg as _egg




class data_buffer(_gr.sync_block):
    """
    docstring for block data_buffer
    """
    def __init__(self, size=100000):
        """
        Create a data buffer that will hold "size" number of packets 
        (346 samples each packet).
        """
        
        _gr.sync_block.__init__(self, name="data_buffer", in_sig=[(_n.int16,2)], out_sig=None)
        
        # Save this for size checking
        self._size = size        
        self._size_lock = _thread.allocate_lock()        
        
        # Create the buffer
        self._buffer  = []
        self._buffer_lock = _thread.allocate_lock()
        
        # Flag for whether the buffer has overrun since the last reset 
        self._buffer_overruns = 0
        self._buffer_overruns_lock = _thread.allocate_lock()
        
    
    def __len__(self):
        """
        Returns the number of packets currently in the buffer.
        """
        self._buffer_lock.acquire()
        N = len(self._buffer)
        self._buffer_lock.release()
        return N
    
    def flush_buffer(self):
        """
        Clears the buffer.
        """
        self._buffer_lock.acquire()
        self._buffer = []
        self._buffer_lock.release()
        
        self._buffer_overruns_lock.acquire()
        self._buffer_overruns = 0
        self._buffer_overruns_lock.release()        

    def get_overruns(self):
        """
        Returns the number of overruns.
        """
        self._buffer_overruns_lock.acquire()
        x = self._buffer_overruns
        self._buffer_overruns_lock.release()     
        return x
    
    def get_packet(self):
        """
        Returns the oldest packet.
        """
        if len(self._buffer): return self._buffer.pop()
        else: return None

    def get_packets(self, min_samples=1, timeout=1.0):
        """
        Waits for enough packets to cover min_samples (or the timeout), then 
        returns all packets, and the number of overruns, clearing the buffer
        and resetting the overrun count.
        
        min_samples     specifies the minimum number of samples to wait for.
        timeout         specifies the "give up" time
        """
        
        t0 = _time.time()
        packets = []
        while _time.time()-t0 < timeout and len(packets)*346 < min_samples: 
            
            # Return all data and clear the buffer
            self._buffer_lock.acquire()
            packets = packets + self._buffer
            self._buffer = []
            self._buffer_lock.release()
            _time.sleep(0.001)        
    
        # Return the number of overruns and reset
        self._buffer_overruns_lock.acquire()
        overruns = self._buffer_overruns
        self._buffer_overruns = 0
        self._buffer_overruns_lock.release()

    
        return packets, overruns

    def set_size(self, size):
        """
        Changes the size of the buffer.
        """
        self._size_lock.acquire()
        self._size = size
        self._size_lock.release()
    
    def get_size(self):
        """
        Returns the maximum size of the buffer.
        """
        self._size_lock.acquire()
        x = self._size
        self._size_lock.release()
        return x

    def work(self, input_items, output_items):
        
        # Acquire the buffer lock for the whole function.
        self._buffer_lock.acquire()
        
        # Append the new data
        self._buffer.append(_n.array(input_items[0]))
        
        # If we've overrun
        self._size_lock.acquire()
        while len(self._buffer) > self._size:

            # Remove the oldest data point            
            self._buffer.pop()
            
            # Increment the overrun
            self._buffer_overruns_lock.acquire()
            self._buffer_overruns += 1
            self._buffer_overruns_lock.release()
        
        # release the buffer lock
        self._buffer_lock.release()        
        self._size_lock.release()
        
        return len(input_items[0])


class jax_data_streamer():

    # Buffer to hold all the data    
    buffer = data_buffer(10000)
    get_packets = buffer.get_packets
    
    def __init__(self):
        
        # Create the gnuradio top block
        self._top_block = _gr.top_block("Data Streamer")        
        
        # Create the faucet from the Crimson
        self._crimson = _uhd.usrp_source("crimson",
        	_uhd.stream_args(cpu_format="sc16", args='sc16', channels=([0])))
        
        # Buffer defined above the __init__        
        # Connect the faucet to the buffer
        self._top_block.connect((self._crimson, 0), (self.buffer, 0))

        # Build the gui, load previous settings, connect signals
        self._build_gui()
        
        # Update settings from the Crimson itself
        self._get_settings_from_crimson()      
    
        # Set the buffer size
        self.buffer.set_size(self.settings['buffer_size'])        
        
        # Show it!
        self.show()
        
        # Start the crimson.
        self._start()
        
        # Start the collection timer
        self.timer_collect.start()
    
    def _build_gui(self):
        """
        Places all the controls and plots etc, loads previous config.
        """        
        # Embeddable docker to hold GUI stuff
        self.docker = _egg.gui.Docker('RXA via Buffer', autosettings_path='rxa_via_buffer_window')
        
        # Top controls
        self.g_top = self.docker.place_object(_egg.gui.GridLayout(False))
        self.b_collect       = self.g_top.place_object(_egg.gui.Button('Collect Data!' , True, True))
        self.b_trigger       = self.g_top.place_object(_egg.gui.Button('Trigger',        True, False))        
        self.pb_buffer       = self.g_top.place_object(_egg.pyqtgraph.QtGui.QProgressBar())        
        self.b_overrun       = self.g_top.place_object(_egg.gui.Button('Buffer Overrun', True))
        self.b_psd_reset_psd = self.g_top.place_object(_egg.gui.Button('Reset PSD'))
        self.n_psd_counter   = self.g_top.place_object(_egg.gui.NumberBox(0))

        # button functions
        self.b_collect.signal_clicked.connect(self._b_collect_clicked)
        
        # Data collection timer
        self.timer_collect = _egg.pyqtgraph.QtCore.QTimer()
        self.timer_collect.setInterval(1)
        self.timer_collect.timeout.connect(self._timer_collect_tick)
        
        # Create Settings tree and parameters
        self.docker.new_autorow()
        self.g_stuff = self.docker.place_object(_egg.gui.GridLayout(False), alignment=0)
        self.settings = self.g_stuff.place_object(_egg.gui.TreeDictionary('rxa_via_buffer_settings'))        
        self.settings.add_parameter('sample_rate',      1e6, type='float', limits=(1e4,325e6), decimals=12, suffix='Hz', siPrefix=True, dec=True)
        self.settings.add_parameter('center_frequency', 7e6, type='float', limits=(0,6e9),     decimals=12, suffix='Hz', siPrefix=True, step=0.1e6)
        self.settings.add_parameter('bandwidth',        1e5, type='float', limits=(0,325e6/2), decimals=12, suffix='Hz', siPrefix=True)        
        self.settings.add_parameter('gain',             0,   type='float', limits=(0,31.5),    step=0.5,    suffix=' dB')
        self.settings.add_parameter('buffer_size',      1e4, type='int',   limits=(1,None),    decimals=12, suffix=' packets', dec=True)
        self.settings.add_parameter('voltage_cal',2.053e-05, type='float')
        self.settings.add_parameter('PSD_resolution',   100, type='float', limits=(1e-3,1e6),  suffix='Hz', siPrefix=True, dec=True)
        self.settings.add_parameter('PSD_averages',     0,   type='float')

        # Load and set previous settings (if any)        
        self.settings.load()
        
        # Set it up so that any changes are sent to the Crimson
        self.settings.connect_signal_changed('sample_rate',      self._sample_rate_changed)
        self.settings.connect_signal_changed('center_frequency', self._center_frequency_changed)
        self.settings.connect_signal_changed('bandwidth',        self._bandwidth_changed)
        self.settings.connect_signal_changed('gain',             self._gain_changed)
        self.settings.connect_signal_changed('buffer_size',      self._buffer_size_changed)
        
        # for saving
        self.settings.connect_any_signal_changed(self._any_setting_changed)

        # Plotter tabs
        self.tabs_plots = self.g_stuff.place_object(_egg.gui.TabArea(False, 'rxa_via_buffer_tabs_plots'), alignment=0)
        
        # Raw time trace    
        self.tab_raw = self.tabs_plots.add_tab('Raw')                
        self.p_raw = self.tab_raw.place_object(_egg.gui.DataboxPlot("*.txt", "rxa_via_buffer_p_raw"), alignment=0)
        self.p_raw_trigger_level = _egg.pyqtgraph.InfiniteLine(0, movable=True, angle=0)
        self.p_raw.ROIs.append([self.p_raw_trigger_level])
        self.p_raw.load_gui_settings()
        
        # "Calibrated" time trace
        self.tab_volts = self.tabs_plots.add_tab('Volts')
        self.p_volts   = self.tab_volts.place_object(_egg.gui.DataboxPlot("*.txt", "rxa_via_buffer_p_volts"), alignment=0)
        
        # PSD
        self.tab_psd = self.tabs_plots.add_tab('PSD')
        self.p_psd   = self.tab_psd.place_object(_egg.gui.DataboxPlot("*.txt", "rxa_via_buffer_p_psd"), alignment=0)

        # load last selected tab
        self.tabs_plots.load_gui_settings()

    def _any_setting_changed(self, *a): self.settings.save()

    def _b_collect_clicked(self, *a):
        if self.b_collect.is_checked(): 
            self.n_psd_counter.set_value(0)
            self.buffer.flush_buffer()

    def _get_settings_from_crimson(self):
        """
        Asks the crimson what all the settings currently are, and updates
        the GUI. This also blocks all user-defined signals for changing the GUI.
        """
        self.settings.set_value('sample_rate',      self.get_sample_rate(),      True)
        self.settings.set_value('center_frequency', self.get_center_frequency(), True)
        self.settings.set_value('bandwidth',        self.get_bandwidth(),        True)
        self.settings.set_value('gain',             self.get_gain(),             True)
        

    def _sample_rate_changed(self, *a):
        self.settings.set_value('sample_rate', self.set_sample_rate(self.settings['sample_rate']), True)
        
    def _center_frequency_changed(self, *a):
        self.settings.set_value('center_frequency', self.set_center_frequency(self.settings['center_frequency']), True)
    
    def _bandwidth_changed(self, *a):
        self.settings.set_value('bandwidth', self.set_bandwidth(self.settings['bandwidth']), True)
    
    def _gain_changed(self, *a):
        self.settings.set_value('gain', self.set_gain(self.settings['gain']), True)
    
    def _buffer_size_changed(self, *a):
        self.buffer.set_size(self.settings['buffer_size'])
    
    def _start(self): return _thread.start_new_thread(self._top_block.start, ())
    
    def _timer_collect_tick(self, *a):
        """
        Called every time the data collection timer ticks.
        """

        # Update the number of packets
        self.pb_buffer.setValue(_n.round(100.0*len(self.buffer)/self.buffer.get_size()))

        # Update the user if the buffer overran
        if self.buffer.get_overruns(): self.b_overrun.set_checked(True)
                            
        if self.b_collect.is_checked(): 

            # Get the time spacing
            dt = 1.0/self.settings['sample_rate']

            # Total time
            T = 1.0/self.settings['PSD_resolution']                        
            N = _n.round(T/dt)           
            
            # Get all the packets we need            
            packets, overruns = self.get_packets(N, 1)
            
            # Assemble the packets            
            [x,y] = _n.concatenate(packets).transpose()
            
            # If we're supposed to trigger, find the first index at which
            # it crosses the threshold
            l   = self.p_raw_trigger_level.value()
            
            ns0 = _n.where(x<l)[0]
            if len(ns0) and self.b_trigger.is_checked():
                
                # first value below trigger
                n0  = ns0[0]

                # indices after n0 where we're above the trigger
                ns1 = _n.where(x[n0:]>l)[0]+n0

                # If we have a crossing                
                if(len(ns1)):  t  = _n.arange(-ns1[0]*dt,(-ns1[0]+len(x)-0.5)*dt, dt) 
                else:          t = _n.arange(0, (len(x)-0.5)*dt, dt)    
            else:
                t = _n.arange(0, (len(x)-0.5)*dt, dt)

            # Plot Raw
            self.p_raw['t'] = t
            self.p_raw['Nx'] = x
            self.p_raw['Ny'] = y
            self.settings.send_to_databox_header(self.p_raw)            
            self.p_raw.plot()

            # Plot Volts
            self.p_volts['t'] = t
            self.p_volts['Vx'] = x*self.settings['voltage_cal']*10**(-0.05*self.settings['gain'])
            self.p_volts['Vy'] = y*self.settings['voltage_cal']*10**(-0.05*self.settings['gain'])
            self.settings.send_to_databox_header(self.p_volts)            
            self.p_volts.plot()
            
            # PSD
            if self.p_psd.button_enabled.is_checked():
                
                # Do the PSD
                f, Px = _s.fun.psd(t[0:N], self.p_volts['Vx'][0:N], True)
                self.p_psd.h(Px0 = Px[0])
                f  = f[1:]
                Px = Px[1:]

                # Reset the counter if the length or frequency range has changed
                if len(self.p_psd) \
                and (not len(self.p_psd[0]) == len(f) or not self.p_psd[0][-1] == f[-1]):
                    self.n_psd_counter.set_value(0)
                    self.p_psd.clear()

                # Make sure we have the data arrays
                if len(self.p_psd) == 0: 
                    self.p_psd['f_Hz'] = f
                    self.p_psd['Px']   = Px

                # Do the average
                n = self.n_psd_counter.get_value()
                self.p_psd['f_Hz'] = f
                self.p_psd['Px']   = (self.p_psd['Px']*n + Px)/(n+1)
                self.settings.send_to_databox_header(self.p_psd)
                self.p_psd.plot()
            
                # increment the psd counter
                if self.settings['PSD_averages'] == 0 or n+1 <= self.settings['PSD_averages']:
                    self.n_psd_counter.increment()
                else:
                    self.n_psd_counter.set_value(0)
                    self.b_collect.set_checked(False)
            
            self.docker.process_events()

    def get_gain(self):             return (126-self._crimson.get_gain())/4
    def get_bandwidth(self):        return self._crimson.get_bandwidth()
    def get_center_frequency(self): return self._crimson.get_center_freq()
    def get_sample_rate(self):      return self._crimson.get_samp_rate()
    
    def set_sample_rate(self, sample_rate=48e3): 
        """
        Sets the sample rate (on all channels) and returns the actual rate.
        """
        self._crimson.set_samp_rate(sample_rate)
        return self.get_sample_rate()
    
    def set_center_frequency(self, center_frequency=1e7, channel=0):
        """
        Sets the center (demodulation) frequency and returns the actual value.
        """
        self._crimson.set_center_freq(center_frequency, channel)
        return self.get_center_frequency()
    
    def set_gain(self, gain=0, channel=0):
        """
        Sets the gain (in dB) and returns the actual value.
        """
        self._crimson.set_gain(gain, channel)
        return self.get_gain()
    
    def set_bandwidth(self, bandwidth=5000, channel=0):
        """
        Sets the demodulation (IF port) bandwidth and returns the actual value.
        """
        self._crimson.set_bandwidth(bandwidth, channel)
        return self.get_bandwidth()

    def hide(self):  return self.docker.hide()
    def show(self):  return self.docker.show()
    



if __name__ == '__main__':   
    c = jax_data_streamer() 
