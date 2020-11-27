# Regular imports
import time     as _t
import os       as _os
import shutil   as _shutil
import numpy    as _n
import scipy.special as _scipy_special
import sys as _sys

import traceback as _traceback
_p = _traceback.print_last

import spinmob as _s
_d = _s.data

# import pyqtgraph and create the App.
import pyqtgraph as _pg
_e = _pg.QtCore.QEvent

# Syntax highlighter
try: from . import _syntax
except:     import _syntax

_a = _pg.mkQApp()

# set the font if we're in linux
#if _sys.platform in ['linux', 'linux2']: _a.setFont(_pg.QtGui.QFont('Arial', 8))

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

def clear_egg_settings():
    """
    Removes the egg_settings directory from the current working directory.
    """
    _shutil.rmtree('egg_settings', ignore_errors=True)


class BaseObject(object):
    """
    Base object containing stuff common to all of our objects. When
    deriving objects from this, call BaseObject.__init__(self) as the
    LAST step of the new __init__ function.
    """

    log = None
    _alignment_default = 1 # If alignment is not overridden, use this.

    def __init__(self, autosettings_path=None):
        if not _s._pyqtgraph_ok: raise Exception('Cannot create egg GUIs without pyqtgraph v0.11.0 or higher.')

        # Parent object (to be set)
        self._parent = None

        self._style = ''

        # for remembering settings; for child objects, overwrite both, and
        # add a load_gui_settings() to the init!
        self._autosettings_path     = autosettings_path
        self._autosettings_controls = []
        self._lazy_load             = dict()

        # common signals
        return

    def __call__(self, *args, **kwargs):
        """
        Shortcut that returns self.set_value() if a value is provided or self.get_value() if it is not.
        **kwargs are sent to both functions.
        """
        if len(args): return self.set_value(*args, **kwargs)
        else:         return self.get_value(**kwargs)

    def hide(self, opposite=False):
        """
        Hides the widget.

        Parameters
        ----------
        opposite=False
            If True, do the opposite (show the widget).
        """
        if opposite: self._widget.show()
        else:        self._widget.hide()
        return self

    def show(self, opposite=False):
        """
        Shows the widget.

        Parameters
        ----------
        opposite=False
            If True, do the opposite (show the widget).
        """
        if opposite: self._widget.hide()
        else:        self._widget.show()
        return self

    def set_hidden(self, hidden=True):
        """
        Hides or shows the widget.

        Parameters
        ----------
        hidden=True
            Whether it should be hidden.
        """
        if hidden: self.hide()
        else:      self.show()
        return self

    def set_colors(self, text=None, background=None):
        """
        Sets the text and background colors of the widget.

        Parameters
        ----------
        text=None
            Color of the main text. None means default
        background=None
            Color of the background. None means default.
        """
        self._widget.setStyleSheet(self._widget.__class__.__name__ + " {"+self._style+"; background-color: "+str(background)+"; color: "+str(text)+"}")
        return self

    def set_style(self, style=''):
        """
        Sets the style for the object. Updates self._style for future calls
        to self.set_colors() etc.

        Parameters
        ----------
        style=''
            Can be any css style elements or a list of them, e.g.,
            'font-family:monospace; background-color:pink;'
        """
        self._widget.setStyleSheet(self._widget.__class__.__name__ + " {"+style+"}")
        self._style = style
        return self

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

    def set_pyqtgraph_options(self, **kwargs):
        """
        Sets the options for a pyqtgraph widget using self._widget.setOpts(**kwargs).
        Any valid pyqtgraph widget keyword arguments can be modified this way
        via keyword arguments, e.g., suffix='pants', bounds=(0,100)

        Returns self
        """
        self._widget.setOpts(**kwargs)
        return self

    def set_parent(self, parent):
        """
        Sets the parent object manually (usually this is done automatically
        when placing the object).
        """
        self._parent = parent

    def get_pyqtgraph_options(self):
        """
        Returns a copy of the current options dictionary for the pyqtgraph widget.
        """
        return dict(self._widget.opts)

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

    def block_signals(self):
        """
        Prevents the widget from sending signals.
        """
        self._widget.blockSignals(True)
        self._widget.setUpdatesEnabled(False)
        return self

    def unblock_signals(self):
        """
        Allows the widget to send signals.
        """
        self._widget.blockSignals(False)
        self._widget.setUpdatesEnabled(True)
        return self

    def block_events(self):
        """
        Antiquated. Use block_signals().
        """
        print('WARNING: block_events and unblock_events are antiquated. Please use block_signals and unblock_signals instead.')
        return self.block_signals()

    def unblock_events(self):
        """
        Antiquated. Use unblock_signals().
        """
        print('WARNING: block_events and unblock_events are antiquated. Please use block_signals and unblock_signals instead.')
        return self.unblock_signals()

    def disable(self, value=True):
        """
        Disables the widget.

        Parameters
        ----------
        value=True
            If set to False, enables the widget.
        """
        self._widget.setEnabled(not value)
        return self

    def enable(self, value=True):
        """
        Enables the widget.

        Parameters
        ----------
        value=True
            If set to False, disables the widget.
        """
        self._widget.setEnabled(value)
        return self

    def print_message(self, message="heya!"):
        """
        If self.log is defined to be an instance of TextLog, it print the
        message there. Otherwise use the usual "print" to command line.
        """
        if self.log == None: print(message)
        else:                self.log.append_text(message)

    def save_gui_settings(self, *a):
        """
        Saves just the current configuration of the controls if the
        autosettings_path is set.
        """

        # only if we're supposed to!
        if self._autosettings_path:

            # Get the gui settings directory
            gui_settings_dir = _os.path.join(_cwd, 'egg_settings')

            # make sure the directory exists
            if not _os.path.exists(gui_settings_dir): _os.mkdir(gui_settings_dir)

            # make a path with a sub-directory
            path = _os.path.join(gui_settings_dir, self._autosettings_path)

            # for saving header info
            d = _d.databox(delimiter=',')

            # add all the controls settings
            for x in self._autosettings_controls: self._store_gui_setting(d, x)

            # Summary of standard set_value items
            d.h(_autosettings_standard_items=list(d.hkeys))

            # Add any additional special information specified by derived objects.
            self._additional_save_gui_settings(d)

            # save the file
            d.save_file(path, force_overwrite=True)

    def _additional_save_gui_settings(self, d):
        """
        Overload me to store additional gui information.
        """
        return

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
            gui_settings_dir = _os.path.join(_cwd, 'egg_settings')

            # assemble the path with a sub-directory
            path = _os.path.join(gui_settings_dir, self._autosettings_path)

            # databox just for loading a cfg file
            d = _d.databox(delimiter=',')

            # if the settings path exists
            if _os.path.exists(path):

                # Load the settings
                d.load_file(path, header_only=True, quiet=True)

                # List of "Standard" items that can be loaded with self.set_value()
                self._autosettings_standard_items = d.pop_header('_autosettings_standard_items', ignore_error=True)
                if not self._autosettings_standard_items: self._autosettings_standard_items = list(d.hkeys)

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

        # Here d is a dictionary of settings, and we know which ones should
        # be set_value()'d because they're in self._autosettings_standard_items

        # only do this if the key exists
        if key in d:

            try:
                # Try to set the value
                if key in self._autosettings_standard_items:
                    eval(key).set_value(d[key])

                    # If this fails, perhaps the element does not yet exist
                    # For example, TabArea may not have all the tabs created
                    # and cannot set the active tab until later.
                    # If we're here, it worked, so pop if necessary
                    if pop_value: d.pop(key)

            except:
                print("ERROR: Could not load gui setting "+repr(key)+'\n'+str(self))

    def _store_gui_setting(self, databox, name):
        """
        Stores the gui setting in the header of the supplied databox.
        hkeys in the file are set to have the format
        "self.controlname"
        """
        try:    databox.insert_header(name, eval(name + ".get_value()"))
        except: print("ERROR: Could not store gui setting "+repr(name)+'\n'+str(self))



class GridLayout(BaseObject):

    '''
    This is a raw, unencapsulated grid layout upon which things like windows
    are built.

    Parameters
    ----------
    margins=True
        Set to True or False or to a length-4 tuple/list to define the space
        around the widgets contained within.
    scroll=False
        Whether it should be allowed to scroll.
    autosettings_path=None
        Sent to BaseObject. If self._autosettings_controls is properly set up
        it will remember settings from run to run.
    '''

    log = None

    def __init__(self, margins=True, scroll=False, autosettings_path=None):
        """
        This creates a grid layout that can contain other Elements
        (including other grid and docked layouts)
        """
        BaseObject.__init__(self, autosettings_path=autosettings_path)
        #self._alignment_default = 0 # Default grids fill space.

        # Qt widget to house the layout
        self._widget = _pg.Qt.QtGui.QWidget()
        
        # Resize event
        self._widget.resizeEvent = self._event_resize 

        # Qt layout object
        self._layout = _pg.Qt.QtGui.QGridLayout()

        # stick the layout into the widget
        self._widget.setLayout(self._layout)

        # auto-add row and column
        self._auto_row      = 0
        self._auto_column   = 0

        # list of objects
        self.objects = []

        # other useful functions to wrap
        self.get_row_count    = self._layout.rowCount
        self.get_column_count = self._layout.columnCount

        # Set the margins
        self.set_margins(margins)

        # Expose the show and hide functions
        # The attr check ensures classes inheriting this object's methods
        # don't have their show's and hide's overwritten
        if not hasattr(self, 'show'): self.show = self._widget.show
        if not hasattr(self, 'hide'): self.hide = self._widget.hide


    def _event_resize(self, *a):
        """
        Called when it resizes.
        """
        # print(self)
        # # Recursively loop over all sub-objects and call their resizers.
        # for o in self.objects:
        #     if type(o) == GridLayout:
        #         o._event_resize()
        
        # Now call this one's customized resizer.
        self.event_resize()

    def event_resize(self):
        """
        Dummy function you can overload when the grid is resized.
        """
        return

    def __getitem__(self, n): return self.objects[n]

    def place_object(self, object, column=None, row=None, column_span=1, row_span=1, alignment=None):
        """
        This adds an egg object or a QWidget to the
        grid at the specified position, appends the object to self.objects.

        Parameters
        ----------
        object : egg or QWidget
            Supply a spinmob egg object or QWidget to place on the grid.
        
        column=None, row=None : None or integer
            Where to place the object on the grid, starting at 0,0 in the upper left.
            If column isn't specified, the new object will be placed in a new column
            (i.e., you can add objects like words in a sentence; see also
            self.new_autorow()).

        column_span=1, row_span=1 : integer
            How many columns or rows the object should span. See also
            self.set_column_stretch() and self.set_row_stretch().
        
        alignment=None : None, 0, 1, or 2
            How to align the object. If None is supplied, this uses the default
            value for the object in question. Otherwise, 0 means "fill space",
            1 means "left justified", 2 means "right justified".
      
        Returns
        -------
        self
        """

        # pick a column
        if column==None:
            column = self._auto_column
            self._auto_column += 1

        # pick a row
        if row==None: row = self._auto_row

        # create the object
        self.objects.append(object)

        # Figure out whether the widget is egg or "standard"
        try:
            object._widget
            widget = object._widget

        # allows the user to specify a standard widget
        except: widget = object

        if alignment==None: alignment = object._alignment_default
        self._layout.addWidget(widget, row, column,
                               row_span, column_span,
                               _pg.Qt.QtCore.Qt.Alignment(alignment))

        # try to store the parent object (self) in the placed object
        try:    object.set_parent(self)
        except: None

        return object

    # Shortcut.
    add = place_object

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

    def set_margins(self, margins=True):
        """
        Sets the grid margins.

        Parameters
        ----------
        margins=True
            True sets them to (10,10,10,10), False sets them to (0,0,0,0). You
            may also manually specify a 4-element tuple or a single integer.
        """
        # Handle the possibilities
        if   margins==True:  margins=[10,10,10,10]
        elif margins==False: margins=[0,0,0,0]
        elif type(margins) == int: margins = [margins]*4

        # Set the margins
        self._layout.setContentsMargins(*margins)
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
    title='Window' : str
        Text for the window's title bar.

    size=[700,500] : tuple or list
        Starting size of the window.

    autosettings_path=None : str
        If set to a file name, e.g. "w.txt", the window will create and update
        the file egg_settings/w.txt every time a window setting changes (e.g.,
        if you resize or move it.) Previous settings will be automatically
        loaded when the program is next run.

    margins=True : bool
        Set to True or False or a length-4 tuple to include, exclude or define
        the space around the widgets in the window.

    event_close=None : function
        Optional function to perform duties when the window closes.
    """


    def __init__(self, title='Window', size=[700,500], autosettings_path=None,
                 margins=True, event_close=None):
        self._parent = self

        # initialize the grid layout
        GridLayout.__init__(self, margins=margins)
        self._alignment_default = 0 # By default, fills space.

        # create the QtMainWindow,
        self._window = _pg.Qt.QtGui.QMainWindow()
        self.set_size(size)
        self.set_title(title)

        #Set some docking options
        self._window.setDockOptions(_pg.Qt.QtGui.QMainWindow.AnimatedDocks    |
                                    _pg.Qt.QtGui.QMainWindow.AllowNestedDocks |
                                    _pg.Qt.QtGui.QMainWindow.AllowTabbedDocks )

        # set the central widget to that created by GridLayout.__init__
        self._window.setCentralWidget(self._widget)

        # events for moving, resizing and closing
        self._last_event_type = None
        self._window.eventFilter = self._event_filter
        self._window.installEventFilter(self._window)
        self._window.closeEvent  = self._event_close

        # autosettings path, to remember the window's position and size
        self._autosettings_path = autosettings_path

        # If there is a close event
        if event_close: self.event_close = event_close

        # reload the last settings if they exist
        self._load_settings()



    def place_docker(self, docker, area='top'):
        """
        IN DEVELOPMENT
        Places a DockWindow instance at the specified area ('top', 'bottom',
        'left', 'right', or None)
        """
        # map of options
        m = dict(top    = _pg.QtCore.Qt.TopDockWidgetArea,
                 bottom = _pg.QtCore.Qt.BottomDockWidgetArea,
                 left   = _pg.QtCore.Qt.LeftDockWidgetArea,
                 right  = _pg.QtCore.Qt.RightDockWidgetArea)


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

    def _event_filter(self, o, e):
        """
        Used to prevent all window move events from saving.
        """
        # Weird event sequence that happens at the end of a
        # move or resize.

        # Covers different sequences on Linux and Windows, with and without a layout
        if self._last_event_type in [_e.Move, _e.UpdateRequest, _e.LayoutRequest] \
            and e.type() in [_e.NonClientAreaMouseMove, _e.WindowActivate]:
                self._save_settings()
                return True

        # Remember the last event
        self._last_event_type = e.type()
        return False

    def _event_close(self, event):
        """
        Don't modify this.
        """
        self._is_open = False
        self.event_close()

    def _save_settings(self):
        """
        Saves all the parameters to a text file.
        """
        if self._autosettings_path == None: return

        # Get the gui settings directory
        gui_settings_dir = _os.path.join(_cwd, 'egg_settings')

        # make sure the directory exists
        if not _os.path.exists(gui_settings_dir): _os.mkdir(gui_settings_dir)

        # make a path with a sub-directory
        path = _os.path.join(gui_settings_dir, self._autosettings_path)

        # Create a Qt settings object
        settings = _pg.QtCore.QSettings(path, _pg.QtCore.QSettings.IniFormat)
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
        gui_settings_dir = _os.path.join(_cwd, 'egg_settings')

        # make a path with a sub-directory
        path = _os.path.join(gui_settings_dir, self._autosettings_path)

        # make sure the directory exists
        if not _os.path.exists(path): return

        # Create a Qt settings object
        settings = _pg.QtCore.QSettings(path, _pg.QtCore.QSettings.IniFormat)

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

    autosettings_path=None
        If you want this object to remember its state from run to run, specify
        a unique identifier string, e.g. 'my_button_no'.

    tip=None
        If set to a string, assigns a tool tip to the button (text that pops up
        when hovering)

    signal_clicked=None : function
        Optional function to which signal_clicked will connect.

    signal_toggled=None : function
        Optional function to which signal_toggled will connect.

    style_checked=None, style_unchecked=None : string
        Stylesheet for the button when checked and unchecked, e.g.,
        'font-size:20px; color:white; background-color:red'

    Signals
    -------
    self.signal_clicked
        When the user has clicked and released the button.

    self.signal_toggled
        When the checked state has changed.
    """


    def __init__(self, text="My Button! No!", checkable=False, checked=False,
                 QPushButton=None, autosettings_path=None, tip=None,
                 signal_clicked=None, signal_toggled=None,
                 style_checked=None, style_unchecked=None):

        # Qt button instance
        if QPushButton is None: self._widget = _pg.Qt.QtGui.QPushButton(text)
        else:                   self._widget = QPushButton

        # Other stuff common to all objects
        BaseObject.__init__(self, autosettings_path=autosettings_path)

        # if there is a tip
        if type(tip)==str: self._widget.setToolTip(tip)

        # signals
        self.signal_clicked = self._widget.clicked
        self.signal_toggled = self._widget.toggled

        # Default colors
        self._style_unchecked = ''
        self._style_checked   = ''

        # set checkable
        self.set_checkable(checkable)
        if checkable: self.set_checked(checked)

        # aliases
        self.get_value = self.is_checked
        self.set_value = self.set_checked

        # Store self as autosettings
        self._autosettings_controls.append('self')

        # Load any previous settings
        self.load_gui_settings()

        # Update the styles
        self.set_style_checked_unchecked(style_checked, style_unchecked)

        # Functions to set the colors etc.
        self.signal_toggled.connect(self._self_toggled)

        # Bind to save gui settings when changed
        self.signal_toggled.connect(self.save_gui_settings)

        # If other functions were supplied
        if signal_clicked: self.signal_clicked.connect(signal_clicked)
        if signal_toggled: self.signal_toggled.connect(signal_toggled)


    def _self_toggled(self, *a):
        """
        Sets the colors etc.
        """
        # If we've set any defaults
        if self._style_checked != '' or self._style_unchecked != '':

            # Get the style string
            style = self._style_checked if self.is_checked() else self._style_unchecked

            # If it's checked and we've specified something
            self._widget.setStyleSheet(self._widget.__class__.__name__ + " {"+style+"}")

    def set_style_unchecked(self, style=None):
        """
        Sets the stylesheet of the button when it's unchecked.

        Parameters
        ----------
        style=None : str (optional)
            Stylesheet string, e.g. 'font-family:monospace; background-color:pink;'
        """
        self._style_unchecked = style
        self._self_toggled()
        return self

    def set_style_checked(self, style=None):
        """
        Sets the stylesheet of the button when it's checked.

        Parameters
        ----------
        style=None : str (optional)
            Stylesheet string, e.g. 'font-family:monospace; background-color:pink;'
        """
        self._style_checked = style
        self._self_toggled()
        return self

    def set_style_checked_unchecked(self, style_checked=None, style_unchecked=None):
        """
        Sets the stylesheet of the button when it's checked and unchecked.

        Parameters
        ----------
        style_checked=None, style_unchecked : str (optional)
            Stylesheet string, e.g. 'font-family:monospace; background-color:pink;'
        """
        if style_checked:   self._style_checked   = style_checked
        if style_unchecked: self._style_unchecked = style_unchecked
        self._self_toggled()
        return self

    def set_colors_unchecked(self, text=None, background=None):
        """
        Sets the default colors when the button is unchecked. This will override
        any other styles you may have applied. For more control, see
        self.set_style_unchecked().

        Parameters
        ----------
        text=None
            Color of the main text. None means default.
        background=None
            Color of the background. None means default.
        """
        self.set_style_unchecked(self._style+" background-color: "+str(background)+"; color: "+str(text))
        return self

    def set_colors_checked(self, text=None, background=None):
        """
        Sets the default colors when the button is checked. This will override
        any other styles you may have applied. For more control, see
        self.set_style_checked().

        Parameters
        ----------
        text=None
            Color of the main text. None means default.
        background=None
            Color of the background. None means default.
        """
        self.set_style_checked(self._style+" background-color: "+str(background)+"; color: "+str(text))
        return self

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

    def set_checked(self, value=True, block_signals=False, **kwargs):
        """
        This will set whether the button is checked.

        Setting block_signals=True will temporarily disable signals
        from the button when setting the value.
        """
        if 'block_events' in kwargs:
            print('WARNING: block_events is antiquated. Please use block_signals instead.')
            block_signals = kwargs['block_events']

        if block_signals: self._widget.blockSignals(True)
        self._widget.setChecked(value)
        if block_signals: self._widget.blockSignals(False)

        return self


    def set_text(self, text="MY Button. MINE."):
        """
        Sets the text of the button.
        """
        self._widget.setText(str(text))
        return self

    def get_text(self):
        """
        Gets the text of the button.
        """
        return self._widget.text()

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

