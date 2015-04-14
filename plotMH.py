import contextlib
import numpy as np
import statsmodels.api as sm # recommended import; only works for scikits >= 0.4



# Originally from https://gist.github.com/dmeliza/3251476, 140706

from matplotlib.offsetbox import AnchoredOffsetbox
class AnchoredScaleBar(AnchoredOffsetbox):
    def __init__(self, transform, sizex=0, sizey=0, labelx=None, labely=None, loc=4,
                 pad=0.1, borderpad=0.1, sep=2, prop=None, **kwargs):
        """
        Draw a horizontal and/or vertical  bar with the size in data coordinate
        of the give axes. A label will be drawn underneath (center-aligned).
 
        - transform : the coordinate frame (typically axes.transData)
        - sizex,sizey : width of x,y bar, in data units. 0 to omit
        - labelx,labely : labels for x,y bars; None to omit
        - loc : position in containing axes
        - pad, borderpad : padding, in fraction of the legend font size (or prop)
        - sep : separation between labels and bars in points.
        - **kwargs : additional arguments passed to base class constructor
        """
        from matplotlib.patches import Rectangle
        from matplotlib.offsetbox import AuxTransformBox, VPacker, HPacker, TextArea, DrawingArea
        bars = AuxTransformBox(transform)
        if sizex:
            bars.add_artist(Rectangle((0,0), sizex, 0, fc="none"))
        if sizey:
            bars.add_artist(Rectangle((0,0), 0, sizey, fc="none"))
 
        if sizex and labelx:
            bars = VPacker(children=[bars, TextArea(labelx, minimumdescent=False)],
                           align="center", pad=0, sep=sep)
        if sizey and labely:
            bars = HPacker(children=[TextArea(labely), bars],
                            align="center", pad=0, sep=sep)
 
        AnchoredOffsetbox.__init__(self, loc, pad=pad, borderpad=borderpad,
                                   child=bars, prop=prop, frameon=False, **kwargs)
 
def add_scalebar(ax, matchx=True, matchy=True, hidex=True, hidey=True, fmtstrx='%.1f', fmtstry='%.1f', **kwargs):
    """ Add scalebars to axes
 
    Adds a set of scale bars to *ax*, matching the size to the ticks of the plot
    and optionally hiding the x and y axes
 
    - ax : the axis to attach ticks to
    - matchx,matchy : if True, set size of scale bars to spacing between ticks
                    if False, size should be set using sizex and sizey params
    - hidex,hidey : if True, hide x-axis and y-axis of parent
    - fmtstrx,fmtstry : label format string to use to generate labels.  
           e.g. xlabel is fmtstrx % sizex.  defaults: '%.1f'
    - **kwargs : additional arguments passed to AnchoredScaleBars
 
    Returns created scalebar object
    """
    def f(axis):
        l = axis.get_majorticklocs()
        return len(l)>1 and (l[1] - l[0])
    
    if matchx:
        kwargs['sizex'] = f(ax.xaxis)
        kwargs['labelx'] = fmtstrx % kwargs['sizex']
    if matchy:
        kwargs['sizey'] = f(ax.yaxis)
        kwargs['labely'] = fmtstry % kwargs['sizey']
        
    sb = AnchoredScaleBar(ax.transData, **kwargs)
    ax.add_artist(sb)
 
    if hidex : ax.xaxis.set_visible(False)
    if hidey : ax.yaxis.set_visible(False)
 
    return sb

################

def newplotMH():
    """Like MATLAB's newplot"""
    if plt.gca().ishold() == True:
        return (plt.gca().figure, plt.gca())
    else:
        figH = figure()
        axH = axes()
        return (figH, axH)


################

# this is a numpy helper to prevent stripping zeros from the end of floats
# http://stackoverflow.com/questions/2891790/pretty-printing-of-numpy-array

# There's now a new way to do this, apparently: 
#  np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
@contextlib.contextmanager
def printoptions(strip_zeros=True, **kwargs):
    origcall = np.core.arrayprint.FloatFormat.__call__
    def __call__(self, x, strip_zeros=strip_zeros):
        return origcall.__call__(self, x, strip_zeros)
    np.core.arrayprint.FloatFormat.__call__ = __call__
    original = np.get_printoptions()
    np.set_printoptions(**kwargs)
    yield 
    np.set_printoptions(**original)
    np.core.arrayprint.FloatFormat.__call__ = origcall

#################################################

def cdfXY(inputV):
    """compute empirical cdf from input vector.
    Use:
    (x,y) = cdfXY(inputV)
    plt.step(x,y)

    Note: for many X values / RV levels this can be inefficient - can add code to deal with that case
    (instead of using every x value, subset using e.g. linspace() )
    """
    ecdf = sm.distributions.ECDF(inputV)
    #x = np.linspace(min(inputV), max(inputV))
    x = np.unique(inputV)
    y = ecdf(x)
    return  (x,y)
