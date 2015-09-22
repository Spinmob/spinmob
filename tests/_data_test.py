# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""

import os  # Used for loading fixtures
import numpy as _n
import spinmob as sm
_dt = sm._data

import unittest as _ut
from unittest import TestLoader as _TL

# Not sure how to handle ~line 125 where if a path is not specified, the user
# manually enters one.  This is annoying to test.  Has to be a way to handle
# this nicely.


def test():
    """
    Run all tests in this module.
    """

    suite_databox  = _TL().loadTestsFromTestCase(Test_databox)
    suite_fitter  = _TL().loadTestsFromTestCase(Test_fitter)

    suites = [suite_databox, suite_fitter]
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
        self.module_path = self.dt_path.rpartition('spinmob')
        self.module_path = self.module_path[0]
        
        self.fixtures_path = os.path.join('spinmob', 'tests', 'fixtures', 'data_types')
        midPath = os.path.join(self.module_path, self.fixtures_path)        
        
        filename = 'simple_xy_data.dat'
        self.data_path = os.path.join(midPath, filename)

        # setup a default databox to be used for testing.
        self.databox = _dt.databox()
        
        # Path to a different data set fixture, with headers
        filename = 'CSV_xy.dat'
        self.data_path2 = os.path.join(midPath, filename)                                      
                                      
        self.databoxCSV = _dt.databox(delimiter=', ')

        filename = 'headers_xy.dat'
        self.data_path3 = os.path.join(midPath, filename)


    def tearDown(self):
        """
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


    def test_execute_script(self):
        self.databox.load_file(path=self.data_path)
        
        val = self.databox.execute_script('3.0 + x/y - self[0] where x=2.0*c(0); y=c(1)')
        val = _n.around(val, 1)  # Round to 1 decimal place
        val = val.tolist()  # Convert numpy array to a list
        val = val[0:5]   # Just check the first five elements
        
        exp = [993.9, 713.0, 70.4, -14.7, -51.6]      
        self.assertListEqual(val, exp)


    def test___len__(self):
        self.databox.load_file(path=self.data_path)   
        val = self.databox.__len__() 
        exp = 2
        self.assertEqual(val, exp)
        
    def test___setitem___str(self):
        self.databox.load_file(path=self.data_path)   
        self.databox.__setitem__(0, 'test_item')
        val = self.databox[0]
        exp = 'test_item'
        self.assertEqual(val, exp)

    def test___setitem___int(self):
        self.databox.load_file(path=self.data_path) 
        self.databox.__setitem__(2, [78, 87])
        val = self.databox[2]
        val = val.tolist()
        exp = [78, 87]
        self.assertListEqual(val, exp)        
        
    def test___getslice__(self):
        self.databox.load_file(path=self.data_path) 
        val = self.databox.__getslice__(0, 1)
        val = val[0]
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements
        exp = [85.0, 90.0, 95.0, 100.0, 105.0] 
        self.assertListEqual(val, exp)            
        
    def test___init__kwargs(self):
        # TODO: is this a valid test?  Did anything pass?
        d = sm.data.databox(test_kwarg='test_value')
        

    def test_h_str(self):
        self.databox.load_file(path=self.data_path3)         
        val = self.databox.h('header1')
        exp = 'value1'
        self.assertEqual(val, exp)          

    def test_h_None(self):
        """
        This should have spinmob print out an error message.
        
        TODO: possible better way of handling/collecting this error message
        while testing.
        """
        self.databox.load_file(path=self.data_path3)  
        val = self.databox.h()
        exp = None
        self.assertEqual(val, exp)          

    def test_h_Fragment(self):
        """
        This should have spinmob print out an error message.
        
        TODO: possible better way of handling/collecting this error message
        while testing.
        """
        self.databox.load_file(path=self.data_path3) 
        val = self.databox.h('fragment')
        exp = None
        self.assertEqual(val, exp)          

    def test_h_GoodFragment(self):
        """
        This should have spinmob print out an error message.
        
        TODO: possible better way of handling/collecting this error message
        while testing.
        """
        self.databox.load_file(path=self.data_path3) 
        val = self.databox.h('header')
        exp = 'value1'
        self.assertEqual(val, exp)   

    def test_pop_column_ckey(self):
        self.databox.load_file(path=self.data_path3) 
        val = self.databox.pop_column('x_data')        
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements        
        exp = [85.0, 90.0, 95.0, 100.0, 105.0] 
        self.assertListEqual(val, exp) 

    def test_pop_column_int(self):
        self.databox.load_file(path=self.data_path3) 
        val = self.databox.pop_column(0)
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements        
        exp = [85.0, 90.0, 95.0, 100.0, 105.0] 
        self.assertListEqual(val, exp)       

    def test_pop_column_neg(self):
        """
        Test spinmob error message for looking for a column that does not exist
        
        TODO: better way to collect these error messsages.
        """
        self.databox.load_file(path=self.data_path3) 
        val = self.databox.pop_column(-2)
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements        
        exp = [85.0, 90.0, 95.0, 100.0, 105.0] 
        self.assertListEqual(val, exp)     



class Test_fitter(_ut.TestCase):
    """
    Test class for fitter.
    """
    debug = False    
    
    def setUp(self):
        """
        Load data
        """
        # Path to the spinmob module
        self.dt_path    = os.path.dirname(_dt.__file__)
        self.module_path = self.dt_path.rpartition('spinmob')
        self.module_path = self.module_path[0]
        
        self.fixtures_path = os.path.join('spinmob', 'tests', 'fixtures', '_data', 'fitter')
        midPath = os.path.join(self.module_path, self.fixtures_path)        
        
        filename = 'Bevington Ex 7p1.dat'
        self.data_path = os.path.join(midPath, filename)

        # setup a default databox to be used for testing.
        self.databox = _dt.databox()


    def tearDown(self):
        """
        """
        self.dt_path       = None
        self.module_path   = None
        self.data_path     = None
        self.fixtures_path = None
        self.databox       = None

    def test_bevington_chi_squared(self):
        """
        Test against Example 7.1 in Bevington.
        """
        self.databox.load_file(path=self.data_path)
        func = 'a1 + a2*x + a3*x**2.'
        params = 'a1=-1., a2=0.04, a3=0.00006'
        f = _dt.fitter(f=func, p=params)
        f.set_data(self.databox[0], self.databox[1])
        f.fit()


if __name__ == "__main__":
    _ut.main()