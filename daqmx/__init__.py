import numpy     as _n
import PyDAQmx   as _mx
import traceback as _traceback

print("WARNING: This code will be phased out of Spinmob v3. You should be using NI's (new-ish) official python library anyway! This code will always be in Github's history if you need it, though.")

import spinmob as _s
_settings = _s.settings

from collections import Iterable

buffer_length = 10000
buffer_string = ' '*buffer_length
def strip_buffer(b): return b[0:b.index('\x00')]

debug_enabled = False
def debug(*args):
    if debug_enabled:
        for arg in args:
            print("  ", arg)


def error(message):
    print("\nERROR: "+message+"\n")



def get_device_names():
    """
    Returns a list of names of DAQ devices present on the system.
    """
    _mx.DAQmxGetSysDevNames(buffer_string, buffer_length)

    # massage the returned string
    device_names = strip_buffer(buffer_string).split(', ')

    # check that there are systems present!
    if device_names == ['']: device_names = []
        
    # now strip and split this thing to return a names.
    return device_names

def get_ai_channel_names(device_name):
    """
    Returns a list of names of input channels on device. Device can be
    an integer or a string name.
    """
    _mx.DAQmxGetDevAIPhysicalChans(device_name, buffer_string, buffer_length)
    return strip_buffer(buffer_string).split(', ')

def get_ao_channel_names(device_name):
    """
    Returns a list of names of input channels on device. Device can be
    an integer or a string name.
    """
    _mx.DAQmxGetDevAOPhysicalChans(device_name, buffer_string, buffer_length)

    names = strip_buffer(buffer_string).split(', ')
    if names == ['']:   return None
    else:               return names

def get_do_channel_names(device_name):
    """
    Returns a list of names of input channels on device. Device can be
    an integer or a string name.
    """
    _mx.DAQmxGetDevDOLines(device_name, buffer_string, buffer_length)

    names = strip_buffer(buffer_string).split(', ')
    if names == ['']:   return None
    else:               return names


def get_terminal_names(device_name):
    """
    Returns a list of terminal names (could be used for triggering). Device
    can be an integer or a string name.
    """
    _mx.DAQmxGetDevTerminals(device_name, buffer_string, buffer_length)

    names = strip_buffer(buffer_string).split(', ')
    if names == ['']:   return None
    else:               return names




class task_base:

    _handle  = None
    settings = {}

    def __init__(self, **kwargs):
        """
        This object provides a command-line interface for a DAQmx task.

        kwargs overwrites default self.settings dictionary.
        """

        # overwrite the defaults
        self(**kwargs)

        self._handle = _mx.TaskHandle()

        debug(self.settings)

    def __getitem__(self, key):
        """
        Returns a setting.
        """
        return self.settings[key]

    def __setitem__(self, key, value):
        """
        Sets a setting, but only if it's valid.
        """
        if key in list(self.settings.keys()):
            self.settings[key] = value
            self._post_setitem(key,value)

    def __call__(self, **kwargs):
        """
        Modifies settings based on kwargs.
        """
        for key in list(kwargs.keys()): self[key] = kwargs[key]

    def _post_setitem(self,key,value):
        """
        Can be overwritten to do some extra stuff after setting an item.
        """
        return

    def print_settings(self):
        """
        Lists all settings.
        """
        keys = list(self.settings.keys())
        keys.sort()

        print("Settings:")
        for k in keys: print('  ', k, '=', self.settings[k])

    def has_key(self, k):
        """
        Python-2 style function to see if a key exists.
        """
        return k in self.keys()

    


