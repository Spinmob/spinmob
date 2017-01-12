# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""
import spinmob as _s
import unittest as _ut



class Test_plot_functions(_ut.TestCase):
    """
    Test class for databox.
    """
    def setUp(self):
        """
        """
        
    def tearDown(self):
        """
        """
        return

    def test_match_data_sets(self):
        
        # Nones
        self.assertEqual(_s._plotting_mess._match_data_sets(None, [1,2,3]), 
                        ([[0,1,2]], [[1, 2, 3]]))
        
        self.assertEqual(_s._plotting_mess._match_data_sets(None, [[1,2,3],[1,2,1]]),
                        ([[0, 1, 2], [0, 1, 2]], [[1, 2, 3], [1, 2, 1]]))
        
        self.assertEqual(_s._plotting_mess._match_data_sets([1,2,3],None),
                        ([[1, 2, 3]], [[0, 1, 2]]))
        
        self.assertEqual(_s._plotting_mess._match_data_sets([[1,2,3],[1,2,1]], None),
                        ([[1, 2, 3], [1, 2, 1]], [[0, 1, 2], [0, 1, 2]]))
        
        self.assertEqual(_s._plotting_mess._match_data_sets([None, [2,3,4]], [[1,2,1],None]),
                        ([[0, 1, 2], [2, 3, 4]], [[1, 2, 1], [0, 1, 2]]))
        
        # Normals
        self.assertEqual(_s._plotting_mess._match_data_sets([1,2,3], [1,2,1]),
                        ([[1, 2, 3]], [[1, 2, 1]]))
        
        # Shared arrays
        self.assertEqual(_s._plotting_mess._match_data_sets([1,2,3], [[1,2,1],[1,3,1]]),
                        ([[1, 2, 3], [1, 2, 3]], [[1, 2, 1], [1, 3, 1]]))
        self.assertEqual(_s._plotting_mess._match_data_sets([[1,2,1],[1,3,1]], [1,2,3]),
                        ([[1, 2, 1], [1, 3, 1]], [[1, 2, 3], [1, 2, 3]]))

    def test_match_error_to_data_set(self):
        # ex matching
        self.assertEqual(_s._plotting_mess._match_error_to_data_set([[1,2,3],[1,2]], None),
                        [None, None])
        
        self.assertEqual(_s._plotting_mess._match_error_to_data_set([[1,2,3],[1,2]], 32),
                        [[32, 32, 32], [32, 32]])
        
        self.assertEqual(_s._plotting_mess._match_error_to_data_set([[1,2,3],[1,2,3]], [3,4,3]),
                        [[3, 4, 3], [3, 4, 3]])
        
        self.assertEqual(_s._plotting_mess._match_error_to_data_set([[1,2,3],[1,2]], [None, 22]),
                        [None, [22, 22]])
        


        

if __name__ == "__main__":
    _ut.main()
