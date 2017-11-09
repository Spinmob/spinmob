import os      as _os
import sys     as _sys
import shutil  as _shutil

# do this so all the scripts will work with all the numpy functions
import numpy          as _n
import scipy.optimize as _opt
import pylab          as _p
import textwrap       as _textwrap
import spinmob        as _s
import time           as _time










#############################################################
# Class for storing / manipulating / saving / loading data
#############################################################

class databox:
    """
    An object to hold, save, and load columns of data and header information.
    
    Parameters
    ----------
    delimiter    
        The delimiter the file uses. None (default) means "Try to figure it out" (reasonably smart)
    debug        
        Displays some partial debug information while running

    Additional optional keyword arguments are sent to self.h()
    """
    
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



    def __init__(self, delimiter=None, debug=False, **kwargs):
        
        # this keeps the dictionaries from getting all jumbled with each other
        self.clear_columns()
        self.clear_headers()

        self.debug     = debug
        self.delimiter = delimiter

    def __setitem__(self, n, x):
        """
        set's the n'th column to x (n can be a column name too)
        """
        if type(n) is str:
            self.insert_column(data_array=x, ckey=n, index=None)

        elif type(n) in [int, int] and n > len(self.ckeys)-1:
            self.insert_column(data_array=x, ckey='_column'+str(len(self.ckeys)), index=None)

        else:
            self.columns[self.ckeys[n]] = _n.array(x)

    def __len__(self):
        return len(self.ckeys)

 
    def __repr__(self):

        s = "<databox instance: "+str(len(self.hkeys))+" headers, "+str(len(self.ckeys))+" columns>"
        return s

    def more_info(self):
        """
        Prints out more information about the databox.
        """
        print("\nDatabox Instance", self.path)
        print("\nHeader")
        for h in self.hkeys: print("  "+h+":", self.h(h))
        s = "\nColumns ("+str(len(self.ckeys))+"): "
        for c in self.ckeys: s = s+c+", "
        print(s[:-2])


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

    def load_file(self, path='ask', first_data_line='auto', filters='*.*', text='Select a file, FACEPANTS.', default_directory=None, header_only=False, quiet=False):
        """
        This will clear the databox, load a file, storing the header info in 
        self.headers, and the data in self.columns

        If first_data_line="auto", then the first data line is assumed to be 
        the first line where all the elements are numbers.

        If you specify a first_data_line (index, starting at 0), the columns 
        need not be numbers. Everything above will be considered header 
        information and below will be data columns.

        In both cases, the line used to label the columns will always be the 
        last header line with the same (or more) number of elements as the 
        first data line.
        
        Parameters
        ----------
        path='ask'
            Path to the file. Using 'ask' will bring up a dialog.
        filters='*.*'            
            Filter for the file dialog (if path isn't specified)
        text='Select a file, FACEPANTS.'               
            Prompt on file dialog
        default_directory=None
            Which spinmob.settings key to use for the dialog's default 
            directory. Will create one if it doesn't already exist.
        header_only=False        
            Only load the header
        quiet=False              
            Don't print anything while loading.
        """
        
        if default_directory is None: default_directory = self.directory

        if path == "ask":
            path = _s.dialogs.open_single(filters=filters,
                                        default_directory=self.directory,
                                        text=text)
        self.path = path

        if path is None:
            if not quiet: print("Aborted.")
            return None

        # make sure the file exists!
        if not _os.path.exists(path):
            if not quiet: print("ERROR: "+repr(path)+" does not exist.")
            return None

        # clear all the existing data
        self.clear()

        # open said file for reading, read in all the lines and close
        f = open(path, 'r')
        lines = f.readlines()
        f.close()

        # Determine the delimiter
        if self.delimiter is None:

            # loop from the end of the file until we get something other than white space
            for n in range(len(lines)):

                # strip away the white space
                s = lines[-n-1].strip()

                # if this line has any content
                if len(s) > 0:

                    # try the different delimiter schemes until we find one
                    # that produces a number. Otherwise it's ambiguous.
                    if   _s.fun.is_a_number(s.split(None)[0]): self.delimiter = None
                    elif _s.fun.is_a_number(s.split(',') [0]): self.delimiter = ','
                    elif _s.fun.is_a_number(s.split(';') [0]): self.delimiter = ';'

                    # quit the loop!
                    break



        ##### read in the header information
        self.header_lines = []

        for n in range(len(lines)):

            # split the line by the delimiter
            s = lines[n].strip().split(self.delimiter)

            # remove a trailing whitespace entry if it exists.
            if len(s) and s[-1].strip() == '': s.pop(-1)

            # first check and see if this is a data line (all elements are numbers)
            if first_data_line == "auto" and _s.fun.elements_are_numbers(s):

                # we've reached the first data line
                first_data_line = n

                # quit the header loop
                break;

            ### now we know it's a header line

            # save the lines for the avid user.
            self.header_lines.append(lines[n].strip())

            # store the hkey and the rest of it
            if len(s):
                hkey      = s[0]
                if self.delimiter is None: remainder = ' '.join(s[1:])
                else:                      remainder = self.delimiter.join(s[1:])

                # first thing to try is simply evaluating the remaining string
                try: self.insert_header(hkey, eval(remainder, self._globals()))

                # otherwise store the string
                except: self.insert_header(hkey, remainder)

        # now we have a valid set of column ckeys one way or another, and we know first_data_line.
        if header_only: return self

        # Make sure first_data_line isn't None (which happens if there's no data)
        if first_data_line == "auto":
            if not quiet: print("\nCould not find a line of pure data! Perhaps check the delimiter?")
            if not quiet: print("The default delimiter is whitespace. For csv files, set delimiter=','\n")
            return self



        ##### at this point we've found the first_data_line,

        # look for the ckeys

        # special case: no header
        if first_data_line == 0: ckeys = []

        # start by assuming it's the previous line
        else: ckeys = lines[first_data_line-1].strip().split(self.delimiter)

        # count the number of actual data columns for comparison
        column_count = len(lines[first_data_line].strip().split(self.delimiter))

        # check to see if ckeys is equal in length to the
        # number of data columns. If it isn't, it's a false ckeys line
        if len(ckeys) >= column_count:
            # it is close enough
            # if we have too many column keys, mention it
            while len(ckeys) > column_count:
                extra = ckeys.pop(-1)
                if not quiet: print("Extra ckey: "+extra)

        else:
            # it is an invalid ckeys line. Generate our own!
            ckeys = []
            for m in range(0, column_count): ckeys.append("c"+str(m))

        # last step with ckeys: make sure they're all different!
        self.ckeys = []
        while len(ckeys):

            # remove the key
            ckey = ckeys.pop(0)

            # if there is a duplicate
            if (ckey in ckeys) or (ckey in self.ckeys):
                # increase the label index until it's unique
                n=0
                while (ckey+"_"+str(n) in ckeys) or (ckey+"_"+str(n) in self.ckeys): n+=1
                ckey = ckey+"_"+str(n)
            self.ckeys.append(ckey)

        # initialize the columns arrays
        # I did benchmarks and there's not much improvement by using numpy-arrays here.
        for label in self.ckeys: self.columns[label] = []

        
        
        
        
        
        
        
        # define a quick function to convert i's to j's
        if _sys.version_info[0] >= 3:
            def fix(x): return bytearray(x.replace('i','j'), encoding='utf-8') 
        else:
            def fix(x): return str(x.replace('i','j'))
        
        # loop over the remaining data lines, converting to numbers
        #return lines[first_data_line:]
        z = _n.genfromtxt((fix(x) for x in lines[first_data_line:]),
                          delimiter=self.delimiter,
                          dtype=_n.complex)
        
        
        
        
        
        
        # genfromtxt returns a 1D array if there is only one data line.
        # highly confusing behavior, numpy!
        if len(_n.shape(z)) == 1:
            # check to make sure the data file contains only 1 column of data
            rows_of_data = len(lines) - first_data_line
            if rows_of_data == 1: z = _n.array([z])
            else: z = _n.array(z)

        # fix for different behavior of genfromtxt on single columns
        if len(z.shape) == 2: z = z.transpose()
        else:                 z = [z]

        # Add all the columns
        for n in range(len(self.ckeys)):

            # if any of the imaginary components are non-zero, use complex
            if _n.any(_n.imag(z[n])): self[n] = z[n]
            else:                     self[n] = _n.real(z[n])

        # now, as an added bonus, rename some of the obnoxious headers
        for k in self.obnoxious_ckeys:
            if k in self.columns:
                self.columns[self.obnoxious_ckeys[k]] = self.columns[k]

        return self

    def save_file(self, path='ask', filters='*.dat', force_overwrite=False, header_only=False, delimiter='use current'):
        """
        This will save all the header info and columns to an ascii file with
        the specified path.

        Parameters
        ----------
        filters='*.dat'         
            File filter for the file dialog (for path="ask")
        force_overwrite=False   
            Normally, if the file * exists, this will copy that
            to *.backup. If the backup already exists, this
            function will abort. Setting this to True will
            force overwriting the backup file.
        header_only=False       
            Only output the header?
        delimiter='use current' 
            This will set the delimiter of the output file
            'use current' means use self.delimiter
        """
        
        # Make sure there isn't a problem later with no-column databoxes
        if len(self)==0: header_only=True

        # This is the final path. We now write to a temporary file in the user
        # directory, then move it to the destination. This (hopefully) fixes
        # problems with sync programs.
        if path == "ask": path = _s.dialogs.save(filters, default_directory=self.directory)
        if path in ["", None]:
            print("Aborted.")
            return False

        # Save the path for future reference
        self.path=path

        # if the path exists, make a backup
        if _os.path.exists(path) and not force_overwrite:
            _os.rename(path,path+".backup")

        # get the delimiter
        if delimiter == "use current":
            if self.delimiter is None: delimiter = "\t"
            else:                      delimiter = self.delimiter

        # figure out the temporary path
        temporary_path = _os.path.join(_s.settings.path_home, "temp-"+str(int(1e3*_time.time()))+'-'+str(int(1e9*_n.random.rand(1))))

        # open the file and write the header
        f = open(temporary_path, 'w')
        for k in self.hkeys: f.write(k + delimiter + repr(self.headers[k]) + "\n")
        f.write('\n')

        # if we're only supposed to write the header
        if not header_only: 
            
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

        # now move it
        _shutil.move(temporary_path, path)

        return self

    def get_data_point(self, n):
        """
        Returns the n'th data point (starting at 0) from all columns.

        Parameters
        ----------
        n       
            Index of data point to return.
        """
        # loop over the columns and pop the data
        point = []
        for k in self.ckeys: point.append(self[k][n])
        return point


    def pop_data_point(self, n):
        """
        This will remove and return the n'th data point (starting at 0) from
        all columns.

        Parameters
        ----------
        n       
            Index of data point to pop.
        """

        # loop over the columns and pop the data
        popped = []
        for k in self.ckeys:

            # first convert to a list
            data = list(self.c(k))

            # pop the data
            popped.append(data.pop(n))

            # now set this column again
            self.insert_column(_n.array(data), k)

        return popped

    def insert_data_point(self, new_data, index=None):
        """
        Inserts a data point at index n.
        
        Parameters
        ----------
        new_data    
            A list or array of new data points, one for each column.
        index       
            Where to insert the point(s) in each column. None => append.
        """

        if not len(new_data) == len(self.columns) and not len(self.columns)==0:
            print("ERROR: new_data must have as many elements as there are columns.")
            return

        # otherwise, we just auto-add this data point as new columns
        elif len(self.columns)==0:
            for i in range(len(new_data)): self[i] = [new_data[i]]

        # otherwise it matches length so just insert it.
        else:
            for i in range(len(new_data)):

                # get the array and turn it into a list
                data = list(self[i])

                # append or insert
                if index is None: data.append(       new_data[i])
                else:             data.insert(index, new_data[i])

                # reconvert to an array
                self[i] = _n.array(data)
        
        return self

    def append_data_point(self, new_data):
        """
        Appends the supplied data point to the column(s).

        Parameters
        ----------
        new_data    
            A list or array of new data points, one for each column.
        """
        return self.insert_data_point(new_data)

    def execute_script(self, script, g=None):
        """
        Runs a script, returning the result.

        Parameters
        ----------
        script
            String script to be evaluated (see below).
        g=None
            Optional dictionary of additional globals for the script evaluation.
            These will automatically be inserted into self.extra_globals.

        Usage
        -----
        Scripts are of the form:

        "3.0 + x/y - d[0] where x=3.0*c('my_column')+h('setting'); y=d[1]"

        By default, "d" refers to the databox object itself, giving access to 
        everything and enabling complete control over the universe. Meanwhile, 
        c() and h() give quick reference to d.c() and d.h() to get columns and 
        header lines. Additionally, these scripts can see all of the numpy 
        functions like sin, cos, sqrt, etc.

        If you would like access to additional globals in a script,
        there are a few options in addition to specifying the g parametres. 
        You can set self.extra_globals to the appropriate globals dictionary 
        or add globals using self.insert_global(). Setting g=globals() will 
        automatically insert all of your current globals into this databox 
        instance.

        There are a few shorthand scripts available as well. You can simply type
        a column name such as 'my_column' or a column number like 2. However, I
        only added this functionality as a shortcut, and something like
        "2.0*a where a=my_column" will not work unless 'my_column is otherwise
        defined. I figure since you're already writing a complicated script in 
        that case, you don't want to accidentally shortcut your way into using 
        a column instead of a constant! Use "2.0*a where a=c('my_column')" 
        instead.
        """

        # add any extra user-supplied global variables for the eventual eval() call.
        if not g==None: self.extra_globals.update(g)

        # If the script is not a list of scripts, return the script value.
        # This is the termination of a recursive call.
        if not _s.fun.is_iterable(script):

            # special case
            if script is None: return None

            # get the expression and variables dictionary
            [expression, v] = self._parse_script(script)

            # if there was a problem parsing the script
            if v is None:
                print("ERROR: Could not parse '"+script+"'")
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
            print("This script ran recursively 1000 times!")
            a = input("<enter> or (q)uit: ")
            if a.strip().lower() in ['q', 'quit']:
                script = None

        if script is None: return [None, None]

        # check if the script is simply an integer
        if type(script) in [int,int]:
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
        if len(split_script) is 1:
            if self.debug: print("script of length 1")

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
                print()
                print("ERROR: Could not evaluate '"+str(script)+"'")
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
                print(s, "has no '=' in it")
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
            if y is None: return [None, None]

            stuff[v] = y[x]

        # at this point we've found or generated the list
        return [expression, stuff]



    def copy_headers(self, other_databox):
        """
        Loops over the hkeys of the other_databox, updating this databoxes' header.
        """
        for k in other_databox.hkeys: self.insert_header(k, other_databox.h(k))

        return self

    def copy_columns(self, other_databox):
        """
        Loops over the ckeys of the other_databox, updating this databoxes' columns.
        """
        for k in other_databox.ckeys: self.insert_column(other_databox[k], k)

        return self
    
    def copy_all(self, other_databox):
        """
        Copies the header and columns from other_databox to this databox.
        """
        self.copy_headers(other_databox)
        self.copy_columns(other_databox)
        return self
    
    def insert_globals(self, *args, **kwargs):
        """
        Appends or overwrites the supplied object in the self.extra_globals.

        Use this to expose execute_script() or _parse_script() etc... to external
        objects and functions.

        Regular arguments are assumed to have a __name__ attribute (as is the
        case for functions) to use as the key, and keyword arguments will just 
        be added as dictionary elements.
        """
        for a in args: kwargs[a.__name__] = a
        self.extra_globals.update(kwargs)

    def insert_header(self, hkey, value, index=None):
        """
        This will insert/overwrite a value to the header and hkeys.

        Parameters
        ----------
        hkey
            Header key. Will be appended to self.hkeys if non existent, or 
            inserted at the specified index. 
            If hkey is an integer, uses self.hkeys[hkey].
        value
            Value of the header.
        index=None
            If specified (integer), hkey will be inserted at this location in 
            self.hkeys.
            
        """
        #if hkey is '': return

        # if it's an integer, use the hkey from the list
        if type(hkey) in [int, int]: hkey = self.hkeys[hkey]

        # set the data
        self.headers[str(hkey)] = value
        if not hkey in self.hkeys:
            if index is None: self.hkeys.append(str(hkey))
            else:             self.hkeys.insert(index, str(hkey))
        return self

    def pop_header(self, hkey):
        """
        This will remove and return the specified header value.

        You can specify either a key string or an index.
        """

        # try the integer approach first to allow negative values
        if type(hkey) is not str:
            return self.headers.pop(self.hkeys.pop(hkey))
        else:
            # find the key integer and pop it
            hkey = self.hkeys.index(hkey)

            # if we didn't find the column, quit
            if hkey < 0:
                print("Column does not exist (yes, we looked).")
                return

            # pop it!
            return self.headers.pop(self.hkeys.pop(hkey))

    def pop_column(self, ckey):
        """
        This will remove and return the data in the specified column.

        You can specify either a key string or an index.
        """

        # try the integer approach first to allow negative values
        if type(ckey) is not str:
            return self.columns.pop(self.ckeys.pop(ckey))
        else:
            # find the key integer and pop it
            ckey = self.ckeys.index(ckey)

            # if we didn't find the column, quit
            if ckey < 0:
                print("Column does not exist (yes, we looked).")
                return

            # pop it!
            return self.columns.pop(self.ckeys.pop(ckey))

    def insert_column(self, data_array, ckey='temp', index=None):
        """
        This will insert/overwrite a new column and fill it with the data from the
        the supplied array.
        
        Parameters
        ----------
        data_array  
            Data; can be a list, but will be converted to numpy array
        ckey        
            Name of the column; if an integer is supplied, uses self.ckeys[ckey]
        index       
            Where to insert this column. None => append to end.
        """

        # if it's an integer, use the ckey from the list
        if type(ckey) in [int, int]: ckey = self.ckeys[ckey]

        # append/overwrite the column value
        self.columns[ckey] = _n.array(data_array)
        if not ckey in self.ckeys:
            if index is None: self.ckeys.append(ckey)
            else:             self.ckeys.insert(index, ckey)
        
        return self

    def append_column(self, data_array, ckey='temp'):
        """
        This will append a new column and fill it with the data from the
        the supplied array.
        
        Parameters
        ----------
        data_array  
            Data; can be a list, but will be converted to numpy array
        ckey        
            Name of the column.
        """
        if not type(ckey) is str:
            print("ERROR: ckey should be a string!")
            return

        if ckey in self.ckeys:
            print("ERROR: ckey '"+ckey+"' already exists!")
            return

        return self.insert_column(data_array, ckey)

    def clear_columns(self):
        """
        This will remove all the ckeys and columns.
        """
        self.ckeys   = []
        self.columns = {}
        return self

    def clear_headers(self):
        """
        This will remove all the hkeys and headers
        """
        self.hkeys    = []
        self.headers  = {}
        return self

    def clear(self):
        """
        Removes all headers and columns from the databox.
        """
        self.clear_columns()
        self.clear_headers()
        return self

    def rename_header(self, old_name, new_name):
        """
        This will rename the header. The supplied names need to be strings.
        """
        self.hkeys[self.hkeys.index(old_name)] = new_name
        self.headers[new_name] = self.headers.pop(old_name)
        return self

    def rename_column(self, column, new_name):
        """
        This will rename the column.
        The supplied column can be an integer or the old column name.
        """
        if type(column) is not str: column = self.ckeys[column]
        self.ckeys[self.ckeys.index(column)] = new_name
        self.columns[new_name] = self.columns.pop(column)
        return self

    def trim(self, *conditions):
        """
        Removes data points not satisfying the supplied conditions. Conditions
        can be truth arrays (having the same length as the columns!)
        or scripted strings.

        Example Workflow
        ----------------
        d1 = spinmob.data.load()
        d2 = d1.trim( (2<d1[0]) & (d1[0]<10) | (d1[3]==22), 'sin(d[2])*h("gain")<32.2')

        Note this will not modify the databox, rather it will generate a new
        one with the same header information and return it.
        """
        conditions = list(conditions)

        # if necessary, evaluate string scripts
        for n in range(len(conditions)):
            if type(conditions[n]) is str:
                conditions[n] = self.execute_script(conditions[n])

        # make a new databox with the same options and headers
        new_databox = databox(delimiter=self.delimiter)
        new_databox.copy_headers(self)

        # trim it up, send it out.
        cs = _s.fun.trim_data_uber(self, conditions)
        for n in range(len(cs)): new_databox.append_column(cs[n], self.ckeys[n])

        return new_databox

    def transpose(self):
        """
        Returns a copy of this databox with the columns as rows.
        
        Currently requires that the databox has equal-length columns.
        """
        # Create an empty databox with the same headers and delimiter.
        d = databox(delimter=self.delimiter)
        self.copy_headers(d)
        
        # Get the transpose
        z = _n.array(self[:]).transpose()
        
        # Build the columns of the new databox
        for n in range(len(z)): d['c'+str(n)] = z[n]
        
        return d
        

    def update_headers(self, dictionary, keys=None):
        """
        Updates the header with the supplied dictionary. If keys=None, it
        will be unsorted. Otherwise it will loop over the supplied keys
        (a list) in order.
        """
        if keys is None: keys = list(dictionary.keys())
        for k in keys: self.insert_header(k, dictionary[k])
        return self




    def c(self, n):
        """
        Returns the n'th column if it's an integer, otherwise the column based
        on key.
        """
        # Nothing to do here.
        if len(self.columns) == 0:   return None
        
        # if it's a string, use it as a key for the dictionary
        if type(n)   is str: return self.columns[n]

        # if it's a list, return the specified columns
        if type(n) in [list, tuple, range]:
            output = []
            for i in n: output.append(self[i])
            return output

        # If it's a slice, do the slice thing
        if type(n) is slice:
            start = n.start
            stop  = n.stop
            step  = n.step
            
            # Fix up the unspecifieds
            if start == None: start = 0
            if stop  == None: stop  = len(self)
            if step  == None: step  = 1
            
            # Return what was asked for
            return self[range(start, stop, step)]
            
        # Otherwise assume it's an integer
        return self.columns[self.ckeys[n]]

    __getitem__ = c

    def h(self, *args, **kwargs):
        """
        This function searches through hkeys for one *containing* a key string
        supplied by args[0] and returns that header value.

        Also can take integers, returning the key'th header value.

        kwargs can be specified to set header elements.
        """

        # first loop over kwargs if there are any to set header elements
        for k in list(kwargs.keys()):
            self.insert_header(k, kwargs[k])

        # Meow search for a key if specified
        if len(args):
            # this can be shortened. Eventually, it'd be nice to get a tuple back!
            hkey = args[0]

            # if this is an index
            if type(hkey) in [int, int]: return self.headers[self.hkeys[hkey]]

            # if this is an exact match
            elif hkey in self.hkeys:      return self.headers[hkey]

            # Look for a fragment.
            else:
                for k in self.hkeys:
                    if k.find(hkey) >= 0:
                        return self.headers[k]
                print()
                print("ERROR: Couldn't find '"+str(hkey) + "' in header.")
                print("Possible values:")
                for k in self.hkeys: print(k)
                print()
                return None




