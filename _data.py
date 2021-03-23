import os      as _os
import shutil  as _shutil

# do this so all the scripts will work with all the numpy functions
import numpy          as _n
import scipy.special  as _special
import pylab          as _p
import textwrap       as _textwrap
import spinmob        as _s
import time           as _time


try:     from . import _functions
except:  _functions = _s.fun








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

    _is_spinmob_databox = True # Flag for type checking on inhereted objects (without need to import library)


    def __init__(self, delimiter=None, debug=False, **kwargs):

        # this keeps the dictionaries from getting all jumbled with each other
        self.clear_columns()
        self.clear_headers()
        self.clear_averagers()

        self.debug     = debug
        self.delimiter = delimiter

    def __setitem__(self, n, x):
        """
        set's the n'th column to x (n can be a column name too)
        """
        if type(n) is str:
            self.insert_column(array=x, ckey=n, index=None)

        elif type(n) in [int, int] and n > len(self.ckeys)-1:
            self.insert_column(array=x, ckey='_column'+str(len(self.ckeys)), index=None)

        else:
            self.columns[self.ckeys[n]] = _n.array(x)

    def __len__(self):
        return len(self.ckeys)

    def _repr_tail(self):
        """
        Returns the tail end of the __repr__ string with databox info (needed for inherited classes).
        """
        # Find the maximum length of the columns, and whether they're matched
        rows    = None
        matched = True
        for n in range(len(self)):
            c = self[n]

            # Use the first length
            if rows is None: rows = len(c)

            # Change it if there are more in this column
            elif len(c) != rows:
                matched = False
                if len(c) > rows: rows = len(c)

        # Clean up formatting.
        if rows is None: rows = 0

        # Base tail.
        s = str(len(self.hkeys))+" headers, "+str(len(self.ckeys))+" columns, "+str(rows)

        if matched: return s+' rows>'
        else:       return s+' rows (max)>'

    def __repr__(self):
        return "<databox instance: "+self._repr_tail()


    def __eq__(self, other):

        return self.is_same_as(other)




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
        globbies.update(_special.__dict__)

        # update with required stuff
        globbies.update({'h':self.h, 'c':self.c, 'd':self, 'self':self})

        # update with user stuff
        globbies.update(self.extra_globals)

        return globbies

    def load_file(self, path=None, first_data_line='auto', filters='*.*', text='Select a file, FACEPANTS.', default_directory=None, header_only=False, quiet=False, strip_nans=False):
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
        path=None
            Path to the file. Using None will bring up a dialog.

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

        strip_nans=False
            If True, runs self.strip_nans() after loading, which will
            remove the trailing nan values (useful for mismatched column lengths).

        Returns
        -------
        databox instance
        """

        # Set the default directory
        if default_directory is None: default_directory = self.directory

        # Ask user for a file to open
        if path is None:
            path = _s.dialogs.load(filters=filters,
                                        default_directory=self.directory,
                                        text=text)
        self.path = path

        if path is None:
            return None

        # make sure the file exists!
        if not _os.path.exists(path):
            if not quiet: print("ERROR: "+repr(path)+" does not exist.")
            return None

        # clear all the existing data
        self.clear()



        # First check if the file is SPINMOB_BINARY format!
        f = open(path, 'rb')

        # If this file is in SPINMOB_BINARY mode!
        if f.read(14).decode('utf-8') == 'SPINMOB_BINARY':

            # Next character is the delimiter
            self.delimiter = f.read(1).decode('utf-8')

            # Find the newline and get the data type
            s = ' '
            while not s[-1] == '\n': s = s+f.read(1).decode('utf-8')

            # Rest of the line is the binary dtype
            self.h(SPINMOB_BINARY = s.strip())

            # Now manually assemble the header lines to use in the analysis
            # below. If I try readline() on the binary file, it will crash.
            lines = ['\n']

            # The end of the header is specified by 'SPINMOB_BINARY' on its own line.
            while not lines[-1] == 'SPINMOB_BINARY':

                # Get the next line, one character at a time.
                s = ' '
                while not s[-1] == '\n': s = s+f.read(1).decode('utf-8')

                # Okay we have it
                lines.append(s.strip())

            # Pop that last line, which should be 'SPINMOB_BINARY'
            lines.pop(-1)

            # We've reached the end of the header.

        # Close the binary read.
        f.close()



        # If we're not in binary mode, we can read all the lines and find
        # the delimiter as usual. (In binary mode, the delimiter is specified)
        if not 'SPINMOB_BINARY' in self.hkeys:

            # For non-binary files, we always read all the lines.
            f = open(path, 'r', errors='ignore')
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
                        if   _functions.is_a_number(s.split(None)[0], ['_']): self.delimiter = None
                        elif _functions.is_a_number(s.split(',') [0], ['_']): self.delimiter = ','
                        elif _functions.is_a_number(s.split(';') [0], ['_']): self.delimiter = ';'

                        # quit the loop!
                        break

        # Done reading lines and auto-determining delimiter.



        ##### Pares the header from lines
        self.header_lines = []

        for n in range(len(lines)):

            # split the line by the delimiter
            s = lines[n].strip().split(self.delimiter)

            # remove a trailing whitespace entry if it exists.
            if len(s) and s[-1].strip() == '': s.pop(-1)

            # first check and see if this is a data line (all elements are numbers)
            if first_data_line == "auto" and _functions.elements_are_numbers(s):

                # we've reached the first data line
                first_data_line = n

                # quit the header loop
                break;

            ### after that check, we know it's a header line

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







        # Deal with the binary mode
        if 'SPINMOB_BINARY' in self.hkeys:

            # Read the binary file
            f = open(path, 'rb')
            s = f.read()
            f.close()

            # Get the delimiter for easier coding
            delimiter = self.delimiter.encode('utf-8')

            # Get the binary mode, e.g., 'float32'
            binary = self.h('SPINMOB_BINARY')

            # Number of bytes per element
            size = eval('_n.'+binary+'().itemsize', dict(_n=_n))

            # Location of first ckey
            start = s.find(b'SPINMOB_BINARY',14) + 15

            # Continue until we reach the last character.
            while not start >= len(s):

                # Get the location of the end of the ckey
                stop  = s.find(delimiter, start)

                # Woa, Nelly! We're at the end of the file.
                if stop == -1: break
                ckey  = s[start:stop].decode('utf-8').strip()

                # Get the array shape
                start = stop+1
                stop  = s.find(b'\n', start)
                shape = eval(s[start:stop].strip())
                if type(shape) == int: length = shape
                else:                  length = _n.prod(_n.array(shape))

                # Get the data!
                start = stop+1
                stop  = start+size*length
                self[ckey] = _n.frombuffer(s[start:stop], binary).reshape(shape)

                # Go to next ckey
                start = stop+1



        # Otherwise we have a text file to load.
        else:
            # Make sure first_data_line isn't still 'auto'
            # which happens if there's no data, or if it's a binary file
            if first_data_line == "auto" and not 'SPINMOB_BINARY' in self.hkeys:
                if not quiet: print("\ndatabox.load_file(): Could not find a line of pure data! Perhaps check the delimiter?")
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


            # # Most used format
            # try:

            # Define a function to fix each line of data.
            def fix(x): return str(x.replace('i','j'))

            # loop over the remaining data lines, converting to numbers
            z = _n.genfromtxt((fix(x) for x in lines[first_data_line:]),
                              delimiter=self.delimiter,
                              missing_values=['_'], filling_values=_n.nan,
                              dtype=_n.complex)

            # # Alternate format
            # except:
            #     print("WOA!")
            #     def fix(x): return bytearray(x.replace('i','j'), encoding='utf-8')

            #     # loop over the remaining data lines, converting to numbers
            #     z = _n.genfromtxt((fix(x) for x in lines[first_data_line:]),
            #                       delimiter=self.delimiter,
            #                       dtype=_n.complex)

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

        # Done with loading in the columns of data



        # now, as an added bonus, rename some of the obnoxious headers
        for k in self.obnoxious_ckeys:
            if k in self.columns:
                self.columns[self.obnoxious_ckeys[k]] = self.columns[k]

        # Strip the nans if we're supposed to
        if strip_nans: self.strip_nans()

        return self

    def save_file(self, path=None, filters='*', force_extension=None, force_overwrite=False, header_only=False, delimiter='use current', binary=None):
        """
        This will save all the header info and columns to an ascii file with
        the specified path.

        Parameters
        ----------
        path=None
            Path for saving the data. If None, this will bring up
            a save file dialog.

        filters='*.dat'
            File filter for the file dialog (for path=None)

        force_extension=None
            If set to a string, e.g., 'txt', it will enforce that the chosen
            filename will have this extension. If set to True, will use
            the supplied filters.

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

        binary=None
            Set to one of the allowed numpy dtypes, e.g., float32, float64,
            complex64, int32, etc. Setting binary=True defaults to float64.
            Note if the header contains the key SPINMOB_BINARY and binary=None,
            it will save as binary using the header specification.
        """

        # Make sure there isn't a problem later with no-column databoxes
        if len(self)==0: header_only=True

        # This is the final path. We now write to a temporary file in the user
        # directory, then move it to the destination. This (hopefully) fixes
        # problems with sync programs.
        if path in [None]: path = _s.dialogs.save(filters, default_directory=self.directory)
        if path in ["", None]:
            print("Aborted.")
            return False

        # Force the extension (we do this here redundantly, because the user may have also
        # specified a path explicitly)
        if force_extension is True: force_extension = filters
        if not force_extension is None:

            # In case the user put "*.txt" instead of just "txt"
            force_extension = force_extension.replace('*','').replace('.','')

            # If the file doesn't end with the extension, add it
            if not _os.path.splitext(path)[-1][1:] == force_extension:
                path = path + '.' + force_extension

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

        # open the temporary file
        f = open(temporary_path, 'w')



        # Override any existing binary if we're supposed to
        if binary in [False, 'text', 'Text', 'ASCII', 'csv', 'CSV']:
            self.pop_header('SPINMOB_BINARY', True)
            binary = None

        # If the binary flag is any kind of binary format, add the key
        if not binary in [None, False, 'text', 'Text', 'ASCII', 'csv', 'CSV']:
            self.h(SPINMOB_BINARY=binary)

        # Now use the header element to determine the binary mode
        if 'SPINMOB_BINARY' in self.hkeys:

            # Get the binary mode (we'll use this later)
            binary = self.pop_header('SPINMOB_BINARY')

            # If it's "True", default to float32
            if binary in ['True', True, 1]: binary = 'float32'

            # Write the special first key.
            f.write('SPINMOB_BINARY' + delimiter + binary + '\n')




        # Write the usual header
        for k in self.hkeys:
            h = self.h(k)

            # Convert arrays to lists so we can get all the numbers.
            if type(h) is _n.ndarray: h = h.tolist()

            # Write it.
            f.write(k + delimiter + repr(h).replace('\n',' ') + "\n")
        f.write('\n')

        # if we're not just supposed to write the header
        if not header_only:

            # Normal ascii saving mode.
            if binary in [None, 'None', False, 'False']:

                # First check if any of the columns are more than 1D and complain
                alles_klar = True
                for n in range(len(self)):
                    if len(_n.array(self[n]).shape) != 1: alles_klar = False
                if not alles_klar: print('WARNING: You must save in binary mode if your columns have more than 1 dimension.')

                # write the ckeys
                elements = []
                for ckey in self.ckeys: elements.append(str(ckey).replace(delimiter,'_'))
                f.write(delimiter.join(elements) + "\n")

                # Find the longest column
                N = 0
                for c in self:
                    if len(c) > N: N=len(c)

                # now loop over the longest column length
                for n in range(0, N):

                    # loop over each column
                    elements = []
                    for m in range(0, len(self.ckeys)):
                        # write the data if there is any, otherwise, placeholder
                        if n < len(self[m]):
                            elements.append(str(self[m][n]))
                        else:
                            elements.append('_')
                    f.write(delimiter.join(elements) + "\n")

            # Binary mode
            else:
                # Announce that we're done with the header. It's binary time
                f.write('SPINMOB_BINARY\n')

                # Loop over the ckeys
                for n in range(len(self.ckeys)):

                    # Get the binary data string
                    data_string = _n.array(self[n]).astype(binary).tostring()

                    # Write the column
                    #  ckey + delimiter + count + \n + datastring + \n
                    f.write(str(self.ckeys[n]).replace(delimiter,'_')
                           + delimiter + str(_n.array(self[n]).shape) + '\n')
                    f.close()
                    f = open(temporary_path, 'ab')
                    f.write(data_string)
                    f.close()
                    f = open(temporary_path, 'a')
                    f.write('\n')

        f.close()

        # now move it
        _shutil.move(temporary_path, path)

        return self

    def set_binary_mode(self, binary='float64'):
        """
        Sets the save_file() mode to binary.

        Parameters
        ----------
        binary=float64
            Can be any of these objects found in numpy:
                'float16', 'float32', 'float64', 'float128' (if supported),
                'int8', 'int16', 'int32', 'int64', 'int128' (if supported),
                'complex64', 'complex128', 'complex256' (if supported).
            If False, this will set the save format to text mode.
            If True, defaults to float64.
        """
        if binary is True: self.h(SPINMOB_BINARY='float64')
        elif binary:       self.h(SPINMOB_BINARY=binary)
        else:              self.pop_header('SPINMOB_BINARY', ignore_error=True)
        return self

    def set_text_mode(self):
        """
        Sets the save_file() format to text mode. Same as self.set_binary_mode(False).
        """
        self.set_binary_mode(False)
        return self

    def get_row(self, n):
        """
        Returns a list of the n'th row (starting at 0) from all columns.

        Parameters
        ----------
        n
            Index of data point to return.
        """
        # loop over the columns and pop the data
        point = []
        for k in self.ckeys: point.append(self[k][n])
        return point

    def get_data_point(self, n):
        """
        Obsolete. Please use get_row() instead.
        """
        print('OBSOLETE: Please use databox.get_row() instead of databox.get_data_point()')
        return self.get_row(n)

    def pop_row(self, n):
        """
        This will remove and return the n'th row (starting at 0) from
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

    def pop_data_point(self, n):
        """
        Obsolete.please use pop_row() instead.
        """
        print('OBSOLETE: Please use databox.pop_row() instead of databox.pop_data_point()')
        return self.pop_row(n)

    def insert_row(self, row, index=None, ckeys=None):
        """
        Inserts a row at index n.

        Parameters
        ----------
        row
            A list or array of new data points, one for each column.

        index=None
            Where to insert the point(s) in each column. None => append.

        ckeys=None
            An optional list (of the same size as row) of ckeys. If this
            list does not match the existing ckeys, it will clear the columns
            and rebuild them, rather than overwriting.
        """

        # Optional ckeys supplied
        if not ckeys is None:

            # Make sure they are a list for comparing with self.ckeys
            ckeys = list(ckeys)

            # If the ckeys do not match, rebuild the columns
            if not self.ckeys == ckeys:
                self.clear_columns()
                for k in ckeys: self[k] = []

        if not len(row) == len(self.columns) and not len(self.columns)==0:
            raise Exception("Row must have as many elements as there are columns:", len(row), 'appending to', self)

        # otherwise, we just auto-add this data point as new columns
        elif len(self.columns)==0:
            for i in range(len(row)): self[i] = [row[i]]

        # otherwise it matches length so just insert it.
        else:
            for i in range(len(row)):

                # get the array and turn it into a list
                data = list(self[i])

                # append or insert
                if index is None: data.append(       row[i])
                else:             data.insert(index, row[i])

                # reconvert to an array
                self[i] = _n.array(data)

        return self

    def insert_data_point(self, *a, **kw):
        """
        Obsolete. Please use insert_row() instead.
        """
        print('OBSOLETE: Please use databox.insert_row() instead of databox.insert_data_point()')
        return self.insert_row(*a, **kw)

    def append_row(self, row, ckeys=None, history=0):
        """
        Appends the supplied row (list) to the column(s).

        Parameters
        ----------
        row
            A list or array of new data, one for each column.

        ckeys=None
            An optional list (of the same size as row) of ckeys. If this
            list does not match the existing ckeys, it will clear the columns
            and rebuild them, rather than overwriting.

        history=None
            If a positive integer is specified, after appending the data point,
            it will pop the first data points off until the length of the
            0th column is equal to the specified value.
        """
        self.insert_row(row, None, ckeys)

        if history > 0:
            while len(self[0]) > history: self.pop_row(0)

        return self

    def append_data_point(self, *a, **kw):
        """
        Obsolete. Use append_row() instead.
        """
        print('OBSOLETE: Please use append_row() instead of append_data_point().')
        return self.append_row(*a, **kw)

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
        if not _functions.is_iterable(script):

            # special case
            if script is None: return None

            # get the expression and variables dictionary
            [expression, v] = self._parse_script(script)

            # if there was a problem parsing the script
            if v is None: raise Exception("Could not parse '"+script+"'")

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
        if len(split_script) == 1:
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
            except Exception as e:
                raise Exception("Could not evaluate '"+str(script)+"'.\n"+e.message)
                #return [None, None]


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



    def copy_headers(self, source_databox):
        """
        Loops over the hkeys of the source_databox, updating this databoxes' header.
        """
        for k in source_databox.hkeys: self.insert_header(k, source_databox.h(k))

        return self
    copy_headers_from = copy_headers

    def copy_columns(self, source_databox):
        """
        Loops over the ckeys of the source_databox, updating this databoxes' columns.
        """
        for k in source_databox.ckeys: self.insert_column(source_databox[k], k)

        return self
    copy_columns_from = copy_columns

    def copy_all(self, source_databox):
        """
        Copies the headers and columns from source_databox to this databox.
        """
        self.copy_headers(source_databox)
        self.copy_columns(source_databox)
        return self
    copy_all_from = copy_all

    def copy(self):
        """
        Creates a databox instance, copies all the information into it,
        and returns it.
        """
        d = databox()
        self.copy_all_to(d)
        return d

    def copy_headers_to(self, destination_databox):
        """
        Copies the headers from this databox to the supplied destination databox.
        """
        destination_databox.copy_headers_from(self)

    def copy_columns_to(self, destination_databox):
        """
        Copies the columns from this databox to the supplied destination databox.
        """
        destination_databox.copy_columns_from(self)

    def copy_all_to(self, destination_databox):
        """
        Copies everything from this databox to the supplied destination databox.
        """
        destination_databox.copy_all_from(self)

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


    def is_same_as(self, other_databox, headers=True, columns=True, header_order=True, column_order=True, ckeys=True):
        """
        Tests that the important (i.e. savable) information in this databox
        is the same as that of the other_databox.

        Parameters
        ----------
        other_databox
            Databox with which to compare.
        headers=True
            Make sure all header elements match.
        columns=True
            Make sure every element of every column matches.
        header_order=True
            Whether the order of the header elements must match.
        column_order=True
            Whether the order of the columns must match. This is only a sensible
            concern if ckeys=True.
        ckeys=True
            Whether the actual ckeys matter, or just the ordered columns of data.


        Note the == symbol runs this function with everything True.
        """
        d = other_databox

        if not hasattr(other_databox, '_is_spinmob_databox'): return False

        # Proceed by testing things one at a time, returning false if one fails
        if headers:

            # Same number of elements
            if not len(self.hkeys) == len(d.hkeys): return False

            # Elements
            if header_order and not self.hkeys == d.hkeys: return False

            # Each value
            for k in self.hkeys:
                # Make sure the key exists
                if not k in d.hkeys: return False

                # Make sure it's the same.
                if not self.h(k) == d.h(k): return False

        if columns:

            # Same number of columns
            if not len(self.ckeys) == len(d.ckeys): return False

            # If we're checking columns by ckeys
            if ckeys:

                # Columns
                if column_order and not self.ckeys == d.ckeys: return False

                # Each value of each array
                for k in self.ckeys:
                    # Make sure the key exists
                    if not k in d.ckeys: return False

                    # Check the values
                    if not (_n.array(self[k]) == _n.array(d[k])).all(): return False

            # Otherwise we're ignoring ckeys
            else:
                for n in range(len(self.ckeys)):
                    if not (_n.array(self[n]) == _n.array(d[n])).all(): return False

        # Passes all tests
        return True



    def pop_header(self, hkey, ignore_error=False):
        """
        This will remove and return the specified header value.

        Parameters
        ----------
        hkey
            Header key you wish to pop.
            You can specify either a key string or an index.
        ignore_error=False
            Whether to quietly ignore any errors (i.e., hkey not found).
        """

        # try the integer approach first to allow negative values
        if type(hkey) is not str:
            try:
                return self.headers.pop(self.hkeys.pop(hkey))
            except:
                if not ignore_error: raise Exception("pop_header() could not find hkey "+str(hkey))

        else:

            try:
                # find the key integer and pop it
                hkey = self.hkeys.index(hkey)

                # pop it!
                return self.headers.pop(self.hkeys.pop(hkey))

            except:
                if not ignore_error: raise Exception("pop_header() could not find hkey "+str(hkey))




    def pop_column(self, ckey, ignore_error=False):
        """
        This will remove and return the data in the specified column.

        You can specify either a key string or an index.
        """

        # try the integer approach first to allow negative values
        if type(ckey) is not str:
            return self.columns.pop(self.ckeys.pop(ckey))

        # Otherwise we assume it's a string
        elif ckey in self.ckeys:

            # find the key integer and pop it
            ckey = self.ckeys.index(ckey)
            return self.columns.pop(self.ckeys.pop(ckey))

        # Column doesn't exist!
        elif not ignore_error:

            print("Column does not exist (yes, we looked).")
            return

    def insert_column(self, array, ckey='temp', index=None):
        """
        This will insert/overwrite a new column and fill it with the data from the
        the supplied array.

        Parameters
        ----------
        array
            Data; can be a list, but will be converted to numpy array
        ckey
            Name of the column; if an integer is supplied, uses self.ckeys[ckey]
        index
            Before which index to insert this column. None => append to end.
        """

        # if it's an integer, use the ckey from the list
        if type(ckey) in [int, int]: ckey = self.ckeys[ckey]

        # append/overwrite the column value
        self.columns[ckey] = _n.array(array)
        if not ckey in self.ckeys:
            if index is None: self.ckeys.append(ckey)
            else:             self.ckeys.insert(index, ckey)

        return self

    def append_column(self, array, ckey='temp'):
        """
        This will append a new column and fill it with the data from the
        the supplied array.

        Parameters
        ----------
        array
            Data; can be a list, but will be converted to numpy array
        ckey
            Name of the column.
        """
        if not type(ckey) is str: raise Exception("ckey should be a string!")

        if ckey in self.ckeys: raise Exception("ckey '"+ckey+"' already exists!")


        return self.insert_column(array, ckey)

    def append_empty_columns(self, ckeys):
        """
        Creates an empty column for each ckey.
        """
        for ckey in ckeys: self[ckey] = []

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

    def clear_averagers(self):
        """
        Empties the dictionary self.averagers.
        """
        self.averagers = dict()

    def clear(self):
        """
        Removes all headers, columns, and averagers from the databox.
        """
        self.clear_columns()
        self.clear_headers()
        self.clear_averagers()
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

    def strip_nans(self, columns=None):
        """
        Removes the trailing nan values from the specified column or list of columns, or
        all columns if columns==None. To remove / replace *all* nans (or infs) use
        the built-in numpy functionality.

        Parameters
        ----------
        columns=None : None, int, str, or list
            Columns to strip. If None, strip all columns.

        Returns
        -------
        self
        """
        if columns is None: columns = self.ckeys
        if not type(columns) in [list, tuple]: columns = [columns]

        # Do the strip
        for c in columns:

            # Get the index of the last non-nan
            N = _n.where(_n.logical_not(_n.isnan(self[c])))[0][-1]

            # Keep up to the last number
            self[c] = self[c][0:N+1]

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
        cs = _functions.trim_data_uber(self, conditions)
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




    def c(self, *args, **kwargs):
        """
        Takes a single argument or keyword argument, and returns the specified
        column. If the argument (or keyword argument) is an integer, return the
        n'th column, otherwise return the column based on key.

        If no arguments are supplied, simply print the column information.
        """
        # If not arguments, print everything
        if len(args) + len(kwargs) == 0:

            print("Columns")
            if len(self.ckeys)==0: print ('  No columns of data yet.')

            # Loop over the ckeys and display their information
            for n in range(len(self.ckeys)):
                print('  '+str(n)+': '+str(self.ckeys[n])+' '+str(_n.shape(self[n])))
            return

        # Otherwise, find n
        elif len(args):   n = args[0]
        elif len(kwargs):
            for k in kwargs: n = kwargs[k]

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
            if start is None: start = 0
            if stop  is None or stop>len(self): stop  = len(self)
            if step  is None: step  = 1

            # Return what was asked for
            return self[range(start, stop, step)]

        # Otherwise assume it's an integer
        return self.columns[self.ckeys[n]]

    get_data    = c
    __getitem__ = c

    def h(self, *args, **kwargs):
        """
        This function searches through hkeys for one *containing* a key string
        supplied by args[0] and returns that header value.

        Also can take integers, returning the key'th header value.

        kwargs can be specified to set header elements.

        Finally, if called with no arguments or keyword arguments, this
        simply prints the header information.
        """
        # If not arguments, print everything
        if len(args) + len(kwargs) == 0:
            print("Headers")
            for n in range(len(self.hkeys)):
                print('  '+str(n)+': '+str(self.hkeys[n])+' = '+repr(self.h(n)))
            return

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
                raise Exception("Couldn't find '"+str(hkey) + "' in header.")


    def add_to_column_average(self, ckey, array, std_mean=True, lowpass_frames=0, precision=_n.float64, ignore_nan=True):
        """
        Adds the supplied array to the averager data pool for column
        'ckey'. Averagers (spinmob.fun.averager) used for these calculations
        will be stored in the dictionary self.averagers under the specified ckey.
        After pushing in the new data and recalculating, this function transfers
        the averaged data to new columns, and sends all the other averager
        information to the header.

        Parameters
        ----------
        ckey
            Destination column key or integer.
        array
            Array of data. Must match the shape of the existing column.
        std_mean=True
            Whether to include the std_mean column. If True, an additional
            column will be inserted after that of ckey, with the name ckey+'.std_mean'.
        lowpass_frames=0
            Time constant (number of frames) for the DSP low pass. See
            spinmob.fun.averager for details.
        precision=numpy.float64
            Numpy dtype used in internal calculations.
        ignore_nan=True
            Whether to set NaN's appearing in calculations to zero.
        """
        # First get the ckey string
        if not type(ckey) == str: ckey = self.ckeys[ckey]

        # If the averager does not exist
        if ckey not in self.averagers:
            self.averagers[ckey] = _functions.averager(name=ckey)

        # Update the averaging method
        x = self.averagers[ckey]
        x.lowpass_frames      = lowpass_frames
        x.precision    = precision
        x.ignore_nan   = ignore_nan

        # Add the new data set
        x.add(array)

        # Update (or create) the mean column
        self[ckey] = x.mean

        # If we're including the std_mean
        if std_mean:

            # Get the std_mean key
            skey = ckey+'.std_mean'

            # Estimate the standard error on the mean
            sigma = x.variance_mean**0.5

            # Make sure the column exists just after that of ckey
            if skey in self.ckeys: self[skey] = sigma
            else:                  self.insert_column(sigma, skey, self.ckeys.index(ckey)+1)

        # Update the header information
        if self.name is None: name = ''
        else:                 name = '/'+self.name+'/'
        self.insert_header(name + ckey+'.ignore_nan',     self.averagers[ckey].ignore_nan)
        self.insert_header(name + ckey+'.lowpass_frames', self.averagers[ckey].lowpass_frames)
        self.insert_header(name + ckey+'.name',           self.averagers[ckey].name)
        self.insert_header(name + ckey+'.N',              self.averagers[ckey].N)
        self.insert_header(name + ckey+'.precision',      self.averagers[ckey].precision)

        return self

    def reset_all_averagers(self, *a, **k):
        """
        Resets all averagers. Arguments and keyword arguments are not used.
        """
        for ckey in self.averagers: self.averagers[ckey].reset()



