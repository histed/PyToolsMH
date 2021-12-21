## math, vector and numpy related tools.  Includes: chop, smooth.  Not completely tested.
#
#  TODO
#    Add tests, esp for smooth and related.  180501
#
# histed imported 120309
#


import numpy as np
import scipy.interpolate
import scipy.signal as ss
import sys

a_ = np.asarray
r_ = np.r_




def smooth(y, x=None, span=None, method='lowess', axis=-1, **kwArgs):
    """Smooth a signal or timeseries.  Master function for smoothing that can use different smoothing methods.

    Arguments:
        method: str ('lowess' (default), 'sgolay', 'moving') type of smoother.
           lowess: extra args: robust
           sgolay: polyorder default is 2, see args: mode, cval, delta, etc.
        span: number of points, or percentage of data, to use as basic smoothing unit
        y: data to smooth
        x: vector of len y.shape[axis], x points / indep var for data

    """
    # for SG and lowess comparison see:
    # http://homepages.ihug.co.nz/~deblight/AUTResearch/papers/Black_Art_Smoothing.pdf

    y = np.asarray(y)
    npts = y.shape[axis]
    if x is None:
        x = np.arange(npts)  # evenly spaced 0..npts
    #print(len(x),len(y))

    if method == 'lowess':
        return smooth_lowess(y, x, span=span, axis=axis, **kwArgs)
    elif method == 'rlowess':  # shortcut for matlab compatibility
        return smooth_lowess(y, x, span=span, axis=axis, robust=True, **kwArgs)
    elif method == 'sgolay':
        if span < 1:
            span = span*np.shape(y)[axis]  # convert pct to number of pts
        if len(np.unique(np.diff(x))) > 1:
            raise RuntimeError('Cannot pass x with different stepsizes to sgolay')
        if not 'polyorder' in kwArgs:  # not present, set default 2
            kwArgs['polyorder'] = 2
        if 'degree' in kwArgs:  # compat with matlab
            kwArgs['polyorder'] = kwargs['degree']
        return ss.savgol_filter(y, window_length=int(span), axis=axis, **kwArgs)
    elif method == 'moving':
        if len(np.unique(np.diff(x))) > 1:
            raise RuntimeError('Cannot pass x with different stepsizes to moving')
        return smooth_filter(y, window_len=int(span), window='flat', axis=axis)









def smooth_lowess_biostat(y, x=None, span=10, iter=3):
    """Uses Bio.statistics.  This is slow.
    span is number of pts, as in matlab smooth.m"""
    # smooth with lowess:
    # from Bio.Statistics.lowess import lowess
    # lowess(x,y,f,iter)  f is in range [0..1]
    #   I believe the Biopython lowess uses a 1-degree polynomial
    #   code is  http://biopython.org/DIST/docs/api/Bio.Statistics.lowess-pysrc.html#lowess

    import Bio.Statistics.lowess
    
    if x is None:
        x = np.arange(len(y), dtype='float')
    if len(y) < 2:
        raise ValueError('Input must have length > 1')
    
    nPts = len(y)

    if span > (nPts-1):
        span = nPts-1
    f = 1.0*span/nPts

    smY = Bio.Statistics.lowess.lowess(np.asarray(x,dtype='float'),
                                       np.asarray(y, dtype='float'),
                                       f,iter=iter)

    return smY


def smooth_lowess_bootstrap(y, x=None, ci=95, nbootreps=1000, noutpts=100, **kwargs):
    """Bootstraps confidence intervals around a lowess smoothing fit
    Args:
        noutpts: number of points in even grid each boostrap run is interpolated to
        **kwargs: args passed directly to smooth_lowess
    Returns:
        (ylow, yhigh, out_xs, boot_mat)
        out_xs: since we reinterpolate over a new x grid for each bootstrap run,
          we need these for plotting
    Notes:
        - to avoid having multiple items at a single point we add a small value to each x,
          could perhaps do this better by setting a weight in lowess()
    """
    def single_sm(xs0, ys0):
        sortNs = np.argsort(xs0)
        xs0 = xs0[sortNs]
        ys0 = ys0[sortNs]
        ysSm = smooth_lowess(ys0, xs0, **kwargs)
        return ysSm, xs0
    if x is None:
        x = np.r_[0:len(y)]
    xs,ys = x,y

    nPts = len(y)
    out_xs = np.linspace(np.min(x), np.max(x), noutpts)
    bm = np.nan*np.zeros((nbootreps, noutpts))
    # find the random offset for jitter: 1e-4*smallest spacing
    adj_xs = np.min(np.abs(np.diff(sorted(xs))))*0.0001 #don't allow getting to zero
    assert np.all(adj_xs > sys.float_info.epsilon*1000), 'xs too tightly spaced for this random strategy'
    # shifting to weighting instead of jitter would fix the above
    for iB in range(nbootreps):
        bNs = np.random.choice(np.arange(nPts), size=(nPts,), replace=True)
        xsB = xs[bNs]
        ysB = ys[bNs]

        xsB = xsB + np.random.rand(len(xsB))*adj_xs
        ysSm, xs0 = single_sm(xsB, ysB)
        ysOut = np.interp(out_xs, xs0, ysSm)
        bm[iB,:] = ysOut
    plow = np.percentile(bm, 100-ci, axis=0)
    phigh = np.percentile(bm, ci, axis=0)
    return (plow, phigh, out_xs, bm)




