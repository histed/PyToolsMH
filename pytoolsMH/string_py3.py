import copy
import types
from . import string as ptstring # py2/py3 both
from . import memProfile as ptmp
import numpy as np
r_ = np.r_

"""This module doesn't support py2 due to fstrings here"""

def whos_obj(obj, skip_underscores=False):
    """Run whos_dict() on obj's attributes (found with obj(dir)

    Note skip_underscores is False by default here
    """
    whos_dict({k:getattr(obj,k) for k in dir(obj)}, skip_underscores=skip_underscores)
    

def whos_dict(in_dict, skip_underscores=True):
    """Show information in summary form of variables in a dict.

    Similar to %whos, whos in ipython, matlab but can be called on an arbitrary sequence.
    Useful as whos_vars(dir(object)) to see all attribs of an object

    Args: 
         in_dict:
        skip_underscores: True by default
    
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
    Todo:
        - 200730: could clean up the formatting to look much more like ipython's %whos

        - 200727: created MH

    """
    # 
    
    curr = copy.copy(in_dict)
    typeD = {k: type(v) for k,v in curr.items()}

    skipL = []
    def print_by_type(curr, print_type=types.ModuleType, title='Modules: '):
        modKL = [k for k,v in typeD.items() if v == print_type and not (skip_underscores and k[0] == '_') ]
        print('%s\n  '%title, end='')
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
        if (skip_underscores and tK[0] == '_') or tK in skipL:
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
        doSize = True
        if tname == 'list' or tname == 'tuple' or tname == 'dict':
            extraS = f'len {len(tV)}'
        elif tname == 'ndarray':
            extraS = f'shape {str(np.shape(tV)):12} dtype {tV.dtype}'
        elif tname == 'method' or tname == 'builtin_function_or_method' or tname == 'method-wrapper':
            tDoc = tV.__doc__
            # pull out first non-empty line once whitespace is removed
            if type(tDoc) == str:  # can be None
                tDocL = [x.strip() for x in tDoc.split("\n")]
                tLens = r_[[len(x) for x in tDocL]]
                firstN = np.nonzero(tLens)[0]
                if len(firstN) > 0:
                    extraS = tDocL[firstN[0]]
            doSize = False

        fullStr = f'{tK:25}: {modS:40}: {extraS:40}'

        if doSize:
            # size in bytes
            sizeStr = ptstring.format_bytes(ptmp.total_size(tV), format_str='{size:4.0f} {suffix}')
            fullStr = fullStr + f': size: {sizeStr}'

        # print it
        print(fullStr)

        nPrinted = nPrinted + 1
