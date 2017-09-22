# windowsTiming histed 120724
#
# To reduce interrupt latency / min sleep time to 1ms in windows: call timeBeginPeriod(1)   - default is 10ms.

# As of 170914: this still works on win 7 to decrease sleep time: before 10ms, after 1ms
#  2017-09-12 10:35:47,084 Testing minimum sleep time before and after reset:
#  2017-09-12 10:35:48,094 Before: 9.9ms
#  2017-09-12 10:35:49,095 After: 1.0ms

# Timer interrupt stuff mostly copied from pyglet in 2009 (long since changed in pyglet).
#   http://code.google.com/p/pyglet/issues/attachmentText?id=445&aid=-2288975315691413876&name=windowstimer.py&token=68bf0416226af9080cf91ec9aa168356
#


import time
import psutil
import os

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

def set_priority_high():
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)

def set_priority_realtime():
    p = psutil.Process(os.getpid())
    p.nice(psutil.REALTIME_PRIORITY_CLASS)


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

