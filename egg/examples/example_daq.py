import numpy as _n
import time  as _t
import spinmob.egg as egg



##### GUI DESIGN

# create the main window
w = egg.gui.Window()

# set the position on the screen and which column of the grid
# should dominate (column 1 will hold the tabbed plot area)
w.set_position([0,0])
w.set_column_stretch(1)

# add the "go" button
b = w.place_object(egg.gui.Button("Pretend to Acquire Data", checkable=True)).set_width(135)
i = w.place_object(egg.gui.NumberBox(int=True)).set_width(50)

# add a tabbed interface for the plotting area,
# spanning the first and second rows
tabs = w.place_object(egg.gui.TabArea(), row_span=2)

# add a tab for some plots
t = tabs.add_tab("Plots")

# add a databox plotter object to the tab
p = t.place_object(egg.gui.DataboxPlot())

# move to the second row and add a TreeDictionary for
# our "settings"
w.new_autorow()
s = w.place_object(egg.gui.TreeDictionary('example_acquisition.cfg'), column_span=2)



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

# create a databox to hold all the acquired data
d = egg.data.databox()



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
        g.update(dict(t=d[0]+s["settings/simulated_input/noise"]*_n.random.rand()))
        y = eval(s["settings/simulated_input/source"], g)+_n.random.random(len(d['t']))

    # default to zeros
    except:
        print "ERROR: Invalid source script."
        y = d[0]*0.0

    # pretend this acquisition actually took time (avoids black holes)
    _t.sleep(s["settings/simulated_input/duration"])

    return y


# define a function to be called whenever the acquire button is pressed
def acquire_button_clicked(*a):

    # don't start another loop if the button is unchecked!
    if not b.is_checked(): return

    # reset the counter
    i.set_value(0)

    print "Sarting fake acquisition loop..."

    # start the loop and keep looping until someone
    # unchecks the acquisition button or we max out the iterations
    # setting iterations = 0 will loop infinitely
    while b.is_checked()                                          \
    and (i.get_value() < s["settings/simulated_input/iterations"] \
         or s["settings/simulated_input/iterations"] == 0):

        # reset the databox
        d.clear()
        d.update_headers(s.get_dictionary()[1], s.get_dictionary()[0])

        # create the fake time data
        d['t'] = _n.linspace(0,s["settings/simulated_input/duration"], s["settings/simulated_input/points"])

        # create the fake channel data
        for n in range(s["settings/simulated_input/channels"]):
            d['ch'+str(n)] = get_fake_data()

        # increment the counter
        i.increment()

        # update the plot
        p.plot(d)

        # process other window events so the GUI doesn't freeze!
        w.process_events()

    # in case the button is still checked
    b.set_checked(False)

    print "Fake acquisition stopped."

# connect the button
b.signal_clicked.connect(acquire_button_clicked)

# Define a function to save the settings whenever
# they change and connect the signal
def settings_changed(*a): s.save()

# connecting is a little different for TreeDictionaries
s.connect_any_signal_changed(settings_changed)



# overwrite the existing shutdown / destroy sequence
def shutdown():
    print "Closing but not destroying..."
    b.set_checked(False)
    return
w.event_close = shutdown

# show the window!
w.show(True)