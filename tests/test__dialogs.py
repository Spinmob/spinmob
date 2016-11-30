# -*- coding: utf-8 -*-

import spinmob  as _s
import unittest as _ut

# Not sure how to handle ~line 125 where if a path is not specified, the user
# manually enters one.  This is annoying to test.  Has to be a way to handle
# this nicely.


class Test_dialogs(_ut.TestCase):
    """
    Test class for databox.
    """

    def setUp(self):
        """
        """
        return

    def tearDown(self):
        """
        """
        return
    
    def test_open_multiple(self):
        """
        """
        r = _s.dialogs.open_multiple(text="SELECT 1 FILE")
        self.assertEqual(type(r), list)

        r = _s.dialogs.open_multiple(text="SELECT MULTIPLE FILES")
        self.assertEqual(type(r), list)
        
        r = _s.dialogs.open_multiple(text="CANCEL ME")
        self.assertEqual(r, None)
        
    def test_open_single(self):
        """
        """
        r = _s.dialogs.open_single(text="SELECT 1 FILE")
        self.assertEqual(type(r), str)

        r = _s.dialogs.open_single(text="CANCEL ME")
        self.assertEqual(r, None)
    
    def test_save(self):
        """
        """
        r = _s.dialogs.save(text="SELECT A FILE (WILL NOT OVERWRITE)")
        self.assertEqual(type(r), str)

        r = _s.dialogs.save(text="CANCEL ME")
        self.assertEqual(r, None)

    def test_select_directory(self):
        """
        """
        r = _s.dialogs.select_directory(text="SELECT A DIRECTORY")
        self.assertEqual(type(r), str)

        r = _s.dialogs.select_directory(text="CANCEL ME")
        self.assertEqual(r, None)
    

if __name__ == "__main__":
    _ut.main()
