import PyQt5.QtWidgets as _qt
import os              as _os


def save(filters='*.*', text='Save THIS, facehead!', default_directory='default_directory'):
    """
    Pops up a save dialog and returns the string path of the selected file.
    """
    # make sure the filters contains "*.*" as an option!
    if filters.find('*.*') < 0: filters = filters + ";;All files (*.*)"
    
    # if this type of pref doesn't exist, we need to make a new one
    if default_directory in _settings.keys(): default = _settings[default_directory]
    else:                                     default = ""
    
    # pop up the dialog
    result = _qt.QFileDialog.getSaveFileName(None,text,default,filters)[0]
    
    if result == '': return None
    else:
        _settings[default_directory] = _os.path.split(result)[0]
        return result 


def open_single(filters="*.*", text='Select a file, FACEFACE!', default_directory='default_directory'):
    """
    Pops up a dialog for opening a single file. Returns a string path or None.
    """
    # make sure the filters contains "*.*" as an option!
    if filters.find('*.*') < 0: filters = filters + ";;All files (*.*)"
    
    # if this type of pref doesn't exist, we need to make a new one
    if default_directory in _settings.keys(): default = _settings[default_directory]
    else:                                     default = ""
    
    # pop up the dialog
    result = _qt.QFileDialog.getOpenFileName(None,text,default,filters)[0]
    
    if result == '': return None
    else:
        _settings[default_directory] = _os.path.split(result)[0]
        return result 


def open_multiple(filters="*.*", text='Select some files, FACEFACE!', default_directory='default_directory'):
    """
    Pops up a dialog for opening more than one file. Returns a list of string paths or None.
    """
    # make sure the filters contains "*.*" as an option!
    if filters.find('*.*') < 0: filters = filters + ";;All files (*.*)"
    
    # if this type of pref doesn't exist, we need to make a new one
    if default_directory in _settings.keys(): default = _settings[default_directory]
    else:                                     default = ""
    
    # pop up the dialog
    result = _qt.QFileDialog.getOpenFileNames(None,text,default,filters)[0]
    
    if len(result)==0: return
    else:
        _settings[default_directory] = _os.path.split(result[0])[0]
        return result 


def select_directory(text='Select a directory, POCKETPANTS!', default_directory='default_directory'):

    # if this type of pref doesn't exist, we need to make a new one
    if default_directory in _settings.keys(): default = _settings[default_directory]
    else:                                     default = ""
    
    # pop up the dialog
    result = _qt.QFileDialog.getExistingDirectory(None,text,default)
    
    if result == '': return None
    else:
        _settings[default_directory] = _os.path.split(result)[0]
        return result 




if __name__=='__main__': 
    import spinmob as _s
    _settings = _s.settings


