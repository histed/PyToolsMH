import shutil



def check_min_gb(indir, mingb):
    """Check if directory has at least minGb Gb remaining space, else raise error"""
    stot, sused, sfree = shutil.disk_usage(indir)
    if sfree / 1e9 < mingb:
        raise RuntimeError('%.3GB, less than %.3gGB of space left in dir %s, cannot continue'
                           % (sfree/1e9, mingb, indir))