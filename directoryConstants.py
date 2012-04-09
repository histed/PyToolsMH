# this file exists to hold system/user specific constants

import os
(system, hostname, kernVersion, fullUname, arch) = os.uname()

if hostname == 'MaunsellMouse1.local':
    varSyncDir = '/Users/holdanddetect/MWVariables-backups';
elif hostname == 'mambo':
    varSyncDir = '/Users/histed/data/mus-behavior/MWVariables-backups';

