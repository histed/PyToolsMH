"""Module with image-processing helper code

2017: we use mostly scikit-image, and tifffile for loading tiffs
"""

import skimage.io as io
from skimage import transform
import numpy as np

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
        
