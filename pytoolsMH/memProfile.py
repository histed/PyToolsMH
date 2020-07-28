from __future__ import print_function
import sys
import numpy as np
import pickle
import types
import copy
from . import string as ptMHstring
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass

def total_size(o, handlers={}, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.
    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:
        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    200726: https://github.com/ActiveState/recipe-577504-compute-mem-footprint
    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                   }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = sys.getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = sys.getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=sys.stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)


def print_locals(in_dict):
    """Show information: sizes, types, bytes, of variables in memory

    Args: 
         in_dict
    
    Returns: none
        Just prints info using print()

    Examples:
        print_vars(locals())
        Prints:

            Modules: 
              colorama, copy, exposure, feature, ii, imp, io, mpimg, mpl

            Functions: 
              a_, glob, info, print_by_type, toFullMat

            F                   : numpy.ndarray                           : shape (256, 256)   dtype float64         : size:  512 kB
            F0                  : numpy.ndarray                           : shape (256, 256)   dtype float64         : size:  512 kB
            In                  : list                                    : len 69                                   : size:   57 kB
            Out                 : dict                                    : len 12                                   : size:    2 kB
            PCA                 : abc.ABCMeta                             :                                          : size:    1 kB

            allstimavg          : numpy.ndarray                           : shape (4, 21, 256, 256) dtype float32    : size:   21 MB


    Notes:
        this is like MATLAB's whos function.  It's not far off from ipython %whos
        - 200727: created MH
    """
    # 
    
    curr = copy.copy(in_dict)
    typeD = {k: type(v) for k,v in curr.items()}

    skipL = []
    def print_by_type(curr, print_type=types.ModuleType, title='Modules: '):
        modKL = [k for k,v in typeD.items() if v == print_type and k[0] is not '_' ]
        print(f'{title}\n  ', end='')
        for (iK,tK) in enumerate(sorted(modKL)):
            tE = ', '
            if iK == len(modKL)-1:
                tE = ''
            print(tK, end=tE)
            if iK > 0 and iK % 15 == 0:
                print('\n  ', end='')
        print('\n')
        return modKL

    tS = print_by_type(curr, types.ModuleType, title='Modules: ')
    skipL.extend(tS)
    tS = print_by_type(curr, types.FunctionType, title='Functions: ')
    skipL.extend(tS)

    nPrinted = 0
    for tK,tV in sorted(curr.items()):
        if tK[0] == '_' or tK in skipL:
            continue
        if nPrinted > 0 and nPrinted % 5 == 0:
            print('')

        # format correctly based on type ########
        tmod = tV.__class__.__module__
        tname = tV.__class__.__name__

        # construct the type name
        if type(tV).__name__ == 'type':  # some functions/classes just say 'type' as type
            modS = f"type from {tV.__module__}"
        elif tmod == 'builtins':  
            modS = tname
        else:
            modS = tmod + '.' + tname

        # add extra info based on type
        extraS = ''
        if tname == 'list' or tname == 'tuple' or tname == 'dict':
            extraS = f'len {len(tV)}'
        elif tname == 'ndarray':
            extraS = f'shape {str(np.shape(tV)):12} dtype {tV.dtype}'

        # size in bytes
        sizeStr = ptMHstring.format_bytes(total_size(tV), format_str='{size:4.0f} {suffix}')

        # print it
        print(f'{tK:20}: {modS:40}: {extraS:40} : size: {sizeStr}')

        nPrinted = nPrinted + 1



def memusage(inA):
    """DEPRECATED Recursively examines objects and determines the total memory usage they report.
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

    raise RuntimeError('As of 200726: this is no longer needed as ndarrays now respond properly to getsizeof; also looks like it gets size for ndarrays wrong.  Use total_size()')

    totSize = 0

    totSize += sys.getsizeof(inA)  # real size for normal objects and base size for lists, tuples, dicts and nparrays

    # TODO: this whole problem space is a mess.  Look at
    # https://github.com/pympler/pympler/blob/master/pympler/asizeof.py
    # for the lengths they go through to sort objects.  I should probably just patch asizeof() to support ndarrays and sparse arrays
    
    
    # goal: anything that might contain something big (e.g. an array), we should break into pieces and do
    # each piece separately.    e.g. instances may have np arrays as attributes, but functions/methods typically do not.
    # So break down instances but not methods

    # do checks in order of preference
    if type(inA) in [bool, float, int, type(None), str, types.MethodType]:
        pass # no extra memory for this object
    elif type(inA) is tuple or type(inA) is list:
        totSize += np.sum([memusage(x) for x in inA])
    elif type(inA) is dict:
        totSize += np.sum([memusage(x) for x in inA.values()])
    elif hasattr(inA, '__array_interface__') and hasattr(inA, 'nbytes') and type(inA.nbytes) is int:
        # likely numpy.ndarray 
        # we should be using the buffer protocol and memoryview() for this
        totSize += inA.nbytes
    elif hasattr(inA, '__array_priority__') and hasattr(inA.data, 'nbytes'): # likely sparse matrix
        totSize += inA.data.nbytes
    elif hasattr(inA, '__array__'):
        # supports the 'array interface', may be a subclass of ndarray, just re-call this function on the array itself
        # pandas dataframes are these
        totSize += memusage(inA.__array__())
    elif type(inA) is types.InstanceType or isinstance(inA, object):
        # is an instance - call memusage on each attribute, many will be methods, handled above
        totSize += np.sum([memusage(getattr(inA,x)) for x in dir(inA)])
    else:
        # brute force
        try:
            bruteBytes = len(pickle.dumps(inA))
        except TypeError:
            # often "can't pickle XXX objects"
            bruteBytes = 0
            pass
        totSize += bruteBytes
        print ('Unknown: brute %d, getsizeof %d, type %s'
               % (bruteBytes, sys.getsizeof(inA), type(inA)))
        if bruteBytes > 10000:
            raise RuntimeError('In brute force sizing: Unknown type %s and pickle size is large: edit this code' % type(inA))

    return totSize
