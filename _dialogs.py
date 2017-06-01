import os              as _os

import spinmob as _s
_qtw    = _s._qtw
_qtcore = _s._qtc



def save(filters='*.*', text='Save THIS, facehead!', default_directory='default_directory'):
    """
    Pops up a save dialog and returns the string path of the selected file.
    """
    # make sure the filters contains "*.*" as an option!
    if not '*' in filters.split(';'): filters = filters + ";;All files (*)"
    
    # if this type of pref doesn't exist, we need to make a new one
    if default_directory in _settings.keys(): default = _settings[default_directory]
    else:                                     default = ""
    
    # pop up the dialog
    result = _qtw.QFileDialog.getSaveFileName(None,text,default,filters)
    
    # If Qt5, take the zeroth element
    if _s._qt.VERSION_INFO[0:5] == "PyQt5": result = result[0]    
    
    # Make sure it's a string
    result = str(result)    
    
    if result == '': return None
    else:
        _settings[default_directory] = _os.path.split(result)[0]
        return result


def open_single(filters="*.*", text='Select a file, FACEFACE!', default_directory='default_directory'):
    """
    Pops up a dialog for opening a single file. Returns a string path or None.
    """
    # make sure the filters contains "*.*" as an option!
    if not '*' in filters.split(';'): filters = filters + ";;All files (*)"
    
    # if this type of pref doesn't exist, we need to make a new one
    if default_directory in _settings.keys(): default = _settings[default_directory]
    else:                                     default = ""
    
    # pop up the dialog
    result = _qtw.QFileDialog.getOpenFileName(None,text,default,filters)
    
    # If Qt5, take the zeroth element
    if _s._qt.VERSION_INFO[0:5] == "PyQt5": result = result[0]
    
    # Make sure it's a string
    result = str(result)    
    
    if result == '': return None
    else:
        _settings[default_directory] = _os.path.split(result)[0]
        return result


def open_multiple(filters="*.*", text='Select some files, FACEFACE!', default_directory='default_directory'):
    """
    Pops up a dialog for opening more than one file. Returns a list of string paths or None.
    """
    # make sure the filters contains "*.*" as an option!
    if not '*' in filters.split(';'): filters = filters + ";;All files (*)"
    
    # if this type of pref doesn't exist, we need to make a new one
    if default_directory in _settings.keys(): default = _settings[default_directory]
    else:                                     default = ""
    
    # pop up the dialog
    results = _qtw.QFileDialog.getOpenFileNames(None,text,default,filters)
    
    # If Qt5, take the zeroth element
    if _s._qt.VERSION_INFO[0:5] == "PyQt5": results = results[0]
    
    # Make sure it's a string
    result = []
    for r in results: result.append(str(r))       
    
    if len(result)==0: return
    else:
        _settings[default_directory] = _os.path.split(result[0])[0]
        return result


def select_directory(text='Select a directory, POCKETPANTS!', default_directory='default_directory'):

    # if this type of pref doesn't exist, we need to make a new one
    if default_directory in _settings.keys(): default = _settings[default_directory]
    else:                                     default = ""
    
    # pop up the dialog
    result = _qtw.QFileDialog.getExistingDirectory(None,text,default)
    
    # Make sure it's a string
    result = str(result)        
    
    if result == '': return None
    else:
        _settings[default_directory] = _os.path.split(result)[0]
        return result 




if __name__=='__main__': 
    import spinmob as _s
    _settings = _s.settings


