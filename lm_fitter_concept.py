"""
Fit Multiple Data Sets
======================

Fitting multiple (simulated) Gaussian data sets simultaneously.

All minimizers require the residual array to be one-dimensional. Therefore, in
the ``objective`` we need to ```flatten``` the array before returning it.

TODO: this should be using the Model interface / built-in models!

"""
import spinmob as _s
import matplotlib.pyplot as plt
import numpy as _n

from lmfit import Parameters, minimize, report_fit

# Functions specified as strings
fstrings = ['a*x+b', 'a*x**2']
pnames   = ['a','b']

# List of functions from these strings.
fs = []
pstring  = ','.join(pnames)
for n in range(len(fstrings)): fs.append(eval('lambda x, '+pstring+': '+fstrings[n]))

# Function that returns the residuals in a 1D array
def residuals_concatenated(parameters, xdatas, ydatas):
    """
    Returns the 1D residuals for the specified parameters (p), xdata, and ydata.
    """
    # Get the list of parameter values
    ps = []
    for n in range(len(pnames)): ps.append(parameters[pnames[n]])
    
    # Calculate the residuals for each function using the supplied xdatas
    rs = []
    for n in range(len(xdatas)): rs.append(fs[n](_n.array(xdatas[n]), *ps)-ydatas[n])
        
    return _n.concatenate(rs)

# Data sets
xdatas = [[1,2,3,4], [1,2,3,4]]
ydatas = [[1,2,1,4], [1,3,2,2]]        

# Parameters
pfit = Parameters()
for pname in pnames: pfit.add(pname, value=1.0)

# Do the fit
results = minimize(residuals_concatenated, pfit, args=(xdatas, ydatas))
report_fit(results.params)