###########################################
# Class for fitting data
###########################################

class fitter():
    """
    Creates an object for fitting data to functions.

    Parameters
    ----------
    Keyword arguments are sent to self.set(). Arguments that apply to a data
    set can be specified as a single element or list of elements. For example:

    xmin = 42

    will specify that all figures not include data with x-values below 42.
    Meanwhile,

    xmin = [42,27]

    will specify that the first data set will include x>42, and the second
    will include x>27.

    Behavior Options
    ----------------
    silent = False
        Ignore warnings and non-crash errors (don't print anything).
    autoplot      = True
        Automatically (re)plot when changing stuff?

    Figure Options
    --------------
    first_figure  = 0
        First figure number to use. This can prevent overwriting an existing
        figure when calling self.plot().
    fpoints       = 1000
        Number of points to use when plotting the fit, guess, and background.
        Set fpoints = None to use the xdata points.
    plot_fit      = True
        Include fit curve in plot(s)?
    plot_bg       = True,
        Include background curve(s) in plots?
    plot_all_data = False,
        Continue to plot the trimmed data?
    plot_errors   = True
        Include error bars in plot(s)?
    plot_guess    = True,
        Include the guess(es)?
    plot_guess_zoom = False,
        Zoom to include guess(es)?
    style_data   = dict(marker='o', color='b', ls='')
        Style for data curve(s).
    style_fit    = dict(marker='',  color='r', ls='-')
        Style for fit curve(s).
    style_guess  = dict(marker='',  color='0.25', ls='-')
        Style for guess curve(s).



    Data Options
    ------------
    subtract_bg   = False
        Subtract background function(s) from plots?
    xmin          = None
        Minimum x-value(s) for trimming.
    xmax          = None
        Maximum x-value(s) for trimming.
    ymin          = None
        Minmium y-value(s) for trimming.
    ymax          =
        Maximum y-value(s) for trimming.
    xlabel        = None
        Optional override for x-axis label(s)
    ylabel        = None
        Optional override for y-axis label(s)
    xscale        = 'linear'
        Scale(s) for x-axis (could be 'log').
    yscale        = 'linear'
        Scale(s) for y-axis (could be 'log').
    scale_eydata  = 1.0
        Optional scale factor(s) for the eydata.
    coarsen       = 1
        How much to coarsen the data, i.e., averaging each group of the
        specified number of points into a single point (and propagating errors).


    Typical workflow
    ----------------
    my_fitter = fitter()
        Creates the fitter object

    my_fitter.set_functions('a*x+b', 'a,b')
        Sets the function(s) and free parameters.

    my_fitter.set_data([1,2,3],[1,2,1])
        Sets the data to be fit.

    my_fitter.fit()
        Does the fitting.

    my_fitter.results
        Contains the output of scipy.leastsq.optimize (see scipy docs)


    Tips
    ----
    Usage
        All methods starting without an underscore are meant to be used
        by a "typical" user. For example, do not set data directly;
        use set_data(), which clears the fit results. Otherwise the fit
        results will not match the existing data.
    self.figures
        Setting this to a figure instance or list of figures will force the
        plot command to use these, rather than creating new figures.

    See the spinmob wiki on github, or use IPython's autocomplete to play around!
    """

    figures = None

    def __init__(self, **kwargs):

        if not _s._lm:
            raise Exception("You need to install lmfit to use the new fitter. You can install it with 'pip install lmfit'.")
            return

        self.f  = []    # list of functions
        self.bg = []    # list of background functions (for subtracting etc)
        self.p_in    = _s._lm.Parameters() # Parameters for the fit
        self.p_fit   = None             # Shortcut to self.results.params
        self.results = None             # output from the fitter.

        self._f_raw  = None # raw argument passed to set_functions()
        self._bg_raw = None # raw argument passed to set_functions()

        self._xdatas_given  = [] # Starting point for massaging data
        self._ydatas_given  = []
        self._eydatas_given = []

        self._xdatas_processed  = None # trimmed, processed data to send to the fitter
        self._ydatas_processed  = None
        self._eydatas_processed = None
        self._guessed_eydata  = False # Flag becomes True when a "guess" is used. For warnings.

        # make sure all the awesome stuff from numpy and scipy special is visible to the functions
        self._globals  = dict(_n.__dict__)
        self._globals.update(_special.__dict__)

        self._fnames    = [] # names for each function
        self._bgnames   = [] # names for each background



        # dictionary containing all the fitter settings
        self._settings = dict()

        # Silence warnings
        self._settings['silent'] = False

        # settings that don't require a re-fit
        self._safe_settings =list(['bg_names', 'fpoints', 'f_names', 'plot_all_data',
                                   'plot_bg', 'plot_errors', 'plot_guess', 'plot_guess_zoom', 'plot_fit',
                                   'silent', 'style_bg', 'style_data', 'style_guess',
                                   'style_fit', 'subtract_bg', 'xscale', 'yscale',
                                   'xlabel', 'ylabel'])

        # settings that should not be lists in general (i.e. not one per data set)
        self._single_settings = list(['autoplot', 'first_figure', 'silent'])

        # default settings; we use the _no_autoplot flag so the set function doesn't
        # do all the automatic stuff like plotting and updating the analysis.
        self._no_autoplot = True
        self.set(silent        = False,    # Ignore warnings
                 autoplot      = True,     # whether we always plot when changing stuff
                 plot_all_data = False,    # Plot all of the data even after trimming?
                 plot_fit      = True,     # include f in plots?
                 plot_bg       = True,     # include bg in plots?
                 plot_errors   = True,     # include the y error bars?
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
                 #scale_exdata  = 1.0,      # by how much should we scale the exdata?
                 coarsen       = 1,        # how much to coarsen the data

                 # styles of plots
                 style_data   = dict(marker='o', color='b',   ls='', mec='b'),
                 style_fit    = dict(marker='',  color='r',   ls='-'),
                 style_guess  = dict(marker='',  color='0.25',ls='-'),
                 style_bg     = dict(marker='',  color='k',   ls='-'),)

        if _s.settings['dark_theme_figures']:
            self.set(
                 style_data   = dict(marker='o', color='#77AAFF',ls='', mec='#77AAFF'),
                 style_fit    = dict(marker='',  color='#FF7777',ls='-'),
                 style_guess  = dict(marker='',  color='0.5',ls='-'),
                 style_bg     = dict(marker='',  color='k',   ls='-'),)


        self._no_autoplot = False

        # Update with additional kwargs, and run the usual processes.
        self.set(**kwargs)


    def set(self, **kwargs):
        """
        Changes a setting or multiple settings. Can also call self() or
        change individual parameters with self['parameter'] = value
        """
        if len(kwargs)==0: return self

        # Set settings
        for k in list(kwargs.keys()): self[k] = kwargs[k]

        # Plot if we're supposed to.
        if not self._no_autoplot and self['autoplot']: self.plot()

        return self


    __call__ = set

    def __setitem__(self, key, value):
        """
        This is the "main" function used by set() and self().
        """

        # special case: setting an input parameter
        if key in self.p_in.keys(): self.p_in[key].value = value

        # everything else should have a value for each data set or plot
        elif key in self._settings or self._no_autoplot:

            # Most settings need lists that match the length of the data sets
            if not key in self._single_settings:

                # make sure it's a list or dictionary
                if not type(value) in [list]: value = [value]

                # make sure it matches the data, unless it's a dictionary
                while len(value) < max(len(self.f), len(self._xdatas_given), len(self._ydatas_given)):
                    value.append(value[0])

            # set the value
            self._settings[key] = value

        # yell.
        else: raise Exception("'"+key+"' is not a valid setting or parameter name.")

        # if it isn't a "safe" key, invalidate the previous fit results.
        if not key in self._safe_settings: self.clear_results()



    def __repr__(self):
        """
        Prints out the current settings.
        """
        keys = list(self._settings.keys())
        keys.sort()

        s = "\nFITTER SETTINGS\n"
        for k in keys:
            # for the clunky style settings, loop over the list
            if k[0:5] == 'style' and _functions.is_iterable(self[k]):
                s = s+"  {:15s} [".format(k)
                for n in range(len(self[k])):
                    s = s+str(self[k][n])
                    if n==len(self[k])-1: s = s+"]\n"
                    else:                 s = s+"\n                   "

            else:
                s = s+"  {:15s} {:s}\n".format(k, str(self[k]))


        # Get the longest string name
        l = 0
        for pname in self.p_in:
            if len(pname) > l: l = len(pname)
        l = str(l)

        # If we don't have any data.
        if len(self._xdatas_given)==0 or len(self._ydatas_given)==0 or len(self.f)==0:
            s = s + "\nINPUT PARAMETERS\n"

        # If we do have data, give mor information
        else:
            s = s + "\nINPUT PARAMETERS (reduced chi^2 = {:s}, {} DOF)\n".format(
                self._format_value_error(self.get_reduced_chi_squared(self.p_in),
                                         _n.sqrt(_n.divide(2.0,self.get_degrees_of_freedom()))),
                        self.get_degrees_of_freedom())

        # Always print the guess parameters
        for pname in self.p_in:
            s = s + str("  {:"+l+"s} = {:G}, vary={:s} min={:G} max={:G} expr={:s}\n").format(
                pname,
                self.p_in[pname].value,
                str(self.p_in[pname].vary == 1),
                self.p_in[pname].min,
                self.p_in[pname].max,
                repr(self.p_in[pname].expr))

        # Print out the fit results
        if self.results and hasattr(self.results, 'covar'):
            s = s + "\nFIT RESULTS (reduced chi^2 = {:s}, {:d} DOF)\n".format(
                    self._format_value_error(self.get_reduced_chi_squared(), _n.sqrt(_n.divide(2.0,self.get_degrees_of_freedom()))),
                    int(self.get_degrees_of_freedom()))
            for pname in self.p_fit:
                if self.p_in[pname].vary:
                    s = s + str("  {:"+l+"s} = {:s}\n").format(pname, self._format_value_error(self.p_fit[pname].value, self.p_fit[pname].stderr))
                else:
                    s = s + str("  {:"+l+"s} = {:G} (fixed)\n").format(pname, self.p_fit[pname].value)
        # If the fit did not converge, the covariance matrix is None
        elif self.results and hasattr(self.results, 'covar'):
            s = s + "\nFIT DID NOT CONVERGE\n"
            for pname in self.p_in:
                s = s + "  {:10s} = {:G} (meaningless)\n".format(pname, self.p_fit[pname].value)
        # No fit results
        else:
            s = s + "\nNO FIT RESULTS\n"

        # Warning: guessed eydata
        if self._guessed_eydata:
            s = s + "\nWARNING: eydata was not specified for at least one data set."

        # Check if there are any zero error bars.
        eys = self.get_processed_data()[2]

        # Could be irregularly shaped, so can't just use (eydata==0).any()
        any_zeros = False
        for ey in eys:
            if _n.any(ey==0):
                any_zeros = True
                break
        if any_zeros: s = s + "\nWARNING: At least one error bar is zero."

        return s

    def get(self, key):
        """
        Returns (in order of availability):
            1. The fit parameter of the specified name (if it exists).
            2. The guess parameter of the specified name (if it exists).
            4. The setting of the specified key, e.g. 'xmin'.

        Parameters
        ----------
        key
            String key, e.g. 'a' or 'coarsen'.
        """

        # Default to fit parameters
        if self.results and key in self.results.params.keys(): return self.results.params[key]

        # Then guess parameters
        if key in self.p_in.keys():                            return self.p_in[key]

        # Then settings.
        return self._settings[key]

    __getitem__ = get

    def _parse_parameter_string(self, p):
        """
        Returns a dictionary of key-value pairs for strings like 'a=-0.2, b, c'.
        If no value is given, 1.0 is assumed. If p is None, returns empty dict()
        """
        r = dict() # return value

        # No parameters
        if not p: return r

        # break up the parameter names and initial values.
        for s in p.split(','):

            # split by '=' and see if there is an initial value
            s = s.split('=')

            # add the key-value pair
            r[s[0].strip()] = float(s[1]) if len(s)>1 else 1.0

        return r

    def set_functions(self,  f='a*x*cos(b*x)+c', p='a=-0.2, b, c=3', c=None, bg=None, g=None, **kwargs):
        """
        Sets the function(s) used to describe the data.

        Parameters
        ----------
        f=['a*x*cos(b*x)+c', 'a*x+c']
            This can be a string function, a defined function
            my_function(x,a,b), or a list of some combination
            of these two types of objects. The length of such
            a list must be equal to the number of data sets
            supplied to the fit routine.

        p='a=1.5, b'
            This must be a comma-separated string list of
            parameters used to fit. If an initial guess value is
            not specified, 1.0 will be used.
            If a function object is supplied, it is assumed that
            this string lists the parameter names in order.

        c=None
            Fit _constants; like p, but won't be allowed to float
            during the fit. This can also be None.

        bg=None
            Can be functions in the same format as f describing a
            background (which can be subtracted during fits, etc)

        g=None
            Can be a dictionary of globals for evaluating functions.

        Additional keyword arguments are added to the globals used when
        evaluating the functions. For example,

            set_functions('f(a,x)+b', 'a,b', f=my_function)

        or

            set_functions('f(a,x)+b', 'a,b', g={'f':my_function})

        will work the same.
        """

        # Update the globals
        if g: self._globals.update(g)
        self._globals.update(kwargs)

        # store these for later
        self._f_raw  = f
        self._bg_raw = bg

        # Get dictionaries for the constants and parameters
        cs = self._parse_parameter_string(c)
        ps = self._parse_parameter_string(p)

        # Create the parameters
        self.p_in.clear()
        for k in cs: self.p_in.add(k, cs[k], vary=False)
        for k in ps: self.p_in.add(k, ps[k], vary=True)

        # use the internal settings we just set to create the functions
        self._update_functions()

        if self['autoplot']: self.plot()

        return self


    def _update_functions(self):
        """
        Uses internal settings to update the functions.
        """

        self.f             = []
        self.bg            = []
        self._fnames       = []
        self._bgnames      = []

        f  = self._f_raw
        bg = self._bg_raw

        # make sure f and bg are lists of matching length
        if not _functions.is_iterable(f) : f  = [f]
        if not _functions.is_iterable(bg): bg = [bg]
        while len(bg) < len(f): bg.append(None)

        # get a comma-delimited string list of parameter names for the "normal" function
        pstring = 'x, ' + ', '.join(self.p_in.keys())

        # loop over all the functions and create the master list
        for n in range(len(f)):

            # if f[n] is a string, define a function on the fly.
            if isinstance(f[n], str):
                self.f.append( eval('lambda ' + pstring + ': ' + f[n],  self._globals))
                self._fnames.append(f[n])

            # Otherwise, just append it.
            else:
                self.f.append(f[n])
                self._fnames.append(f[n].__name__)

            # if bg[n] is a string, define a function on the fly.
            if isinstance(bg[n], str):
                self.bg.append(eval('lambda ' + pstring + ': ' + bg[n], self._globals))
                self._bgnames.append(bg[n])

            # Otherwise assume it's an actual function or None
            else:
                self.bg.append(bg[n])
                if bg[n] is None: self._bgnames.append('None')
                else:             self._bgnames.append(bg[n].__name__)

        # update the format of all the settings (each setting should be a list of size equal to the number of data sets)
        for k in list(self._settings.keys()): self[k] = self[k]

        # make sure we don't think our fit results are valid!
        self.clear_results()


    def set_data(self, xdata=[1,2,3,4,5], ydata=[1.7,2,3,4,3], eydata=None, dtype=None, **kwargs):
        """
        This will handle the different types of supplied data and put everything
        in a standard format for processing.

        Parameters
        ----------
        xdata, ydata, eydata=None
            These can each be a single array of data, a number, or None (generates
            integer arrays), or a list of any combination of these for fitting
            multiple data sets.

        dtype=None
            When converting the data to arrays, use this conversion function.

        **kwargs
            Sent to self.set()

        Note this function is "somewhat" smart about reshaping the input
        data to ease life a bit, but it can't handle ambiguities. If you
        want to play it safe, supply lists for all three arguments that
        match in dimensionality.
        """
        # Send additional kwargs to set
        self(**kwargs)

        # SET UP DATA SETS TO MATCH EACH OTHER AND NUMBER OF FUNCTIONS
        xdatas, ydatas = _functions._match_data_sets        (xdata,  ydata)
        eydatas        = _functions._match_error_to_data_set(ydatas, eydata)

        # Convert all None to a guess value.
        self._guessed_eydata = False
        for n in range(len(eydatas)):

            # If it's none, guess a value 0.2*(ymax-ymin)
            if eydatas[n] is None:
                self._guessed_eydata = True
                eyguess = 0.1*(max(ydatas[n])-min(ydatas[n]))
                if eyguess == 0: eyguess = 1
                eydatas[n] = _n.zeros(len(ydatas[n])) + eyguess

        # Convert to arrays
        for n in range(len(xdatas)):
            xdatas[n]  = _n.array(xdatas[n], dtype)
            ydatas[n]  = _n.array(ydatas[n], dtype)
            eydatas[n] = _n.array(eydatas[n],dtype)

        # store the data, script, or whatever it is!
        self._xdatas_given  = xdatas
        self._ydatas_given  = ydatas
        self._eydatas_given = eydatas
        self._dtype = dtype

        # set the eyscale to 1 for each data set
        self['scale_eydata'] = [1.0]*len(self._xdatas_given)

        # Update the settings so they match the number of data sets.
        for k in self._settings.keys(): self[k] = self[k]

        # Plot if necessary
        if self['autoplot']: self.plot()

        return self

    def get_data(self):
        """
        Returns the original xdata, ydata, eydata, supplied by set_data().
        """
        if len(self._xdatas_given) == 0: return [], [], []

        return list(self._xdatas_given), list(self._ydatas_given), list(self._eydatas_given)

    def get_fit_parameters(self):
        """
        Returns a list of the fit parameters, in order.
        """
        if self.p_fit is None: return None

        ps = []
        for p in self.p_fit: ps.append(self.p_fit[p])

        return ps

    def get_fit_values(self):
        """
        Returns a numpy array of the fit values, in order.
        """
        if self.p_fit is None: return None

        ps = []
        for p in self.p_fit: ps.append(self.p_fit[p].value)

        return _n.array(ps)

    def get_fit_standard_errors(self):
        """
        Returns a numpy array of the fit standard errors, in order.
        """
        if self.p_fit is None: return None

        ps = []
        for p in self.p_fit: ps.append(self.p_fit[p].stderr)

        return _n.array(ps)

    def get_fit_results(self):
        """
        If there are fit results, returns a dictionary with all the fit
        results.
        """
        # No fit
        if self.results is None: return None

        # Fit may have not converged, evidenced by not hasattr(results, 'covar')

        # Dictionary of all the stuff
        d = dict()

        # Loop over pnames
        for k in self.results.var_names:
            p = self.results.params[k]

            # Get the pname, fit value, and fit error
            value = p.value
            error = p.stderr

            # Stuff it in the dictionary
            d[k] = value
            d[k+'.std'] = error

        # Include some other stuff
        d['covariance']         = self.results.covar
        d['chi2']               = self.results.chisqr
        d['chi2s']              = self.get_chi_squareds()
        d['reduced_chi2']       = self.results.redchi
        d['reduced_chi2.std']   = _n.sqrt(2.0/self.get_degrees_of_freedom())
        d['reduced_chi2s']      = self.get_reduced_chi_squareds()
        d['get_degrees_of_freedom'] = self.get_degrees_of_freedom()

        return d

    def set_guess_to_fit_result(self):
        """
        If you have a fit result, set the guess parameters to the
        fit parameters.
        """
        if self.results is None:
            print("No fit results to use! Run fit() first.")
            return

        # loop over the results and set the guess values
        for k in self.results.var_names: self.p_in[k].value = self.results.params[k].value

        if self['autoplot']: self.plot()

        return self

    def get_processed_data(self, do_coarsen=True, do_trim=True):
        """
        This will coarsen and then trim the data sets according to settings.

        Returns processed xdata, ydata, eydata.

        Parameters
        ----------
        do_coarsen=True
            Whether we should coarsen the data
        do_trim=True
            Whether we should trim the data

        Settings
        --------
        xmin, xmax, ymin, ymax
            Limits on x and y data points for trimming.
        coarsen
            Break the data set(s) into this many groups of points, and average
            each group into one point, propagating errors.
        """

        # get the data
        xdatas, ydatas, eydatas = self.get_data()

        # get the trim limits (trimits)
        xmins   = self['xmin']
        xmaxs   = self['xmax']
        ymins   = self['ymin']
        ymaxs   = self['ymax']
        coarsen = self['coarsen']

        # make sure we have one limit for each data set
        if type(xmins)   is not list: xmins   = [xmins]  *len(xdatas)
        if type(xmaxs)   is not list: xmaxs   = [xmaxs]  *len(xdatas)
        if type(ymins)   is not list: ymins   = [ymins]  *len(xdatas)
        if type(ymaxs)   is not list: ymaxs   = [ymaxs]  *len(xdatas)
        if type(coarsen) is not list: coarsen = [coarsen]*len(xdatas)

        # this should cover all the data sets (dimensions should match!)
        xdata_processed  = []
        ydata_processed  = []
        eydata_processed = []
        for n in range(len(xdatas)):

            x  = xdatas[n]
            y  = ydatas[n]
            ey = eydatas[n]*self['scale_eydata'][n]

            # coarsen the data
            if do_coarsen:
                x  =         _functions.coarsen_array(x,     self['coarsen'][n], 'mean')
                y  =         _functions.coarsen_array(y,     self['coarsen'][n], 'mean')
                ey = _n.sqrt(_functions.coarsen_array(ey**2, self['coarsen'][n], 'mean')/self['coarsen'][n])

            if do_trim:
                # Create local mins and maxes
                xmin = xmins[n]
                ymin = ymins[n]
                xmax = xmaxs[n]
                ymax = ymaxs[n]

                # handle "None" limits
                if xmin is None: xmin = min(x)
                if xmax is None: xmax = max(x)
                if ymin is None: ymin = min(y)
                if ymax is None: ymax = max(y)

                # trim the data
                [xt, yt, eyt] = _functions.trim_data_uber([x, y, ey],
                                                      [x>=xmin, x<=xmax,
                                                       y>=ymin, y<=ymax])

                # Catch the over-trimmed case
                if(len(xt)==0):
                    raise Exception("\nDATA SET "+str(n)+": OOPS! OOPS! Specified limits (xmin, xmax, ymin, ymax) eliminate all data! Ignoring.")
                else:
                    x = xt
                    y = yt
                    ey = eyt
                    #ex = ext

            # store the result
            xdata_processed.append(x)
            ydata_processed.append(y)
            eydata_processed.append(ey)

        return xdata_processed, ydata_processed, eydata_processed

    def _process_data(self):
        """
        Processes the data and stores it.
        """
        self._xdatas_processed, self._ydatas_processed, self._eydatas_processed = self.get_processed_data()
        return self

    def _studentized_residuals(self, p, xdatas, ydatas, eydatas):
        """
        Given the supplied parameters, return the studentized residuals of all
        data sets.
        """
        # Get the list of parameter values
        ps = []
        for k in self.p_in.keys(): ps.append(p[k].value)

        # Collect the residuals for each data set
        rs = []
        for n in range(len(ydatas)):
            if n < len(self.f):
                rs.append( (ydatas[n] - self.f[n](xdatas[n], *ps)) / eydatas[n])

        # Concatenate and return
        return rs

    def _studentized_residuals_concatenated(self, p, xdatas, ydatas, eydatas):
        """
        Returns concatenated 1D array of residuals.
        """
        return _n.concatenate(self._studentized_residuals(p,xdatas,ydatas,eydatas))

    def fit(self, autoscale_eydata=False, **kwargs):
        """
        This will try to determine fit parameters using the least squares
        method in lmfit.minimize. This function relies on a previous call
        of set_data() and set_functions().

        Parameters
        ----------
        autoscale_eydata=False : bool
            If True, runs the fit, runs self.autoscale_eydata(), and runs the fit again.
            Use with caution; this can give some sense of the error, but is
            very hard to justify and generally a bad idea.

        **kwargs ar sent to lmfit.minimize().

        Notes
        -----
        results of the fit algorithm are stored in self.results.
        See lmfit.minimize for more information.

        """
        if len(self._xdatas_given)==0 or len(self._ydatas_given)==0:
            raise Exception("No data. Please use set_data() prior to fitting.")
        if self._f_raw is None:
            raise Exception("No functions. Please use set_functions() prior to fitting.")
        if len(self.f) != len(self._xdatas_given):
            raise Exception("The number of functions must equal the number of data sets.")


        # Do the processing once, to increase efficiency
        self._process_data()

        # do the actual optimization
        self.results = _s._lm.minimize(self._studentized_residuals_concatenated, self.p_in,
                                       scale_covar=False, # WTF? Why do I have to specify this? AWFUL default!
                                       args=(self._xdatas_processed, self._ydatas_processed, self._eydatas_processed),
                                       **kwargs)
        self.p_fit = self.results.params

        # If we're supposed to autoscale, temporarily disable autoplot and do so
        if autoscale_eydata: self.autoscale_eydata().fit(**kwargs)

        # plot if necessary
        if self['autoplot'] and not autoscale_eydata: self.plot()

        return self

    def fix(self, *args, **kwargs):
        """
        Turns parameters to constants. As arguments, parameters must be strings.
        As keyword arguments, they can be set at the same time.

        set_constants() is the same as fix(), and you can do all of this using
        self.p_in directly.
        """

        # first set all the keyword argument values
        self.set(**kwargs)

        # get everything into one big list
        pnames = list(args) + list(kwargs.keys())

        # move each pname to the constants
        for pname in pnames:

            # Exists!
            if pname in self.p_in.keys(): self.p_in[pname].vary = False

            # Naughty!
            else: raise Exception("Naughty. '"+pname+"' is not a valid fit parameter name.")

        self.clear_results().plot()
        return self

    set_constants = fix

    def free(self, *args, **kwargs):
        """
        Turns a constant into a parameter. As arguments, parameters must be strings.
        As keyword arguments, they can be set at the same time.

        set_variables() is the same as free(), and you can do all of this
        using self.p_in directly.
        """
        # first set all the keyword argument values
        self.set(**kwargs)

        # get everything into one big list
        pnames = list(args) + list(kwargs.keys())

        # move each pname to the constants
        for pname in pnames:

            # Exists!
            if pname in self.p_in.keys(): self.p_in[pname].vary = True

            # Naughty!
            else: raise Exception("Naughty. '"+pname+"' is not a valid fit parameter name.")

        self.clear_results().plot()
        return self

    set_variables = free

    def get_parameter_names(self):
        """
        Returns a list of parameter names.
        """
        pnames = []
        for pname in self.p_fit: pnames.append(pname)
        return pnames


    def get_constants(self):
        """
        Returns a list of Parameters that are constant.
        """
        r = []
        for pname in self.p_in:
            if not self.p_in[pname].vary: r.append(self.p_in[pname])
        return r

    def get_variables(self):
        """
        Returns a list of Parameters that are constant.
        """
        r = []
        for pname in self.p_in:
            if self.p_in[pname].vary: r.append(self.p_in[pname])
        return r


    def clear_results(self):
        """
        Removes any fit results.
        """
        self.results = self.p_fit = None
        return self

    def _parameters_to_list(self, p):
        """
        Takes the supplied Parameters() instance and returns a list of
        parameter values.
        """
        ps = []
        for pname in p: ps.append(p[pname])
        return ps

    def _evaluate_f(self, n, xdata, p=None):
        """
        Evaluates a single function n for arbitrary xdata and parameters p.
        """
        return self.f[n](xdata, *self._parameters_to_list(p))

    def _evaluate_bg(self, n, xdata, p=None):
        """
        Evaluates a single background function n for arbitrary xdata and parameters p.
        """
        if self.bg[n]: return self.bg[n](xdata, *self._parameters_to_list(p))

    def _format_value_error(self, v, e, pm=" +/- "):
        """
        Returns a string v +/- e with the right number of sig figs.
        """
        # If we have weird stuff
        if not _functions.is_a_number(v) or not _functions.is_a_number(e) \
            or v in [_n.inf, _n.nan, _n.NAN] or e in [_n.inf, _n.nan, _n.NAN]:
            return str(v)+pm+str(e)

        # Normal values.
        try:
            sig_figs = -int(_n.floor(_n.log10(abs(e))))+1
            return str(_n.round(v, sig_figs)) + pm + str(_n.round(e, sig_figs))

        except:
            return str(v)+pm+str(e)

    def get_studentized_residuals(self, p=None):
        """
        Calculates the studentized residuals for each processed data set / function.

        Parameters
        ----------
        p=None
            List of parameter values for the functions. If None, it will use
            the fit results or guess values (if no fit results exist).
        """
        if len(self._xdatas_given)==0 or len(self._ydatas_given)==0: return None

        # Default parameters
        if p == None and self.results: p = self.results.params
        elif not p:                    p = self.p_in

        # Get the processed data and residuals
        self._process_data()
        return self._studentized_residuals(p, self._xdatas_processed, self._ydatas_processed, self._eydatas_processed)

    def get_chi_squareds(self, p=None):
        """
        Returns a list of chi squared for each processed data set.

        p=None means use the fit results if possible, and guess results otherwise.
        """
        # get the residuals
        rs = self.get_studentized_residuals(p)

        # will be None if no data, etc
        if rs:

            # square em and sum em.
            cs = []
            for r in rs: cs.append(sum(r**2))
            return cs

    def get_chi_squared(self, p=None):
        """
        Returns the total chi squared (summed over all processed data sets).

        p=None means use the fit results.
        """
        chi2s = self.get_chi_squareds(p)
        if chi2s: return sum(chi2s)

    def get_degrees_of_freedom(self):
        """
        Returns the number of degrees of freedom for processed data.
        """
        if len(self.f) == 0 or len(self._ydatas_given) == 0:
            raise Exception("You have to call self.set_functions() and self.set_data() first.")

        # Get the studentized residuals, which uses the processed data
        # This should later be changed to get_processed_data()
        xs, ys, eys = self.get_processed_data()

        # calculate the number of points
        N = 0.0
        for i in range(len(xs)): N += len(xs[i])

        return N-len(self.p_in)


    def get_reduced_chi_squareds(self, p=None):
        """
        Returns the reduced chi squared for each processed data set.

        p=None means use the fit results (if defined) then guess values.
        """
        if len(self._xdatas_given)==0 or len(self._ydatas_given)==0: return None

        r = self.get_studentized_residuals(p)

        # In case it's not possible to calculate
        if r is None: return

        # calculate the number of points
        N = 0
        for i in range(len(r)): N += len(r[i])

        # degrees of freedom per point
        dof_per_point = self.get_degrees_of_freedom()/N

        for n in range(len(r)): r[n] = sum(r[n]**2)/(len(r[n])*dof_per_point)

        return r

    def get_reduced_chi_squared(self, p=None):
        """
        Returns the reduced chi squared for all processed data sets.

        p=None means use the fit results if defined, then use guess results.
        """
        chi2 = self.get_chi_squared(p)
        dof  = self.get_degrees_of_freedom()
        if not chi2 or not dof: return None

        # Safe divider.
        return _n.divide(self.get_chi_squared(p), self.get_degrees_of_freedom())

    def autoscale_eydata(self):
        """
        Rescales the error so the next fit will give reduced chi squareds of 1.
        Each data set will be scaled independently, and you may wish to run
        this a few times until it converges.
        """

        if not self.results:
            raise Exception("You must complete a fit first.")
            return

        r = self.get_reduced_chi_squareds()

        # loop over the eydata and rescale
        for n in range(len(r)): self["scale_eydata"][n] *= _n.sqrt(r[n])

        # the fit is no longer valid
        self.clear_results()

        # replot
        if self['autoplot']: self.plot()

        return self



    def plot(self, **kwargs):
        """
        This will plot the data (with error) for inspection.

        Setting self.figures to a figure instance or list of figure instances
        will override the creation of new figures. If you specify
        a list, its length had better be at least as large as the
        number of data sets.

        kwargs will update the settings
        """
        alpha = 0.57 if _s.settings['dark_theme_figures'] else 0.3

        # Make sure there is data to plot.
        if len(self._xdatas_given)==0 or len(self._ydatas_given)==0: return self

        # Make sure the figures is a list
        if not self.figures is None and not type(self.figures) == list: self.figures = [self.figures]

        # Get the trimmed and full processed data
        xts, yts, eyts = self.get_processed_data()
        xas, yas, eyas = self.get_processed_data(do_trim=False)

        # update settings
        for k in kwargs: self[k] = kwargs[k]

        # Calculate all studentized residuals
        if len(self.f) > 0: rt = self.get_studentized_residuals()

        # make a new figure for each data set
        for n in range(len(self._xdatas_given)):
            xt = xts[n]
            xa = xas[n]
            yt = yts[n]
            ya = yas[n]
            eyt = eyts[n]
            eya = eyas[n]
            eyt = eyts[n]

            # get the next figure
            if self.figures is None: fig = _p.figure(self['first_figure']+n)
            else:                    fig = self.figures[n]

            # turn off interactive mode and clear the figure
            _p.ioff()
            fig.clear()

            # set up two axes. One for data and one for residuals.
            a1 = fig.add_subplot(211)            # Residuals
            a2 = fig.add_subplot(212, sharex=a1) # Data
            a1.set_position([0.15, 0.65, 0.75, 0.15])
            a2.set_position([0.15, 0.12, 0.75, 0.50])

            # set the scales
            a1.set_xscale(self['xscale'][n])
            a2.set_xscale(self['xscale'][n])
            a2.set_yscale(self['yscale'][n])

            # Set the window geometry
            #_s.tweaks.set_figure_window_geometry(fig, None, [500,500])

            # Get the function xdata
            fxa = self._get_xdata_for_function(n,xa)
            fxt = self._get_xdata_for_function(n,xt)

            # get the values to subtract from ydata if subtracting the background
            if self['subtract_bg'][n] and not self.bg[n] is None:

                # if we have a fit, use that for the background
                if self.results: p = self.p_fit
                else:            p = self.p_in

                # Get the background data
                d_ya  = self._evaluate_bg(n, xa,  p)
                d_fya = self._evaluate_bg(n, fxa, p)
                d_yt  = self._evaluate_bg(n, xt,  p)
                d_fyt = self._evaluate_bg(n, fxt, p)

            # Otherwise just make some zero arrays
            else:
                d_ya  = 0*xa
                d_fya = 0*fxa
                d_yt  = 0*xt
                d_fyt = 0*fxt



            # PLOT DATA FIRST

            # If we're supposed to, add the "all" data and function
            if self['plot_all_data'][n]:

                # Make it faint.
                style_data  = dict(self['style_data' ][n]); style_data ['alpha'] = alpha

                if self['plot_errors'][n]: a2.errorbar(xa, ya-d_ya, eya, zorder=5, **style_data)
                else:                      a2.plot    (xa, ya-d_ya,      zorder=5, **style_data)

            # add the trimmed data
            if self['plot_errors'][n]:     a2.errorbar(xt, yt-d_yt, eyt, zorder=7, **self['style_data'][n])
            else:                          a2.plot(    xt, yt-d_yt,      zorder=7, **self['style_data'][n])

            # Zoom on just the data for now
            _s.tweaks.auto_zoom(axes=a2, draw=False)

            # PLOT FUNCTIONS

            if n < len(self.f): # If there are any functions to plot


                # Plot the GUESS under the fit
                if self['plot_guess'][n]:

                    # FULL GUESS
                    if self['plot_all_data'][n]:

                        # Make it faint.
                        style_guess = dict(self['style_guess'][n]); style_guess['alpha'] = alpha

                        # FULL background GUESS
                        if self['plot_bg'][n] and self.bg[n] is not None:
                            bg_gya = self._evaluate_bg(n, fxa, self.p_in)
                            a2.plot(fxa, bg_gya-d_fya, zorder=9, **style_guess)

                        # FULL guess
                        gya = self._evaluate_f(n, fxa, self.p_in)
                        a2.plot(fxa, gya-d_fya, zorder=9, **style_guess)

                        # Update the trimmed datas so that the points line up
                        [fxt] = _functions.trim_data_uber([fxt], [fxt>=min(xt), fxt<=max(xt)])

                    # TRIMMED GUESS BACKGROUND

                    # TRIMMED guess background curve
                    if self['plot_bg'][n] and self.bg[n] is not None:
                        bg_gyt = self._evaluate_bg(n, fxt, self.p_in)
                        a2.plot(fxt, bg_gyt-d_fyt, zorder=9, **self['style_guess'][n])

                    # TRIMMED main guess curve
                    gyt = self._evaluate_f (n, fxt, self.p_in)
                    a2.plot(fxt, gyt-d_fyt, zorder=9, **self['style_guess'][n])



                # Plot the FIT if there is one
                if not self.results is None:

                    # FULL FIT
                    if self['plot_all_data'][n]:

                        # Make it faint.
                        style_fit = dict(self['style_fit'][n]); style_fit['alpha'] = alpha

                        # FULL background fit
                        if self['plot_bg'][n] and self.bg[n] is not None:
                            bg_fya = self._evaluate_bg(n, fxa, self.results.params)
                            a2.plot(fxa, bg_fya-d_fya, zorder=10, **style_fit)

                        # FULL fit
                        fya = self._evaluate_f (n, fxa, self.results.params)
                        a2.plot(fxa, fya-d_fya, zorder=10, **style_fit)

                        # Update the trimmed datas so that the points line up
                        [fxt] = _functions.trim_data_uber([fxt], [fxt>=min(xt), fxt<=max(xt)])

                    # TRIMMED FIT BACKGROUND
                    if self['plot_bg'][n] and self.bg[n] is not None:
                        bg_fyt = self._evaluate_bg(n, fxt, self.results.params)
                        a2.plot(fxt, bg_fyt-d_fyt, zorder=10, **self['style_fit'][n])

                    # TRIMMED main curve
                    fyt = self._evaluate_f(n, fxt, self.results.params)
                    a2.plot(fxt, fyt-d_fyt, zorder=10, **self['style_fit'][n])

                if self['plot_guess_zoom'][n]: _s.tweaks.auto_zoom(axes=a2, draw=False)


            # plot the residuals only if there are functions defined
            if len(self.f):

                # If we're supposed to also plot all the data, we have to
                # Manually calculate the residuals. Clunky, I know.
                if self['plot_all_data'][n]:

                    # Figure out what guy to use for the residuals
                    if self.results is None:
                        p = self.p_in
                        style = style_guess
                    else:
                        p = self.p_fit
                        style = style_fit

                    # Calculate them
                    ra = (ya-self._evaluate_f(n, xa, p))/eya

                    # style_data, style_guess, and style_fit should already be faint
                    a1.errorbar(xa, ra, _n.ones(len(ra)), **style_data)

                    # Put the line on top
                    a1.plot([min(xa), max(xa)], [0,0], **style)

                # Figure out what style to use for the line
                if self.results is None: style = self['style_guess'][n]
                else:                    style = self['style_fit'  ][n]

                # Main residuals plot
                if n < len(rt):
                    a1.errorbar (xt, rt[n], _n.ones(len(xt)), **self['style_data'][n])
                    a1.plot([min(xt), max(xt)], [0,0], **style)


            # Tidy up
            yticklabels = a1.get_yticklabels()
            for m in range(2,len(yticklabels)-2): yticklabels[m].set_visible(False)
            for m in a1.get_xticklabels(): m.set_visible(False)

            # Add labels to the axes
            if self['xlabel'][n] is None: a2.set_xlabel('xdata['+str(n)+']')
            else:                         a2.set_xlabel(self['xlabel'][n])
            if self['ylabel'][n] is None:
                ylabel='ydata['+str(n)+']'
                if self['subtract_bg'][n] and self.bg[n] is not None:
                    ylabel=ylabel+' - bg['+str(n)+']'
                a2.set_ylabel(ylabel)
            else:                         a2.set_ylabel(self['ylabel'][n])
            a1.set_ylabel('Studentized\nResiduals')


            # Assemble the title
            wrap = 80
            indent = '      '

            # Include the function names if available
            if n < len(self.f):
                t = _textwrap.fill('Function ('+str(n)+'/'+str(len(self._fnames)-1)+'): y = '+self._fnames[n], wrap, subsequent_indent=indent)
            else:
                t = "No functions defined. Use set_functions()."


            # Now create the strings for Constants: ... and Fit: ...
            constant_strings = []
            fit_strings = []
            for pname in self.p_in:

                # Fit and guess parameters stored in fit_strings
                if self.p_in[pname].vary:
                    if self.results:
                        fit_strings.append(pname+"={:s}".format(self._format_value_error(self.p_fit[pname].value, self.p_fit[pname].stderr, '$\pm$')))
                    else:
                        fit_strings.append(pname+"={:G}".format(self.p_in[pname].value))

                # Constants
                else: constant_strings.append(pname+"={:G}".format(self.p_in[pname].value))

            # do the line about constants
            if len(constant_strings):
                t1 = "Constants: "+', '.join(constant_strings)
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            # If the fit converged
            if self.results and hasattr(self.results, 'covar'):
                t1 = "Fit: "+', '.join(fit_strings) + \
                    ', $\chi^2_r$={} ({} DOF)'.format(
                        self._format_value_error(self.get_reduced_chi_squared(), _n.sqrt(_n.divide(2.0,self.get_degrees_of_freedom())), '$\pm$'),
                        int(self.get_degrees_of_freedom()))
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            # If the fit did not converge
            elif self.results:
                t1 = "Fit did not converge: "+', '.join(fit_strings)
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            # No fit
            else:
                t1 = "Guess: "+', '.join(fit_strings)
                t = t + '\n' + _textwrap.fill(t1, wrap, subsequent_indent=indent)

            # Set the title to t
            a1.set_title(t, fontsize=10, ha='left', position=(0,1))


            # turn back to interactive and show the plots.
            _p.ion()
            if self.figures is None:
                _p.draw()
                _p.show()

        # End of new figure for each data set loop
        return self

    def _get_xdata_for_function(self, n, xdata):
        """
        Generates the x-data for plotting the function.

        Parameters
        ----------
        n
            Which data set we're using
        xdata
            Data set upon which to base this

        Returns
        -------
        float
        """

        # Use the xdata itself for the function
        if self['fpoints'][n] in [None, 0]: return _n.array(xdata)

        # Otherwise, generate xdata with the number of fpoints

        # do exponential ranging if xscale is log
        if self['xscale'][n] == 'log':
            return _n.logspace(_n.log10(min(xdata)), _n.log10(max(xdata)),
                               self['fpoints'][n], True, 10.0)

        # otherwise do linear spacing
        else: return _n.linspace(min(xdata), max(xdata), self['fpoints'][n])

    def trim(self, n='all', x=True, y=True):
        """
        This will set xmin and xmax based on the current zoom-level of the
        figures.

        n='all'     Which figure to use for setting xmin and xmax.
                    'all' means all figures. You may also specify a list.
        x=True      Trim the x-range
        y=True      Trim the y-range
        """
        if len(self._xdatas_given)==0 or len(self._ydatas_given)==0:
            raise Exception("No data. Please use set_data() and plot() prior to trimming.")
            return

        if _functions.is_a_number(n): n = [n]
        elif isinstance(n,str):   n = list(range(len(self._xdatas_given)))

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
                raise Exception("Data "+str(i)+" is not currently plotted.")

        # now show the update.
        self.clear_results()
        if self['autoplot']: self.plot()

        return self

    def untrim(self, n='all'):
        """
        Removes xmin, xmax, ymin, and ymax.

        Parameters
        ----------
        n='all'
            Which data set to perform this action upon. 'all' means all data
            sets, or you can specify a list.
        """
        if len(self._xdatas_given)==0 or len(self._ydatas_given)==0:
            raise Exception("No data. Please use set_data() and plot() prior to zooming.")
            return

        if   _functions.is_a_number(n): n = [n]
        elif isinstance(n,str):     n = list(range(len(self._xdatas_given)))

        # loop over the specified plots
        for i in n:
            self['xmin'][i] = None
            self['xmax'][i] = None
            self['ymin'][i] = None
            self['ymax'][i] = None

        # now show the update.
        self.clear_results()
        if self['autoplot']: self.plot()
        return self

    def zoom(self, n='all', xfactor=2.0, yfactor=2.0):
        """
        This will scale the chosen data set's plot range by the
        specified xfactor and yfactor, respectively, and set the trim limits
        xmin, xmax, ymin, ymax accordingly

        Parameters
        ----------
        n='all'
            Which data set to perform this action upon. 'all' means all data
            sets, or you can specify a list.
        xfactor=2.0
            Factor by which to scale the x range.
        yfactor=2.0
            Factor by which to scale the y range.
        """
        if len(self._xdatas_given)==0 or len(self._ydatas_given)==0:
            raise Exception("No data. Please use set_data() and plot() prior to zooming.")
            return

        # get the data
        xdata, ydata, eydata = self.get_data()

        if   _functions.is_a_number(n): n = [n]
        elif isinstance(n,str):     n = list(range(len(xdata)))

        # loop over the specified plots
        for i in n:
            fig = self['first_figure']+i
            try:
                xmin, xmax = _p.figure(fig).axes[1].get_xlim()
                xc = 0.5*(xmin+xmax)
                xs = 0.5*abs(xmax-xmin)
                self['xmin'][i] = xc - xfactor*xs
                self['xmax'][i] = xc + xfactor*xs

                ymin, ymax = _p.figure(fig).axes[1].get_ylim()
                yc = 0.5*(ymin+ymax)
                ys = 0.5*abs(ymax-ymin)
                self['ymin'][i] = yc - yfactor*ys
                self['ymax'][i] = yc + yfactor*ys
            except:
                raise Exception("Data "+str(fig)+" is not currently plotted.")

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

