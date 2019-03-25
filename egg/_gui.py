import time     as _t
import os       as _os
import numpy    as _n
from sys import platform as _platform

import spinmob as _spinmob
_d = _spinmob.data

# import pyqtgraph and create the App.
import pyqtgraph as _g

# If imported by spinmob
try:    from . import _temporary_fixes

# If running the file directly
except: import _temporary_fixes


_a = _g.mkQApp()

# set the font if we're in linux
if _platform in ['linux', 'linux2']: _a.setFont(_g.QtGui.QFont('Arial', 8))

_defaults = dict(margins=(10,10,10,10))


# Get the current working directory and keep it! Dialogs change this on the fly
_cwd = _os.getcwd()



# HACK FOR WEIRD BEHAVIOR WITH hasattr AND PYQTGRAPH OBJECTS. NO IDEA.
def hasattr_safe(x,a):
    try:
        x.a
        return True
    except:
        return False



class BaseObject(object):

    log = None

    def __init__(self):
        """
        Base object containing stuff common to all of our objects. When
        deriving objects from this, call BaseObject.__init__(self) as the
        LAST step of the new __init__ function.
        """
        # Parent object (to be set)
        self._parent = None

        # for remembering settings; for child objects, overwrite both, and
        # add a load_gui_settings() to the init!
        self._autosettings_path     = None
        self._autosettings_controls = []
        self._lazy_load    = dict()
        
        # common signals
        return

    def set_width(self, width):
        """
        Sets the width of the object. This is only valid for some controls, as
        it just uses self.setFixedWidth.
        """
        self._widget.setFixedWidth(width)
        return self

    def set_height(self, height):
        """
        Sets the width of the object. This is only valid for some controls, as
        it just uses self.setFixedHeight.
        """
        self._widget.setFixedHeight(height)
        return self

    def set_parent(self, parent):
        """
        Sets the parent object manually (usually this is done automatically
        when placing the object).
        """
        self._parent = parent

    def get_parent(self): 
        """
        Gets the parent object into which this object was placed.
        """        
        return self._parent
    
    def get_window(self): 
        """
        Returns the object's parent window. Returns None if no window found.
        """
        x = self
        while not x._parent == None and \
              not isinstance(x._parent, Window): 
                  x = x._parent
        return x._parent

    def process_events(self):
        """
        Processes pending GUI events. This just calls 
          
           self.get_window().process_events()
        
        so it requires the object to have been placed somewhere within a window.
        """
        self.get_window().process_events() 
        return self
        
    def sleep(self, seconds=0.05, dt=0.01):
        """
        A "smooth" version of time.sleep(): waits for the time to pass but
        processes events every dt as well.
        
        Note this requires that the object is either a window or embedded 
        somewhere within a window.
        """
        t0 = _t.time()
        while _t.time()-t0 < seconds:
            
            # Pause a bit to avoid heavy CPU
            _t.sleep(dt)
            
            # process events
            self.process_events()
    
    
    def block_events(self):
        """
        Prevents the widget from sending signals.
        """
        self._widget.blockSignals(True)
        self._widget.setUpdatesEnabled(False)

    def unblock_events(self):
        """
        Allows the widget to send signals.
        """
        self._widget.blockSignals(False)
        self._widget.setUpdatesEnabled(True)

    def disable(self):
        """
        Disables the widget.
        """
        self._widget.setEnabled(False)
        return self

    def enable(self):
        """
        Enables the widget.
        """
        self._widget.setEnabled(True)
        return self

    def print_message(self, message="heya!"):
        """
        If self.log is defined to be an instance of TextLog, it print the
        message there. Otherwise use the usual "print" to command line.
        """
        if self.log == None: print(message)
        else:                self.log.append_text(message)

    def save_gui_settings(self):
        """
        Saves just the current configuration of the controls if the
        autosettings_path is set.
        """
        
        # only if we're supposed to!
        if self._autosettings_path:

            # Get the gui settings directory
            gui_settings_dir = _os.path.join(_cwd, "gui_settings")

            # make sure the directory exists
            if not _os.path.exists(gui_settings_dir): _os.mkdir(gui_settings_dir)

            # make a path with a sub-directory
            path = _os.path.join(gui_settings_dir, self._autosettings_path)
            
            # for saving header info
            d = _d.databox()

            # add all the controls settings
            for x in self._autosettings_controls: self._store_gui_setting(d, x)

            # save the file
            d.save_file(path, force_overwrite=True)


    def load_gui_settings(self, lazy_only=False):
        """
        Loads the settings (if we're supposed to).
        
        Parameters
        ----------
        lazy_only=False
            If True, it will only load the settings into self._lazy_load, and
            not try to update the value. Presumably the widget will apply these
            settings later, e.g., when enough tabs exist to set the current
            tab in TabArea.
        """

        # only do this if we're supposed to
        if self._autosettings_path is not None:

            # Get the gui settings directory
            gui_settings_dir = _os.path.join(_cwd, "gui_settings")

            # assemble the path with a sub-directory
            path = _os.path.join(gui_settings_dir, self._autosettings_path)

            # databox just for loading a cfg file
            d = _d.databox()

            # if the settings path exists
            if _os.path.exists(path):
                
                # Load the settings
                d.load_file(path, header_only=True, quiet=True)

                # Store the settings in the lazy dictionary
                self._lazy_load.update(d.headers)
                
                # Loop over the settings we're supposed to change
                # Note without specifying d, this will try to pop
                # the value off of self._lazy_load. If 
                #
                if not lazy_only:
                    for x in self._autosettings_controls: 
                        self._load_gui_setting(x)

    def _load_gui_setting(self, key, d=None):
        """
        Safely reads the header setting and sets the appropriate control
        value. 
        
        Parameters
        ----------
        key
            Key string of the format 'self.controlname'.
        d = None
            Databox instance or dictionary, presumably containing the aforementioned
            key. If d=None, pops the value from self._lazy_load.
        """
        # Whether we should pop the value from the dictionary when we set it.
        pop_value = False
        
        # If d is None, assume we're using the lazy load settings.
        if d == None: 
            d = self._lazy_load
            pop_value = True
        
        # If we have a databox, take the header dictionary
        if not type(d) == dict: d = d.headers
        
        # only do this if the key exists
        if key in d:
            
            try:
                # Try to set the value
                eval(key).set_value(d[key])

                # If this fails, perhaps the element does not yet exist
                # For example, TabArea may not have all the tabs created
                # and cannot set the active tab until later.
                # If it's here, it worked, so pop if necessary
                if pop_value: d.pop(key)
           
            except: 
                print("ERROR: Could not load gui setting "+repr(key))

    def _store_gui_setting(self, databox, name):
        """
        Stores the gui setting in the header of the supplied databox.
        hkeys in the file are set to have the format
        "self.controlname"
        """
        try:    databox.insert_header(name, eval(name + ".get_value()"))
        except: print("ERROR: Could not store gui setting "+repr(name))



class GridLayout(BaseObject):

    '''
    This is a raw, unencapsulated grid layout upon which things like windows
    are built. 
    
    Parameters
    ----------
    margins
        Set to True or False to include the buffer around the layout's contents.
    '''
    
    log = None

    def __init__(self, margins=_defaults['margins']):
        """
        This creates a grid layout that can contain other Elements
        (including other grid and docked layouts)
        """

        BaseObject.__init__(self)

        # Qt widget to house the layout
        self._widget = _g.Qt.QtGui.QWidget()

        # Qt layout object
        self._layout = _g.Qt.QtGui.QGridLayout()

        # stick the layout into the widget
        self._widget.setLayout(self._layout)

        # auto-add row and column
        self._auto_row      = 0
        self._auto_column   = 0

        # 2D list of objects
        self.objects    = []

        # other useful functions to wrap
        self.get_row_count    = self._layout.rowCount
        self.get_column_count = self._layout.columnCount

        # remove margins if necessary
        if margins==False: self._layout.setContentsMargins(0,0,0,0)
        else:              self._layout.setContentsMargins(*margins)
        
        # Expose the show and hide functions
        # The attr check ensures classes inheriting this object's methods
        # don't have their show's and hide's overwritten 
        if not hasattr(self, 'show'): self.show = self._widget.show
        if not hasattr(self, 'hide'): self.hide = self._widget.hide
        


    def __getitem__(self, n): return self.objects[n]

    def block_events(self):
        """
        This will tell the window widget to stop processing events.
        """
        self._widget.blockSignals(True)
        self._widget.setUpdatesEnabled(False)

    def unblock_events(self):
        """
        This will tell the window widget to start processing events again.
        """
        self._widget.blockSignals(False)
        self._widget.setUpdatesEnabled(True)

    def place_object(self, object, column=None, row=None, column_span=1, row_span=1, alignment=1):
        """
        This adds either one of our simplified objects or a QWidget to the
        grid at the specified position, appends the object to self.objects.

        alignment=0     Fill the space.
        alignment=1     Left-justified.
        alignment=2     Right-justified.

        If column isn't specified, the new object will be placed in a new column.
        """

        # pick a column
        if column==None:
            column = self._auto_column
            self._auto_column += 1

        # pick a row
        if row==None: row = self._auto_row

        # create the object
        self.objects.append(object)

        # add the widget to the layout
        try:
            object._widget
            widget = object._widget

        # allows the user to specify a standard widget
        except: widget = object

        self._layout.addWidget(widget, row, column,
                               row_span, column_span,
                               _g.Qt.QtCore.Qt.Alignment(alignment))

        # try to store the parent object (self) in the placed object
        try:    object.set_parent(self)
        except: None

        return object

    def remove_object(self, object=0, delete=True):
        """
        Removes the supplied object from the grid. If object is an integer,
        it removes the n'th object.
        """
        if type(object) in [int, int]: n = object
        else:                           n = self.objects.index(object)

        # pop it from the list
        object = self.objects.pop(n)

        # remove it from the GUI and delete it
        if hasattr_safe(object, '_widget'):
            self._layout.removeWidget(object._widget)
            object._widget.hide()
            if delete: object._widget.deleteLater()
        else:
            self._layout.removeWidget(object)
            object.hide()
            if delete: object.deleteLater()

    def clear(self):
        """
        Removes all objects.
        """
        while len(self.objects): self.remove_object(0)
        return self


    def set_column_stretch(self, column=0, stretch=10):
        """
        Sets the column stretch. Larger numbers mean it will expand more to
        fill space.
        """
        self._layout.setColumnStretch(column, stretch)
        return self

    def set_row_stretch(self, row=0, stretch=10):
        """
        Sets the row stretch. Larger numbers mean it will expand more to fill
        space.
        """
        self._layout.setRowStretch(row, stretch)
        return self

    def new_autorow(self, row=None):
        """
        Sets the auto-add row. If row=None, increments by 1
        """
        if row==None: self._auto_row += 1
        else:         self._auto_row = row

        self._auto_column=0
        return self


    def print_message(self, message="heya!"):
        """
        If self.log is defined to be an instance of TextLog, it print the
        message there. Otherwise use the usual "print" to command line.
        """
        if self.log == None: print(message)
        else:                self.log.append_text(message)




