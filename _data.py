import os as _os
import _dialogs

# do this so all the scripts will work with all the numpy functions
import numpy as _n
import scipy.optimize as _opt
import pylab as _p
import textwrap as _textwrap
import spinmob as _s













#############################################################
# Class for storing / manipulating / saving / loading data
#############################################################

class databox:

    # this is used by the load_file to rename some of the annoying
    # column names that aren't consistent between different types of data files (and older data files)
    # or to just rename columns with difficult-to-remember ckeys.

    obnoxious_ckeys = {}
    #obnoxious_ckeys = {"example_annoying1" : "unified_name1",
    #                   "example_annoying2" : "unified_name2"}

    directory      = "default_directory"
    path           = "(no path)"

    debug          = False  # Use this to print debug info in various places
    delimiter      = None   # delimiter of the ascii file. If "None" this will just use any whitespace

    headers = {}            # this dictionary will hold the header information
    columns = {}            # this dictionary will hold the data columns
    ckeys   = []            # we need a special list of column keys to keep track of their order during data assembly
    hkeys   = []            # ordered list of header keys
    extra_globals = {}



    def __setitem__(self, n, x):
        """
        set's the n'th column to x (n can be a column name too)
        """
        if type(n) == str:
            self.insert_column(data_array=x, ckey=n, index='end')

        elif type(n) in [int, long] and n > len(self.ckeys)-1:
            self.insert_column(data_array=x, ckey='_column'+str(len(self.ckeys)), index='end')

        else:
            self.columns[self.ckeys[n]] = _n.array(x)

    def __len__(self):
        return len(self.ckeys)

    def __getslice__(self,i,j):
        output = []
        for n in range(i,min(j, len(self))): output.append(self[n])
        return output

    #
    # functions that are often overwritten in modified data classes
    #
    def __init__(self, delimiter=None, debug=False):
        """
        delimiter                   The delimiter the file uses. None means "white space"
        debug                       Displays some partial debug information while running
        """

        # this keeps the dictionaries from getting all jumbled with each other
        self.clear_columns()
        self.clear_headers()

        self.debug     = debug
        self.delimiter = delimiter

    # create a simple initializer command for the user.
    initialize = __init__

    def __repr__(self):

        s = "\nDatabox Instance"
        s = s+"\n  header elements: "+str(len(self.hkeys))
        s = s+"\n  columns of data: "+str(len(self.ckeys))
        s = s+"\n"
        return s

    def _globals(self):
        """
        Returns the globals needed for eval() statements.
        """

        # start with numpy
        globbies = dict(_n.__dict__)

        # update with required stuff
        globbies.update({'h':self.h, 'c':self.c, 'd':self, 'self':self})

        # update with user stuff
        globbies.update(self.extra_globals)

        return globbies


    #
    # really useful functions
    #
    def load_file(self, path="ask", first_data_line="auto", filters="*.*", text="Select a file, FACEPANTS.", default_directory=None, header_only=False, quiet=False):
        """
        This will clear the databox, load a file, storing the header info in self.headers, and the data in
        self.columns

        If first_data_line="auto", then the first data line is assumed to be the first line
        where all the elements are numbers.

        If you specify a first_data_line (index, starting at 0), the columns need not be
        numbers. Everything above will be considered header information and below will be
        data columns.

        In both cases, the line used to label the columns will always be the last
        header line with the same (or more) number of elements as the first data line.

        """

        if default_directory==None: default_directory = self.directory

        if path=="ask":
            path = _dialogs.open_single(filters=filters,
                                        default_directory=self.directory,
                                        text=text)
        self.path = path

        if path==None:
            if not quiet: print "Aborted."
            return None

        # make sure the file exists!
        if not _os.path.exists(path):
            if not quiet: print "ERROR: "+repr(path)+" does not exist."
            return None

        # clear all the existing data
        self.clear()

        # open said file for reading, read in all the lines and close
        f = open(path, 'r')
        lines = f.readlines()
        f.close()



        ##### read in the header information
        self.header_lines = []
        
        for n in range(len(lines)):
            
            # save the lines for the avid user.
            self.header_lines.append(lines[n].strip())            
            
            # split the line by the delimiter
            s = lines[n].strip().split(self.delimiter)
            
            # remove a trailing whitespace entry if it exists.
            if len(s) and s[-1].strip() == '': s.pop(-1)

            # first check and see if this is a data line (all elements are numbers)
            if first_data_line=="auto" and _s.fun.elements_are_numbers(s):

                # we've reached the first data line
                first_data_line = n
                
                # quit the header loop
                break;


            ### now we know it's a header line

            # first thing to try is simply evaluating the remaining string
            try:
                hkey      = s[0]
                remainder = ' '.join(s[1:])
                self.insert_header(hkey, eval(remainder, self._globals()))

            except: pass

        # now we have a valid set of column ckeys one way or another, and we know first_data_line.
        if header_only: return self

        # Make sure first_data_line isn't None (which happens if there's no data)
        if first_data_line == "auto":
            if not quiet: print "\nCould not find a line of pure data! Perhaps check the delimiter?"
            if not quiet: print "The default delimiter is whitespace. For csv files, set delimiter=','\n"
            return self



        ##### at this point we've found the first_data_line,

        # look for the ckeys

        # special case: no header
        if first_data_line == 0: self.ckeys = []
    
        # start by assuming it's the previous line    
        else: self.ckeys = lines[first_data_line-1].strip().split(self.delimiter)

        # count the number of actual data columns for comparison
        column_count = len(lines[first_data_line].strip().split(self.delimiter))
        
        # check to see if ckeys is equal in length to the
        # number of data columns. If it isn't, it's a false ckeys line
        if len(self.ckeys) >= column_count:
            # it is close enough
            # if we have too many column keys, mention it
            while len(self.ckeys) > column_count:
                extra = self.ckeys.pop(-1)
                if not quiet: print "Extra ckey: "+extra

        else:
            # it is an invalid ckeys line. Generate our own!
            self.ckeys = []
            for m in range(0, column_count): self.ckeys.append("c"+str(m))

        # initialize the columns arrays
        # I did benchmarks and there's not much improvement by using numpy-arrays here.
        for label in self.ckeys: self.columns[label] = []

        # define a quick function to convert i's to j's
        def fix(x): return x.replace('i','j')
        
        # loop over the remaining data lines, converting to numbers
        z = _n.genfromtxt((fix(x) for x in lines[first_data_line:]), 
                          delimiter=self.delimiter,
                          dtype=complex)

        # fix for different behavior of genfromtxt on single columns
        if len(z.shape)==2: z = z.transpose()
        else:               z = [z]
        
        # Add all the columns
        for n in range(len(self.ckeys)):

            # if any of the imaginary components are non-zero, use complex
            if _n.any(_n.imag(z[n])): self[self.ckeys[n]] = z[n]
            else:                     self[self.ckeys[n]] = _n.real(z[n])

        # now, as an added bonus, rename some of the obnoxious headers
        for k in self.obnoxious_ckeys:
            if self.columns.has_key(k):
                self.columns[self.obnoxious_ckeys[k]] = self.columns[k]

        return self

    def save_file(self, path="ask", filters="*.dat", force_overwrite=False, header_only=False):
        """
        This will save all the header info and columns to an ascii file.
        """

        if path=="ask": path = _dialogs.save(filters, default_directory=self.directory)
        if path in ["", None]:
            print "Aborted."
            return False

        self.path=path

        # if the path exists, make a backup
        if _os.path.exists(path) and not force_overwrite:
            _os.rename(path,path+".backup")

        # get the delimiter
        if self.delimiter==None: delimiter = "\t"
        else:                    delimiter = self.delimiter

        # open the file and write the header
        f = open(path, 'w')
        for k in self.hkeys: f.write(k + delimiter + repr(self.headers[k]) + "\n")
        f.write('\n')

        # if we're only supposed to write the header
        if header_only: return

        # now write the ckeys
        elements = []
        for ckey in self.ckeys: elements.append(str(ckey))
        f.write(delimiter.join(elements) + "\n")

        # now loop over the data
        for n in range(0, len(self[0])):
            # loop over each column
            elements = []
            for m in range(0, len(self.ckeys)):
                # write the data if there is any, otherwise, placeholder ("x")
                if n < len(self[m]):
                    elements.append(str(self[m][n]))
                else:
                    elements.append('_')
            f.write(delimiter.join(elements) + "\n")


        f.close()



    def pop_data_point(self, n, ckeys=[]):
        """
        This will remove and return the n'th data point (starting at 0)
        in the supplied list of columns.

        n       index of data point to pop
        ckeys   which columns to do this to, specified by index or key
                empty list means "every column"
        """

        # if it's empty, it's everything
        if ckeys == []: ckeys = self.ckeys

        # loop over the columns of interest and pop the data
        popped = []
        for k in ckeys:
            if not k == None:
                # first convert to a list
                data = list(self.c(k))

                # pop the data
                popped.append(data.pop(n))

                # now set this column again
                self.insert_column(data, k)

        return popped






    def execute_script(self, script, g={}):
        """
        Runs a script, returning the result.

        Scripts are of the form:

        "3.0 + x/y - self[0] where x=3.0*c('my_column')+h('setting'); y=c(1)"

        "self" refers to the data object, giving access to everything, enabling
        complete control over the universe. c() and h() give quick reference
        to self.c() and self.h() to get columns and header lines

        Additionally, these scripts can see all of the numpy functions like sin,
        cos, sqrt, etc.

        Finally, if you would like access to additional globals, set
        self.extra_globals to the appropriate globals dictionary or add globals
        using insert_global(). Setting g=globals() will automatically insert
        your globals into this databox instance.

        There are a few shorthand scripts available as well. You can simply type
        a column name such as "my_column" or a column number like 2. However, I
        only added this functionality as a shortcut, and something like
        "2.0*a where a=F" will not work unless F is defined somehow. I figure
        since you're already writing a complicated script, you don't want to
        accidentally shortcut your way into using a column instead of a constant!
        Use "2.0*a where a=c('F')" instead.

        NOTE: You shouldn't try to use variables like 'c=...' or 'h=...' because
        they are already column and header functions!

        """

        # add any extra user-supplied global variables for the eventual eval() call.
        self.extra_globals.update(g)

        # If the script is not a list of scripts, return the script value.
        # This is the termination of a recursive call.
        if not _s.fun.is_iterable(script):

            # special case
            if script == None: return None

            # get the expression and variables dictionary
            [expression, v] = self._parse_script(script)

            # if there was a problem parsing the script
            if v == None:
                print "ERROR: Could not parse '"+script+"'"
                return None

            # get all the numpy stuff too
            g = self._globals()
            g.update(v)

            # otherwise, evaluate the script using python's eval command
            return eval(expression, g)

        # Otherwise, this is a list of (lists of) scripts. Make the recursive call.
        output = []
        for s in script: output.append(self.execute_script(s))

        return output

    # Define this so you can quickly call a script
    __call__ = execute_script

    def _parse_script(self, script, n=0):
        """
        This takes a script such as "a/b where a=c('current'), b=3.3" and returns
        ["a/b", {"a":self.columns["current"], "b":3.3}]

        You can also just use an integer for script to reference columns by number
        or use the column label as the script.

        n is for internal use. Don't use it. In fact, don't use this function, user.
        """

        if n > 1000:
            print "This script ran recursively 1000 times!"
            a = raw_input("<enter> or (q)uit: ")
            if a.strip().lower() in ['q', 'quit']:
                script = None

        if script==None: return [None, None]

        # check if the script is simply an integer
        if type(script) in [int,long]:
            if script<0: script = script+len(self.ckeys)
            return ["___"+str(script), {"___"+str(script):self[script]}]

        # the scripts would like to use calls like "h('this')/3.0*c('that')",
        # so to make eval() work we should add these functions to a local list

        # first split up by "where"
        split_script = script.split(" where ")


        ########################################
        # Scripts without a "where" statement:
        ########################################

        # if it's a simple script, like "column0" or "c(3)/2.0"
        if len(split_script) == 1:
            if self.debug: print "script of length 1"

            # try to evaluate the script

            # first try to evaluate it as a simple column label
            if n==0 and script in self.ckeys:
                # only try this on the zero'th attempt
                # if this is a recursive call, there can be ambiguities if the
                # column names are number strings
                return ['___', {'___':self[script]}]


            # Otherwise, evaluate it.
            try:
                b = eval(script, self._globals())
                return ['___', {'___':b}]
            except:
                print
                print "ERROR: Could not evaluate '"+str(script)+"'"
                return [None, None]


        #######################################
        # Full-on fancy scripts
        #######################################

        # otherwise it's a complicated script like "c(1)-a/2 where a=h('this')"

        # tidy up the expression
        expression = split_script[0].strip()

        # now split the variables list up by ,
        varsplit = split_script[1].split(';')

        # loop over the entries in the list of variables, storing the results
        # of evaluation in the "stuff" dictionary
        stuff = dict()
        for var in varsplit:

            # split each entry by the "=" sign
            s = var.split("=")
            if len(s) == 1:
                print s, "has no '=' in it"
                return [None, None]

            # tidy up into "variable" and "column label"
            v = s[0].strip()
            c = s[1].strip()

            # now try to evaluate c, given our current globbies

            # recursively call this sub-script. At the end of all this mess
            # we want the final return value to be the first expression
            # and a full dictionary of variables to fill it
            [x,y] = self._parse_script(c, n+1)

            # if it's not working, just quit out.
            if y==None: return [None, None]

            stuff[v] = y[x]

        # at this point we've found or generated the list
        return [expression, stuff]



    def insert_column(self, data_array, ckey='temp', index='end'):
        """
        This will insert/overwrite a new column and fill it with the data from the
        the supplied array.

        If ckey is an integer, use self.ckeys[ckey]
        """

        # if it's an integer, use the ckey from the list
        if type(ckey) in [int, long]: ckey = self.ckeys[ckey]

        # append/overwrite the column value
        self.columns[ckey] = _n.array(data_array)
        if not ckey in self.ckeys:
            if index=='end':
                self.ckeys.append(ckey)
            else:
                self.ckeys.insert(index, ckey)


    def copy_headers(self, other_databox):
        """
        Loops over the hkeys of the other_databox and sets this databoxes' header.
        """
        for k in other_databox.hkeys: self.insert_header(k, other_databox.h(k))

    def copy_columns(self, other_databox):
        """
        Loops over the ckeys of the other_databox and sets this databoxes' columns.
        """
        for k in other_databox.ckeys: self.insert_column(other_databox[k], k)

    def copy_all(self, other_databox):
        """
        Copies the header and columns from other_databox.
        """
        self.copy_headers(other_databox)
        self.copy_columns(other_databox)

    def insert_header(self, hkey, value, index='end'):
        """
        This will insert/overwrite a value to the header and hkeys.

        If hkey is an integer, use self.hkeys[hkey]
        """

        # if it's an integer, use the hkey from the list
        if type(hkey) in [int, long]: hkey = self.hkeys[hkey]

        # set the data
        self.headers[str(hkey)] = value
        if not hkey in self.hkeys:
            if index=='end': self.hkeys.append(str(hkey))
            else:            self.hkeys.insert(index, str(hkey))

    def insert_global(self, thing, name=None):
        """
        Appends or overwrites the supplied object in the self.extra_globals.

        Use this to expose execute_script() or _parse_script() etc... to external
        objects and functions.

        If name=None, use thing.__name__
        """

        if name==None: name=thing.__name__
        self.extra_globals[name] = thing



    def pop_header(self, hkey):
        """
        This will remove and return the specified header value.

        You can specify either a key string or an index.
        """

        # try the integer approach first to allow negative values
        if not type(hkey) == str:
            return self.headers.pop(self.hkeys.pop(hkey))
        else:
            # find the key integer and pop it
            hkey = self.hkeys.index(hkey)

            # if we didn't find the column, quit
            if hkey < 0:
                print "Column does not exist (yes, we looked)."
                return

            # pop it!
            return self.headers.pop(self.hkeys.pop(hkey))

    def pop_column(self, ckey):
        """
        This will remove and return the data in the specified column.

        You can specify either a key string or an index.
        """

        # try the integer approach first to allow negative values
        if not type(ckey) == str:
            return self.columns.pop(self.ckeys.pop(ckey))
        else:
            # find the key integer and pop it
            ckey = self.ckeys.index(ckey)

            # if we didn't find the column, quit
            if ckey < 0:
                print "Column does not exist (yes, we looked)."
                return

            # pop it!
            return self.columns.pop(self.ckeys.pop(ckey))


    def clear_columns(self):
        """
        This will remove all the ckeys and columns.
        """
        self.ckeys   = []
        self.columns = {}


    def clear_headers(self):
        """
        This will remove all the hkeys and headers
        """
        self.hkeys    = []
        self.headers  = {}

    def clear(self):
        """
        Removes all headers and columns from the databox.
        """
        self.clear_columns()
        self.clear_headers()



    def rename_header(self, old_name, new_name):
        """
        This will rename the header. The supplied names need to be strings.
        """
        self.hkeys[self.hkeys.index(old_name)] = new_name
        self.headers[new_name] = self.headers.pop(old_name)

    def rename_column(self, old_name, new_name):
        """
        This will rename the column. The supplied names need to be strings.
        """
        self.ckeys[self.ckeys.index(old_name)] = new_name
        self.columns[new_name] = self.columns.pop(old_name)

    def update_headers(self, dictionary, keys=None):
        """
        Updates the header with the supplied dictionary. If keys=None, it
        will be unsorted. Otherwise it will loop over the supplied keys
        (a list) in order.
        """
        if keys==None: keys = dictionary.keys()
        for k in keys: self.insert_header(k, dictionary[k])





    def c(self, n):
        """
        Returns the n'th column if it's an integer, otherwis the column based
        on key.
        """
        if len(self.columns) == 0:   return []
        if type(n)           == str: return self.columns[n]
        else:                        return self.columns[self.ckeys[n]]

    __getitem__ = c

    def h(self, *args, **kwargs):
        """
        This function searches through hkeys for one *containing* a key string
        supplied by args[0] and returns that header value.

        Also can take integers, returning the key'th header value.

        kwargs can be specified to set header elements.
        """

        # first loop over kwargs if there are any to set header elements
        for k in kwargs.keys():
            self.insert_header(k, kwargs[k])

        # Meow search for a key if specified
        if len(args):
            # this can be shortened. Eventually, it'd be nice to get a tuple back!
            hkey = args[0]

            # if this is an index
            if type(hkey) in [int, long]: return self.headers[self.hkeys[hkey]]

            # if this is an exact match
            elif hkey in self.hkeys:      return self.headers[hkey]

            # Look for a fragment.
            else:
                for k in self.hkeys:
                    if k.find(hkey) >= 0:
                        return self.headers[k]
                print
                print "ERROR: Couldn't find '"+str(hkey) + "' in header."
                print "Possible values:"
                for k in self.hkeys: print k
                print
                return None