class Image(BaseObject):
    """
    Simplified QPixmap container.

    Parameters
    ----------
    image_path= : str
        Path to the image.
    """
    def __init__(self, image_path):

        # Create the widget and label
        self._widget = _pg.Qt.QtGui.QLabel()
        self._pixmap = _pg.Qt.QtGui.QPixmap(image_path)
        self._widget.setPixmap(self._pixmap)

        # Other stuff common to all objects
        BaseObject.__init__(self)




class Label(BaseObject):
    """
    Simplified QLabel object.

    Parameters
    ----------
    text="My Label! No!"
        Text to appear on the button.
    autosettings_path=None
        If you want this object to remember its state from run to run, specify
        a unique identifier string, e.g. 'my_button_no'.
    """
    def __init__(self, text="My Label. NO!", autosettings_path=None):

        # Create the widget
        self._widget = _pg.Qt.QtGui.QLabel(text)

        # Other stuff common to all objects
        BaseObject.__init__(self, autosettings_path=autosettings_path)

        self._autosettings_controls = ['self']

        self.load_gui_settings()

    def get_text(self):
        """
        Gets the current value of the text.
        """
        return str(self._widget.text())
    get_value=get_text

    def set_text(self, text="I said NO."):
        """
        Sets the text.
        """
        self._widget.setText(str(text))
        self.save_gui_settings()
        return self
    set_value=set_text


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
    """
    Simplified number box with spinners. This is pyqtgraph's SpinBox().
    Extra keyword arguments are sent to the SpinBox.

    Parameters
    ----------
    value=0 : number
        Initial value

    step=1 : number
        Step size

    bounds=(None,None) : tuple or list
        Min and max values

    int=False : bool
        Force the value to be an integer if True

    autosettings_path=None : str
        If you want this object to remember its value from run to run, specify
        a unique identifier, e.g. 'my_numberbox'.

    tip=None : str
        If set to a string, sets the tool tip (text that pops up when hovering).

    signal_changed=None : function
        Optional function to which signal_changed will connect.

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

    def __init__(self, value=0, step=1, bounds=(None,None), int=False,
                 autosettings_path=None, tip=None, signal_changed=None, **kwargs):

        # Fix the weird default behavior
        kwargs['compactHeight'] = False

        # pyqtgraph spinbox
        self._widget = _pg.SpinBox(value=value, step=step, bounds=bounds, int=int, **kwargs)

        # Other stuff common to all objects
        BaseObject.__init__(self, autosettings_path=autosettings_path)

        # If there is a tip
        if tip: self._widget.setToolTip(tip)

        # signals
        self.signal_changed = self._widget.sigValueChanging

        # set a less ridiculous width
        self.set_width(70)

        # Store self as autosettings
        self._autosettings_controls.append('self')

        # Load any previous settings
        self.load_gui_settings()

        # Bind to save gui settings when changed
        self.signal_changed.connect(self.save_gui_settings)

        # If functions provided
        if signal_changed: self.signal_changed.connect(signal_changed)

    def get_value(self):
        """
        Returns the current value of the number box.
        """
        return self._widget.value()

    def set_value(self, value, block_signals=False, **kwargs):
        """
        Sets the current value of the number box.

        Setting block_signals=True will temporarily block the widget from
        sending any signals when setting the value.
        """
        if 'block_events' in kwargs:
            print('WARNING: block_events is antiquated. Please use block_signals instead.')
            block_signals = kwargs['block_events']

        if block_signals: self.block_signals()
        self._widget.setValue(value)
        if block_signals: self.unblock_signals()
        return self

    def set_step(self, value, block_signals=False, **kwargs):
        """
        Sets the step of the number box.

        Setting block_signals=True will temporarily block the widget from
        sending any signals when setting the value.
        """
        if 'block_events' in kwargs:
            print('WARNING: block_events is antiquated. Please use block_signals instead.')
            block_signals = kwargs['block_events']

        if block_signals: self.block_signals()
        self._widget.setSingleStep(value)
        if block_signals: self.unblock_signals()

        return self

    def increment(self, n=1):
        """
        Increments the value by n.
        """
        return self.set_value(self.get_value()+n)


class CheckBox(GridLayout):
    """
    Simplified QCheckBox.

    Parameters
    ----------
    text=None : str
        None means no label. A string will set the label next to the box.

    checked=False : bool
        Whether it is initially checked.

    text_editable=False : bool
        If True, self.text will be a TextBox. If False, it will be a Label.

    text_position='right' : str
        Can be 'right', 'left', 'top', 'bottom'

    autosettings_path=None : str
        If you wish for this object to remember its state from run to run,
        specify a unique identifier string, e.g. 'my_checkbox'

    signal_toggled=None : function
    signal_changed=None : function
    signal_clicked=None : function
    signal_text_changed=None : function
        Optional functions to which each signal will connect. Note
        signal_text_changed only exists if label_editable==True

    Signals
    -------
    self.signal_toggled
        Emitted whenever someone toggles the state of the checkbox. This is the
        recommended signal.

    self.signal_text_changed
        If label_editable==True, this is the signal self.text.signal_changed

    self.signal_changed
        Emitted whenver the 'state' changes.

    self.signal_clicked
        Emitted whenever the checkbox is clicked.

    **kwargs are sent to the label item.

    """

    def __init__(self, text=None, checked=False, text_editable=False, text_position='right',
                 autosettings_path=None, tip=None,
                 signal_toggled=None,
                 signal_text_changed=None,
                 signal_changed=None,
                 signal_clicked=None,
                 **kwargs):

        # pyqt objects
        self._widget_checkbox = _pg.QtGui.QCheckBox()
        self._widget_checkbox.setToolTip(tip)

        # Other stuff common to all objects
        GridLayout.__init__(self, margins=False, scroll=False, autosettings_path=autosettings_path)

        # Add the widget to the grid
        self.add(self._widget_checkbox, 1,1)

        # Add the text
        if text:
            if text_editable:
                self.text = TextBox(text=text, **kwargs)
                self._autosettings_controls = ['self', 'self.text']
                self.signal_text_changed = self.text.signal_changed
                if signal_text_changed: self.signal_text_changed.connect(signal_text_changed)
            else:
                self.text = Label  (text=text, **kwargs)
                self._autosettings_controls = ['self']

            # Position the text
            if   text_position == 'right': self.add(self.text, 2,1, alignment=1)
            elif text_position == 'left' : self.add(self.text, 0,1, alignment=2)
            elif text_position == 'top'  : self.add(self.text, 1,0, alignment=0)
            else:                          self.add(self.text, 1,2, alignment=0)

            # Set the tooltip.
            self.text._widget.setToolTip(tip)

        # No label.
        else: self.text = None

        # Default value
        if checked: self.set_checked(True)

        # signals
        self.signal_changed = self._widget_checkbox.stateChanged
        self.signal_toggled = self._widget_checkbox.toggled
        self.signal_clicked = self._widget_checkbox.clicked

        # Store self as autosettings


        # Load any previous settings
        self.load_gui_settings()

        # Bind to save gui settings when changed
        self.signal_changed.connect(self.save_gui_settings)
        if text and text_editable: self.text.signal_changed.connect(self.save_gui_settings)

        # If functions supplied
        if signal_changed: self.signal_changed.connect(signal_changed)
        if signal_toggled: self.signal_toggled.connect(signal_toggled)
        if signal_clicked: self.signal_clicked.connect(signal_clicked)

    def is_checked(self):
        """
        Check if checked.
        """
        return self._widget_checkbox.checkState()
    get_value = is_checked

    def set_text(self, text='Nooooooo!'):
        """
        Sets the text.
        """
        self.text.set_value(text)
        self.save_gui_settings()

    def get_text(self): return self.text.get_text()

    def set_checked(self, value=True):
        """
        Set checkbox state.
        """
        self._widget_checkbox.setChecked(value)
        return self
    set_value = set_checked



class ComboBox(BaseObject):
    """
    Simplified QComboBox.

    Parameters
    ----------
    items=['test','me']
        List of items for the combobox.

    autosettings_path=None
        If you want this object to remember its settings from run to run,
        give it a unique identifier string, e.g. 'my_combobox'

    tip=None
        Set to a string to pop up a message while the mouse hovers.

    default_index=0
        Default selected index.

    signal_changed=None : function
    signal_activated=None : function
        Optional functions to which the signals will be connected.

    Signals
    -------
    self.signal_changed
        Called when the selection changes.

    self.signal_activated
        Called when the combo box is activated.


    **kwargs are sent to the underlying widget options self._widget.setOpts()
    """

    def __init__(self, items=['test','me'], autosettings_path=None, tip=None,
                 default_index=0, signal_changed=None, signal_activated=None):

        # pyqt objects
        self._widget = _pg.QtGui.QComboBox()
        self._widget.setToolTip(tip)

        # Other stuff common to all objects
        BaseObject.__init__(self, autosettings_path=autosettings_path)

        # Populate it.
        for item in items: self.add_item(item)

        # Set the default index
        if default_index: self.set_index(default_index)

        # signals
        self.signal_activated = self._widget.activated
        self.signal_changed   = self._widget.currentIndexChanged

        # Store self as autosettings
        self._autosettings_controls.append('self')

        # Load any previous settings
        self.load_gui_settings()

        # Bind to save gui settings when changed
        self.signal_changed.connect(self.save_gui_settings)

        if signal_activated: self.signal_activated.connect(signal_activated)
        if signal_changed:   self.signal_changed  .connect(signal_changed)


    def add_item(self, text="ploop"):
        """
        Adds an item to the combobox.
        """
        self._widget.addItem(str(text))
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

    def set_index(self, index=0, block_signals=False, **kwargs):
        """
        Sets current index.
        """
        if 'block_events' in kwargs:
            print('WARNING: block_events is antiquated. Please use block_signals instead.')
            block_signals = kwargs['block_events']

        if block_signals: self.block_signals()
        self._widget.setCurrentIndex(index)
        if block_signals: self.unblock_signals()
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


class Slider(GridLayout):
    """
    Slider with editable bounds. Note that sliders are limited to integer steps.

    Parameters
    ----------
    bounds=(0,1)
        Default bounds on the slider value.

    steps=1000
        Number of

    autosettings_path=None
        Unique identifier string that also works as a file name for saving settings.

    hide_numbers=False
        If True, numbers will be hidden.

    signal_value_changed=None : function
    signal_upper_changed=None : function
    signal_lower_changed=None : function
        Optional functions to which these signals will connect.

    Keyword arguments are sent to the pyqtgraph number boxes.

    Common Keyword Arguments
    ------------------------
    suffix : string
        Units label.

    siPrefix : bool
        Whether to use SI prefixes on the label.

    bounds=None : tuple or list
        2-long tuple or list specifying the allowed values.

    Signals
    -------
    self.signal_value_changed
        Emitted when the value of the slider changes.

    self.signal_upper_changed
        Emitted when the upper bound changes.

    self.signal_lower_changed
        Emitted when the lower bound changes.
    """
    def __init__(self, bounds=(0,1), steps=1000, autosettings_path=None, hide_numbers=False,
                 signal_value_changed=None,
                 signal_upper_changed=None,
                 signal_lower_changed=None, **kwargs):

        # Do all the parent class initialization; this sets _widget and _layout
        GridLayout.__init__(self, margins=False)

        # autosave settings path
        self._autosettings_path = autosettings_path

        # Add all the components to the GUI
        self.number_lower_bound = self.add(NumberBox(bounds[0], **kwargs))  .show(hide_numbers)
        self.number_value       = self.add(NumberBox(**kwargs), alignment=0).show(hide_numbers)
        self.number_upper_bound = self.add(NumberBox(bounds[1], **kwargs))  .show(hide_numbers)
        self.number_lower_bound._widget.setMaximumWidth(16777215)
        self.number_value      ._widget.setMaximumWidth(16777215)
        self.number_upper_bound._widget.setMaximumWidth(16777215)

        self.signal_value_changed = self.number_value.signal_changed
        self.signal_upper_changed = self.number_upper_bound.signal_changed
        self.signal_lower_changed = self.number_lower_bound.signal_changed

        self.new_autorow()
        self._widget_slider = self.add(_pg.QtGui.QSlider(_pg.QtCore.Qt.Horizontal), column_span=3, alignment=0)
        self._widget_slider.setMinimum(0)
        self.set_steps(steps)
        self.set_row_stretch(3)

        # list of controls we should auto-save / load
        self._autosettings_controls = [
            "self.number_upper_bound",
            "self.number_lower_bound",
            "self"]

        # load settings if a settings file exists and initialize
        self.load_gui_settings()

        # Signals
        self._widget_slider.valueChanged      .connect(self._slider_changed)
        self.number_lower_bound.signal_changed.connect(self._number_bound_changed)
        self.number_upper_bound.signal_changed.connect(self._number_bound_changed)
        self.number_value      .signal_changed.connect(self._number_value_changed)

        # Update the value
        self._slider_changed()

        # Connect to user functions
        if signal_value_changed: self.signal_value_changed.connect(signal_value_changed)
        if signal_upper_changed: self.signal_upper_changed.connect(signal_upper_changed)
        if signal_lower_changed: self.signal_lower_changed.connect(signal_lower_changed)

    def _slider_changed(self, *a):
        """
        Raw call that updates gui and calls event_changed(value)
        """
        v = self.get_value()
        self.number_value.set_value(v, block_signals=True)
        self.save_gui_settings()
        self.event_changed(v)

    def _number_bound_changed(self, *a):
        """
        Called when a bound changes. Defers to value and updates slider.
        """
        # Get values based on the slider and bounds
        v = self.number_value.get_value()
        u = self.number_upper_bound.get_value()
        l = self.number_lower_bound.get_value()

        if v < l: v = l
        if v > u: v = u

        # Set the value, triggering the update event.
        self.set_value(v)


    def _number_value_changed(self, *a):
        """
        Raw call when the number_value changes.
        """
        # Get values
        v = self.number_value.get_value()
        l = self.number_lower_bound.get_value()
        u = self.number_upper_bound.get_value()

        if v < l: v = l
        if v > u: v = u

        self.set_value(v)

    def get_steps(self):
        """
        Returns the number of slider steps.
        """
        return self._widget_slider.maximum()

    def set_steps(self, steps):
        """
        Sets the number of steps for the slider.
        """
        self._widget_slider.setMaximum(int(steps))
        self._widget_slider.setTickInterval(int(steps/10))
        return self

    def event_changed(self, value):
        """
        Dummy function to overload. Triggered whenever something changes.
        """
        return

    def set_value(self, value, block_signals=False, **kwargs):
        """
        Sets the value, respecting bounds and the slider steps.
        """
        if 'block_events' in kwargs:
            print('WARNING: block_events is antiquated. Please use block_signals instead.')
            block_signals = kwargs['block_events']

        # Convert it to the nearest integer.
        l = self.number_lower_bound.get_value()
        u = self.number_upper_bound.get_value()
        if u-l == 0: N = int(self.get_steps()/2)
        else:        N = int(_n.round(self.get_steps()*(value-l)/(u-l)))

        if block_signals: self.block_signals()

        # See if the slider will change
        slider_stayed = (N == self._widget_slider.value())

        # Slider imposes the boundaries
        self._widget_slider.setValue(N) # Only sends a signal change if it changes.

        # If the slider didn't change position, still update the number box.
        if slider_stayed:

            # Get the value based on slider and bounds
            v = self.get_value()

            if not v == self.number_value.get_value():

                # This will route us back to this function to impose the discrete slider steps.
                self.number_value.set_value(v)

                # Next time we won't arrive here because they'll be the same. Run the user event change
                self.event_changed(v)

        if block_signals: self.unblock_signals()

        self.save_gui_settings()

        return self

    def get_value(self):
        """
        Returns the current value with respect to the bounds, based on the
        slider position.
        """
        l = self.number_lower_bound.get_value()
        u = self.number_upper_bound.get_value()

        return l + (self._widget_slider.value()/self.get_steps())*(u-l)



class TabArea(BaseObject):
    """
    Simplified QTabWidget.

    Parameters
    ----------
    autosettings_path=None
        Set to a string file name to have this widget remember settings from
        the previous run.

    signal_switched=None : function
    signal_tab_close_requested : function
        Optional functions to which the signals will connect.

    Signals
    -------
    self.signal_switched
        Emitted when the tab switches.

    self.signal_tab_close_requested
        Emitted when someone tries to close a tab.

    """



    def __init__(self, autosettings_path=None,
                 signal_switched=None,
                 signal_tab_close_requested=None):

        # tab widget
        self._widget = _pg.Qt.QtGui.QTabWidget()
        self._widget.setTabsClosable(True)

        # Other stuff common to all objects
        BaseObject.__init__(self)
        self._alignment_default = 0 # By default, tabs fill all space.

        # tab widgets by index
        self.docked_tabs = []
        self.objects    = []
        self.popped_tabs = {}

        # signals
        self.signal_switched             = self._widget.currentChanged
        self.signal_tab_close_requested  = self._widget.tabCloseRequested

        # connect signals
        self.signal_switched.connect(self._tab_changed)
        self.signal_tab_close_requested.connect(self._tab_closed)

        # list of controls we should auto-save / load
        self._autosettings_path = autosettings_path
        self._autosettings_controls = ["self"]

        # Expose the count function
        self.get_docked_tab_count = self._widget.count

        # Load the previous settings. Of course, we cannot set the tab
        # yet (no tabs added!), so only load into self._lazy_load
        self.load_gui_settings(lazy_only=True)

        # Connect signals
        if signal_switched: self.signal_switched.connect(signal_switched)
        if signal_tab_close_requested: self.signal_tab_close_requested.connect(signal_tab_close_requested)

    def get_total_tab_count(self):
        """
        Returns the total tab count (integer).
        """
        return len(self.objects)

    def _tab_closed(self, *a):
        """
        Pops it out.
        """
        # This is the index of the requested closed tab. Pop it out
        self.pop_tab(a[0])


    def _tab_changed(self, *a): self.save_gui_settings()

    def __getitem__(self, n): return self.objects[n]

    def add_tab(self, title="Yeah!", margins=True, block_signals=True, **kwargs):
        """
        Adds a tab to the area, and creates the layout for this tab.

        Parameters
        ----------
        title : string
            Title of the tab.

        block_signals=True : bool
            Whether to block events when adding the tab. This is useful for
            auto-loading sequences.

        margins=True: bool
            Whether the tab should include margins.
        """
        if 'block_events' in kwargs:
            print('WARNING: block_events is antiquated. Please use block_signals instead.')
            block_signals = kwargs['block_events']

        self._widget.blockSignals(block_signals)

        # create a widget to go in the tab
        tab = GridLayout(margins=margins)
        tab.set_parent(self)
        tab.title = title

        # Remember this tab.
        self.objects.append(tab)

        # create and append the tab to the list
        # Note this makes _widget no longer able to be added to a QGridLayout
        # for some unknown reason. This is why we nest the grids
        self._widget.addTab(tab._widget, title)

        # Remember the unique tab id (total tab index)
        tab.index = self.get_total_tab_count()-1

        # Unblock signals
        self._widget.blockSignals(False)

        # try to lazy set the current tab
        if 'self' in self._lazy_load and self.get_total_tab_count() > self._lazy_load['self']:
            self.set_current_tab(self._lazy_load['self'])

        # Add this tab to the lists and put the grid layout on it.
        self.docked_tabs.append(tab)

        # Make sure it's visible (in case lazy popping happened.)
        self.show();

        # At this point it's been added normally, but may have some before it missing.

        # If this tab's index is in the popped list, pop it.
        if 'popped_tabs' in self._lazy_load \
        and tab.index    in self._lazy_load['popped_tabs']: self.pop_tab(-1)

        return tab

    add = add_tab

    def _remove_tab(self, n=0):
        """
        Removes the tab by visible index.
        """
        if n<0: n = self.get_docked_tab_count()+n

        # pop it from the internal "visible" list
        tab = self.docked_tabs.pop(n)

        # remove it from the gui
        self._widget.removeTab(n)

        # return it in case someone cares
        return tab

    def pop_tab(self, n=0):
        """
        Removes the tab by visible index, but
        puts its contents into a visible window.

        Returns the popped tab, but these also live in self.popped_tabs.
        """
        if n<0: n = self.get_docked_tab_count()+n

        tab = self._remove_tab(n)

        # Get the autosettings path.
        if self._autosettings_path: path = self._autosettings_path+'_tab'+str(tab.index)
        else: path = None

        # Window to house the grid from the popped tab. If this changes
        # structure, you may need to adjust unpop_tab()
        self.popped_tabs[tab.index] = Window(tab.title,
            autosettings_path = path,
            size=[self._widget.size().width(), self._widget.size().height()],
            margins = False)

        # Bind the close to the function
        def close(*a): self.unpop_tab(tab.index)
        self.popped_tabs[tab.index].event_close = close

        # Add the contents of the removed tab.
        self.popped_tabs[tab.index].add(tab, alignment=0)
        tab.show()
        self.popped_tabs[tab.index].show()

        # If we have no tabs after popping, hide it.
        if self.get_docked_tab_count() == 0 : self.hide()

        # Save the gui settings
        self.save_gui_settings()

        # Return it
        return self.popped_tabs[tab.index]

    def unpop_tab(self, index):
        """
        Reinserts the popped tab.

        Parameters
        ----------
        index : int
            Index of said popped tab.
        """
        self._widget.blockSignals(True)

        # Take the object out of the popped dictionary
        tab = self.popped_tabs.pop(index).objects[0]

        # Insert this at the appropriate place in the docked list
        for n in range(len(self.docked_tabs)):

            # If this tab's index is less than the next one in the list,
            # This is where we should insert it.
            if tab.index < self.docked_tabs[n].index:
                self.docked_tabs.insert(n,tab)
                break

        # Put it at the end
        if not tab in self.docked_tabs: self.docked_tabs.append(tab)

        # Remove all the widgets
        while self.get_docked_tab_count(): self._widget.removeTab(0)

        # Re-add them in order
        for t in self.docked_tabs: self._widget.addTab(t._widget, t.title)

        self.show()

        self._widget.blockSignals(False)

        # Save the gui settings
        self.save_gui_settings()

        return tab

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

    def _additional_save_gui_settings(self, d):
        """
        Adds to the gui settings databox (d) header some additional information.
        """
        d.h(popped_tabs=list(self.popped_tabs.keys()))

class Table(BaseObject):
    """
    Simplified QTableWidget. This is not a commonly used object. If you need
    features let Jack know.

    Parameters
    ----------
    columns=2 : int
    rows=1 : int
        Columns and rows of the table.

    signal_cell_changed=None : function
    signal_cell_clicked=None : function
    signal_cell_double_clicked=None : function
        Optional functions to which these signals connect.

    Signals
    -------
    self.signal_cell_changed
        Emitted when a cell's value changes.

    self.signal_cell_clicked
        Emitted when someone clicks a cell.

    self.signal_cell_double_clicked
        Emitted when someone double-clicks a cell.
    """

    def __init__(self, columns=2, rows=1,
                 signal_cell_changed=None,
                 signal_cell_clicked=None,
                 signal_cell_double_clicked=None):

        # create the widget
        self._widget = _pg.Qt.QtGui.QTableWidget(rows, columns)

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

        if signal_cell_changed: self.signal_cell_changed.connect(signal_cell_changed)
        if signal_cell_clicked: self.signal_cell_clicked.connect(signal_cell_clicked)
        if signal_cell_double_clicked: self.signal_cell_double_clicked.connect(signal_cell_double_clicked)




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

    def set_value(self, column=0, row=0, value='', block_signals=False, **kwargs):
        """
        Sets the value at column, row. This will create elements dynamically,
        and in a totally stupid while-looping way.

        Setting block_signals=True will temporarily block the widget from
        sending any signals when setting the value.
        """
        if 'block_events' in kwargs:
            print('WARNING: block_events is antiquated. Please use block_signals instead.')
            block_signals = kwargs['block_events']

        if block_signals: self.block_signals()

        # dynamically resize
        while column > self._widget.columnCount()-1: self._widget.insertColumn(self._widget.columnCount())
        while row    > self._widget.rowCount()   -1: self._widget.insertRow(   self._widget.rowCount())

        # set the value
        self._widget.setItem(row, column, _pg.Qt.QtGui.QTableWidgetItem(str(value)))

        if block_signals: self.unblock_signals()

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
    """
    This object has been replaced by TreeDictionary, which is much more powerful.

    This is an enhanced version of Table() with two columns, containing
    key / value pairs. It is designed to behave somewhat like a python
    dictionary object, and has a specific use, namely to store settings
    for writing to a header file.

    The keys are strings none of the characters in self.naughty
    (these will be replaced). The dictionary
    can be sorted by key, alphabetically.

    The values must be python code that can be eval'd.
    """

    naughty = [' ','\t','\n',',']

    def __init__(self):


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
        self.block_signals()

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
                    self._widget.item(n,1).setData(_pg.QtCore.Qt.BackgroundRole, _pg.Qt.QtGui.QColor('white'))
                except:
                    self._widget.item(n,1).setData(_pg.QtCore.Qt.BackgroundRole, _pg.Qt.QtGui.QColor('pink'))

        # unblock all signals
        self.unblock_signals()

    def get_item(self, key):
        """
        Returns the value associated with the key.
        """
        keys = list(self.keys())

        # make sure it exists
        if not key in keys:
            self.print_message("ERROR: '"+str(key)+"' not found."+'\n'+str(self))
            return None

        try:
            x = eval(self.get_value(1,keys.index(key)))
            return x

        except:
            self.print_message("ERROR: '"+str(self.get_value(1,keys.index(key)))+"' cannot be evaluated.\n"+str(self))
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
    """
    Tired of print statements to the command line? Try this for dumping
    your log info.
    """

    def __init__(self):
        self._widget = _pg.QtGui.QTextEdit()

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
    """
    Simplified QLineEdit.

    Parameters
    ----------

    text='' : str
        Default text.

    multiline=False : bool
        Whether this box should be multiple lines.

    autosettings_path=None : str
        If specified with a unique path-like string, this will save the state of the text box
        between runs.

    python_highlighting=False : bool
        Enables python syntax highlighting, but only in multiline mode.

    signal_changed=None : function
        Optional function to which this signal will connect.

    Signals
    -------
    self.signal_changed
        Emitted when the value / text changes.
    """
    def __init__(self, text="", multiline=False, autosettings_path=None, python_highlighting=False,
                 signal_changed=None, tip=None):

        self._multiline = multiline

        # pyqt objects
        if multiline:
            self._widget = _pg.QtGui.QTextEdit()

            # Python highlighting
            self._highlighter = _syntax.PythonHighlighter(self._widget.document())


        # Single-line
        else:
            self._widget = _pg.QtGui.QLineEdit()
            self.signal_return_pressed = self._widget.returnPressed

        # Set the text
        self.set_text(str(text))

        # signals
        self.signal_changed = self._widget.textChanged
        #self.signal_return_pressed = self._widget.returnPressed

        # Other stuff common to all objects
        BaseObject.__init__(self, autosettings_path=autosettings_path)

        # aliases
        self.get_value = self.get_text
        self.set_value = self.set_text

        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide

        # Store self as autosettings
        self._autosettings_controls.append('self')

        # Load any previous settings
        self.load_gui_settings()

        # Bind to save gui settings when changed
        self.signal_changed.connect(self.save_gui_settings)

        # Set the tooltip
        if tip: self._widget.setToolTip(tip)

        if signal_changed: self.signal_changed.connect(signal_changed)


    def get_text(self):
        """
        Returns the current text.
        """
        if self._multiline: return str(self._widget.toPlainText())
        else:               return str(self._widget.text())
    get_value = get_text

    def set_text(self, text="YEAH."):
        """
        Sets the current value of the text box.
        """
        # Make sure the text is actually different, so as not to
        # trigger a value changed signal
        s = str(text)
        if not s == self.get_text(): self._widget.setText(str(text))
        return self
    set_value = set_text


class Timer():
    """
    Simplified QTimer.

    Parameters
    ----------
    interval_ms=500 : int
        How long before signal_tick is emitted.

    single_shot=False
        Whether the timer fires only once

    signal_tick=None : function
        Optional function to which signal_tick will connect. Shortcut to
        calling self.signal_tick.connect(function).
    """
    def __init__(self, interval_ms=500, single_shot=False, signal_tick=None):


        # pyqt objects
        self._widget     = _pg.QtCore.QTimer();
        self.signal_tick = self._widget.timeout

        # aliases
        self.start        = self._widget.start
        self.stop         = self._widget.stop

        # Set the interval
        self.set_interval(interval_ms)
        self.set_single_shot(single_shot)

        if signal_tick: self.signal_tick.connect(signal_tick)

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

class _TimerExceptions(Timer):

    def __init__(self, interval_ms=500, always_print=True, **kwargs):
        Timer.__init__(self, interval_ms=interval_ms, **kwargs)

        self.always_print=always_print
        self.signal_tick.connect(self._timer_tick)
        self.signal_new_exception = _s.thread.signal()

    def __call__(self, interval_ms=500, always_print=True):
        """
        Periodically checks for a new exception and prints the last one if it exists.

        Note this is a really dumb object that just checks for sys.last_value; this
        doesn't ensure every passing exception is caught. If you know how to get a
        list of *all* exceptions, please let me know.

        Note this is a function call of a single instance of an enhanced Timer()
        object. This way, there won't be more than one such timer, all accessing
        the same exceptions.

        Parameters
        ----------
        interval_ms=500 : number
            How often to check for a new exception.

        always_print=True: bool
            Whether the timer should always print the exception when sending the
            signal.

        **kwargs are sent to Timer(), upon which this is based.

        Signals
        -------
        signal_tick
            Emitted when the timer ticks.

        signal_new_exception
            Emitted when a new exception is found.
        """
        self.set_interval(interval_ms)
        self.always_print=always_print
        self.start()
        return self


    def _timer_tick(self, *a):
        """
        Checks if there is a new exception and appends it.
        """
        if hasattr(_sys, 'last_value') and _sys.last_value:
            if self.always_print: _p()
            self.signal_new_exception.emit(_sys.last_value.args[0])
            _sys.last_value = None

# We will have one instance only.
TimerExceptions = _TimerExceptions()

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
    autosettings_path=None : str
        Where this object will save its settings when self.save() and self.load()
        are called without a path specified. None means no settings will be
        automatically saved.

    name=None : str
        If specified as a string, this will prepend name+'/' to all elements
        output in self.get_dictionary(), self.send_to_databox_header(), self.save()
        and will strip them from self.load() and self.update() accordingly

    show_header=False : bool
        Whether to show the top-level trunk.

    new_parameter_signal_changed=None : function
        Optional function to which signal_changed will automatically connect
        for all newly created parameters. You can also change this function
        after the tree is created by writing directly to self.any_signal_changed.

    Signals
    -------
    This object uses a different means of connecting signals.

    self.connect_signal_changed(name, function)
        This will connect the change event for the specified parameter
        name to the specified function.

    self.connect_any_signal_changed(function)
        This will connect the signal from anything changing to the specified
        function.
    """
    def __init__(self, autosettings_path=None, name=None, show_header=False, new_parameter_signal_changed=None):

        # Other stuff common to all objects
        BaseObject.__init__(self)

        self._widget             = _pg.parametertree.ParameterTree(showHeader=show_header)
        self.naughty             = ['\t', '\n', '\r', ',', ';','|'] # disallowed characters for keys (delimiters, and | for expanded)
        self._autosettings_path  = autosettings_path
        self._connection_lists   = dict()
        self._lazy_load          = dict()
        self._tree_widgets       = dict() # list of all tree widgets, including non-parameters.
        self.name = name
        self.default_signal_changed = None
        self.new_parameter_signal_changed = new_parameter_signal_changed

        # Load the previous settings (if any)
        self.load()

        # Expose the show and hide functions
        self.show = self._widget.show
        self.hide = self._widget.hide


    def __repr__(self):
        """
        How do display this object.
        """
        s = "TreeDictionary() -> "+str(self._autosettings_path)

        # for k in self.get_dictionary(True)[0]:

        #     if not self.get_type(k) in ['list']:
        #         s = s + "  "+k+" = "+repr(self[k])+"\n"
        #     else:
        #         s = s + "  "+k+" = "+repr(self[k])+" from "+repr(self.get_list_values(k)) + "\n"
        return s

    def block_signals(self):
        """
        Special version of block_signals that also loops over all tree elements.
        """
        # block events in the usual way
        BaseObject.block_signals(self)

        # loop over all top level parameters
        for i in range(self._widget.topLevelItemCount()):
            self._widget.topLevelItem(i).param.blockSignals(True)

        return self

    def block_events(self):
        """
        Antiquated. Use block_signals().
        """
        print("WARNING: block_events() and unblock_events() are antiquated. Use block_signals() and unblock_signals()")
        return self.block_signals()

    def unblock_signals(self):
        """
        Special version of unblock_signals that loops over all tree elements as well.
        """
        # unblock events in the usual way
        BaseObject.unblock_signals(self)

        # loop over all top level parameters
        for i in range(self._widget.topLevelItemCount()):
            self._widget.topLevelItem(i).param.blockSignals(False)

        return self

    def unblock_events(self):
        """
        Antiquated. Use unblock_signals().
        """
        print("WARNING: block_events() and unblock_events() are antiquated. Use block_signals() and unblock_signals()")
        return self.unblock_signals()

    def connect_any_signal_changed(self, function, unique=True):
        """
        Connects the "anything changed" signal for all of the tree to the
        specified function. Note this is using the sigTreeStateChanged signal,
        not the sigValueChanged signal (as is the case for self.connect_signal_changed())

        Parameters
        ----------
        function : function
            Function to connect to this signal.

        unique=True : bool
            Whether only one such connection is allowed.
        """

        # loop over all top level parameters
        for i in range(self._widget.topLevelItemCount()):

            # make sure there is only one connection!
            try:
                if unique:
                    self._widget.topLevelItem(i).param.sigTreeStateChanged.connect(
                        function, type=_pg.QtCore.Qt.UniqueConnection)
                else:
                    self._widget.topLevelItem(i).param.sigTreeStateChanged.connect(function)
            except:
                pass

        return self

    def connect_signal_changed(self, key, function, unique=True):
        """
        Connects a changed signal from the parameters of the specified key
        to the supplied function. Note this uses the sigValueChanged signal,
        not the sigTreeStateChanged signal (as is the case for
        self.connect_any_signal_changed()).

        Parameters
        ----------
        key : str
            Parameter whose signal_changed we connect.

        function : function
            Function to which signal_changed will connect.

        unique=True : bool
            Whether only one such connection will be allowed.
        """
        x = self._find_parameter(key.split("/"))

        # if it pooped.
        if x==None: return None

        # connect it
        if unique: x.sigValueChanged.connect(function, type=_pg.QtCore.Qt.UniqueConnection)
        else:      x.sigValueChanged.connect(function)

        # Keep track of the functions
        if key in self._connection_lists: self._connection_lists[key].append(function)
        else:                             self._connection_lists[key] = [function]

        return self

    def emit_signal_changed(self, key):
        """
        Emits a signal_changed for the specified key.

        Parameters
        ----------
        key : string
            Dictionary string, e.g., 'a/parameter/stuff'. Must be a key that already exists.

        Returns
        -------
        None.
        """
        s = key.split('/')

        # Find the parameter itself
        p = self._find_parameter(s)

        # Find the group parameter at the root.
        r = self._find_parameter([s[0]])

        # Emit the signal the same way pyqtgraph does.
        p.sigValueChanged.emit(r, self[key])

    def block_key_signals(self, key, ignore_error=False):
        """
        Temporarily disconnects the user-defined signals for the specified
        parameter key.

        Note this only affects those connections made with
        connect_signal_changed(), and I do not recommend adding new connections
        while they're blocked!
        """
        x = self._find_parameter(key.split("/"), quiet=ignore_error)

        # if it pooped.
        if x==None: return None

        # disconnect it from all its functions
        if key in self._connection_lists:
            for f in self._connection_lists[key]: x.sigValueChanged.disconnect(f)

        return self

    def unblock_key_signals(self, key, ignore_error=False):
        """
        Reconnects the user-defined signals for the specified
        parameter key (blocked with "block_user_signal_changed")

        Note this only affects those connections made with
        connect_signal_changed(), and I do not recommend adding new connections
        while they're blocked!
        """
        x = self._find_parameter(key.split("/"), quiet=ignore_error)

        # if it pooped.
        if x==None: return None

        # reconnect it to all its functions
        if key in self._connection_lists:
            for f in self._connection_lists[key]: x.sigValueChanged.connect(f)

        return self

    def _find_parameter(self, key_list, create_missing=False, quiet=False):
        """
        Recursively tries to find and return the parameter of the specified key. The key
        should be of the form

        ['branch1', 'branch2', 'parametername']

        Setting create_missing=True means if it doesn't find a branch it
        will create one.

        Setting quiet=True will suppress error messages (for checking)
        """
        # make a copy so this isn't destructive to the supplied list
        s = list(key_list)

        # if the length is zero, return the root widget
        if len(s)==0: return self._widget

        # the first key must be treated differently because it is
        # the main widget, not a branch
        r = self._clean_up_key(s.pop(0))

        # search for the root key
        result = self._widget.findItems(r, _pg.QtCore.Qt.MatchCaseSensitive | _pg.QtCore.Qt.MatchFixedString)

        # if it pooped and we're not supposed to create it, quit
        if len(result) == 0 and not create_missing:
            if not quiet: raise Exception("Could not find '"+r+"' in "+str(self))
            return None

        # otherwise use the first value
        elif len(result): x = result[0].param

        # otherwise, we didn't find it; create the branch and keep going
        else:
            key = '/'.join(key_list)

            # x is the empty group
            x = _pg.parametertree.Parameter.create(name=r, type='group', children=[], syncExpanded=True)
            self._tree_widgets[self._unstrip(key)] = x
            self._widget.addParameters(x)

            # Load the expanded state
            if key+'|expanded' in self._lazy_load:
                expanded = self._lazy_load.pop(key+'|expanded')
                self._tree_widgets[self._unstrip(key)].setOpts(expanded=expanded)

        # loop over the remaining keys, and use a different search method
        for n in s:

            # first clean up
            n = self._clean_up_key(n)

            # try to search for the key
            try: x = x.param(n)

            # key doesn't exist
            except:

                # if we're supposed to, create the new branch
                if create_missing:
                    x = x.addChild(_pg.parametertree.Parameter.create(name=n, type='group', children=[], syncExpanded=True))
                    if self.name: self._tree_widgets['/'+self.name+'/'+'/'.join(key_list)] = x
                    else:         self._tree_widgets[                  '/'.join(key_list)] = x

                # otherwise poop out
                else:
                    if not quiet: raise Exception("Could not find '"+'/'.join(key_list)+"' in "+str(self))
                    return None

        # return the last one we found / created.
        return x

    def _unstrip(self, key):
        """
        Prepends '/'+self.name+'/' to the key if available.
        """
        if self.name: return '/'+self.name+'/'+key
        else:         return key

    def _strip(self, key):
        """
        Strips '/'+self.name+'/' from the specified key.
        """
        if self.name is not None:
            s = '/'+self.name+'/'
            if key[0:len(s)] == s: return key[len(s):]
        return key

    def _clean_up_key(self, key):
        """
        Cleans up the key according to the rules specified in this exact
        function. Uses self.naughty, a list of naughty characters.
        """
        for n in self.naughty: key = key.replace(n, '_')
        return key

    def add_button(self, key, checkable=False, checked=False, tip=None):
        """
        Adds (and returns) a button at the specified location.
        """

        # first clean up the key
        key = self._clean_up_key(key)

        # split into (presumably existing) branches and parameter
        s = key.split('/')

        # make sure it doesn't already exist
        if not self._find_parameter(s, quiet=True) == None:
            self.print_message("ERROR: '"+key+"' already exists.\n"+str(self))
            return None

        # get the leaf key off the list.
        p = s.pop(-1)

        # create / get the branch on which to add the leaf
        b = self._find_parameter(s, create_missing=True)

        # quit out if it pooped
        if b == None: return None

        # create the leaf object
        ap = _pg.parametertree.Parameter.create(name=p, type='action', syncExpanded=True)
        self._tree_widgets[self._unstrip(key)] = ap

        # add it to the tree (different methods for root)
        if b == self._widget: b.addParameters(ap)
        else:                 b.addChild(ap)

        # modify the existing class to fit our conventions
        ap.signal_clicked = ap.sigActivated

        # Now set the default value if any
        if key in self._lazy_load:
            v = self._lazy_load.pop(key)
            self._set_value_safe(key, v, True, True)

        # Connect it to autosave (will only create unique connections)
        self.connect_any_signal_changed(self.autosave)

        return Button(key, checkable, checked, list(ap.items.keys())[0].button, tip=tip)

    def add_parameter(self, key='test', value=42.0, default_list_index=0, signal_changed=None, **kwargs):
        """
        Adds a parameter "leaf" to the tree. If self.default_signal_changed is
        a function, this runs self.connect_signal_changed(key, self.default_signal_changed).

        Parameters
        ----------

        key='test'
            The key of the leaf. It should be a string of the form
            "branch1/branch2/parametername" and will be nested as indicated.

        value=42.0
            Value of the leaf. If nothing else is specified, the parameter
            will be assumed to be the type of the value, so specifying 0 will
            result in an int, 0.0 will be a float, [] will be a list, etc.

        default_list_index=0
            When setting value=[], use this to specify the default selected
            list index.

        signal_changed=None
            Optional function to which signal_changed for this parameter will connect.


        Common Keyword Arguments
        ------------------------
        type=None
            If set to None, type will be automatically set to type(value).__name__.
            This will not work for all data types, but is
            a nice shortcut for floats, ints, strings, etc.
            If it doesn't work, just specify the type manually (see below).
        values
            Not used by default. Only relevant for type='list', or if you simply
            specified a list for this keyword argument, and should then
            be a list of possible values. If you go this route, you can use
            the value argument above to specify which item is selected by
            default.
        step=1
            Step size of incrementing numbers
        dec=False
            Set to True to enable decade increments.
        bounds
            Not used by default. Should be a 2-element tuple or list used to
            bound numerical values.
        default
            Not used by default. Used to specify the default numerical value
        siPrefix=False
            Set to True to display units on numbers
        suffix
            Not used by default. Used to add unit labels to elements.
        readonly=False
            Whether the user can edit the values.


        See pyqtgraph ParameterTree for more options. Particularly useful is the
        tip='insert your text' option, which supplies a tooltip!
        """

        # Check for limits (should be bounds)
        if 'limits' in kwargs:
            print('ParameterTree.add_parameter() WARNING: Please specify bounds rather than limits moving forward, to match changes in pyqtgraph API.')
            kwargs['bounds'] = kwargs.pop('limits')

        # update the default kwargs
        other_kwargs = dict(type=None) # Set type=None by default
        other_kwargs.update(kwargs)    # Slap on the ones we specified

        # Special case: we send a list to value => list
        if type(value)==list: other_kwargs['values'] = value

        # Auto typing for lists specified by either method
        if 'values' in other_kwargs:
            other_kwargs['type'] = 'list'
            value = other_kwargs['values'][default_list_index]

        # Normal autotyping
        elif other_kwargs['type'] == None: other_kwargs['type'] = type(value).__name__

        # Fix 'values' for list objects to be only strings
        if other_kwargs['type'] == 'list' or 'values' in other_kwargs:
            for n in range(len(other_kwargs['values'])):
                other_kwargs['values'][n] = str(other_kwargs['values'][n])

        # Now that the type is determined, set up other options
        if other_kwargs['type'] in ['int', 'float']:
            other_kwargs['compactHeight'] = False


        # split into (presumably existing) branches and parameter
        s = key.split('/')

        # make sure it doesn't already exist
        if not self._find_parameter(s, quiet=True) == None:
            self.print_message("Error: '"+key+"' already exists.\n"+str(self))
            return self

        # get the leaf key off the list.
        p = s.pop(-1)

        # create / get the branch on which to add the leaf
        b = self._find_parameter(s, create_missing=True)

        # quit out if it pooped
        if b == None:
            self.print_message('Error: Could not create \''+key+'\'')
            return self

        # create the leaf object
        leaf = _pg.parametertree.Parameter.create(name=p, value=value, syncExpanded=True, **other_kwargs)
        if self.name: self._tree_widgets['/'+self.name+'/'+key] = leaf
        else:         self._tree_widgets[                  key] = leaf

        # add it to the tree (different methods for root)
        if b == self._widget: b.addParameters(leaf)
        else:                 b.addChild(leaf)

        # Now set the default value if any
        if key in self._lazy_load:
            v = self._lazy_load.pop(key)
            self._set_value_safe(key, v, True, True)

        # And the expanded state
        if key+'|expanded' in self._lazy_load:
            expanded = self._lazy_load.pop(key+'|expanded')
            self.get_param(key).setOpts(expanded=expanded)

        # Connect it to autosave (will only create unique connections; will not duplicate)
        self.connect_any_signal_changed(self.autosave)
        if self.new_parameter_signal_changed: self.connect_signal_changed(key, self.new_parameter_signal_changed)
        if signal_changed:          self.connect_signal_changed(key, signal_changed)

        # Make the tool tip more responsive
        w = self.get_widget(key)
        if 'tip' in w.param.opts:
            w.setToolTip(0, w.param.opts['tip'])
            w.setToolTip(1, w.param.opts['tip'])

        # Connect to the default signal_changed function if it's specified.
        if self.default_signal_changed:
            self.connect_signal_changed(key, self.default_signal_changed)

        return self

    add = add_parameter


    def _get_parameter_dictionary(self, base_key, dictionary, sorted_keys, parameter):
        """
        Recursively loops over the parameter's children, adding
        keys (starting with base_key) and values to the supplied dictionary
        (provided they do not have a value of None).
        """

        # assemble the key for this parameter
        k = base_key + "/" + parameter.name()

        # first add this parameter (if it has a value)
        if not parameter.value()==None:
            sorted_keys.append(k[1:])
            dictionary[sorted_keys[-1]] = parameter.value()

        # now loop over the children
        for p in parameter.children():
            self._get_parameter_dictionary(k, dictionary, sorted_keys, p)

    def send_to_databox_header(self, destination_databox=None):
        """
        Sends all the information currently in the tree to the supplied
        databox's header, in alphabetical order. If the entries already
        exists, just updates them. If destination_databox=None, returns a
        new databox.
        """
        if destination_databox == None: destination_databox = _s.data.databox()
        k, d = self.get_dictionary()
        destination_databox.update_headers(d,k)


    def hide_parameter(self, key, opposite=False):
        """
        Hides the specified parameter.
        """
        #print('hiding', key, key.split('/'), self._find_parameter(key.split('/')))
        #self.block_signals()
        if opposite: self._find_parameter(key.split('/')).show()
        else:        self._find_parameter(key.split('/')).hide()
        #self.unblock_signals()

    def show_parameter(self, key, opposite=False):
        """
        Hides the specified parameter.
        """
        self.block_signals()
        try:
            if opposite: self._find_parameter(key.split('/')).hide()
            else:        self._find_parameter(key.split('/')).show()
        except:
            print('issue')
            pass
        self.unblock_signals()

    def get_key(self, param):
        """
        For the supplied param (see also self.get_param()) this will return the
        full key associated with it.

        This function is particularly useful within the function supplied to
        self.connect_any_signal_changed(), e.g., since the data sent to this
        function is a param.
        """
        if not param: return

        key = param.name()
        while param.parent():
            param = param.parent()
            key = param.name() + '/' + key

        return key

    def get_pyqtgraph_options(self, key):
        """
        Returns a copy of the pyqtgraph options for the supplied parameter key.
        """
        return dict(self.get_param(key).opts)

    def set_pyqtgraph_options(self, key, **kwargs):
        """
        Sets the pyqtgraph options for the supplied parameter key (e.g.
        key='my/parameter'). Keyword arguments are the options to set,
        e.g., suffix='pants'.

        Returns self.
        """
        self.get_param(key).setOpts(**kwargs)
        return self

    def get_param(self, key):
        """
        Returns the pyqtgraph Parameter associated with the specified key.
        """
        s = self._strip(key).split('/')
        if s[0] == '': s.pop(0)
        return self._find_parameter(s)

    def get_widget(self, key):
        """
        Returns the ParameterItem associated with the specified key.
        """
        # Get the usual widget
        w = self.get_param(key)

        # Create a QTreeWidgetItemIterator to search
        iterator = _pg.Qt.QtWidgets.QTreeWidgetItemIterator(self._widget)

        # Loop and search.
        item = iterator.value()
        while item is not None and item.param is not w:

            # Iterate
            iterator += 1
            item = iterator.value()

        return item

    def get_type(self, key):
        """
        Returns the type string of the specified parameter.
        """
        return str(self.get_param(key).opts['type'])

    def get_value(self, key):
        """
        Returns the value of the parameter with the specified key. If self.name
        is a string, removes '/'+self.name+'/' from the key.
        """
        # first clean up the name
        key = self._clean_up_key(self._strip(key))

        # now get the parameter object
        x = self._find_parameter(key.split('/'))

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
                    self.set_value(key, x.opts['values'][0])
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

    def get_list_values(self, key):
        """
        Returns the values for a list item of the specified key.

        Parameters
        ----------
        key : string
            Dictionary key to query.
        """
        # Make sure it's a list
        if not self.get_type(key) in ['list']:
            self.print_message('ERROR: "'+key+'" is not a list.\n'+str(self))
            return

        # Return a copy of the list values
        return list(self.get_param(key).opts['values'])

    def get_list_index(self, key):
        """
        Returns the index of the currently selected list item of the specified
        key.

        Parameters
        ----------
        key : string
            Dictionary key to query.
        """
        return self.get_list_values(key).index(self.get_value(key))

    def get_dictionary(self, short_keys=False):
        """
        Returns the list of parameters and a dictionary of values
        (good for writing to a databox header!)

        If self.name is a string, prepends '/'+self.name+'/' to all keys.

        Parameters
        ----------
        short_keys=False
            If True, will not return keys with '/'+self.name+'/' prepended.

        Return format is sorted_keys, dictionary
        """

        # output
        k = list()
        d = dict()

        # loop over the root items
        for i in range(self._widget.topLevelItemCount()):

            # grab the parameter item, and start building the name
            x = self._widget.topLevelItem(i).param

            # now start the recursive loop. Too complicated to do the name/ stuff
            # here...
            self._get_parameter_dictionary('', d, k, x)

        # If we have a name, prepend it to all keys
        if self.name is not None and not short_keys:

            # loop over all the keys
            for n in range(len(k)):

                # Assemble the new key
                k_new = '/'+self.name+'/' + k[n]

                # Replace the dictionary key
                d[k_new] = d.pop(k[n])

                # Update the list value
                k[n] = k_new

        return k, d

    def keys(self, short_keys=False):
        """
        Returns a list of the TreeDictionary keys.
        """
        return self.get_dictionary(short_keys=short_keys)[0]
    get_keys = keys

    def set_list_index(self, key, n, ignore_error=False, block_key_signals=False, block_all_signals=False):
        """
        Sets the selected index of a list (combo box) in the tree.

        Parameters
        ----------
        key : string
            Key to a list item / combo box in the tree.

        n : integer
            Index to select.

        ignore_error=False : bool
            If True, will ignore the error, such as not finding the key.

        block_key_signals=False : bool
            If True, this will not trigger a signal_changed, etc.

        block_all_signals=False : bool
            If True, try to block ALL signals while setting.
        """
        self.set_value(key, self.get_param(key).opts['values'][n],
                       ignore_error=ignore_error,
                       block_key_signals=block_key_signals,
                       block_all_signals=block_all_signals)

    def set_value(self, key, value, ignore_error=False, block_key_signals=False, block_all_signals=False):
        """
        Sets the variable of the supplied key to the supplied value.

        Parameters
        ----------
        key : string
            Dictionary key, e.g. 'a/b/parameter'

        value
            Value to set for this item.

        ignore_error=False : bool
            If True, will ignore the error, such as not finding the key.

        block_key_signals=False : bool
            If True, this will not trigger a signal_changed, etc.

        block_all_signals=False : bool
            If True, try to block ALL signals while setting.
        """

        # first clean up the key
        key = self._clean_up_key(self._strip(key))

        # If we're supposed to, block the user signals for this parameter
        if block_all_signals: self.block_signals()
        if block_key_signals: self.block_key_signals(key, ignore_error)

        # now get the parameter object
        x = self._find_parameter(key.split('/'), quiet=ignore_error)

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
        if block_key_signals: self.unblock_key_signals(key, ignore_error)
        if block_all_signals: self.unblock_signals()

        # Do other stuff if needed.
        self.after_set_value()

        return self

    __setitem__ = set_value

    def after_set_value(self):
        """
        This (dummy) function is run immediately after self.set_value().
        You can set this to a function of your own design.

        Returns
        -------
        self
        """

        return self

    def autosave(self, *a):
        """
        Runs self.save() with no arguments. This is a convenience function;
        you can connect signals to it, such as with
        self.connect_any_signal_changed()
        """
        # Only want to do this when updating values!
        if not a[1][0][1] == 'childAdded': self.save()

    def save(self, path=None, short_keys=False, include_expanded=True, filters='*', force_extension=None, **kwargs):
        """
        Saves all the parameters to a text file using the databox
        functionality. 
        
        Parameters
        ----------
        path=None: None, str, True
            Optional path (str) to save the data to. If None, saves to 
            self._autosettings_path. If self._autosettings_path=None, it does 
            not save. If True or 'ask', will pop up a dialog.
        
        short_keys=False : bool
            If True, do not prepend self.name to the keys.
        
        include_expanded=True : bool
            If True, save also the information about which branches are expanded.
        
        filters='*'
            File filter for the file dialog (for path=True or 'ask')

        force_extension=None
            If set to a string, e.g., 'txt', it will enforce that the chosen
            filename will have this extension. If set to True, will use
            the supplied filters.

        Other keyword arguments are sent to spinmob.dialogs.save().
        
        Returns
        -------
        self
        """
        if path in [True, 'ask']: 
            path = _s.dialogs.save(filters=filters, force_extension=force_extension, **kwargs)
            if path is None: return self
        
        if path is None:

            if self._autosettings_path == None: return self

            # Get the gui settings directory
            gui_settings_dir = _os.path.join(_cwd, 'egg_settings')

            # make sure the directory exists
            if not _os.path.exists(gui_settings_dir): _os.mkdir(gui_settings_dir)

            # Assemble the path
            path = _os.path.join(gui_settings_dir, self._autosettings_path)

        # make the databox object
        d = _d.databox()

        # In case someone modified self.name, rebuild _tree_widgets.
        ws = dict()
        for k in self._tree_widgets: # _tree_widgets is a dictionary; loop over keys.
            w = self._tree_widgets[k]
            k = self._strip(k)
            k = self._unstrip(k)
            ws[k] = w
        self._tree_widgets = ws

        # loop over the keys and add them to the databox header
        for k in self._tree_widgets:
            
            # Add the value if there is one
            if type(self._tree_widgets[k]).__name__ not in ['GroupParameter', 'ActionParameter']:
                d.insert_header(self._strip(k) if short_keys else k, self[k])

            # Add the expanded value
            if include_expanded:
                d.insert_header((self._strip(k) if short_keys else k) + '|expanded', self._tree_widgets[k].opts['expanded'])

        # save it
        try:
            d.save_file(path, force_overwrite=True, header_only=True)
        except:
            print('Warning: could not save '+path.__repr__()+' once. Could be that this is being called too rapidly.')

        return self

    def load(self, path=None, ignore_errors=True, block_key_signals=False, filters='*', **kwargs):
        """
        Loads all the parameters from a databox file. If path=None,
        loads from self._autosettings_path (provided this is not None).

        Parameters
        ----------
        path=None
            Path to load the settings from. If None, will load from the
            specified autosettings_path. If True or 'ask', pop up a dialog.
            
        ignore_errors=True
            Whether we should raise a stink when a setting doesn't exist.
            When settings do not exist, they are stuffed into the dictionary
            self._lazy_load.
        
        block_key_signals=False
            If True, the load will not trigger any signals.
            
        filters='*'
            Filters to use if there is a dialog.
            
        Other keyword arguments are sent to spinmob.dialogs.load()
        
        Returns
        -------
        self
        
        See also
        --------
        self.save(), self.update()
        """
        if path in [True, 'ask']: 
            path = _s.dialogs.load(filters=filters, **kwargs)
            if path is None: return self
        
        if path is None:

            # Bail if there is no path
            if self._autosettings_path == None: return self

            # Get the gui settings directory
            gui_settings_dir = _os.path.join(_cwd, 'egg_settings')

            # Get the final path
            path = _os.path.join(gui_settings_dir, self._autosettings_path)

        # make the databox object
        d = _d.databox(delimiter='\t')

        # only load if it exists
        if _os.path.exists(path): d.load_file(path, header_only=True)
        else:                     return None

        # update the settings
        self.update(d, ignore_errors=ignore_errors, block_key_signals=block_key_signals)
        return self

    def update(self, source_d, ignore_errors=True, block_key_signals=False):
        """
        Supply a dictionary or databox with a header of the same format
        and this will update this TreeDictionary's settings accordingly.

        This will store non-existent key-value pairs in the dictionary
        self._lazy_load. When you add settings in the future,
        these will be checked for the default values.

        If self.name is a string (not None), '/'+self.name+'/' will be stripped
        from the keys if present.
        
        Parameters
        ----------
        source_d : databox instance or dictionary
            Source of key-value pairs (dictionary or header of databox) with 
            which to update the tree.
        
        ignore_errors=True : bool
            If True, missing keys will simply not be used, with no warnings.
        
        block_key_signals=False : bool
            If True, block signals associated with each key while setting 
            the parameters.
            
        Returns
        -------
        self
        
        See also
        --------
        self.load(), self.save()
        """
        # Make sure d is a dictionary
        if not type(source_d) == dict: source_d = source_d.headers

        # Make a copy!
        source_d = dict(source_d)

        # Strip the name from each key if present
        for k in list(source_d.keys()): source_d[self._strip(k)] = source_d.pop(k)

        # Update the lazy load
        self._lazy_load.update(source_d)

        # loop over the lazy load dictionary and update
        for k in list(self._lazy_load.keys()):

            # Only proceed if the parameter exists
            if not self._find_parameter(k.split('/'), False, True) == None:

                # Pop the value so it's not set again in the future
                v = self._lazy_load.pop(k)
                self._set_value_safe(k, v, ignore_errors, block_key_signals)

        return self

    def _set_value_safe(self, k, v, ignore_errors=False, block_key_signals=False):
        """
        Actually sets the value, first by trying it directly.
        """
        # for safety: by default assume it's a repr() with python code
        try:
            self.set_value(k, v, ignore_error       = ignore_errors,
                                 block_key_signals = block_key_signals)

        except:
            raise Exception("Could not set '"+str(k)+"' to '"+str(v)+"'"+'\n'+str(self))