class ai_task(task_base):

    


    def __init__(self, **kwargs):
        """
        Task object for analog input. Typical workflow is to create one of
        these with the desired configuration (using kwargs, see below),
        starting it, then reading the acquired data and cleaning up, e.g.:
            
            ai = ai_task(...)
            ai.start()
            ai.read_and_clean()
        
        Note, when you set ai_rate and start(), this will automatically
        query the actual rate and update ai_rate internally!        
        
        Parameters
        ----------
        "ai_task_name"      : "Default AI Task",
        "ai_rate"           : 10000,
        "ai_mode"           : _mx.DAQmx_Val_FiniteSamps,
        "ai_samples"        : 1000,
        "ai_delay"          : 0,
        "ai_timeout"        : 1000.0/10000.0 + 3.0,
        
        "ai_clock_source"   : "",
        "ai_clock_edge"     : _mx.DAQmx_Val_Rising,
        "ai_trigger_source" : "UNSPECIFIED: ai_trigger_source",
        "ai_trigger_slope"  : _mx.DAQmx_Val_RisingSlope,
        
        "ai_channels"          : [0],
        "ai_input_couplings"   : [None], 
        "ai_min"               : -10.0,
        "ai_max"               : 10.0,
        "ai_terminal_config"   : _mx.DAQmx_Val_Cfg_Default, # also DAQmx_Val_RSE, NRSE, Diff
        "ai_units"             : _mx.DAQmx_Val_Volts

        """
        self.settings = dict(
                       {"ai_task_name"      : "Default AI Task",
                        "ai_rate"           : 10000,
                        "ai_mode"           : _mx.DAQmx_Val_FiniteSamps,
                        "ai_samples"        : 1000,
                        "ai_delay"          : 0,
                        "ai_timeout"        : 1000.0/10000.0 + 3.0,
                        
                        "ai_clock_source"   : "",
                        "ai_clock_edge"     : _mx.DAQmx_Val_Rising,
                        "ai_trigger_source" : "UNSPECIFIED: ai_trigger_source",
                        "ai_trigger_slope"  : _mx.DAQmx_Val_RisingSlope,
                        
                        "ai_channels"          : [0],
                        "ai_input_couplings"   : [None], 
                        "ai_min"               : -10.0,
                        "ai_max"               : 10.0,
                        "ai_terminal_config"   : _mx.DAQmx_Val_Cfg_Default, # also DAQmx_Val_RSE, NRSE, Diff
                        "ai_units"             : _mx.DAQmx_Val_Volts})

        # make sure this key exists in kwargs
        if not "ai_channels"        in kwargs: kwargs["ai_channels"]        = self["ai_channels"]    
        if not "ai_input_couplings" in kwargs: kwargs["ai_input_couplings"] = self["ai_input_couplings"]
        
        # make sure ai_channels is a list
        x = kwargs["ai_channels"]
        if not hasattr(x, '__iter__'): kwargs["ai_channels"] = [x]

        # make sure it's iterable
        kwargs["ai_input_couplings"] = _s.fun.equalize_list_lengths(kwargs["ai_input_couplings"], kwargs["ai_channels"])    
        
        # Note this overwrites the entries in self.settings
        task_base.__init__(self, **kwargs)
    
        

    def start(self, test=False, **kwargs):
        """
        1. Creates a task using settings.
        2. Starts the task.
        3. Fetches data.

        You need to call read_and_clean() after start().

        kwargs are sent to self() to set parameters.
        """
        
        # update any last-minute settings
        self(**kwargs)
        debug(self.settings)


        # create the task object. This doesn't return an object, because
        # National Instruments. Instead, we have this handle, and we need
        # to be careful about clearing the thing attached to the handle.
        debug("input task handle")
        _mx.DAQmxClearTask(self._handle)
        _mx.DAQmxCreateTask(self["ai_task_name"], _mx.byref(self._handle))

        # Loop over all the input channel names and create a channel for each
        debug("input channels")
        for n in range(len(self["ai_channels"])):

            # get the channel-specific attributes
            name     = self["ai_channels"][n]
            nickname = name.replace("/","")
            debug(name)

            if isinstance(self["ai_terminal_config"], Iterable):
                  ai_terminal_config = self["ai_terminal_config"][n]
            else: ai_terminal_config = self["ai_terminal_config"]

            if isinstance(self["ai_min"], Iterable):
                  ai_min = self["ai_min"][n]
            else: ai_min = self["ai_min"]

            if isinstance(self["ai_max"], Iterable):
                  ai_max = self["ai_max"][n]
            else: ai_max = self["ai_max"]

            if isinstance(self["ai_units"], Iterable):
                  ai_units   = self["ai_units"][n]
            else: ai_units   = self["ai_units"]

            # add an input channel
            debug(name)
            _mx.DAQmxCreateAIVoltageChan(self._handle, name, nickname, ai_terminal_config,
                                         ai_min, ai_max, ai_units, "")
            
            # set the input coupling (optional)
            if not self["ai_input_couplings"] == None:
                ai_input_coupling = self["ai_input_couplings"][n]
                if ai_input_coupling == "AC" : _mx.DAQmxSetAICoupling(self._handle, name, _mx.DAQmx_Val_AC)
                if ai_input_coupling == "DC" : _mx.DAQmxSetAICoupling(self._handle, name, _mx.DAQmx_Val_DC)
                if ai_input_coupling == "GND": _mx.DAQmxSetAICoupling(self._handle, name, _mx.DAQmx_Val_GND)

        # Configure the clock
        debug("input clock")

        # make sure we don't exceed the max
        ai_max_rate = _mx.float64()
        _mx.DAQmxGetSampClkMaxRate(self._handle, _mx.byref(ai_max_rate))
        if self['ai_rate'] > ai_max_rate.value:
            print("ERROR: ai_rate is too high! Current max = "+str(ai_max_rate.value))
            self.clean()            
            return False

        _mx.DAQmxCfgSampClkTiming(self._handle, self["ai_clock_source"], self["ai_rate"],
                                  self["ai_clock_edge"], self["ai_mode"], self["ai_samples"])

        
        # get the actual ai_rate
        ai_rate = _mx.float64()
        _mx.DAQmxGetSampClkRate(self._handle, _mx.byref(ai_rate))
        debug("input actual ai_rate =", ai_rate.value)
        self(ai_rate=ai_rate.value)

        # Configure the trigger
        debug("input trigger")
        _mx.DAQmxCfgDigEdgeStartTrig(self._handle,
                                     self.settings["ai_trigger_source"],
                                     self.settings["ai_trigger_slope"])

        # Set the post-trigger delay
        try:
            n = self["ai_delay"] * 10e6
            if n < 2: n=2
            _mx.DAQmxSetStartTrigDelayUnits(self._handle, _mx.DAQmx_Val_Ticks)
            _mx.DAQmxSetStartTrigDelay     (self._handle, n)
        except:
            _traceback.print_exc()
        
        # in test mode, just check that it doesn't fail and clean up.
        if test: self.clean()

        # otherwise, start the show!
        else:
            debug("input start")
            try:
                _mx.DAQmxStartTask(self._handle)
            except:
                _traceback.print_exc()

        return True

    def read_and_clean(self):
        """
        This should be called after start().

        Collects data from the running task, cleans up, then returns the data.
        """

        # Fetch the data
        debug("fetch data")
        array_size = self["ai_samples"]*len(self["ai_channels"])

        # create the array in which to store the data
        data       = _n.zeros(array_size, dtype=_n.float64)
        bytes_read = _mx.int32()

        # read the data
        debug("_handle", self._handle)
        _mx.DAQmxReadAnalogF64(
            self._handle,                    # handle to the task
            self["ai_samples"],              # number of samples per channel (-1 => Read ALL in Buffer)
            self["ai_timeout"],              # timeout (sec)
            _mx.DAQmx_Val_GroupByChannel,    # how to fill the data array
            data,                            # array to fill
            array_size,                      # array size (samples)
            _mx.byref(bytes_read),           # samples per channel actually read
            None)                            # "reserved"

        # clean up the task
        self.clean()

        #Organize the data
        data =  _n.split(data, len(self["ai_channels"]))
        return data

    def clean(self):
        """
        Cleans up the task, frees memory etc...
        """
        # cleanup
        debug("clear input task")
        _mx.DAQmxClearTask(self._handle)




