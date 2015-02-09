import sys
import numpy as np
import pickle

def memusage(inA):
    """Recursively examines objects and determines the total memory usage they report.
    Return total size in bytes of inA.

    Better than pympler.asizeof because this accounts for numpy arrays and sparse arrrays.

    If a non-recognized class is detected on recursion, print: "Unknown: " 
    with estimated size, brute force estimated from pickle.dumps()
    If brute force estimate is too large, raise RuntimeError 
    (change this code to handle that class)

    Note that some memory may be shared, so deleting the object may free less 
    memory than reported.  
    To determine memory freed on delete, can try guppy (not sure if this 
    accounts for numpy):  
    import guppy; h=guppy.hpy(); h.iso(obj).domisize

    MH 150201
    """

    totSize = 0

    totSize += sys.getsizeof(inA)  # real size for normal objects and base size for lists, tuples, dicts and nparrays

    if type(inA) is tuple or type(inA) is list:
        totSize += np.sum([memusage(x) for x in inA])
    elif type(inA) is dict:
        totSize += np.sum([memusage(x) for x in inA.values()])
    elif hasattr(inA, 'dtype') and hasattr(inA, 'nbytes') and type(inA.nbytes) is int: # likely numpy.ndarray
        totSize += inA.nbytes
    elif hasattr(inA, 'todense') and hasattr(inA, 'data') and hasattr(inA.data, 'nbytes'): # likely sparse matrix
        totSize += inA.data.nbytes
    elif type(inA) in [bool, float, int, type(None)]:
        pass # no extra memory for this object
    else:
        # brute force
        bruteBytes = len(pickle.dumps(inA))
        totSize += bruteBytes
        print ('Unknown: brute %d, getsizeof %d, type %s'
               % (bruteBytes, sys.getsizeof(inA), type(inA)))
        if bruteBytes > 10000:
            raise RuntimeError, 'Unknown type %s: edit this code' % type(inA)

    return totSize
