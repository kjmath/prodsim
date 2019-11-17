'''Assortment of helper methods for prodsim.'''

import numpy as np

def weibull(a, scale=1):
    '''Draw sample from two-parameter Weibull distribution. Similar to 
    numpy.random.weibull, but with added scale parameter. See scipy.org
    for documentation.

    Arguments:
        a (scalar): shape parameter of distribution.
        scale (scalar): scale parameter of distribution.

    Returns:
        scalar: drawn sample from two-parameter Weibull distribution.
    '''

    return scale*np.random.weibull(a)

