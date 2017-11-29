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

        t = _n.linspace(0,10,1024)
        y = _n.cos(2*_n.pi*37*t+1)

        # Survival tests        
        f, Y = _f.fft(t,y)
    
    def test_psd(self):

        t = _n.linspace(0,10,1024)
        y = _n.cos(2*_n.pi*37*t+1)

        # Survival tests        
        f, Y = _f.psd(t,y)

if __name__ == "__main__": _ut.main()
