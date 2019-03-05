# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""
import os      as _os # For loading fixtures
import numpy   as _n
import spinmob as _s

import unittest as _ut

d = None
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

    def test_load_save_binary(self):
        global d
        
        # Write a confusing binary file.
        d = _s.data.databox(delimiter=',')
        d.h(poo = 32)
        d['pants']       = [1,2,3,4,5]
        d['shoes,teeth'] = [1,2,1]
        d.save_file('test_binary.txt',binary='float16')
        
        # Load said binary
        d = _s.data.load('test_binary.txt')
        
        


        # Now modify it and save again.
        d.h(SPINMOB_BINARY='int64', test=['1,2,3,4',1,2,3,4])
        d['new_column'] = [44]
        d.delimiter = None
        d.save_file('test_binary.txt')
        
        # Load it again
        d = _s.data.load('test_binary.txt')
        self.assertEqual(len(d.ckeys), 3)
        self.assertEqual(len(d.hkeys), 3)
        self.assertEqual(len(d[2]),    1)
        self.assertEqual(d[1][1],      2)
        
        # Clean up.
        _os.remove('test_binary.txt')
        _os.remove('test_binary.txt.backup')

        

f = None
class Test_fitter(_ut.TestCase):
    """
    Test class for fitter.
    """
    debug = False

    def setUp(self): 
        # Path to the spinmob module
        self.data_path = _os.path.join(_os.path.dirname(_s.__file__), 'tests', 'fixtures', 'data_files')
        
        self.x1 = [0,1,2,3,4,5,6,7]
        self.y1 = [10,1,2,1,3,4,5,3]
        self.y2 = [2,1,2,4,5,2,1,5]
        self.ey = [0.3,0.5,0.7,0.9,1.1,1.3,1.5,1.7]
        self.plot_delay = 0.1
        
        return
        
    def test_basics_function_first(self):
        """
        Basic tests for a simple example smallish data set.
        """
        # Load a test file and fit it, making sure "f" is defined at each step.
        f = _s.data.fitter()
        f.__repr__()
        
        f.set_functions('a1 + a2*x + a3*x**2.', 'a1=-1., a2=0.04, a3=0.00006')
        f.__repr__()
        f.plot()

        f.set_data(self.x1, self.y1, 0.5)
        _s.pylab.ginput(timeout=self.plot_delay)
        f.__repr__()
                
        f.fit()
        _s.tweaks.set_figure_window_geometry(position=[0,0])
        _s.pylab.ginput(timeout=self.plot_delay)
        f.__repr__()
        
        # Check that the reduced chi^2 is roughly correct
        r = f.reduced_chi_squareds()
        self.assertIs(type(r), list)
        self.assertAlmostEqual(r[0], 29.2238, 2)
    
        # trim the data
        f.set(xmin=1.5, xmax=6.5)
        _s.pylab.ginput(timeout=self.plot_delay)
        f.__repr__()
        
        f.fit()
        _s.pylab.ginput(timeout=self.plot_delay)
        f.__repr__()
        
        # trim the data and test what happens when there are 0 DOF
        f.set(xmin=1.5, coarsen=2, plot_all_data=True, plot_guess_zoom=True)
        _s.pylab.ginput(timeout=self.plot_delay)
        f.__repr__()
        
        f.fit()
        _s.pylab.ginput(timeout=self.plot_delay)
        f.__repr__()
        
        # Change the first figure
        f(first_figure=1)
        
        # Change the function and starting plot, then refit
        f.set_functions('a*x+b', 'a,b')
        _s.tweaks.set_figure_window_geometry(position=[0,400])
        _s.pylab.ginput(timeout=self.plot_delay)
        f.__repr__()
        
        f.fit()
        _s.pylab.ginput(timeout=self.plot_delay)
        f.__repr__()
        
        # Coarsen and untrim

    
    def test_two_data_sets_data_first(self):
        """
        Two-data-set-fit.
        
        Also includes
         - trim, zoom, etc
        """
        f = _s.data.fitter(first_figure=10)
        f.__repr__()
        
        # Set the data first
        f.set_data(self.x1, [self.y1,self.y2], self.ey)
        _s.tweaks.set_figure_window_geometry(10, position=[500,0])
        _s.tweaks.set_figure_window_geometry(11, position=[500,400])
        f.__repr__()

        # Set the functions
        f.set_functions(['a*x+b', 'a*cos(b*x)+c'], 'a=-1,b,c')
        f.__repr__()
        
        # Fit
        f.fit()
        f.__repr__()
        
        # Trim
        f.trim()
        f.__repr__()
        
        # Zoom
        f.zoom()
        f.__repr__()
        
        # Untrim
        f.untrim()
        f.__repr__()
        
        # Make sure untrim worked
        self.assertEqual(f['xmin'][0], None)
        
        # Fit
        f.fit()
        f.__repr__()
    
    def test_get_processed_data(self):
        """
        Test self.get_processed_data().
        """
        global f
        
        f = _s.data.fitter(first_figure=7, autoplot=False)
        f.__repr__()
        
        # Set the data first
        f.set_data(self.x1, [self.y1,self.y2], self.ey)
        f.__repr__()
        
        # Massage conditions
        f(xmin=1.5, ymax=3, coarsen=2)
        f.__repr__()
        
        # Levels of process
        self.assertAlmostEqual(f.get_processed_data(                )[0][1][1], 6.5)
        self.assertAlmostEqual(f.get_processed_data(do_trim=False   )[0][1][3], 6.5)
        self.assertAlmostEqual(f.get_processed_data(do_coarsen=False)[2][0][3], 1.7)
    
    def test_fix_free_and_function_globals(self):
        """
        Tests whether we can specify globals for the functions and do a fix()
        and free() call.
        """
        global f
        
        def my_fun(x,a,b): return a*x+b
        
        f = _s.data.fitter().set_data([1,2,3],[1,2,1],0.1).set_functions('stuff(x,a,b)', 'a,b', stuff=my_fun)
        f.fix('a', b=2)
        self.assertEqual(f['b'], 2)
        self.assertEqual(f._cnames, ['a','b'])
        f.__repr__()
        f.fit()
        f.__repr__()
        f.free('a')
        f.__repr__()
        f.fit()
        f.__repr__()
        
if __name__ == "__main__":
    _ut.main()
