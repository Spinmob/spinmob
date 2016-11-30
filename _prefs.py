import os as _os

def read_lines(path):
    f = open(path, 'rU')
    a = f.readlines()
    f.close()
    return(a)


class Prefs():
    prefs_path     = ''
    home_dir       = ''
    temp_dir       = ''
    colormaps_dir  = ''
    path_delimiter = ''
    prefs = {}


    def __init__(self):
        """
        This class holds all the user-variables, paths etc...
        """

        # figure out what path delimiter we need to use
        if _os.name == "posix":
            self.path_delimiter = "/"
        else:
            # assume windows
            _os.environ['HOME'] = _os.environ['USERPROFILE']
            self.path_delimiter = "\\"

        # assemble the home and temp directory path for this environment
        self.home_dir      = _os.environ['HOME'] + self.path_delimiter + '.spinmob'
        self.temp_dir      = self.home_dir       + self.path_delimiter + 'temp'
        self.prefs_path    = self.home_dir       + self.path_delimiter + 'preferences.txt'
        self.colormaps_dir = self.home_dir       + self.path_delimiter + 'colormaps'

        # see if this is the first time running (no home directory)
        if not _os.path.exists(self.home_dir):
            print("Creating "+self.home_dir)
            _os.mkdir(self.home_dir)

        if not _os.path.exists(self.temp_dir):
            print("Creating "+self.temp_dir)
            _os.mkdir(self.temp_dir)

        if not _os.path.exists(self.prefs_path):
            print("Creating "+self.prefs_path)
            open(self.prefs_path, 'w').close()

        if not _os.path.exists(self.colormaps_dir):
            print("Creating "+self.colormaps_dir)
            _os.mkdir(self.colormaps_dir)

        # now read in the prefs file
        lines = read_lines(self.prefs_path)
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
            s = s + key + " = " + self.prefs[key] + '\n'
        return s

    def keys(self): return list(self.prefs.keys())
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

    def Dump(self):
        """
        Dumps the current prefs to the preferences.txt file
        """
        prefs_file = open(self.prefs_path, 'w')
        for n in range(0,len(self.prefs)):
            if len(list(self.prefs.items())[n]) > 1:
                prefs_file.write(str(list(self.prefs.items())[n][0]) + ' = ' +
                                 str(list(self.prefs.items())[n][1]) + '\n')
        prefs_file.close()


