#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to plot distribution of data included in the input CSV.
CSV file must be the output of rdt_prepare_csv*.py
with --split_by_method option if you're not filter your dataframe.

By default, MRI measurement ranges are defined in the parameter file. 
Use the --apply_factor option if you have applied a factor to individual 
measurements, to adapt the ranges from the parameter file.

rdt_generate_mean_measures_across_bundles_plot.py dti.csv
"""

import argparse
import pandas as pd

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from dataframe.func import split_df_by
from dataframe.utils import load_df
from plots.utils import save_figures_as
from plots.scatter import interactive_distribution_plot


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV MRI data.')
    p.add_argument('x',
                   help='Column name corresponding to x-axis.')
    p.add_argument('y',
                   help='Column name corresponding to y-axis.')
    p.add_argument('colors',
                   help='Column name use to code for colors.')
    
    p.add_argument('--out_name', default='_distribution',
                   help='Output filename to save plot.')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')
    p.add_argument('--split_by',
                   help='Column name. Use to plot distribution on each unique'
                        ' argument in column. ')


    scatter = p.add_argument_group(title='Scatter plot options')
    scatter.add_argument('--split_plot',
                         help='Column name use to split plot into multi facet. ')
    scatter.add_argument('--plot_size', nargs=2, type=int,
                         metavar=('p_width', 'p_height'),
                         default=(1100, 800),
                         help='Width and Height of Scatter Plot. ')
    scatter.add_argument('--title',
                         help='Plot title. ')
    scatter.add_argument('--custom_order',
                         help='Use dictionary provided to set order of '
                         'metrics plot.')
    scatter.add_argument('--yrange',
                         help='Use dictionary provided to set x and y axis '
                         'range by measures.')
    scatter.add_argument('--custom_colors',
                         help='Dictionary containing the bundle names and '
                         'colors associated in HEX format.')

    scatter.add_argument('--save_as_png', action='store_true',
                         help='Save plot as png. Require kaleido.')
    scatter.add_argument('--dpi_scale', type=int, default=6,
                         help='Use to increase (>1) or decrease (<1) the '
                              ' image resolution. [%(default)s]')
    add_overwrite_arg(p)

    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    # Load and filter Dataframe
    df = load_df(args.in_csv)

    if args.split_by:
        multi_df, df_names = split_df_by(df, args.split_by)
        for frame, sub_name in zip(multi_df, df_names):
            curr_title = args.title + ' :' + sub_name

            if args.custom_order and args.yrange is not None:
                custom_order = args.custom_order
                custom_yaxis = args.yrange

            col_wrap = 0
            if args.split_plot:
                if len(frame[args.split_plot].unique()) > 2:
                    col_wrap = len(frame[args.split_plot].unique().tolist()) / 2

            fig = interactive_distribution_plot(
                frame, "Bundles", "Value", "Bundles", colormap=args.custom_colors,
                f_column="Measures", column_wrap=int(col_wrap),
                custom_order={"Measures": custom_order}, figtitle=curr_title,
                fig_width=args.plot_size[0], fig_height=args.plot_size[1],
                custom_y_range=custom_yaxis)

            outname = sub_name + '_' + args.out_name

            save_figures_as(fig, args.out_dir, outname,
                            save_as_png=args.save_as_png,
                            dpi_scale=args.dpi_scale,
                            heigth_value=args.plot_size[1],
                            width_value=args.plot_size[0])

    else:

        if args.custom_order and args.yrange is not None:
            custom_order = args.custom_order
            custom_yaxis = args.yrange

        col_wrap = 0
        if args.split_plot:
            if len(frame[args.split_plot].unique()) > 2:
                col_wrap = len(frame[args.split_plot].unique().tolist()) / 2

        fig = interactive_distribution_plot(
            frame, "Bundles", "Value", "Bundles", colormap=args.custom_colors,
            f_column="Measures", column_wrap=int(col_wrap),
            custom_order={"Measures": custom_order}, figtitle=args.title,
            fig_width=args.plot_size[0], fig_height=args.plot_size[1],
            custom_y_range=custom_yaxis)

        save_figures_as(fig, args.out_dir, args.out_name,
                    save_as_png=args.save_as_png, dpi_scale=args.dpi_scale,
                    heigth_value=args.plot_size[1],
                    width_value=args.plot_size[0])


if __name__ == '__main__':
    main()
