import numpy as _n
from spinmob import egg

# Create the window
w = egg.gui.Window("Hey, mammal.")

# Move it to the upper left corner (plus 17 pixels)
w.set_position([17,0])

# Add a button
b = egg.gui.Button("Fire!")
w.place_object(b)

# Modify the button using the "daisy chain"
b.set_text("Fire Once!")

# Define a basic function
def f(*a): print("Oooooh, received", a)

# Connect the button to f
w.connect(b.signal_clicked, f)

# Create a databox with load / save buttons and place it in the window
d = egg.gui.DataboxSaveLoad(autosettings_path='d.cfg')
w.place_object(d)

# Add some basic data, and enable the save button
d['x'] = [1,2,3]
d['y'] = [1,2,1]
d.enable_save()

# New auto-row
w.new_autorow()

# (Mis-)Place the graph
p = w.place_object(egg.pyqtgraph.PlotWidget())

# Re-place it properly
w.place_object(p, 0,1, column_span=2, alignment=0)

# Set the column stretch
w.set_column_stretch(1, 10)

# Add a curve to the graph
c = egg.pyqtgraph.PlotCurveItem()
p.addItem(c)

# Define a function to get fake data
def get_fake_data(*a):
    """
    Called whenever someone presses the "fire" button.
    """
    # add columns of data to the databox
    d['x'] = _n.linspace(0,10,100)
    d['y'] = _n.cos(d['x']) + 0.1*_n.random.rand(100)
    
    # update the curve    
    c.setData(d['x'], d['y'])
 
# Connect the button to this function
b.signal_clicked.connect(get_fake_data)

# Create a custom post_load function
def my_post_load(): 
    """
    Called after someone loads data using the "load" button.
    """    
    # update the curve with the loaded data    
    c.setData(d['x'], d['y'])

# Overwrite the existing (blank) post-load function
d.post_load = my_post_load

# Show the window (we block the command line so it can be run by double-clicking)
w.show(block_command_line=True)