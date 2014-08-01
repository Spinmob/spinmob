# -*- coding: utf-8 -*-
"""

"""

import os  # Used for loading fixtures
import spinmob as sm
_dt = sm._data_types

import unittest as _ut
from unittest import TestLoader as _TL


def test():
    """
    Run all tests in this module.
    """

    suite_databox  = _TL().loadTestsFromTestCase(Test_databox)

    suites = [suite_databox]

    alltests = _ut.TestSuite(suites)


    _ut.TextTestRunner(verbosity=2).run(alltests)




class Test_databox(_ut.TestCase):
    """
    Test class for databox.
    """
    debug = False    
    
    def setUp(self):
        """
        Load data
        """

        # Path to the spinmob module
        self.dt_path    = os.path.dirname(_dt.__file__)
        if self.debug: print "self.dt_path =", self.dt_path
        self.module_path = self.dt_path.rpartition('spinmob')
        self.module_path = self.module_path[0]
        if self.debug: print "self.module_path=", self.module_path
        
        self.fixtures_path = os.path.join('spinmob', 'tests', 'fixtures', 'data_types')
        midPath = os.path.join(self.module_path, self.fixtures_path)        
        
        filename = 'simple_xy_data.dat'
        self.data_path = os.path.join(midPath, filename)
        if self.debug: print "self.data_path =", self.data_path

        # setup a default databox to be used for testing.
        self.databox = _dt.databox()
        
        # Path to a different data set fixture, with headers
        filename = 'CSV_xy.dat'
        self.data_path2 = os.path.join(midPath, filename)                                      
                                      
        self.databoxCSV = _dt.databox(delimiter=', ')

        filename = 'headers_xy.dat'
        self.data_path3 = os.path.join(midPath, filename)

        # This is not a good idea, as you get all the spinmob prints
        #self.databoxDebug = _dt.databox(debug=True, delimiter=',    ')


    def tearDown(self):
        """
        Cleanup procedure for the imageData and backgroundData
        """

        self.dt_path       = None
        self.module_path   = None
        self.data_path     = None
        self.fixtures_path = None
        self.databox       = None


    def test___repr__Default(self):
        """
        Test default output of __repr__ for a new databox.
        """
        val = self.databox.__repr__()
        exp = "\nDatabox Instance\n  header elements: 0\n  columns of data: 0\n"

#        if self.debug:
#            print "function output procedure path = ", val
#            print "correct procedure path = ", out
        self.assertEqual(val, exp)



    def test_load_file(self):
        self.databox.load_file(path=self.data_path)
        
        # Check a value of the loaded file, first level
        val = self.databox[0][0]
        
        # The expected response
        exp = 85.0

        self.assertEqual(val, exp)

    def test_defaultDelimiter(self):
        val = self.databox.delimiter
        exp = None

        self.assertEqual(val, exp)        

    def test_CSVDelimiter(self):
        val = self.databoxCSV.delimiter
        exp = ', '
        
        self.assertEqual(val, exp)        


    def test_load_fileCSV(self):
        """
        Test loading a CSV file
        """
        self.databoxCSV.load_file(path=self.data_path2)

        # Check a value of the loaded file, first level
        val = self.databoxCSV[0][1]
        
        # The expected response
        exp = 90.0

        self.assertEqual(val, exp)


    def test_pop_data_point(self):
        self.databox.load_file(path=self.data_path)
        
        
        # Check a value of the loaded file, first level
        val = self.databox.pop_data_point(3, ckeys=[0])
        
        # The expected response
        exp = [100.0]      
        self.assertEqual(val, exp)



if __name__ == "__main__":
    #test()
    _ut.main()













