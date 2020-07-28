
def str2bool_onlyknown(v):
    if v.lower() in ("yes", "true", "t", "1"):
        oV = True
    elif v.lower() in ("no", "false", "f", "0"):
        oV = False
    else:
        raise ValueError('Unknown: %s' % v)
    return oV


def format_bytes(size, format_str='{size:.3g} {suffix}'):
    """"format a number of bytes by reducing the number and adding a metrix suffix

    Returns: 
       formattedStr: formatted with ''.format(size,suffix)

    Examples:
        format_bytes(239842039.48)
        '229 MB'

        format_bytes(239842039.48, format_str='{size:4.3f} {suffix}')
        '228.731 MB'

    From https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/37423778
    """
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'k', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return format_str.format(size=size, suffix=power_labels[n]+'B')

