import os as _os
import spinmob as _s


def read_lines(path):
    f = open(path, 'rU')
    a = f.readlines()
    f.close()
    return(a)


class settings():
    path_user       = ''
    path_settings   = ''
    path_home       = ''
    path_temp       = ''
    path_colormaps  = ''
    _databox = _s.data.databox(delimiter='=')


    def __init__(self, name="spinmob"):
        """
        This class holds all the user-variables, paths etc...
        """

        # assemble the home and temp directory path for this environment
        self.path_user      = _os.path.expanduser('~')
        self.path_home      = _os.path.join(self.path_user, "."+name)
        self.path_settings  = _os.path.join(self.path_home, 'settings.txt')

        # see if this is the first time running (no home directory)
        if not _os.path.exists(self.path_home):
            print("\nFirst run:\n Creating "+self.path_home)
            _os.mkdir(self.path_home)

        if not _os.path.exists(self.path_settings):
            print(" Creating "+self.path_settings + "\n")
            f = open(self.path_settings, 'w')
            f.close()


        # now read in the prefs file
        self._databox.load_file(self.path_settings, header_only=True)


    def set_get(self, *keys, **kwargs):
        """
        Sets all keyword arguments and returns a list of values associated
        with each supplied key (if any). If only one key is supplied, returns
        the associated value (not a list).

        settings.set_get() and settings() are the same function.
        """
        # Loop over keyword arguments and set them
        for key in kwargs: self.set(key, kwargs[key])

        # Create a list of values
        values = []
        for key in keys: values.append(self.get(key))

        # Return the value if there's one or the list if there are multiple
        if   len(values) == 1: return values[0]
        elif len(values) >  1: return values

    __call__ = set_get

    def __getitem__(self,key):  return self.get(key)
    def __setitem__(self,key,value): self.set(key, value)
    def __str__(self):
        s = ''
        for key in list(self._databox.hkeys):
            s = s + key + " = " + str(self._databox.h(key)) + '\n'
        return s

    def __repr__(self):
        s = '\nSPINMOB SETTINGS'
        keys = list(self._databox.hkeys)
        keys.sort()

        for key in keys:
            s = s + "\n  " + key + " = " + repr(self._databox.h(key))
        return s

    def keys(self):         return list(self._databox.hkeys)
    def has_key(self, key): return key in self._databox.hkeys

    def get(self, key):
        """
        Checks if the key exists and returns it. Returns None if it doesn't
        """
        if key in self._databox.hkeys: return self._databox.h(key)
        else:                          return None

    def _set_theme_figures(self, theme):
        """
        Sets the matplotlib figure theme.

        Parameters
        ----------
        theme : str
            Can be 'classic' (for white) or 'dark_background' for dark theme
            (or any other theme that exists).
        """
        _s.pylab.style.use(theme)

    def set(self, key, value=None):
        """
        Sets the key-value pair and dumps to the preferences file.

        If value=None, pops / removes the setting.
        """
        if not key is None:
            if not value is None: self._databox.h(**{key:value})
            else:
                self._databox.pop_header(key, ignore_error=True)
                self.save()
                return

        # If figure theme is provided, update it.
        if key == 'dark_theme_figures':
            self._set_theme_figures('dark_background' if self['dark_theme_figures'] else 'classic')

            if not self['dark_theme_figures']:
                _s.pylab.rcParams['figure.facecolor'] = 'white'

        # Other pylab settings
        if key in ['font_size']:
             _s.pylab.rcParams.update({'font.size' : self['font_size']})

        # pyqtgraph opengl
        if key in ['egg_use_opengl'] and _s._pyqtgraph_ok:
            _s._pyqtgraph.setConfigOptions(useOpenGL=self['egg_use_opengl'])

        # Save the settings.
        self.save()


    def pop(self, *keys):
        """
        Pops the specified keys.
        """
        for key in keys: self.set(key)

    def clear(self):
        """
        Removes all settings.
        """
        self.pop(*self.keys())

    def make_dir(self, path="temp"):
        """
        Creates a directory of the specified path in the .spinmob directory.
        """
        full_path = _os.path.join(self.path_home, path)

        # only make it if it doesn't exist!
        if not _os.path.exists(full_path): _os.makedirs(full_path)

    def list_dir(self, path="temp"):
        """
        Returns a list of files in the specified path (directory), or an
        empty list if the directory doesn't exist.
        """
        full_path = _os.path.join(self.path_home, path)

        # only if the path exists!
        if _os.path.exists(full_path) and _os.path.isdir(full_path):
            return _os.listdir(full_path)
        else:
            return []

    def save(self):
        """
        Dumps the current prefs to the preferences.txt file
        """
        self._databox.save_file(self.path_settings, force_overwrite=True)

    def reset(self):
        """
        Clears any user settings and resets expected settings to their defaults.
        """
        self.clear()

        # Loop over defaults and set them
        for _k in _s._defaults: self[_k] = _s._defaults[_k]
