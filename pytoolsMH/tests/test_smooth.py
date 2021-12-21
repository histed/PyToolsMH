import warnings
# warnings thrown via imports
warnings.filterwarnings("ignore", "Using or importing the ABCs from 'collections'") # DeprecationWarning
warnings.filterwarnings("ignore", "zmq.eventloop.ioloop is deprecated in pyzmq 17") # DeprecationWarning

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pytest
import sys

import pytoolsMH as ptMH


# 180430: call smooth() and exercise the three smoothing methods.  Mostly do not do output checking.

@pytest.fixture(params=['2d','1d'])
def smoothdata(request):
    d = np.load('data/smooth_data1.npz')['arr']
    if request.param == '2d':
        return d
    elif request.param == '1d':
        return np.squeeze(d[0,:])

def test_smooth(smoothdata):
    if smoothdata.ndim == 2:
        axis = 1
    elif smoothdata.ndim == 1:
        axis = -1
        
    # lowess method
    ptMH.math.smooth(smoothdata, method='lowess', span=11, axis=axis)
    r1 = ptMH.math.smooth(smoothdata, method='lowess', span=11, axis=axis, robust=True)
    r2 = ptMH.math.smooth(smoothdata, method='rlowess', span=11, axis=axis)
    assert np.all(r1==r2)
    
    # moving method
    sm1 = ptMH.math.smooth(smoothdata, method='sgolay', span=11, axis=axis, polyorder=1)
    sm2 = ptMH.math.smooth(smoothdata, method='moving', span=11, axis=axis)
    assert np.allclose(sm1,sm2,atol=1e-5,rtol=1e-5)

    # sgolay
    sm1 = ptMH.math.smooth(smoothdata, method='sgolay', span=11, axis=axis, polyorder=2)
    

def test_lowess_bootstrap(smoothdata):
    # note: smoothdata has small spacing that is a problem for sorting/jitter in bootstrap
    # also this only works for 1d data
    if smoothdata.ndim == 2:
        return
    smoothdata = smoothdata + 3 #np.sin(np.linspace(-3,3)) + 3
    xs = np.r_[:len(smoothdata)]*1.0
    xs[-10:] = xs[-10:] - 0.5  # make distances not always the same
    (ylow,yhigh,out_xs,boot_mat) = ptMH.math.smooth_lowess_bootstrap(smoothdata, xs, ci=95, nbootreps=10, noutpts=100)
    # not checking output for now - bootstrap is a fundamentally random process.  We could cap it probalistically if we want...
    (ylow,yhigh,out_xs,boot_mat,ys0,xs0) = ptMH.math.smooth_lowess_bootstrap(smoothdata, nbootreps=1, noutpts=100) # check for no x passed in
