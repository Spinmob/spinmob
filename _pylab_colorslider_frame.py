#Boa:Frame:ColorSliderFrame
import _pylab_colorslider as _pc
import wx

from spinmob import _app

def create(parent):
    return ColorSliderFrame(parent)

[wxID_COLORSLIDERFRAME, wxID_COLORSLIDERFRAMEBUTTONCOLOR,
 wxID_COLORSLIDERFRAMEBUTTONCOLOR2, wxID_COLORSLIDERFRAMEBUTTONINSERT,
 wxID_COLORSLIDERFRAMEBUTTONKILL, wxID_COLORSLIDERFRAMECHECKBOXLOCKED,
 wxID_COLORSLIDERFRAMEPANEL1, wxID_COLORSLIDERFRAMESLIDERPOSITION,
 wxID_COLORSLIDERFRAMETEXTLOWERBOUND, wxID_COLORSLIDERFRAMETEXTUPPERBOUND,
] = [wx.NewId() for _init_ctrls in range(10)]

[wxID_COLORSLIDERFRAMETIMERUPDATE] = [wx.NewId() for _init_utils in range(1)]

class ColorSliderFrame(wx.Frame):
    # This thing's purpose is to pop into creation when the parent color line
    # object needs gui modification, get modified, and then get destroyed once
    # things are edited to the user's liking

    dialog  = wx.ColourDialog(_app.GetTopWindow())
    dialog2 = wx.ColourDialog(_app.GetTopWindow())
    daddy   = None

    def _init_utils(self):
        # generated method, don't edit
        self.timerUpdate = wx.Timer(id=wxID_COLORSLIDERFRAMETIMERUPDATE,
              owner=self)
        self.timerUpdate.SetEvtHandlerEnabled(False)
        self.Bind(wx.EVT_TIMER, self.OnTimerUpdateTimer,
              id=wxID_COLORSLIDERFRAMETIMERUPDATE)

    def _init_ctrls(self, prnt, style=0,size=wx.Size(351, 38),position=wx.Point(0,0)):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_COLORSLIDERFRAME,
              name=u'ColorSliderFrame', parent=prnt, pos=position,
              size=size, style=style,
              title=u'Color Slider')
        self._init_utils()
        self.SetClientSize(size)
        self.Bind(wx.EVT_CLOSE, self.OnColorSliderFrameClose)
        self.Bind(wx.EVT_LEFT_UP, self.OnColorSliderFrameLeftUp)
        self.Bind(wx.EVT_MOVE, self.OnColorSliderFrameMove)
        self.Bind(wx.EVT_ICONIZE, self.OnColorSliderFrameLower)

        self.panel1 = wx.Panel(id=wxID_COLORSLIDERFRAMEPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(351, 38),
              style=wx.TAB_TRAVERSAL)

        self.buttonColor = wx.Button(id=wxID_COLORSLIDERFRAMEBUTTONCOLOR,
              label=u'', name=u'buttonColor', parent=self.panel1,
              pos=wx.Point(8, 8), size=wx.Size(24, 23), style=0)
        self.buttonColor.Bind(wx.EVT_BUTTON, self.OnButtonColorButton,
              id=wxID_COLORSLIDERFRAMEBUTTONCOLOR)

        self.sliderPosition = wx.Slider(id=wxID_COLORSLIDERFRAMESLIDERPOSITION,
              maxValue=1000, minValue=0, name=u'sliderPosition',
              parent=self.panel1, pos=wx.Point(128, 8), size=wx.Size(128, 24),
              style=wx.SL_HORIZONTAL, value=500)
        self.sliderPosition.SetLabel(u'')
        self.sliderPosition.SetToolTipString(u'sliderPosition')
        self.sliderPosition.Bind(wx.EVT_COMMAND_SCROLL,
              self.OnSliderPositionCommandScroll,
              id=wxID_COLORSLIDERFRAMESLIDERPOSITION)
        self.sliderPosition.Bind(wx.EVT_LEFT_DOWN,
              self.OnSliderPositionLeftDown)
        self.sliderPosition.Bind(wx.EVT_LEFT_UP, self.OnSliderPositionLeftUp)

        self.textLowerBound = wx.TextCtrl(id=wxID_COLORSLIDERFRAMETEXTLOWERBOUND,
              name=u'textLowerBound', parent=self.panel1, pos=wx.Point(94, 8),
              size=wx.Size(34, 22), style=wx.PROCESS_ENTER, value=u'0.0')
        self.textLowerBound.SetHelpText(u'')
        self.textLowerBound.SetInsertionPoint(0)
        self.textLowerBound.Bind(wx.EVT_TEXT_ENTER,
              self.OnTextLowerBoundTextEnter,
              id=wxID_COLORSLIDERFRAMETEXTLOWERBOUND)

        self.textUpperBound = wx.TextCtrl(id=wxID_COLORSLIDERFRAMETEXTUPPERBOUND,
              name=u'textUpperBound', parent=self.panel1, pos=wx.Point(256, 8),
              size=wx.Size(32, 22), style=wx.PROCESS_ENTER, value=u'1.0')
        self.textUpperBound.Bind(wx.EVT_TEXT_ENTER,
              self.OnTextUpperBoundTextEnter,
              id=wxID_COLORSLIDERFRAMETEXTUPPERBOUND)

        self.buttonColor2 = wx.Button(id=wxID_COLORSLIDERFRAMEBUTTONCOLOR2,
              label='', name='buttonColor2', parent=self.panel1,
              pos=wx.Point(32, 8), size=wx.Size(24, 23), style=0)
        self.buttonColor2.Bind(wx.EVT_BUTTON, self.OnButtonColor2Button,
              id=wxID_COLORSLIDERFRAMEBUTTONCOLOR2)

        self.checkBoxLocked = wx.CheckBox(id=wxID_COLORSLIDERFRAMECHECKBOXLOCKED,
              label='lock', name='checkBoxLocked', parent=self.panel1,
              pos=wx.Point(56, 13), size=wx.Size(34, 13), style=0)
        self.checkBoxLocked.SetValue(True)
        self.checkBoxLocked.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxLockedCheckbox,
              id=wxID_COLORSLIDERFRAMECHECKBOXLOCKED)

        self.buttonKill = wx.Button(id=wxID_COLORSLIDERFRAMEBUTTONKILL,
              label='-', name='buttonKill', parent=self.panel1,
              pos=wx.Point(320, 8), size=wx.Size(24, 23), style=0)
        self.buttonKill.Bind(wx.EVT_BUTTON, self.OnButtonKillButton,
              id=wxID_COLORSLIDERFRAMEBUTTONKILL)

        self.buttonInsert = wx.Button(id=wxID_COLORSLIDERFRAMEBUTTONINSERT,
              label='+', name='buttonInsert', parent=self.panel1,
              pos=wx.Point(296, 8), size=wx.Size(24, 23), style=0)
        self.buttonInsert.Bind(wx.EVT_BUTTON, self.OnButtonInsertButton,
              id=wxID_COLORSLIDERFRAMEBUTTONINSERT)

    def __init__(self, parent_window, parent_ColorPoint, style=0, size=wx.Size(359, 72), position=wx.Point(0,0)):
        #wx.Frame.__init__(self, parent_window, style=wx.FRAME_NO_TASKBAR|wx.DEFAULT_FRAME_STYLE)

        # This is something that wx needs to do. Don't mess with it.
        self._init_ctrls(prnt=parent_window, style=style, size=size, position=position)

        # Set the variables and mess with the controls
        self.daddy     = parent_ColorPoint

        # should we skip an event?
        self.shhhh = 0

        # update the controls based on these new values
        self.UpdateControls()



