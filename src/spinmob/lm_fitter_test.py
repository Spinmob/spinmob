"""
Fit Multiple Data Sets
======================

Fitting multiple (simulated) Gaussian data sets simultaneously.

All minimizers require the residual array to be one-dimensional. Therefore, in
the ``objective`` we need to ```flatten``` the array before returning it.

TODO: this should be using the Model interface / built-in models!

"""
import spinmob as _s
import numpy as _n
from scipy.optimize import leastsq
from lmfit import Parameters, minimize, report_fit


sigma = 17
dof = 100
N = 1000


# Functions that return the residuals in a 1D array
def residuals_lmfit(parameters): return (parameters['y']-ydata)/sigma
def residuals_leastsq(y       ): return (y              -ydata)/sigma

# My fitter
f = _s.data.fitter(autoplot=False)
f.set_functions('a', 'a')

# Parameters container for lmfit
p_lmfit = Parameters()
p_lmfit.add('y', value=1.0)
p_lmfit.add('x', vary=False)

# Run the fitter many times
ys_leastsq = [] # fit y-values
es_leastsq = [] # fit errorbars
ys_lmfit = []   # fit y-values
es_lmfit = []   # fit errorbars
ys_me = []
es_me = []
for n in range(N):
    
    # Data
    xdata = _n.linspace(     0,    1,dof+1)
    ydata = _n.random.normal(0,sigma,dof+1)        
    
    # Do the fit
    results_lmfit   = minimize(residuals_lmfit,   p_lmfit)
    results_leastsq = leastsq (residuals_leastsq, 1, full_output=True)
    f.set_data(xdata, ydata, sigma).fit()
    
    # Record the results
    ys_lmfit.append(results_lmfit.params['y'].value)
    es_lmfit.append(results_lmfit.params['y'].stderr)
    
    ys_leastsq.append(results_leastsq[0][0])
    es_leastsq.append(results_leastsq[1][0][0]**0.5)
    
    ys_me.append(f.results[0][0])
    es_me.append(f.results[1][0][0]**0.5)

a1 = _s.pylab.subplot(211)
a2 = _s.pylab.subplot(212)
_s.plot.xy.data(None, [ys_lmfit, es_lmfit, ys_me, es_me], axes=a1)

n,b,p = a2.hist(ys_lmfit, alpha=0.5)
_s.plot.xy.function('N*db/(s*sqrt(2*pi))*exp(-0.5*x**2/s**2)', 
                    min(ys_leastsq), max(ys_leastsq), 
                    g=dict(s=sigma/dof**0.5, N=N, db=b[1]-b[0]), clear=0, axes=a2)
