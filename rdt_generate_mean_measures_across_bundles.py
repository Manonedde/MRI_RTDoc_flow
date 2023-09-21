#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to plot distribution of data included in the input CSV.
CSV file could be the output of rdt_prepare_csv_for_figures.py
with --split_by_method option.

rdt_generate_mean_measures_across_bundles_plot.py dti.csv
"""

import argparse

import os
import pandas as pd

import plotly.graph_objs as go
import plotly.express as px

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist

from plot_utils import (average_parameters_dict, order_plot_dict,
                        bundle_dict_color_v1, bundle_dict_color_v10)
from plotly_func import interactive_scatter


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV MRI data.')

    p.add_argument('--out_name',
                   help='Output filename to save plot.')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')
    p.add_argument('--rbx_version', default='v1', choices={'v1', 'v10'},
                   help='Rbx flow version to segment bundles.'
                        '[%(default)s]')
    p.add_argument('--specific_stats', default='mean',
                   help='Use to select a specific statistic. '
                        '[%(default)s]')
    p.add_argument('--specific_method',
                   help='Use to select a specific method. ')

    scatter = p.add_argument_group(title='Scatter plot options')
    scatter.add_argument('--plot_size', nargs=2, type=int,
                         metavar=('p_width', 'p_height'),
                         default=(1100, 800),
                         help='Width and Height of Scatter Plot. ')
    scatter.add_argument('--custom_order',
                         help='Use dictionary provided to set order of metrics plot.')
    scatter.add_argument('--custom_yaxis',
                         help='Use dictionary provided to set x and y axis range by measures.')
    scatter.add_argument('--use_data',
                         help='Use data to set x and y axis range.')
    scatter.add_argument('--custom_colors',
                         help='Dictionary containing the bundle names and colors '
                              'associated in HEX format.')
    scatter.add_argument('--apply_factor', action='store_true',
                         help='Use if you apply factor on some metrics. ')
    scatter.add_argument('--print_yaxis_range', action='store_true',
                         help='Use to check/update the y axis range. ')

    scatter.add_argument('--save_as', default='html', choices={'html', 'png'},
                         help='Save plot as png. Require kaleido. [%(default)s]')
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

    df = pd.read_csv(args.in_csv)
    df.drop('Unnamed: 0', axis=1, inplace=True)

    df = df[df['Statistics'] == args.specific_stats]

    if args.specific_method is not None:
        df = df[df['Method'] == args.specific_method]

    df = df.reset_index(drop=True)

    # check lists
    if 'Section' in df.columns.tolist():
        parser.error('The csv contains a section column.\n'
                     'This script only deals with average measurements.')

    if 'Method' not in df.columns.tolist():
        print("The csv not contains Method column. \nRename column or add it. ")

    if len(df['Method'].unique().tolist()) > 1 and args.specific_method is None:
        parser.error('Multiple method categories are found in csv files.\n '
                     'Please provide a csv file containing single Method or '
                     'use --specific_method options.')

    if len(df['Statistics'].unique().tolist()) > 1:
        parser.error('Multiple statistics are found in csv files.\n '
                     'Please provide a csv file containing single Statistic or '
                     'use --specific_stats options.')

    if df['Method'].unique().tolist()[0] not in order_plot_dict:
        if args.use_data is None:
            parser.error('Method does not exist in default parameter.\n '
                         'Please use --use_data option or use --custom_order\n'
                         'and --custom_yaxis options to provide specific'
                         ' informations.')

    if args.custom_colors is not None:
        bundle_colors = args.custom_colors
    elif args.rbx_version == 'v10':
        bundle_colors = bundle_dict_color_v10
    else:
        bundle_colors = bundle_dict_color_v1

    for bundle in df['Bundles'].unique().tolist():
        if bundle not in bundle_colors:
            parser.error("No match colors is found for ", bundle, "."
                         "\nPlease use --custom_colors option to provide "
                         "specific colors.")

    curr_method = df['Method'].unique().tolist()[0]
    curr_title = "Distribution of " + curr_method + " measurements"

    if args.out_name is None:
        args.out_name = curr_method + '_measurement_distribution'

    if args.custom_order and args.custom_yaxis is not None:
        custom_order = args.custom_order
        custom_yaxis = args.custom_yaxis
    elif args.use_data is not None:
        custom_order = df['Measures'].unique().tolist()
    else:
        custom_order = order_plot_dict[curr_method]
        custom_yaxis = average_parameters_dict

    if args.apply_factor:
        custom_yaxis[1][1] = custom_yaxis[1][1] * 10

    col_wrap = len(df['Measures'].unique().tolist()) / 2

    fig = interactive_scatter(df, "Bundles", "Value", "Bundles",
                              colormap=bundle_colors, f_column="Measures",
                              column_wrap=int(col_wrap), title_size=25,
                              custom_order={"Measures": custom_order},
                              figtitle=curr_title, fig_width=args.plot_size[0],
                              fig_height=args.plot_size[1])

    if args.use_data is None:
        y_axis_name = []
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                y_axis_name.append(axis)

        for idx, yname in enumerate(y_axis_name):
            curr_key = fig.layout.annotations[idx].text
            fig.layout[yname].range = custom_yaxis[curr_key]

    if args.print_yaxis_range:
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                print(axis, fig.layout[axis].range)

    if args.save_as == 'png':
        fig.write_image(os.path.join(args.out_dir, args.out_name + '.png'),
                        scale=args.dpi_scale, height=args.plot_size[1],
                        width=args.plot_size[0])
    else:
        fig.write_html(os.path.join(args.out_dir, args.out_name + '.html'))


if __name__ == '__main__':
    main()