###########################################
# Class for fitting data
###########################################

class fitter():
    """
    Creates an object for fitting data to functions.

    Parameters
    ----------
    f = ['a*x*cos(b*x)+c', 'a*x+c']
        function or list of functions
    p = 'a=1.5, b, c=-2'
        comma-delimited list of fit parameters (and optional guess values)
    c = None 
        comma-delimited list of constants (and values), following the format
        of 'p' above
    bg = None
        optional background function or list of functions, following the format
        of 'f' above
    g = None
        optional globals dictionary used when for evaluating string functions

    f, p, bg are sent to set_functions()

    **kwargs are sent to settings

    Typical workflow
    ----------------
    my_fitter = fitter('a*x+b', 'a,b')    
        creates the fitter object
    my_fitter.set_data([1,2,3],[1,2,1])   
        sets the data to be fit
    my_fitter.fit()                       
        does the fitting
    my_fitter.results 
        contains the output of scipy.leastsq.optimize (see scipy docs)
        

    Tips
    ----
    Usage
        All methods starting without an underscore are meant to be used
        by a "typical" user. For example, do not set data directly; 
        use set_data(), which clears the fit results. Otherwise the fit 
        results will not match the existing data.
        
    See the spinmob wiki on github!
    """
    
    
    f  = None    # list of functions
    bg = None    # list of background functions (for subtracting etc)

    _f_raw  = None # raw argument passed to set_functions()
    _bg_raw = None # raw argument passed to set_functions()

    _set_xdata  = None # definitions from which data is derived during fits
    _set_ydata  = None
    _set_eydata = None
    _set_data_globals = dict(_n.__dict__) # defaults to numpy

    _xdata_massaged  = None # internal storage of trimmed data sets (used for fitting)
    _ydata_massaged  = None
    _eydata_massaged = None

    _settings = None   # dictionary containing all the fitter settings

    results = None  # full output from the fitter.

    def __init__(self, f=['a*x*cos(b*x)+c', 'a*x+c'], p='a=1.5, b, c=-2', c=None, bg=None, g=None, **kwargs):

        # make sure all the awesome stuff from numpy is visible.
        self._globals  = _n.__dict__

        # update the globals dictionary
        if not g is None: self._globals.update(g)

        self._pnames    = []
        self._cnames    = []
        self._fnames    = []
        self._bgnames   = []
        self._pguess    = []
        self._constants = []

        # default settings
        self._settings = dict(autoplot      = True,     # whether we always plot when changing stuff
                              plot_all_data = False,    # whether to plot only the trimmed data
                              plot_fit      = True,     # include f in plots?
                              plot_bg       = True,     # include bg in plots?
                              plot_ey       = True,     # include error bars?
                              plot_guess    = True,     # include the guess?
                              plot_guess_zoom = False,  # zoom to include plot?
                              subtract_bg   = False,    # subtract bg from plots?
                              first_figure  = 0,        # first figure number to use
                              fpoints       = 1000,     # number of points to use when plotting f
                              xmin          = None,     # list of limits for trimming x-data
                              xmax          = None,     # list of limits for trimming x-data
                              ymin          = None,     # list of limits for trimming y-data
                              ymax          = None,     # list of limits for trimming y-data
                              xlabel        = None,     # list of x labels
                              ylabel        = None,     # list of y labels
                              xscale        = 'linear', # axis scale type
                              yscale        = 'linear', # axis scale type
                              scale_eydata  = 1.0,      # by how much should we scale the eydata?
                              coarsen       = 1,        # how much to coarsen the data

                              # styles of plots
                              style_data   = dict(marker='+', color='b',   ls=''),
                              style_fit    = dict(marker='',  color='r',    ls='-'),
                              style_guess  = dict(marker='',  color='0.25', ls='-'),
                              style_bg     = dict(marker='',  color='k',    ls='-'))

        # Silence warnings
        self._settings['silent'] = False

        # settings that don't require a re-fit
        self._safe_settings =list(['bg_names', 'fpoints', 'f_names', 'plot_all_data',
                                   'plot_bg', 'plot_ey', 'plot_guess', 'plot_fit',
                                   'silent', 'style_bg', 'style_data', 'style_guess',
                                   'style_fit', 'subtract_bg', 'xscale', 'yscale',
                                   'xlabel', 'ylabel'])

        # settings that should not be lists in general (i.e. not one per data set)
        self._single_settings = list(['autoplot', 'first_figure'])

        # set the functions
        self.set_functions(f, p, c, bg)

        # update the default settings
        for k in list(kwargs.keys()): self[k] = kwargs[k]


    def set(self, **kwargs):
        """
        Changes a setting or multiple settings. Can also call self() or
        change individual parameters with self['parameter'] = value
        """
        for k in list(kwargs.keys()): self[k] = kwargs[k]

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
        elif key in self._settings:

            # make sure it's a list.
            if not _s.fun.is_iterable(value) or isinstance(value, dict):
                value = [value]

            # make sure it matches the data.
            while len(value) < len(self.f): value.append(value[0])

            # set the value
            self._settings[key] = value

        # yell.
        else: self._error("'"+key+"' is not a valid setting, pname or cname.")

        # if it isn't a "safe" key, invalidate the previous fit results.
        if not key in self._safe_settings: self.clear_results()



    def __repr__(self):
        """
        prints out the current settings.
        """
        keys = list(self._settings.keys())
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

        if self._set_xdata is None or self._set_ydata is None: 
            s = s + "\nGUESS\n"
        else:
            s = s + "\nGUESS (reduced chi^2 = {:s}, {:d} DOF)\n".format(
                self._format_value_error(self.reduced_chi_squared(self._pguess), _n.sqrt(2.0/self.degrees_of_freedom())), 
                        int(self.degrees_of_freedom()))
        for p in self._pnames: s = s + "  {:10s} = {:s}\n".format(p, str(self[p]))


        # If we have no data, don't print fit stuff.
        if self._set_xdata is None or self._set_ydata is None: s = s + "\nNO DATA\n"

        else:
            if self.results and not self.results[1] is None:
                s = s + "\nFIT RESULTS (reduced chi^2 = {:s}, {:d} DOF)\n".format(
                        self._format_value_error(self.reduced_chi_squared(), _n.sqrt(2.0/self.degrees_of_freedom())), 
                        int(self.degrees_of_freedom()))
                for n in range(len(self._pnames)):
                    s = s + "  {:10s} = {:s}\n".format(self._pnames[n], self._format_value_error(self.results[0][n], _n.sqrt(self.results[1][n][n])))

            elif self.results and self.results[1] is None:
                s = s + "\nFIT DID NOT CONVERGE\n"
                for n in range(len(self._pnames)):
                    s = s + "  {:10s} = {:G} (meaningless)\n".format(self._pnames[n], self.results[0][n])

            else: s = s + "\nNO FIT RESULTS\n"

        return s

    def print_fit_parameters(self):
        """
        Just prints them out in a way that's easy to copy / paste.
        """
        s = ''
        if self.results and self.results[1] is not None:
            s = s + "\n# FIT RESULTS (reduced chi squared = {:s})\n".format(str(self.reduced_chi_squareds()))
            for n in range(len(self._pnames)):
                s = s + "{:10s} = {:G}\n".format(self._pnames[n], self.results[0][n])

        elif self.results and self.results[1] is None:
            s = s + "\n# FIT DID NOT CONVERGE\n"
            for n in range(len(self._pnames)):
                s = s + "{:10s} = {:G}\n".format(self._pnames[n], self.results[0][n])

        else: s = s + "\n# NO FIT RESULTS\n"

        print(s)

    def __getitem__(self, key):
        if key in self._pnames: return self._pguess   [self._pnames.index(key)]
        if key in self._cnames: return self._constants[self._cnames.index(key)]
        return self._settings[key]

    def _error(self, message): print("ERROR: "+str(message))

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

        self.f      = []
        self.bg     = []
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
                self.f.append( eval('lambda ' + pstring + ': ' + f[n],  self._globals))
                self._fnames.append(f[n])
            else:
                self.f.append(f[n])
                self._fnames.append(f[n].__name__)

            # if bg[n] is a string, define a function on the fly.
            if isinstance(bg[n], str):
                self.bg.append(eval('lambda ' + pstring + ': ' + bg[n], self._globals))
                self._bgnames.append(bg[n])
            else:
                self.bg.append(bg[n])
                if bg[n] is None: self._bgnames.append("None")
                else:             self._bgnames.append(bg[n].__name__)

        # update the format of all the settings
        for k in list(self._settings.keys()): self[k] = self[k]

        # make sure we don't think our fit results are valid!
        self.clear_results()


    def set_data(self, xdata=[1,2,3,4,5], ydata=[[1,2,1,2,1],[3,2,3,4,3]], eydata=None, **kwargs):
        """
        This will handle the different types of supplied data and put everything
        in a standard format for processing.

        xdata, ydata    These can be a single array of data or a list of data
                        arrays.

        eydata          Error bars. These can be None (for guessed error) or
                        data / numbers matching the dimensionality of xdata
                        and ydata

        xdata, ydata, and eydata can all be scripts or lists of scripts that
        produce arrays. Any python code will work, and the scripts
        automatically know about all numpy functions, the guessed parameters,
        and the data itself (as x, y, and ey). However, the scripts are
        executed in order -- xdata, ydata, and eydata -- so the xdata script
        cannot know about ydata or eydata, the ydata script cannot know about
        eydata, and the eydata script knows about xdata and ydata.

        Example:
          xdata  = [1,2,3,4,5]
          ydata  = [[1,2,1,2,1], 'cos(x[0])']
          eydata = ['arctan(y[1])*a+b', 5]

        In this example, there will be two data sets to fit (so there better be
        two functions!), they will share the same xdata, the second ydata set
        will be the array cos([1,2,3,4,5]) (note since there are multiple data
        sets assumed (always), you have to select the data set with an index
        on x and y), the error on the first data set will be this weird
        functional dependence on the second ydata set and fit parameters a and
        b (note, if a and b are not fit parameters, then you must
        send them as keyword arguments so that they are defined) and the second
        data set error bar will be a constant, 5.

        Note this function is "somewhat" smart about reshaping the input
        data to ease life a bit, but it can't handle ambiguities. If you
        want to play it safe, supply lists for all three arguments that
        match in dimensionality.

        results can be obtained by calling get_data()

        **kwargs are added to the globals for script evaluation
        """
        self._eydata_warning(eydata)

        # xdata and ydata   'script', [1,2,3], [[1,2,3],'script'], ['script', [1,2,3]]
        # eydata            'script', [1,1,1], [[1,1,1],'script'], ['script', [1,1,1]], 3, [3,[1,2,3]], None

        # if xdata, ydata, or eydata are bare scripts, make them into lists
        if type(xdata)  is str: xdata  = [xdata]
        if type(ydata)  is str: ydata  = [ydata]
        if type(eydata) is str or _s.fun.is_a_number(eydata) or eydata is None: eydata = [eydata]

        # xdata and ydata   ['script'], [1,2,3], [[1,2,3],'script'], ['script', [1,2,3]]
        # eydata            ['script'], [1,1,1], [[1,1,1],'script'], ['script', [1,1,1]], [3], [3,[1,2,3]], [None]

        # if the first element of data is a number, then this is a normal array
        if _s.fun.is_a_number(xdata[0]): xdata = [xdata]
        if _s.fun.is_a_number(ydata[0]): ydata = [ydata]

        # xdata and ydata   ['script'], [[1,2,3]], [[1,2,3],'script'], ['script', [1,2,3]]
        # eydata            ['script'], [1,1,1],   [[1,1,1],'script'], ['script', [1,1,1]], [3], [3,[1,2,3]], [None]

        # if the first element of eydata is a number, this could also just be an error bar value
        # Note: there is some ambiguity here, if the number of data sets equals the number of data points!
        if _s.fun.is_a_number(eydata[0]) and len(eydata) == len(ydata[0]): eydata = [eydata]

        # xdata and ydata   ['script'], [[1,2,3]], [[1,2,3],'script'], ['script', [1,2,3]]
        # eydata            ['script'], [[1,1,1]], [[1,1,1],'script'], ['script', [1,1,1]], [3], [3,[1,2,3]], [None]

        # make sure these lists are the same length as the number of functions
        while len(ydata)  < len(self.f): ydata.append(ydata[0])
        while len(xdata)  < len(self.f): xdata.append(xdata[0])
        while len(eydata) < len(self.f): eydata.append(eydata[0])

        # xdata and ydata   ['script','script'], [[1,2,3],[1,2,3]], [[1,2,3],'script'], ['script', [1,2,3]]
        # eydata            ['script','script'], [[1,1,1],[1,1,1]], [[1,1,1],'script'], ['script', [1,1,1]], [3,3], [3,[1,2,3]], [None,None]

        # poop out if the number of ydata sets doesn't match the number of
        # functions
        if not len(ydata) == len(self.f):
            return self._error("Naughty! Number of data sets does not match the number of functions!")

        # store the data, script, or whatever it is!
        self._set_xdata  = xdata
        self._set_ydata  = ydata
        self._set_eydata = eydata
        self._set_data_globals.update(kwargs)

        # set the eyscale to 1 for each data set
        self['scale_eydata'] = [1.0]*len(self._set_xdata)

        if self['autoplot']: self.plot()
        
        return self

    def _eydata_warning(self, eydata):
        """
        Warning if eydata is None.

        This warning is suppressed if self._safe_settings['silent'] is True.
        """
        if self._settings['silent'][0] is True:
            pass
        elif eydata is None:
            print("\nWARNING: Setting eydata=None (i.e. the default) results in a random guess for the error bars associated with ydata. This will allow you to fit, but results in meaningless fit errors. Please estimate your errors and supply an argument such as:\n")
            print("  eydata = 0.1")
            print("  eydata = [[0.1,0.1,0.1,0.1,0.2],[1,1,1,1,1]]\n")

    def evaluate_script(self, script, **kwargs):
        """
        Evaluates the supplied script (python-executable string).
        Useful for testing your scripts!

        globals already include all of numpy objects plus

        self = self
        f    = self.f
        bg   = self.bg

        and all the current guess parameters and constants

        kwargs are added to globals for script evaluation.
        """
        self._set_data_globals.update(kwargs)
        return eval(script, self._set_data_globals)

    def get_data(self):
        """
        Returns current xdata, ydata, eydata, after set_data() has been run.
        """
        # make sure we've done a "set data" call
        if self._set_xdata is None or self._set_ydata is None:
            print("\nERROR: You must call set_data() first!")
            return

        # update the globals with the current fit parameters guess values
        for n in range(len(self._pnames)): self._set_data_globals[self._pnames[n]] = self._pguess[n]
        for n in range(len(self._cnames)): self._set_data_globals[self._cnames[n]] = self._constants[n]

        # update the globals with x, y, and ey, and the functions
        self._set_data_globals['f']    = self.f
        self._set_data_globals['bg']   = self.bg
        self._set_data_globals['self'] = self

        # possibilities after calling set_data():
        # xdata and ydata   ['script','script'], [[1,2,3],[1,2,3]], [[1,2,3],'script'], ['script', [1,2,3]]
        # eydata            ['script','script'], [[1,1,1],[1,1,1]], [[1,1,1],'script'], ['script', [1,1,1]], [3,3], [3,[1,2,3]], [None,None]

        # make a copy
        xdata  = list(self._set_xdata)
        ydata  = list(self._set_ydata)
        eydata = list(self._set_eydata)

        # make sure they're all lists of numpy arrays
        for n in range(len(xdata)):

            # For xdata, handle scripts or arrays
            if type(xdata[n]) is str: xdata[n] = self.evaluate_script(xdata[n])
            else:                     xdata[n] = _n.array(xdata[n])*1.0

        # update the globals
        self._set_data_globals['x'] = xdata

        # make sure they're all lists of numpy arrays
        for n in range(len(ydata)):

            # For ydata, handle scripts or arrays
            if type(ydata[n]) is str: ydata[n] = self.evaluate_script(ydata[n])
            else:                     ydata[n] = _n.array(ydata[n])*1.0

        # update the globals
        self._set_data_globals['y'] = ydata

        # make sure they're all lists of numpy arrays
        for n in range(len(eydata)):

            # handle scripts
            if type(eydata[n]) is str:
                eydata[n] = self.evaluate_script(eydata[n])

            # handle None (possibly returned by script): take a visually-appealing guess at the error
            if eydata[n] is None:
                eydata[n] = _n.ones(len(xdata[n])) * (max(ydata[n])-min(ydata[n]))*0.05

            # handle constant error bars (possibly returned by script)
            if _s.fun.is_a_number(eydata[n]):
                eydata[n] = _n.ones(len(xdata[n])) * eydata[n]

            # make it an array
            eydata[n] = _n.array(eydata[n]) * self["scale_eydata"][n]

        # return it
        return xdata, ydata, eydata

    def set_guess_to_fit_result(self):
        """
        If you have a fit result, set the guess parameters to the
        fit parameters.
        """
        if self.results is None:
            print("No fit results to use! Run fit() first.")
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
            ymin    = None  # can be a number
            ymax    = None  # can be a number

        Results are stored in self._xdata_massaged, ...
        """

        # get the data
        xdata, ydata, eydata = self.get_data()

        self._xdata_massaged  = []
        self._ydata_massaged  = []
        self._eydata_massaged = []

        # get the trim limits (trimits)
        xmins = self['xmin']
        xmaxs = self['xmax']
        ymins = self['ymin']
        ymaxs = self['ymax']

        # make sure we have one limit for each data set
        if type(xmins) is not list: xmins = [xmins]*len(xdata)
        if type(xmaxs) is not list: xmaxs = [xmaxs]*len(xdata)
        if type(ymins) is not list: ymins = [ymins]*len(xdata)
        if type(ymaxs) is not list: ymaxs = [ymaxs]*len(xdata)

        # this should cover all the data sets (dimensions should match!)
        for n in range(len(xdata)):

            # handle "None" limits
            if xmins[n] is None: xmins[n] = min(xdata[n])
            if xmaxs[n] is None: xmaxs[n] = max(xdata[n])
            if ymins[n] is None: ymins[n] = min(ydata[n])
            if ymaxs[n] is None: ymaxs[n] = max(ydata[n])

            # trim the data
            [x, y, ey] = _s.fun.trim_data_uber([xdata[n], ydata[n], eydata[n]],
                                               [xdata[n]>=xmins[n], xdata[n]<=xmaxs[n],
                                                ydata[n]>=ymins[n], ydata[n]<=ymaxs[n]])
            if(len(x)==0):
                print("\nDATA SET "+str(n)+": OOPS! OOPS! Specified limits (xmin, xmax, ymin, ymax) eliminate all data! Ignoring.")
                x  = xdata[n]
                y  = ydata[n]
                ey = eydata[n]

            # coarsen the data
            if self['coarsen'][n] == 0: self['coarsen'][n] = 1
            x  =         _s.fun.coarsen_array(x,     self['coarsen'][n], 'mean')
            y  =         _s.fun.coarsen_array(y,     self['coarsen'][n], 'mean')
            ey = _n.sqrt(_s.fun.coarsen_array(ey**2, self['coarsen'][n], 'mean')/self['coarsen'][n])

            # store the result
            self. _xdata_massaged.append(x)
            self. _ydata_massaged.append(y)
            self._eydata_massaged.append(ey)



    def fit(self, pguess=None, **kwargs):
        """
        This will try to determine fit parameters using scipy.optimize's leastsq
        algorithm. This function relies on a previous call of set_data()

        pguess        If None, this will set the internal guess values

        results of the fit are stored in self.results

        kwargs are sent to self.set()
        """
        if self._set_xdata is None:
            return self._error("No data. Please use set_data() prior to fitting.")

        # zero-checking doesn't handle all error types
        #if (_n.array(self._eydata_massaged)==0).any():
        #if (_n.concatenate(self._eydata_massaged)==0).any():
        #    return self._error("One or more of your error bars is zero! Are you trying to make me divide by zero? Answer the question.")

        self.set(**kwargs)

        # massage the data
        self._massage_data()

        # set the initial values if specified
        if pguess is not None: self._pguess = pguess

        # do the actual optimization
        self.results = _opt.leastsq(self._studentized_residuals_concatenated, self._pguess, full_output=1)

        # plot if necessary
        if self['autoplot']: self.plot()

        return self

    def fix(self, *args, **kwargs):
        """
        Turns parameters to constants. As arguments, parameters must be strings.
        As keyword arguments, they can be set at the same time.
        """

        # first set all the keyword argument values
        self.set(**kwargs)

        # get everything into one big list
        pnames = list(args) + list(kwargs.keys())

        # move each pname to the constants
        for pname in pnames:
            if not pname in self._pnames:
                self._error("Naughty. '"+pname+"' is not a valid fit parameter name.")

            else:
                n = self._pnames.index(pname)

                # use the fit result if it exists
                if self.results: value = self.results[0][n]

                # otherwise use the guess value
                else: value = self._pguess[n]

                # make the switcheroo
                if type(self._pnames)    is not list: self._pnames    = list(self._pnames)
                if type(self._pguess)    is not list: self._pguess    = list(self._pguess)
                if type(self._cnames)    is not list: self._cnames    = list(self._cnames)
                if type(self._constants) is not list: self._constants = list(self._constants)
                self._pnames.pop(n)
                self._pguess.pop(n)
                self._cnames.append(pname)
                self._constants.append(value)

                # update
                self._update_functions()

        return self

    def free(self, *args, **kwargs):
        """
        Turns a constant into a parameter. As arguments, parameters must be strings.
        As keyword arguments, they can be set at the same time.
        """
        # first set all the keyword argument values
        self.set(**kwargs)

        # get everything into one big list
        cnames = list(args) + list(kwargs.keys())

        # move each pname to the constants
        for cname in cnames:

            if not cname in self._cnames:
                self._error("Naughty. '"+cname+"' is not a valid constant name.")

            else:
                n = self._cnames.index(cname)

                # make the switcheroo
                if type(self._pnames)    is not list: self._pnames    = list(self._pnames)
                if type(self._pguess)    is not list: self._pguess    = list(self._pguess)
                if type(self._cnames)    is not list: self._cnames    = list(self._cnames)
                if type(self._constants) is not list: self._constants = list(self._constants)
                self._pnames.append(self._cnames.pop(n))
                self._pguess.append(self._constants.pop(n))

                # update
                self._update_functions()

        return self

    def clear_results(self):
        """
        Removes any fit results.
        """
        self.results = None

    def _evaluate_all_functions(self, xdata, p=None):
        """
        This returns a list of function outputs given the stored data sets.
        This function relies on a previous call of set_data().

        p=None means use the fit results
        """
        if p is None: p = self.results[0]

        output = []
        for n in range(len(self.f)):
            output.append(self._evaluate_f(n, self._xdata_massaged[n], p) )

        return output

    def _evaluate_f(self, n, xdata, p=None):
        """
        Evaluates a single function n for arbitrary xdata and p tuple.

        p=None means use the fit results
        """
        # by default, use the fit values, otherwise, use the guess values.
        if   p is None and self.results is not None: p = self.results[0]
        elif p is None and self.results is None:     p = self._pguess

        # assemble the arguments for the function
        args = (xdata,) + tuple(p)

        # evaluate this function.
        return self.f[n](*args)

    def _evaluate_bg(self, n, xdata, p=None):
        """
        Evaluates a single background function n for arbitrary xdata and p tuple.

        p=None means use the fit results
        """
        # by default, use the fit values, otherwise, use the guess values.
        if   p is None and self.results is not None: p = self.results[0]
        elif p is None and self.results is None:     p = self._pguess

        # return None if there is no background function
        if self.bg[n] is None: return None

        # assemble the arguments for the function
        args = (xdata,) + tuple(p)

        # evaluate the function
        return self.bg[n](*args)
    
    def _format_value_error(self, v, e, pm=" +/- "):
        """
        Returns a string v +/- e with the right number of sig figs.
        """
        if _n.isnan(e) or _n.isinf(e): sig_figs = 1
        else:           sig_figs = -int(_n.floor(_n.log10(abs(e))))+1
        return str(_n.round(v, sig_figs)) + pm + str(_n.round(e, sig_figs))
        
    def studentized_residuals(self, p=None):
        """
        Returns a list of studentized residuals, (ydata - model)/error

        This function relies on a previous call to set_data().

        p=None means use the fit results; if no fit, use guess results.
        """
        if self._xdata_massaged is None or self._ydata_massaged is None: return
        
        if p is None:
            if self.results: p = self.results[0]
            else:            p = self._pguess

        # evaluate the function for all the data, returns a list!
        f = self._evaluate_all_functions(self._xdata_massaged, p)

        # get the full residuals list
        residuals = []
        for n in range(len(f)):
            numerator = self._ydata_massaged[n]-f[n]
            denominator = _n.absolute(self._eydata_massaged[n])
            residuals.append(numerator/denominator)
        return residuals

    def _studentized_residuals_concatenated(self, p=None):
        """
        This function returns a big long list of residuals so leastsq() knows
        what to do with it. This function relies on a previous call to set_data()

        p=None means use the fit results
        """
        if p is None: p = self.results[0]
        return _n.concatenate(self.studentized_residuals(p))

    def chi_squareds(self, p=None):
        """
        Returns a list of chi squared for each data set. Also uses ydata_massaged.

        p=None means use the fit results
        """
        if self._set_xdata == None or self._set_ydata == None: return None
        
        if p is None: p = self.results[0]

        # get the residuals
        rs = self.studentized_residuals(p)

        # square em and sum em.
        cs = []
        for r in rs: cs.append(sum(r**2))
        return cs

    def chi_squared(self, p=None):
        """
        Returns the total chi squared (summed over all massaged data sets).
        
        p=None means use the fit results.
        """
        return sum(self.chi_squareds(p))

    def degrees_of_freedom(self):
        """
        Returns the number of degrees of freedom.
        """
        if self._set_xdata == None or self._set_ydata == None: return None
        
        # Temporary hack: get the studentized residuals, which uses the massaged data
        # This should later be changed to get_massaged_data()
        r = self.studentized_residuals()
        
        # calculate the number of points
        N = 0.0
        for i in range(len(r)): N += len(r[i])
        
        return N-len(self._pnames)
        
        

    def reduced_chi_squareds(self, p=None):
        """
        Returns the reduced chi squared for each massaged data set. 

        p=None means use the fit results.
        """
        if self._set_xdata == None or self._set_ydata == None: return None

        if p is None: p = self.results[0]
        r = self.studentized_residuals(p)
        
        # In case it's not possible to calculate
        if r is None: return

        # calculate the number of points
        N = 0
        for i in range(len(r)): N += len(r[i])

        # degrees of freedom
        dof_per_point = self.degrees_of_freedom()/N

        for n in range(len(r)):
            r[n] = sum(r[n]**2)/(len(r[n])*dof_per_point)

        return r

    def reduced_chi_squared(self, p=None):
        """
        Returns the reduced chi squared for all massaged data sets. 

        p=None means use the fit results.
        """
        
        if self._set_xdata == None or self._set_ydata == None: return None
        if p is None: p = self.results[0]
        
        return _n.divide(self.chi_squared(p), self.degrees_of_freedom())

    def autoscale_eydata(self):
        """
        Rescales the error so the next fit will give reduced chi squareds of 1.

        Each data set will be scaled independently.
        """
        if not self.results:
            self._error("You must complete a fit first.")
            return

        r = self.reduced_chi_squareds()

        # loop over the eydata and rescale
        for n in range(len(r)): self["scale_eydata"][n] *= _n.sqrt(r[n])

        # the fit is no longer valid
        self.clear_results()

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
        if self._set_xdata is None or self._set_ydata is None:
            return self._error("No data. Please use set_data() prior to plotting.")

        # get the data
        xdatas, ydatas, eydatas = self.get_data()

        # update settings
        for k in kwargs: self[k] = kwargs[k]

        # update the massaged data
        self._massage_data()


        # get the residuals
        r = None
        if not self.results is None: r = self.studentized_residuals(self.results[0])

        # otherwise get the guess residuals
        else:                        r = self.studentized_residuals(self._pguess)

        # make a new plot for each data set
        for n in range(len(xdatas)):

            # get the next figure
            fig = _p.figure(self['first_figure']+n)

            # turn off interactive mode
            _p.ioff()

            fig.clear()

            # set up two axes. One for data and one for residuals.
            a1 = _p.subplot(211)            # Residuals
            a2 = _p.subplot(212, sharex=a1) # Data
            a1.set_position([0.15, 0.72, 0.75, 0.15])
            a2.set_position([0.15, 0.10, 0.75, 0.60])

            # set the scales
            a1.set_xscale(self['xscale'][n])
            a2.set_xscale(self['xscale'][n])
            a2.set_yscale(self['yscale'][n])

            # Use all of the data to plot
            if self['plot_all_data']: 
                xdata  = xdatas[n]
                ydata  = ydatas[n]
                eydata = eydatas[n]
                
            # Use only the trimmed / massaged data
            else:
                xdata  = self._xdata_massaged[n]
                ydata  = self._ydata_massaged[n]
                eydata = self._eydata_massaged[n]
            

            # Get the xdata for plotting the function
            xt, xf = self._get_xdata_for_function(n=n)
            
            # get the thing to subtract from ydata
            if self['subtract_bg'][n] and not self.bg[n] is None:

                # if we have a fit, use that.
                if self.results:
                    dy_data = self._evaluate_bg(n, xdata, self.results[0])
                    dy_func = self._evaluate_bg(n, xt,    self.results[0])

                # otherwise, use the _pguess background
                else:
                    dy_data = self._evaluate_bg(n, xdata, self._pguess)
                    dy_func = self._evaluate_bg(n, xt,    self._pguess)
            
            # If we have no background defined, dy is zero.
            else:
                dy_data = 0*xdata
                dy_func = 0*xt

            # add the data to the plot
            if self['plot_ey'][n]:
                a2.errorbar(xdata,
                            ydata-dy_data,
                            eydata,
                            **self['style_data'][n])
            else:
                a2.plot(    xdata,
                            ydata-dy_data,
                            **self['style_data'][n])

            # set the plot range according to just the data
            _s.tweaks.auto_zoom(axes=a2, draw=False)
            a2.set_autoscale_on(False)

            # add the _pguess curves
            y_guess = self._evaluate_f(n,xt,self._pguess)-dy_func
            if self['plot_guess'][n]:

                # plot the _pguess background curve
                if self['plot_bg'][n] and self.bg[n] is not None:
                    a2.plot(xt, self._evaluate_bg(n,xt,self._pguess)-dy_func, **self['style_guess'][n])

                # plot the _pguess main curve
                a2.plot(xt, y_guess, **self['style_guess'][n])

            # add the fit curves (if we have a fit)
            if self['plot_fit'] and self.results:

                # plot the background curve
                if self['plot_bg'][n] and self.bg[n] is not None:
                    a2.plot(xt, self._evaluate_bg(n,xt,self.results[0])-dy_func, **self['style_fit'][n])

                # plot the pfit main curve
                a2.plot(xt, self._evaluate_f(n,xt,self.results[0])-dy_func, **self['style_fit'][n])

            a2.set_autoscale_on(True)

            # plot the residuals
            if self.results is not None:
                a1.errorbar(self._xdata_massaged[n], r[n], _n.ones(len(r[n])),             **self['style_data'][n])
                a1.plot([min(self._xdata_massaged[n]),max(self._xdata_massaged[n])],[0,0], **self['style_fit'][n])
                _s.tweaks.auto_zoom(axes=a1, draw=False)

            # otherwise plot the guess residuals
            elif self['plot_guess'][n]:
                a1.errorbar(self._xdata_massaged[n], r[n], _n.ones(len(r[n])),             **self['style_data'][n])
                a1.plot([min(self._xdata_massaged[n]),max(self._xdata_massaged[n])],[0,0], **self['style_guess'][n])
                _s.tweaks.auto_zoom(axes=a1, draw=False)

                
            # Tidy up
            yticklabels = a1.get_yticklabels()
            for m in range(2,len(yticklabels)-2): yticklabels[m].set_visible(False)
            for m in a1.get_xticklabels(): m.set_visible(False)
            
            # Add labels to the axes
            if self['xlabel'][n] is None: _p.xlabel('xdata['+str(n)+']')
            else:                         _p.xlabel(self['xlabel'][n])
            if self['ylabel'][n] is None:
                ylabel='ydata['+str(n)+']'
                if self['subtract_bg'][n] and self.bg[n] is not None:
                    ylabel=ylabel+' - bg['+str(n)+']'
                _p.ylabel(ylabel)
            else:                         _p.ylabel(self['ylabel'][n])
            a1.set_ylabel('Studentized\nResiduals')

            # Assemble the title
            wrap = 80
            indent = '      '
            t = _textwrap.fill('Function ('+str(n)+'/'+str(len(self._fnames)-1)+'): y = '+self._fnames[n], wrap, subsequent_indent=indent)

            if len(self._cnames):
                t1 = "Constants: "
                for i in range(len(self._cnames)):
                    t1 = t1 + self._cnames[i] + "={:G}, ".format(self._constants[i])
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            if self.results and not self.results[1] is None:
                t1 = "Fit: "
                for i in range(len(self._pnames)):
                    t1 = t1 + self._pnames[i] + "={:s}, ".format(self._format_value_error(self.results[0][i], _n.sqrt(self.results[1][i][i]), '$\pm$'))
                t1 = t1 + '$\chi^2_r$={} ({} DOF)'.format(
                        self._format_value_error(self.reduced_chi_squared(), _n.sqrt(_n.divide(2.0,self.degrees_of_freedom())), '$\pm$'), 
                        int(self.degrees_of_freedom()))
                
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            elif self.results:
                t1 = "Fit did not converge: "
                for i in range(len(self._pnames)):
                    t1 = t1 + self._pnames[i] + "={:8G}$, "
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            a1.set_title(t, fontsize=10, ha='left', position=(0,1))

            # if we're supposed to plot the guess and zoom to include it
            if self['plot_guess_zoom'][n]:
                ymin, ymax = a2.get_ylim()
                a2.set_ylim(min(ymin,min(y_guess)),
                            max(ymax,max(y_guess)))


            # turn back to interactive and show the plots.
            _p.ion()
            _p.draw()
            _p.show()

        # for some reason, it's necessary to touch every figure, too
        for n in range(len(xdatas)-1,-1,-1): _p.figure(self['first_figure']+n)

        return self

    def _get_xdata_for_function(self, n):
        """
        Generates the x-data for plotting the function.
        
        Parameters
        ----------
        n
            Which data set?

        Returns
        -------
        float
        """
        
        # Figure out which data set to use
        xdata_trim = self._xdata_massaged[n]
        if self['plot_all_data']: xdata_full = self.get_data()[0][n]
        else:                     xdata_full = xdata_trim
        
        # Use the xdata itself for the function
        if self['fpoints'][n] in [None, 0]: 
            return _n.array(xdata_trim), _n.array(xdata_full)
            
        # Otherwise, generate xdata with the number of fpoints
        
        # do exponential ranging if xscale is log
        if self['xscale'][n] == 'log':
            xf = _n.logspace(_n.log10(min(xdata_full)), _n.log10(max(xdata_full)),
                             self['fpoints'][n], True, 10.0)
        
        # otherwise do linear spacing
        else:
            xf = _n.linspace(min(xdata_full), max(xdata_full), self['fpoints'][n])
    
        # Get the trimmed data
        xt = _s.fun.trim_data_uber([xf], [xf>=min(xdata_trim), xf<=max(xdata_trim)])[0]
        
        return xt, xf

    def trim(self, n='all', x=True, y=True):
        """
        This will set xmin and xmax based on the current zoom-level of the
        figures.

        n='all'     Which figure to use for setting xmin and xmax.
                    'all' means all figures. You may also specify a list.
        x=True      Trim the x-range
        y=True      Trim the y-range
        """
        if self._set_xdata is None or self._set_ydata is None:
            self._error("No data. Please use set_data() and plot() prior to trimming.")
            return

        # get the data
        xdata, ydata, eydata = self.get_data()

        if _s.fun.is_a_number(n): n = [n]
        elif isinstance(n,str):   n = list(range(len(xdata)))

        # loop over the specified plots
        for i in n:
            try:
                if x:
                    xmin, xmax = _p.figure(self['first_figure']+i).axes[1].get_xlim()
                    self['xmin'][i] = xmin
                    self['xmax'][i] = xmax

                if y:
                    ymin, ymax = _p.figure(self['first_figure']+i).axes[1].get_ylim()
                    self['ymin'][i] = ymin
                    self['ymax'][i] = ymax

            except:
                self._error("Data "+str(i)+" is not currently plotted.")

        # now show the update.
        self.clear_results()
        if self['autoplot']: self.plot()

        return self

    def zoom(self, n='all', xfactor=2.0, yfactor=1.0):
        """
        This will scale the chosen data set's plot range by the
        specified xfactor and yfactor, respectively, and set the trim limits
        xmin, xmax, ymin, ymax accordingly

        n='all'     Which figure to zoom out. 'all' means all figures, or
                    you can specify a list.
        """
        if self._set_xdata is None or self._set_ydata is None:
            self._error("No data. Please use set_data() and plot() prior to zooming.")
            return

        # get the data
        xdata, ydata, eydata = self.get_data()

        if   _s.fun.is_a_number(n): n = [n]
        elif isinstance(n,str):     n = list(range(len(xdata)))

        # loop over the specified plots
        for i in n:
            try:
                xmin, xmax = _p.figure(self['first_figure]']+i).axes[1].get_xlim()
                xc = 0.5*(xmin+xmax)
                xs = 0.5*abs(xmax-xmin)
                self['xmin'][i] = xc - xfactor*xs
                self['xmax'][i] = xc + xfactor*xs

                ymin, ymax = _p.figure(self['first_figure]']+i).axes[1].get_ylim()
                yc = 0.5*(ymin+ymax)
                ys = 0.5*abs(ymax-ymin)
                self['ymin'][i] = yc - yfactor*ys
                self['ymax'][i] = yc + yfactor*ys
            except:
                self._error("Data "+str(i)+" is not currently plotted.")

        # now show the update.
        self.clear_results()
        if self['autoplot']: self.plot()

        return self


    def ginput(self, data_set=0, **kwargs):
        """
        Pops up the figure for the specified data set.

        Returns value from pylab.ginput().

        kwargs are sent to pylab.ginput()
        """
        # this will temporarily fix the deprecation warning
        import warnings
        import matplotlib.cbook
        warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

        _s.tweaks.raise_figure_window(data_set+self['first_figure'])
        return _p.ginput(**kwargs)



############################
# Dialogs for loading data
############################

def load(path='ask', first_data_line='auto', filters='*.*', text='Select a file, FACEHEAD.', default_directory='default_directory', quiet=True, header_only=False, transpose=False, **kwargs):
    """
    Loads a data file into the databox data class. Returns the data object.

    Most keyword arguments are sent to databox.load() so check there
    for documentation.(if their function isn't obvious).

    Parameters
    ----------
    path='ask'
        Supply a path to a data file; "ask" means pop up a dialog.
    first_data_line="auto"
        Specify the index of the first data line, or have it figure this out
        automatically.
    filters="*.*"
        Specify file filters.
    text="Select a file, FACEHEAD."
        Window title text.
    default_directory="default_directory"
        Which directory to start in (by key). This lives in spinmob.settings.
    quiet=True
        Don't print stuff while loading.
    header_only=False
        Load only the header information.
    transpose = False    
        Return databox.transpose().

    Additioinal optional keyword arguments are sent to spinmob.data.databox(), 
    so check there for more information.
    """
    d = databox(**kwargs)
    d.load_file(path=path, first_data_line=first_data_line,
                filters=filters, text=text, default_directory=default_directory,
                header_only=header_only)

    if not quiet: print("\nloaded", d.path, "\n")

    if transpose: return d.transpose()
    return d

def load_multiple(paths="ask", first_data_line="auto", filters="*.*", text="Select some files, FACEHEAD.", default_directory="default_directory", quiet=True, header_only=False, transpose=False, **kwargs):
    """
    Loads a list of data files into a list of databox data objects.
    Returns said list.
    
    Parameters
    ----------
    path='ask'
        Supply a path to a data file; "ask" means pop up a dialog.
    first_data_line="auto"
        Specify the index of the first data line, or have it figure this out
        automatically.
    filters="*.*"
        Specify file filters.
    text="Select some files, FACEHEAD."
        Window title text.
    default_directory="default_directory"
        Which directory to start in (by key). This lives in spinmob.settings.
    quiet=True
        Don't print stuff while loading.
    header_only=False
        Load only the header information.
    transpose = False    
        Return databox.transpose().

    Optional keyword arguments are sent to spinmob.data.load(), so check there for more information.
    """
    if paths == "ask": paths = _s.dialogs.open_multiple(filters, text, default_directory)
    if paths is None : return

    datas = []
    for path in paths:
        if _os.path.isfile(path): datas.append(load(path=path, first_data_line=first_data_line,
                filters=filters, text=text, default_directory=default_directory,
                header_only=header_only, transpose=transpose, **kwargs))

    return datas
    

    
    
    
if __name__ == "__main__":
    
    import spinmob as sm
    d=sm.data.databox()
    