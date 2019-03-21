from spinmob import egg

# create the window and two tab areas
w     = egg.gui.Window('Hey Mammal II', autosettings_path='w')
tabs1 = w.place_object(egg.gui.TabArea(autosettings_path='tabs1'))
tabs2 = w.place_object(egg.gui.TabArea(autosettings_path='tabs2'), alignment=0)

# add some tabs
t_settings  = tabs1.add_tab("Settings")
t_raw       = tabs2.add_tab("Raw")
t_processed = tabs2.add_tab("Processed")






###########################
# TREE DICTIONARY
###########################
settings = t_settings.place_object(egg.gui.TreeDictionary('settings'))

# add some settings
settings.add_parameter('DAQ/Rate',      1000,      type='float', step=1000, suffix='Hz', siPrefix=True, limits=[1,1e5])
settings.add_parameter('DAQ/Pants',        0,      type='list',  values=['required','optional'])
settings.add_parameter('Other/Function', 'cos(t)', type='str')



#############################
# Databox Plotter
#############################
d_raw = t_raw.place_object(egg.gui.DataboxPlot('*.raw', 'd_raw'), alignment=0)

# Add some ROIs
r1 = egg.pyqtgraph.LinearRegionItem([1.5,3.5])
r2 = egg.pyqtgraph.InfiniteLine(4.2, movable=True)
r3 = egg.pyqtgraph.InfiniteLine(4.2, movable=True)
d_raw.ROIs = [[r1,r2], r3]

# Add some data / header info
d_raw['t']  = [1,2,3,4,5]
d_raw['V1'] = [1,2,1,2,1]
d_raw['V2'] = [2,1,2,1,2]
d_raw.h(Time="Pants O'Clock", Amp_Gain="32")

# Plot it
d_raw.plot()

# Overload the post-data-load function to send header info to s
def after_load_file(d): settings.update(d.headers, ignore_errors=True)
d_raw.after_load_file = after_load_file




# show it!
w.show(True)
