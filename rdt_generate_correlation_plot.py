#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to plot correlation plot with linear trend.
"""

import argparse
import pandas as pd

from dataframe.func import split_df_by, pivot_to_wide
from plots.utils import save_figures_as
from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from plots.scatter import multi_correlation_with_menu


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)
    p.add_argument('in_csv',
                   help='CSV data. Recommended output from prep_csv.py. ')

    p.add_argument('--out_name', default='correlation_plots',
                   help='Output filename to save heatmap. [%(default)s]')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')
    p.add_argument('--save_as_png', action='store_true',
                   help='Save plot as png. Require kaleido.')

    frames = p.add_argument_group(title='Dataframe options')
    frames.add_argument('--split_by', default='Bundles',
                        help='Column name. Generate heatmap for each unique '
                             'argument from the parse column')
    frames.add_argument('--rbx_version', default='v1', choices={'v1', 'v10'},
                        help='Rbx flow version to segment bundles.'
                        '[%(default)s]')
    frames.add_argument('--use_stats', default='mean',
                        help='Use to select a specific statistic. '
                             '[%(default)s]')
    frames.add_argument('--use_columns',
                        help='List to use to select a specific columns.')

    plot = p.add_argument_group(title='Scatter plot options')
    plot.add_argument('--plot_size', nargs=2, type=int,
                      metavar=('p_width', 'p_height'), default=(1000, 700),
                      help='Width and Height of heatmap. [%(default)s]')
    plot.add_argument('--trendtype', default='ols',
                      help='Method use to display data trend. '
                           '[%(default)s]')
    plot.add_argument('--trendscope', default='overall',
                      help='How the trendline is draw: by group or for'
                           'all data. [%(default)s]')
    plot.add_argument('--trendline_color', default='black',
                           help='Color of regression line. [%(default)s]')

    add_overwrite_arg(p)

    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    # Load Data frame
    df = pd.read_csv(args.in_csv)
    if 'Unnamed: 0' in df.columns.tolist():
        df.drop('Unnamed: 0', axis=1, inplace=True)
    df = df.loc[(df.Statistics == args.use_stats) &
                (df.rbx_version == args.rbx_version)].reset_index(drop=True)

    if args.split_by:
        multi_df, df_names = split_df_by(df, args.split_by)
        for frame, curr_name in zip(multi_df, df_names):
            frame = pivot_to_wide(frame, 'Sid', 'Measures', 'Value'
                                  longitudinal=args.longitudinal)
            frame = frame.set_index(frame.columns.tolist()[0])
            fig = multi_correlation_with_menu(
                        frame, column_list=args.use_columns,
                        trend=args.trendtype, scope=args.trendscope,
                        colorline=args.trendline_color,
                        fig_width=args.plot_size[0],
                        fig_height=args.plot_size[1])

            outname = curr_name + args.out_name

            save_figures_as(fig, args.out_dir, outname,
                            save_as_png=args.save_as_png)

if __name__ == '__main__':
    main()
