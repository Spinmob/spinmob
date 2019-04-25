# -*- coding: utf-8 -*-
import os       as _os
import spinmob  as _s
import unittest as _ut
import shutil   as _sh

class Test_egg(_ut.TestCase):
    """
    Test class for databox.
    """

    def setUp(self):
        """
        """
        self.module_path = _os.path.dirname(_s.__file__)
        
        # Path to the data files
        self.data_path = _os.path.join(_os.path.dirname(_s.__file__), '_tests', 'fixtures', 'data_files')

        return

    def tearDown(self):
        """
        """
        return
    
    def test_example(self):
        """
        Just opens a full-featured example and lets the user play with it
        """
        import spinmob.egg.example_sweeper as sweeper
        if _os.path.exists('egg_settings'): _sh.rmtree('egg_settings')
        
        sweeper.d_sweep.load_file(_os.path.join(self.data_path, 'difficult.binary'))
        
        sweeper.w.show(True)
        
        
    def test_TreeDictionary(self):
        """
        Runs through a bunch of value setting and getting, to make sure
        the interpretation of different types is reliable.
        """
        import spinmob.egg as _e
        
        # clear out the gui settings
        if _os.path.exists('egg_settings'): _sh.rmtree('egg_settings')
        
        test_list_values = [42, 'test', 'pants', 37.2, dict(stuff='otherstuff')]
        test_list_values_stringified = [str(42), 'test', 'pants', str(37.2), str(dict(stuff='otherstuff'))]
        
        # Create the TreeDictionary
        self.d = _e.gui.TreeDictionary('pants.txt')
        
        # Make sure the autosettings path is right.
        self.assertEqual(self.d._autosettings_path, 'pants.txt')
        
        # Create some different value types
        self.d.add_button('button')
        self.d.add_parameter('booly',   value=False)
        self.d.add_parameter('inty',    value=42)
        self.d.add_parameter('floaty',  value=42.0)
        self.d.add_parameter('stringy', value=574,    type='str')
        self.d.add_parameter('listy',   value='test', type='list', values=test_list_values)
    
        # Make sure the get-value returns the right types
        
        # Bool stuff
        self.assertEqual(type(self.d['booly']), bool)
        self.d['booly'] = True
        self.assertEqual(self.d['booly'], True)
        self.d['booly'] = False
        self.assertEqual(self.d['booly'], False)
        
        # Integer stuff
        self.assertEqual(type(self.d['inty']), int)
        self.d['inty'] = '32'
        self.assertEqual(self.d['inty'], 32)
        
        # Float stuff
        self.assertEqual(type(self.d['floaty']), float)
        self.d['floaty'] = '45.5555'
        self.assertEqual(self.d['floaty'], 45.5555)

        # See if it's autosaving
        self.assertTrue(_os.path.exists('egg_settings/pants.txt'))
        
        # String stuff
        self.assertEqual(type(self.d['stringy']), str)
        self.d['stringy'] = 47.2
        self.assertEqual(type(self.d['stringy']), str)
        
        # List
        self.assertEqual(self.d.get_list_values('listy'), test_list_values_stringified)
        self.assertEqual(type(self.d['listy']), str)
        self.d['listy'] = 37.2
        self.assertEqual(self.d['listy'], str(37.2))
        
        # Save, load, and make sure the values are still the same (with types)
        self.d.save()
        self.d.load()
        self.assertTrue(_os.path.exists('egg_settings/pants.txt'))
        self.assertEqual(self.d['inty'], 32)
        self.assertEqual(self.d['floaty'], 45.5555)
        self.assertEqual(type(self.d['stringy']),  str)
        self.assertEqual(self.d['listy'], str(37.2))
        
        # Now change a parameter, which should autosave
        self.d['floaty'] = 32
        
        # Create a new one with the same autosettings path
        self.e = _e.gui.TreeDictionary(autosettings_path='pants.txt')
        
        # Test the lazy load & string recall.
        self.e.add_parameter('floaty', 42.0)
        self.assertEqual(self.e['floaty'],32)
        self.e.add_parameter('stringy', 'test')
        self.assertEqual(self.e['stringy'],'47.2')
        
        

if __name__ == "__main__":
    _ut.main()
    
    self = Test_egg()
    