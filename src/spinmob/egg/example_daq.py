import numpy   as _n
import time    as _t
import spinmob as _s
from spinmob import egg



##### GUI DESIGN

# create the main window
w = egg.gui.Window(autosettings_path='example_daq_w.cfg')

# add the "go" button
b = w.place_object(egg.gui.Button("Pretend to Acquire Data", checkable=True)).set_width(135)
i = w.place_object(egg.gui.NumberBox(int=True)).set_width(50)

# add a tabbed interface for the plotting area, spanning the first and second rows
tabs = w.place_object(egg.gui.TabArea(), row_span=2, alignment=0)

# add a tab for some plots
t1 = tabs.add_tab("Plots")
t2 = tabs.add_tab("Analysis")

# add a databox plotter object to the tab
d1 = t1.place_object(egg.gui.DataboxPlot(autosettings_path='example_daq_p1.cfg'), alignment=0)
d2 = t2.place_object(egg.gui.DataboxPlot(autosettings_path='example_daq_p2.cfg'), alignment=0)

# move to the second row and add a TreeDictionary for
# our "settings"
w.new_autorow()
s = w.place_object(egg.gui.TreeDictionary('example_daq_s.cfg'), column_span=2)



##### DATA OBJECTS

# add various parameters to use later
s.add_parameter("settings/simulated_input/iterations", value=0,            type='int')
s.add_parameter("settings/simulated_input/channels",   value=3,            type='int',   limits=(1, 8))
s.add_parameter("settings/simulated_input/duration",   value=0.02,         type='float', limits=(0.001,None), dec=True, siPrefix=True, suffix='s')
s.add_parameter("settings/simulated_input/points",     value=1000,         type='int',   limits=(2,    None))
s.add_parameter("settings/simulated_input/source",     value="cos(500*t)", type='str')
s.add_parameter("settings/simulated_input/noise",      value=0.2,          type='float')
s.add_parameter("settings/other_stuff/name",           value="moose",      type='str')
s.add_parameter("settings/other_stuff/quality",        value="round",      type='list', values=["round", "faceted", "regular moose"])

# load previous settings if they exist
s.load()



##### FUNCTIONALITY

# define a function to create fake data
# this is where you might put code for
# talking to a daq card or sillyscope
def get_fake_data():

    # try to evaluate the source script
    try:
        # first get all the extra numpy globals
        g = _n.__dict__

        # update these globals with extra stuff needed for evaluation
        g.update(dict(t=d1[0]+s["settings/simulated_input/noise"]*_n.random.rand()))
        y = eval(s["settings/simulated_input/source"], g)+_n.random.random(len(d1['t']))

    # default to zeros
    except:
        print("ERROR: Invalid source script.")
        y = d1[0]*0.0

    # pretend this acquisition actually took time (avoids black holes)
    _t.sleep(s["settings/simulated_input/duration"])

    return y


# define a function to be called whenever the acquire button is pressed
def acquire_button_clicked(*a):

    # don't start another loop if the button is unchecked!
    if not b.is_checked(): return

    # reset the counter
    i.set_value(0)

    print("Sarting fake acquisition loop...")

    # start the loop and keep looping until someone
    # unchecks the acquisition button or we max out the iterations
    # setting iterations = 0 will loop infinitely
    while b.is_checked()                                          \
    and (i.get_value() < s["settings/simulated_input/iterations"] \
         or s["settings/simulated_input/iterations"] == 0):

        # reset the databox
        d1.clear()
        d2.clear()
        
        # all the information to the databox headers
        s.send_to_databox_header(d1)
        s.send_to_databox_header(d2)

        # create the fake time data
        d1['t'] = _n.linspace(0,s["settings/simulated_input/duration"], s["settings/simulated_input/points"])

        # create the fake channel data and do some analysis on it
        for n in range(s["settings/simulated_input/channels"]):

            # get the channel name
            c = 'ch'+str(n)

            # create the data
            d1[c] = get_fake_data()
            
            # get a power spectral density
            d2['f'], d2[c] = _s.fun.psd(d1['t'], d1[c])
            
        # increment the counter
        i.increment()

        # update the plot (note updating d1 updates p1.databox by reference)
        # and autosave (only does anything if this is enabled on the gui)
        d1.plot(); d1.autosave()
        d2.plot(); d2.autosave()
        
        # process other window events so the GUI doesn't freeze
        w.process_events()

    # in case the button is still checked
    b.set_checked(False)

    print("Fake acquisition stopped.")

# connect the button
b.signal_clicked.connect(acquire_button_clicked)

# Define a function to save the settings whenever
# they change and connect the signal
def settings_changed(*a): s.save()

# connecting is a little different for TreeDictionaries
s.connect_any_signal_changed(settings_changed)



# overwrite the existing shutdown / destroy sequence
def shutdown():
    print("Closing but not destroying...")
    b.set_checked(False)
    return
w.event_close = shutdown

# show the window!
w.show(True)