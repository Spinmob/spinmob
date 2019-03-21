import numpy as _n
import time  as _t
import spinmob.egg as egg



##### GUI DESIGN

# create the main window
w = egg.gui.Window(autosettings_path="example_sweeper_w")

# add the "go" button
b_sweep  = w.place_object(egg.gui.Button("Sweep!",         checkable=True))
b_select = w.place_object(egg.gui.Button("Use Blue Range", checkable=True))
l_x      = w.place_object(egg.gui.Label("x:"), alignment=2)
n_x      = w.place_object(egg.gui.NumberBox(int=False))

# move to the second row and add a TreeDictionary for our "settings"
w.new_autorow()
settings = w.place_object(egg.gui.TreeDictionary('example_sweeper_settings'), column_span=4, alignment=0)
settings.add_parameter('sweep/x_start', 0.0)
settings.add_parameter('sweep/x_stop',  0.004)
settings.add_parameter('sweep/x_steps', 200)

# add a tabbed interface for the plotting area, spanning the first and second rows
tabs = w.place_object(egg.gui.TabArea('example_sweeper_tabs'), 10,0, row_span=2, alignment=0)
w.set_column_stretch(10)

# add a tab for some plots
t_raw      = tabs.add_tab("Raw Plots")
t_analysis = tabs.add_tab("Analysis")

# add a databox plotter object to the tab
d_sweep = t_raw.place_object(egg.gui.DataboxPlot(autosettings_path="example_sweeper_d_sweep"), alignment=0)
d_sweep['x']     = []
d_sweep['mag']   = []
d_sweep['phase'] = []

# add a "region of interest" (ROI) for selecting the sweep range
roi_sweep = egg.pyqtgraph.LinearRegionItem([settings['sweep/x_start'], settings['sweep/x_stop']])
d_sweep.ROIs = [roi_sweep]

# show the blank plots
d_sweep.plot()


##### MAIN FUNCTIONALITY

# define a function to set some parameter on an external instrument
def set_x(x):
    """
    Pretends to set some instrument to a value "x" somehow.
    This is where your code should go.
    """

    # for now just update the gui
    n_x.set_value(x)

# define a function to create fake data.
# This is where you might put code for talking to a piece of equipment
def get_data():
    """
    Currently pretends to talk to an instrument and get back the magnitud
    and phase of the measurement.
    """

    # pretend we're measuring a noisy resonance at zero
    y = 1.0 / (1.0 + 1j*(n_x.get_value()-0.002)*1000) + _n.random.rand()*0.1

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

    # figure out the sweep range from the graph if we're supposed to
    if b_select.is_checked():
        settings['sweep/x_start'], settings['sweep/x_stop'] = roi_sweep.getRegion()

    # otherwise update the roi_sweep to match the sweep
    else: roi_sweep.setRegion((settings['sweep/x_start'],
                               settings['sweep/x_stop']))

    # clear the data and create new columns
    d_sweep.clear()
    d_sweep['x']     = []
    d_sweep['mag']   = []
    d_sweep['phase'] = []

    # dump the settings to the databox header
    settings.send_to_databox_header(d_sweep)

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
        d_sweep.append_data_point([x,m,p])

        # plot the data
        d_sweep.plot()

        # process other window events so the GUI doesn't freeze!
        w.process_events()

    # in case the button is still checked
    b_sweep.set_checked(False)

    # re-enable the settings
    settings.enable()

# connect the button
b_sweep.signal_clicked.connect(acquire_button_clicked)




######### OTHER GUI STUFF


# overwrite the post_load function so it plots and sets up the settings
def d_sweep_after_load():

    # dump the header into the settings
    settings.update(d_sweep, ignore_errors=True)

    # update the roi_sweep region
    roi_sweep.setRegion((settings['sweep/x_start'], settings['sweep/x_stop']))

# actually overwrite the existing function
d_sweep.after_load_file = d_sweep_after_load








# overwrite the existing shutdown / destroy sequence
def shutdown():
    print("Closing but not destroying...")
    b_sweep.set_checked(False)
    return
w.event_close = shutdown

if __name__ == '__main__':
    # show the window!
    w.show(True)