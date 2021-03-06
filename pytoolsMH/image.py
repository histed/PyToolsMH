from __future__ import print_function

"""Module with image-processing helper code

2017: we use mostly scikit-image, and tifffile for loading tiffs
"""

import skimage.io as io
from skimage import transform
from skimage import feature
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import tifffile

a_ = np.asarray
r_ = np.r_

def downscale_in_chunks(im, downscale_tuple=None, nfrchunk=1000, print_status=True):
    cL = []
    if print_status: print('downscaling frames... ', end='')
    for iC in range(int(np.ceil(im.shape[0]/nfrchunk))):
        maxfr = np.min((nfrchunk*(iC+1),im.shape[0]))
        cL.append(transform.downscale_local_mean(im[nfrchunk*iC:maxfr,:,:],
                                                 downscale_tuple))
        if print_status: print(maxfr, end=' ')
    if print_status: print('done.')
    return(np.concatenate(cL,axis=0))


def align_stack(im, alignNs=r_[0:100], print_status=True, do_plot=False):
    """Realign a stack to an image -- default to mean image from near the start

    Args:
        im
        alignNs: frameNs to average to give the alignment reference image
        print_status: give updates for long calcs to terminal
        do_plot: show a plot with alignment calculations

    Returns:
        aligned stack, same size as input stack, padded with zeros where shifted

    """
    
    # run alignment calculations, saving result in a dataframe
    aligntarg = im[:100,:,:].mean(axis=0)
    tL = []
    nfrdo = im.shape[0]
    if print_status: print('Computing offsets ({} frames)... '.format(nfrdo), end='')
    for iF in range(nfrdo):  
        tL.append(feature.register_translation(aligntarg, im[iF,:,:]))

    regDf = pd.DataFrame(tL, columns=('coords','err','phasediff'))
    regDf['row'] = [x[0][0] for x in tL]
    regDf['col'] = [x[0][1] for x in tL]

    if do_plot:
        gs = mpl.gridspec.GridSpec(2,2)
        fig = plt.figure()
        plt.subplot(gs[0,0])
        plt.plot(regDf.err)
        plt.title('translation-independent error')
        plt.ylabel('RMS error')
        plt.subplot(gs[0,1])
        plt.plot(regDf.col)
        plt.plot(regDf.row)
        plt.title('row and col pixel offsets')
        plt.legend(['col','row'])

    # do the shifts
    regim = im.copy()*0
    maxv = im.max()
    if print_status: print('Aligning frames... ', end='')
    for iF in range(nfrdo): #debug range(nframes):
        regim[iF,:,:] = transform.warp(im[iF,:,:]*1.0/maxv, \
                    transform.SimilarityTransform(translation=(-1*regDf.col[iF],-regDf.row[iF]))) * maxv
        t = transform.warp(im[iF,:,:]*1.0/maxv, \
                    transform.SimilarityTransform(translation=(-1*regDf.col[iF],-regDf.row[iF]))) * maxv
        if print_status and iF % 500 == 0:
            print('%d (%d,%d)'%(iF,-regDf.col[iF],-regDf.row[iF]), end=' ')
    if print_status: print('Done.')

    return regim




def write_tiff_stack(im, outname):
        """Write a 3d image into a tiff stack on disk
        Stack dims: [nFrames, nY, nX] """
        with tifffile.TiffWriter(outname, imagej=True) as stack:
            for iF in range(im.shape[0]):
                stack.save(im[iF,:,:], photometric='minisblack')


def tif_file_get_dims(fname):
    """"get dimensions of a tif file on disk
    Returns:
        shape: e.g. (nFr, nY, nX)

    After CaImAn code 180508 MH
    """
    with tifffile.TiffFile(fname) as tf:
        T = len(tf.pages)
        if T == 1:  # Fiji-generated TIF
            is_fiji = True
            T, d1, d2 = tf[0].shape
        else:
            d1, d2 = tf.pages[0].shape
    return (T,d1,d2)