def smooth_lowess(y, x=None, span=10, robust=False, iter=None, axis=-1):
    """Uses statsmodels.  As of around 2013, this is faster than Bio.statistics.
    Args:
        y: ndarray, can be 2d  (or maybe N-d - needs testing)
        x: None (default) or 1d ndarray, same length as specified axis of y.  If None, use 1:len(y)
        robust: bool, default False.  Whether to reweight to reduce influence of outliers, see docs
        span: number of pts, or percent of total number of points, as in matlab smooth.m
        axis: the axis to smooth over.

    Notes:
        Has MATLAB's nan behavior: drops nan's before smoothing, then puts the nans
        back in the same places in the smoothed array and returns.
    """
    
    import statsmodels.nonparametric.api

    if iter is not None:
        raise RuntimeError('iter no longer used: use robust param instead')

    y = a_(y, dtype='f8')
    nPts = y.shape[axis]

    if x is None:
        x = np.arange(nPts, dtype='float')
    else:
        x = a_(x, dtype='f8')
    if nPts < 2:
        raise ValueError('Input must have length > 1')
    if len(x) != np.shape(y)[axis]:
        raise ValueError('x has len %d, mismatch with y (ax %d), has len %d'
                         % (len(x), axis, np.shape(y)[axis]))

    assert (np.all(np.diff(x)>0)), 'x must be strictly increasing'  # or output will be all nans

    if span > (nPts-1):
        span = nPts-1
    if span < 1:
        frac = span  # percent
    else:
        frac = 1.0*span/nPts  # is number of points, convert to span

    if robust:
        iter = 5
    else:
        iter = 1

    delta = np.min((0.01 * np.ptp(x), span/5))  # hardcode.  first is suggestion in docs

    # iterate over the specified axis.  Note we need a func because lowess() returns a tuple
    def runonvec(y,x,frac,iter,delta):
        # remove nans manually
        ns = np.where(~np.isnan(y))
        ysm = statsmodels.nonparametric.api.lowess(y[ns],x[ns],
                                                    frac, it=iter, delta=delta, missing='raise')[:,1]
        yret = y.copy() # contains nans
        yret[ns] = ysm
        return yret
    smY = np.apply_along_axis(runonvec, axis, y, x, frac, iter, delta)

    return smY


def smooth_spline(y, x=None, knots=None, degree=3):
    """knots is s in scipy.interpolate.UnivariateSpline"""
    if x is None:
        x = np.arange(len(y))
    if len(y) < 2:
        raise ValueError('Input must have length > 1')
    s = scipy.interpolate.UnivariateSpline(x, y, w=None, bbox=[None,None], k=degree, s=knots)
    return s(x)


def chop(x0, sig=2):
    xin_ndim = np.ndim(x0)
    x0 = np.atleast_1d(x0) # will promote scalars to an array
    zeroIx = np.array(x0)==0
    x = np.array(x0, dtype='f8')  # must be float for chop to make sense.  Later, support single precision?
    x[zeroIx] = 1  # will unmask below
    nSig = sig-(np.floor(np.log10(np.abs(x))))-1
    chopped = np.array([np.around(x0,int(n0)) for (x0,n0) in zip(x,nSig)])
    chopped[zeroIx] = 0
    if xin_ndim == 0:
        chopped = np.squeeze(chopped) # drop back to 0-d if scalar passed in
    return chopped


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
    tShape = np.array(shape(inArray))
    finalEls = np.floor(tShape[axis]/nInBin)
    maxInEls = finalEls * nInBin

    # define a slice to chop the desired axis so there are no partial bins
    newSlice = [s_[:] for a in range(inArray.ndim)]
    newSlice[axis] = s_[:maxInEls]
    newSlice = tuple(newSlice)
    # chop
    resizedInArray = inArray[newSlice]

    # reshape to get a new axis
    tShape = np.array(shape(inArray))
    newShape = np.hstack((tShape, nInBin))
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

    inPrime = np.diff(inVec)
    desIx = inPrime == increment
    inPP = np.diff(np.hstack((0,desIx,0)))

    startNs = np.where(inPP == 1)[0]
    endNs = np.where(inPP == -1)[0]

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

    inVec = np.asarray(inVec,dtype=bool)
    (startS,endS) = findConsecutive(inVec, 0);
    
    runLens = endS-startS;
    isTrueToStart = inVec[startS] == True;
    
    desIx = (runLens >= howMany) & (isTrueToStart);
    
    startNs = startS[desIx];
    endNs = endS[desIx];

    return (startNs, endNs)


