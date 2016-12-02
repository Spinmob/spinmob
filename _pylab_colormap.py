import os                     as _os
import matplotlib             as _mpl
import pylab                  as _pylab
from functools import partial as _partial

try:    from . import _pylab_tweaks
except: import        _pylab_tweaks 


import spinmob as _s
_qtw    = _s._qtw
_qt     = _s._qt
_qtcore = _s._qtc



# make sure we have an application
if __name__ == '__main__':
    _qtapp = _qtcore.QCoreApplication.instance()

    if not _qtapp:
        print("_pylab_colormap.py: Creating QApplication")
        _qtapp = _qtw.QApplication(_os.sys.argv)

    from . import _settings
    _settings = _settings.settings()


class colormap():

    # Each element of the list contains the position on the colorbar,
    # and the bottom/top colors
    _colorpoint_list = [[0.0, [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]],
                        [0.5, [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
                        [1.0, [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]] ]

    # name of the colormap
    _name = "Last Used"

    # pylab image object
    _image=None

    def __init__(self, name="Last Used", image='auto'):
        """
        This object is responsible for loading and saving all the spinmob
        colormaps, and converting them to a cmap for pylab.
        """

        self.set_name(name)
        self.set_image(image)
        self.load_colormap()
        return

    def __repr__(self):
        s = "\n"+self.get_name()
        n = 0
        for x in self._colorpoint_list:
            s = s+"\n"+str(n)+": " + str(x[0])+" "+str(x[1])+" "+str(x[2])
            n += 1
        return s+"\n"

    def __getitem__(self, n): return self._colorpoint_list[n]

    def load_colormap(self, name=None):
        """
        Loads a colormap of the supplied name. None means used the internal
        name. (See self.get_name())
        """

        if name == None: name = self.get_name()
        if name == "" or not type(name)==str: return "Error: Bad name."

        # assemble the path to the colormap
        path = _os.path.join(_settings.path_home, "colormaps", name+".cmap")

        # make sure the file exists
        if not _os.path.exists(path):
            print("load_colormap(): Colormap '"+name+"' does not exist. Creating.")
            self.save_colormap(name)
            return

        # open the file and get the lines
        f = open(path, 'r')
        x = f.read()
        f.close()

        try:
            self._colorpoint_list = eval(x)
        except:
            print("Invalid colormap. Overwriting.")
            self.save_colormap()

        # update the image
        self.update_image()

        return self

    def save_colormap(self, name=None):
        """
        Saves the colormap with the specified name. None means use internal
        name. (See get_name())
        """
        if name == None: name = self.get_name()
        if name == "" or not type(name)==str: return "Error: invalid name."

        # get the colormaps directory
        colormaps = _os.path.join(_settings.path_home, 'colormaps')

        # make sure we have the colormaps directory
        _settings.MakeDir(colormaps)

        # assemble the path to the colormap
        path = _os.path.join(_settings.path_home, 'colormaps', name+".cmap")

        # open the file and overwrite
        f = open(path, 'w')
        f.write(str(self._colorpoint_list))
        f.close()

        return self

    def delete_colormap(self, name=None):
        """
        Deletes the colormap with the specified name. None means use the internal
        name (see get_name())
        """
        if name == None: name = self.get_name()
        if name == "" or not type(name)==str: return "Error: invalid name."

        # assemble the path to the colormap
        path = _os.path.join(_settings.path_home, 'colormaps', name+".cmap")
        _os.unlink(path)

        return self

    def set_name(self, name="My Colormap"):
        """
        Sets the name.

        Make sure the name is something your OS could name a file.
        """
        if not type(name)==str:
            print("set_name(): Name must be a string.")
            return
        self._name = name
        return self

    def get_name(self):
        """
        Returns the name of the current colormap.
        """
        return self._name

    def set_image(self, image='auto'):
        """
        Set which pylab image to tweak.
        """
        if image=="auto": image = _pylab.gca().images[0]
        self._image=image
        self.update_image()

    def update_image(self):
        """
        Set's the image's cmap.
        """
        if self._image:
            self._image.set_cmap(self.get_cmap())
            _pylab.draw()

    def pop_colorpoint(self, n=0):
        """
        Removes and returns the specified colorpoint. Will always leave two behind.
        """

        # make sure we have more than 2; otherwise don't pop it, just return it
        if len(self._colorpoint_list) > 2:

            # do the popping
            x = self._colorpoint_list.pop(n)

            # make sure the endpoints are 0 and 1
            self._colorpoint_list[0][0]  = 0.0
            self._colorpoint_list[-1][0] = 1.0

            # update the image
            self.update_image()

            return x

        # otherwise just return the indexed item
        else: return self[n]

    def insert_colorpoint(self, position=0.5, color1=[1.0,1.0,0.0], color2=[1.0,1.0,0.0]):
        """
        Inserts the specified color into the list.
        """
        L = self._colorpoint_list

        # if position = 0 or 1, push the end points inward
        if   position <= 0.0:
            L.insert(0,[0.0,color1,color2])

        elif position >= 1.0:
            L.append([1.0,color1,color2])

        # otherwise, find the position where it belongs
        else:

            # loop over all the points
            for n in range(len(self._colorpoint_list)):
                # check if it's less than the next one
                if position <= L[n+1][0]:
                    # found the place to insert it
                    L.insert(n+1,[position,color1,color2])
                    break

        # update the image with the new cmap
        self.update_image()

        return self

    def modify_colorpoint(self, n, position=0.5, color1=[1.0,1.0,1.0], color2=[1.0,1.0,1.0]):
        """
        Changes the values of an existing colorpoint, then updates the colormap.
        """
        if    n==0.0                         : position = 0.0
        elif  n==len(self._colorpoint_list)-1: position = 1.0
        else: position = max(self._colorpoint_list[n-1][0], position)

        self._colorpoint_list[n] = [position, color1, color2]
        self.update_image()
        self.save_colormap("Last Used")

    def get_cmap(self):
        """
        Generates a pylab cmap object from the colorpoint data.
        """

        # now generate the colormap from the ordered list
        r = []
        g = []
        b = []
        for p in self._colorpoint_list:
            r.append((p[0], p[1][0]*1.0, p[2][0]*1.0))
            g.append((p[0], p[1][1]*1.0, p[2][1]*1.0))
            b.append((p[0], p[1][2]*1.0, p[2][2]*1.0))

        # store the formatted dictionary
        c = {'red':r, 'green':g, 'blue':b}

        # now set the dang thing
        return _mpl.colors.LinearSegmentedColormap('custom', c)






class colormap_interface(colormap):

    def __init__(self, name="Last Used", image="auto"):
        """
        This is the graphical interface for interacting with a
        pylab image.
        """
        colormap.__init__(self,name,image)

        # create the main window
        self._window = _qtw.QMainWindow()
        self._window.setWindowTitle("Colormap")

        # main widget inside window
        self._central_widget = _qtw.QWidget()
        self._window.setCentralWidget(self._central_widget)

        # add all the controls
        self._build_gui()

        # disable the save (just loaded)
        self._button_save.setEnabled(False)

        # set the location
        pos, size = _pylab_tweaks.get_figure_window_geometry()
        self._window.move(pos[0]+size[0],pos[1])

        self.show()



    def _build_gui(self):
        """
        Removes all existing sliders and rebuilds them based on the colormap.
        """
        # remove all widgets (should destroy all children too)
        self._central_widget.deleteLater()

        # remove all references to other controls
        self._sliders               = []
        self._buttons_top_color     = []
        self._buttons_bottom_color  = []
        self._checkboxes            = []
        self._buttons_plus          = []
        self._buttons_minus         = []
        self._color_dialogs_top     = []
        self._color_dialogs_bottom  = []

        # create the new central widget
        self._central_widget = _qtw.QWidget()
        self._window.setCentralWidget(self._central_widget)

        # layout for main widget
        self._layout = _qtw.QGridLayout(self._central_widget)
        self._central_widget.setLayout(self._layout)

        # add the list of cmaps
        self._combobox_cmaps = _qtw.QComboBox(self._central_widget)
        self._combobox_cmaps.setEditable(True)
        self._load_cmap_list()

        # add the save and delete buttons
        self._button_save   = _qtw.QPushButton("Save",   self._central_widget)
        self._button_delete = _qtw.QPushButton("Delete", self._central_widget)
        self._button_save.setFixedWidth(70)
        self._button_delete.setFixedWidth(70)

        # layouts
        self._layout.addWidget(self._combobox_cmaps, 1,1, 1,3, _qtcore.Qt.Alignment(0))
        self._layout.addWidget(self._button_save,    1,5, 1,1, _qtcore.Qt.Alignment(1))
        self._layout.addWidget(self._button_delete,  1,6, 1,2, _qtcore.Qt.Alignment(1))

        # actions
        self._combobox_cmaps.currentIndexChanged.connect(self._signal_load)
        self._button_save  .clicked.connect(self._button_save_clicked)
        self._button_delete.clicked.connect(self._button_delete_clicked)

        # ensmallen the window
        self._window.resize(10,10)

        # now create a control set for each color point
        for n in range(len(self._colorpoint_list)):

            c1 = self._colorpoint_list[n][1]
            c2 = self._colorpoint_list[n][2]

            # create a top-color button
            self._buttons_top_color.append(_qtw.QPushButton(self._central_widget))
            self._buttons_top_color[-1].setStyleSheet("background-color: rgb("+str(int(c2[0]*255))+","+str(int(c2[1]*255))+","+str(int(c2[2]*255))+"); border-radius: 3px;")

            # create a bottom-color button
            self._buttons_bottom_color.append(_qtw.QPushButton(self._central_widget))
            self._buttons_bottom_color[-1].setStyleSheet("background-color: rgb("+str(int(c1[0]*255))+","+str(int(c1[1]*255))+","+str(int(c1[2]*255))+"); border-radius: 3px;")

            # create color dialogs
            self._color_dialogs_top.append(_qtw.QColorDialog(self._central_widget))
            self._color_dialogs_top[-1].setCurrentColor(self._buttons_top_color[-1].palette().color(1))

            self._color_dialogs_bottom.append(_qtw.QColorDialog(self._central_widget))
            self._color_dialogs_bottom[-1].setCurrentColor(self._buttons_top_color[-1].palette().color(1))

            # create link checkboxes
            self._checkboxes.append(_qtw.QCheckBox(self._central_widget))
            self._checkboxes[-1].setChecked(c1==c2)

            # create a slider
            self._sliders.append(_qtw.QSlider(self._central_widget))
            self._sliders[-1].setOrientation(_qtcore.Qt.Horizontal)
            self._sliders[-1].setMaximum(1000)
            self._sliders[-1].setValue(int(self._colorpoint_list[n][0]*1000))
            self._sliders[-1].setFixedWidth(250)

            # create + and - buttons
            self._buttons_plus.append(_qtw.QPushButton(self._central_widget))
            self._buttons_plus[-1].setText("+")
            self._buttons_plus[-1].setFixedWidth(25)

            self._buttons_minus.append(_qtw.QPushButton(self._central_widget))
            self._buttons_minus[-1].setText("-")
            self._buttons_minus[-1].setFixedWidth(25)

            # layout
            self._layout.addWidget(self._buttons_bottom_color[-1], n+3,1,      _qtcore.Qt.AlignCenter)
            self._layout.addWidget(self._checkboxes[-1],           n+3,2, 1,1, _qtcore.Qt.AlignCenter)
            self._layout.addWidget(self._buttons_top_color[-1],    n+3,3,      _qtcore.Qt.AlignCenter)
            self._layout.addWidget(self._sliders[-1],              n+3,4, 1,2, _qtcore.Qt.AlignCenter)
            self._layout.setColumnStretch(5,100)
            self._layout.addWidget(self._buttons_minus[-1],        n+3,7,      _qtcore.Qt.AlignCenter)
            self._layout.addWidget(self._buttons_plus[-1],         n+3,6,      _qtcore.Qt.AlignCenter)

            # connect the buttons and slider actions to the calls
            self._buttons_bottom_color[-1]            .clicked.connect(_partial(self._color_button_clicked, n, 0))
            self._buttons_top_color[-1]               .clicked.connect(_partial(self._color_button_clicked, n, 1))
            self._color_dialogs_bottom[-1].currentColorChanged.connect(_partial(self._color_dialog_changed, n, 0))
            self._color_dialogs_top[-1]   .currentColorChanged.connect(_partial(self._color_dialog_changed, n, 1))

            self._buttons_plus[-1]        .clicked.connect(_partial(self._button_plus_clicked,  n))
            self._buttons_minus[-1]       .clicked.connect(_partial(self._button_minus_clicked, n))
            self._sliders[-1]        .valueChanged.connect(_partial(self._slider_changed,   n))



        # disable the appropriate sliders
        self._sliders[0] .setDisabled(True)
        self._sliders[-1].setDisabled(True)


    def _signal_load(self):
        """
        Load the selected cmap.
        """

        # set our name
        self.set_name(str(self._combobox_cmaps.currentText()))

        # load the colormap
        self.load_colormap()

        # rebuild the interface
        self._build_gui()

        self._button_save.setEnabled(False)


    def _button_save_clicked(self):
        """
        Save the selected cmap.
        """
        self.set_name(str(self._combobox_cmaps.currentText()))
        self.save_colormap()
        self._button_save.setEnabled(False)
        self._load_cmap_list()

    def _button_delete_clicked(self):
        """
        Save the selected cmap.
        """
        name = str(self._combobox_cmaps.currentText())
        self.delete_colormap(name)
        self._combobox_cmaps.setEditText("")
        self._load_cmap_list()


    def _color_dialog_changed(self, n, top, c):
        """
        Updates the color of the slider.
        """
        self._button_save.setEnabled(True)

        cp = self._colorpoint_list[n]

        # if they're linked, set both
        if self._checkboxes[n].isChecked():
            self.modify_colorpoint(n, cp[0], [c.red()/255.0, c.green()/255.0, c.blue()/255.0],
                                             [c.red()/255.0, c.green()/255.0, c.blue()/255.0])
            self._buttons_top_color   [n].setStyleSheet("background-color: rgb("+str(c.red())+","+str(c.green())+","+str(c.green())+"); border-radius: 3px;")
            self._buttons_bottom_color[n].setStyleSheet("background-color: rgb("+str(c.red())+","+str(c.green())+","+str(c.green())+"); border-radius: 3px;")


        elif top:
            self.modify_colorpoint(n, cp[0], cp[1], [c.red()/255.0, c.green()/255.0, c.blue()/255.0])
            self._buttons_top_color   [n].setStyleSheet("background-color: rgb("+str(c.red())+","+str(c.green())+","+str(c.green())+"); border-radius: 3px;")

        else:
            self.modify_colorpoint(n, cp[0], [c.red()/255.0, c.green()/255.0, c.blue()/255.0], cp[2])
            self._buttons_bottom_color[n].setStyleSheet("background-color: rgb("+str(c.red())+","+str(c.green())+","+str(c.green())+"); border-radius: 3px;")



    def _button_plus_clicked(self, n):
        """
        Create a new colorpoint.
        """
        self._button_save.setEnabled(True)

        self.insert_colorpoint(self._colorpoint_list[n][0],
                               self._colorpoint_list[n][1],
                               self._colorpoint_list[n][2])
        self._build_gui()

    def _button_minus_clicked(self, n):
        """
        Remove a new colorpoint.
        """
        self._button_save.setEnabled(True)

        self.pop_colorpoint(n)
        self._build_gui()

    def _slider_changed(self, n):
        """
        updates the colormap / plot
        """
        self._button_save.setEnabled(True)

        self.modify_colorpoint(n, self._sliders[n].value()*0.001, self._colorpoint_list[n][1], self._colorpoint_list[n][2])


    def _color_button_clicked(self, n,top):
        """
        Opens the dialog.
        """
        self._button_save.setEnabled(True)

        if top: self._color_dialogs_top[n].open()
        else:   self._color_dialogs_bottom[n].open()


    def _load_cmap_list(self):
        """
        Searches the colormaps directory for all files, populates the list.
        """
        # store the current name
        name = self.get_name()

        # clear the list
        self._combobox_cmaps.blockSignals(True)
        self._combobox_cmaps.clear()

        # list the existing contents
        paths = _settings.ListDir('colormaps')

        # loop over the paths and add the names to the list
        for path in paths:
            self._combobox_cmaps.addItem(_os.path.splitext(path)[0])

        # try to select the current name
        self._combobox_cmaps.setCurrentIndex(self._combobox_cmaps.findText(name))
        self._combobox_cmaps.blockSignals(False)

    def close(self):
        """
        Closes the window.
        """
        self._window.close()
        #_qt.QtWidgets.qApp.processEvents()

    def show(self):
        """
        Shows the window.
        """
        self._window.show()
        #_qt.QtWidgets.qApp.processEvents()


######################
## Example Code
######################




