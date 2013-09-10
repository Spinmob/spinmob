#!/usr/bin/env python
#Boa:App:BoaApp

import wx
import pylab
import numpy
import pylab_helper_frame

modules ={'pylab_helper_frame': [1,
                             'Main frame of Application',
                             'pylab_helper_frame.py']}

class BoaApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.main = pylab_helper_frame.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    pylab.plot([1,2,1,2,1,2])
    pylab.figure()
    pylab.plot([1,2,1,3,1,4])
    pylab.plot([2,1,2,1,2,1])
    application = BoaApp(0)
    application.MainLoop()

def gui():
    wx.InitAllImageHandlers()
    a = wx.GetApp()
    a.main = pylab_helper_frame.create(None)
    a.main.Show()
    a.SetTopWindow(a.main)
    return a
    
    #return(BoaApp(0))
    
if __name__ == '__main__':
    main()
