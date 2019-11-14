import shutil
# lazy load, dont' import git here, requires gitpython, present in mh37c envs et al


def get_git_root(path):
    """Given a directory or file, find the enclosing git repo path"""
    import git
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root


def get_git_branch(path):
    """Given a directory or file, find the branch of any enclosing git repo"""
    import git
    git_repo = git.Repo(path, search_parent_directories=True)
    return git_repo.active_branch.name


def check_min_gb(indir, mingb):
    """Check if directory has at least minGb Gb remaining space, else raise error"""
    stot, sused, sfree = shutil.disk_usage(indir)
    if sfree / 1e9 < mingb:
        raise RuntimeError('%.3GB, less than %.3gGB of space left in dir %s, cannot continue'
                           % (sfree/1e9, mingb, indir))