class ao_task(task_base):

    _handle  = _mx.TaskHandle()
    def __init__(self, **kwargs):
        """
        Creates a task to output analog waveforms. Typical workflow is 
        to create the task of the desired configuration (see below), 
        start it, then clean it up, e.g.:
            
            ao = ao_task()       # creates the task. kwargs set settings
            ao.start()           # starts the task
            ao.wait_and_clean()  # waits until the task is done and cleans up
        
        Note, when you set ao_rate and start(), this will automatically
        query the actual rate and update ao_rate internally!        
        
        Parameters
        ----------
        "ao_task_name"      : "Default Output Task",
        "ao_mode"           : _mx.DAQmx_Val_FiniteSamps,
        "ao_timeout"        : 10.0,

        "ao_channels"       : [0],
        "ao_rate"           : 10000,
        "ao_delay"          : 0,
        "ao_waveforms"      : [[1,2,3,0]],
        "ao_min"            : -10.0,
        "ao_max"            : 10.0,
        "ao_units"          : _mx.DAQmx_Val_Volts,

        "ao_clock_source"   : "",
        "ao_clock_edge"     : _mx.DAQmx_Val_Rising,

        "ao_trigger_source" : "UNSPECIFIED: ao_trigger_source",
        "ao_trigger_slope"  : _mx.DAQmx_Val_RisingSlope,
        
        "ao_export_signal"   : _mx.DAQmx_Val_StartTrigger,
        "ao_export_terminal" : None}
        """
        
        self.settings = dict(
               {"ao_task_name"      : "Default Output Task",
                "ao_mode"           : _mx.DAQmx_Val_FiniteSamps,
                "ao_timeout"        : 10.0,

                "ao_channels"       : [0],
                "ao_rate"           : 10000,
                "ao_delay"          : 0,
                "ao_waveforms"      : [[1,2,3,0]],
                "ao_min"            : -10.0,
                "ao_max"            : 10.0,
                "ao_units"          : _mx.DAQmx_Val_Volts,

                "ao_clock_source"   : "",
                "ao_clock_edge"     : _mx.DAQmx_Val_Rising,
        
                "ao_trigger_source" : "UNSPECIFIED: ao_trigger_source",
                "ao_trigger_slope"  : _mx.DAQmx_Val_RisingSlope,
                
                "ao_export_signal"   : _mx.DAQmx_Val_StartTrigger,
                "ao_export_terminal" : None})
            
        # make sure ao_channels is a list
        x = kwargs["ao_channels"]
        if not hasattr(x, '__iter__'): kwargs["ao_channels"] = [x]

        task_base.__init__(self, **kwargs)

        
        

    def start(self, test=False, **kwargs):
        """
        1. Creates a task using settings.
        2. Starts the task.

        You need to call wait_and_clean() after you start()

        kwargs are sent to self() to set parameters.
        """

        self(**kwargs)

        # make sure everything that should be a list is a list
        if not isinstance(self["ao_channels"], Iterable):
            self["ao_channels"]  = [self["ao_channels"]]

        # if the first element of the waveform is not an array
        if len(_n.shape(self["ao_waveforms"][0])) < 1:
            self["ao_waveforms"] = [self["ao_waveforms"]]

        # create the task object. This doesn't return an object, because
        # National Instruments. Instead, we have this handle, and we need
        # to be careful about clearing the thing attached to the handle.
        debug("output task handle")
        _mx.DAQmxClearTask(self._handle)
        _mx.DAQmxCreateTask(self["ao_task_name"], _mx.byref(self._handle))

        # create all the output channels
        debug("output channels")

        # this is an array of output data arrays, grouped by channel
        samples = 0
        data    = _n.array([])

        # loop over all the channels
        for n in range(len(self["ao_channels"])):

            # get the channel-specific attributes
            name     = self["ao_channels"][n]
            nickname = name.replace("/","")

            debug(name)

            if isinstance(self["ao_min"], Iterable): ao_min = self["ao_min"][n]
            else:                                    ao_min = self["ao_min"]

            if isinstance(self["ao_max"], Iterable): ao_max = self["ao_max"][n]
            else:                                    ao_max = self["ao_max"]

            if isinstance(self["ao_units"], Iterable): ao_units = self["ao_units"][n]
            else:                                      ao_units = self["ao_units"]

            waveform = self["ao_waveforms"][n]

            # add an output channel
            _mx.DAQmxCreateAOVoltageChan(self._handle, name, nickname,
                                         ao_min, ao_max, ao_units, "")

            # add the corresponding output wave to the master data array
            debug ("data", data, "waveform", waveform)
            data = _n.concatenate([data, waveform])

            # Set the samples number to the biggest output array size
            samples = max(len(self["ao_waveforms"][n]), samples)


        # Configure the clock
        debug("output clock")

        # make sure we don't exceed the max
        #ao_max_rate = _mx.float64()
        #_mx.DAQmxGetSampClkMaxRate(self._handle, _mx.byref(ao_max_rate))
        #if self['ao_rate'] > ao_max_rate.value:
        #    print "ERROR: ao_rate is too high! Current max = "+str(ao_max_rate.value)
        #    self.clean()
        #    return False
        
        _mx.DAQmxCfgSampClkTiming(self._handle, self["ao_clock_source"], self["ao_rate"],
                                  self["ao_clock_edge"], self["ao_mode"], samples)

        # if we're supposed to, export a signal
        if not self['ao_export_terminal'] == None:
            _mx.DAQmxExportSignal(self._handle, self['ao_export_signal'], self['ao_export_terminal'])

        

        # update to the actual ao_rate (may be different than what was set)
        ao_rate = _mx.float64()
        _mx.DAQmxGetSampClkRate(self._handle, _mx.byref(ao_rate))
        debug("output actual ao_rate =", ao_rate.value)
        self(ao_rate=ao_rate.value)

        # Configure the trigger
        debug("output trigger")
        _mx.DAQmxCfgDigEdgeStartTrig(self._handle, self["ao_trigger_source"], self["ao_trigger_slope"])

        # Set the post-trigger delay
        try:
            n = self["ao_delay"] * 10e6
            if n < 2: n=2
            _mx.DAQmxSetStartTrigDelayUnits(self._handle, _mx.DAQmx_Val_Ticks)
            _mx.DAQmxSetStartTrigDelay     (self._handle, n)
        except:
            _traceback.print_exc()
        
        # write the data to the analog outputs (arm it)
        debug("output write", len(data))
        write_success = _mx.int32()
        _mx.DAQmxWriteAnalogF64(self._handle, samples, False, self["ao_timeout"],
                _mx.DAQmx_Val_GroupByChannel,   # Type of grouping of data in the array (for interleaved use DAQmx_Val_GroupByScanNumber)
                data,                           # Array of data to output
                _mx.byref(write_success),       # Output the number of successful write
                None)                           # Reserved input (just put in None...)
        debug("success:", samples, write_success)

        if test:
            self.clean()
        else:
            # Start the task!!
            debug("output start")
            try:
                _mx.DAQmxStartTask(self._handle)
            except:
                _traceback.print_exc()

        return True

    def wait_and_clean(self):
        """
        This should be called after start().

        Waits for the task to finish and then cleans up.
        """

        #Wait for the task to finish
        complete = _mx.bool32()
        while not (complete): _mx.DAQmxGetTaskComplete(self._handle, _mx.byref(complete))
        self.clean()


    def clean(self):
        """
        Clears the task and does whatever else we think is best practice.
        """
        # cleanup
        debug("clear output task")
        _mx.DAQmxClearTask(self._handle)






