# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""
import os      as _os # For loading fixtures
import numpy   as _n
import spinmob as _s
_d = _s.data

import unittest as _ut

# Not sure how to handle ~line 125 where if a path is not specified, the user
# manually enters one.  This is annoying to test.  Has to be a way to handle
# this nicely.


class Test_databox(_ut.TestCase):
    """
    Test class for databox.
    """

    def setUp(self):
        """
        Load data
        """
        # Path to the spinmob module
        self.dt_path        = _os.path.dirname(_d.__file__)
        self.module_path    = self.dt_path.rpartition('spinmob')
        self.module_path    = self.module_path[0]
        self.fixtures_path  = _os.path.join('spinmob', 'tests', 'fixtures', 'data')
        self.data_path      = _os.path.join(self.module_path, self.fixtures_path)

#        filename = 'simple_xy_data.dat'
#        self.data_path = _os.path.join(midPath, filename)
#
#        # setup a default databox to be used for testing.
#        d = _dt.databox()
#
#        # Path to a different data set fixture, with headers
#        filename = 'CSV_xy.dat'
#        self.data_path2 = _os.path.join(midPath, filename)
#
#        dCSV = _dt.databox(delimiter=', ')
#
#        filename = 'headers_xy.dat'
#        self.data_path3 = _os.path.join(midPath, filename)

    def tearDown(self):
        """
        """
        return

    def test___repr__Default(self):
        """
        Test default output of __repr__ for a new databox.
        """
        d = _d.databox()
        v = d.__repr__()
        self.assertEqual(v, "<databox instance: 0 headers, 0 columns>")

    def test_load_several_files(self):
        
        d = _s.data.load(path=_os.path.join(self.data_path, "simple_xy_data.dat"))
        self.assertEqual(d[0][0], 85.0)
        self.assertEqual(d.delimiter, None)
        
        d = _s.data.load(path=_os.path.join(self.data_path, "CSV_xy.dat"))
        self.assertEqual(d[0][1], 90.0)
        self.assertEqual(d.delimiter, ',')
        
        d = _s.data.load(path=_os.path.join(self.data_path, "mixed_complex_data.dat"))
        self.assertEqual(d[0][4], 105+45j)
        self.assertEqual(d.delimiter, None)
        
    def test_pop_data_point(self):
        d = _d.load(path=_os.path.join(self.data_path, "simple_xy_data.dat"))
        l = len(d[0])
        
        # Check a value of the loaded file, first level
        val = d.pop_data_point(3)

        # The expected response
        exp = [100.0, 2.43]
        self.assertEqual(val, exp)
        self.assertEqual(len(d[0]), l-1)

    def test_execute_script(self):
        d = _d.load(path=_os.path.join(self.data_path, "simple_xy_data.dat"))
        
        val = d.execute_script('3.0 + x/y - self[0] where x=2.0*c(0); y=c(1)')
        val = _n.around(val, 1)  # Round to 1 decimal place
        val = val.tolist()  # Convert numpy array to a list
        val = val[0:5]   # Just check the first five elements

        exp = [993.9, 713.0, 70.4, -14.7, -51.6]
        self.assertListEqual(val, exp)

    def test___len__(self):
        d = _d.load(path=_os.path.join(self.data_path, "simple_xy_data.dat"))
        val = d.__len__()
        exp = 2
        self.assertEqual(val, exp)

    def test___setitem___str(self):
        d = _d.load(path=_os.path.join(self.data_path, "simple_xy_data.dat"))
        d.__setitem__(0, 'test_item')
        val = d[0]
        exp = 'test_item'
        self.assertEqual(val, exp)

    def test___setitem___int(self):
        d = _d.load(path=_os.path.join(self.data_path, "simple_xy_data.dat"))
        d.__setitem__(2, [78, 87])
        val = d[2]
        val = val.tolist()
        exp = [78, 87]
        self.assertListEqual(val, exp)

    def test___getslice__(self):
        d = _d.load(path=_os.path.join(self.data_path, "simple_xy_data.dat"))
        val = d.__getslice__(0, 1)
        val = val[0]
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements
        exp = [85.0, 90.0, 95.0, 100.0, 105.0]
        self.assertListEqual(val, exp)

    def test_h_str(self):
        d = _d.load(path=_os.path.join(self.data_path, "headers_xy.dat"))
        val = d.h('header1')
        exp = 'value1'
        self.assertEqual(val, exp)

    def test_h_None(self):
        """
        This should have spinmob print out an error message.
        """
        d = _d.load(path=_os.path.join(self.data_path, "headers_xy.dat"))
        val = d.h()
        exp = None
        self.assertEqual(val, exp)

    def test_h_Fragment(self):
        """
        This should have spinmob print out an error message.

        TODO: possible better way of handling/collecting this error message
        while testing.
        """
        d = _d.load(path=_os.path.join(self.data_path, "headers_xy.dat"))
        val = d.h('fragment')
        exp = None
        self.assertEqual(val, exp)

    def test_h_GoodFragment(self):
        """
        This should have spinmob print out an error message.

        TODO: possible better way of handling/collecting this error message
        while testing.
        """
        d = _d.load(path=_os.path.join(self.data_path, "headers_xy.dat"))
        val = d.h('header')
        exp = 'value1'
        self.assertEqual(val, exp)

    def test_pop_column_ckey(self):
        d = _d.load(path=_os.path.join(self.data_path, "headers_xy.dat"))
        val = d.pop_column('x_data')
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements
        exp = [85.0, 90.0, 95.0, 100.0, 105.0]
        self.assertListEqual(val, exp)

    def test_pop_column_int(self):
        d = _d.load(path=_os.path.join(self.data_path, "headers_xy.dat"))
        val = d.pop_column(0)
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements
        exp = [85.0, 90.0, 95.0, 100.0, 105.0]
        self.assertListEqual(val, exp)

    def test_pop_column_neg(self):
        """
        Test spinmob error message for looking for a column that does not exist

        TODO: better way to collect these error messsages.
        """
        d = _d.load(path=_os.path.join(self.data_path, "headers_xy.dat"))
        
        val = d.pop_column(-2)
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements
        exp = [85.0, 90.0, 95.0, 100.0, 105.0]
        self.assertListEqual(val, exp)

    def test_load_single_row_of_data(self):
        """
        Test that a file with a single row of data can be loaded.
        """
        d = _d.load(path=_os.path.join(self.data_path, "one_row_of_data.dat"))
        
        # TODO: need a better test that only tests the load.
        value = d[0][0]
        expected_value = 85.0
        self.assertEqual(value, expected_value)


    def test_bevington_fit(self):
        """
        Test against Example 7.1 in Bevington.
        """
        # Load a test file and fit it, making sure "f" is defined at each step.
        d = _s.data.load(path=_os.path.join(self.data_path,"Bevington Ex 7p1.csv"))
        f = _d.fitter('a1 + a2*x + a3*x**2.', 'a1=-1., a2=0.04, a3=0.00006', autoplot=False)
        f.__repr__()
        f.set_data(d[0], d[1], 0.05)
        f.__repr__()
        f.fit()
        f.__repr__()
        
        # Check that the reduced chi^2 is close to the 1.5 value of Bevington
        r = f.reduced_chi_squareds()
        self.assertIs(type(r), list)
        self.assertAlmostEqual(r[0], 1.5, 1)
        

        

if __name__ == "__main__":
    _ut.main()
