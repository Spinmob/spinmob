import wx as _wx
try:    _prefs
except: _prefs = {}
#
# Dialogs
#
def Save(filters="*.*", text='save THIS!', default_directory='default_directory'):

    global _prefs

    # if this type of pref doesn't exist, we need to make a new one
    if _prefs.has_key(default_directory): default = _prefs[default_directory]
    else:                                default = ""

    # define the dialog object.  Doesn't opent he window
    dialog = _wx.FileDialog(None,
                           message = text,
                           defaultDir = default,
                           wildcard = filters,
                           style = _wx.SAVE|_wx.OVERWRITE_PROMPT)

    # This is the command that pops up the dialog for the user
    if dialog.ShowModal() == _wx.ID_OK:

       # update the default path so you don't have to keep navigating
       _prefs[default_directory] = dialog.GetDirectory()

       # not sure if you need to, but destroy the object
       dialog.Destroy()

       return(dialog.GetPath())

    else:   return(None)






def SingleFile(filters="*.*", text='select a file, fungus pants!', default_directory='default_directory'):

    global _prefs

    # if this type of pref doesn't exist, we need to make a new one
    if _prefs.has_key(default_directory): default = _prefs[default_directory]
    else:                                 default = ""

    # define the dialog object.  Doesn't opent he window
    dialog = _wx.FileDialog(None,
                           message = text,
                           defaultDir = default,
                           wildcard = filters,
                           style = _wx.OPEN)

    # This is the command that pops up the dialog for the user
    if dialog.ShowModal() == _wx.ID_OK:

	    # get the paths for returning
	    path = dialog.GetPath()

	    # update the default path so you don't have to keep navigating
	    _prefs[default_directory] = dialog.GetDirectory()

	    # not sure if you need to, but destroy the object
	    dialog.Destroy()

	    return(path)
    else:   return(None)

def Directory(text='select a directory, hairhead!', default_directory='default_directory'):

    global _prefs

    # if this type of pref doesn't exist, we need to make a new one
    if _prefs.has_key(default_directory): default = _prefs[default_directory]
    else:                                 default = ""

    # define the dialog object.  Doesn't opent he window
    dialog = _wx.DirDialog(None,
                           message = text,
                           defaultPath = default,
                           style = _wx.DD_DEFAULT_STYLE)

    # This is the command that pops up the dialog for the user
    if not dialog.ShowModal() == _wx.ID_OK: return None

    # update the default path so you don't have to keep navigating
    _prefs[default_directory] = dialog.GetPath()

    # not sure if you need to, but destroy the object
    dialog.Destroy()

    return(dialog.GetPath())






def MultipleFiles(filters="*.*", text='select some files, facehead!', default_directory='default_directory'):

    global _prefs

    # if this type of pref doesn't exist, we need to make a new one
    if _prefs.has_key(default_directory): default = _prefs[default_directory]
    else:                                default = ""

    # define the dialog object.  Doesn't opent he window
    dialog = _wx.FileDialog(None,
                           message = text,
                           defaultDir = default,
                           wildcard = filters,
                           style = _wx.OPEN | _wx.MULTIPLE)

    # This is the command that pops up the dialog for the user
    if not dialog.ShowModal() == _wx.ID_OK: return None

    # update the default path so you don't have to keep navigating
    _prefs[default_directory] = dialog.GetDirectory()

    # not sure if you need to, but destroy the object
    dialog.Destroy()

    return(dialog.GetPaths())


