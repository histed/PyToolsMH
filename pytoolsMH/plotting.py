import contextlib
import numpy as np
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore") # 180109: block FutureWarning. Can delete this in future.  see https://github.com/statsmodels/statsmodels/issues/3868
    import statsmodels.api as sm # recommended import; only works for scikits >= 0.4
import matplotlib.pyplot as plt

r_ = np.r_
a_ = np.asarray
# 170905: MH: 
# 140706: Originally from https://gist.github.com/dmeliza/3251476,

from matplotlib.offsetbox import AnchoredOffsetbox
class AnchoredScaleBar(AnchoredOffsetbox):
    """Draw a scalebar with labels on an axis."""

    def __init__(self, transform, sizex=0, sizey=0, labelx=None, labely=None, loc=4,
                 pad=0.1, borderpad=0.1, sep=2, linewidth=3, prop=None, fontprops={},
                 **kwargs):
        """
        Args:
            - transform : the coordinate frame (typically axes.transData)
            - sizex,sizey : width of x,y bar, in data units. 0 to omit
            - labelx,labely : labels for x,y bars; None to omit
            - loc : position in containing axes
            - pad, borderpad : padding, in fraction of the legend font size (or prop)
            - sep : separation between labels and bars in points.
            - fontprops: dict specifying text label properties, https://matplotlib.org/users/text_props.html
            - **kwargs : additional arguments passed to base class constructor
        """

        from matplotlib.patches import Rectangle
        from matplotlib.lines import Line2D
        from matplotlib.offsetbox import AuxTransformBox, VPacker, HPacker, TextArea, DrawingArea, OffsetBox

        fontprops.update({'fontsize': 8})  # need fontprops defaults here, otherwise overwritten on change if in fn defn
        
        bars = AuxTransformBox(transform)

        bars.add_artist(Line2D((0,0,sizex),(sizey,0,0), lw=linewidth,
                                   color='k', solid_capstyle='butt', solid_joinstyle='miter'))

        # Note: this packs the y label and both bars together into a box, then packs the x label below the box, so the
        # x label is slightly off center of the x bar.  This can cause some small alignment problems, but fixing it requires knowledge
        # of matplotlib offsetboxes, auxtransformboxes, and transforms that I don't have.
        if sizey and labely:
            bars = HPacker(children=[TextArea(labely.strip(), textprops=fontprops), bars],
                            align="center", pad=0, sep=sep)
        if sizex and labelx:
            bars = VPacker(children=[bars, TextArea(labelx.strip(), minimumdescent=False, textprops=fontprops)],
                           align="center", pad=0, sep=sep)
 
        AnchoredOffsetbox.__init__(self, loc, pad=pad, borderpad=borderpad,
                                   child=bars, prop=prop, frameon=False, **kwargs)
 
def add_scalebar(ax, sizex=None, sizey=None, hidex=True, hidey=True,
                 fmtstrx='%.1f', fmtstry='%.1f', **kwargs):
    """ Add scalebars to axes
 
    Adds a set of scale bars to *ax*, matching the size to the ticks of the plot
    and optionally hiding the x and y axes
 
    Args:
        - ax : the axis to attach ticks to
        - sizex,sizey: 
            None (Default): set size of scale bars to spacing between ticks
            numeric value: sets size of x and y bars in data units
        - hidex,hidey : if True, hide x-axis and y-axis of parent
        - fmtstrx,fmtstry : label format string to use to generate labels.  
               e.g. xlabel is fmtstrx % sizex.  defaults: '%.1f'
        - **kwargs : additional arguments passed to AnchoredScaleBars
 
    Returns created scalebar object
    """
    def f(axis):
        l = axis.get_majorticklocs()
        return len(l)>1 and (l[1] - l[0])

    if sizex is None:
        sizex = f(ax.xaxis)
    if sizey is None:
        sizey = f(ax.yaxis)

    kwargs['labelx'] = fmtstrx % sizex 
    kwargs['labely'] = fmtstry % sizey
        
    sb = AnchoredScaleBar(ax.transData, sizex=sizex, sizey=sizey, **kwargs)
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

def cdfplot(inputV):
    """Plot empirical cdf of input vector.

    Calls plotMH.cdfXY
    """
    (x,y) = cdfXY(inputV)

    xp = np.hstack((np.min(inputV),x,np.max(inputV)))
    yp = np.hstack((0,y,1))
    tH = plt.step(xp,yp)

    return tH

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

################
# small plotting style functions

def setAxFontSizes(text_pts=7, ticklabel_pts=6, axH=None):
    """quickly rescale font sizes on axes, e.g. to prepare for print"""
    if axH is None:
        axH = plt.gca()
    for tA in [axH.title, axH.xaxis.label, axH.yaxis.label]:
        tA.set_fontsize(text_pts)
    for tA in axH.get_xticklabels()+axH.get_yticklabels():
        tA.set_fontsize(ticklabel_pts)
    
