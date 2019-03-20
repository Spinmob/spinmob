# -*- coding: utf-8 -*-

import spinmob  as _s
import os       as _os
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
    
    def test_all(self):
        """
        Written this way so it's easy to cancel early.
        """
        r = _s.dialogs.load_multiple(text="SELECT 1 FILE (OR CANCEL TO END DIALOG TESTS)")
        if r == None: return
        self.assertEqual(type(r), list)

        r = _s.dialogs.load_multiple(text="SELECT MULTIPLE FILES")
        self.assertEqual(type(r), list)
        
        r = _s.dialogs.load_multiple(text="CANCEL ME")
        self.assertEqual(r, None)
        
        r = _s.dialogs.load(text="SELECT 1 FILE")
        self.assertEqual(type(r), str)

        r = _s.dialogs.load(text="CANCEL ME")
        self.assertEqual(r, None)
    
        r = _s.dialogs.save(text="SELECT A FILE (WILL NOT OVERWRITE)")
        self.assertEqual(type(r), str)

        r = _s.dialogs.save(text="SELECT A NON-*.XYZ FILE (WILL NOT OVERWRITE)", force_extension='XYZ')
        self.assertEqual(_os.path.splitext(r)[1][1:], 'XYZ')

        r = _s.dialogs.save(text="SELECT A NON-*.XYZ FILE (WILL NOT OVERWRITE)", force_extension='*.XYZ')
        self.assertEqual(_os.path.splitext(r)[1][1:], 'XYZ')

        r = _s.dialogs.save(text="CANCEL ME")
        self.assertEqual(r, None)

        r = _s.dialogs.select_directory(text="SELECT A DIRECTORY")
        self.assertEqual(type(r), str)

        r = _s.dialogs.select_directory(text="CANCEL ME")
        self.assertEqual(r, None)

        # Crash tests for databox dialogs
        _s.data.load(text='CANCEL ME')
        _s.data.load_multiple(text='CANCEL ME')



if __name__ == "__main__":
    _ut.main()
