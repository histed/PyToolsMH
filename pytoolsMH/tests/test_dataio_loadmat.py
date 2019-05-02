import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pytest

import pytoolsMH as ptMH

# 190502: call ptMH.dataio.loadmat() and do some very very basic checks
#   this mat came from analysisPhysiology2019/190501/develop
#  TODO: should be expanded, do some other datafiles

fname = 'data/endState-180411_1550.mat'
def test_loadmat():
    es = ptMH.dataio.loadmat(fname)['es']

    print(np.unique(es['tAPeakPowerMw']))
    assert(len(es['tATrainPulseLengthMs']) == 484)  # trials in this mat file
    assert(np.all(np.unique(es['tAPeakPowerMw']) == [0.3,0.5,1,2,4,8]))
