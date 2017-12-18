
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AuTomo example to generage sample previews.
"""

from __future__ import print_function

import six.moves.configparser as ConfigParser
import argparse
import os
import sys
from os.path import expanduser
import dxchange
import warnings
import numpy as np
from glob import glob
import re, shutil

import automo.util as util


def main(arg):

    parser = argparse.ArgumentParser()
    parser.add_argument("prefix", help="existing recon foldername")
    parser.add_argument("shift", help="shift between datasets",default='auto')
    parser.add_argument("new_folder",help="target folder",default='auto')
    args = parser.parse_args()

    home = expanduser("~")
    tomo = os.path.join(home, '.tomo/automo.ini')
    cf = ConfigParser.ConfigParser()
    cf.read(tomo)

    prefix = args.prefix

    if shift == 'auto':
        print (find_shit)
    else:
        shift = int(shift) #number of slices to keep 
    
    if new_folder == 'auto':
        new_folder = prefix + '_restack'

    folder_list = sorted(glob(prefix)

    for i, folder in enumerate(folder_list):
        file_list = glob(os.path.join(os.path.join(folder, 'recon', 'recon*.tiff')))
        file_list.sort()
        if i < len(folder_list) - 1:
            for j, f in enumerate(file_list[:shift]):
                shutil.copyfile(f, os.path.join('full_stack', 'recon_{:05d}.tiff'.format(j + shift * i)))
        else:
            for j, f in enumerate(file_list):
                shutil.copyfile(f, os.path.join('full_stack', 'recon_{:05d}.tiff'.format(j + shift * i)))

if __name__ == "__main__":
    main(sys.argv[1:])