class daqmx_system:


    def __init__(self):
        """
        This object's job is to provide a command-line interface for all the
        DAQmx devices on the system.
        """

        # get a names of devices on the system
        self.device_names = self.get_device_names()

        # create a databox to hold everything
        self.databox = _s.data.databox()

        # print the info
        print(self.__repr__())


    def __getitem__(self, device):
        """
        Accepts either integer or device name. Returns device name.
        """
        if isinstance(device, int): return self.device_names[device]
        else:                               return device

    def __repr__(self):
        if self.device_names == []: return "\ndaq_system:\n  No DAQmx devices detected."
        else:
            s = "\ndaqmx_system devices"
            for n in range(len(self)):
                s = s+"\n  "+str(n)+": "+str(self.device_names[n])
        return s+'\n'

    def __len__(self): return len(self.device_names)

    def get_device_names(self):
        """
        Returns a list of names of DAQ devices present on the system.
        Also updates self.device_names
        """
        _mx.DAQmxGetSysDevNames(buffer_string, buffer_length)

        # massage the returned string
        self.device_names = strip_buffer(buffer_string).split(', ')

        # check that there are systems present!
        if self.device_names == ['']:
            self.device_names = []
            print("WARNING: No DAQmx devices detected.")

        # now strip and split this thing to return a names.
        return self.device_names

    def get_ai_channel_names(self, device):
        """
        Returns a list of names of input channels on device. Device can be
        an integer or a string name.
        """
        _mx.DAQmxGetDevAIPhysicalChans(self[device], buffer_string, buffer_length)
        return strip_buffer(buffer_string).split(', ')

    def get_ao_channel_names(self, device):
        """
        Returns a list of names of input channels on device. Device can be
        an integer or a string name.
        """
        _mx.DAQmxGetDevAOPhysicalChans(self[device], buffer_string, buffer_length)

        names = strip_buffer(buffer_string).split(', ')
        if names == ['']:   return None
        else:               return names

    def get_terminal_names(self, device):
        """
        Returns a list of terminal names (could be used for triggering). Device
        can be an integer or a string name.
        """
        _mx.DAQmxGetDevTerminals(self[device], buffer_string, buffer_length)

        names = strip_buffer(buffer_string).split(', ')
        if names == ['']:   return None
        else:               return names

    def ai_single_device(self, device=0,
                         ai_channels=[0,3], ai_time=0.1, ai_rate=10000,
                         ai_min=[-10,-10],  ai_max=[10,10], **kwargs):
        """
        Performs an on-demand single-shot readout of the specified channels and
        returns the data. Also stores data in self.databox

        device=0                Which device to use. Can be an index or a
                                device string.
        ai_channels=[0,3]       Which channels to read in (by index). This can
                                be a list or a single number.
        ai_time=0.1             How long to take data (seconds)

        **kwargs are sent to daq_input_task()
        """

        # clear the data. This could be used as a thread check.
        d = self.databox
        d.clear()

        # if ai_channels is a single element, make it into a list.
        if not isinstance(ai_channels, Iterable): ai_channels = [ai_channels]

        # turn the indices into strings
        ai_channel_names          = self.get_ai_channel_names(device)
        if not ai_channel_names:
            error("No AI channels present!")
            return

        # add all the selected channels to the list
        ai_selected_channel_names = []
        for n in range(len(ai_channels)):
            ai_selected_channel_names.append(ai_channel_names[ai_channels[n]])


        # save the header info
        d.h(ai_trigger_source = "/"+self[device]+"/100kHzTimebase",
            ai_channels = ai_selected_channel_names,     # names of channels
            ai_rate     = ai_rate,                       # acquisition rate
            ai_samples  = int(1.0*ai_rate*ai_time),      # number of samples
            ai_timeout  = ai_time + 3.0,                 # acquisition time + 3 seconds
            **kwargs)

        # create the task
        ai = ai_task(**d.headers)

        # start it!
        if ai.start():

            # store the time column
            d['t'] = _n.linspace(0, ai_time-1.0/ai['ai_rate'], ai['ai_samples'])

            # retrieve the data
            vs = ai.read_and_clean()

            # store the data
            for n in range(len(vs)): d[d.h('ai_channels')[n]] = vs[n]

        # Return databox. Could be empty.
        return d


    def ao_single_device(self, device=0, ao_channels=[0,1], ao_waveforms=['sin(t)', 'cos(t)'], ao_time=0.01, autozero=True, **kwargs):
        """
        Performs an on-demand single-shot analog out.

        device=0                Which device to use. Can be an index or a string.
        ao_channels=[0,1]       List of channels to use in (by index).
        ao_waveforms=[]         List of waveforms to send to ao_channels.

                                Each element can be a string function or data.

                                Constants can be used for the strings, such as
                                'sin(2*pi*f*t)' so long as pi and f are
                                supplied as keyword arguments.

        Example:
            ao_single_device(0, [1], ['sin(a*t)'], 0.1, a=2*3.14)

            will generate the waveform sin(2*3.14*t) for 0.1 seconds on device 0
            channel 1

        **kwargs are sent to ao_task()
        """

        # get a decent trigger name
        ao_trigger_source = "/"+self[device]+"/100kHzTimebase"
        debug(ao_trigger_source)

        debug(ao_waveforms)

        # turn the indices into strings
        ao_channel_names          = self.get_ao_channel_names(device)
        if not ao_channel_names:
            error("No AO channels present!")
            return

        ao_selected_channel_names = []
        for n in range(len(ao_channels)):
            ao_selected_channel_names.append(ao_channel_names[ao_channels[n]])

        # create the task
        ao = ao_task(ao_trigger_source = ao_trigger_source,
                     ao_channels       = ao_selected_channel_names,
                     **kwargs)

        # update with only the kwargs that already exist
        for key in list(kwargs.keys()):
            if key in ao: ao[key] = kwargs.pop(key)
        debug("remaining kwargs", kwargs)

        # loop over the waveforms and convert functions to
        for n in range(len(ao_waveforms)):
            if isinstance(ao_waveforms[n], str):

                # generate the time array
                kwargs['t'] = _n.linspace(0, ao_time, ao["ao_rate"]*ao_time)

                # evaluate the expression
                g = dict(_n.__dict__)
                g.update(kwargs)

                debug(ao_waveforms[n])
                ao_waveforms[n] = eval(ao_waveforms[n], g)

            # if we're supposed to, set the output to zero
            # we add two data points in case the daq card requires an even number of samples
            if autozero: ao_waveforms[n] = _n.concatenate([ao_waveforms[n],[0.0,0.0]])


        debug(ao_waveforms)

        # set the waveforms
        ao(ao_waveforms=ao_waveforms)

        # start it, and wait for it to finish
        if ao.start():
            ao.wait_and_clean()
            return True

        return False


    def ao_ai_single_device(self, device=0,
                            ai_channels=[0,3], ai_time=0.1, ai_rate=10000,
                            ai_min=[-10,-10],  ai_max=[10,10],
                            ao_channels=[0,1], ao_waveforms=['sin(20*t)', 'cos(20*t)'],
                            ao_time=0.1, ao_rate=1000,
                            ao_min=[-10,-10],  ao_max=[10,10],
                            autozero=True, enforce_even=True, **kwargs):
        """
        Performs an on-demand single-shot analog in and out.

        device = 0               Which device to use. Can be an index or a string.

        ai_channels  = [0,3]     Which input channels to use.
        ai_time      = 0.1       How long to acquire data (seconds).
        ai_rate      = 10000     Sampling rate.
        ai_min       = [-10,-10] Minimum volts. Can also be a single number as a shortcut.
        ai_max       = [ 10, 10] Maximum volts. Same.

        ao_channels  = [0,1]     List of channels to use in (by index).
        ao_waveforms = []        List of waveforms to send to ao_channels.

                                 Each element can be a string function or data.

                                 Constants can be used for the strings, such as
                                 'sin(2*pi*f*t)' so long as pi and f are
                                 supplied as keyword arguments.
        ao_time = 0.1            How long the output waveforms should last.
        ao_rate = 1000           Output sampling rate.
        ao_min  = [-10, -10]     Minimum volts for output. Can be a single number.
        ao_max  = [ 10,  10]     Maximum volts for output. Can be a single number.

        autozero= True           Set the output voltage to zero at the end. Can
                                 also be a list.

        Example:
            ao_single_device(0, [1], ['sin(a*t)'], 0.1, a=2*3.14)

            will generate the waveform sin(2*3.14*t) for 0.1 seconds on device 0
            channel 1
        """

        # clear out the databox
        d = self.databox
        d.clear()

        # make sure there are ai and ao channels
        ai_channel_names          = self.get_ai_channel_names(device)
        if not ai_channel_names:
            error("No AI channels present!")
            return

        ao_channel_names          = self.get_ao_channel_names(device)
        if not ao_channel_names:
            error("No AO channels present!")
            return



        ##### Create the output task

        # This keeps long-term memory from becoming a problem
        ao_waveforms = list(ao_waveforms)

        # turn the indices into strings
        ao_selected_channel_names = []
        for n in range(len(ao_channels)):
            ao_selected_channel_names.append(ao_channel_names[ao_channels[n]])

        # create the task
        ao = ao_task(ao_trigger_source = "/"+self[device]+"/100kHzTimebase",
                     ao_channels       = ao_selected_channel_names,
                     ao_rate           = ao_rate,
                     ao_min            = ao_min,
                     ao_max            = ao_max)

        # store the header info
        h = dict(ao.settings)
        h.pop('ao_waveforms')
        d.h(**h)

        # loop over the waveforms and convert functions to data
        for n in range(len(ao_waveforms)):
            if isinstance(ao_waveforms[n], str):

                # evaluate the expression
                g = dict(_n.__dict__)
                g['t'] = _n.arange(0, ao_time, 1.0/ao_rate)
                g.update(kwargs)

                debug(ao_waveforms[n])
                ao_waveforms[n] = eval(ao_waveforms[n], g)

            # if we're supposed to, set the output to zero
            # we add two data points in case the card is picky about even numbers
            if isinstance(autozero, Iterable) and autozero[n] or autozero==True:
                ao_waveforms[n] = _n.concatenate([ao_waveforms[n],[0.0,0.0]])
            else:
                ao_waveforms[n] = _n.concatenate([ao_waveforms[n],[ao_waveforms[n][-1],ao_waveforms[n][-1]]])

        # set the waveforms
        ao(ao_waveforms = ao_waveforms)



        ##### Create the input task

        # if ai_channels is a single element, make it into a list.
        if not isinstance(ai_channels, Iterable): ai_channels = [ai_channels]

        # turn the specified channel indices into strings
        ai_selected_channel_names = []
        for n in range(len(ai_channels)):
            ai_selected_channel_names.append(ai_channel_names[ai_channels[n]])

        # create the task and modify the default parameters
        ai = ai_task(ai_trigger_source    = "/"+self[device]+"/ao/StartTrigger",
                     ai_channels          = ai_selected_channel_names, # names of channels
                     ai_samples           = int(1.0*ai_rate*ai_time),  # number of samples
                     ai_timeout           = ai_time + 3.0,
                     ai_rate              = ai_rate,
                     ai_min               = ai_min,
                     ai_max               = ai_max)

        # store the header info
        d.h(**ai.settings)

        # get the time array from the actual rate
        d['t'] = _n.linspace(0, ai_time-1.0/ai['ai_rate'], ai['ai_samples'])

        # start the tasks
        ai.start()
        ao.start()

        # retrieve the data
        vs = ai.read_and_clean()

        # store the data
        for n in range(len(vs)): d[d.h('ai_channels')[n]] = vs[n]

        # clean up the ao task.
        ao.wait_and_clean()

        return d







#################
# EXAMPLE CODE
#################
if __name__ == "__main__":
    debug_enabled=False
    ai = ai_task()