class Window(GridLayout):

    """
    This class is a simplified Qt window builder. It behaves like a GridLayout
    encapsulated within a window object.

    Users are expected to use all properties not starting with an underscore,
    and all the underlying Qt objects have names starting with an underscore.
    
    Parameters
    ----------
    title='Window'
        Text for the window's title bar.
    size=[700,500]
        Starting size of the window. 
    autosettings_path=None
        If set to a file name, e.g. "w.txt", the window will create and update
        the file gui_settings/w.txt every time a window setting changes (e.g.,
        if you resize or move it.) Previous settings will be automatically
        loaded when the program is next run.
    margins
        Set to True or False to decide whether to include some buffer space 
        around the widgets in the window.
    
    """
        
    
    def __init__(self, title='Window', size=[700,500], autosettings_path=None, margins=_defaults['margins']):
        self._parent = self

        # initialize the grid layout
        GridLayout.__init__(self, margins=margins)
        
        # create the QtMainWindow,
        self._window = _g.Qt.QtGui.QMainWindow()
        self.set_size(size)
        self.set_title(title)
        
        #Set some docking options
        self._window.setDockOptions(_g.Qt.QtGui.QMainWindow.AnimatedDocks    | 
                                    _g.Qt.QtGui.QMainWindow.AllowNestedDocks | 
                                    _g.Qt.QtGui.QMainWindow.AllowTabbedDocks )

        # set the central widget to that created by GridLayout.__init__
        self._window.setCentralWidget(self._widget)

        # events
        self._window.closeEvent  = self._event_close
        self._window.resizeEvent = self._event_resize
        self._window.moveEvent   = self._event_move
        
        # autosettings path, to remember the window's position and size
        self._autosettings_path = autosettings_path

        # reload the last settings if they exist
        self._load_settings()

    

    def place_docker(self, docker, area='top'):
        """
        IN DEVELOPMENT        
        Places a DockWindow instance at the specified area ('top', 'bottom', 
        'left', 'right', or None)
        """
        # map of options
        m = dict(top    = _g.QtCore.Qt.TopDockWidgetArea,
                 bottom = _g.QtCore.Qt.BottomDockWidgetArea,
                 left   = _g.QtCore.Qt.LeftDockWidgetArea,
                 right  = _g.QtCore.Qt.RightDockWidgetArea)
        
        
        # set the parent
        docker.set_parent(self)

        # events
        docker._window.resizeEvent = self._event_resize
        docker._window.moveEvent   = self._event_move  

        # Keep it in the window        
        docker._window.setFeatures(docker._window.DockWidgetMovable)        
        
        # set it
        self._window.addDockWidget(m[area], docker._window)
        
        return docker

    def close(self):
        """
        Acts like we pressed the close button.
        """
        self._window.close()
        return self

    def event_close(self, *args, **kwargs):
        """
        Overwrite this function if you need to do a shutdown procedure.

        If you want to clean up, you are responsible for using
        self._window.deleteLater() appropriately. Otherwise it will just
        close the window.
        """
        self.print_message("Window closed but not destroyed. Use self.show() to bring it back.")

    def _event_close(self, event):
        """
        Don't modify this.
        """
        self._is_open = False
        self.event_close()

    def _event_resize(self, event):
        """
        Don't modify this.
        """
        self._save_settings()
        return

    def _event_move(self, event):
        """
        Don't modify this.
        """
        self._save_settings()
        return
        
    def _save_settings(self):
        """
        Saves all the parameters to a text file.
        """
        if self._autosettings_path == None: return
        
        # Get the gui settings directory
        gui_settings_dir = _os.path.join(_cwd, "gui_settings")

        # make sure the directory exists
        if not _os.path.exists(gui_settings_dir): _os.mkdir(gui_settings_dir)

        # make a path with a sub-directory
        path = _os.path.join(gui_settings_dir, self._autosettings_path)
        
        # Create a Qt settings object
        settings = _g.QtCore.QSettings(path, _g.QtCore.QSettings.IniFormat)
        settings.clear()
        
        # Save values
        if hasattr_safe(self._window, "saveState"):
            settings.setValue('State',self._window.saveState())
        settings.setValue('Geometry', self._window.saveGeometry())
        
    def _load_settings(self):
        """
        Loads all the parameters from a databox text file. If path=None,
        loads from self._autosettings_path.
        """
        if self._autosettings_path == None: return
        
        # Get the gui settings directory
        gui_settings_dir = _os.path.join(_cwd, "gui_settings")

        # make a path with a sub-directory
        path = _os.path.join(gui_settings_dir, self._autosettings_path)
        
        # make sure the directory exists
        if not _os.path.exists(path): return
        
        # Create a Qt settings object
        settings = _g.QtCore.QSettings(path, _g.QtCore.QSettings.IniFormat)
        
        # Load it up! (Extra steps required for windows command line execution)
        if settings.contains('State') and hasattr_safe(self._window, "restoreState"):    
            x = settings.value('State')
            if hasattr(x, "toByteArray"): x = x.toByteArray()            
            self._window.restoreState(x)
        
        if settings.contains('Geometry'): 
            x = settings.value('Geometry')
            if hasattr(x, "toByteArray"): x = x.toByteArray()
            self._window.restoreGeometry(x)        

    def connect(self, signal, function):
        """
        This will connect an signal associated with an object to a function.
        The first argument of the function must be the signal.

        For example, if b is a Button:

           self.connect(my_function, b.signal_clicked) or

        will result in calling print_everything(signal) whenever the button is
        clicked.

        To reduce coding complexity, you can also specify

           self.connect(my_function)

        A good route might be to have the function be a method of the object
        itself, so that it's clear which object is making noise.

        """
        signal.connect(function)
        return self

    
    def process_events(self):
        """
        Allows the GUI to update.
        """
        self._widget.update()
        _a.processEvents()
        return self

    def set_position(self, position=[0,0]):
        """
        This sets the position of the window in pixels, with the upper-left
        corner being [0,0].
        """
        self._window.move(position[0], position[1])
        return self


    def set_size(self, size=[1000,650]):
        """
        Sets the window size in pixels.
        """
        self._window.resize(size[0],size[1])
        return self


    def set_title(self, title='Window'):
        """
        Sets the title of the window.
        """
        self._window.setWindowTitle(title)
        return self


    def show(self, block_command_line=False, block_timing=0.05):
        """
        Shows the window and raises it.

        If block_command_line is 0, this will start the window up and allow you
        to monkey with the command line at the same time. Otherwise, the
        window will block the command line and process events every
        block_timing seconds.
        """

        self._is_open = True
        self._window.show()
        self._window.raise_()

        # start the blocking loop
        if block_command_line:

            # stop when the window closes
            while self._is_open:
                _a.processEvents()
                _t.sleep(block_timing)

            # wait a moment in case there is some shutdown stuff.
            _t.sleep(0.5)

        return self

    def hide(self):
        """
        Hides the window.
        """
        self._window.hide()
        return self

class Docker(Window):

    log = None
    
    def __init__(self, name='Docker', size=[300,200], autosettings_path=None, margins=_defaults['margins']):
        """
        This creates a docked layout that can contain other object.
        
        All names must be unique within one project!
        """
        # This sets _widget and _layout
        Window.__init__(self)
        
        # create the docker widget        
        self._window = _g.Qt.QtGui.QDockWidget(name, None)
        self._window.setFeatures(self._window.DockWidgetFloatable |
                                 self._window.DockWidgetMovable   |
                                 self._window.DockWidgetClosable)
        
        # set unique name of dock
        self._window.setObjectName(name)
                      
        # Qt widget to house the layout
        self._widget = _g.Qt.QtGui.QWidget()

        # Qt layout object
        self._layout = _g.Qt.QtGui.QGridLayout()

        # stick the layout into the widget
        self._widget.setLayout(self._layout)

        # put all that widget junk in the docker
        self._window.setWidget(self._widget)
        
        # set margins if necessary
        if margins==False: self._layout.setContentsMargins(0,0,0,0)
        else:              self._layout.setContentsMargins(*margins)
        
        # Set the initial geometry
        self.set_size(size)
    
        # events
        self._window.moveEvent   = self._event_move
        self._window.resizeEvent = self._event_resize
        self._window.closeEvent  = self._event_close

        # autosettings path, to remember the window's position and size
        self._autosettings_path = autosettings_path
        
        # Load the previous settings
        self._load_settings()
        
        # other useful functions to wrap
        self.get_row_count    = self._layout.rowCount
        self.get_column_count = self._layout.columnCount        
        
        # Remove non-functional window stuff
        self.place_docker = self._disabled
         
    def _disabled(self):
        """
        This function is disabled for Docker object.
        """
        self.print_message("This function is disabled for Docker object.")
        return
        
    def show(self, block_command_line=False, block_timing=0.05):
        """
        Shows the window and raises it.

        If block_command_line is 0, this will start the window up and allow you
        to monkey with the command line at the same time. Otherwise, the
        window will block the command line and process events every
        block_timing seconds.
        """

        self._is_open = True
        self._window.show()
        self._window.raise_()

        # start the blocking loop
        if block_command_line:
            
            # stop when the window closes
            while self._is_open:
                _a.processEvents()
                _t.sleep(block_timing)

            # wait a moment in case there is some shutdown stuff.
            _t.sleep(0.5)

        return self

    

