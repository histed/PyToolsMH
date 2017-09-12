import unittest
from unittest import TestCase
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from pytoolsMH import plotting

class TestScalebar(unittest.TestCase):

    #def setUp(self):

    def test_make_scalebar(self):
        xs = np.r_[0:100]
        ys = np.sqrt(xs)
        gs = mpl.gridspec.GridSpec(3,3)
        
        figH = plt.figure()

        ax = plt.subplot(gs[0,0])
        plt.plot(xs,ys)
        plotting.add_scalebar(ax) # all defaults
        plt.title('defaults')

        ax = plt.subplot(gs[1,0])
        plt.plot(xs,ys)
        plotting.add_scalebar(ax, hidex=False, hidey=False)
        plt.title('no hide')

        ax = plt.subplot(gs[2,0])
        plt.plot(xs,ys)
        plotting.add_scalebar(ax, sizex=10, sizey=2)
        plt.title('sizes')

        ax = plt.subplot(gs[0,1])
        plt.plot(xs,ys)
        plotting.add_scalebar(ax, sizex=12.1, fmtstrx='%0.2g')
        plt.title('fmtstrx')

        ax = plt.subplot(gs[1,1])
        plt.plot(xs,ys)
        plotting.add_scalebar(ax, sizex=12.1, fmtstrx='%0.2g stuff', fmtstry='%.4g thing')
        plt.title('both fmtstrs')

        ax = plt.subplot(gs[2,1])
        plt.plot(xs,ys)
        plotting.add_scalebar(ax, sizex=12.1, fmtstrx='%0.2g stuff', fmtstry='%.4g 6pt', fontprops={'fontsize':6})
        plt.title('smaller font')

        ax = plt.subplot(gs[0,2])
        plt.plot(xs,ys)
        plotting.add_scalebar(ax, sizex=12.1, fontprops={'backgroundcolor':'red'})
        plt.title('background color')

        # export
        plt.tight_layout()
        figH.savefig('output-foreyes-test_plotting.pdf', format='pdf')


if __name__ == '__main__':
    unittest.main()
