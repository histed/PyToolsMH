import sys
import warnings


# customize this for other systems we use as needed
if sys.platform == 'darwin':
    # should provide init code for the curses-based way of getting keypresses
    pass
elif sys.platform == 'win32':
    import msvcrt






def kbhit():
    if sys.platform == 'darwin':
        warnings.warn('No kbhit() yet for darwin')
        # can implement the curses-based solution
        return False
    elif sys.platform == 'win32':
        return msvcrt.kbhit()
    else:
        raise RuntimeError('Unknown platform: bug')
    

def getch():
    if sys.platform == 'darwin':
        warnings.warn('No getch() yet for darwin')
        # can implement the curses-based solution
        return False
    elif sys.platform == 'win32':
        return msvcrt.getch()
    else:
        raise RuntimeError('Unknown platform: bug')