class Button(BaseObject):

    """
    This is a simplified button object. The underlying Qt object is stored as
    self._widget.
    
    Parameters
    ----------
    text="My Button! No!"
        Text to appear on the button.
    checkable=False
        Whether the button can be toggled or just pressed.
    checked=False
        Whether the initial state is checked.
    QPushButton=None
        Optionally, you can specify a QPushButton instance that it will use
        instead of creating a new one.
    
    Signals
    -------
    self.signal_clicked
        When the user has clicked and released the button.
    self.signal_toggled
        When the value has changed.
    """

    
    def __init__(self, text="My Button! No!", checkable=False, checked=False, QPushButton=None):
        
        # Qt button instance
        if QPushButton is None: self._widget = _g.Qt.QtGui.QPushButton(text)
        else:                   self._widget = QPushButton
    
        # signals
        self.signal_clicked = self._widget.clicked
        self.signal_toggled = self._widget.toggled

        # Other stuff common to all objects
        BaseObject.__init__(self)

        # set checkable
        self.set_checkable(checkable)
        if checkable: self.set_checked(checked)

        # aliases
        self.get_value = self.is_checked
        self.set_value = self.set_checked

        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide
        

    def is_checked(self):
        """
        Whether the button is pressed.
        """
        return self._widget.isChecked()
    
    def is_checkable(self):
        """
        Whether it's possible to check this button.
        """
        return self._widget.isCheckable()
        
    def set_checkable(self, checkable=True):
        """
        Set's the action of the button. If checkable=True, the button
        will stay pressed when you click it.
        """
        self._widget.setCheckable(checkable)
        return self

    def set_checked(self, value=True, block_events=False):
        """
        This will set whether the button is checked.

        Setting block_events=True will temporarily disable signals
        from the button when setting the value.
        """
        if block_events: self._widget.blockSignals(True)
        self._widget.setChecked(value)
        if block_events: self._widget.blockSignals(False)

        return self

    def set_text(self, text="MY Button. MINE."):
        """
        Sets the text of the button.
        """
        self._widget.setText(str(text))
        return self

    def sleep_until_unchecked(self, dt=0.1):
        """
        Waits while updating the gui until the button is unchecked.
        """
        while self.is_checked(): self.sleep(dt)
        return self
    
    def sleep_until_checked(self, dt=0.1):
        """
        Waits while updating the gui until the button is unchecked.
        """
        while not self.is_checked(): self.sleep(dt)
        return self

    def click(self):
        """
        Pretends to user clicked it, sending the signal and everything.
        """
        if self.is_checkable():        
            if self.is_checked(): self.set_checked(False)
            else:                 self.set_checked(True)
            self.signal_clicked.emit(self.is_checked())
        else:
            self.signal_clicked.emit(True)
        return self


class Label(BaseObject):

    def __init__(self, text="My Label. NO!"):
        """
        Simplified QLabel. Good for putting text somewhere.
        """

        # Create the widget
        self._widget = _g.Qt.QtGui.QLabel(text)

        # Other stuff common to all objects
        BaseObject.__init__(self)

    def get_text(self):
        """
        Gets the current value of the text.
        """
        return str(self._widget.text())

    def set_text(self, text="I said NO."):
        """
        Sets the text.
        """
        self._widget.setText(str(text))
        return self

    

    def set_style(self, *args, **kwargs):
        """
        Provides access to any number of style sheet settings via 
        self._widget.SetStyleSheet()
        
        *args can be any element between semicolons, e.g.
            self.set_stylesheet('text-align: right; padding-left: 5px')

        **kwargs can be any key-value pair, replacing '-' with '_' in the key, e.g.
            self.set_stylesheet(text_align='right', padding_left='5px')
            
        See QLabel.SetStyleSheet() documentation.
        """
        # assemble the string
        s = "QLabel {"
        for a in args:          s = s+a+"; "
        for k in list(kwargs.keys()): s = s+k.replace("_","-")+": "+kwargs[k]+"; "
        s = s+"}"
        
        # set it!
        self._widget.setStyleSheet(s)
        return self


class NumberBox(BaseObject):

    def __init__(self, value=0, step=1, bounds=(None,None), int=False, **kwargs):
        """
        Simplified number box with spinners. This is pyqtgraph's SpinBox().
        Extra keyword arguments are sent to the SpinBox.

        Parameters
        ----------
        value=0
            Initial value
        step=1
            Step size
        bounds=(None,None)
            Min and max values
        int=False
            Force the value to be an integer if True
        
        Some Common Keyword Arguments
        -----------------------------
        suffix=None    
            String value for units to display
        siPrefix=False
            True to add a prefix on units
        dec=False
            True means increments grow with the size of the number.
        minStep=None
            Minimum step when dec is True
        decimals    
            Number of decimals to display
        """

        # pyqtgraph spinbox
        self._widget = _temporary_fixes.SpinBox(value=value, step=step, bounds=bounds,
                                  int=int, **kwargs)

        # signals
        self.signal_changed = self._widget.sigValueChanging

        # Other stuff common to all objects
        BaseObject.__init__(self)

        # set a less ridiculous width
        self.set_width(70)
        
        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide
        

    def get_value(self):
        """
        Returns the current value of the number box.
        """
        return self._widget.value()

    def set_value(self, value, block_events=False):
        """
        Sets the current value of the number box.

        Setting block_events=True will temporarily block the widget from
        sending any signals when setting the value.
        """
        if block_events: self.block_events()
        self._widget.setValue(value)
        if block_events: self.unblock_events()

    def set_step(self, value, block_events=False):
        """
        Sets the step of the number box.

        Setting block_events=True will temporarily block the widget from
        sending any signals when setting the value.
        """
        if block_events: self.block_events()
        self._widget.setSingleStep(value)
        if block_events: self.unblock_events()


    def increment(self, n=1):
        """
        Increments the value by n.
        """
        self.set_value(self.get_value()+n)

    def set_colors(self, text='black', background='white'):
        """
        Sets the colors of the text area.
        """
        self._widget.setStyleSheet("SpinBox {background-color: "+background+"; color: "+text+"}")


class CheckBox(BaseObject):
    
    def __init__(self):
        """
        Simplified QCheckBox.
        """      
        # pyqt objects
        self._widget = _g.QtGui.QCheckBox()
        
        # signals
        self.signal_changed = self._widget.stateChanged
        
        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide
        
        
    def is_checked(self):
        """
        Check if checked.
        """
        return self._widget.checkState()
        
    def set_checked(self, value=True):
        """
        Set checkbox state.
        """
        self._widget.setCheckState(value)
        return self


class ComboBox(BaseObject):
    
    def __init__(self, items=['test','me']):
        """
        Simplified QComboBox.
        """
        
        # pyqt objects
        self._widget = _g.QtGui.QComboBox()
        
        # Populate it.
        for item in items: self.add_item(item)        
        
        # signals
        self.signal_activated = self._widget.activated       
        self.signal_changed   = self._widget.currentIndexChanged
        
        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide
        
        
    def add_item(self, text="ploop"):
        """
        Adds an item to the combobox.
        """
        self._widget.addItem(text)
        return self
        
    def remove_item(self, index=0):
        """
        Removes an item from the combobox.
        """        
        self._widget.removeItem(index)        
        return self
        
    def insert_separator(self,index=1):
        """
        Adds a separator to the combobox.
        """
        self._widget.insertSeparator(index)
        return self
        
    def get_index(self):
        """
        Gets current index.
        """
        return self._widget.currentIndex()
        
    def set_index(self,index=0):
        """
        Sets current index.
        """
        self._widget.setCurrentIndex(index)
        return self
        
    def get_text(self, index=None):
        """
        Gets text from a given index. If index=None, returns the current value
        self.get_text(self.get_value())
        """
        if index==None:
            return self.get_text(self.get_value())
        else:
            return str(self._widget.itemText(index))
    
    get_value = get_index
    set_value = set_index
    
    def get_all_items(self):
        """
        Returns all items in the combobox dictionary.
        """
        return [self._widget.itemText(k) for k in range(self._widget.count())]




class TabArea(BaseObject):

    """
    Simplified QTabWidget.
    
    Parameters
    ----------
    autosettings_path=None
        Set to a string file name to have this widget remember settings from 
        the previous run.
    tabs_closable=False
        Set to True to make the tabs closable (you still have to link the tab
        signals to a suitable close function, however.)
    """

    
    
    def __init__(self, autosettings_path=None, tabs_closable=False):
        
        # tab widget
        self._widget = _g.Qt.QtGui.QTabWidget()
        self._widget.setTabsClosable(tabs_closable)

        # tab widgets
        self.tabs = []

        # signals
        self.signal_switched             = self._widget.currentChanged
        self.signal_tab_close_requested  = self._widget.tabCloseRequested

        # connect signals
        self.signal_switched.connect(self._tab_changed)

        # Other stuff common to all objects
        BaseObject.__init__(self)

        # list of controls we should auto-save / load
        self._autosettings_path = autosettings_path
        self._autosettings_controls = ["self"]

        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide
        
        # Expose the count function
        self.get_tab_count = self._widget.count
        
        # Load the previous settings. Of course, we cannot set the tab
        # yet (no tabs added!), so only load into self._lazy_load
        self.load_gui_settings(lazy_only=True)
               

    def _tab_changed(self, *a): self.save_gui_settings()

    def __getitem__(self, n): return self.tabs[n]

    def add_tab(self, title="Yeah!", block_events=True):
        """
        Adds a tab to the area, and creates the layout for this tab.
        """
        self._widget.blockSignals(block_events)

        # create a widget to go in the tab
        tab = GridLayout()
        self.tabs.append(tab)
        tab.set_parent(self)

        # create and append the tab to the list
        self._widget.addTab(tab._widget, title)

        # try to lazy set the current tab
        if 'self' in self._lazy_load and self.get_tab_count() > self._lazy_load['self']:
            v = self._lazy_load.pop('self')
            self.set_current_tab(v)

        self._widget.blockSignals(False)

        return tab

    def remove_tab(self, tab=0):
        """
        Removes the tab by index.
        """

        # pop it from the list
        t = self.tabs.pop(tab)

        # remove it from the gui
        self._widget.removeTab(tab)

        # return it in case someone cares
        return t

    def get_current_tab(self):
        """
        Returns the active tab index.
        """
        return self._widget.currentIndex()

    get_value = get_current_tab

    def set_current_tab(self, n):
        """
        Returns the active tab index.
        """
        return self._widget.setCurrentIndex(n)

    set_value = set_current_tab

