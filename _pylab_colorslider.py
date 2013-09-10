#!/usr/bin/env python
#Boa:App:BoaApp

import wx
import matplotlib as _matplotlib
import pylab as _pylab
import _pylab_colorslider_frame as _pcf; reload(_pcf)

try:    _prefs
except: _prefs = None

modules ={u'pylab_colorslider_frame': [1,
                              'Main frame of Application',
                              u'pylab_colorslider_frame.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = _pcf.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()






#
# This class contains one color point and generates new slider gui's when it's time to modify
#
class ColorPoint:

    color    = None
    color2   = None
    position = 0.0
    min      = 0.0 # in case the user modifies this
    max      = 1.0 # in case the user modifies this
    parent   = None
    slider   = None

    def __init__(self, parent, position, red=0, green=0, blue=255, red2=0, green2=0, blue2=255):

        # just store the local variables
        self.parent   = parent
        self.color    = wx.Colour(red, green, blue)
        self.color2   = wx.Colour(red2,green2,blue2)
        self.position = position

        return

    def ShowSlider(self, position=[0,0]):
        """
        Creates a color slider GUI object, and pops it up. When the colorslider
        moves, this object's color data is updated.
        """

        # close/delete any old ones
        self.HideSlider()

        # find out if this is the "main" slider (that appears in the taskbar)
        n = None
        for i in range(len(self.parent.colorpoints)):
            if self == self.parent.colorpoints[i]: n=i

        # modify the style accordingly
        style = 0
        if not n==len(self.parent.colorpoints)-1:
            style  = wx.FRAME_NO_TASKBAR|wx.CLIP_CHILDREN|wx.FRAME_FLOAT_ON_PARENT|wx.NO_BORDER
            size   = wx.Size(351, 38)
            parent = self.parent.colorpoints[-1].slider # better make the last one first!
        else:
            style  = wx.CLIP_CHILDREN|wx.CAPTION|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.SYSTEM_MENU
            size   = wx.Size(351, 40+35*(len(self.parent.colorpoints)-1))
            parent = wx.GetApp().GetTopWindow()

        # convert the coords to a real position
        position = wx.Point(position[0], position[1])

        # create the GUI object
        self.slider = _pcf.ColorSliderFrame(parent, self, style=style, size=size, position=position)
        if n in [0, len(self.parent.colorpoints)-1]: self.slider.EnableStuff(False)
        self.slider.Show()


    def HideSlider(self):
        if self.slider:
            self.slider.Hide()
            self.slider.Destroy()
            self.slider = None



#
# This class contains a list of color points and a link to a parent image.
# Its job is to update the parent image colormap
#
class GuiColorMap:

    # define the local variables of the class
    colorpoints  = []
    image = None

    def __init__(self, image="top", colormap="_last"):
        """
        This class contains a list of color points defining a colormap. It is
        capable of providing GUI sliders to modify the colors and locations of
        the color points in the color map and updating the supplied image on
        the fly.

        To get the initial color from the supplied image, it assumes that
        the red, green, and blue channels have the same set of positions!

        To find the image, try gca().images[0]

        set colormap=None to try and import the current colormap
        """

        if image == "top":
            image = _pylab.gca().images[0]

        # store the reference to the image
        self.image = image

        # get the data for easier coding
        if colormap == None:
            # use the color map from the image if possible
            c = image.cmap._segmentdata
            cr = c['red']
            cg = c['green']
            cb = c['blue']

            # get the number of steps in this cmap
            N = len(cb)

            # loop over the number of entries and generate the list
            self.colorpoints = []

            # try to import the colormap from the image
            for n in range(N):
                if cr[n][0] == cb[n][0] and cr[n][0] == cg[n][0]:
                    self.colorpoints.append(ColorPoint(
                                 self, cr[n][0],
                                 cr[n][1]*255, cg[n][1]*255, cb[n][1]*255,
                                 cr[n][2]*255, cg[n][2]*255, cb[n][2]*255))
                else:
                    print "This colormap is too complicated. Switching to default."
                    colormap = "default"
                    break;

        # if we need to, use the default map
        if not colormap == None:
            self.LoadColorMap(colormap)


        # may as well show these guys to the user too
        self.ShowSliders()

    def LoadColorMap(self, name="default"):
        # open the file "[spinmobpath]/colormaps/whatever.txt"
        try:
            f = open(_prefs.colormaps_dir + _prefs.path_delimiter + name + ".txt", "r")
            lines = f.readlines()
            f.close()

            # now loop over the colors (lines) and generate a list
            self.colorpoints = []
            for line in lines:
                # split the line by white space
                s = line.split()

                # now create a new color point
                if len(s) == 7:
                    self.colorpoints.append(ColorPoint(self, float(s[0]),
                        float(s[1]), float(s[2]), float(s[3]),
                        float(s[4]), float(s[5]), float(s[6])))


        # use the hard-coded default
        except:
            print "Could not load "+_prefs.colormaps_dir + _prefs.path_delimiter + name + ".txt"
            self.colorpoints = [ColorPoint(self, 0.0, 255, 255, 255, 255, 255, 255),
                         ColorPoint(self, 0.5, 0,   0,   255, 0,   0,   255),
                         ColorPoint(self, 1.0, 255, 0,   0,   255, 0,   0)]

        # now update
        self.UpdateImage()

    def SaveColorMap(self, name="_last"):

        try:
            f = open(_prefs.colormaps_dir + _prefs.path_delimiter + name + ".txt", "w")

            # loop over the color points
            for c in self.colorpoints:
                f.write(str(c.position) + " " +
                    str(c.color.Red()) + " " + str(c.color.Green()) + " " + str(c.color.Blue()) + " " +
                    str(c.color2.Red())+ " " + str(c.color2.Green())+ " " + str(c.color2.Blue()) + "\n")

            f.close()

        except:
            print "Couldn't save last colormap!"

    def UpdateImage(self):
        """
        This takes the current values of the various color points, orders them,
        and updates the colormap of the parent image.
        """

        # first order the list according to the element positions
        new_list = []
        while len(self.colorpoints):

            # find the minimum position
            x0 = 2.0
            n0 = 0
            for n in range(len(self.colorpoints)):
                # if this item is smaller than the previous record, store it
                if self.colorpoints[n].position < x0:
                    x0 = self.colorpoints[n].position
                    n0 = n

                # if it's equal to the previous record, make it a little bigger
                # next time around, this can be the new minimum
                elif self.colorpoints[n].position == x0:
                    self.colorpoints[n].position = x0 + 0.0001

                    # if it's larger than 1, set it to 1 and knock off the best a little
                    if self.colorpoints[n].position > 1.0:
                        self.colorpoints[n].position = 1.0
                        self.colorpoints[n0].position = 1.0-0.0001

            # now we have the minimum index
            new_list.append(self.colorpoints.pop(n0))

        # now set the new list
        self.colorpoints = new_list

        # now generate the colormap from the ordered list
        r = []
        g = []
        b = []
        for point in self.colorpoints:
            r.append((point.position, point.color.Red()/255.0,   point.color2.Red()/255.0))
            g.append((point.position, point.color.Green()/255.0, point.color2.Green()/255.0))
            b.append((point.position, point.color.Blue()/255.0,  point.color2.Blue()/255.0))

        # store the formatted dictionary
        c = {'red':r, 'green':g, 'blue':b}

        # now set the dang thing
        self.image.set_cmap(_matplotlib.colors.LinearSegmentedColormap('custom', c))
        _pylab.draw()

        self.SaveColorMap()

    def ShowSliders(self):
        """
        This will show all the sliders, tiling them to the right of the figure
        """

        # loop over the points in the list
        for n in range(len(self.colorpoints)-1,-1,-1): self.ShowSlider(n, "auto")

    def HideSliders(self):
        for p in self.colorpoints: p.HideSlider()

    def ShowSlider(self, n, position="auto"):
        """
        This will show the n'th slider at the specified screen position
        """
        try:
            if position == "auto":
            # get the figure position and size
                p = self.image.figure.canvas.Parent.GetPosition()
                w = self.image.figure.canvas.Parent.GetSize()[0]
            
                if n==len(self.colorpoints)-1:
                    position = [p[0]+w, p[1]+40*(len(self.colorpoints)-n-1)]
                else:
                    position = [p[0]+w+3, p[1]+65+35*(len(self.colorpoints)-n-2)]
            
        except:
                print "Can't position slider relative to anything but a wxAgg plot."

        if not hasattr(position, '__iter__'): position = [0,0]
        
        self.colorpoints[n].ShowSlider(position)

        

    def HideSlider(self, n):
        self.colorpoints[n].HideSlider()
