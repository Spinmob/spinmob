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
b_sweep  = w.add_object(egg.gui.Button("Sweep!",    checkable=True)).set_width(50)
b_select = w.add_object(egg.gui.Button("Selection", checkable=True)).set_width(70)
l_x      = w.add_object(egg.gui.Label("x:"), alignment=2)
n_x      = w.add_object(egg.gui.NumberBox(int=False))

# add a tabbed interface for the plotting area,
# spanning the first and second rows
tabs = w.add_object(egg.gui.TabArea(), row_span=2)

# add a tab for some plots
t_raw = tabs.add_tab("Raw Plots")

# add a databox plotter object to the tab
data_raw = t_raw.add_object(egg.gui.DataboxWithButtons(), alignment=0)
plot_ms  = t_raw.add_object(egg.pyqtgraph.PlotWidget(labels=dict(bottom='x', left='Magnitude')), 0,1, alignment=0)
plot_ps  = t_raw.add_object(egg.pyqtgraph.PlotWidget(labels=dict(bottom='x', left='Phase')),     0,2, alignment=0)

# link the axes
plot_ps.plotItem.setXLink(plot_ms.plotItem)

# move to the second row and add a TreeDictionary for
# our "settings"
w.new_autorow()
settings = w.add_object(egg.gui.TreeDictionary('example_sweeper.cfg'), column_span=4)
settings.add_parameter('sweep/x_start', -10, type='float')
settings.add_parameter('sweep/x_stop',   10, type='float')
settings.add_parameter('sweep/x_steps', 200, type='float')




##### DATA OBJECTS

# load previous settings if they exist
settings.load()

# add the selecty region
selection = egg.pyqtgraph.LinearRegionItem([settings['sweep/x_start'], settings['sweep/x_stop']])
plot_ms.addItem(selection)

# curves for the datasets
curve_ms = egg.pyqtgraph.PlotCurveItem(pen=(1,2))
curve_ps = egg.pyqtgraph.PlotCurveItem(pen=(2,2))

# add curves to the plots
plot_ms.addItem(curve_ms)
plot_ps.addItem(curve_ps)




##### MAIN FUNCTIONALITY

# define a function to set some parameter on an external instrument
def set_x(x):
    """
    Pretends to set some instrument to a value "x" somehow.
    This is where your code should go.
    """

    # for now just update the gui
    n_x.set_value(x)

# define a function to create fake data
# this is where you might put code for
# talking to a piece of equipment
def get_data():
    """
    Currently pretends to talk to an instrument and get back the magnitud
    and phase of the measurement.
    """

    # pretend we're measuring a noisy resonance at zero
    y = 1.0 / (1.0 + 1j*n_x.get_value()) + _n.random.rand()*0.1

    # and that it takes time to do so
    _t.sleep(0.1)

    # return mag phase
    return abs(y), _n.angle(y, True)


# define a function to be called whenever the acquire button is pressed
def acquire_button_clicked(*a):

    # don't start another loop if the button is unchecked!
    if not b_sweep.is_checked(): return

    # disable the settings during the sweep
    settings.disable()
    data_raw.disable_save()

    # we'll append the data as we roll it in
    xs = []
    ms = []
    ps = []

    # figure out the sweep range from the graph if we're supposed to
    if b_select.is_checked():
        settings['sweep/x_start'], settings['sweep/x_stop'] = selection.getRegion()

    # otherwise update the selection to match the sweep
    else:
        selection.setRegion((settings['sweep/x_start'], settings['sweep/x_stop']))

    # start the loop and keep looping until someone
    # unchecks the acquisition button or we max out the iterations
    # setting iterations = 0 will loop infinitely
    for x in _n.linspace(settings['sweep/x_start'],
                         settings['sweep/x_stop'],
                         settings['sweep/x_steps']):

        # make sure the button is still pressed
        if not b_sweep.is_checked(): break

        # set the current value
        set_x(x)

        # get the data
        m, p = get_data()

        # store the data
        xs.append(x)
        ms.append(m)
        ps.append(p)

        # update the curves
        curve_ms.setData(xs, ms)
        curve_ps.setData(xs, ps)

        # process other window events so the GUI doesn't freeze!
        w.process_events()

    # in case the button is still checked
    b_sweep.set_checked(False)

    # update the databox header
    k,d = settings.get_dictionary()
    data_raw.update_headers(d,k)

    # transfer the final data
    data_raw['x'] = xs
    data_raw['m'] = ms
    data_raw['p'] = ps

    # enable the save button
    data_raw.enable_save()

    # re-enable the settings
    settings.enable()


# connect the button
b_sweep.signal_clicked.connect(acquire_button_clicked)




######### OTHER GUI STUFF

# Define a function to save the settings whenever
# they change and connect the signal
def settings_changed(*a): settings.save()

# connecting is a little different for TreeDictionaries
settings.connect_any_signal_changed(settings_changed)



# overwrite the post_load function so it plots and sets up the settings
def data_raw_post_load():

    # dump the header into the settings
    settings.update(data_raw)

    # plot what we loaded.
    curve_ms.setData(data_raw['x'], data_raw['m'])
    curve_ps.setData(data_raw['x'], data_raw['p'])

    # update the selection region
    selection.setRegion((settings['sweep/x_start'], settings['sweep/x_stop']))

    # enable the save
    data_raw.enable_save()

# actually overwrite the existing function
data_raw.post_load = data_raw_post_load







# overwrite the existing shutdown / destroy sequence
def shutdown():
    print "Closing but not destroying..."
    b_sweep.set_checked(False)
    return
w.event_close = shutdown

# show the window!
w.show(True)