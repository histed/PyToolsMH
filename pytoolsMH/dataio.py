import os
import pandas as pd
import tables
import warnings
from tables.nodes import filenode
import inspect
import argparse
import numpy as np

from six import iteritems,iterkeys,itervalues
import dill


def saveDataAsH5(fName, objSaveD):
    """Save data in a pandas/pytables HDF5 store
    Note: blosc is best compression tradeoff, complevel 9,8, or 5 may be best"""

    # complete file extension
    (fName0, fExt0) = os.path.splitext(fName)
    if fExt0 == '':
        fExt0 = '.h5'
    if not (fExt0 =='.h5'):
        raise RuntimeError('only .h5 extension is allowed on save file')
    fName= fName0+fExt0

    # this warning happens in pytables when close is called on a closed file: safe to ignore
    # avoid catch_warnings context manager: is not thread safe and makes for ugly extra indents
    warnings.filterwarnings('ignore', 'host PyTables file is already closed')


    # move any existing old file to trash
    if os.path.exists(fName):
        os.system('trash %s' % fName) # needs 'brew install trash', also can use os.remove()
    with pd.HDFStore(fName, complib='blosc', complevel=9) as store:
        # initialize node for saving pickles directly
        store._handle.create_group('/', 'objects')
        for (tF,tVal) in iteritems(objSaveD):
            ## for future ref: should add an elif for np arrays here? pickling them is very fast
            if type(tVal) == pd.DataFrame:
                # save DataFrames directly
                store[tF] = tVal
            else:
                # save non-DataFrames by pickling with dill
                fnode = filenode.new_node(store._handle, where='/objects', name=tF)
                fnode.write(dill.dumps(tVal)) 

                    
def readDataFromH5(fName):
    """Return data from file as a dictionary.  """
    initD = {}
    with pd.HDFStore(fName) as store:
        pdNames = [k[1:] for k in list(store.keys())]  # remove leading slash
        for tP in pdNames:
            initD[tP] = store[tP] 
        pklNames = list(store._handle.root.objects._v_leaves.keys())
        for tP in pklNames:
            initD[tP] = dill.loads(getattr(store._handle.root.objects, tP)[:])
    return initD

## these functions need work: check for file already existing.  deal with non-normalizable var names in namespace.  etc?
# needsa lso: global lookup, probably refactor lookup code into function that caches dicts...

def save(filename, *args):
    """Use the h5 format to save all kinds of objects.  See saveDataAsH5 for disk format.

    Args:
        filename: filename to save into (h5)
        args: objects to save.  In file they will get same name as in calling namespace (if you don't know what that means, don't worry about it)
    Returns:
        None

    Example: dataio.save('Desktop/outfile', array1, array2)
    """
    saveD = {}

    # get name for each obj
    callinglocals = inspect.currentframe().f_back.f_locals
    keyA = np.array(list(callinglocals.keys()), dtype='O')
    valA = np.array(list(callinglocals.values()), dtype='O')
    for tA in args:
        matchIx = valA == tA
        nM = np.sum(matchIx)
        if nM == 1:
            tName = keyA[matchIx][0]
        elif nM > 1:
            raise RuntimeError('bug: more than one match??')
        elif nM == 0:
            raise RuntimeError('name not found in locals.  In globals()?  Add to this code and test')
        saveD.update({tName:tA})

    # write
    saveDataAsH5(filename, saveD)


def load(filename):
    """read objects from h5 format.  Put them in a namespace var"""
    tD = readDataFromH5(filename)
    # if this throws an error, do something nice to clean it up...Named tuple?
    return argparse.Namespace(**tD)