class Table(BaseObject):

    def __init__(self, columns=2, rows=1):
        """
        Simplified QTableWidget.
        """

        # create the widget
        self._widget = _g.Qt.QtGui.QTableWidget(rows, columns)

        # default behavior
        self.set_row_heights(18)
        self.set_header_visibility(False,False)

        # signals
        self.signal_cell_changed        = self._widget.cellChanged
        self.signal_cell_clicked        = self._widget.cellClicked
        self.signal_cell_double_clicked = self._widget.cellDoubleClicked

        # Other stuff common to all objects
        BaseObject.__init__(self)
        
        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide
        

    def clear(self):
        """
        Clears the table.
        """
        self._widget.clear()

    def get_column_count(self):
        """
        Returns the number of rows.
        """
        return self._widget.columnCount()

    def get_row_count(self):
        """
        Returns the number of rows.
        """
        return self._widget.rowCount()

    def get_value(self, column=0, row=0):
        """
        Returns a the value at column, row.
        """
        x = self._widget.item(row, column)

        if x==None: return x
        else:       return str(self._widget.item(row,column).text())

    def set_value(self, column=0, row=0, value='', block_events=False):
        """
        Sets the value at column, row. This will create elements dynamically,
        and in a totally stupid while-looping way.

        Setting block_events=True will temporarily block the widget from
        sending any signals when setting the value.
        """

        if block_events: self.block_events()

        # dynamically resize
        while column > self._widget.columnCount()-1: self._widget.insertColumn(self._widget.columnCount())
        while row    > self._widget.rowCount()   -1: self._widget.insertRow(   self._widget.rowCount())

        # set the value
        self._widget.setItem(row, column, _g.Qt.QtGui.QTableWidgetItem(str(value)))

        if block_events: self.unblock_events()

        return self

    def set_column_width(self, n=0, width=120):
        """
        Sets the n'th column width in pixels.
        """
        self._widget.setColumnWidth(n, width)
        return self

    def set_header_visibility(self, column=False, row=False):
        """
        Sets whether we can see the column and row headers.
        """
        if row:    self._widget.verticalHeader().show()
        else:      self._widget.verticalHeader().hide()

        if column: self._widget.horizontalHeader().show()
        else:      self._widget.horizontalHeader().hide()

        return self

    def set_row_height(self, n=0, height=18):
        """
        Sets the n'th row height in pixels.
        """
        self._widget.setRowHeight(n, height)
        return self

    def set_row_heights(self, height=18):
        """
        Sets the cell height for all cells in pixels.
        """
        self._widget.verticalHeader().setDefaultSectionSize(height)
        return self


class TableDictionary(Table):

    naughty = [' ','\t','\n',',']

    def __init__(self):
        """
        This is an enhanced version of Table() with two columns, containing
        key / value pairs. It is designed to behave somewhat like a python
        dictionary object, and has a specific use, namely to store settings
        for writing to a header file.

        The keys are strings none of the characters in self.naughty
        (these will be replaced). The dictionary
        can be sorted by key, alphabetically.

        The values must be python code that can be eval'd.
        """

        # Other stuff common to all objects
        Table.__init__(self, 2, 0)

        # signals
        self.signal_cell_changed        = self._widget.cellChanged
        self.signal_cell_clicked        = self._widget.cellClicked
        self.signal_cell_double_clicked = self._widget.cellDoubleClicked

        # default connections
        self.signal_cell_changed.connect(self._cell_changed)
        
        return

    def __len__(self): return self.get_row_count()

    def _clean_up_key(self, key):
        """
        Returns the key string with no naughty characters.
        """
        for n in self.naughty: key = key.replace(n, '_')
        return key

    def _cell_changed(self, *a):
        """
        Called whenever a cell is changed. Updates the dictionary.
        """

        # block all signals during the update (to avoid re-calling this)
        self.block_events()

        # loop over the rows
        for n in range(self.get_row_count()):

            # get the keys and values (as text)
            key   = self.get_value(0,n)
            value = self.get_value(1,n)

            # get rid of the None's
            if key   == None:
                key = ''
                self.set_value(0,n, '')
            if value == None:
                value = ''
                self.set_value(1,n, '')

            # if it's not an empty entry make sure it's valid
            if not key == '':

                # clean up the key
                key = self._clean_up_key(key)

                # now make sure the value is python-able
                try:
                    eval(value)
                    self._widget.item(n,1).setData(_g.QtCore.Qt.BackgroundRole, _g.Qt.QtGui.QColor('white'))
                except:
                    self._widget.item(n,1).setData(_g.QtCore.Qt.BackgroundRole, _g.Qt.QtGui.QColor('pink'))

        # unblock all signals
        self.unblock_events()

    def get_item(self, key):
        """
        Returns the value associated with the key.
        """
        keys = list(self.keys())

        # make sure it exists
        if not key in keys:
            self.print_message("ERROR: '"+str(key)+"' not found.")
            return None

        try:
            x = eval(self.get_value(1,keys.index(key)))
            return x

        except:
            self.print_message("ERROR: '"+str(self.get_value(1,keys.index(key)))+"' cannot be evaluated.")
            return None

    def __getitem__(self, key): return self.get_item(key)

    def keys(self):
        """
        Returns a sorted list of keys
        """
        keys = list()
        for n in range(len(self)):

            # only append the valid keys
            key = self.get_value()
            if not key in ['', None]: keys.append(key)

        return keys

    def set_item(self, key, value):
        """
        Sets the item by key, and refills the table sorted.
        """
        keys = list(self.keys())

        # if it exists, update
        if key in keys:
            self.set_value(1,keys.index(key),str(value))

        # otherwise we have to add an element
        else:
            self.set_value(0,len(self),   str(key))
            self.set_value(1,len(self)-1, str(value))


    def __setitem__(self, key, value): self.set_item(key, value)

    def update(self, dictionary=None, **kwargs):
        """
        Adds/overwrites all the keys and values from the dictionary.
        """
        if not dictionary == None: kwargs.update(dictionary)
        for k in list(kwargs.keys()): self[k] = kwargs[k]

    __call__ = update


class TextLog(BaseObject):

    def __init__(self):
        """
        Tired of print statements to the command line? Try this for dumping
        your log info.
        """
        self._widget = _g.QtGui.QTextEdit()

        # Other stuff common to all objects
        BaseObject.__init__(self)
        
        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide
        

    def get_text(self):
        """
        Returns all the text in the box.
        """
        return str(self._widget.toPlainText())

    def set_text(self, string=''):
        """
        Clears the box contents and sets the value to the supplied string.
        """
        self._widget.setText(string)

    def append_text(self, string=''):
        """
        Appends the supplied string to the existing text.
        """
        self._widget.append(string)


class TextBox(BaseObject):

    def __init__(self, text="", multiline=False):
        """
        Simplified QLineEdit.
        """
        self._multiline = multiline

        # pyqt objects
        if multiline:   self._widget = _g.QtGui.QTextEdit()
        else:           self._widget = _g.QtGui.QLineEdit(); self.signal_return_pressed = self._widget.returnPressed
        self.set_text(str(text))

        # signals
        self.signal_changed        = self._widget.textChanged
        #self.signal_return_pressed = self._widget.returnPressed

        # Other stuff common to all objects
        BaseObject.__init__(self)

        # aliases
        self.get_value = self.get_text
        self.set_value = self.set_text
        
        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide
        

    def get_text(self):
        """
        Returns the current text.
        """
        if self._multiline: return str(self._widget.toPlainText())
        else:               return str(self._widget.text())

    def set_text(self, text="YEAH."):
        """
        Sets the current value of the text box.
        """
        self._widget.setText(str(text))
        return self

    def set_colors(self, text='black', background='white'):
        """
        Sets the colors of the text area.
        """
        if self._multiline: self._widget.setStyleSheet("QTextEdit {background-color: "+str(background)+"; color: "+str(text)+"}")
        else:               self._widget.setStyleSheet("QLineEdit {background-color: "+str(background)+"; color: "+str(text)+"}")


class Timer():

    def __init__(self, interval_ms=500, single_shot=False):
        """
        Simplified QTimer. 
          
          interval_ms   in milliseconds
          single_shot   whether the timer fires only once
        """

        # pyqt objects
        self._widget     = _g.QtCore.QTimer(); 
        self.signal_tick = self._widget.timeout
        
        # aliases
        self.start        = self._widget.start
        self.stop         = self._widget.stop
        
        # Set the interval
        self.set_interval(interval_ms)
        self.set_single_shot(single_shot)

    def set_interval(self, interval_ms=500):
        """
        Set the interval for the ticks in milliseconds.
        """
        self._widget.setInterval(interval_ms)
        
        return self
        
    def set_single_shot(self, single_shot=True):
        """
        Sets whether the timer is single shot (one tick).
        """
        self._widget.setSingleShot(single_shot)


