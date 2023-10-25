#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate a GIF from MRI images (--in_mri) or list of png (--in_png).

For MRI images, any 3D image can be used.The GIF is built along the z axis,
by default the first 4 slice of z and the last 5 are ignored.
To change this setting, use the --z_range option.

generate_gif.py --in_mri fa.nii.gz
generate_gif.py --in_png ./AF (path containing multiple PNGs)

Note :
This script can also be used to create the png for each slice
(use --keep_tmp_files) and use convert (Imagemagick) to generate the gif with
similar options:
-delay image_per_second -loop 0/1 -layers optimize -resize image_size
-interpolate method

Examples :
    convert -delay 20 -loop 0 `ls -v` your_gif.gif
    convert -delay 20 -loop 0 *png -resize 768x576 your_gif.gif

"""

import argparse
import glob
import os
import shutil

import imageio
import matplotlib
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import scipy.ndimage as ndimage

from scilpy.io.utils import (add_overwrite_arg,
                             assert_output_dirs_exist_and_empty)
from scilpy.utils.filenames import split_name_with_nii


def _build_arg_p():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawTextHelpFormatter)

    im_type = p.add_mutually_exclusive_group(required=True)
    im_type.add_argument('--in_mri',
                         help='Single MRI image.')
    im_type.add_argument('--in_png',
                         help='Path to PNG images.')

    p.add_argument('--out_dir',
                   help='Output directory to save GIF.')
    p.add_argument('--out_prefix',
                   help='Prefix used to generate GIF png images. ')

    gif_opts = p.add_argument_group(title='GIF options')
    gif_opts.add_argument('--delay', type=int, default=20,
                          help='Number of png images per second. '
                               '[%(default)s]')
    gif_opts.add_argument('--loop', type=int, default=0,
                          help='Use to stop the GIF after the last frame '
                               '(put 1). [%(default)s]')

    plot_mri = p.add_argument_group(title='Generate PNG from MRI options')
    plot_mri.add_argument('--z_range', nargs=2, type=int,
                          metavar=('Min', 'Max'),
                          help='Minimum and maximum z-axis values used to '
                               'create the GIF. ')
    plot_mri.add_argument('--color_map', default='gray',
                          choices={'gray', 'jet'},
                          help='Specify colormap use for GIF. [%(default)s]')
    plot_mri.add_argument('--dpi', type=int, default=200,
                          help='Use to set the dpi resolution of png images.'
                               ' [%(default)s]')
    plot_mri.add_argument('--keep_tmp_files', action='store_true',
                          help='By default, the png images for each slice are '
                               'not preserved. Use this option to save png '
                               'images. ')

    add_overwrite_arg(p)

    return p


def generate_individual_image_plot(data, map_prefix, slices_order,
                                   colmap, out_dir):
    for slice_z in slices_order:
        fig, ax = plt.subplots(1, 1)
        image = ax.imshow(ndimage.rotate(data[:, :, slice_z], -90),
                          cmap=colmap, origin='lower')
        ax.axis('off')
        ax.set_facecolor('k')
        out_name = map_prefix + '_slice_' + str(slice_z) + '.png'
        plt.savefig(os.path.join(out_dir, out_name), facecolor='k',
                    dpi=200, bbox_inches='tight')
        plt.close()


def custom_color_for_nii(colors, range=200):
    colors1 = plt.cm.inferno(np.linspace(0, 0.05, 1))
    colors2 = colors(np.linspace(0.1, 1, range))
    stack_colmap = np.vstack((colors1, colors2))
    return matplotlib.colors.LinearSegmentedColormap.from_list('my_colormap',
                                                               stack_colmap)


def main():
    p = _build_arg_p()
    args = p.parse_args()

    if args.out_dir is None:
        args.out_dir = './'

    if args.in_png:
        png_list = glob.glob(os.path.join(args.in_png + '/*png'))
        png_list.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))

        if args.out_prefix is None:
            args.out_prefix = (os.path.splitext(
                os.path.basename(png_list[0]))[0])

        frames = []
        for curr_png in png_list:
            frames.append(imageio.imread(curr_png))

    if args.in_mri:
        assert_output_dirs_exist_and_empty(p, args,
                                           os.path.join(args.out_dir, 'tmp'),
                                           create_dir=True)

        if args.out_prefix is None:
            args.out_prefix = split_name_with_nii(
                os.path.basename(args.in_mri))[0]

        img_data = nib.load(args.in_mri).get_fdata(dtype=np.float32)

        if args.z_range is not None:
            z_min = args.z_range[0]
            z_max = args.z_range[1]
        else:
            z_min = 4
            z_max = img_data.shape[2] - 5

        if args.color_map == 'jet':
            use_color = plt.cm.jet
        else:
            use_color = plt.cm.gray

        z_slices = np.linspace(z_min, z_max, num=z_max-z_min).astype(int)
        generate_individual_image_plot(img_data, args.out_prefix, z_slices,
                                       custom_color_for_nii(use_color),
                                       os.path.join(args.out_dir, 'tmp'))

        frames = []
        for z in z_slices:
            image_name = args.out_prefix + '_slice_' + str(z) + '.png'
            frames.append(imageio.imread(os.path.join(
                                         args.out_dir, 'tmp', image_name)))

        if not args.keep_tmp_files:
            shutil.rmtree(os.path.join(args.out_dir, 'tmp'),
                          ignore_errors=False, onerror=None)

    # Save Gif
    imageio.mimsave(os.path.join(args.out_dir, args.out_prefix + '.gif'),
                    frames, fps=args.delay, loop=args.loop)


if __name__ == "__main__":
    main()
