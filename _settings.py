import os as _os


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
    prefs = {}


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
            print("\nFirst run: creating "+self.path_home)
            _os.mkdir(self.path_home)

        if not _os.path.exists(self.path_settings):
            print(" Creating "+self.path_settings + "\n")
            open(self.path_settings, 'w').close()


        # now read in the prefs file
        lines = read_lines(self.path_settings)
        self.prefs = {}
        for n in range(0,len(lines)):
            s = lines[n].split('=')
            if len(s) > 1:
                self.prefs[s[0].strip()] = s[1].strip()


    def __call__   (self, key): return self.Get(key)
    def __getitem__(self,key):  return self.Get(key)
    def __setitem__(self,key,value): self.Set(key, value)
    def __str__(self):
        s = ''
        for key in list(self.prefs.keys()):
            s = s + key + " = " + str(self.prefs[key]) + '\n'
        return s

    def __repr__(self):
        s = '\nSPINMOB SETTINGS\n'
        for key in list(self.prefs.keys()):
            s = s + "\n" + key + " = " + str(self.prefs[key]) + '\n'
        return s

    def keys(self):         return list(self.prefs.keys())
    def has_key(self, key): return key in self.prefs

    def List(self):
        """
        Lists the keys and values.
        """
        print()
        for key in list(self.keys()):
            print(key,'=',self[key])
        print()

    def Get(self, key):
        """
        Checks if the key exists and returns it. Returns None if it doesn't
        """
        if key in self.prefs:
            return self.prefs[key]
        else:
            return None

    def Set(self, key, value):
        """
        Sets the key-value pair and dumps to the preferences file.
        """
        if not value == None: self.prefs[key] = value
        else:                 self.prefs.pop(key)

        self.Dump()

    def Remove(self, key):
        """
        Removes a key/value pair
        """
        self.Set(key, None)

    def RemoveAll(self):
        """
        Removes all settings.
        """
        for key in list(self.keys()): self.Remove(key)

    def MakeDir(self, path="temp"):
        """
        Creates a directory of the specified path in the .spinmob directory.
        """
        full_path = _os.path.join(self.path_home, path)

        # only make it if it doesn't exist!
        if not _os.path.exists(full_path): _os.makedirs(full_path)

    def ListDir(self, path="temp"):
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

    def Dump(self):
        """
        Dumps the current prefs to the preferences.txt file
        """
        prefs_file = open(self.path_settings, 'w')
        for n in range(0,len(self.prefs)):
            if len(list(self.prefs.items())[n]) > 1:
                prefs_file.write(str(list(self.prefs.items())[n][0]) + ' = ' +
                                 str(list(self.prefs.items())[n][1]) + '\n')
        prefs_file.close()


