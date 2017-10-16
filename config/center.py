#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TomoPy example script to reconstruct tomography data with different center.

"""

from __future__ import print_function

import ConfigParser
import argparse
import os
import sys
import re
from os.path import expanduser

import h5py
import dxchange
import tomopy
import numpy as np

import automo.util as util


def main(arg):

    parser = argparse.ArgumentParser()
    parser.add_argument("file_name", help="existing hdf5 file name")
    parser.add_argument("rot_start", help="rotation axis start location")
    parser.add_argument("rot_end", help="rotation axis end location")
    parser.add_argument("rot_step", help="rotation axis end location")
    parser.add_argument("slice_start", help="a single slice to run center.py. Put -1 for n_slice if supplied")
    parser.add_argument("n_slice", help="number of slices. Put -1 for slice_start if supplied")
    parser.add_argument("medfilt_size", help="size of median filter")
    parser.add_argument("level", help="level of downsampling")
    args = parser.parse_args()

    home = expanduser("~")
    tomo = os.path.join(home, '.tomo/automo.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(tomo)

    fname = args.file_name
    rot_start = int(args.rot_start)
    rot_end = int(args.rot_end)
    rot_step = int(args.rot_step)
    slice = int(args.slice_start)
    n_slice = int(args.n_slice)
    medfilt_size = int(args.medfilt_size)
    level = float(args.level)

    array_dims = util.read_data_adaptive(fname, shape_only=True)

    if slice == -1:
        sino_start = 0
        sino_end = array_dims[1]-1
        sino_step = int((sino_end - sino_start)) / n_slice + 1
    else:
        sino_start = slice
        sino_end = slice + 1
        sino_step = 1


    # Select the rotation center range.
    if (rot_start < 0) or (rot_end > array_dims[2]):
        rot_center = array_dims[2]/2
        rot_start = rot_center - 30
        rot_end = rot_center + 30

    if (rot_step < 0) or (rot_step > (rot_end - rot_start)):
        rot_step = 1
    center_range=[rot_start, rot_end, rot_step]
    print ("Center:", center_range)

    # Select the sinogram range to reconstruct.
    if (sino_start < 0) or (sino_start > array_dims[1]):
        sino_start = array_dims[1]/2

    folder = os.path.dirname(fname) + os.sep
    try:
        N_recon = rot_start - rot_end

        prj, flat, dark = util.read_data_adaptive(fname, sino=(sino_start, sino_end, sino_step))

        # Read theta from the dataset:
        theta = tomopy.angles(prj.shape[0])

        print('## Debug: after reading data:')
        print('\n** Shape of the data:'+str(np.shape(prj)))
        print('** Shape of theta:'+str(np.shape(theta)))
        print('\n** Min and max val in prj before recon: %0.5f, %0.3f'  % (np.min(prj), np.max(prj)))

        prj = tomopy.normalize(prj, flat, dark)
        print('\n** Flat field correction done!\n')

        print('## Debug: after normalization:')
        print('\n** Min and max val in prj before recon: %0.5f, %0.3f'  % (np.min(prj), np.max(prj)))

        prj = tomopy.minus_log(prj)
        print('\n** minus log applied!')

        print('## Debug: after minus log:')
        print('\n** Min and max val in prj before recon: %0.5f, %0.3f'  % (np.min(prj), np.max(prj)))

        prj = tomopy.misc.corr.remove_neg(prj, val=0.001)
        prj = tomopy.misc.corr.remove_nan(prj, val=0.001)
        prj[np.where(prj == np.inf)] = 0.001

        print('## Debug: after cleaning bad values:')
        print('\n** Min and max val in prj before recon: %0.5f, %0.3f'  % (np.min(prj), np.max(prj)))

        prj = tomopy.remove_stripe_ti(prj,4)
        print('\n** Stripe removal done!')
        print('## Debug: after remove_stripe:')
        print('\n** Min and max val in prj before recon: %0.5f, %0.3f' % (np.min(prj), np.max(prj)))

        prj = tomopy.median_filter(prj,size=medfilt_size)
        print('\n** Median filter done!')
        print('## Debug: after nedian filter:')
        print('\n** Min and max val in prj before recon: %0.5f, %0.3f' % (np.min(prj), np.max(prj)))


        if level>0:
            prj = tomopy.downsample(prj, level=level)
            print('\n** Down sampling done!\n')
            print('## Debug: after down sampling:')
            print('\n** Min and max val in prj before recon: %0.5f, %0.3f' % (np.min(prj), np.max(prj)))

        slice_ls = range(sino_start, sino_end, sino_step)
        center_ls = []
        for i in slice_ls:
            outpath = os.path.join(os.getcwd(), 'center', str(i))
            tomopy.write_center(prj, theta, dpath=outpath,
                                cen_range=[rot_start/pow(2,level), rot_end/pow(2, level),
                                           rot_step/pow(2, level)])
            min_entropy_fname = util.minimum_entropy(outpath, mask_ratio=0.7, ring_removal=True)
            center_ls.append(float(re.findall('\d+\.\d+', os.path.basename(min_entropy_fname))[0]))
        if len(center_ls) == 1:
            center_pos = center_ls[0]
        else:
            center_pos = np.mean(util.most_neighbor_clustering(center_ls, 5))
        f = open('center_pos.txt', 'w')
        f.write(str(center_pos))
        f.close()
        print("#################################")

    except:
        print(folder, 'does not contain the expected file hdf5 file')
        pass




if __name__ == "__main__":
    main(sys.argv[1:])
