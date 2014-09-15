import PyQt4.QtGui as _qt
import os          as _os

if __name__=='__main__': 
    import spinmob as _s
    _settings = _s.settings

def save(filters='*.*', text='Save THIS, facehead!', default_directory='default_directory'):
    """
    Pops up a save dialog and returns the string path of the selected file.
    """
    # make sure the filters contains "*.*" as an option!
    if filters.find('*.*') < 0: filters = filters + ";;All files (*.*)"
    
    
    # if this type of pref doesn't exist, we need to make a new one
    if _settings.has_key(default_directory): default = _settings[default_directory]
    else:                                    default = ""
    
    # pop up the dialog
    result = str(_qt.QFileDialog.getSaveFileName(None,text,default,filters))
    
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
    if _settings.has_key(default_directory): default = _settings[default_directory]
    else:                                    default = ""
    
    # pop up the dialog
    result = str(_qt.QFileDialog.getOpenFileName(None,text,default,filters))
    
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
    if _settings.has_key(default_directory): default = _settings[default_directory]
    else:                                    default = ""
    
    # pop up the dialog
    result = list(_qt.QFileDialog.getOpenFileNames(None,text,default,filters))
    for n in range(len(result)): result[n] = str(result[n])    
    
    if len(result)==0: return
    else:
        _settings[default_directory] = _os.path.split(result[0])[0]
        return result 


def select_directory(text='Select a directory, POCKETPANTS!', default_directory='default_directory'):

    # if this type of pref doesn't exist, we need to make a new one
    if _settings.has_key(default_directory): default = _settings[default_directory]
    else:                                    default = ""
    
    # pop up the dialog
    result = str(_qt.QFileDialog.getExistingDirectory(None,text,default))
    
    if result == '': return None
    else:
        _settings[default_directory] = _os.path.split(result)[0]
        return result 







