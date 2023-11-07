#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate bundle profile.
"""

import argparse

import os
import pandas as pd

from dataframe.func import split_df_by
from dataframe.utils import load_df
from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from plots.parameters import dict_plot_profile, metric_colors
from plots.utils import (check_df_for_columns, check_agreement_with_dict,
                         save_figures_as)
from plots.line import interactive_lineplot

def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV MRI data.')
    p.add_argument('plot_args', nargs=3, metavar=('x', 'y', 'xlabel'), 
                   help='List of column name corresponding to x, y.')

    p.add_argument('--out_name', default='_profile',
                   help='Output filename to save plot.')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')

    frames = p.add_argument_group(title='Dataframe options')
    frames.add_argument('--plot_kwargs', default=dict(),
                        help='List of additional arguments for lineplot.')
    frames.add_argument('--split_by',
                        help='Column name. Generate heatmap for each unique '
                             'argument from the parse column')
    frames.add_argument('--use_as_slider',
                        help='Column name. Generates a heatmap for each unique'
                             ' argument corresponding to the column.')
    frames.add_argument('--use_stats', default='mean',
                        help='Use to select a specific statistic. '
                             '[%(default)s]')
    frames.add_argument('--rbx_version', default='v1', choices={'v1', 'v10'},
                        help='Rbx flow version to segment bundles.'
                        '[%(default)s]')
    frames.add_argument('--filter_missing', action='store_true',
                        help='Use to filter missing metrics when you reorder.')
    frames.add_argument('--longitudinal', action='store_true',
                        help='In case of longitudinal data, some plots option '
                             'require to group by using mean().')

    scatter = p.add_argument_group(title='Scatter plot options')
    scatter.add_argument('--plot_size', nargs=2, type=int,
                         metavar=('p_width', 'p_height'),
                         default=(1100, 800),
                         help='Width and Height of Scatter Plot. ')
    scatter.add_argument('--custom_y',
                         help='Use dictionary provided to set x and y axis '
                         'range by measures.')
    scatter.add_argument('--use_data', action='store_true',
                         help='Use data to set x and y axis range.')
    scatter.add_argument('--custom_colors',
                         help='Dictionary containing the bundle names and '
                         'colors associated in HEX format.')
    scatter.add_argument('--apply_factor', type=int,
                         help='Factor applied on MRI measure for plot. '
                              ' [%(default)s].')

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
    df = df.loc[(df.Statistics == args.use_stats) &
                (df.rbx_version == args.rbx_version)].reset_index(drop=True)

    if args.custom_colors is not None:
        metrics_colors = args.custom_colors
    else:
        metrics_colors = metric_colors

    if args.custom_y is not None:
        custom_yaxis = args.custom_y
    elif args.use_data:
        custom_yaxis = False
    else:
        custom_yaxis = dict_plot_profile

    # check Dataframe shape before plot
    check_df_for_columns(df, split_filter=args.split_by, profile=True)
    df = check_agreement_with_dict(df, 'Measures', metrics_colors,
                                   ignore_lenght=True, 
                                   rm_missing=args.filter_missing)
    
    if args.split_by:
        multi_df, df_names = split_df_by(df, args.split_by)
        for frame, curr_name in zip(multi_df, df_names):
            curr_title = "Profil of " + curr_name
            frame = frame.groupby([args.plot_args[0], args.use_as_slider,
                                   'Session','Measures']
                                   )[args.plot_args[1]].mean().reset_index()

            fig = interactive_lineplot(
                        frame, args.plot_args[0], args.plot_args[1],
                        color_col='Measures', frame=args.use_as_slider,
                        custom_y_dict=custom_yaxis, x_label=args.plot_args[2],
                        group = None, y_label=curr_name,
                        kwgs=dict(args.plot_kwargs),
                        colormap=metrics_colors, title=curr_title)

            # Save figure
            save_figures_as(fig, args.out_dir, 
                            curr_name + args.out_name + '.html',
                            is_slider=args.use_as_slider,
                            save_as_png=args.save_as_png)


if __name__ == '__main__':
    main()
