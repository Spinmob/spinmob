import spinmob.egg as egg

# Create a window with the title 'Hello World!'
w = egg.gui.Window('Hello World!')

# add a button at grid position 0,0 and a text label at 1,0
b = w.place_object(egg.gui.Button('Do something.'), 0,0)
t = w.place_object(egg.gui.Label ('<-- Push me.'),  1,0)

# create a function that changes the label text
def f(*args): t.set_text('Boom.')

# Connect the "button clicked" signal to the function
w.connect(b.signal_clicked, f)

# resize and show the window
w.set_size([250,100])
w.show(True)