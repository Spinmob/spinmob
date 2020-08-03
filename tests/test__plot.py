# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""
import spinmob  as _s
import numpy    as _n
import unittest as _ut
import os       as _os


a = x = y = None

class Test_plot_functions(_ut.TestCase):
    """
    Test class for databox.
    """
    def setUp(self):
        """
        """
        # Path to the spinmob module
        self.data_path = _os.path.join(_os.path.dirname(_s.__file__), 'tests', 'fixtures')

    def tearDown(self):
        """
        """
        return


    def test_auto_zoom(self):
        global a
        _s.pylab.figure(40)
        
        _s.pylab.plot([1,2,3],[1,2,1])
        a = _s.pylab.gca()
        
        a.set_xlim(1.5,2.5)
        a.set_ylim(1.5,2.5)
        _s.tweaks.auto_zoom()
        self.assertAlmostEqual(3.04, a.get_xlim()[1])
        self.assertAlmostEqual(2.02, a.get_ylim()[1])
        
        a.set_xlim(1.5,2.5)
        a.set_ylim(1.5,2.5)
        _s.tweaks.auto_zoom(False, True)
        self.assertAlmostEqual(2.5, a.get_xlim()[1])
        self.assertAlmostEqual(2.02, a.get_ylim()[1])
        
        a.set_xlim(1.5,2.5)
        a.set_ylim(1.5,2.5)
        _s.tweaks.auto_zoom(True, False)
        self.assertAlmostEqual(3.04, a.get_xlim()[1])
        self.assertAlmostEqual(2.5, a.get_ylim()[1])
        
        
    
    def test_plots(self):
        
        _s.pylab.figure(20)
        _s.plot.xy.function()
        _s.pylab.ginput(timeout=0.5)
        
        _s.plot.magphase.function()
        _s.pylab.ginput(timeout=0.5)
        
        # Advanced files plotting
        paths = [_os.path.join(self.data_path,'basic.dat'),
                 _os.path.join(self.data_path,'basic2.dat'),
                 _os.path.join(self.data_path,'basic3.dat')]
        pants = 32
        _s.plot.xy.files(0, 'a*b*pants*d[1]*2**n where a=2; b=3', g=dict(pants=pants), yscale='log', paths=paths)
        _s.pylab.ginput(timeout=0.5)
        _s.plot.magphase.files(0, 'a*b*pants*d[1]*2**m where a=2; b=3', g=dict(pants=pants), mscale='log', paths=paths)
        _s.pylab.ginput(timeout=0.5)
        
        # End with this one to facilitate playing.
        _s.plot.image.function()
        _s.pylab.ginput(timeout=0.5)
    
    def test_fit_shown_data(self):
        _s.plot.xy.function()
        _s.tweaks.fit_shown_data(verbose=False)
        

if __name__ == "__main__":
    _ut.main()
