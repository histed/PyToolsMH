

def extractItems(dikt, keyTuple, ignoreMissing=False):
    """Call as extractDictKeys(d, ("fieldname1", "f2") etc."""
    # adapted from http://stackoverflow.com/questions/9433356/how-to-pass-members-of-a-dict-to-a-function to use a tuple; more similar to usual usage so easier to remember for me

    if not ignoreMissing:
        return dict((k, dikt[k]) for k in keyTuple)
    else:
        return dict((k,dikt[k]) for k in keyTuple if dikt.has_key(k))


