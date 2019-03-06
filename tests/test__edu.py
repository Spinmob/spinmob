# -*- coding: utf-8 -*-
import os          as _os
import spinmob     as _s
import spinmob.edu as _edu
import unittest    as _ut
import numpy       as _n



global g
class Test_edu(_ut.TestCase):
    """
    Test class for edu package.
    """

    def setUp(self):
        """
        """
        self.module_path = _os.path.dirname(_s.__file__)
        return

    def tearDown(self):
        """
        """
        return
    
    def test_example(self):
        """
        Just opens a full-featured example and lets the user play with it
        """
        global g
        g = _edu.fitting.fake_data_taker() 
        
        
    
        

if __name__ == "__main__":
    _ut.main()
    
    self = Test_edu()
    