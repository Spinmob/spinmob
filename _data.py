import os as _os
import _useful_functions as _fun      
import _dialogs                      
import _data_types                    


# make the databox data class visible, ja.
databox = _data_types.databox

def load(path="ask", first_data_line="auto", filters="*.*", text="Select a file, FACEHEAD.", default_directory="default_directory", quiet=False, header_only=False, **kwargs):
    """
    Loads a data file into the databox data class. Returns the data object.

    **kwargs are sent to databox(), so check there for more information (i.e.
    about delimiters)
    
    The most common modification to the default behavior is to change the
    delimiter for csv files:
    
    >>> load(delimiter=",")
    """
    d = databox(**kwargs)
    d.load_file(path=path, first_data_line=first_data_line,
                filters=filters, text=text, default_directory=default_directory,
                header_only=header_only)

    if not quiet: print "loaded", d.path

    return d

def load_multiple(paths="ask", first_data_line="auto", filters="*.*", text="Select some files, FACEHEAD.", default_directory="default_directory", **kwargs):
    """
    Loads a list of data files into a list of databox data objects.
    Returns said list.

    **kwargs are sent to databox()
    
    The most common modification to the default behavior is to change the
    delimiter for csv files:
    
    >>> load(delimiter=",")
    """
    if paths=="ask": paths = _dialogs.open_multiple(filters, text, default_directory)
    if paths==None : return

    datas = []
    for path in paths:
        if _os.path.isfile(path): datas.append(load(path, first_data_line, **kwargs))

    return datas