###########################################
# Class for fitting data
###########################################

class fitter():

    _f  = None    # list of functions
    _bg = None    # list of background functions (for subtracting etc)

    _f_raw  = None # raw argument passed to set_functions()
    _bg_raw = None # raw argument passed to set_functions()

    xdata  = None # internal storage of data sets
    ydata  = None
    eydata = None

    _xdata_massaged  = None # internal storage of trimmed data sets (used for fitting)
    _ydata_massaged  = None
    _eydata_massaged = None

    _settings = None   # dictionary containing all the fitter settings

    results = None  # full output from the fitter.

    def __init__(self, f=['a*x*cos(b*x)+c', 'a*x+c'], p='a=1.5, b, c=-2', c=None, bg=None, **kwargs):
        """
        Creates an object for fitting data to nonlinear curves.

        f  = function or list of functions
        p  = comma-delimited list of fit parameters
        c  = comma-delimited list of constants
        bg = optional background function or list of functions

        f, p, bg are sent to set_functions()

        **kwargs are sent to settings

        Typical workflow:
            my_fitter = fitter('a*x+b', 'a,b')      # creates the fitter object
            my_fitter.set_data([1,2,3],[1,2,1])     # sets the data to be fit
            my_fitter.fit_leastsq()                 # does the fitting
            my_fitter.plot()

        Tips:

            Do not set data directly; use set_data(), which clears the fit
            results. Otherwise the fit results will not match the existing data.

            When errors are completely unknown, try autoscale_errors_and_fit()
            repeatedly until the reduced chi squareds of all the data sets
            are approximately 1. This is one way to more-or-less estimate
            the error from the data itself.
        """

        # make sure all the awesome stuff from numpy is visible.
        self._globals  = _n.__dict__

        self._pnames    = []
        self._cnames    = []
        self._fnames    = []
        self._bgnames   = []
        self._pguess    = []
        self._constants = []

        # default settings
        self._settings = dict(autoplot      = True,     # whether we always plot when changing stuff
                              plot_fit      = True,     # include f in plots?
                              plot_bg       = False,    # include bg in plots?
                              plot_ey       = True,     # include error bars?
                              plot_guess    = True,     # include the guess?
                              subtract_bg   = True,     # subtract bg from plots?
                              fpoints       = 1000,     # number of points to use when plotting f
                              xmin          = None,     # list of truncation values
                              xmax          = None,     # list of truncation values
                              xlabel        = None,     # list of x labels
                              ylabel        = None,     # list of y labels
                              xscale        = 'linear', # axis scale type
                              yscale        = 'linear', # axis scale type
                              coarsen       = 1,        # how much to coarsen the data
                              
                              # styles of plots
                              style_data   = dict(marker='+', color='b',   ls=''),
                              style_fit    = dict(marker='',  color='r',    ls='-'),
                              style_guess  = dict(marker='',  color='0.25', ls='-'),
                              style_bg     = dict(marker='',  color='k',    ls='-'))

        # settings that don't require a re-fit
        self._safe_settings =list(['bg_names', 'fpoints', 'f_names',
                                   'plot_bg', 'plot_ey', 'plot_guess', 'plot_fit',
                                   'silent', 'style_bg', 'style_data', 'style_guess',
                                   'style_fit', 'subtract_bg', 'xscale', 'yscale',
                                   'xlabel', 'ylabel'])

        # settings that should not be lists in general (i.e. not one per data set)
        self._single_settings = list(['autoplot'])

        # set the functions
        self.set_functions(f, p, c, bg)

        # update the default settings
        for k in kwargs.keys(): self[k] = kwargs[k]


    def set(self, **kwargs):
        """
        Changes a setting or multiple settings. Can also call self() or
        change individual parameters with self['parameter'] = value
        """
        for k in kwargs.keys(): self[k] = kwargs[k]

        if self['autoplot']: self.plot()

        return self


    __call__ = set

    def __setitem__(self, key, value):

        # special case: setting a _pguess
        if key in self._pnames: self._pguess[self._pnames.index(key)] = value

        # special case: setting a _constants
        elif key in self._cnames:
            self._constants[self._cnames.index(key)] = value
            self._update_functions()

        # special case: single-valued keys
        elif key in self._single_settings:
            self._settings[key] = value

        # everything else should have a value for each data set or plot
        elif self._settings.has_key(key):

            # make sure it's a list.
            if not _s.fun.is_iterable(value) or isinstance(value, dict):
                value = [value]

            # make sure it matches the data.
            while len(value) < len(self._f): value.append(value[0])

            # set the value
            self._settings[key] = value

        # yell.
        else: self._error("'"+key+"' is not a valid setting, pname or cname.")

        # if it isn't a "safe" key, invalidate the previous fit results.
        if not key in self._safe_settings: self._clear_results()



    def __repr__(self):
        """
        prints out the current settings.
        """
        keys = self._settings.keys()
        keys.sort()

        s = "\nSETTINGS\n"
        for k in keys:
            # for the clunky style settings, loop over the list
            if k[0:5] == 'style' and _s.fun.is_iterable(self[k]):
                s = s+"  {:15s} [".format(k)
                for n in range(len(self[k])):
                    s = s+str(self[k][n])
                    if n==len(self[k])-1: s = s+"]\n"
                    else:                 s = s+"\n                   "

            else:
                s = s+"  {:15s} {:s}\n".format(k, str(self[k]))

        s = s + "\nCONSTANTS\n"
        for c in self._cnames: s = s + "  {:10s} = {:s}\n".format(c, str(self[c]))

        s = s + "\nGUESS\n"
        for p in self._pnames: s = s + "  {:10s} = {:s}\n".format(p, str(self[p]))

        if self.xdata==None: s = s + "\nNO DATA\n"

        else:
            if self.results and not self.results[1]==None:
                s = s + "\nFIT RESULTS (reduced chi squared = {:s})\n".format(str(self.reduced_chi_squareds()))
                for n in range(len(self._pnames)):
                    s = s + "  {:10s} = {:G} +/- {:G}\n".format(self._pnames[n], self.results[0][n], _n.sqrt(self.results[1][n][n]))

            elif self.results and self.results[1] == None:
                s = s + "\nFIT DID NOT CONVERGE\n"
                for n in range(len(self._pnames)):
                    s = s + "  {:10s} = {:G} (meaningless)\n".format(self._pnames[n], self.results[0][n])

            else: s = s + "\nNO FIT RESULTS\n"

        return s

    def __getitem__(self, key):
        if key in self._pnames: return self._pguess   [self._pnames.index(key)]
        if key in self._cnames: return self._constants[self._cnames.index(key)]
        return self._settings[key]

    def _error(self, message): print "ERROR: "+str(message)

    def set_functions(self,  f=['a*x*cos(b*x)+c', 'a*x+c'], p='a=1.5, b, c=-2', c=None, bg=None):
        """
        Sets the function(s) used to describe the data.

        f='a*cos(b*x)'  This can be a string function, a defined function
                        my_function(x,a,b), or a list of some combination
                        of these two types of objects. The length of such
                        a list must be equal to the number of data sets
                        supplied to the fit routine.

        p='a=1.5, b'    This must be a comma-separated string list of
                        parameters used to fit. If an initial guess value is
                        not specified, 1.0 will be used.

                        If a function object is supplied, it is assumed that
                        this string lists the parameter names in order.

        c=None          Fit _constants; like p, but won't be allowed to float
                        during the fit. This can also be None.

        bg=None         Can be functions in the same format as f describing a
                        background (which can be subtracted during fits, etc)
        """

        # initialize everything
        self._pnames    = []
        self._cnames    = []
        self._pguess    = []
        self._constants = []

        # store these for later
        self._f_raw  = f
        self._bg_raw = bg

        # break up the constant names and initial values.
        if c:
            for s in c.split(','):

                # split by '=' and see if there is an initial value
                s = s.split('=')

                # add the name to the list
                self._cnames.append(s[0].strip())

                # if there is a guess value, add this (or 1.0)
                if len(s) > 1: self._constants.append(float(s[1]))
                else:          self._constants.append(1.0)


        # break up the parameter names and initial values.
        for s in p.split(','):

            # split by '=' and see if there is an initial value
            s = s.split('=')

            # add the name to the list
            self._pnames.append(s[0].strip())

            # if there is a guess value, add this (or 1.0)
            if len(s) > 1: self._pguess.append(float(s[1]))
            else:          self._pguess.append(1.0)


        # use the internal settings we just set to create the functions
        self._update_functions()
        return self


    def _update_functions(self):
        """
        Uses internal settings to update the functions.
        """

        self._f      = []
        self._bg     = []
        self._fnames  = []
        self._bgnames = []

        f  = self._f_raw
        bg = self._bg_raw

        # make sure f and bg are lists of matching length
        if not _s.fun.is_iterable(f) : f  = [f]
        if not _s.fun.is_iterable(bg): bg = [bg]
        while len(bg) < len(f): bg.append(None)

        # get a comma-delimited string list of parameter names
        pstring = ', '.join(self._pnames)
        pstring = 'x, ' + pstring

        # update the globals for the functions
        # the way this is done, we must redefine the functions
        # every time we change a constant
        for cname in self._cnames: self._globals[cname] = self[cname]

        # loop over all the functions and create the master list
        for n in range(len(f)):

            # if f[n] is a string, define a function on the fly.
            if isinstance(f[n], str):
                self._f.append( eval('lambda ' + pstring + ': ' + f[n],  self._globals))
                self._fnames.append(f[n])
            else:
                self._f.append(f[n])
                self._fnames.append(f[n].__name__)

            # if bg[n] is a string, define a function on the fly.
            if isinstance(bg[n], str):
                self._bg.append(eval('lambda ' + pstring + ': ' + bg[n], self._globals))
                self._bgnames.append(bg[n])
            else:
                self._bg.append(bg[n])
                if bg[n] == None: self._bgnames.append("None")
                else:             self._bgnames.append(bg[n].__name__)

        # update the format of all the settings
        for k in self._settings.keys(): self[k] = self[k]

        # make sure we don't think our fit results are valid!
        self._clear_results()


    def set_data(self, xdata=[1,2,3,4,5], ydata=[[1,2,1,2,1],[3,2,3,4,3]], eydata=None, **kwargs):
        """
        This will handle the different types of supplied data and put everything
        in a standard format for processing.

        xdata, ydata      These can be a single array of data or a list of data
                            arrays. If one is an array# assemble the arguments for the function
        args = (xdata,) + tuple(p)    and the other is a list
                            of arrays, copies of the first will be made to pair
                            with the other's data. Their lengths must match.

        eydata             Error bars. These can be None (for auto error) or
                            data matching the dimensionality of xdata and ydata

        Results will be stored in self.xdata, self.ydata, self.eydata
        
        **kwargs are sent to set()
        """
        
        # warn the user
        if eydata == None:
            print "\nWARNING: Setting eydata=None (i.e. the default) results in a random guess for the error bars associated with ydata. This will allow you to fit, but results in meaningless fit errors. Please estimate your errors and supply an argument such as:\n"
            print "  eydata = 0.1"
            print "  eydata = [[0.1,0.1,0.1,0.1,0.2],[1,1,1,1,1]]\n"
        
        # make sure xdata and ydata are lists of data sets
        if not _s.fun.is_iterable(xdata[0]): xdata = [xdata]
        if not _s.fun.is_iterable(ydata[0]): ydata = [ydata]

        # make sure these lists are the same length
        while len(ydata) < len(xdata): ydata.append(ydata[0])
        while len(xdata) < len(ydata): xdata.append(xdata[0])

        # poop out if the number of ydata sets doesn't match the number of
        # functions
        if not len(ydata) == len(self._f):
            return self._error("Naughty! Number of data sets does not match the number of functions! If you want to fit many data sets simultaneously with one function, make a list of duplicated functions in set_functions().")

        # assemble the errors
        # example eydata: None, 3, [None, 3] or [None, [1,2,1,2,1]]
        # makes sure it's at least a list of the right length
        if not _s.fun.is_iterable(eydata): eydata = [eydata]*len(xdata)

        # example eydata at this point: [None, None], [3,3], [None,3] or [None, [1,2,1,2,1]]
        
        # catch the potentially ambiguous case [3,3] where this could either be "two constants"
        # or "the error bars for each data point" (assume the latter if possible)        
        if _s.fun.elements_are_numbers(eydata) and len(eydata) == len(ydata[0]):
            eydata = [_n.array(eydata)]
                
        # make sure the lengths match
        while len(eydata) < len(ydata): eydata.append(eydata[0])

        # now make sure everything is a list of numpy arrays
        for n in range(len(xdata)):

            xdata[n]  = _n.array(xdata[n]) * 1.0
            ydata[n]  = _n.array(ydata[n]) * 1.0

            # take a visually-appealing guess at the error
            if eydata[n] == None:
                eydata[n] = _n.ones(len(xdata[n])) * (max(ydata[n])-min(ydata[n]))/20.

            # use constant error bars
            elif _s.fun.is_a_number(eydata[n]): 
                eydata[n] = _n.ones(len(xdata[n])) * eydata[n]

            eydata[n] = _n.array(eydata[n]) * 1.0

        # store the data and errors internally
        self.xdata  = xdata
        self.ydata  = ydata
        self.eydata = eydata

        # reset the massaged data
        self._xdata_massaged  = xdata
        self._ydata_massaged  = ydata
        self._eydata_massaged = eydata

        # make sure we don't think our fit results are valid!
        self._clear_results()

        # update settings (need to do this last to avoid plotting no data!)
        self.set(**kwargs)

        # plot if not in silent mode
        if self['autoplot']: self.plot()

        return self

    def set_guess_to_fit(self):
        """
        If you have a fit result, set the guess parameters to the 
        fit parameters.
        """
        if self.results == None: 
            print "No fit results to use! Run fit() first."
            return
            
        # loop over the results and set the guess values
        for n in range(len(self._pguess)): self._pguess[n] = self.results[0][n]
        
        if self['autoplot']: self.plot()        
        
        return self

    def _massage_data(self):
        """
        This will trim and coarsen the data sets according to self._settings:
            coarsen = 0     # can be an integer
            xmin    = None  # can be a number
            xmax    = None  # can be a number

        Results are stored in self._xdata_massaged, ...
        """

        self._xdata_massaged  = []
        self._ydata_massaged  = []
        self._eydata_massaged = []

        N = 0 # total number of data points

        for n in range(len(self.xdata)):

            # trim the data
            if (not self['xmin'][n]==None and self['xmin'][n] > max(self.xdata[n])) \
            or (not self['xmax'][n]==None and self['xmax'][n] < min(self.xdata[n])):
                self._error("This combination of xmin, xmax, and xdata results in no trimmed data!")
                x, y, ey = _s.fun.trim_data(None, None,
                                     self.xdata[n], self.ydata[n], self.eydata[n])
            else:
                x, y, ey = _s.fun.trim_data(self['xmin'][n], self['xmax'][n],
                                     self.xdata[n], self.ydata[n], self.eydata[n])

            # coarsen the data
            if self['coarsen'][n] == 0: self['coarsen'][n] = 1
            x  =         _s.fun.coarsen_array(x,     self['coarsen'][n], 'mean')
            y  =         _s.fun.coarsen_array(y,     self['coarsen'][n], 'mean')
            ey = _n.sqrt(_s.fun.coarsen_array(ey**2, self['coarsen'][n], 'mean')/self['coarsen'][n])

            # store the result
            self. _xdata_massaged.append(x)
            self. _ydata_massaged.append(y)
            self._eydata_massaged.append(ey)

            # keep track of the number of data points
            N += len(x)



    def fit(self, pguess=None, method='leastsq', **kwargs):
        """
        This will try to determine fit parameters using scipy.optimize's leastsq
        algorithm. This function relies on a previous call of set_data()

        pguess        If None, this will set the internal guess values

        results of the fit are stored in self.results

        kwargs are sent to self.set()
        """
        if self.xdata == None or self.ydata == None:
            self._error("No data. Please use set_data() prior to fitting.")

        self.set(**kwargs)

        # massage the data
        self._massage_data()

        # set the initial values if specified
        if not pguess == None: self._pguess = pguess

        # do the actual optimization
        self.results = _opt.leastsq(self._residuals_concatenated, self._pguess, full_output=1)

        # plot if necessary
        if self['autoplot']: self.plot()

        return self

    def fix(self, pname):
        """
        Turns a parameter in to a constant.
        """
        if not pname in self._pnames:
            self._error("Naughty. '"+pname+"' is not a valid fit parameter name.")
            return

        n = self._pnames.index(pname)

        # use the fit result if it exists
        if self.results: value = self.results[0][n]

        # otherwise use the guess value
        else: value = self._pguess[n]

        # make the switcheroo
        self._pnames.pop(n)
        self._pguess.pop(n)
        self._constants.append(value)
        self._cnames.append(pname)

        # update
        self._update_functions()

        return self

    def free(self, cname):
        """
        Turns a constant into a parameter.
        """
        if not cname in self._cnames:
            self._error("Naughty. '"+cname+"' is not a valid constant name.")
            return

        n = self._cnames.index(cname)

        # make the switcheroo
        self._pnames.append(self._cnames.pop(n))
        self._pguess.append(self._constants.pop(n))

        # update
        self._update_functions()

        return self

    def _clear_results(self):
        """
        Removes any fit results that may be lingering.
        """
        self.results = None

    def _evaluate_all_functions(self, xdata, p=None):
        """
        This returns a list of function outputs given the stored data sets.
        This function relies on a previous call of set_data().

        p=None means use the fit results
        """
        if p==None: p = self.results[0]

        output = []
        for n in range(len(self._f)):
            output.append(self._evaluate_f(n, self._xdata_massaged[n], p) )

        return output

    def _evaluate_f(self, n, xdata, p=None):
        """
        Evaluates a single function n for arbitrary xdata and p.

        p=None means use the fit results
        """
        if p==None: p = self.results[0]

        # assemble the arguments for the function
        args = (xdata,) + tuple(p)

        # evaluate this function.
        return self._f[n](*args)

    def _evaluate_bg(self, n, xdata, p=None):
        """
        Evaluates a single background function n for arbitrary xdata and p.

        p=None means use the fit results
        """
        if p==None: p = self.results[0]

        # evaluate this function.
        if self._bg[n] == None: return None

        # assemble the arguments for the function
        args = (xdata,) + tuple(p)
        return self._bg[n](*args)

    def _residuals(self, p=None):
        """
        This function returns a list of vectors of the differences between the
        model and ydata_massaged, scaled by the error. This function relies
        on a previous call to set_data().

        p=None means use the fit results
        """
        if p==None:
            if not self.results:
                self._error("Can't call _residuals(None) without a fit result.")
                return
            p = self.results[0]

        # evaluate the function for all the data, returns a list!
        f = self._evaluate_all_functions(self._xdata_massaged, p)

        # get the full residuals list
        r = []
        for n in range(len(f)):
            r.append((self._ydata_massaged[n]-f[n]) / _n.absolute(self._eydata_massaged[n]))
        return r

    def _residuals_concatenated(self, p=None):
        """
        This function returns a big long list of residuals so leastsq() knows
        what to do with it. This function relies on a previous call to set_data()

        p=None means use the fit results
        """
        if p==None: p = self.results[0]
        return _n.concatenate(self._residuals(p))

    def _chi_squareds(self, p=None):
        """
        returns a list of chi squared for each data set. Also uses ydata_massaged.

        p=None means use the fit results
        """
        if p==None: p = self.results[0]

        # get the residuals
        rs = self._residuals(p)

        # square em and sum em.
        cs = []
        for r in rs: cs.append(sum(r**2))
        return cs

    def reduced_chi_squared(self,p=None):
        """
        returns the reduced chi squared given p.

        p=None means use the fit results.
        """
        r = self._residuals_concatenated(p)
        return sum(r**2) / (len(r)-len(self._pnames))

    def reduced_chi_squareds(self, p=None):
        """
        Returns the reduced chi squared for each data set. Degrees of freedom
        of each data point are reduced.

        p=None means use the fit results.
        """
        if p==None: p = self.results[0]
        r = self._residuals(p)

        # degrees of freedom
        dof_per_point = 1.0*(_n.size(r)-len(self._pnames))/_n.size(r)

        for n in range(len(r)):
            r[n] = sum(r[n]**2)/(len(r[n])*dof_per_point)

        return r

    def autoscale_eydata(self):
        """
        Rescales the error so the next fit will give reduced chi squareds of 1.

        Each data set will be scaled independently.
        """
        if not self.results:
            self._error("You must complete a fit first.")

        r = self.reduced_chi_squareds()

        # loop over the eydata and rescale
        for n in range(len(r)):
            self.eydata[n] = self.eydata[n] * _n.sqrt(r[n])

        # the fit is no longer valid
        self._clear_results()

        # replot
        if self['autoplot']: self.plot()

        return self

    def autoscale_eydata_and_fit(self):
        """
        Shortcut to

        self.autoscale_eydata()
        self.fit_leastsq(_pguess=self.results[0])
        """
        if not self.results:
            self._error("You must complete a fit first.")
            return

        # use the fit as a guess
        self._pguess = self.results[0]

        self.autoscale_eydata()
        self.fit(pguess=self._pguess)
        return self

    def plot(self, **kwargs):
        """
        This will plot the data (with error) for inspection.

        kwargs will update the settings
        """
        if self.xdata == None or self.ydata == None:
            self._error("No data. Please use set_data() prior to plotting.")
            return

        # update settings
        for k in kwargs: self[k] = kwargs[k]

        # update the massaged data
        self._massage_data()

        # turn off interactive mode
        _p.ioff()

        # get the residuals
        r = None
        if not self.results==None: r = self._residuals(self.results[0])

        # make a new plot for each data set
        for n in range(len(self.xdata)):

            # get the next figure
            fig = _p.figure(n)
            fig.clear()

            # set up two axes. One for data and one for residuals.
            a1 = _p.subplot(211)
            a2 = _p.subplot(212, sharex=a1)
            a1.set_position([0.15, 0.75, 0.75, 0.15])
            a2.set_position([0.15, 0.15, 0.75, 0.55])

            # set the scales
            a1.set_xscale(self['xscale'][n])
            a1.set_yscale(self['yscale'][n])
            a2.set_xscale(self['xscale'][n])
            a2.set_yscale(self['yscale'][n])

            # get the xdata for the curves
            if self['fpoints'][n] == None:
                x = self._xdata_massaged[n]
            else:
                # do exponential ranging if xscale is log
                if self['xscale'][n] == 'log':
                    x = _n.logspace(_n.log10(min(self._xdata_massaged[n])),
                                    _n.log10(max(self._xdata_massaged[n])),
                                    self['fpoints'][n], True, 10.0)

                # otherwise do linear spacing                
                else:                
                    x = _n.linspace(min(self._xdata_massaged[n]),
                                    max(self._xdata_massaged[n]),
                                    self['fpoints'][n])

            # get the thing to subtract from ydata
            if self['subtract_bg'] and not self._bg[n]==None:

                # if we have a fit, use that.
                if self.results:
                    dy_data = self._evaluate_bg(n, self._xdata_massaged, self.results[0])
                    dy_func = self._evaluate_bg(n, x,                    self.results[0])

                # otherwise, use the _pguess background
                else:
                    dy_data = self._evaluate_bg(n, self._xdata_massaged, self._pguess)
                    dy_func = self._evaluate_bg(n, x,                    self._pguess)
            else:
                dy_data = 0*self._xdata_massaged[n]
                dy_func = 0*x


            # add the data to the plot
            if self['plot_ey'][n]:
                a2.errorbar(self._xdata_massaged[n],
                            self._ydata_massaged[n]-dy_data,
                            self._eydata_massaged[n],
                            **self['style_data'][n])
            else:
                a2.plot(    self._xdata_massaged[n],
                            self.ydata_massage[n]-dy_data,
                            **self['style_data'][n])

            # set the plot range according to just the data
            _s.tweaks.auto_zoom(axes=a2, draw=False)
            a2.set_autoscale_on(False)

            # add the _pguess curves
            if self['plot_guess'][n]:

                # plot the _pguess background curve
                if self['plot_bg'][n]:
                    a2.plot(x, self._evaluate_bg(n,x,self._pguess)-dy_func, **self['style_guess'][n])

                # plot the _pguess main curve
                a2.plot(x, self._evaluate_f(n,x,self._pguess)-dy_func, **self['style_guess'][n])

            # add the fit curves (if we have a fit)
            if self['plot_fit'] and self.results:

                # plot the background curve
                if self['plot_bg'][n]:
                    a2.plot(x, self._evaluate_bg(n,x,self.results[0])-dy_func, **self['style_fit'][n])

                # plot the pfit main curve
                a2.plot(x, self._evaluate_f(n,x,self.results[0])-dy_func, **self['style_fit'][n])

            a2.set_autoscale_on(True)

            # plot the residuals
            if not r==None:
                a1.errorbar(self._xdata_massaged[n], r[n], _n.ones(len(r[n])), **self['style_data'][n])
                a1.plot([min(self._xdata_massaged[n]),max(self._xdata_massaged[n])],[0,0], **self['style_fit'][n])
                _s.tweaks.auto_zoom(axes=a1, draw=False)

            # tidy up
            if self['xlabel'][n] == None: _p.xlabel('xdata['+str(n)+']')
            else:                         _p.xlabel(self['xlabel'][n])
            if self['ylabel'][n] == None: _p.ylabel('ydata['+str(n)+']')
            else:                         _p.ylabel(self['ylabel'][n])
            a1.set_ylabel('residuals')

            # Assemble the title
            wrap = 80
            indent = '      '
            t = _textwrap.fill('Function ('+str(n)+'/'+str(len(self.ydata)-1)+'): y = '+self._fnames[n], wrap, subsequent_indent=indent)

            if len(self._cnames):
                t1 = "Constants: "
                for i in range(len(self._cnames)):
                    t1 = t1 + self._cnames[i] + "={:G}, ".format(self._constants[i])
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            if self.results and not self.results[1]==None:
                t1 = "Fit: "
                for i in range(len(self._pnames)):
                    t1 = t1 + self._pnames[i] + "={:G}$\pm${:G}, ".format(self.results[0][i], _n.sqrt(self.results[1][i][i]))
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            elif self.results:
                t1 = "Fit did not converge: "
                for i in range(len(self._pnames)):
                    t1 = t1 + self._pnames[i] + "={:8G}$, "
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            a1.set_title(t, fontsize=10, ha='left', position=(0,1))


        # turn back to interactive and show the plots.
        _p.ion()
        _p.draw()
        _p.show()

        # for some reason, it's necessary to touch every figure, too
        for n in range(len(self.xdata)-1,-1,-1): _p.figure(n)

        return self

    def trim(self, n='all'):
        """
        This will set xmin and xmax based on the current zoom-level of the
        figures.

        n='all'     Which figure to use for setting xmin and xmax.
                    'all' means all figures. You may also specify a list.
        """
        if self.xdata == None or self.ydata == None:
            self._error("No data. Please use set_data() and plot() prior to trimming.")
            return


        if   _s.fun.is_a_number(n): n = [n]
        elif isinstance(n,str):   n = range(len(self.xdata))

        # loop over the specified plots
        for i in n:
            try:
                xmin, xmax = _p.figure(i).axes[1].get_xlim()
                self['xmin'][i] = xmin
                self['xmax'][i] = xmax
            except:
                self._error("Data "+str(i)+" is not currently plotted.")

        # now show the update.
        self._clear_results()
        if self['autoplot']: self.plot()

        return self

    def zoom(self, n='all', factor=2.0):
        """
        This will scale the x range of the chosen plot.

        n='all'     Which figure to zoom out. 'all' means all figures, or
                    you can specify a list.
        """
        if self.xdata == None or self.ydata == None:
            self._error("No data. Please use set_data() and plot() prior to zooming.")
            return

        if   _s.fun.is_a_number(n): n = [n]
        elif isinstance(n,str):   n = range(len(self.xdata))

        # loop over the specified plots
        for i in n:
            try:
                xmin, xmax = _p.figure(i).axes[1].get_xlim()
                xc = 0.5*(xmin+xmax)
                xs = 0.5*abs(xmax-xmin)
                self['xmin'][i] = xc - factor*xs
                self['xmax'][i] = xc + factor*xs
            except:
                self._error("Data "+str(i)+" is not currently plotted.")

        # now show the update.
        self._clear_results()
        if self['autoplot']: self.plot()

        return self

    def ginput(self, figure_number=0, **kwargs):
        """
        Pops up the n'th figure and lets you click it. Returns value from pylab.ginput().

        args and kwargs are sent to pylab.ginput()
        """
        _s.tweaks.raise_figure_window(figure_number)
        return _p.ginput(**kwargs)



############################
# Dialogs for loading data
############################

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

    if not quiet: print "\nloaded", d.path, "\n"

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
