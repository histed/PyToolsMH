import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pytest

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
    
