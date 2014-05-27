import ctypes, ctypes.util
import sys
import time
import logging
import numpy as np
cocoa = ctypes.cdll.LoadLibrary(ctypes.util.find_library("Cocoa"))

# based on some psychopy calls.  See https://github.com/psychopy/psychopy/blob/dae85517020cb1da2e5bebc9d804f0fa9465a71c/psychopy/platform_specific/darwin.py

### constants
#############

# see thread_policy.h (Darwin)
THREAD_STANDARD_POLICY=ctypes.c_int(1)
THREAD_STANDARD_POLICY_COUNT=ctypes.c_int(0 )
THREAD_TIME_CONSTRAINT_POLICY=ctypes.c_int(2)
THREAD_TIME_CONSTRAINT_POLICY_COUNT=ctypes.c_int(4)
KERN_SUCCESS=0;

class timeConstraintThreadPolicy(ctypes.Structure):
    _fields_ = [('period', ctypes.c_uint),
        ('computation', ctypes.c_uint),
        ('constrain', ctypes.c_uint),
        ('preemptible', ctypes.c_int)]


def getCpuFreq():
    """Frequency of cpu (HZ var in Mach kernel)"""

    CTL_HW=ctypes.c_int(6) # see  http://stackoverflow.com/questions/8147796/iphone-getting-cpu-frequency-not-run
    HW_BUS_FREQ=ctypes.c_int(14)

    mib = (ctypes.c_int*2)(CTL_HW, HW_BUS_FREQ)
    val = ctypes.c_int(0)
    intSize = ctypes.c_int(ctypes.sizeof(val))
    cocoa.sysctl(ctypes.byref(mib), 2, ctypes.byref(val), ctypes.byref(intSize), 0, 0)
    return val.value


def setRealtime(doRealtime=True):
    """ doRealtime: raise priority to realtime.  False: lower to normal
    """
    HZ = getCpuFreq()

    if doRealtime:
        extendedPolicy = timeConstraintThreadPolicy()
        extendedPolicy.period = HZ/100 # abstime units, length of one bus cycle: this means run every 10 ms
        extendedPolicy.computation = extendedPolicy.period/4 # give up to this time to execute
        extendedPolicy.constrain = extendedPolicy.period # and allow cpu cycles to be distributed anywhere in period
        extendedPolicy.preemptible=1
        extendedPolicy=getThreadPolicy(getDefault=True, flavour=THREAD_TIME_CONSTRAINT_POLICY)
        err=cocoa.thread_policy_set(cocoa.mach_thread_self(), THREAD_TIME_CONSTRAINT_POLICY,
            ctypes.byref(extendedPolicy), #send the address of the struct
            THREAD_TIME_CONSTRAINT_POLICY_COUNT)
        if err!=KERN_SUCCESS:
            raise RuntimeError('Failed to set darwin thread policy, with thread_policy_set')
        else:
            pMs = np.array([extendedPolicy.period, extendedPolicy.computation, extendedPolicy.constrain]) / 1000.0
            logging.info('Successfully set darwin thread to realtime (per comp constrain: %d %d %d)'.format(x[1] for x in enumerate(pMs)))

    else:
        #revert to default policy
        extendedPolicy=getThreadPolicy(getDefault=True, flavour=THREAD_STANDARD_POLICY)
        err=cocoa.thread_policy_set(cocoa.mach_thread_self(), THREAD_STANDARD_POLICY,
            ctypes.byref(extendedPolicy), #send the address of the struct
            THREAD_STANDARD_POLICY_COUNT)
    return True


def getThreadPolicy(getDefault, flavour):
    """Retrieve the current (or default) thread policy.

    getDefault should be True or False
    flavour should be 1 (standard) or 2 (realtime)

    Returns a ctypes struct with fields:
    .period
    .computation
    .constrain
    .preemptible

    See http://docs.huihoo.com/darwin/kernel-programming-guide/scheduler/chapter_8_section_4.html"""

    extendedPolicy=timeConstraintThreadPolicy()
    getDefault=ctypes.c_int(getDefault) #we want to retrieve actual policy or the default
    err=cocoa.thread_policy_get(cocoa.mach_thread_self(), THREAD_TIME_CONSTRAINT_POLICY,
        ctypes.byref(extendedPolicy), #send the address of the policy struct
        ctypes.byref(THREAD_TIME_CONSTRAINT_POLICY_COUNT),
        ctypes.byref(getDefault))
    return extendedPolicy
