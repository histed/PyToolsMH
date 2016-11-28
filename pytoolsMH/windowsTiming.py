# histed 120724
#
# mostly copied from pyglet:
#   http://code.google.com/p/pyglet/issues/attachmentText?id=445&aid=-2288975315691413876&name=windowstimer.py&token=68bf0416226af9080cf91ec9aa168356

import time

from ctypes import *
from ctypes.wintypes import DWORD

timeGetDevCaps = windll.winmm.timeGetDevCaps
timeBeginPeriod = windll.winmm.timeBeginPeriod
timeEndPeriod   = windll.winmm.timeEndPeriod
timeSetEvent = windll.winmm.timeSetEvent
timeKillEvent = windll.winmm.timeKillEvent

class TIMECAPS(Structure):
    _fields_ = [("wPeriodMin",c_uint),
                ("wPeriodMax",c_uint)
                ]

caps = TIMECAPS()
timeGetDevCaps(byref(caps), sizeof(caps))

def timerTest(resolution, duration):
    start = time.clock()
    end = start + duration
    now = start
    count = 0
    while now < end:
        time.sleep(resolution)
        count += 1
        now = time.clock()
    return 1.0*duration/count*1000 # resolution, ms

################################################################
# testing below

debugLevel = 0

if debugLevel > 0:
    print(timerTest(0.001, 3))

    timeBeginPeriod(caps.wPeriodMin)
    print(timerTest(0.001, 3))
    timeEndPeriod(caps.wPeriodMin)

    timeBeginPeriod(10)
    print(timerTest(0.001, 3))
    timeEndPeriod(10)

    timeBeginPeriod(caps.wPeriodMax)
    print(timerTest(0.001, 3))
    timeEndPeriod(caps.wPeriodMax)