class TreeDictionary(BaseObject):
    """
    Simplified / Modified version of pyqtgraph's ParameterTree() object,
    designed to store databox-ready header information and settings.

    Main Changes
    ------------
     * simplified methods for setting parameters and getting them.
     * all parameter names must not have self.naughty characters.
     * autosettings_path is where the settings will be saved / loaded
       from when calling self.save() and self.load(). The settings
       file is just a databox with no data, and you can use other
       databox files.
     * Note: for the 'list' type, may have to specify a list of strings.
       Otherwise there will be confusion upon loading.

    Parameters
    ----------
    autosettings_path=None
        Where this object will save its settings when self.save() and self.load()
        are called without a path specified. None means no settings will be
        automatically saved.
    show_header=False
        Whether to show the top-level trunk.
        
    Signals
    -------
    self.connect_signal_changed(name, function)
        This will connect the change event for the specified parameter
        name to the specified function.
        
    self.connect_any_signal_changed(function) 
        This will connect the signal from anything changing to the specified 
        function. 
    """
    def __init__(self, autosettings_path=None, show_header=False):
        
        # Other stuff common to all objects
        BaseObject.__init__(self)
        
        self._widget             = _g.parametertree.ParameterTree(showHeader=show_header)
        self.naughty             = [' ', '\t', '\n', '\r', ',', ';']
        self._autosettings_path  = autosettings_path
        self._connection_lists   = dict()
        self._lazy_load = dict()
        
        # Load the previous settings (if any)
        self.load()
        
        # Connect any signal changing to the autosave
        self.connect_any_signal_changed(self.autosave)
        
        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide
        

    def __repr__(self):
        """
        How do display this object.
        """
        s = "\nTreeDictionary() -> "+str(self._autosettings_path)+"\n"

        for k in self.get_dictionary()[0]:
            
            if not self.get_type(k) in ['list']:
                s = s + "  "+k+" = "+repr(self[k])+"\n"
            else:
                s = s + "  "+k+" = "+repr(self[k])+" from "+repr(self.get_list_values(k)) + "\n"
        return s

    def block_events(self):
        """
        Special version of block_events that loops over all tree elements.
        """
        # block events in the usual way
        BaseObject.block_events(self)
        
        # loop over all top level parameters
        for i in range(self._widget.topLevelItemCount()):
            self._widget.topLevelItem(i).param.blockSignals(True)
        
        return self

    def unblock_events(self):
        """
        Special version of unblock_events that loops over all tree elements as well.
        """
        # unblock events in the usual way
        BaseObject.unblock_events(self)
        
        # loop over all top level parameters
        for i in range(self._widget.topLevelItemCount()):
            self._widget.topLevelItem(i).param.blockSignals(False)
        
        return self


    def connect_any_signal_changed(self, function):
        """
        Connects the "anything changed" signal for all of the tree to the
        specified function.
        
        Parameters
        ----------
        function
            Function to connect to this signal.
        """
        
        # loop over all top level parameters
        for i in range(self._widget.topLevelItemCount()):

            # make sure there is only one connection!
            try:
                self._widget.topLevelItem(i).param.sigTreeStateChanged.connect(
                                  function, type=_g.QtCore.Qt.UniqueConnection)
            except:
                pass
            
        return self

    def connect_signal_changed(self, name, function):
        """
        Connects a changed signal from the parameters of the specified name
        to the supplied function.
        """
        x = self._find_parameter(name.split("/"))

        # if it pooped.
        if x==None: return None

        # connect it
        x.sigValueChanged.connect(function)
        
        # Keep track of the functions
        if name in self._connection_lists: self._connection_lists[name].append(function)
        else:                              self._connection_lists[name] = [function]

        return self

    def block_user_signals(self, name, ignore_error=False):
        """
        Temporarily disconnects the user-defined signals for the specified 
        parameter name. 
        
        Note this only affects those connections made with 
        connect_signal_changed(), and I do not recommend adding new connections
        while they're blocked!
        """
        x = self._find_parameter(name.split("/"), quiet=ignore_error)

        # if it pooped.
        if x==None: return None
            
        # disconnect it from all its functions
        if name in self._connection_lists:
            for f in self._connection_lists[name]: x.sigValueChanged.disconnect(f)
        
        return self

    def unblock_user_signals(self, name, ignore_error=False):
        """
        Reconnects the user-defined signals for the specified 
        parameter name (blocked with "block_user_signal_changed")
        
        Note this only affects those connections made with 
        connect_signal_changed(), and I do not recommend adding new connections
        while they're blocked!
        """
        x = self._find_parameter(name.split("/"), quiet=ignore_error)

        # if it pooped.
        if x==None: return None
            
        # reconnect it to all its functions
        if name in self._connection_lists:
            for f in self._connection_lists[name]: x.sigValueChanged.connect(f)
        
        return self

    def _find_parameter(self, name_list, create_missing=False, quiet=False):
        """
        Tries to find and return the parameter of the specified name. The name
        should be of the form

        ['branch1','branch2', 'parametername']

        Setting create_missing=True means if it doesn't find a branch it
        will create one.

        Setting quiet=True will suppress error messages (for checking)
        """
        # make a copy so this isn't destructive to the supplied list
        s = list(name_list)

        # if the length is zero, return the root widget
        if len(s)==0: return self._widget

        # the first name must be treated differently because it is
        # the main widget, not a branch
        r = self._clean_up_name(s.pop(0))

        # search for the root name
        result = self._widget.findItems(r, _g.QtCore.Qt.MatchCaseSensitive | _g.QtCore.Qt.MatchFixedString)

        # if it pooped and we're not supposed to create it, quit
        if len(result) == 0 and not create_missing:
            if not quiet: self.print_message("ERROR: Could not find '"+r+"'")
            return None

        # otherwise use the first value
        elif len(result): x = result[0].param

        # otherwise, if there are more names in the list,
        # create the branch and keep going
        else:
            x = _g.parametertree.Parameter.create(name=r, type='group', children=[])
            self._widget.addParameters(x)

        # loop over the remaining names, and use a different search method
        for n in s:

            # first clean up
            n = self._clean_up_name(n)

            # try to search for the name
            try: x = x.param(n)

            # name doesn't exist
            except:

                # if we're supposed to, create the new branch
                if create_missing: x = x.addChild(_g.parametertree.Parameter.create(name=n, type='group', children=[]))

                # otherwise poop out
                else:
                    if not quiet: self.print_message("ERROR: Could not find '"+n+"' in '"+x.name()+"'")
                    return None

        # return the last one we found / created.
        return x



    def _clean_up_name(self, name):
        """
        Cleans up the name according to the rules specified in this exact
        function. Uses self.naughty, a list of naughty characters.
        """
        for n in self.naughty: name = name.replace(n, '_')
        return name

    def add_button(self, name, checkable=False, checked=False):
        """
        Adds (and returns) a button at the specified location. 
        """

        # first clean up the name
        name = self._clean_up_name(name)

        # split into (presumably existing) branches and parameter
        s = name.split('/')

        # make sure it doesn't already exist
        if not self._find_parameter(s, quiet=True) == None:
            self.print_message("Error: '"+name+"' already exists.")
            return None

        # get the leaf name off the list.
        p = s.pop(-1)

        # create / get the branch on which to add the leaf
        b = self._find_parameter(s, create_missing=True)

        # quit out if it pooped
        if b == None: return None

        # create the leaf object
        ap = _g.parametertree.Parameter.create(name=p, type='action')

        # add it to the tree (different methods for root)
        if b == self._widget: b.addParameters(ap)
        else:                 b.addChild(ap)

        # modify the existing class to fit our conventions
        ap.signal_clicked = ap.sigActivated

        # Now set the default value if any
        if name in self._lazy_load:
            v = self._lazy_load.pop(name)
            self.set_value(name, v)
        
        # Connect it to autosave (will only create unique connections)
        self.connect_any_signal_changed(self.autosave)
        
        return Button(name, checkable, checked, list(ap.items.keys())[0].button)

    def add_parameter(self, name='test', value=42.0, **kwargs):
        """
        Adds a parameter "leaf" to the tree. 
        
        Parameters
        ----------
        name='test'
            The name of the leaf. It should be a string of the form
            "branch1/branch2/parametername" and will be nested as indicated.
        value=42.0
            Value of the leaf.
        
        Common Keyword Arguments
        ------------------------
        type=None
            If set to None, type will be automatically set to type(value).__name__.
            This will not work for all data types, but is 
            a nice shortcut for floats, ints, strings, etc. 
            If it doesn't work, just specify the type manually (see below).
        values
            Not used by default. Only relevant for 'list' type, and should then
            be a list of possible values.
        step=1         
            Step size of incrementing numbers
        dec=False
            Set to True to enable decade increments.
        limits
            Not used by default. Should be a 2-element tuple or list used to 
            bound numerical values.
        default  
            Not used by default. Used to specify the default numerical value
        siPrefix=False
            Set to True to display units on numbers
        suffix
            Not used by default. Used to add unit labels to elements.
        

        See pyqtgraph ParameterTree for more options.
        """

        # update the default kwargs
        other_kwargs = dict(type=None)
        other_kwargs.update(kwargs)
        
        # Auto typing
        if other_kwargs['type'] == None: other_kwargs['type'] = type(value).__name__
        
        # Fix 'values' for list objects to be only strings
        if other_kwargs['type'] == 'list':
            for n in range(len(other_kwargs['values'])):
                other_kwargs['values'][n] = str(other_kwargs['values'][n])

        # split into (presumably existing) branches and parameter
        s = name.split('/')

        # make sure it doesn't already exist
        if not self._find_parameter(s, quiet=True) == None:
            self.print_message("Error: '"+name+"' already exists.")
            return self

        # get the leaf name off the list.
        p = s.pop(-1)

        # create / get the branch on which to add the leaf
        b = self._find_parameter(s, create_missing=True)

        # quit out if it pooped
        if b == None: return self

        # create the leaf object
        leaf = _g.parametertree.Parameter.create(name=p, value=value, **other_kwargs)
        
        # add it to the tree (different methods for root)
        if b == self._widget: b.addParameters(leaf)
        else:                 b.addChild(leaf)
        
        # Now set the default value if any
        if name in self._lazy_load:
            v = self._lazy_load.pop(name)
            self.set_value(name, v)
        
        # Connect it to autosave (will only create unique connections)
        self.connect_any_signal_changed(self.autosave)

        return self


    def _get_parameter_dictionary(self, base_name, dictionary, sorted_keys, parameter):
        """
        Recursively loops over the parameter's children, adding
        keys (starting with base_name) and values to the supplied dictionary
        (provided they do not have a value of None).
        """

        # assemble the key for this parameter
        k = base_name + "/" + parameter.name()

        # first add this parameter (if it has a value)
        if not parameter.value()==None:
            sorted_keys.append(k[1:])
            dictionary[sorted_keys[-1]] = parameter.value()

        # now loop over the children
        for p in parameter.children():
            self._get_parameter_dictionary(k, dictionary, sorted_keys, p)

    def send_to_databox_header(self, databox):
        """
        Sends all the information currently in the tree to the supplied
        databox's header, in alphabetical order. If the entries already
        exists, just updates them.
        """
        k, d = self.get_dictionary()
        databox.update_headers(d,k)

    def get_dictionary(self):
        """
        Returns the list of parameters and a dictionary of values
        (good for writing to a databox header!)

        Return format is sorted_keys, dictionary
        """

        # output
        k = list()
        d = dict()

        # loop over the root items
        for i in range(self._widget.topLevelItemCount()):

            # grab the parameter item, and start building the name
            x = self._widget.topLevelItem(i).param

            # now start the recursive loop
            self._get_parameter_dictionary('', d, k, x)

        return k, d

    def hide_parameter(self, name):
        """
        Hides the specified parameter.
        """
        self._find_parameter(name.split('/')).hide()

    def show_parameter(self, name):
        """
        Hides the specified parameter.
        """
        self._find_parameter(name.split('/')).show()        
        

    def get_widget(self, name):
        """
        Returns the Qt widget associated with the parameter.
        """
        return self._find_parameter(name.split('/'))

    def get_type(self, name):
        """
        Returns the type string of the specified parameter.
        """
        return str(self.get_widget(name).opts['type'])

    def get_value(self, name):
        """
        Returns the value of the parameter with the specified name.
        """
        # first clean up the name
        name = self._clean_up_name(name)

        # now get the parameter object
        x = self._find_parameter(name.split('/'))

        # quit if it pooped.
        if x == None: return None

        # get the value and test the bounds
        value  = x.value()
        
        # handles the two versions of pyqtgraph
        bounds = None
    
        # For lists, just make sure it's a valid value
        if x.opts['type'] == 'list':

            # If it's not one from the master list, choose
            # and return the default value.            
            if not value in x.opts['values']:
                
                # Only choose a default if there exists one                
                if len(x.opts('values')):                              
                    self.set_value(name, x.opts['values'][0])                
                    return x.opts['values'][0]
                
                # Otherwise, just return None and do nothing                
                else: return None

        # For strings, make sure the returned value is always a string.
        elif x.opts['type'] in ['str']: return str(value)
                
        # Otherwise assume it is a value with bounds or limits (depending on 
        # the version of pyqtgraph)    
        else:        
            if   'limits' in x.opts: bounds = x.opts['limits']
            elif 'bounds' in x.opts: bounds = x.opts['bounds']
            if not bounds == None:
                if not bounds[1]==None and value > bounds[1]: value = bounds[1]
                if not bounds[0]==None and value < bounds[0]: value = bounds[0]
            
        # return it        
        return value

    __getitem__ = get_value

    def get_list_values(self, name):
        """
        Returns the values for a list item of the specified name.
        """
        # Make sure it's a list
        if not self.get_type(name) in ['list']: 
            self.print_message('ERROR: "'+name+'" is not a list.')
            return
        
        # Return a copy of the list values
        return list(self.get_widget(name).opts['values'])

    def set_value(self, name, value, ignore_error=False, block_user_signals=False):
        """
        Sets the variable of the supplied name to the supplied value.

        Setting block_events=True will temporarily block the widget from
        sending any signals when setting the value.
        """
        # first clean up the name
        name = self._clean_up_name(name)

        # If we're supposed to, block the user signals for this parameter
        if block_user_signals: self.block_user_signals(name, ignore_error)        

        # now get the parameter object
        x = self._find_parameter(name.split('/'), quiet=ignore_error)

        # quit if it pooped.
        if x == None: return None
        
        # for lists, make sure the value exists!!
        if x.type() in ['list']:
            
            # Make sure it exists before trying to set it
            if str(value) in list(x.forward.keys()): x.setValue(str(value))
            
            # Otherwise default to the first key
            else: x.setValue(list(x.forward.keys())[0])
        
        # Bail to a hopeful set method for other types
        else: x.setValue(eval(x.opts['type'])(value))

        # If we're supposed to unblock the user signals for this parameter
        if block_user_signals: self.unblock_user_signals(name, ignore_error)

        return self

    __setitem__ = set_value

    def _signal_changed_handler(self, *args):
        """
        If we're supposed to autosave when something changes,
        do so.
        """
        self.print_message("signal change!")
        #if self.autosave: self.save()

    def autosave(self, *a):
        """
        Runs self.save() with no arguments. This is a convenience function;
        you can connect signals to it, such as with 
        self.connect_any_signal_changed()
        """
        self.save()

    def save(self, path=None):
        """
        Saves all the parameters to a text file using the databox
        functionality. If path=None, saves to self._autosettings_path. If
        self._autosettings_path=None, does not save.
        """
        if path==None: 
            
            if self._autosettings_path == None: return self
            
            # Get the gui settings directory
            gui_settings_dir = _os.path.join(_cwd, "gui_settings")

            # make sure the directory exists
            if not _os.path.exists(gui_settings_dir): _os.mkdir(gui_settings_dir)            
            
            # Assemble the path
            path = _os.path.join(gui_settings_dir, self._autosettings_path)
      
        # make the databox object
        d = _d.databox()

        # get the keys and dictionary
        keys, dictionary = self.get_dictionary()

        # loop over the keys and add them to the databox header
        for k in keys: 
            d.insert_header(k, dictionary[k])
            
        # save it
        d.save_file(path, force_overwrite=True, header_only=True)
        
        return self

    def load(self, path=None, ignore_errors=True, block_user_signals=False):
        """
        Loads all the parameters from a databox text file. If path=None,
        loads from self._autosettings_path (provided this is not None).
        
        Parameters
        ----------
        path=None
            Path to load the settings from. If None, will load from the 
            specified autosettings_path.
        ignore_errors=True
            Whether we should raise a stink when a setting doesn't exist.
            When settings do not exist, they are stuffed into the dictionary
            self._lazy_load.
        block_user_signals=False
            If True, the load will not trigger any signals.
        """
        if path==None: 
            
            # Bail if there is no path
            if self._autosettings_path == None: return self
            
            # Get the gui settings directory
            gui_settings_dir = _os.path.join(_cwd, "gui_settings")

            # Get the final path
            path = _os.path.join(gui_settings_dir, self._autosettings_path)
      
        # make the databox object
        d = _d.databox()

        # only load if it exists
        if _os.path.exists(path): d.load_file(path, header_only=True)
        else:                     return None

        # update the settings
        self.update(d, ignore_errors=ignore_errors, block_user_signals=block_user_signals)
        return self

    def update(self, d, ignore_errors=True, block_user_signals=False):
        """
        Supply a dictionary or databox with a header of the same format
        and see what happens! (Hint: it updates the existing values.)
        
        This will store non-existent key-value pairs in the dictionary 
        self._lazy_load. When you add settings in the future,
        these will be checked for the default values.
        """
        if not type(d) == dict: d = d.headers

        # Update the lazy load
        self._lazy_load.update(d)

        # loop over the dictionary and update
        for k in list(self._lazy_load.keys()):

            # Only proceed if the parameter exists
            if not self._find_parameter(k.split('/'), False, True) == None:

                # Pop the value so it's not set again in the future
                v = self._lazy_load.pop(k)
               
                # Set the value
                self._set_value_safe(k, v, ignore_errors, block_user_signals)

        return self

    def _set_value_safe(self, k, v, ignore_errors=False, block_user_signals=False):
        """
        Actually sets the value, first by trying it directly, then by 
        """
        # for safety: by default assume it's a repr() with python code
        try:
            self.set_value(k, v, ignore_error       = ignore_errors, 
                                 block_user_signals = block_user_signals)

        except:
            print("TreeDictionary ERROR: Could not set '"+k+"' to '"+v+"'")



