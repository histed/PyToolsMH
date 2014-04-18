import sys
import warnings
import msvcrt

# todo: need to figure out best way to tell what system we're on.  sys.platform?

if sys.platform == 'darwin':
    pass
else:
    raise RuntimeError, 'Need to deal with new system/platform'
    import msvcrt






def kbhit():
    if sys.platform == 'darwin':
        warnings.warn('No getch() yet for darwin')
        return False
    elif sys.platform =='win':
        return msvcrt.kbhit()
    

