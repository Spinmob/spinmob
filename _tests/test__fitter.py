# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""
import os      as _os # For loading fixtures
import numpy   as _n
import spinmob as _s

import unittest as _ut

a = b = c = d = x = y = f = None

class Test_fitter(_ut.TestCase):
    """
    Test class for fitter.
    """
    debug = False

    def setUp(self):
        # Path to the spinmob module
        self.data_path = _os.path.join(_os.path.dirname(_s.__file__), '_tests', 'fixtures', 'data_files')

        self.x1 = [0,1,2,3,4,5,6,7]
        self.y1 = [10,1,2,1,3,4,5,3]
        self.y2 = [2,1,2,4,5,2,1,5]
        self.ey = [0.3,0.5,0.7,0.9,1.1,1.3,1.5,1.7]

        self.x3 = [1,     2, 4.2,   4]
        self.y3 = [0.3, 0.5, 0.2, 0.7]
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

    def test_multi_data_sets(self):
        """
        Two-data-set-fit.

        Also includes
         - trim, zoom, etc
        """
        global f
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

        # Two data sets with different x-datas, different lengths, and different bit depth
        f.set_data([self.x1, self.x1, self.x3], [self.y1,self.y2,self.y3], [self.ey,self.ey,45], dtype=_n.float32)
        f.__repr__()

        f.set_functions(['a*x+b', 'a*cos(b*x)+c', 'a*x**2'], 'a=-1,b,c')
        f.__repr__()

        # Fit it.
        f.fit()
        f.__repr__()

        # Set functions to have the wrong number
        f.set_functions(['a*x+b', 'a*cos(b*x)+c'], 'a=-1,b,c')
        f.__repr__()

        f.set_functions(['a*x+b', 'a*cos(b*x)+c', 'a*x**2', 'a*x'], 'a=-1,b,c')
        f.__repr__()



    def test_get_processed_data(self):
        """
        Test self.get_processed_data().
        """

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

    def test_dtype(self):
        """
        Ensures that the dtype is set.
        """

        f = _s.data.fitter(first_figure=7, autoplot=False)
        f.set_data(_n.array([1,2,3,4], dtype=_n.float16),
                   _n.array([1,2,3,4], dtype=_n.float64),
                   _n.array([1,2,3,4], dtype=_n.float32))
        self.assertEqual(f.get_processed_data()[0][0].dtype, _n.float64)

        f.set_data(_n.array([1,2,3,4], dtype=_n.float16),
                   _n.array([1,2,3,4], dtype=_n.float64),
                   _n.array([1,2,3,4], dtype=_n.float32),
                   dtype=_n.float32)
        self.assertEqual(f.get_processed_data()[1][0].dtype, _n.float32)


    def test_fix_free_and_function_globals(self):
        """
        Tests whether we can specify globals for the functions and do a fix()
        and free() call.
        """

        def my_fun(x,a,b): return a*x+b
        f = _s.data.fitter()
        f.set_functions('stuff(x,a,b)', 'a,b', stuff=my_fun)
        f.fix('a')
        f.set_data([1,2,3],[1,2,1],0.1)
        f.fix(b=2)
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
