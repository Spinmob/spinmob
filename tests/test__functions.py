# -*- coding: utf-8 -*-
"""
Module for testing _data.py
"""
import os  # For loading fixtures
import numpy as _n
import spinmob as sm
_f = sm._functions

import unittest as _ut

# Not sure how to handle ~line 125 where if a path is not specified, the user
# manually enters one.  This is annoying to test.  Has to be a way to handle
# this nicely.


class Test_functions(_ut.TestCase):
    """
    Test class for databox.
    """

    def setUp(self):    return
    def tearDown(self): return
    
    def test_is_a_number(self):
        
        # Normal test
        self.assertTrue(_f.is_a_number(7))
        
        # String test (used for databox loading I believe)
        self.assertTrue(_f.is_a_number('100'))
        
        # Non-numbers
        self.assertFalse(_f.is_a_number([]))
    
    def test_fft(self):

        # Odd number of points
        f, Y = _f.fft([1,2,3,4,5],[1,2,1,2,1])
        self.assertEqual(f[0],-0.4)
        self.assertEqual(f[-1],0.4)
        self.assertAlmostEqual(Y[0],-0.1+0.30776835j)
        self.assertAlmostEqual(Y[2],1.4)

        # Even number of points
        f, Y = _f.fft([1,2,3,4],[1,2,1,2])
        self.assertEqual(f[0],-0.5)
        self.assertEqual(f[-1],0.25)
        self.assertAlmostEqual(Y[0],-0.5)
        self.assertAlmostEqual(Y[2],1.5)
    
    def test_match_data_sets(self):
        
        # Nones
        self.assertEqual(_f._match_data_sets(None, [1,2,3]), 
                        ([[0,1,2]], [[1, 2, 3]]))
        
        self.assertEqual(_f._match_data_sets(None, [[1,2,3],[1,2,1]]),
                        ([[0, 1, 2], [0, 1, 2]], [[1, 2, 3], [1, 2, 1]]))
        
        self.assertEqual(_f._match_data_sets([1,2,3],None),
                        ([[1, 2, 3]], [[0, 1, 2]]))
        
        self.assertEqual(_f._match_data_sets([[1,2,3],[1,2,1]], None),
                        ([[1, 2, 3], [1, 2, 1]], [[0, 1, 2], [0, 1, 2]]))
        
        self.assertEqual(_f._match_data_sets([None, [2,3,4]], [[1,2,1],None]),
                        ([[0, 1, 2], [2, 3, 4]], [[1, 2, 1], [0, 1, 2]]))
        
        
        # Normals
        self.assertEqual(_f._match_data_sets([1,2,3], [1,2,1]),
                        ([[1, 2, 3]], [[1, 2, 1]]))
        
        # Shared arrays
        self.assertEqual(_f._match_data_sets([1,2,3], [[1,2,1],[1,3,1]]),
                        ([[1, 2, 3], [1, 2, 3]], [[1, 2, 1], [1, 3, 1]]))
        self.assertEqual(_f._match_data_sets([[1,2,1],[1,3,1]], [1,2,3]),
                        ([[1, 2, 1], [1, 3, 1]], [[1, 2, 3], [1, 2, 3]]))
        
        # Numpy arrays
        x = [_n.array([1,2,3])]
        y = [_n.array([1,2,1]), _n.array([2,1,2])]
        self.assertEqual(len(_f._match_data_sets(x,y)[0]), 2)

        # Empty arrays
        x = _n.array([])
        y = _n.array([])
        self.assertEqual(_f._match_data_sets(x,y), ([],[]))
        

    def test_match_error_to_data_set(self):
        # ex matching
        self.assertEqual(_f._match_error_to_data_set([[1,2,3],[1,2]], None),
                        [None, None])
        
        self.assertEqual(_f._match_error_to_data_set([[1,2,3],[1,2]], 32),
                        [[32, 32, 32], [32, 32]])
        
        self.assertEqual(_f._match_error_to_data_set([[1,2,3],[1,2,3]], [3,4,3]),
                        [[3, 4, 3], [3, 4, 3]])
        
        self.assertEqual(_f._match_error_to_data_set([[1,2,3],[1,2]], [None, 22]),
                        [None, [22, 22]])
        
        self.assertEqual(_f._match_error_to_data_set([[1,2,3],[1,2]], [3]), [[3,3,3],[3,3]])
        
        self.assertEqual(_f._match_error_to_data_set([[1,2,3],[1,2]], [None]), [None,None])
    
    
    def test_psd(self):

        # Odd number of points
        t    = _n.linspace(0,10,101)
        y    = _n.cos(t) + 1
        f, P = _f.psd(t,y)
        
        # Integral test
        self.assertAlmostEqual(sum(P)*(f[1]-f[0]), _n.average(y**2))

        # Even number of points
        t    = _n.linspace(0,10,100)
        y    = _n.cos(t) + 1
        f, P = _f.psd(t,y)
        
        # Integral test
        self.assertAlmostEqual(sum(P)*(f[1]-f[0]), _n.average(y**2))
    
        # Windowed, pow2
        t    = _n.linspace(0,10,100)
        y    = _n.cos(5*t) + 1
        f, P = _f.psd(t,y,pow2=True,window='hanning')
        
        # Integral test
        self.assertAlmostEqual(sum(P)*(f[1]-f[0]), _n.average( (y[0:64]*_n.hanning(64))**2))


        # Windowed, pow2, rescaled
        t    = _n.linspace(0,10,100)
        y    = _n.cos(5*t) + 1
        f, P = _f.psd(t,y,pow2=True,window='hanning',rescale=True)
        
        # Integral test
        self.assertAlmostEqual(sum(P)*(f[1]-f[0]), _n.average( y[0:64]**2))

    
        # DC and nyquist component test
        f, P = _f.psd([1,2,3,4],[1,2,1,2])
        self.assertEqual(( P[0]*(f[1]-f[0]))**0.5, 1.5)
        self.assertEqual((P[-1]*(f[1]-f[0]))**0.5, 0.5)
        
        # Middle frequency component test
        f, P = _f.psd([1,2,3,4],[1,2,2,1])
        self.assertAlmostEqual((P[0]*(f[1]-f[0]))**0.5, 1.5)
        self.assertAlmostEqual((P[1]*(f[1]-f[0]))**0.5, 0.5)
        
    def test_generate_fake_data(self):
        
        # Survival test
        _f.generate_fake_data('cos(x)*3',_n.linspace(-5,5,11),1,2)
    
    def test_coarsen_data(self):
        
        # Simple coarsen
        a = sm.fun.coarsen_data([1,2,3,4,5],[1,2,1,2,1])
        self.assertEqual(_n.shape(a), (2,2))
        self.assertEqual(a[1][1], 1.5)
    
        # With ey float
        a = sm.fun.coarsen_data([1,2,3,4,5],[1,2,1,2,1],2,level=3)
        self.assertEqual(_n.shape(a), (3,1))
        self.assertAlmostEqual(a[2][0], 1.15470054)
        
        # With ey array
        a = sm.fun.coarsen_data([1,2,3,4,5],[1,2,1,2,1],[1,2,3,4,5],level=2)
        self.assertEqual(_n.shape(a), (3,2))
        self.assertAlmostEqual(a[2][0], 1.118033988749895)
        
        # With ex and ey
        a = sm.fun.coarsen_data([1,2,3,4,5],[1,2,1,2,1],[1,2,3,4,5],[1,2,1,2,1],level=2)
        self.assertEqual(_n.shape(a), (4,2))
        self.assertAlmostEqual(a[3][1], 1.118033988749895)
        
        # Exponential coarsen simple
        a = sm.fun.coarsen_data(_n.linspace(0,100,100),_n.linspace(100,0,100),exponential=True)
        self.assertEqual(_n.shape(a), (2,7))
        self.assertAlmostEqual(a[1][5], 52.02020202020202)
        
        # Exponential coarsen ex and ey
        a = sm.fun.coarsen_data(_n.linspace(0,100,100),_n.linspace(100,0,100),
                                _n.linspace(1,2,100), 3, 1.3, exponential=True)
        self.assertEqual(_n.shape(a), (4,16))
        self.assertAlmostEqual(a[3][5], 2.1213203435596424)
        
    def test_averager_normal(self):
        
        import spinmob as sm
        
        points = 1000
        
        # When to record information
        print_me  = [4,8,16,32,64,128,256]
        vs      = []
        sigma2s = []
        ns      = []
        a       = sm.fun.averager()
        y_sum   = 0
        y2_sum  = 0
        for n in range(1,1000):
            
            # Get the new measurement. Best to think of this as a
            # single number, and the array you get out is the 
            # result of repeating the same measurement many times 
            # independently.
            y = _n.random.normal(size=points) + 7
            
            # Do the calculation by hand
            y_sum  += y
            y2_sum += y*y
            
            if(n<2): sigma2 = 0
            else:    sigma2 = (y2_sum - y_sum**2/n)/(n-1)
            
            # Let the averager do it
            a.add(y)
        
            # Calculate the reduced chi2s
            if(n>2):
                vs     .append(_n.mean(a.variance_sample))
                sigma2s.append(_n.mean(sigma2))
                ns.append(n)
                
            # Update the user
            if n in print_me: print('Regular variance', n, ' should = 1 =', vs[-1])
        
        sm.pylab.figure(77)
        sm.plot.xy.data(ns, [vs, sigma2s], 
                        label = ['vs   Reg mean %.3f' % _n.mean(vs),
                                 'sigma2s by hand'],
                        xlabel='N', 
                        xscale='log', title='Regular', clear=0,
                        style=sm.plot.style(ls=['-','--']))
        
        
        
    def test_averager_dsp(self):
        
        import spinmob as sm
        
        points = 10000
        
        # Try a bunch of different frames.
        taus = sm.fun.erange(1, 32, 20) #_n.array([1.5,2,4,8,16,32,64,128])
        vs   = []
        c2s  = []
        for tau in taus:
                        
            # Create a new averager
            a = sm.fun.averager(lowpass_frames=tau)

            # Steady state index
            N = int(tau*10)

            # Iterate until steady state
            for n in range(N):
                
                # New data set
                y = _n.random.normal(size=points) + 7
                
                # Add it to the averager
                a.add(y)
                
            # Get the variance and chi^2 after having settled
            vs.append(_n.mean(a.variance_sample))
            print('Tau =', tau, 'Variance should = 1 =', vs[-1])

        sm.pylab.figure(77)
        sm.plot.xy.data(taus, [vs], 
                        label = ['vs DSP'],
                        xlabel='tau', ylabel='chi2', 
                        xscale='log', title='DSP', clear=0)
            
            

if __name__ == "__main__": _ut.main()
