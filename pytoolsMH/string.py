
def str2bool_onlyknown(v):
    if v.lower() in ("yes", "true", "t", "1"):
        oV = True
    elif v.lower() in ("no", "false", "f", "0"):
        oV = False
    else:
        raise ValueError('Unknown: %s' % v)
    return oV



