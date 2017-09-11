import macTimingMH as mt
import time
import timeit
import numpy as np
reload(mt)

print mt.getCpuFreq()
mt.setRealtime(True)

nPts = 100
for i in xrange(100):
    elV = np.ones((nPts,), dtype='f64')
    for i in xrange(nPts):
        stT = timeit.default_timer()
        np.random.random((1000000,))
        time.sleep(0.001)
        elS = timeit.default_timer() - stT
        elV[i] = elS * 1000
    print 'median ms %3.2f, max %3.2f' % (np.median(elV), np.max(elV))


    

