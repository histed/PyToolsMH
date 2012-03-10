from numpy import *
import numpy
import sys
import traceback

############### 
# misc numpy stuff for vectorizing

def binAvg(inArray, axis=0, nInBin=10):
    """sliding-window average an array along a given axis by binning then
    taking mean over each bin

    inArray

    returns: outArr 
        if inArray has shape (nRows, nCols) and axis=0, outArr 
        has shape(floor(nRows/10),nCols)  
    """

    nextAxis = inArray.ndim +1 -1 # 0-origin
    tShape = array(shape(inArray))
    finalEls = floor(tShape[axis]/nInBin)
    maxInEls = finalEls * nInBin

    # define a slice to chop the desired axis so there are no partial bins
    newSlice = [s_[:] for a in range(inArray.ndim)]
    newSlice[axis] = s_[:maxInEls]
    newSlice = tuple(newSlice)
    # chop
    resizedInArray = inArray[newSlice]

    # reshape to get a new axis
    tShape = array(shape(inArray))
    newShape = hstack((tShape, nInBin))
    newShape[axis] = finalEls

    # take mean over the new axis
    outArr = resizedInArray.reshape(newShape).mean(axis=nextAxis)

    return outArr

def findConsecutive(inVec, increment=0):
    """from Matlab code

    %FIND_CONSECUTIVE (ps-utils): return indices of runs of consec. numbers
    %  [STARTI ENDI] = FIND_CONSECUTIVE (INVEC, INCREMENT)
    %
    %  increment is optional and tells what the difference of i and i+1
    %  should be to be considered a run.  (default is 0)
    %
    %  Examples:
    %  invec = [0 0 0 1 2 3 3 0 4 8 10 12 14 24 25 26 27 20 0 0 0];
    %                   |         |             |             |
    %  (index)         (5)       (10)          (15)          (20)
    %
    %  find_consecutive (invec, 1): starti = [ 3 14 ]
    %                               endi   = [ 6 17 ]
    %  find_consecutive (invec, 0): starti = [ 1 6 19 ]
    %                               endi   = [ 3 7 21 ]
    %  find_consecutive (invec, 2): starti = [  9 ]
    %                               endi   = [ 13 ]

    returns: startNs, endNs
    """

    inPrime = diff(inVec)
    desIx = inPrime == increment
    inPP = diff(hstack((0,desIx,0)))

    startNs = where(inPP == 1)[0]
    endNs = where(inPP == -1)[0]

    return (startNs,endNs)

def findConsecutiveTrue(inVec, howMany=2):
    """
    %FIND_CONSECUTIVE_TRUE (ps-utils): indices of consecutive true entries
    %  [STARTI ENDI] = FIND_CONSECUTIVE (INVEC, HOW_MANY)
    %
    %  find consecutive true entries of HOW_MANY or more in a logical vector
    %
    
    Returns: (startNs, endNs)
    """

    inVec = numpy.asarray(inVec,dtype=bool)
    (startS,endS) = findConsecutive(inVec, 0);
    
    runLens = endS-startS;
    isTrueToStart = inVec[startS] == True;
    
    desIx = (runLens >= howMany) & (isTrueToStart);
    
    startNs = startS[desIx];
    endNs = endS[desIx];

    return (startNs, endNs)

def smooth(x,window_len=10,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]


def vec2padded(invec, startNs, endNs=None, pad=NaN, dtype=float64, matOffsets=None):
    """Convert vector to padded 2d array; ragged vectors allowed

    each span from startNs[i] to endNs[i] is a row of the output
        and invec is order='C'

    This ends up being a pretty common array/vector operation for me
    and neither Python or Matlab has it built-in
    
    080621 histed - Ported over from my matlab code
    """

    # fill in parameters
    if endNs is None:
        # compute from startNs
        endNs = r_[startNs[1:]-1, len(invec)]
        assert(all(endNs-startNs) == 1)
    if matOffsets is None:
        matOffsets = numpy.zeros(len(startNs), dtype=int)

    # error checking
    if any(startNs<0) or any(endNs>len(invec)):
        raise ValueError, 'indices range outside of vector'
    if any(endNs-startNs <= 0):
        raise ValueError, 'some ends below start'


    # allocate outmat
    nCols = (endNs-startNs).max()
    nRows = len(startNs)
    if nRows != len(endNs):
        raise ValueError, 'start and end must match'
    outMat = pad + numpy.zeros((nRows,nCols), dtype=dtype, order='C')

    # there has to be a faster way to use this with list comprehensions
    #  that doesn't occur to me right away
    for iR in range(nRows):
        tV = invec[startNs[iR]:endNs[iR]]
        outMat[iR,matOffsets[iR]:size(tV)] = tV

    return outMat

############## 
# done with numpy stuff

def remaining_bytes(fd):
    """Give the number of bytes in the file remaining from file pointer"""
    cur_pos = fd.tell()
    fd.seek(0, 2)
    end_pos = fd.tell()
    fd.seek(cur_pos)
    #print cur_pos
    #print end_pos
    return end_pos - cur_pos

def print_exc_plus():
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """

    tb = sys.exc_info()[2]
    stack = []
    
    while tb:
        stack.append(tb.tb_frame)
        tb = tb.tb_next

    print "Locals by frame, innermost last"
    for frame in stack:
        print
        print "Frame %s in %s at line %s" % (frame.f_code.co_name,
                                             frame.f_code.co_filename,
                                             frame.f_lineno)
        for key, value in frame.f_locals.items():
            print "\t%20s = " % key,
            #We have to be careful not to cause a new error in our error
            #printer! Calling str() on an unknown object could cause an
            #error we don't want.
            try:                   
                print value
            except:
                print "<ERROR WHILE PRINTING VALUE>"

    traceback.print_exc()

#     tb = sys.exc_info()[2]
#     while 1:
#         if not tb.tb_next:
#             break
#         tb = tb.tb_next
#     stack = []
#     f = tb.tb_frame
#     while f:
#         stack.append(f)
#         f = f.f_back
#     stack.reverse()
#     traceback.print_exc()
#     print "Locals by frame, innermost last"