#
# EVENTS AND FUNCTIONS
#
    def CheckIfEndPoint(self):
        # just look at where we are in the list
        if self.FindSelf() == 0 or self.FindSelf() == len(self.daddy.parent.colorpoints)-1:
            self.EnableStuff(False)
        else:
            self.EnableStuff(True)

    def EnableStuff(self, enable):
        self.buttonKill.Enable(enable)
        self.textLowerBound.Show(enable)
        self.textUpperBound.Show(enable)
        self.sliderPosition.Show(enable)


    def OnSliderPositionCommandScroll(self, event):
        # store the 0-1 position
        self.daddy.position = self.GetSliderPosition()

        # now update the graph!
        self.daddy.parent.UpdateImage()
        # let the mouse timer update the image

        self.CheckIfEndPoint()


    def OnButtonColorButton(self, event):
        #self.timerUpdate.Stop()

        # pop up the color dialog
        self.dialog.ShowModal()

        # update the data variables
        self.daddy.color = self.dialog.ColourData.GetColour()
        if self.checkBoxLocked.GetValue():
            self.daddy.color2 = self.daddy.color
            self.dialog2.ColourData.SetColour(self.daddy.color)

        # update the gui
        self.daddy.parent.UpdateImage()
        self.UpdateControls()

    def OnButtonColor2Button(self, event):
        #self.timerUpdate.Stop()

        # pop up the color dialog
        self.dialog2.ShowModal()

        # update the data variables
        self.daddy.color2 = self.dialog2.ColourData.GetColour()
        if self.checkBoxLocked.GetValue():
            self.daddy.color = self.daddy.color2
            self.dialog.ColourData.SetColour(self.daddy.color2)

        # update the gui
        self.daddy.parent.UpdateImage()
        self.UpdateControls()

    def OnCheckBoxLockedCheckbox(self, event):
        #self.timerUpdate.Stop()

        # set colors to uniform
        if self.checkBoxLocked.GetValue():
            self.daddy.color2 = self.daddy.color
            self.dialog2.ColourData.SetColour(self.daddy.color)

            self.daddy.parent.UpdateImage()
            self.UpdateControls()





    def OnTextLowerBoundTextEnter(self, event):
        #self.timerUpdate.Stop()

        # try to update our lower bound value
        self.daddy.min = self.SafeFloat(self.daddy.min, self.textLowerBound.GetValue(), 0.0, self.daddy.max-0.001)
        self.textLowerBound.SetValue(str(self.daddy.min))
        self.UpdateControls()

    def OnTextUpperBoundTextEnter(self, event):
        #self.timerUpdate.Stop()

        # try to update our max value
        self.daddy.max = self.SafeFloat(self.daddy.max, self.textUpperBound.GetValue(), self.daddy.min+0.001, 1.0)
        self.textUpperBound.SetValue(str(self.daddy.max))
        self.UpdateControls()

    def UpdateControls(self):
        # set the controls based on internal variables
        self.buttonColor.SetBackgroundColour(self.daddy.color)
        self.buttonColor2.SetBackgroundColour(self.daddy.color2)

        self.textLowerBound.SetValue(str(self.daddy.min))
        self.textUpperBound.SetValue(str(self.daddy.max))

        self.SetSliderPosition(self.daddy.position)

        # if we're the end points, gray out the delete button
        self.CheckIfEndPoint()





    def GetSliderPosition(self):
        x0 = self.sliderPosition.GetMin()
        x1 = self.sliderPosition.GetMax()

        return 1.0*(self.sliderPosition.GetValue()-x0)/(x1-x0)*(self.daddy.max-self.daddy.min)+self.daddy.min

    def SetSliderPosition(self, position):
        x0 = self.sliderPosition.GetMin()
        x1 = self.sliderPosition.GetMax()
        self.sliderPosition.SetValue((position-self.daddy.min)/(self.daddy.max-self.daddy.min)*(x1-x0)+x0)


    def SafeFloat(self, old_float, new_value, min=0.0, max=1.0):
        """
        This is for modifying min, max or the value. It makes sure new_value (string or float)
        is a valid float between min and max
        """

        try:
            x = float(new_value)
            if x <= max and x >= min: return x
            else:                     return old_float
        except:
            return old_float

    def OnButtonKillButton(self, event):
        #self.timerUpdate.Stop()

        # don't delete the end points!
        if self.daddy.position in [0.0,1.0]:
            return

        self.Hide()

        # remove this guy from the list
        self.daddy.parent.colorpoints.pop(self.FindSelf())

        # now redraw everything
        self.daddy.parent.ShowSliders()
        self.daddy.parent.UpdateImage()

    def FindSelf(self):
        #self.timerUpdate.Stop()

        # loop over the boss's list and pop this one out
        for n in range(len(self.daddy.parent.colorpoints)):
            if self.daddy.parent.colorpoints[n].slider == self:
                return n

    def OnButtonInsertButton(self, event):
        #self.timerUpdate.Stop()

        # insert a new color point in before this one
        self.daddy.parent.colorpoints.insert(self.FindSelf(),
            _pc.ColorPoint(self.daddy.parent, self.daddy.position,
                self.daddy.color.Red(),
                self.daddy.color.Green(),
                self.daddy.color.Blue(),
                self.daddy.color2.Red(),
                self.daddy.color2.Green(),
                self.daddy.color2.Blue()))

        # now redraw everything
        self.daddy.parent.ShowSliders()
        self.daddy.parent.UpdateImage()

    def OnColorSliderFrameClose(self, event):
        #self.timerUpdate.Stop()

        # close all the slider windows
        self.daddy.parent.HideSliders()

    def OnSliderPositionLeftDown(self, event):
        #self.timerUpdate.Start(1000)
        event.Skip()


    def OnSliderPositionLeftUp(self, event):
        #self.timerUpdate.Stop()
        #self.daddy.parent.ShowSliders()
        event.Skip()

    def OnTimerUpdateTimer(self, event):
        self.daddy.parent.UpdateImage()

    def OnColorSliderFrameLeftUp(self, event):
        # now redraw everything
        #self.daddy.parent.ShowSliders()
        event.Skip()

    def OnColorSliderFrameMove(self, event):
        # if we're supposed to skip this event or we're NOT the boss slider
        if not self.FindSelf() == len(self.daddy.parent.colorpoints)-1:
            return

        # get the list of windows
        l = self.daddy.parent.colorpoints

        # get the coordinates of this one
        x = self.Position.x
        y = self.Position.y

        # windows minimizing means "move the window way negative off screen"
        if x < -31000 or y < -31000: return

        # find out which one we are in the list
        n = self.FindSelf()

        # if we didn't find one, better quit!
        if n==None:
            print "couldn't find this window in list"
            event.Skip()

        # set the positions of all the other frames
        # the only frame that does the moving is the last one
        for i in range(len(l)-1):
            # only update coordinates of guys that aren't us
            # only mess with it if the colorpoint has made a slider
            if l[i].slider:
                l[i].slider.SetPosition([x+3,y+65+35*(len(l)-i-2)])


    def OnColorSliderFrameLower(self, event):
        if self.shhhh:
            self.shhhh=self.shhhh-1
            event.Skip()

        # figure out our current state
        i = self.IsIconized()

        # iconize everything
        for guy in self.daddy.parent.colorpoints:
            if not guy.slider == self:
                guy.slider.Show(not i)







