import os              as _os

import spinmob as _s
_qtw    = _s._qtw
_qtcore = _s._qtc



def save(filters='*.*', text='Save THIS, facehead!', default_directory='default_directory', force_extension=None):
    """
    Pops up a save dialog and returns the string path of the selected file.
    
    Parameters
    ----------
    filters='*.*'
        Which file types should appear in the dialog.
    text='Save THIS, facehead!'
        Title text for the dialog.
    default_directory='default_directory'
        Key for the spinmob.settings default directory. If you use a name, e.g.
        'my_defaultypoo', for one call of this function, the next time you use
        the same name, it will start in the last dialog's directory by default.
    force_extension=None
        Setting this to a string, e.g. 'txt', will enforce that the filename 
        will have this extension.   
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
    
    # Enforce the extension if necessary
    if  not force_extension == None:
            
        # In case the user put "*.txt" instead of just "txt"
        force_extension = force_extension.replace('*','').replace('.','')

        # If it doesn't end with the right extension, add this.
        if not _os.path.splitext(result)[-1][1:] == force_extension:
            result = result + '.' + force_extension

    if result == '': return None
    else:
        _settings[default_directory] = _os.path.split(result)[0]
        return result


def load(filters="*.*", text='Select a file, FACEFACE!', default_directory='default_directory'):
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


def load_multiple(filters="*.*", text='Select some files, FACEFACE!', default_directory='default_directory'):
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
    print(save('*.xyz', force_extension='pdf'))


