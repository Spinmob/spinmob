import numpy as _n          # This library adds all kinds of numerical functions
import spinmob.egg as egg   # this is our graphical window builder






#########################################
### Main window
#########################################

# Create a "sleg" window with the title 'Hello World!'
# This will not automatically show the window (see below)
window = egg.gui.Window('Hello World!', autosettings_path='example_other_widgets_window.cfg')

# make the second column the one that grows the most when resizing
window.set_column_stretch(1,100)

# top row (sub grid of misc controls defined below)
top_row = window.place_object(egg.gui.GridLayout(False), 0,0, column_span=2)




#########################################
### Buttons and file dialogs.
#########################################

# define a dummy functions to catch signals from buttons etc
def dummy_function(a): print("dummy function received argument:", a)
def open_files(a):     print(egg.dialogs.load_multiple(filters="*.txt"))

# add a buttons to the layout at grid position 0,0 (upper-left corner)
b0 = top_row.place_object(egg.gui.Button("File Dialog"), 0,0)

# connect the button's "clicked" signal to a function
window.connect(b0.signal_clicked, open_files)



#########################################
### Number box
#########################################

# make a number box, set its width
n = top_row.place_object(egg.gui.NumberBox(), 7,0, alignment=2)
n.set_width(50)

# connect this control's "changed" signal to the dummy function
# note: this is same as using window.connect() above.
window.connect(n.signal_changed, dummy_function)


#########################################
### Line Edit
#########################################
top_row.place_object(egg.gui.TextBox("TextBox Object."),8,0)


#########################################
### Toggle button
#########################################

# This button will toggle when pressed.
# The function it fires will receive its current state.
bt = top_row.place_object(egg.gui.Button("Checkable").set_checkable(), 5,0, alignment=1)

# yet another method to connect to a function
bt.signal_clicked.connect(dummy_function)


#########################################
### Label
#########################################

l = top_row.place_object(egg.gui.Label("Some text goes here."), 6,0, alignment=1)


#########################################
### pyqtgraph line plot and data taking
#########################################

# add a line plot in the second row
p1 = window.place_object(egg.pyqtgraph.PlotWidget(), 0,1)

# create a "box" to hold data and header information
data = egg.data.databox()

def acquire_fake_data(number_of_points=1000):
    """
    This function generates some fake data and returns two channels of data
    in the form

    time_array, [channel1, channel2]
    """
    # time array
    t = _n.linspace(0,10,number_of_points)

    return(t, [_n.cos(t)*(1.0+0.2*_n.random.random(number_of_points)),
               _n.sin(t      +0.5*_n.random.random(number_of_points))])

# function to acquire and plot some fake data
def acquire_and_plot(*a):

    # acquire fake data
    t, [y1,y2] = acquire_fake_data(1000)

    # plot fake data
    p1.clear()
    p1.plot(t, y1, pen=(1,2))
    p1.plot(t, y2, pen=(2,2))

    # store the data in the databox
    data['t']  = t
    data['y1'] = y1
    data['y2'] = y2

    # add header information
    data.insert_header('numberbox_value', n.get_value())

# create a button to acquire / plot data
b1 = top_row.place_object(egg.gui.Button("Acquire"), 1,0)

# connect the button's "clicked" signal to the "acquire data" function
window.connect(b1.signal_clicked, acquire_and_plot)




#########################################
### Saving data (can also load)
#########################################

# function to save the databox we created above
def save_data(a): data.save_file(filters="*.txt")

b2 = top_row.place_object(egg.gui.Button("Save Data"), 2,0)
window.connect(b2.signal_clicked, save_data)



#########################################
### pyqtgraph image plot
#########################################

# add a color plot to the second row spanning the right-most columns
p2 = window.place_object(egg.pyqtgraph.ImageView(), 1,1)

# function to plot an image
def randomize_image(*a): # note that *a will catch any number of arguments
                         # and store them all in a "tuple"
    # create a 2D random array
    z = _n.random.rand(100,100)

    # set the image data in the plot (see pyqtgraph documentation)
    p2.setImage(z)

# randomize it
#randomize_image()

# add a randomizer button above it
b3 = top_row.place_object(egg.gui.Button("Randomize"), 3,0)

# connect b3's click to re-randomizing the plot
window.connect(b3.signal_clicked, randomize_image)





#########################################
### Tab Area
#########################################

# add a tab area to the 2nd row, spanning all columns
tabs = window.place_object(egg.gui.TabArea(), 0,2, column_span=2)

# add two tabs
t1 = tabs.add_tab("Parameter Tree!")
t2 = tabs.add_tab("More Plots!")
t3 = tabs.add_tab("Plain Table!")
t4 = tabs.add_tab("Table Dictionary!")

# connect some tab signals
window.connect(tabs.signal_switched,            dummy_function)

# this signal is sent when the user clicks the red "x" on the tab
window.connect(tabs.signal_tab_close_requested, tabs.remove_tab)

# add a button and a plot to the first tab
t2.place_object(egg.pyqtgraph.PlotWidget(),0,0)
t2.place_object(egg.pyqtgraph.PlotWidget(),1,0)





#########################################
### Table
#########################################

# add the table object to the second tab
table = t3.place_object(egg.gui.Table(2,10))
window.connect(table.signal_cell_changed, dummy_function)

# a function that plays with the table
def do_something(a):
    table.set_value(2,11, 'test')
    table.set_value(1,1,  2.3)
    print(table.get_value(1,1))

# make a button
bt = t3.place_object(egg.gui.Button("Do something."),1,0)

# make the button do something
window.connect(bt.signal_clicked, do_something)


#########################################
# Table dictionary (souped up table)
# I use this for header information
#########################################

# create the dictionary
d = t4.place_object(egg.gui.TableDictionary(), 0,0).set_column_width(0,200).set_column_width(1,400).set_width(602)

# setting and getting values
d['test']         = 32
d['another test'] = [3,2,5]
d['final test']   = d['test']+400

# other ways to set / get. All values must be valid python code or it turns pink.
d(more_stuff="'strings need quotes'", comment_on_code='"this must be valid python code"')


#########################################
### Modified parameter tree.
#########################################

# create the parameter tree
tree = t1.place_object(egg.gui.TreeDictionary())

tree.add_parameter('LOL_WUT', 32.5, type='float')
tree.add_parameter('Some Category/parameter', '32')
tree.add_parameter('Some Category/parameter2', values=dict(a=32,b=45,c=17), value=45, type='list')
tree.add_parameter('LOL_WUT/test', 'lsdkjf')

tree.add_parameter('Numbers/limits(min=-7_max=0)', -3, type='int', limits=(-7,0), step=0.1)
tree.add_parameter('Numbers/Units Too!', 1e-6, type='float', siPrefix=True, suffix='V', step=1e-4)

x=tree.add_button('Some Category/test button')
x.signal_clicked.connect(dummy_function)

#########################################
### Show the window
#########################################

# show it
window.show(True) 

# If launching in spyder, it's good to call it without "True", so that you
# can interact with the thing on the command line as well as graphically.
