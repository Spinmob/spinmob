import spinmob.egg as egg; gui = egg.gui
import numpy       as np



### CREATE THE GUI

# Make a window
window = gui.Window(autosettings_path='window')

# Add a grid on the left to hold a bunch of sliders
grid_left = window.add(gui.GridLayout(margins=False))

# Add the plot next to the grid
plot = window.add(gui.DataboxPlot(autosettings_path='plot'))

# Create sliders
slider1 = gui.Slider(bounds=[1,10], suffix='V', siPrefix=True, autosettings_path='slider1')
slider2 = gui.Slider(bounds=[1,10], autosettings_path='slider2', hide_numbers=True)

# Add the sliders
grid_left.add(slider1)
grid_left.new_autorow()
grid_left.add(slider2, alignment=0)

# Set the 3rd row to stretch so they are pushed to the top
grid_left.set_row_stretch(2)

# Show the window
window.show()

### LINK THE SLIDER CHANGE EVENT TO A FUNCTION

# Define a custom function to be triggered when something changes.
def f(value=0):
    """
    You could use the value of the slider, or just get the current values.
    But your function needs to have this 1 argument. :)
    """
    v1 = slider1.get_value()
    v2 = slider2.get_value()

    # Plot something new
    t  = np.linspace(0,3,10000)
    y1 = v1*t*t + t*np.cos(v1*v2*t)
    y2 = np.sin(v2*t)
    
    # Stick the data in the plotter
    plot.clear()
    plot['t'] = t
    plot['y1'] = y1
    plot['y2'] = y2
    
    # Plot it.
    plot.plot()

# Now assign this function to the change events.
slider1.event_changed = f
slider2.event_changed = f
    
# Call it once to make the initial plot
f()
