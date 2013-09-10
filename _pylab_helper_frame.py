#Boa:Frame:FrameMain

import time
import wx
from wx.lib.anchors import LayoutAnchors
import matplotlib
from matplotlib import pylab
from pylab_helper_standalones import *

def create(parent):
    return FrameMain(parent)

[wxID_FRAMEMAIN, wxID_FRAMEMAINBUTTONAPPLY, wxID_FRAMEMAINBUTTONAPPLYALL, 
 wxID_FRAMEMAINBUTTONAUTOSCALE, wxID_FRAMEMAINBUTTONTIDY, 
 wxID_FRAMEMAINTEXTCTRLVALUE, wxID_FRAMEMAINTREECTRLMAIN, 
] = [wx.NewId() for _init_ctrls in range(7)]

class FrameMain(wx.Frame):
        
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAMEMAIN, name='FrameMain',
              parent=prnt, pos=wx.Point(639, 0), size=wx.Size(385, 424),
              style=wx.DEFAULT_FRAME_STYLE, title='Fancy Pantsy')
        self.SetClientSize(wx.Size(377, 390))
        self.SetBackgroundStyle(wx.BG_STYLE_COLOUR)
        self.SetBackgroundColour(wx.Colour(222, 222, 240))

        self.TreeCtrlMain = wx.TreeCtrl(id=wxID_FRAMEMAINTREECTRLMAIN,
              name='TreeCtrlMain', parent=self, pos=wx.Point(8, 8),
              size=wx.Size(360, 296), style=wx.TR_SINGLE | wx.TR_HAS_BUTTONS)
        self.TreeCtrlMain.SetSpacing(8)
        self.TreeCtrlMain.Bind(wx.EVT_TREE_SEL_CHANGED,
              self.OnTreeCtrlMainSelChanged, id=wxID_FRAMEMAINTREECTRLMAIN)

        self.TextCtrlValue = wx.TextCtrl(id=wxID_FRAMEMAINTEXTCTRLVALUE,
              name='TextCtrlValue', parent=self, pos=wx.Point(8, 308),
              size=wx.Size(260, 48), style=wx.TE_LINEWRAP | wx.TE_MULTILINE,
              value='')
        self.TextCtrlValue.Bind(wx.EVT_TEXT_ENTER, self.OnButtonApplyButton,
              id=wxID_FRAMEMAINTEXTCTRLVALUE)

        self.ButtonApply = wx.Button(id=wxID_FRAMEMAINBUTTONAPPLY,
              label='Apply', name='ButtonApply', parent=self, pos=wx.Point(272,
              308), size=wx.Size(96, 23), style=0)
        self.ButtonApply.Bind(wx.EVT_BUTTON, self.OnButtonApplyButton,
              id=wxID_FRAMEMAINBUTTONAPPLY)

        self.ButtonTidy = wx.Button(id=wxID_FRAMEMAINBUTTONTIDY,
              label='\xdcbertidy', name='ButtonTidy', parent=self,
              pos=wx.Point(104, 360), size=wx.Size(96, 23), style=0)
        self.ButtonTidy.Bind(wx.EVT_BUTTON, self.OnButtonTidyButton,
              id=wxID_FRAMEMAINBUTTONTIDY)

        self.ButtonApplyAll = wx.Button(id=wxID_FRAMEMAINBUTTONAPPLYALL,
              label='Apply All', name='ButtonApplyAll', parent=self,
              pos=wx.Point(272, 332), size=wx.Size(96, 23), style=0)
        self.ButtonApplyAll.Enable(False)
        self.ButtonApplyAll.Bind(wx.EVT_BUTTON, self.OnButtonApplyAllButton,
              id=wxID_FRAMEMAINBUTTONAPPLYALL)

        self.ButtonAutoscale = wx.Button(id=wxID_FRAMEMAINBUTTONAUTOSCALE,
              label='Autoscale', name='ButtonAutoscale', parent=self,
              pos=wx.Point(8, 360), size=wx.Size(96, 23), style=0)
        self.ButtonAutoscale.SetToolTipString('Autoscale')
        self.ButtonAutoscale.Bind(wx.EVT_BUTTON, self.OnButtonAutoscaleButton,
              id=wxID_FRAMEMAINBUTTONAUTOSCALE)

    def __init__(self, parent):
        self._init_ctrls(parent)
        
        # T is used a lot
        T  = self.TreeCtrlMain
 
        # here is where we make the root of the tree
        self.tree_root = T.AddRoot("Current Session")
        
        
        # here is where we define the line attributes
        self.line_attributes = ["linestyle", "linewidth", "color", "marker", \
                                "markersize", "markerfacecolor",             \
                                "markeredgewidth", "markeredgecolor"]
                
        # now fill the tree
        self.FillTree()
        T.SelectItem(self.tree_root)
    
        
     
    ########################
    # Standalone functions #
    ########################        
    
    # This is the MEAT function.
    # given the current wx session, this function
    # finds all the axes/lines/attributes and fills up
    # the main tree.
    def FillTree(self):
        # For ease of coding
        T = self.TreeCtrlMain
        
        # starting from the top, grab ALL the wx windows available
        w = wx.GetTopLevelWindows()
        
        # find all the windows that are plot windows for wxagg
        self.plot_windows = []
        for x in w:
            if type(x) == matplotlib.backends.backend_wxagg.FigureFrameWxAgg:
                self.plot_windows.append(x)
        
        # get all the figures associated with these windows
        self.figures = []
        for x in self.plot_windows:
            self.figures.append(x.canvas.figure)
            
        # all items in the tree must have data associated with it 
        # we use a dictionary of important values for ease of coding
        # children, parents and selfs are all tree ID's
        T.SetItemData(self.tree_root, 
          wx.TreeItemData({"string":"Current Session", 
                           "type":"tree_root_title", 
                           "self":self.tree_root, 
                           "parent":None, 
                           "children":[],
                           "window":None,
                           "figure":None,
                           "axes":None,
                           "line":None}))
        
        # fill the tree items!
        
        # kill all the root's children
        T.DeleteChildren(self.tree_root)
        
        # now loop over the figures and add a branch for each
        for nf in range(0,len(self.figures)):
            f = self.figures[nf]
            w = self.plot_windows[nf]
            
            # add the tree item corresponding to the figure
            cf_title = self.plot_windows[nf].GetTitle()
            cf = T.AppendItem(self.tree_root, cf_title)
            
            # we need to append this to the children array in the root
            self.AppendTreeItemData(self.tree_root, "children", cf)
            
            # we also need to set the tree item data for this item
            T.SetItemData(cf, 
              wx.TreeItemData({"string":cf_title, 
                               "type":"figure_title", 
                               "self":cf, 
                               "parent":self.tree_root, 
                               "children":[],
                               "window":w,
                               "figure":f,
                               "axes":None,
                               "line":None}))
            
            # now loop over the axes
            for na in range(0,len(f.axes)):
                a = f.axes[na]
                                
                # add the axes tree item to the figure item
                ca_title = "axes "+str(na)
                ca = T.AppendItem(cf, ca_title)
                
                # now append this id to the children array of the figure
                self.AppendTreeItemData(cf, "children", ca)
            
                # we also need to set the tree item data for this item
                T.SetItemData(ca, 
                  wx.TreeItemData({"string":ca_title, 
                                   "type":"axes_tree_label", 
                                   "self":ca, 
                                   "parent":cf, 
                                   "children":[],
                                   "window":w,
                                   "figure":f,
                                   "axes":a,
                                   "line":None}))
                                
                # add the "axes title" item to the tree and axes children list
                p = T.AppendItem(ca, "Axes Title")
                self.AppendTreeItemData(ca, "children", p)
                T.SetItemData(p, 
                    wx.TreeItemData({"string":a.title.get_text(),
                                     "type":"axes_title", 
                                     "self":p, 
                                     "parent":ca, 
                                     "children":[],
                                     "window":w,
                                     "figure":f,
                                     "axes":a,
                                     "line":None}))
                
                # add the "y-scale" item to the tree and axes children list
                p = T.AppendItem(ca, "y-scaling = 1.0")
                self.AppendTreeItemData(ca, "children", p)
                T.SetItemData(p, 
                    wx.TreeItemData({"type":"y_scale", 
                                     "string":"1.0",
                                     "last_value":1.0,
                                     "self":p, 
                                     "parent":ca, 
                                     "children":[],
                                     "window":w,
                                     "figure":f,
                                     "axes":a,
                                     "line":None}))
                
                
                
                # now loop over the lines
                lines = a.get_lines()
                for nl in range(0,len(lines)):
                    l = lines[nl]
                    
                    # add the axes tree item to the figure item
                    cl_title = "line "+str(nl)
                    cl = T.AppendItem(ca, cl_title)
                    
                    # now append this id to the children array of the figure
                    self.AppendTreeItemData(ca, "children", cl)
                
                    # we also need to set the tree item data for this item
                    T.SetItemData(cl, 
                      wx.TreeItemData({"string":cl_title, 
                                       "type":"line_title", 
                                       "self":cl, 
                                       "parent":ca, 
                                       "children":[],
                                       "window":w,
                                       "figure":f,
                                       "axes":a,
                                       "line":l}))
                
                    # now we set the individual line attributes
                    for x in self.line_attributes:
                        # make the tree branch
                        y = T.AppendItem(cl, x+": '"+str(pylab.getp(l,x))+"'")
                        
                        self.AppendTreeItemData(cl, "children", y)
                        
                        T.SetItemData(y,
                          wx.TreeItemData({"string": str(pylab.getp(l,x)),
                                           "type":x,
                                           "self":y,
                                           "parent":cl,
                                           "children":[],
                                           "window":w,
                                           "figure":f,
                                           "axes":a,
                                           "line":l}))
        
        # now expand the bitch
        T.Expand(self.tree_root)
        
    


    def GetTreeItemData(self, id, key):
        return(self.TreeCtrlMain.GetItemData(id).GetData()[key])

    def SetTreeItemData(self, id, key, new_value):
        T = self.TreeCtrlMain
        data = T.GetItemData(id).GetData()
        data[key] = new_value
        T.SetItemData(id, wx.TreeItemData(data))


    def AppendTreeItemData(self, id, key, new_value):
        # store in a temp variable
        T = self.TreeCtrlMain
        
        # get the data from the tree item id
        data = T.GetItemData(id).GetData()
        
        # set the key/value pair
        data[key].append(new_value)
        
        # update the tree item data
        T.SetItemData(id, wx.TreeItemData(data))
        
        return
     

    def SetYScale(self, id, new_string):
        T = self.TreeCtrlMain
        
        # get the axes associated with this, and the previous value
        a         = self.GetTreeItemData(id, "axes")
        old_scale = self.GetTreeItemData(id, "last_value")
               
        try:    scale     = float(new_string)
        except: return
         
        # get all the lines associated with the axes
        lines = a.get_lines()
        
        # for each line, scale the ydata
        for l in lines:
            y = l.get_ydata()
            for n in range(0,len(y)):
                y[n] = y[n]*scale/old_scale
            l.set_ydata(y)
        
        # update the tree
        T.SetItemText(id, "y-scaling = "+new_string)
        
        # update the old value
        self.SetTreeItemData(id, "last_value", scale)
        
        # now autoscale to the data + 3% margins
        self.OnButtonAutoscaleButton(None)
    
    


    def SetAttribute(self, id, new_string):
        T = self.TreeCtrlMain
        
        # get the attribute type from the tree id data
        type   = self.GetTreeItemData(id, "type")
        line   = self.GetTreeItemData(id, "line")
        axes   = self.GetTreeItemData(id, "axes")
        figure = self.GetTreeItemData(id, "figure")
        window = self.GetTreeItemData(id, "window")
        
        # if it's just a title, all we update is the tree (not the plot)
        if type == "tree_root_title": T.SetItemText(id, new_string)
        
        elif type == "figure_title":
            T.SetItemText(id, new_string)
            window.SetTitle(new_string)
 
        elif type == "axes_tree_label":
            T.SetItemText(id, new_string)
        
        elif type == "axes_title":
            axes.title.set_text(new_string)
        
        elif type == "y_scale":
            self.SetYScale(id, new_string)    
        
        elif type == "line_title":
            T.SetItemText(id, new_string)  
    
           
        # if it's a line attribute
        elif type in self.line_attributes and not line == None:
            # update the title string
            formatted = type+": '"+new_string+"'"
            T.SetItemText(id, formatted)    
            
            # also edit the attribute
            if is_a_number(new_string): 
                pylab.setp(line, type, float(new_string))
            else:
                pylab.setp(line, type, new_string)

        figure.canvas.Refresh()




    def FindChildType(self, selection, type):
        # this looks for a child with of specified type
        # in the specified selection
        
        children = self.GetTreeItemData(selection, "children")
        
        # loop over the children
        for c in children:
            if self.GetTreeItemData(c,"type") == type:
                return c
        
        return None



    
    
    ##########
    # Events #
    ##########
    
    def OnButtonTidyButton(self, event):
        
        # for easy coding
        T = self.TreeCtrlMain
        s = T.GetSelection()
        f = self.GetTreeItemData(s, "figure") 
        w = self.GetTreeItemData(s, "window")
        
        # set the current figure
        pylab.figure(f.number)
        
        # first set the size of the window
        w.SetSize([500,500])
        
        # now loop over all the data and get the range
        lines = f.axes[0].get_lines()
        
        # we want thick lines
        f.axes[0].get_frame().set_linewidth(3.0)

        # get the tick lines in one big list
        xticklines = f.axes[0].get_xticklines()
        yticklines = f.axes[0].get_yticklines()
        
        # set their marker edge width
        pylab.setp(xticklines+yticklines, mew=2.0)
        
        # set what kind of tickline they are (outside axes)
        for l in xticklines: l.set_marker(matplotlib.lines.TICKDOWN)
        for l in yticklines: l.set_marker(matplotlib.lines.TICKLEFT)
        
        # get rid of the top and right ticks
        f.axes[0].xaxis.tick_bottom()
        f.axes[0].yaxis.tick_left()
        
        # we want bold fonts
        pylab.xticks(fontsize=20, fontweight='bold', fontname='Arial')
        pylab.yticks(fontsize=20, fontweight='bold', fontname='Arial')

        # we want to give the labels some breathing room (1% of the data range)
        for label in pylab.xticks()[1]:
            label.set_y(-0.02)
        for label in pylab.yticks()[1]:
            label.set_x(-0.01)
            
        # set the position/size of the axis in the window
        f.axes[0].set_position([0.1,0.1,0.8,0.8])
        
        # set the axis labels
        f.axes[0].set_title('')
        f.axes[0].set_xlabel('')
        f.axes[0].set_ylabel('')

        # set the position of the legend far away
        f.axes[0].legend(loc=[1.2,0])
        
        f.canvas.Refresh()
        
        # autoscale
        self.OnButtonAutoscaleButton(None)
        

   
    def OnTreeCtrlMainSelChanged(self, event):
        T = self.TreeCtrlMain
        
        # get the current selection
        # all branches should have a my_value variable (string)
        s     = T.GetSelection()
        
        # set the value in the value box to that of this tree branch
        self.TextCtrlValue.SetValue(self.GetTreeItemData(s,"string"))
        
        # if the type is a line attribute
        if self.GetTreeItemData(s,"type") in self.line_attributes:
            self.ButtonApplyAll.Enable()
        else:
            self.ButtonApplyAll.Disable()
            
        if self.GetTreeItemData(s,"axes") == None:
            self.ButtonAutoscale.Disable()
        else:
            self.ButtonAutoscale.Enable()
        
        # highlight the text in the box
        self.TextCtrlValue.SetFocus()
        
    
        
        
    

            
                    
    def OnButtonApplyButton(self, event):
        T = self.TreeCtrlMain
        s = T.GetSelection()
        
        # get the value from the text box
        new_string = self.TextCtrlValue.GetValue()
        
        # set the attribute (updates the plot too)
        self.SetAttribute(s, new_string)
    
    
    
    def OnButtonApplyAllButton(self, event):
        # get the current selection
        s = self.TreeCtrlMain.GetSelection()
        f = self.GetTreeItemData(s, "figure")
            
        # get the parent axes
        p = self.GetTreeItemData(s, "parent")
        p = self.GetTreeItemData(p, "parent")
        
        # get all the children
        children = self.GetTreeItemData(p, "children")
    
        # get all the children that have an associated line
        line_children = []
        for child in children:
            if self.GetTreeItemData(child, "type") == "line_title":
                line_children.append(child)
    
        # get the value from the text box
        new_string = self.TextCtrlValue.GetValue()
        type       = self.GetTreeItemData(s, "type")
        
        # loop over the line children
        for child in line_children:
            # find the child that has the same type
            s = self.FindChildType(child, type)    
    
            # set the attribute
            self.SetAttribute(s, new_string)
    
        f.canvas.Refresh()
        
    def OnButtonAutoscaleButton(self, event):
        # Autoscales the data on the currently selected axes
        
        # for ease of coding:
        T = self.TreeCtrlMain
        s = T.GetSelection()
        f = self.GetTreeItemData(s, "figure")
        a = self.GetTreeItemData(s, "axes") 
        
        # get all the lines
        lines = a.get_lines()
        
        xdata = []
        ydata = []
        # get all the data into one giant array
        for n in range(0,len(lines)):
            x = lines[n].get_xdata()
            y = lines[n].get_ydata()
            for m in range(0,len(x)):
                xdata.append(x[m])
                ydata.append(y[m])
        
        xmin = min(xdata)
        xmax = max(xdata)
        ymin = min(ydata)
        ymax = max(ydata)
        
        # we want a 3% white space boundary surrounding the data in our plot
        # so set the range accordingly
        a.set_xlim(xmin-0.03*(xmax-xmin), xmax+0.03*(xmax-xmin))
        a.set_ylim(ymin-0.03*(ymax-ymin), ymax+0.03*(ymax-ymin))
        
        f.canvas.Refresh()
    
    
    
   
