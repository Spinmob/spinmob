# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""
import os  # For loading fixtures
import numpy as _n
import spinmob as sm
_dt = sm._data

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


if __name__ == "__main__":
    _ut.main()
