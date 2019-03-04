# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""
import os  # For loading fixtures
import numpy as _n
import spinmob as sm
_f = sm._functions

import unittest as _ut

# Not sure how to handle ~line 125 where if a path is not specified, the user
# manually enters one.  This is annoying to test.  Has to be a way to handle
# this nicely.


class Test_functions(_ut.TestCase):
    """
    Test class for databox.
    """

    def setUp(self):    return
    def tearDown(self): return
    
    def test_is_a_number(self):
        
        # Normal test
        self.assertTrue(_f.is_a_number(7))
        
        # String test (used for databox loading I believe)
        self.assertTrue(_f.is_a_number('100'))
        
        # Non-numbers
        self.assertFalse(_f.is_a_number([]))
    
    def test_fft(self):

        # Odd number of points
        f, Y = _f.fft([1,2,3,4,5],[1,2,1,2,1])
        self.assertEqual(f[0],-0.4)
        self.assertEqual(f[-1],0.4)
        self.assertAlmostEqual(Y[0],-0.1+0.30776835j)
        self.assertAlmostEqual(Y[2],1.4)

        # Even number of points
        f, Y = _f.fft([1,2,3,4],[1,2,1,2])
        self.assertEqual(f[0],-0.5)
        self.assertEqual(f[-1],0.25)
        self.assertAlmostEqual(Y[0],-0.5)
        self.assertAlmostEqual(Y[2],1.5)
        
    
    def test_psd(self):

        # Odd number of points
        t    = _n.linspace(0,10,101)
        y    = _n.cos(t) + 1
        f, P = _f.psd(t,y)
        
        # Integral test
        self.assertAlmostEqual(sum(P)*(f[1]-f[0]), _n.average(y**2))

        # Even number of points
        t    = _n.linspace(0,10,100)
        y    = _n.cos(t) + 1
        f, P = _f.psd(t,y)
        
        # Integral test
        self.assertAlmostEqual(sum(P)*(f[1]-f[0]), _n.average(y**2))
    
        # Windowed, pow2
        t    = _n.linspace(0,10,100)
        y    = _n.cos(5*t) + 1
        f, P = _f.psd(t,y,pow2=True,window='hanning')
        
        # Integral test
        self.assertAlmostEqual(sum(P)*(f[1]-f[0]), _n.average( (y[0:64]*_n.hanning(64))**2))
    
        
    def test_generate_fake_data(self):
        
        # Survival test
        _f.generate_fake_data('cos(x)*3',_n.linspace(-5,5,11),1,2)
    
        

if __name__ == "__main__": _ut.main()