class DataboxPlot(_d.databox, GridLayout):
    """
    A collection of common controls and functionality for plotting, saving, and
    loading data. This object inherits all databox functionality and adds
    a gui to the mix.

    ROIs for each plot can be stored in self.ROIs as a list (sub-lists allowed)

    Parameters
    ----------
    file_type="*.dat"
        What type of file to use for dialogs and saving.
    autosettings_path=None
        autosettings_path=None means do not automatically save the configuration
        of buttons / controls / script etc. Setting this to a path will cause
        DataboxPlot to automatically save / load the settings. Note you will
        need to specify a different path for each DataboxPlot instance.
    autoscript=1
        Sets the default autoscript entry in the combobox. Set to 0 for the 
        manual script, and 4 for the custom autoscript, which can be 
        defined by overwriting the function self.autoscript_custom, which 
        needs only return a valid script string.

    Note checking the "Auto-Save" button does not result in the data being automatically
    saved until you explicitly call self.autosave() (which does nothing
    unless auto-saving is enabled).
    """
    
    def __init__(self, file_type="*.dat", autosettings_path=None, autoscript=1, **kwargs):

        # Do all the parent class initialization; this sets _widget and _layout
        GridLayout.__init__(self, margins=False)
        _d.databox.__init__(self, **kwargs)

        # top row is main controls
        self.place_object(Label("Raw Data:"), alignment=1)
        self.button_clear    = self.place_object(Button("Clear")                 .set_width(50), alignment=1)
        self.button_load     = self.place_object(Button("Load")                  .set_width(50), alignment=1)
        self.button_save     = self.place_object(Button("Save")                  .set_width(50), alignment=1)
        self.combo_binary    = self.place_object(ComboBox(['Text', 'float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'complex64', 'complex128', 'complex256']), alignment=1)
        self.button_autosave = self.place_object(Button("Auto",   checkable=True).set_width(50), alignment=1)
        self.number_file     = self.place_object(NumberBox(int=True, limits=(0,None)))
        self._label_path     = self.place_object(Label(""))

        self.place_object(Label("")) # spacer
        self.button_script     = self.place_object(Button  ("Show Script", checkable=True)).set_checked(False)
        self.combo_autoscript  = self.place_object(ComboBox(['Manual Script', 'Autoscript 1', 'Autoscript 2', 'Autoscript 3', 'Custom'])).set_value(autoscript) 
        self.button_multi      = self.place_object(Button  ("Multi",       checkable=True).set_width(50)).set_checked(True) 
        self.button_link_x     = self.place_object(Button  ("Link X",      checkable=True).set_width(50)).set_checked(autoscript==1)
        self.button_enabled    = self.place_object(Button  ("Enabled",     checkable=True).set_width(50)).set_checked(True)

        # keep the buttons shaclackied together
        self.set_column_stretch(5)

        # second rows is the script
        self.new_autorow()

        # grid for the script
        self.grid_script = self.place_object(GridLayout(margins=False), 0,1, column_span=self.get_column_count(), alignment=0)

        # script grid
        self.button_plot  = self.grid_script.place_object(Button("Try it!").set_width(50), 2,3)
        self.script       = self.grid_script.place_object(TextBox("", multiline=True), 1,0, row_span=4, alignment=0)
        self.script.set_height(81)

        # make sure the plot fills up the most space
        self.set_row_stretch(2)

        # plot area
        self.grid_plot = self.place_object(GridLayout(margins=False), 0,2, column_span=self.get_column_count(), alignment=0)

        ##### set up the internal variables

        # will be set later. This is where files will be dumped to when autosaving
        self._autosave_directory = None

        # file type (e.g. *.dat) for the file dialogs
        self.file_type = file_type

        # autosave settings path
        self._autosettings_path = autosettings_path

        # holds the curves and plot widgets for the data, and the buttons
        self._curves      = []
        self.plot_widgets = []
        self.ROIs         = []

        ##### Functionality of buttons etc...

        self.button_plot      .signal_clicked.connect(self._button_plot_clicked)
        self.button_save      .signal_clicked.connect(self._button_save_clicked)
        self.button_load      .signal_clicked.connect(self._button_load_clicked)
        self.button_clear     .signal_clicked.connect(self._button_clear_clicked)
        self.button_autosave  .signal_toggled.connect(self._button_autosave_clicked)
        self.button_script    .signal_toggled.connect(self._button_script_clicked)
        self.combo_binary     .signal_changed.connect(self._combo_binary_changed)
        self.combo_autoscript .signal_changed.connect(self._combo_autoscript_clicked)
        self.button_multi     .signal_toggled.connect(self._button_multi_clicked)
        self.button_link_x    .signal_toggled.connect(self._button_link_x_clicked)
        self.button_enabled   .signal_toggled.connect(self._button_enabled_clicked)
        self.number_file      .signal_changed.connect(self._number_file_changed)
        self.script           .signal_changed.connect(self._script_changed)

        # list of controls we should auto-save / load
        self._autosettings_controls = ["self.combo_binary",
                                       "self.combo_autoscript",
                                       "self.button_enabled",
                                       "self.button_multi",
                                       "self.button_link_x",
                                       "self.button_script",
                                       "self.number_file",
                                       "self.script"]

        # load settings if a settings file exists and initialize
        self.load_gui_settings()
        self._synchronize_controls()
        
        



    def _button_enabled_clicked(self, *a):  self.save_gui_settings()
    def _number_file_changed(self, *a):     self.save_gui_settings()
    def _script_changed(self, *a):          self.save_gui_settings()

    def _button_multi_clicked(self, *a):
        """
        Called whenever someone clicks the Multi button.
        """
        self.plot()
        self.save_gui_settings()

    def _button_link_x_clicked(self, *a):
        """
        Called whenever the Link X button is clicked.
        """
        self._update_linked_axes()
        self.save_gui_settings()

    def _combo_autoscript_clicked(self, *a):
        """
        Called whenever the combo is clicked.
        """
        self._synchronize_controls()
        self.plot()
        self.save_gui_settings()

    def _combo_binary_changed(self, *a):
        """
        Called whenever the combo is clicked.
        """
        self.save_gui_settings()

    def _button_script_clicked(self, checked):
        """
        Called whenever the button is clicked.
        """
        self._synchronize_controls()
        self.save_gui_settings()

    def _button_autosave_clicked(self, checked):
        """
        Called whenever the button is clicked.
        """
        if checked:
            # get the path from the user
            path = _spinmob.dialogs.save(filters=self.file_type)

            # abort if necessary
            if not path:
                self.button_autosave.set_checked(False)
                return

            # otherwise, save the info!
            self._autosave_directory, filename = _os.path.split(path)
            self._label_path.set_text(filename)

        self.save_gui_settings()

    def _button_save_clicked(self, *a):
        """
        Called whenever the button is clicked.
        """
        self.save_file()

    def _button_load_clicked(self, *a):
        """
        Called whenever the button is clicked.
        """
        self.load_file()

    def _button_clear_clicked(self, *a):
        """
        Called whenever the button is clicked.
        """
        self.clear()
        self.plot()

    def save_file(self, path=None, force_overwrite=False, just_settings=False, **kwargs):
        """
        Saves the data in the databox to a file.

        Parameters
        ----------
        path=None
            Path for output. If set to None, use a save dialog.
        force_overwrite=False
            Do not question the overwrite if the file already exists.
        just_settings=False 
            Set to True to save only the state of the DataboxPlot controls
        
        **kwargs are sent to the normal databox save_file() function.
        """
        # Update the binary mode
        if not 'binary' in kwargs: kwargs['binary'] = self.combo_binary.get_text()
        
        # if it's just the settings file, make a new databox
        if just_settings: d = _d.databox()

        # otherwise use the internal databox
        else: d = self

        # add all the controls settings to the header
        for x in self._autosettings_controls: self._store_gui_setting(d, x)

        # save the file using the skeleton function, so as not to recursively 
        # call this one again!
        _d.databox.save_file(d, path, self.file_type, self.file_type, force_overwrite, **kwargs)

    def load_file(self, path=None, just_settings=False):
        """
        Loads a data file. After the file is loaded, calls self.after_load_file(self),
        which you can overwrite if you like!

        just_settings=True will only load the configuration of the controls,
        and will not plot anything or run after_load_file
        """
        # if it's just the settings file, make a new databox
        if just_settings:
            d = _d.databox()
            header_only = True

        # otherwise use the internal databox
        else:
            d = self
            header_only = False

        # import the settings if they exist in the header
        if not None == _d.databox.load_file(d, path, filters=self.file_type, header_only=header_only, quiet=just_settings):
            
            # loop over the autosettings and update the gui
            for x in self._autosettings_controls: self._load_gui_setting(x,d)

        # always sync the internal data
        self._synchronize_controls()

        # plot the data if this isn't just a settings load
        if not just_settings:
            self.plot()
            self.after_load_file()


    def after_load_file(self,*args):
        """
        Called after a file is loaded. Does nothing. Feel free to overwrite!

        The first argument is the DataboxPlotInstance so your function can
        tell which instance loaded a file.
        """
        return

    def _button_plot_clicked(self, *a):
        """
        Called whenever the button is pressed.
        """
        self.plot()

    def _autoscript(self):
        """
        Automatically generates a python script for plotting. 
        """
        # This should never happen unless I screwed up.
        if self.combo_autoscript.get_index() == 0: return "ERROR: Ask Jack."
        
        # if there is no data, leave it blank
        if   len(self)==0: return "x = []; y = []; xlabels=[]; ylabels=[]"

        # if there is one column, make up a one-column script
        elif len(self)==1: return "x = [None]\ny = [ d[0] ]\n\nxlabels=[ 'Data Point' ]\nylabels=[ 'd[0]' ]"
            
        # Shared x-axis (column 0)
        elif self.combo_autoscript.get_index() == 1:
        
            # hard code the first columns
            sx = "x = [ d[0]"
            sy = "y = [ d[1]"

            # hard code the first labels
            sxlabels = "xlabels = '" +self.ckeys[0]+"'"
            sylabels = "ylabels = [ '"+self.ckeys[1]+"'"

            # loop over any remaining columns and append.
            for n in range(2,len(self)):
                sy += ", d["+str(n)+"]"
                sylabels += ", '"+self.ckeys[n]+"'"

            return sx+" ]\n"+sy+" ]\n\n"+sxlabels+"\n"+sylabels+" ]\n"
            
        
        # Column pairs
        elif self.combo_autoscript.get_index() == 2:
            
            # hard code the first columns
            sx = "x = [ d[0]"
            sy = "y = [ d[1]"
            
            # hard code the first labels
            sxlabels = "xlabels = [ '"+self.ckeys[0]+"'"
            sylabels = "ylabels = [ '"+self.ckeys[1]+"'"
            
            # Loop over the remaining columns and append
            for n in range(1,int(len(self)/2)):
                sx += ", d["+str(2*n  )+"]"
                sy += ", d["+str(2*n+1)+"]"
                sxlabels += ", '"+self.ckeys[2*n  ]+"'"
                sylabels += ", '"+self.ckeys[2*n+1]+"'"
            
            return sx+" ]\n"+sy+" ]\n\n"+sxlabels+" ]\n"+sylabels+" ]\n"
            print("test")
            
        # Column triples
        elif self.combo_autoscript.get_index() == 3:
            
            # hard code the first columns
            sx = "x = [ d[0], d[0]"
            sy = "y = [ d[1], d[2]"

            # hard code the first labels
            sxlabels = "xlabels = [ '"+self.ckeys[0]+"', '"+self.ckeys[0]+"'"
            sylabels = "ylabels = [ '"+self.ckeys[1]+"', '"+self.ckeys[2]+"'"

            # Loop over the remaining columns and append
            for n in range(1,int(len(self)/3)):
                sx += ", d["+str(3*n  )+"], d["+str(3*n  )+"]"
                sy += ", d["+str(3*n+1)+"], d["+str(3*n+2)+"]"
                
                sxlabels += ", '"+self.ckeys[3*n  ]+"', '"+self.ckeys[3*n  ]+"'"
                sylabels += ", '"+self.ckeys[3*n+1]+"', '"+self.ckeys[3*n+2]+"'"

            return sx+" ]\n"+sy+" ]\n\n"+sxlabels+" ]\n"+sylabels+" ]\n"
            
        else: return self.autoscript_custom()

    def autoscript_custom(self):
        """
        Overwrite this function (returning a valid script string) to redefine 
        the custom autoscript.
        """
        return "To use the 'Custom Autoscript' option, you must overwrite the function 'self.autoscript_custom' with your own (which must return a valid python script string)."

    def plot(self):
        """
        Sets the internal databox to the supplied value and plots it.
        If databox=None, this will plot the internal databox.
        """

        # if we're disabled or have no data columns, clear everything!
        if not self.button_enabled.is_checked() or len(self) == 0:
            self._set_number_of_plots(0)
            return self

        # if there is no script, create a default
        if not self.combo_autoscript.get_index()==0: 
            self.script.set_text(self._autoscript())

        ##### Try the script and make the curves / plots match

        try:
            # get globals for sin, cos etc
            g = _n.__dict__
            g.update(dict(d=self))
            g.update(dict(xlabels='x', ylabels='y'))

            # run the script.
            exec(self.script.get_text(), g)

            # x & y should now be data arrays, lists of data arrays or Nones
            x = g['x']
            y = g['y']

            # make it the right shape
            if x == None: x = [None]
            if y == None: y = [None]
            if not _spinmob.fun.is_iterable(x[0]) and not x[0] == None: x = [x]
            if not _spinmob.fun.is_iterable(y[0]) and not y[0] == None: y = [y]
            if len(x) == 1 and not len(y) == 1: x = x*len(y)
            if len(y) == 1 and not len(x) == 1: y = y*len(x)


            # xlabels and ylabels should be strings or lists of strings
            xlabels = g['xlabels']
            ylabels = g['ylabels']

            # make sure we have exactly the right number of plots
            self._set_number_of_plots(len(x))
            self._update_linked_axes()

            # return if there is nothing.
            if len(x) == 0: return

            # now plot everything
            for n in range(max(len(x),len(y))-1,-1,-1):

                # Create data for "None" cases.
                if x[n] is None: x[n] = list(range(len(y[n])))
                if y[n] is None: y[n] = list(range(len(x[n])))
                self._curves[n].setData(x[n],y[n])

                # get the labels for the curves

                # if it's a string, use the same label for all axes
                if type(xlabels) in [str,type(None)]: xlabel = xlabels
                elif n < len(xlabels):                xlabel = xlabels[n]
                else:                                 xlabel = ''

                if type(ylabels) in [str,type(None)]: ylabel = ylabels
                elif n < len(ylabels):                ylabel = ylabels[n]
                else:                                 ylabel = ''

                # set the labels
                i = min(n, len(self.plot_widgets)-1)
                self.plot_widgets[i].setLabel('left',   ylabel)
                self.plot_widgets[i].setLabel('bottom', xlabel)

                # special case: hide if None
                if xlabel == None: self.plot_widgets[i].getAxis('bottom').showLabel(False)
                if ylabel == None: self.plot_widgets[i].getAxis('left')  .showLabel(False)

            # unpink the script, since it seems to have worked
            self.script.set_colors('black','white')

        # otherwise, look angry and don't autosave
        except: self.script.set_colors('black','pink')

        return self

    def autosave(self):
        """
        Autosaves the currently stored data, but only if autosave is checked!
        """
        # make sure we're suppoed to
        if self.button_autosave.is_checked():

            # save the file
            self.save_file(_os.path.join(self._autosave_directory, "%04d " % (self.number_file.get_value()) + self._label_path.get_text()))

            # increment the counter
            self.number_file.increment()

    def autozoom(self, n=None):
        """
        Auto-scales the axes to fit all the data in plot index n. If n == None,
        auto-scale everyone.
        """
        if n==None:
            for p in self.plot_widgets: p.autoRange()
        else:        self.plot_widgets[n].autoRange()

        return self

    def _synchronize_controls(self):
        """
        Updates the gui based on button configs.
        """

        # whether the script is visible
        self.grid_script._widget.setVisible(self.button_script.get_value())

        # whether we should be able to edit it.
        if not self.combo_autoscript.get_index()==0: self.script.disable()
        else:                                        self.script.enable()


    def _set_number_of_plots(self, n):
        """
        Adjusts number of plots & curves to the desired value the gui.
        """

        # multi plot, right number of plots and curves = great!
        if self.button_multi.is_checked()               \
        and len(self._curves) == len(self.plot_widgets) \
        and len(self._curves) == n: return

        # single plot, right number of curves = great!
        if not self.button_multi.is_checked() \
        and len(self.plot_widgets) == 1       \
        and len(self._curves) == n: return

        # time to rebuild!

        # don't show the plots as they are built
        self.grid_plot.block_events()

        # make sure the number of curves is on target
        while len(self._curves) > n: self._curves.pop(-1)
        while len(self._curves) < n: self._curves.append(_g.PlotCurveItem(pen = (len(self._curves), n)))

        # figure out the target number of plots
        if self.button_multi.is_checked(): n_plots = n
        else:                              n_plots = min(n,1)

        # clear the plots
        while len(self.plot_widgets):

            # pop the last plot widget and remove all items
            p = self.plot_widgets.pop(-1)
            p.clear()

            # remove it from the grid
            self.grid_plot.remove_object(p)

        # add new plots
        for i in range(n_plots):
            self.plot_widgets.append(self.grid_plot.place_object(_g.PlotWidget(), 0, i, alignment=0))

        # loop over the curves and add them to the plots
        for i in range(n):
            self.plot_widgets[min(i,len(self.plot_widgets)-1)].addItem(self._curves[i])

        # loop over the ROI's and add them
        if self.ROIs is not None:

            for i in range(len(self.ROIs)):

                # get the ROIs for this plot
                ROIs = self.ROIs[i]

                if not _spinmob.fun.is_iterable(ROIs): ROIs = [ROIs]

                # loop over the ROIs for this plot
                for ROI in ROIs:

                    # determine which plot to add the ROI to
                    m = min(i, len(self.plot_widgets)-1)

                    # add the ROI to the appropriate plot
                    if m>=0: self.plot_widgets[m].addItem(ROI)

        # show the plots
        self.grid_plot.unblock_events()


    def _update_linked_axes(self):
        """
        Loops over the axes and links / unlinks them.
        """
        # no axes to link!
        if len(self.plot_widgets) <= 1: return

        # get the first plotItem
        a = self.plot_widgets[0].plotItem.getViewBox()
        
        # now loop through all the axes and link / unlink the axes
        for n in range(1,len(self.plot_widgets)):
            
            # Get one of the others
            b = self.plot_widgets[n].plotItem.getViewBox() 
            
            # link the axis, but only if it isn't already
            if self.button_link_x.is_checked() and b.linkedView(b.XAxis) == None:
                b.linkView(b.XAxis, a)
            
            # Otherwise, unlink the guy, but only if it's linked to begin with
            elif not self.button_link_x.is_checked() and not b.linkedView(b.XAxis) == None:
                b.linkView(b.XAxis, None)


class DataboxSaveLoad(_d.databox, GridLayout):

    def __init__(self, file_type="*.dat", autosettings_path=None, **kwargs):
        """
        This is basically just a databox with a load and save button. To change
        the behavior of loading and saving, overwrite the functions
        self.pre_save() and self.post_load()
        
        Parameters
        ----------
        file_type="*.dat"
            File extension for saving and dialogs.
        autosettings_path=None
            If set to a <some string>, will save it's settings to 
            gui_settings/<some string>.
        """

        # Do all the tab-area initialization; this sets _widget and _layout
        GridLayout.__init__(self, margins=False)
        _d.databox.__init__(self, **kwargs)

        # create the controls
        self.button_load     = self.place_object(Button("Load"), alignment=1)
        self.button_save     = self.place_object(Button("Save"), alignment=1)
        self.combo_binary    = self.place_object(ComboBox(['Text', 'float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'complex64', 'complex128', 'complex256']), alignment=1)
        self.label_path      = self.place_object(Label(""), alignment=0)
        self.set_column_stretch(2,100)

        # connect the signals to the buttons
        self.button_save .signal_clicked.connect(self._button_save_clicked)
        self.button_load .signal_clicked.connect(self._button_load_clicked)
        self.combo_binary.signal_changed.connect(self._combo_binary_changed)
        
        # disabled by default
        self.button_save.disable()

        # Store the file type for later.
        self.file_type = file_type

        # autosave settings path
        self._autosettings_path = autosettings_path
        
        # list of controls we should auto-save / load
        self._autosettings_controls = ["self.combo_binary"]
        
        # Load the previous settings
        self.load_gui_settings()


    def pre_save(self):
        """
        Function you should overwrite for what to do prior to saving.
        """
        return

    def post_save(self):
        """
        Function you should overwrite if you want to do anything after saving.
        """
        return

    def post_load(self):
        """
        Function you should overwrite for what to do after loading a file.
        """
        return

    def pre_load(self):
        """
        Function you should overwrite if you want to do something prior to loading.
        """
        return

    def _button_save_clicked(self, *a):
        self.pre_save()
        self.save_file(None, self.file_type, self.file_type, binary=self.combo_binary.get_text())

        self.post_save()

    def _button_load_clicked(self, *a):
        self.pre_load()
        self.load_file(filters=self.file_type)
        self.post_load()

    def _combo_binary_changed(self, *a):
        """
        Called whenever the combo is clicked.
        """
        self.save_gui_settings()

    def disable_save(self): self.button_save.disable()
    def enable_save(self):  self.button_save.enable()




if __name__ == '__main__':
    w = Window()
    p = w.place_object(DataboxPlot(autoscript=2))
    w.show()
    
    p[0] = [1,2]
    p[1] = [1,2]
    p[2] = [2,1]
    p[3] = [1,2]
    
    p.plot()
    




