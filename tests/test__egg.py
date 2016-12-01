# -*- coding: utf-8 -*-
import os       as _os
import spinmob  as _s
import unittest as _ut

class Test_egg(_ut.TestCase):
    """
    Test class for databox.
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
        import spinmob.egg.example_sweeper
        

                
    

if __name__ == "__main__":
    _ut.main()
    