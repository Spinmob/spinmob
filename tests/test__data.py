# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""
import os      as _os # For loading fixtures
import numpy   as _n
import spinmob as _s

import unittest as _ut


class Test_databox(_ut.TestCase):
    """
    Test class for databox.
    """

    def setUp(self):
        """
        Load data
        """
        # Path to the spinmob module
        self.data_path = _os.path.join(_os.path.dirname(_s.__file__), 'tests', 'fixtures', 'data_files')

    def tearDown(self):
        """
        """
        return

    def test_load_file(self):
        d = _s.data.databox()
        d.load_file(path=_os.path.join(self.data_path, 'basic.dat'))
        self.assertEqual(d[0][0], 85.0)

    def test_default_delimiter(self):
        d = _s.data.databox()
        self.assertEqual(d.delimiter, None)

    def test_set_delimiter(self):
        d = _s.data.databox(delimiter=',')
        self.assertEqual(d.delimiter, ',')

    def test_autoload_csv(self):
        """
        Test loading a CSV file
        """
        d = _s.data.load(path=_os.path.join(self.data_path, "comma.dat"))
        self.assertEqual(d[0][1], 90.0)
        self.assertEqual(d.delimiter, ',')

    def test_autoload_semicolon(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "semicolon.dat"))
        self.assertEqual(d[0][1], 90.0)
        self.assertEqual(d.delimiter, ';')

    def test_pop_data_point(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "basic.dat"))
        
        # length
        l = len(d[0])
        
        # Check a value of the loaded file, first level
        val = d.pop_data_point(3)

        # The expected response
        exp = [100.0, 2.43]
        self.assertEqual(val, exp)
        self.assertEqual(len(d[0]), l-1)

    def test_execute_script(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "basic.dat"))
        
        val = d.execute_script('3.0 + x/y - self[0] where x=2.0*c(0); y=c(1)')
        val = _n.around(val, 1)  # Round to 1 decimal place
        val = val.tolist()  # Convert numpy array to a list
        val = val[0:5]   # Just check the first five elements

        exp = [993.9, 713.0, 70.4, -14.7, -51.6]
        self.assertListEqual(val, exp)

    def test___len__(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "basic.dat"))
        val = d.__len__()
        exp = 2
        self.assertEqual(val, exp)

    def test___setitem___str(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "basic.dat"))
        d.__setitem__(0, 'test_item')
        val = d[0]
        exp = 'test_item'
        self.assertEqual(val, exp)

    def test___setitem___int(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "basic.dat"))
        d.__setitem__(2, [78, 87])
        val = d[2]
        val = val.tolist()
        exp = [78, 87]
        self.assertListEqual(val, exp)

    def test___getslice__(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "basic.dat"))
        val = d[0:1]
        val = val[0]
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements
        exp = [85.0, 90.0, 95.0, 100.0, 105.0]
        self.assertListEqual(val, exp)

    def test_h_str(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "headers.dat"))
        val = d.h('header1')
        exp = 'value1'
        self.assertEqual(val, exp)

    def test_h_None(self):
        """
        This should have spinmob print out an error message.
        """
        d = _s.data.load(path=_os.path.join(self.data_path, "headers.dat"))
        val = d.h()
        exp = None
        self.assertEqual(val, exp)

    def test_h_Fragment(self):
        """
        This should have spinmob print out an error message.

        TODO: possible better way of handling/collecting this error message
        while testing.
        """
        d = _s.data.load(path=_os.path.join(self.data_path, "headers.dat"))
        val = d.h('fragment')
        exp = None
        self.assertEqual(val, exp)

    def test_h_GoodFragment(self):
        """
        This should have spinmob print out an error message.

        TODO: possible better way of handling/collecting this error message
        while testing.
        """
        d = _s.data.load(path=_os.path.join(self.data_path, "headers.dat"))
        val = d.h('header')
        exp = 'value1'
        self.assertEqual(val, exp)

    def test_pop_column_ckey(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "headers.dat"))
        val = d.pop_column('x_data')
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements
        exp = [85.0, 90.0, 95.0, 100.0, 105.0]
        self.assertListEqual(val, exp)

    def test_pop_column_int(self):
        d = _s.data.load(path=_os.path.join(self.data_path, "headers.dat"))
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
        d = _s.data.load(path=_os.path.join(self.data_path, "headers.dat"))
        val = d.pop_column(-2)
        val = val.tolist()
        val = val[0:5]   # Just check the first five elements
        exp = [85.0, 90.0, 95.0, 100.0, 105.0]
        self.assertListEqual(val, exp)

    def test_load_single_row(self):
        """
        Test that a file with a single row of data can be loaded.
        """
        d = _s.data.load(path=_os.path.join(self.data_path, "one_row.dat"))
        
        # TODO: need a better test that only tests the load.
        value = d[0][0]
        expected_value = 85.0
        self.assertEqual(value, expected_value)

    def test_load_single_column_of_data(self):
        """
        Test that a file with a single column of data can be loaded.
        """
        d = _s.data.load(path=_os.path.join(self.data_path, 'one_column.dat'))

        value = d[0].tolist()
        expected_value = [85., 42.]
        self.assertListEqual(value, expected_value)


class Test_fitter(_ut.TestCase):
    """
    Test class for fitter.
    """
    debug = False

    def setUp(self):
        """
        Test against Example 7.1 in Bevington.
        """
        # Load a test file and fit it, making sure "f" is defined at each step.
        d = _s.data.load(path=_os.path.join(self.data_path,"Bevington Ex 7p1.csv"))
        f = _s.data.fitter('a1 + a2*x + a3*x**2.', 'a1=-1., a2=0.04, a3=0.00006', autoplot=False)
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
