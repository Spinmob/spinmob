# -*- coding: utf-8 -*-
import os       as _os
import spinmob  as _s
import unittest as _ut
import shutil   as _sh

import spinmob.egg as _e
import numpy as _n
_g = _e.gui
        

x = None

class Test_egg(_ut.TestCase):
    """
    Test class for databox.
    """

    def setUp(self):
        """
        """
        self.module_path = _os.path.dirname(_s.__file__)
        
        # Path to the data files
        self.data_path = _os.path.join(_os.path.dirname(_s.__file__), 'tests', 'fixtures')

        return

    def tearDown(self):
        """
        """
        return
    
    def test_example(self):
        """
        Just opens a full-featured example and lets the user play with it
        """
        if _os.path.exists('egg_settings'): _sh.rmtree('egg_settings')
        
        import spinmob.egg.example_sweeper as sweeper
        sweeper.d_sweep.load_file(_os.path.join(self.data_path, 'difficult.binary'))
        sweeper.w.show(True)
        
    def test_TreeDictionary(self):
        """
        Runs through a bunch of value setting and getting, to make sure
        the interpretation of different types is reliable.
        """
        
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
        
        # Crash test; also tests self.e.get_dictionary(strip_name=True)
        repr(self.e)
        
        # Test get_dictionary with a name
        
        # Set the name
        self.e.name = 'testname'
        ks, d = self.e.get_dictionary()
        self.assertEqual(ks[0], '/testname/floaty')
        
        # Test update
        d['/testname/floaty'] = 77
        self.e.update(d)
        self.assertEqual(self.e['floaty'], 77)
        self.assertEqual(self.e['/testname/floaty'], 77)
        
        # Output to a databox header
        d = _s.data.databox()
        self.e.send_to_databox_header(d)
        self.assertEqual(d.hkeys[0],'/testname/floaty')
        
        # Test load
        self.e.load()
        self.assertEqual(self.e['/testname/floaty'], 77)
        
        
        
        # Test blocking connect_signal_changed
        self.d.add_parameter('a', 0)
        self.d.add_parameter('b', 0)
        def f(*a): self.d['a'] += 1
        self.d.connect_any_signal_changed(f)
        self.d.connect_signal_changed('a', f)
        self.d.set_value('a', 1, block_all_signals=True)
        self.assertEqual(self.d['a'], 1)
        
    def test_DataboxPlot_DataboxProcessor(self):
        
        # Create window
        w = _g.Window(autosettings_path='w')
        
        # Create buttons
        b = w.add(_g.Button('Get Fake Data'))
        l = w.add(_g.Button('Loop', checkable=True))
        
        # Create tab area
        w.new_autorow()
        ts = w.add(_g.TabArea(), alignment=0, column_span=10)
        w.set_column_stretch(4)
        
        # Create plotter and processor
        p = ts.add_tab('Data').add(_g.DataboxPlot('*.dat','p', autoscript=4), alignment=0)
        a = ts.add_tab('Processor').add(_g.DataboxProcessor(databox_source=p), alignment=0)
        
        p.button_script.set_checked(True)
        
        # Window close stops acquisition
        def close(): l.set_checked(False)
        w.event_close = close
        
        # Initial data
        p[0] = [1,2,3,4]
        p[1] = [1,2,1,2]
        p[2] = [0.5,0.5,0.5,0.5]
        p[3] = [2,1,2,1]
        p[4] = [0.3,0.1,20,0.3]
        p.plot()
        
        # New Data
        def get_fake_data():
            p.clear()
            p['t']  = _n.linspace(0,10,1000)
            p['V1'] = 0.01*_n.random.normal(size=1000)
            p['V2'] = _n.random.normal(size=1000)
            p.plot()
            a.run()
        b.signal_clicked.connect(get_fake_data)
        
        # Loop
        def loop():
            while l.is_checked():
                get_fake_data()
                w.sleep(0.25)
        l.signal_clicked.connect(loop)
        
        w.show(True)
        global x
        x = p
    
      

if __name__ == "__main__":
    _ut.main()
    
    self = Test_egg()
    