def load(path=None, first_data_line='auto', filters='*.*', text='Select a file, FACEHEAD.', default_directory='default_directory', quiet=True, header_only=False, transpose=False, strip_nans=False, **kwargs):
    """
    Loads a data file into the databox data class. Returns the data object.

    Most keyword arguments are sent to databox.load() so check there
    for documentation.(if their function isn't obvious).

    Parameters
    ----------
    path=None
        Supply a path to a data file; None means use a dialog.

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

    strip_nans = False
        If True, runs databox.strip_nans() after loading, which removes all the
        trailing nan values (useful for files with mismatched column lengths).

    Additioinal optional keyword arguments are sent to spinmob.data.databox(),
    so check there for more information.
    """
    d = databox(**kwargs)
    d.load_file(path=path, first_data_line=first_data_line,
                filters=filters, text=text, default_directory=default_directory,
                header_only=header_only, strip_nans=strip_nans)

    if not quiet: print("\nloaded", d.path, "\n")

    if transpose: return d.transpose()
    return d

def load_multiple(paths=None, first_data_line="auto", filters="*.*", text="Select some files, FACEHEAD.", default_directory="default_directory", quiet=True, header_only=False, transpose=False, strip_nans=False, **kwargs):
    """
    Loads a list of data files into a list of databox data objects.
    Returns said list.

    Parameters
    ----------
    path=None
        Supply a path to a data file; None means pop up a dialog.

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

    strip_nans = False
        If True, runs databox.strip_nans() after loading, which removes all the
        trailing nan values (useful for files with mismatched column lengths).


    Optional keyword arguments are sent to spinmob.data.load(), so check there for more information.
    """
    if paths is None: paths = _s.dialogs.load_multiple(filters, text, default_directory)
    if paths is None : return

    datas = []
    for path in paths:
        if _os.path.isfile(path): datas.append(load(path=path, first_data_line=first_data_line,
                filters=filters, text=text, default_directory=default_directory,
                header_only=header_only, transpose=transpose, strip_nans=strip_nans, **kwargs))

    return datas



if __name__ == '__main__':

#    _s.plot.xy.function()
#    _s.tweaks.auto_zoom()
#    a = _s.pylab.gca()

    # Load a test file and fit it, making sure "f" is defined at each step.
    f = fitter(xmin=2, plot_guess_zoom=True, plot_all_data=True)
    f.set_data()
    f.set_functions('stuff*cos(x*other_stuff)+final_stuff', 'stuff, other_stuff, final_stuff', bg='final_stuff')
    f.fit()


