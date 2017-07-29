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
        
    def test_TreeDictionary(self):
        """
        Runs through a bunch of value setting and getting, to make sure
        the interpretation of different types is reliable.
        """
        import spinmob.egg as _e
        
        test_list_values = [42, 'test', 'pants', 37.2, dict(stuff='otherstuff')]
        test_list_values_stringified = [str(42), 'test', 'pants', str(37.2), str(dict(stuff='otherstuff'))]
        
        # Create the TreeDictionary
        self.d = _e.gui.TreeDictionary()
        
        # Create some different value types
        self.d.add_button('button')
        self.d.add_parameter('inty',    value=42,     type='int')
        self.d.add_parameter('floaty',  value=42.0,   type='float')
        self.d.add_parameter('stringy', value=574,    type='str')
        self.d.add_parameter('listy',   value='test', type='list', values=test_list_values)
    
        # Make sure the get-value returns the right types
        
        # Integer stuff
        self.assertEqual(type(self.d['inty']),     int)
        self.d['inty'] = '32'
        self.assertEqual(self.d['inty'], 32)
        
        # Float stuff
        self.assertEqual(type(self.d['floaty']), float)
        self.d['floaty'] = '45.5555'
        self.assertEqual(self.d['floaty'], 45.5555)
        
        # String stuff
        self.assertEqual(type(self.d['stringy']),  str)
        self.d['stringy'] = 47.2
        self.assertEqual(type(self.d['stringy']),  str)
        
        # List
        self.assertEqual(self.d.get_list_values('listy'), test_list_values_stringified)
        self.assertEqual(type(self.d['listy']),    str)
        self.d['listy'] = 37.2
        self.assertEqual(self.d['listy'], str(37.2))
        
        # Save, load, and make sure the values are still the same (with types)
        self.d.save()
        self.d.load()
        self.assertEqual(self.d['inty'], 32)
        self.assertEqual(self.d['floaty'], 45.5555)
        self.assertEqual(type(self.d['stringy']),  str)
        self.assertEqual(self.d['listy'], str(37.2))
        

if __name__ == "__main__":
    _ut.main()
    
    self = Test_egg()
    self.test_TreeDictionary()
    
    import spinmob.egg as e; w = e.gui.Window(); w.place_object(self.d); w.show()
    
    # Try to set self.d['listy'] = '3'?
    # Get list elements to print options and a star
    