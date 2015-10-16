from spinmob import egg

# create the window and two tab areas
w          = egg.gui.Window('Hey Guy II', autosettings_path='w.cfg')
t_settings = w.place_object(egg.gui.TabArea()).add_tab("Settings")
t_raw_data = w.place_object(egg.gui.TabArea()).add_tab("Raw Data")

# make the "data" tab preferentially fill the area
w.set_column_stretch(1)


# show it!
w.show()




# Add tree dictionary
s = t_settings.place_object(egg.gui.TreeDictionary('s.cfg'))

# add some settings
s.add_parameter('DAQ/Rate',      1000,      type='float', step=1000, suffix='Hz', siPrefix=True, limits=[1,1e5])
s.add_parameter('DAQ/Pants',        0,      type='list',  values=['required','optional'])
s.add_parameter('Other/Function', 'cos(t)', type='str')

# load the previous settings if they exist.
s.load()

# need to define this function to auto-save when settings change
def s_changed(*a): s.save()
s.connect_any_signal_changed(s_changed)




# Add the raw databox plotter
d = t_raw_data.place_object(egg.gui.DataboxPlot(autosettings_path='d.cfg'))
d.load_gui_settings()

# Add some data / header info
d['t']  = [1,2,3,4,5]
d['V1'] = [1,2,1,2,1]
d['V2'] = [2,1,2,1,2]
d.h(Time="Pants O'Clock", Amp_Gain="32")

# Plot it
d.plot()

# Overload the post-data-load function to send header info to s
def after_load_file(d): s.update(d.headers, ignore_errors=True)
d.after_load_file = after_load_file