class DataboxPlot(_d.databox, GridLayout):
    """
    This object is a spinmob databox plus a collection of common controls and
    functionality for plotting, saving, loading, and manipulating data on the
    fly.

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

    name=None
        Stored in self.name for your purposes.

    styles=[]
        Optional list of dictionaries defining the styles, one for each plotted
        data set. Stored as self._styles (which you can later set again), each
        dictionary is used to send keyword arguments as PlotDataItem(**styles[n])
        for the n'th data set. Note these are the same keyword arguments one
        can supply to pyqtgraph's plot() function. See pyqtgraph examples, e.g.,

        import pyqtgraph.examples; pyqtgraph.examples.run()

        or http://www.pyqtgraph.org/documentation/plotting.html

        Typical example: styles = [dict(pen=(0,1)), dict(pen=None, symbol='o')]

    **kwargs are sent to the underlying databox

    Note checking the "Auto-Save" button does not result in the data being automatically
    saved until you explicitly call self.autosave() (which does nothing
    unless auto-saving is enabled).

    About Plot Scripts
    ------------------
    Between the top controls and the plot region is a text box in which you can
    define an arbitrary python plot script (push the "Script" button to toggle
    its visibility). The job of this script is minimally to define x and y.
    These can both be arrays of data or lists of arrays of data to plot. You may
    also specify None for one of them. You can also similarly (optionally)
    define error bars with ey, xlabels, ylabels, and styles. Once you have
    stored some columns of data in this object, try selecting the different
    options in the combo box to see example / common scripts, or select "Edit"
    to create your own.

    The script's namespace includes: all of numpy (sin, cos, sqrt, array, etc),
    all of scipy.special (erf, erfc, etc), d=self, styles=self._styles,
    sm=s=_s=spinmob, and everything in self.plot_script_globals.

    Optional additional globals can be defined by setting
    self.plot_script_globals to a dictionary of your choice. For example,
    self.plot_script_globals = dict(d2=self.my_other_databox) will expose
    self.my_other_databox to the script as d2.

    The script is executed by either self.plot() or when you click the
    "Try it!" button. If there is an error, the script will turn pink and the
    error will be printed to the console, but this is a "safe" crash and will
    not affect the flow of the program otherwise.

    Importantly, this script will NOT affect the underlying data unless you
    use it to actually modify the variable d, e.g., d[0] = d[0]+3.

    """

    def __init__(self, file_type="*.dat", autosettings_path=None, autoscript=1,
                 name=None, show_logger=False, styles=[], **kwargs):

        self.name = name

        # Do all the parent class initialization; this sets _widget and _layout
        GridLayout.__init__(self, margins=False)
        _d.databox.__init__(self, **kwargs)
        self._alignment_default = 0 # By default, fill all space.

        # top row is main controls
        self.grid_controls   = self.place_object(GridLayout(margins=False), alignment=0)
        self.grid_controls.event_resize = self._event_resize_databox_plot

        self.grid_controls1  = self.grid_controls.place_object(GridLayout(margins=False), 0,0, alignment=1)

        self.button_clear    = self.grid_controls1.place_object(Button("Clear", tip='Clear all header and columns.').set_width(40), alignment=1)
        self.button_load     = self.grid_controls1.place_object(Button("Load",  tip='Load data from file.')         .set_width(40), alignment=1)
        self.button_save     = self.grid_controls1.place_object(Button("Save",  tip='Save data to file.')           .set_width(40), alignment=1)
        self.combo_binary    = self.grid_controls1.place_object(ComboBox(['Text', 'float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'complex64', 'complex128', 'complex256'], tip='Format of output file columns.'), alignment=1)
        self.button_autosave = self.grid_controls1.place_object(Button("Auto",   checkable=True, tip='Enable autosaving. Note this will only autosave when self.autosave() is called in the host program.').set_width(40), alignment=1)
        self.number_file     = self.grid_controls1.place_object(NumberBox(int=True, bounds=(0,None), tip='Current autosave file name prefix number. This will increment every autosave().'))
        
        self.label_path      = self.grid_controls.place_object(Label(""), 1,0)

        self.grid_controls2 = self.grid_controls.place_object(GridLayout(margins=False), 0,1, alignment=1)
        self.grid_controls.set_column_stretch(2)

        self.button_script     = self.grid_controls2.place_object(Button  ("Script",      checkable=True, checked=True, tip='Show the script box.').set_width(50)).set_checked(False)
        self.combo_autoscript  = self.grid_controls2.place_object(ComboBox(['Edit', 'x=d[0]', 'Pairs', 'Triples', 'x=d[0], ey', 'x=None', 'User'], tip='Script mode. Select "Edit" to modify the script.')).set_value(autoscript)
        self.button_multi      = self.grid_controls2.place_object(Button  ("Multi",       checkable=True, tip="If checked, plot with multiple plots. If unchecked, all data on the same plot.").set_width(40)).set_checked(True)
        self.button_link_x     = self.grid_controls2.place_object(Button  ("Link",        checkable=True, tip="Link the x-axes of all plots.").set_width(40)).set_checked(autoscript==1)
        self.button_enabled    = self.grid_controls2.place_object(Button  ("Enable",      checkable=True, tip="Enable this plot.").set_width(50)).set_checked(True)

        # second rows is the script
        self.new_autorow()

        # grid for the script
        self.grid_script = self.place_object(GridLayout(margins=False), 0,1, alignment=0)

        # script grid
        self.button_save_script = self.grid_script.place_object(Button("Save", tip='Save the shown script.').set_width(40), 2,1)
        self.button_load_script = self.grid_script.place_object(Button("Load", tip='Load a script.').set_width(40), 2,2)
        self.button_plot        = self.grid_script.place_object(Button("Plot!", tip='Attempt to plot using the shown script!').set_width(40), 2,3)

        self.script = self.grid_script.place_object(TextBox("", multiline=True,
            tip='Script defining how the data is plotted. The minimum requirement is that\n'+
                'x and y (arrays, lists of arrays, or None) are defined. Optionally, you may\n'+
                'also define:\n\n'+

                '  ey : number, array or list of numbers and/or arrays\n    defines y-error bars for each data set\n\n'+

                '  xlabels, ylabels : string or list of strings\n    defines axis labels for each data set.\n\n'+

                '  styles : list of dictionaries and/or or None\'s (default)\n    Keword arguments to be sent to pyqtgraph.PlotDataItem() when\n    creating the curves.\n\n'+

                'The script knows about all numpy objects (sin, cos, sqrt, array, etc),\n'+
                'scipy.special functions (also via special.), and self.plot_script_globals,\n'+
                '(dictionary) which allows you to include your own variables and objects.\n'+
                'Finally, the following variables are defined by default:\n\n'+

                '  mkPen & mkBrush : from pyqtgraph, used for creating styles.\n\n'+

                '  d : this DataboxPlot instance\n\n' +

                '  spinmob, sm, s, and _s : spinmob library'),
                1,0, row_span=4, alignment=0)
        self.script.set_height(120)

            # g = dict(_n.__dict__, np=_n, _n=_n, numpy=_n)
            # g.update(_scipy_special.__dict__, special=_scipy_special)
            # g.update(dict(mkPen=_pg.mkPen, mkBrush=_pg.mkBrush))
            # g.update(dict(d=self, x=None, y=None, ex=None, ey=None, styles=self._styles))
            # g.update(dict(xlabels='x', ylabels='y'))
            # g.update(dict(spinmob=_s, sm=_s, s=_s, _s=_s))
            # g.update(self.plot_script_globals)

        #self.script.set_style('font-family:monospace; font-size:12;')
        # Windows compatibility
        font = _s._qtw.QFont()
        font.setFamily("monospace")
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.script._widget.setFont(font)

        self._label_script_error = self.place_object(Label('ERRORS GO HERE'), 0,2, column_span=2, alignment=0)
        self._label_script_error.hide()


        # make sure the plot fills up the most space
        self.set_row_stretch(3)

        # plot area
        self.grid_plot = self.place_object(GridLayout(margins=False), 0,3, column_span=self.get_column_count(), alignment=0)

        # History area
        self.grid_logger = self.add(GridLayout(margins=False), 0,4, column_span=self.get_column_count(), alignment=0)

        self.grid_logger.add(Label('History:'), alignment=0)
        self.grid_logger.set_column_stretch(2)
        self.number_history = self.grid_logger.add(NumberBox(
            0, step=100, bounds=(0,None), int=True,
            tip='How many points to keep in the plot when using append_row(). Set to 0 to keep everything.\n'+
                'You can also use the script to display the last N points with indexing,\n'+
                'e.g., d[0][-200:], which will not delete the old data.')).set_width(70)

        self.text_log_note = self.grid_logger.add(TextBox(
            'Note', tip='Note to be added to the header when saving.'), alignment=0)

        self.button_log_data = self.grid_logger.add(Button(
            'Log Data',
            checkable=True,
            signal_toggled=self._button_log_data_toggled,
            tip='Append incoming data to a text file of your choice when calling self.append_row(). Saves the current data and header first.'
            )).set_width(70).set_colors_checked('white', 'red')

        self.label_log_path = self.grid_logger.add(Label('')).hide()
        if not show_logger: self.grid_logger.hide()



        ##### set up the internal variables

        # will be set later. This is where files will be dumped to when autosaving
        self._autosave_directory = None

        # file type (e.g. *.dat) for the file dialogs
        self.file_type = file_type

        # autosave settings path
        self._autosettings_path = autosettings_path

        # holds the curves and plot widgets for the data, and the buttons
        self._curves          = []
        self._errors          = []
        self._legend          = None
        self._styles          = []   # List of dictionaries to send to PlotDataItem's
        self._previous_styles = None # Used to determine if a rebuild is necessary
        self.plot_widgets     = []
        self.ROIs             = []

        ##### Functionality of buttons etc...

        self.button_plot       .signal_clicked.connect(self._button_plot_clicked)
        self.button_save       .signal_clicked.connect(self._button_save_clicked)
        self.button_save_script.signal_clicked.connect(self._button_save_script_clicked)
        self.button_load       .signal_clicked.connect(self._button_load_clicked)
        self.button_load_script.signal_clicked.connect(self._button_load_script_clicked)
        self.button_clear      .signal_clicked.connect(self._button_clear_clicked)
        self.button_autosave   .signal_toggled.connect(self._button_autosave_clicked)
        self.button_script     .signal_toggled.connect(self._button_script_clicked)
        self.combo_binary      .signal_changed.connect(self._combo_binary_changed)
        self.combo_autoscript  .signal_changed.connect(self._combo_autoscript_clicked)
        self.button_multi      .signal_toggled.connect(self._button_multi_clicked)
        self.button_link_x     .signal_toggled.connect(self._button_link_x_clicked)
        self.button_enabled    .signal_toggled.connect(self._button_enabled_clicked)
        self.number_file       .signal_changed.connect(self._number_file_changed)
        self.script            .signal_changed.connect(self._script_changed)
        self.number_history    .signal_changed.connect(self.save_gui_settings)
        self.text_log_note     .signal_changed.connect(self.save_gui_settings)

        # list of controls we should auto-save / load
        self._autosettings_controls = ["self.combo_binary",
                                       "self.combo_autoscript",
                                       "self.button_enabled",
                                       "self.button_multi",
                                       "self.button_link_x",
                                       "self.button_script",
                                       "self.number_file",
                                       "self.script",
                                       "self.number_history",
                                       "self.text_log_note", ]

        # load settings if a settings file exists and initialize
        self.load_gui_settings()
        self._synchronize_controls()

    def _event_resize_databox_plot(self):
        """
        Called when the widget resizes.
        """
        # If we're below a certain width, move the right controls below
        # if self.grid_controls._widget.width() < 700: self.grid_controls.place_object(self.grid_controls2, 0,1, alignment=1)
        # else:                                        self.grid_controls.place_object(self.grid_controls2, 2,0, alignment=2)
        
    def _button_log_data_toggled(self, *a):
        """
        Called when someone toggles the dump button. Ask for a path or remove the path.
        """
        if self.button_log_data.is_checked():
            path = _s.dialogs.save(self.file_type, 'Dump incoming data to this file.', force_extension=self.file_type)

            # If the path is valid, reset the clock, write the header
            if path:

                # Store the path in a visible location
                self.label_log_path.set_text(path).show()
                self.text_log_note.disable()

                # Add header information to the Databox
                self.h(**{
                    'DataboxPlot_Note'              : self.text_log_note(),
                    'DataboxPlot_LogFileCreated'    : _t.ctime(_t.time()),
                    'DataboxPlot_LogFileCreated(s)' : _t.time(),})

                if len(self.ckeys): self.h(**{'Log File Initial Row Count' : len(self[0])})
                else:               self.h(**{'Log File Initial Row Count' : 0})

                # Save it forcing overwrite
                self.save_file(path, force_overwrite=True)

            else:
                self.button_log_data.set_checked(False)
                self.text_log_note.enable()

        else:
            self.label_log_path.set_text('').hide()
            self.text_log_note.enable()

    def __repr__(self): return "<DataboxPlot instance: " + self._repr_tail()

    def _button_enabled_clicked(self, *a):  self.save_gui_settings()
    def _number_file_changed(self, *a):     self.save_gui_settings()
    def _script_changed(self, *a):          self.save_gui_settings()

    def _button_save_script_clicked(self, *a):
        """
        When someone wants to save their script.
        """
        path = _s.dialogs.save('*.py', text='Save script to...', force_extension='*.py', default_directory='DataboxPlot_scripts')
        if not path: return

        f = open(path, 'w')
        f.write(self.script.get_text())
        f.close()

    def _button_load_script_clicked(self, *a):
        """
        When someone wants to load their script.
        """
        path = _s.dialogs.load('*.py', default_directory='DataboxPlot_scripts')
        if not path: return

        self.load_script(path)

    def load_script(self, path=None):
        """
        Loads a script at the specified path.

        Parameters
        ----------
        path=None
            String path of script file. Setting this to None will bring up a
            load dialog.
        """
        if path == None: self._button_load_script_clicked()
        else:
            f = open(path, 'r')
            s = f.read()
            f.close()

            self.script.set_text(s)
            self.combo_autoscript.set_value(0)

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
            path = _s.dialogs.save(filters=self.file_type, force_extension=self.file_type)

            # abort if necessary
            if not path:
                self.button_autosave.set_checked(False)
                return

            # otherwise, save the info!
            self._autosave_directory, filename = _os.path.split(path)
            self.label_path.set_text(filename)

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

        self.after_clear()

    def after_clear(self):
        """
        Dummy function you can overwrite to run code after the clear button
        is done.
        """
        return

    def before_save_file(self):
        """
        Called at the start of save_file(). You can overload this to insert
        your own functionality.
        """
        return

    def append_row(self, row, ckeys=None, history=True):
        """
        Appends the supplied row of data, using databox.append_row(), but with
        history equal to the current value in self.number_history. Also, if the
        "Log Data" button is enabled, appends the new data to the log file.

        Parameters
        ----------
        row : list or 1D array
            Values for the new row of data.

        ckeys=None : list of strings (optional)
            Column keys the databox must enforce. If they don't match the current
            keys, the columns will be cleared and the new ckeys will be used.

        history=True : True or integer
            Number of previous data points to keep in memory. If True (default),
            use self.number_history's value. If 0, kep all data.
        """
        if history is True: history = self.number_history()

        # First append like normal
        super().append_row(row, ckeys, history)

        # If the dump file is checked, dump the row
        if self.button_log_data() and len(self.label_log_path()):

            # Get a list of strings
            row_strings = []
            for x in row: row_strings.append(str(x))

            # The most pythony python that ever pythoned.
            delimiter = '\t' if self.delimiter is None else self.delimiter

            # Append a single line.
            f = open(self.label_log_path(), 'a')
            f.write(delimiter.join(row_strings)+'\n')
            f.close()

        return self

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
            Note that setting header_only=True will include settings and the usual
            databox header.

        **kwargs are sent to the normal databox save_file() function.
        """
        self.before_save_file()

        # Update the log file note
        self.h(**{'DataboxPlot_Note' : self.text_log_note(),})

        # Update the binary mode
        if not 'binary' in kwargs: kwargs['binary'] = self.combo_binary.get_text()

        # if it's just the settings file, make a new databox with no columns
        if just_settings: d = _d.databox()

        # otherwise use the internal databox with the columns
        else: d = self

        # add all the controls settings to the header
        for x in self._autosettings_controls: self._store_gui_setting(d, x)

        # save the file using the skeleton function, so as not to recursively
        # call this one again!
        _d.databox.save_file(d, path, self.file_type, self.file_type, force_overwrite, **kwargs)

        return self

    def load_file(self, path=None, just_settings=False, just_data=False):
        """
        Loads a data file. After the file is loaded, calls self.after_load_file(self),
        which you can overwrite if you like!

        Parameters
        ----------
        path=None
            Optional path. If not specified, pops up a dialog.
        
        just_settings=False
            Load only the settings, not the data
        
        just_data=False
            Load only the data, not the settings.

        Returns
        -------
        self
        """
        # if it's just the settings file, make a new databox
        if just_settings:
            d = _d.databox()
            header_only = True

        # otherwise use the internal databox
        else:
            d = self
            header_only = False

        # Load the file
        result = _d.databox.load_file(d, path, filters=self.file_type, header_only=header_only, quiet=just_settings)

        # import the settings if they exist in the header
        if not just_data:

            if not None == result:
    
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

    def _generate_autoscript(self):
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
            sx = "x = ( d[0]"
            sy = "y = ( d[1]"

            # hard code the first labels
            sxlabels = "xlabels = '" +self.ckeys[0]+"'"
            sylabels = "ylabels = ( '"+self.ckeys[1]+"'"

            # loop over any remaining columns and append.
            for n in range(2,len(self)):
                sy += ", d["+str(n)+"]"
                sylabels += ", '"+self.ckeys[n]+"'"

            return sx+" )\n"+sy+" )\n\n"+sxlabels+"\n"+sylabels+" )\n"


        # Column pairs
        elif self.combo_autoscript.get_index() == 2:

            # hard code the first columns
            sx = "x = ( d[0]"
            sy = "y = ( d[1]"

            # hard code the first labels
            sxlabels = "xlabels = ( '"+self.ckeys[0]+"'"
            sylabels = "ylabels = ( '"+self.ckeys[1]+"'"

            # Loop over the remaining columns and append
            for n in range(1,int(len(self)/2)):
                sx += ", d["+str(2*n  )+"]"
                sy += ", d["+str(2*n+1)+"]"
                sxlabels += ", '"+self.ckeys[2*n  ]+"'"
                sylabels += ", '"+self.ckeys[2*n+1]+"'"

            return sx+" )\n"+sy+" )\n\n"+sxlabels+" )\n"+sylabels+" )\n"

        # Column triples
        elif self.combo_autoscript.get_index() == 3:

            # hard code the first columns
            sx = "x = ( d[0], d[0]"
            sy = "y = ( d[1], d[2]"

            # hard code the first labels
            sxlabels = "xlabels = ( '"+self.ckeys[0]+"', '"+self.ckeys[0]+"'"
            sylabels = "ylabels = ( '"+self.ckeys[1]+"', '"+self.ckeys[2]+"'"

            # Loop over the remaining columns and append
            for n in range(1,int(len(self)/3)):
                sx += ", d["+str(3*n  )+"], d["+str(3*n  )+"]"
                sy += ", d["+str(3*n+1)+"], d["+str(3*n+2)+"]"

                sxlabels += ", '"+self.ckeys[3*n  ]+"', '"+self.ckeys[3*n  ]+"'"
                sylabels += ", '"+self.ckeys[3*n+1]+"', '"+self.ckeys[3*n+2]+"'"

            return sx+" )\n"+sy+" )\n\n"+sxlabels+" )\n"+sylabels+" )\n"

        # Shared d[0] and pairs of y, ey
        elif self.combo_autoscript.get_index() == 4:

            # hard code the first columns
            sx  = "x  = ( d[0]"
            sy  = "y  = ( d[1]"
            sey = "ey = ( d[2]"

            # hard code the first labels
            sxlabels = "xlabels = '"  +self.ckeys[0]+"'"
            sylabels = "ylabels = ( '"+self.ckeys[1]+"'"

            # loop over any remaining columns and append.
            for n in range(1,int((len(self)-1)/2)):
                sy  += ", d["+str(2*n+1)  +"]"
                sey += ", d["+str(2*n+2)+"]"
                sylabels += ", '"+self.ckeys[2*n+1]+"'"

            return sx+" )\n"+sy+" )\n"+sey+" )\n\n"+sxlabels+"\n"+sylabels+" )\n"

        # Shared x-axis (None)
        elif self.combo_autoscript.get_index() == 5:

            # hard code the first columns
            sx = "x = ( None"
            sy = "y = ( d[0]"

            # hard code the first labels
            sxlabels = "xlabels = 'Array Index'"
            sylabels = "ylabels = ( '"+self.ckeys[0]+"'"

            # loop over any remaining columns and append.
            for n in range(1,len(self)):
                sy += ", d["+str(n)+"]"
                sylabels += ", '"+self.ckeys[n]+"'"

            return sx+" )\n"+sy+" )\n\n"+sxlabels+"\n"+sylabels+" )\n"



        else: return self.autoscript_custom()

    def autoscript_custom(self):
        """
        Overwrite this function (returning a valid script string) to redefine
        the custom autoscript.
        """
        return "To use the 'Custom Autoscript' option, you must overwrite the function 'self.autoscript_custom' with your own (which must return a valid python script string)."

    # Globals to help execute the plot script
    plot_script_globals = dict();

    def plot(self):
        """
        Updates the plot according to the script and internal data.
        """

        # If we're disabled or have no data, clear
        if not self.button_enabled.is_checked() \
        or len(self)==0:
            self._set_number_of_plots([],[])
            return self

        # if there is no script, create a default
        if not self.combo_autoscript.get_index()==0:
            self.script.set_text(self._generate_autoscript())

        ##### Try the script and make the curves / plots match
        try:

            # get globals for sin, cos etc and libraries
            g = dict(_n.__dict__, np=_n, _n=_n, numpy=_n)
            g.update(_scipy_special.__dict__, special=_scipy_special)
            g.update(dict(spinmob=_s, sm=_s, s=_s, _s=_s))

            # Pyqtgraph globals
            g.update(dict(mkPen=_pg.mkPen, mkBrush=_pg.mkBrush))

            # Object globals
            g.update(dict(d=self, x=None, y=None, ex=None, ey=None, styles=self._styles))

            # Default values
            g.update(dict(xlabels='x', ylabels='y'))

            # Other globals
            g.update(self.plot_script_globals)

            # run the script.
            exec(self.script.get_text(), g)

            # x & y should now be data arrays, lists of data arrays or Nones
            x = g['x']
            y = g['y']
            #ex = g['ex']
            ey = g['ey'] # Use spinmob._plotting_mess

            # make everything the right shape
            x, y = _s.fun._match_data_sets(x,y)
            ey   = _s.fun._match_error_to_data_set(y,ey)

            # xlabels and ylabels should be strings or lists of strings
            xlabels = g['xlabels']
            ylabels = g['ylabels']

            # Make sure these are iterable lists
            if not type(xlabels) in [tuple,list]: xlabels = [xlabels]
            if not type(ylabels) in [tuple,list]: ylabels = [ylabels]

            xlabels = list(xlabels)
            ylabels = list(ylabels)

            # Increase the length to match
            while len(xlabels) < len(x): xlabels.append('')
            while len(ylabels) < len(y): ylabels.append('')

            # Decrease the label length to match
            while len(xlabels) > len(x): xlabels.pop(-1)
            while len(ylabels) > len(y): ylabels.pop(-1)

            # Get the styles
            self._styles = g['styles']

            # make sure we have exactly the right number of plots
            self._set_number_of_plots(y, ey)
            self._update_linked_axes()
            self._update_legend(ylabels)

            # return if there is nothing.
            if len(y) == 0: return

            # now plot everything
            for n in range(len(y)):

                # Set the curve data
                self._curves[n].setData(x[n],y[n])
                if ey[n] is not None:
                    self._errors[n].setData(x=x[n], y=y[n], top=ey[n], bottom=ey[n])

                # set the labels
                i = min(n, len(self.plot_widgets)-1)
                self.plot_widgets[i].setLabel('left',   ylabels[n])
                self.plot_widgets[i].setLabel('bottom', xlabels[n])

                # special case: hide if None
                if xlabels[n] == None:
                    self.plot_widgets[i].getAxis('bottom').showLabel(False)

                # special case: hide if None or we're in single-plot mode (legend handles this)
                if ylabels[n] == None or not self.button_multi.is_checked():
                    self.plot_widgets[i].getAxis('left').showLabel(False)

            # unpink the script, since it seems to have worked
            self.script       .set_colors(None, None)
            self.button_script.set_colors(None, None)

            # Remember the style of this plot
            if self._styles: self._previous_styles = list(self._styles)
            else:            self._previous_styles = self._styles

            # Clear the error if present
            self._label_script_error.hide()

        # otherwise, look angry and don't autosave
        except Exception as e:
            self._e = e
            if _s.settings['dark_theme_qt']: self.script.set_colors(None,'#552222')
            else:                            self.script.set_colors(None,'pink')
            self.button_script.set_colors('black', 'pink')

            # Show the error
            self._label_script_error.show()
            self._label_script_error.set_text('OOP! '+ type(e).__name__ + ": '" + str(e.args[0]) + "'")
            if _s.settings['dark_theme_qt']: self._label_script_error.set_colors('pink', None)
            else:                            self._label_script_error.set_colors('red', None)

        return self

    def autosave(self):
        """
        Autosaves the currently stored data, but only if autosave is checked!
        """
        # make sure we're suppoed to
        if self.button_autosave.is_checked():

            # save the file
            self.save_file(_os.path.join(self._autosave_directory, "%04d " % (self.number_file.get_value()) + self.label_path.get_text()))

            # increment the counter
            self.number_file.increment()

        return self

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


    def _plots_already_match_data(self, y, ey):
        """
        Checks if curves and plots all match the data and error.
        """
        # First check if the styles have changed
        if self._styles != self._previous_styles: return False

        N = len(y)

        # We should always have a curve and an error bar for each data set.
        if N != len(self._curves) or N != len(self._errors): return False

        # If we're in multiplots and the number of plots doesn't match the number of data sets
        if self.button_multi.is_checked() and N != len(self.plot_widgets): return False

        # If we're in single plot mode and the number of plots is not 1
        if not self.button_multi.is_checked() and not len(self.plot_widgets) == 1: return False

        # Make sure all the None's line up
        for n in range(N):
            if ey[n] is     None and self._errors[n] is not None: return False
            if ey[n] is not None and self._errors[n] is     None: return False

        # All good!
        return True

    def _update_legend(self, ylabels):
        """
        Updates the legend according to the list of ylabels.
        """
        if not self._legend: return

        # Clear it
        self._legend.clear()

        # Loop and append
        for i in range(len(ylabels)):

            # Only add the legend item if it's interesting
            if ylabels[i] not in [None, '', False]:
                self._legend.addItem(self._curves[i], ylabels[i])

    def _set_number_of_plots(self, y, ey):
        """
        Adjusts number of plots & curves to the desired value the gui, populating
        self._curves list as needed based on y and ey.

        y and ey must be equal-length lists, but ey can have None elements.
        """
        # If we match, we're done!
        if self._plots_already_match_data(y,ey): return

        # Otherwise, we rebuild from scratch (too difficult to track everything)

        # don't update anything until we're done
        self.grid_plot.block_signals()

        # clear the plots
        while len(self.plot_widgets):

            # pop the last plot widget and remove all items
            p = self.plot_widgets.pop()
            p.clear()

            # remove it from the grid so nothing is tracking it
            self.grid_plot.remove_object(p)

        # Delete the curves, too
        while len(self._curves): self._curves.pop()
        while len(self._errors): self._errors.pop()

        # Create the new curves and errors
        for i in range(len(y)):

            # Default to the user-supplied self._styles, if they exist.
            if self._styles and i < len(self._styles) and self._styles[i]:
                kw = self._styles[i]
            else:
                kw = dict(pen=_pg.mkPen(color=(i,len(y)), width=_s.settings['egg_pen_width']))

            # Append the curve @JACK
            self._curves.append(_pg.PlotDataItem(**kw))
            if ey[i] is None:
                self._errors.append(None)
            else:
                self._errors.append(_pg.ErrorBarItem(
                    x=_n.array([0,1]), y=_n.array([0,0]),
                    pen=_pg.mkPen(color=(i,len(y)), width=_s.settings['egg_pen_width'])) )

        # figure out the target number of plots
        if self.button_multi.is_checked(): n_plots = len(y)        # one plot per data set
        else:                              n_plots = min(len(y),1) # 0 or 1 plot

        # add new plots
        for i in range(n_plots):
            self.plot_widgets.append(self.grid_plot.place_object(_pg.PlotWidget(), 0, i, alignment=0))

            # Legend for single plot mode.
            if self.button_multi.is_checked(): self._legend = None
            else:                              self._legend = self.plot_widgets[-1].addLegend()

        # loop over the curves and add them to the plots
        for i in range(len(y)):

            # Ceilinged plot_widget index (paranoid I suppose)
            l = min(i,len(self.plot_widgets)-1)

            # Always add a curve
            self.plot_widgets[l].addItem(self._curves[i])

            # Sometimes add an error bar
            if ey[i] is not None:
                self.plot_widgets[l].addItem(self._errors[i])

        # loop over the ROI's and add them
        if self.ROIs is not None:

            for i in range(len(self.ROIs)):

                # get the ROIs for this plot
                ROIs = self.ROIs[i]

                if not _s.fun.is_iterable(ROIs): ROIs = [ROIs]

                # loop over the ROIs for this plot
                for ROI in ROIs:

                    # determine which plot to add the ROI to
                    m = min(i, len(self.plot_widgets)-1)

                    # add the ROI to the appropriate plot
                    if m>=0 and not ROI == None: self.plot_widgets[m].addItem(ROI)

        # show the plots
        self.grid_plot.unblock_signals()


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


class DataboxProcessor(Window):
    """
    Object for performing common processes on data from a databox or DataboxPlot
    object (or any other source). Includes a GUI for taking power spectral
    densities, running averages, error bar estimates, and more.

    Parameters
    ----------
    name='processor'
        Unique identifier used for settings and stuff. This takes the place of
        autosettings_path because this object comprises several egg objects.
    databox_source
        Databox (or DataboxPlot) serving as the default source when calling
        self.run().
    margins=False
        Margins around the window's inside edges. Can be True, False, or a 4-length tuple.
    """

    def __init__(self, name='processor', databox_source=None, file_type='*.dp', margins=False):

        # Run the window init
        Window.__init__(self, 'Databox Processor', autosettings_path=name+'.window', margins=margins)
        self._alignment_default = 0 # By default, fill all space.

        # Store variables and create the window.
        self.name        = name
        self._clear_dump = False
        self.t0          = _t.time()

        # Remembers when user edits it
        self._histogram_script    = None
        self._prehistogram_script = None

        # Source databox for the "do it" button.
        self.databox_source = databox_source

        # Add the rows.
        self.grid_top = self.add(GridLayout(margins=False), alignment=1)
        self.new_autorow()
        self.grid_bottom = self.add(GridLayout(margins=False), alignment=0)

        # Top controls
        self.button_run   = self.grid_top.add(Button('Run', tip='Run the enabled processes on the specified source data.')).set_width(50)
        self.number_count = self.grid_top.add(NumberBox(int=True, tip='How many times this has run since last reset.'))
        self.button_reset = self.grid_top.add(Button('Reset', tip='Reset the run count.')).set_width(50)
        self.label_info   = self.grid_top.add(Label('')).set_colors('pink' if _s.settings['dark_theme_qt'] else 'red',None)
        self.label_dump   = self.grid_top.add(Label(''))

        # Add settings and plotter
        self.settings   = self.grid_bottom.add(TreeDictionary(name+'.settings', name), 0,0).set_width(210)
        self.plot       = self.grid_bottom.add(DataboxPlot(file_type, name+'.plot', name=name), 1,0, alignment=0)

        # Add the PSD settings
        self.settings.add_parameter('Enabled',      False, tip='Enable or disable all analyses below.')
        self.settings.add_parameter('Coarsen',          0, bounds=(0,None), tip='Break the data into groups of this many, and average each group into a single data point. 0 to disable.')

        self.settings.add_parameter('PSD',          False, tip='Calculate the power spectral density')
        self.settings.add_parameter('PSD/pow2',     False, tip='Truncate the data into the nearest 2^N data points, to speed up the PSD.')
        self.settings.add_parameter('PSD/Window',       1, values=['hanning', 'None'], default_list_index=1, tip='Apply this windowing function to the time domain prior to PSD.')
        self.settings.add_parameter('PSD/Rescale',  False, tip='Whether to rescale the PSD after windowing so that the integrated value is the RMS in the time-domain.')
        self.settings.add_parameter('PSD/Coarsen',      0, bounds=(0,None), tip='Break the PSD data into groups of this many, and average each group into a single data point. 0 to disable.')

        self.settings.add_parameter('Histogram',    False, tip='Perform a histogram on the data.')
        self.settings.add_parameter('Histogram/Bins', 100, bounds=(2,None), tip='How many bins to use for the histogram.')

        self.settings.add_parameter('Average',      False, tip='Calculate a running average of the data.')
        self.settings.add_parameter('Average/Frames',   0, step=2, tip='Exponential moving average time constant. Set to 0 to include all data in average.')
        self.settings.add_parameter('Average/Error',False, tip='Estimate the standard error on the mean (sent to column "<name>.std_mean")')
        self.settings.add_parameter('Stream',       False, tip='Stream some single quantity associated with the data.')
        self.settings.add_parameter('Stream/Method', 'mean', values=['max','min','mean','mean+e','std','hkeys'], tip='Method for converting source data into a single data point.')
        self.settings.add_parameter('Stream/hkeys',  '',   tip='Comma-separated list of hkeys used to stream header elements as well.')
        self.settings.add_parameter('Stream/History', 200, dec=True, bounds=(2, None), tip='How many points to keep in the stream.')
        self.settings.add_parameter('Stream/File_Dump',  False, tip='Enable to dump the whole stream to a file of your choice.')

        # Connect signals
        self.settings.connect_any_signal_changed(self._reset)
        self.settings.connect_signal_changed('Histogram', self._histogram_changed)

        self.settings.connect_signal_changed('Stream/File_Dump', self._stream_dump_changed)
        self.settings.connect_signal_changed('Stream', self._stream_changed)
        self.settings.connect_signal_changed('Stream/Method', self._stream_method_changed)
        self.button_run.signal_clicked.connect(self._button_run_clicked)
        self.plot.button_clear.signal_clicked.connect(self._reset)
        self.button_reset.signal_clicked.connect(self._button_reset_clicked)

        # After loading
        self.plot.after_load_file = self._after_load_file

        # Update the visibility of hkeys
        self._stream_method_changed()

    def _button_run_clicked(self, *a):
        self.run()

    def _button_reset_clicked(self, *a):
        """
        This one just resets the counter and kills the averagers, which doesn't
        affect the plot zoom.
        """
        self.number_count.set_value(0)
        self.plot.clear()
        self.plot.clear_averagers()

    def _reset(self, *a):

        # In stream mode, only the clear button should reset it.
        if not self.settings['Stream']:
            self.plot.clear()
            self.plot.clear_averagers()
            self.number_count.set_value(0)
            self.t0 = _t.time()

    def _histogram_changed(self, *a):
        """
        Sets up the plot for histograms.
        """
        if self.settings['Histogram']:

            # Remeber the previous script
            self._prehistogram_script = self.plot.script.get_text()

            # Set the script to edit and show it.
            self.plot.combo_autoscript.set_index(0)
            self.plot.button_script.set_checked(True)

            # Unlink the axes
            self.plot.button_link_x.set_checked(False)

            # Load the script or use the previous one
            if self._histogram_script is None:
                self.plot.load_script(_os.path.join(
                    _s.__path__[0], 'egg', 'DataboxProcessor',
                    'histogram_plot_script.py'))
            else:
                self.plot.script.set_text(self._histogram_script)

        # If we're unchecking
        else:
            # Remember this histogram script
            self._histogram_script = self.plot.script.get_text()

            # Input the previous one.
            if self._prehistogram_script is not None:
                self.plot.script.set_text(self._prehistogram_script)

    def _stream_changed(self, *a):
        if self.settings['Stream']: self.label_dump.enable()
        else:                       self.label_dump.disable()

    def _stream_method_changed(self, *a):
        """
        Toggles the visibility of hkeys
        """
        if self.settings['Stream/Method'] == 'hkeys':
            self.settings.show_parameter('Stream/hkeys')
        else:
            self.settings.hide_parameter('Stream/hkeys')

    def _stream_dump_changed(self, *a):
        """
        If enabled, bring up a dialog. If disabled, remove the dump file info.
        """
        if self.settings['Stream/File_Dump']:

            # Get the path
            path = _s.dialogs.save(
                    self.plot.file_type,
                    'Where should we dump the stream? (WILL DELETE!)',
                    force_extension=self.plot.file_type)

            # Cancel
            if not type(path) == str:
                self.settings['Stream/File_Dump'] = False
                return

            # Remember this is our first time
            self._clear_dump = True

            # Store the path
            self.label_dump.set_text('>>> '+path)

        else: self.label_dump.set_text('')

    def _after_load_file(self, d):
        """
        By default, this sends the header to the settings. You can overwrite
        this function to do your own thing.
        """
        self.settings.update(d.headers, ignore_errors=True)

    def run(self, d=None):
        """
        Performs the analysis on the data in the supplied (if enabled).

        Parameters
        ----------
        d=None
            If None, processes self.databox_source. Otherwise must be a databox.
            If self.databox_source is defined, d temporarily overrides this.
        """
        if not self.settings['Enabled']:
            self.label_info.set_text('(Disabled)')
            return self

        # Get the databox source as d for easy coding.
        if d == None: d = self.databox_source
        if d == None:
            self.label_info.set_text('No databox source to process.')
            return self

        # Reset the label.
        self.label_info.set_text('')

        # FIRST we do all the calculations, generating a list of ckeys and
        # arrays of data, without touching the original or plot data

        # Get the default list of ckeys
        ckeys = list(d.ckeys)

        # Coarsen. This also creates a copy of the array.
        cs = [] # Columns
        for n in range(len(d)): cs.append(_s.fun.coarsen_array(d[n], self.settings['Coarsen']))

        # If we have no columns, quit
        if len(cs) == 0:
            self.label_info.set_text('(no source data)')
            return self

        # Now perform the PSD
        if self.settings['PSD']:

            # Temporary storage for the power spectral densities (for coding ease)
            ps = []

            # Assume the 0th column is time.
            for n in range(1, len(cs)):
                f, p = _s.fun.psd(cs[0], cs[n],
                                  pow2    = self.settings['PSD/pow2'],
                                  window  = self.settings['PSD/Window'],
                                  rescale = self.settings['PSD/Rescale'])
                if n==1: ps.append(f)
                ps.append(p)

            # Coarsen & overwrite the previous result
            for n in range(len(ps)): cs[n] = _s.fun.coarsen_array(ps[n], self.settings['PSD/Coarsen'])

            # Update the ckeys, too!
            for n in range(len(ckeys)): ckeys[n] = 'P'+ckeys[n]


        # Histogram
        if self.settings['Histogram']:

            # For this we will histogram and then discard every column we
            # have created up to this point, creating a pair of columns for
            # each. This step is different, however, because we want the
            # bins to match any existing bins, to facilitate averaging.

            # Let's put together the ckeys first, then we can see if the
            # bin columns already exist in the plotter.

            # Loop over the existing ckeys and make a bin and counts version
            new_ckeys = []
            new_cs    = []
            for n in range(len(ckeys)):
                ckey = ckeys[n]
                c    = cs[n]

                # Create the new ckeys
                new_ckeys.append(ckey+'.values')
                new_ckeys.append(ckey+'.counts')

                # See if there already exists a .values column
                if ckey+'.values' in self.plot.ckeys:

                    # start with these (center) values
                    bins = _n.array(self.plot[ckey+'.values'])

                    # Shift by half a bin width to get the lower edges
                    dv = bins[1]-bins[0]
                    bins -= dv*0.5

                    # Add the extra upper bin edge
                    bins = _n.concatenate([bins, [bins[-1]+dv]])

                # Otherwise we define our own bins
                else: bins = self.settings['Histogram/Bins']

                # Do the histogram on the new data
                counts, bins = _n.histogram(c, bins)

                # Convert bins (currently edges) back to centers
                dv = bins[1]-bins[0]
                bins = (bins - 0.5*dv)[1:]
                new_cs.append(bins)
                new_cs.append(counts)

            # Overwrite the old data
            cs    = new_cs
            ckeys = new_ckeys

        # Now we have valid ckeys and column list cs

        # First transfer the header contents from the source databox
        self.plot.copy_headers(d)
        self.settings.send_to_databox_header(self.plot)

        # Streaming mode
        if self.settings['Stream']:

            # If we're dumping, make sure the file exists with the header
            if self.settings['Stream/File_Dump']:

                # Get the path
                path = self.label_dump.get_text()

                # If we don't yet have a path for some reason, cancel the dump
                if len(path) < 5: self.settings['Stream/File_Dump'] = False

                # Strip the '>>> '
                path = path[4:]

                # If the path does not already exist or we're supposed to clear it
                # create / overwrite it.
                if not _os.path.exists(path) or self._clear_dump:

                    # This will save all the header info + ckeys
                    self.plot.save_file(path, force_overwrite=True)

                    # Don't do this next time!
                    self._clear_dump = False

            # First column is time
            new_data  = [_t.time()-self.t0]

            # If we're doing an hkey stream
            if self.settings['Stream/Method'] == 'hkeys':

                # We build our own new ckeys because they're not related
                # to the old column ckeys
                ckeys = ['t']

                # Get the new data
                for hkey in self.settings['Stream/hkeys'].split(','):
                    ckeys.append(hkey.strip())
                    new_data.append(self.plot.h(hkey.strip()))

            # Some column operation stream method
            else:

                # We modify the old column ckeys
                # Prepend an S for "Stream"
                for n in range(len(ckeys)): ckeys[n] = 'S'+ckeys[n]

                # If we also want the standard error on the mean
                if self.settings['Stream/Method'] == 'mean+e':
                    for n in range(len(ckeys)):
                        ckeys.insert(2*n+1, ckeys[2*n]+'.std_mean')

                # Keep the iterator
                ckeys = ['t'] + ckeys

                # Standard methods that can be evaluated with numpy's dictionary
                if self.settings['Stream/Method'] in ['min','max','mean','std']:
                    for c in cs:
                        new_data.append(eval('_n.'+self.settings['Stream/Method']+'(c)', dict(_n=_n, c=c)))

                # Mean + standard error on the mean
                elif self.settings['Stream/Method'] == 'mean+e':
                    for c in cs:
                        new_data.append(_n.mean(c))
                        new_data.append(_n.std(c, ddof=1)/_n.sqrt(len(c)))

            # Now append this line to the plotter
            self.plot.append_row(new_data, ckeys)

            # If we're keeping fixed history
            history = self.settings['Stream/History']
            if history > 0:
                while(len(self.plot[0]))>history: self.plot.pop_row(0)

            # Now write it to the file if necessary
            if self.settings['Stream/File_Dump']:

                # Get the delimiter
                delimiter = self.plot.delimiter
                if delimiter == None: delimiter = '\t'

                # Assemble the line
                line = delimiter.join([str(x) for x in new_data])

                # Append
                f = open(path, 'a')
                f.write(line + '\n')
                f.close()

            # Increment the counter
            self.number_count.increment()

        # Non-streaming (update columns / averagers) mode.
        else:

            # Explicitly pop all the columns, but don't clear the averagers
            while len(self.plot): self.plot.pop_column(0)

            # Add the rest of the columns to the pool.
            for n in range(0, len(cs)):

                # If we're averaging.
                if self.settings['Average']:
                    self.plot.add_to_column_average(
                            ckeys[n], cs[n],
                            std_mean       = self.settings['Average/Error'],
                            lowpass_frames = self.settings['Average/Frames'],
                            precision      = _n.float64,
                            ignore_nan     = True)

                    # Update the counter on the last step (averagers are defined here)
                    if n==len(cs)-1: self.number_count.set_value(self.plot.averagers[ckeys[-1]].N)

                # Not averaging
                else:
                    self.plot[ckeys[n]] = cs[n]
                    self.number_count.set_value(0)

        # Now dump the updated counter value to the header
        self.plot.insert_header('/'+self.name+'/Count', self.number_count.get_value())

        # Plot it, process events
        self.plot.plot()
        self.process_events()

        # Do other stuff if the user wishes it.
        self.after_run()

        return self

    def after_run(self):
        """
        Dummy function you can overwrite. Executed after self.run().
        """
        return


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
            egg_settings/<some string>.
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
    import spinmob
    #runfile(spinmob.__path__[0] + '/tests/test__egg.py')
    
    w = Window()
    ts = w.add(TabArea())
    t = ts.add('test')
    p = t.add(DataboxPlot())
    
    w.show()







