#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate an interactive visualization of MRI images.
It's best to crop the images first.


List of available colors: Blackbody, Bluered, Blues, Vividis, Earth, Electric,
                          Greens, Hot, Jet, Picnic, Rainbow, RdBu, Reds,
                          Viridis, YlGnBu, YlOrRd.

"""

import argparse
import os

import nibabel as nib
import numpy as np

from plots.parameters import colormap_3d_volume
from plots.utils import save_figures_as
from plots.three_dimension import generate_3d_volume
from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from scilpy.utils.filenames import split_name_with_nii

import matplotlib.cm as cm

def _build_arg_parser():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawTextHelpFormatter)

    p.add_argument('in_image',
                   help='Brain MRI image.')

    p.add_argument('--out_html',
                   help='Output html filename.')
    p.add_argument('--out_dir',
                   help='Output directory to save html page.')

    visu = p.add_argument_group(title='visualization options')
    visu.add_argument('--title', default='Brain MRI',
                      help='Use the provided info for the histogram title.'
                           ' [%(default)s]')
    visu.add_argument('--first_z_slice', type=int, default=1,
                      help='Defines the first frame used to display the image.'
                           ' [%(default)s]')
    visu.add_argument('--colorname', default='Greys',
                      help='Use to display brain maps according to a '
                           'specific colorname using the list of possible '
                           'colornames provided. Must be compatible with the'
                           'surfaces. [%(default)s]')
    visu.add_argument('--add_buttons', action='store_true',
                      help='Add two buttons play and stop to the scroll bar. ')
    visu.add_argument('--display_scale', action='store_true',
                      help='Add two buttons play and stop to the scroll bar. ')

    p.add_argument('--show_only', action='store_true',
                   help='Do not save the figure, only display.')

    add_overwrite_arg(p)

    return p


def main():
    p = _build_arg_parser()
    args = p.parse_args()

    assert_inputs_exist(p, args.in_image)

    if args.out_dir is None:
        args.out_dir = './'

    if args.out_html is None:
        args.out_html = split_name_with_nii(os.path.basename(args.in_image))[0]

    # load image
    data = nib.load(args.in_image).get_fdata().T

    # Define parameters for grid
    x_size, y_size = data[0].shape
    z_slices = data.shape[0]
    rescale_z_max = (data.shape[0]-1) / 10
    all_grid_step = np.linspace(0, rescale_z_max, z_slices)
    z_step = all_grid_step[1] - all_grid_step[0]

    fig = generate_3d_volume(data, rescale_z_max, z_slices, z_step, x_size,
                             y_size, args.colorname, title=args.title,
                             prefix_slider='z slice', start_at=7,
                             add_buttons=args.add_buttons,
                             show_scale=args.display_scale)

    # Show or save html page
    if args.show_only:
        fig.show()
    else:
        save_figures_as(fig, args.out_dir, args.out_html)


if __name__ == "__main__":
    main()
