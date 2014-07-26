import os as _os
import _dialogs

# do this so all the scripts will work with all the numpy functions
import numpy as _n


######################
# Random functions
######################

def join(array_of_strings, delimiter=' '):
    if array_of_strings == []: return ""

    if delimiter==None: delimiter=' '

    output = str(array_of_strings[0])
    for n in range(1, len(array_of_strings)):
        output += delimiter + str(array_of_strings[n])
    return(output)

def elements_are_numbers(array, start_index=0, end_index=-1):
    if len(array) == 0: return 0

    output_value=1

    if end_index < 0: end_index=len(array)-1
    for n in array:
        try: float(n)
        except:
            try:
                complex(n)
                output_value=2
            except:
                try:
                    complex(n.replace('(','').replace(')',''))
                    output_value=2
                except:
                    return 0
    return output_value
    
def index(value, array):
    for n in range(0,len(array)):
        if value == array[n]:
            return(n)
    return(-1)

def is_iterable(a):
    """
    Test if something is iterable.
    """
    return hasattr(a, '__iter__')







###################################################
# This is the base class, which currently rocks.
###################################################

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
        
        # break up the path into parts and take the last bit (and take a stab at the legend string)
        self.legend_string = path.split(_os.path.sep)[-1]
        if self.legend_string[0] == '_': self.legend_string = '|' + self.legend_string


        ##### read in the header information
        
        ckeys_line = -2
        for n in range(len(lines)):
            
            # split the line by the delimiter
            s = lines[n].strip().split(self.delimiter)

            # remove a trailing whitespace entry if it exists.
            if len(s) and s[-1].strip() == '': s.pop(-1)

            # first check and see if this is a data line (all elements are numbers)
            if first_data_line=="auto" and elements_are_numbers(s):
                # we've reached the first data line
                first_data_line = n
                
                # quit the header loop
                break;


            ### now we know it's a header line

            # first thing to try is simply evaluating the remaining string
            try:
                hkey      = s[0]
                remainder = join(s[1:], ' ')
                self.insert_header(hkey, eval(remainder, _n.__dict__))
                
            except: pass

        # now we have a valid set of column ckeys one way or another, and we know first_data_line.
        if header_only: return self

        # Make sure first_data_line isn't None (which happens if there's no data)
        if first_data_line == "auto":
            if not quiet: print "\nCould not find a line of pure data! Perhaps check the delimiter?"
            if not quiet: print "The default delimiter is whitespace. For csv files, set delimiter=','\n"
            return self



        ##### at this point we've found the first_data_line, 
        ##### and ckeys_line is correct or -2

        # count the number of data columns
        column_count = len(lines[first_data_line].strip().split(self.delimiter))

        # check to see if ckeys line is first_data_line-1, and that it is equal in length to the
        # number of data columns. If it isn't, it's a false ckeys line
        if ckeys_line == first_data_line-1 and len(self.ckeys) >= column_count:
            # it is valid.
            # if we have too many column keys, mention it
            if len(self.ckeys) > column_count:
                if not quiet: print "Note: more ckeys than columns (stripping extras)"

            # remove this line from the header
            try:    self.pop_header(self.ckeys[0])
            except: 
                if not quiet: print "Couldn't pop column labels from header. Weird."

        else:
            # it is an invalid ckeys line. Generate our own!
            self.ckeys = []
            for m in range(0, column_count): self.ckeys.append("c"+str(m))

        # for good measure, make sure to trim down the ckeys array to the size of the data columns
        for n in range(column_count, len(self.ckeys)): self.ckeys.pop(-1)

        # initialize the columns arrays
        # I did benchmarks and there's not much improvement by using numpy-arrays here.
        for label in self.ckeys: self.columns[label] = []

        
        # now loop over the remainder of the file
        z = _n.genfromtxt(path, delimiter=self.delimiter, skip_header=first_data_line).transpose()       
        
        
        # Add all the columns
        for n in range(len(self.ckeys)): self[self.ckeys[n]] = z[n]
        
       
        # now, as an added bonus, rename some of the obnoxious headers
        for k in self.obnoxious_ckeys:
            if self.columns.has_key(k):
                self.columns[self.obnoxious_ckeys[k]] = self.columns[k]
                
        return self

    def save_file(self, path="ask", filters="*.dat", force_overwrite=False):
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
        
        # now write the ckeys
        elements = []
        for ckey in self.ckeys: elements.append(str(ckey))
        f.write(join(elements,delimiter)+"\n")

        # now loop over the data
        for n in range(0, len(self[0])):
            # loop over each column
            elements = []
            for m in range(0, len(self)):
                # write the data if there is any, otherwise, placeholder ("x")
                if n < len(self[m]):
                    elements.append(str(self[m][n]))
                else:
                    elements.append('_')
            f.write(join(elements, delimiter)+"\n")


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
        if not is_iterable(script):

            # special case
            if script == None: return None

            # get the expression and variables dictionary
            [expression, v] = self._parse_script(script)
            
            # if there was a problem parsing the script            
            if v == None: 
                print "ERROR: Could not parse '"+script+"'"                
                return None  
            
            # get all the numpy stuff too
            g = _n.__dict__
            g.update(v)
            
            # otherwise, evaluate the script using python's eval command
            return eval(expression, g)
        
        # Otherwise, this is a list of scripts. Make the recursive call.
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

        # start with the globals list
        globbies = globals()

        # update the globals with supplied extras
        globbies.update(self.extra_globals)

        # override the important ones!
        globbies.update({'h':self.h, 'c':self.c, 'd':self, 'self':self})
        
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
                b = eval(script, globbies)
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
        stuff = {}
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

        # incorporate the globbies so other functions can eval() with things
        # like c('this')
        stuff.update(globbies)

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

    def get_XYZ(self, xaxis=None, yaxis=None):

        """
        This will assemble the X, Y, Z data for a 2d colorplot or surface.

        yaxis=None          What values to use for the y-axis data. "first" means take the first column
                            yaxis=None means just use bin number
        xaxis=None          What values to use for the x-axis data, can be a header array
                            xaxis="first" means pop off the first row of the data
        xcoarsen, ycoarsen  How much to coarsen the columns or rows

        """


        # next we assemble the 2-d array for the colorplot
        Z=[]
        for c in self.ckeys:
            # transform so the image plotting has the same orientation as the data
            # in the file itself.
            col = list(self.columns[c])
            col.reverse()
            Z.append(col)

        # initialize the axis labels
        X=[]
        for n in range(len(Z)): X.append(n)
        
        Y=[]
        for n in range(len(Z[0])): Y.append(n)
        Y.reverse()

        # now if we're supposed to, pop off the first column as Y labels
        if yaxis=="first":

            # just pop off the first column (Z columns are already reversed)
            Y = Z.pop(0)
            
            # pop the first element of the X-data
            X.pop(0)


        # otherwise, it's a column value
        elif not yaxis==None:
            Y = list(self.c(yaxis))
            Y.reverse()
            


        # if we're supposed to, pop off the top row for the x-axis values
        if xaxis == "first":
            X = []
            for n in range(len(Z)):
                X.append(Z[n].pop(-1))

            
            # pop the first element of the Y-data
            Y.pop(-1)

        # otherwise, if we specified a row from the header, use that
        elif not xaxis==None:
            X = array(self.h(xaxis))

            # trim X down to the length of the Zd.ZX row
            X.resize(len(Z[:])-1)



        Z = Z.transpose()

        return X, Y, Z


    


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

            

