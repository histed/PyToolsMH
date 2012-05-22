# this file exists to hold system/user specific constants

import os, string

(system, hostname, kernVersion, fullUname, arch) = os.uname()

hostname = string.replace(hostname, '.local', '')
if hostname == 'MaunsellMouse1':
    varSyncDir = '/Users/holdanddetect/MWVariables-backups';
elif hostname == 'mambo':
    varSyncDir = '/Users/histed/data/mus-behavior/MWVariables-backups';

