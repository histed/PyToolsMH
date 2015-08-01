

def extractItems(dikt, keyTuple, ignoreMissing=False):
    """Call as extractDictKeys(d, ("fieldname1", "f2") etc."""
    # adapted from http://stackoverflow.com/questions/9433356/how-to-pass-members-of-a-dict-to-a-function to use a tuple; more similar to usual usage so easier to remember for me

    if not ignoreMissing:
        return dict((k, dikt[k]) for k in keyTuple)
    else:
        return dict((k,dikt[k]) for k in keyTuple if dikt.has_key(k))


def issequence(x):
    """Test if an object is a sequence type -- convenience function

    This kind of test is a little subtle.  We don't want to test for instance types, we want to see if the
    object can be indexed.  Scalars have no len (throws an exception if we test it).  Dicts can be indexed 
    but not necessarily by integers in order.  So we index by a sequence of integers (a slice) and see if 
    an exception is thrown.
    """
    try:
        _a = x[0:]  
        isSeq = True  # i.e. the above succeeded without an exception
    except:
        isSeq = False
    return isSeq

    # below doesn't work because it is true for dicts
    #return hasattr(x, '__getitem__')

    # could check for instances of list, tuple, ndarray, I suppose

    # below False for ndarray
    #return isinstance(x, collections.Sequence)


def lenorzero(x):
    """Return an object's len, or 0 if it has no len (without raising an exception as normally happens)"""
    try:
        tLen = len(x)
    except TypeError:
        tLen = 0
    return tLen

def haslen(x):
    """Test if an object has a len()"""
    try:
        tLen = len(x)
        hasOne = True
    except TypeError:
        hasOne = False
    return hasOne