def smooth_filter(x, window_len=10, window='hanning', axis=-1):
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
    
    np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

    x = np.asarray(x)

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len<3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    def run_conv(x, wnorm, window_len):
        s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]
        y=np.convolve(wnorm,s,mode='same')
        return y[window_len-1:-window_len+1]

    return np.apply_along_axis(run_conv, axis, x, w/w.sum(), window_len)


def vec2padded(invec, startNs, endNs=None, pad=np.NaN, dtype='float64', matOffsets=None):
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
        matOffsets = np.zeros(len(startNs), dtype=int)

    # error checking
    if any(startNs<0) or any(endNs>len(invec)):
        raise ValueError('indices range outside of vector')
    if any(endNs-startNs <= 0):
        raise ValueError('some ends below start')


    # allocate outmat
    nCols = (endNs-startNs).max()
    nRows = len(startNs)
    if nRows != len(endNs):
        raise ValueError('start and end must match')
    outMat = pad + np.zeros((nRows,nCols), dtype=dtype, order='C')

    # there has to be a faster way to use this with list comprehensions
    #  that doesn't occur to me right away
    for iR in range(nRows):
        tV = invec[startNs[iR]:endNs[iR]]
        outMat[iR,matOffsets[iR]:size(tV)] = tV

    return outMat

def convertToFloat(listV):
    """convert list to float; deals with errors by substituting NaNs"""
    outA = np.ones((len(listV),))*np.NaN

    for i, tItem in enumerate(listV):
        try:
            outA[i] = np.float(tItem)
        except:
            outA[i] = np.NaN;  # failure to convert

    return(outA)

def local_minima(fits, window=15):
    """fm Zachary Pinkus"""
    from scipy.ndimage import minimum_filter
    fits = np.asarray(fits)
    minfits = minimum_filter(fits, size=window, mode="wrap")
    minima_mask = fits == minfits
    good_indices = np.arange(len(fits))[minima_mask]
    good_fits = fits[minima_mask]
    order = good_fits.argsort()
    return good_indices[order], good_fits[order] 

################

# functions to estimate the correct number of bins in a histogram
# See:
# http://stats.stackexchange.com/questions/798/calculating-optimal-number-of-bins-in-a-histogram-for-n-where-n-ranges-from-30

def nBinsFD(inArr):
    """Freedman-Diaconis algorithm to find number of bins in a histogram
    Returns: nBins (integer)"""
    nBins = np.ptp(inArr) / (2* (np.percentile(gs,75)-np.percentile(gs,25)) * len(inArr)**(-1/3.0) )
    return int(np.ceil(nBins))

def nBinsSS(inArr):
    """Shimazaki and Shinomoto algorithm to find number of bins in a histogram
    Returns: nBins (integer)"""
    # Shimazaki and Shinomoto Neural Comput 2007 http://176.32.89.45/~hideaki/res/histogram.html
    N_MIN = 4   #Minimum number of bins (integer)
                #N_MIN must be more than 1 (N_MIN > 1).
    N_MAX = 50  #Maximum number of bins (integer)
    N = np.arange(N_MIN,N_MAX) # #of Bins
    D = np.ptp(inArr)/N    #Bin size vector
    C = np.zeros(shape=(np.size(D),1))

    #Computation of the cost function
    for i in range(np.size(N)):
        edges = np.linspace(np.min(inArr),np.max(inArr),N[i]+1) # Bin edges
        ki = np.histogram(inArr,edges)[0] # Count # of events in bins
        k = np.mean(ki) #Mean of event count
        v = np.sum((ki-k)**2)/N[i] #Variance of event count
        C[i] = (2*k-v)/((D[i])**2) #The cost Function
    #Optimal Bin Size Selection
    return N[np.argmin(C)]+1  # D[argmin(C)] is the optimal bin size, I believe

################
# see http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array

def find_idx_nearest_val(array, value):
    """Return index of vector's closest value to the one specified.

    Args:
        array: input vector
        value: to search for

    Returns: nearest_index (integer)

    Todo:
        check: does this work only with vectors?  or multi-dim arrays?
    """
    idx_sorted = np.argsort(array)
    sorted_array = np.array(array[idx_sorted])
    idx = np.searchsorted(sorted_array, value, side="left")
    if idx >= len(array):
        idx_nearest = idx_sorted[len(array)-1]
        return idx_nearest
    elif idx == 0:
        idx_nearest = idx_sorted[0]
        return idx_nearest
    else:
        if abs(value - sorted_array[idx-1]) < abs(value - sorted_array[idx]):
            idx_nearest = idx_sorted[idx-1]
            return idx_nearest
        else:
            idx_nearest = idx_sorted[idx]
            return idx_nearest
