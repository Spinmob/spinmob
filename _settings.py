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


    def __init__(self):
        """
        This class holds all the user-variables, paths etc...
        """
        
        # assemble the home and temp directory path for this environment
        self.path_user      = _os.path.expanduser('~')      
        self.path_home      = _os.path.join(self.path_user, ".spinmob")
        self.path_temp      = _os.path.join(self.path_home, 'temp')
        self.path_settings  = _os.path.join(self.path_home, 'preferences.txt')
        self.path_colormaps = _os.path.join(self.path_home, 'colormaps')

        # see if this is the first time running (no home directory)
        if not _os.path.exists(self.path_home):
            print "Creating "+self.path_home
            _os.mkdir(self.path_home)

        if not _os.path.exists(self.path_temp):
            print "Creating "+self.path_temp
            _os.mkdir(self.path_temp)

        if not _os.path.exists(self.path_settings):
            print "Creating "+self.path_settings
            open(self.path_settings, 'w').close()

        if not _os.path.exists(self.path_colormaps):
            print "Creating "+self.path_colormaps
            _os.mkdir(self.path_colormaps)

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
        for key in self.prefs.keys():
            s = s + key + " = " + str(self.prefs[key]) + '\n'
        return s

    def __repr__(self): 
        s = '\nSPINMOB SETTINGS\n'
        for key in self.prefs.keys():
            s = s + "  " + key + " = " + str(self.prefs[key]) + '\n'
        return s

    def keys(self): return self.prefs.keys()
    def has_key(self, key): return self.prefs.has_key(key)

    def List(self):
        """
        Lists the keys and values.
        """
        print
        for key in self.keys():
            print key,'=',self[key]
        print

    def Get(self, key):
        """
        Checks if the key exists and returns it. Returns None if it doesn't
        """
        if self.prefs.has_key(key):
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
        for key in self.keys(): self.Remove(key)

    def Dump(self):
        """
        Dumps the current prefs to the preferences.txt file
        """
        prefs_file = open(self.path_settings, 'w')
        for n in range(0,len(self.prefs)):
            if len(self.prefs.items()[n]) > 1:
                prefs_file.write(str(self.prefs.items()[n][0]) + ' = ' +
                                 str(self.prefs.items()[n][1]) + '\n')
        prefs_file.close()


