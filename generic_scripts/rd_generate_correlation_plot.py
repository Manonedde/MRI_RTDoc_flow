#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates correlation plot with linear trend and menu.

Dataframe must be in WIDE format with one value per subject and column (not 
deal with longitudinal data). Subject id must be the first column.
By default, the script will generates all pair combination. 
To generate correlation plot on subset of columns use --use_columns 
options (2 columns minimum).

Input could be single data or contains multi data like as bundles.
In this case use --split_by option.

Columns : Subject_id, [Group_col,] metric1, metric2, ..., metricN

rd_generate_correlation_plot.py wide_data.csv 
rd_generate_correlation_plot.py wide_data.csv --split_by Bundles
"""

import argparse
import pandas as pd

from dataframe.func import split_df_by, pivot_to_wide
from dataframe.utils import load_df
from plots.utils import save_figures_as
from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from plots.scatter import multi_correlation_with_menu


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)
    p.add_argument('in_csv',
                   help='CSV data. Recommended output from prep_csv.py. ')

    p.add_argument('--split_by',
                   help='Column name. Generate heatmap for each unique '
                        'argument from the parse column. Outname is updates.')
    p.add_argument('--use_columns',
                   help='List to select specific columns.')
    p.add_argument('--out_name', default='correlation_plots',
                   help='Output filename to save heatmap. [%(default)s]')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')
    p.add_argument('--save_as_png', action='store_true',
                   help='Save plot as png. Require kaleido.')

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
    df = load_df(args.in_csv)

    if args.split_by:
        multi_df, df_names = split_df_by(df, args.split_by)
        for frame, curr_name in zip(multi_df, df_names):
            frame = frame.drop(args.split_by, axis=1)
            frame = frame.set_index(frame.columns.tolist()[0])
            fig = multi_correlation_with_menu(
                        frame, column_list=args.use_columns,
                        trend=args.trendtype, scope=args.trendscope,
                        colorline=args.trendline_color,
                        fig_width=args.plot_size[0],
                        fig_height=args.plot_size[1])

            outname = curr_name + '_' + args.out_name

            save_figures_as(fig, args.out_dir, outname,
                            save_as_png=args.save_as_png)
    else:
        df = df.set_index(df.columns.tolist()[0])
        fig = multi_correlation_with_menu(
                    df, column_list=args.use_columns,
                    trend=args.trendtype, scope=args.trendscope,
                    colorline=args.trendline_color,
                    fig_width=args.plot_size[0],
                    fig_height=args.plot_size[1])

        save_figures_as(fig, args.out_dir, args.out_name,
                        save_as_png=args.save_as_png)

if __name__ == '__main__':
    main()
