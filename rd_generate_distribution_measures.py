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
from dataframe.parameters import scaling_metrics
from dataframe.func import split_df_by
from dataframe.utils import load_df
from plots.parameters import (average_parameters_dict, order_plot_dict,
                              bundle_dict_color_v1, bundle_dict_color_v10)
from plots.utils import (check_df_for_columns, check_agreement_with_dict,
                         save_figures_as)
from plots.scatter import interactive_distribution_plot


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV MRI data.')

    p.add_argument('--out_name', default='_measurement_distribution',
                   help='Output filename to save plot.')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')
    p.add_argument('--rbx_version', choices={'v1', 'v10'},
                   help='Rbx flow version to segment bundles.'
                        '[%(default)s]')
    p.add_argument('--use_stats',
                   help='Use to select a specific statistic. '
                        '[%(default)s]')
    p.add_argument('--specific_method',
                   help='String. Use to select a specific method. '
                        'Could be DTI, FW, NODDI, etc.')
    p.add_argument('--split_by',
                   help='Column name. Use to plot distribution on each unique'
                        ' argument in slected column. ')
    p.add_argument('--filter_missing', action='store_true',
                   help='Use to filter missing metrics when you reorder.')

    scatter = p.add_argument_group(title='Scatter plot options')
    scatter.add_argument('--plot_size', nargs=2, type=int,
                         metavar=('p_width', 'p_height'),
                         default=(1100, 800),
                         help='Width and Height of Scatter Plot. ')
    scatter.add_argument('--custom_order',
                         help='Use dictionary provided to set order of '
                         'metrics plot.')
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
    scatter.add_argument('--print_yaxis_range', action='store_true',
                         help='Use to check/update the y axis range. ')

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

    if args.use_stats:
        df = df.loc[df.Statistics == args.use_stats].reset_index(drop=True)
    if args.rbx_version:
         df = df[(df.rbx_version == args.rbx_version)].reset_index(drop=True)
    if args.specific_method:
        df = df[df['Method'] == args.specific_method].reset_index(drop=True)

    if args.custom_colors is not None:
        bundle_colors = args.custom_colors
    elif args.rbx_version == 'v10':
        bundle_colors = bundle_dict_color_v10
    else:
        bundle_colors = bundle_dict_color_v1

    # check Dataframe shape before plot
    check_df_for_columns(df, split_filter=args.split_by)
    df = check_agreement_with_dict(df, 'Bundles', bundle_colors,
                                   ignore_lenght=True,
                                   rm_missing=args.filter_missing)
    df = check_agreement_with_dict(df, 'Method', order_plot_dict,
                                   rm_missing=args.filter_missing,
                                   ignore_lenght=True)

    if args.split_by:
        multi_df, df_names = split_df_by(df, args.split_by)
        for frame, curr_method in zip(multi_df, df_names):
            curr_title = "Distribution of " + curr_method + " measurements"

            if args.custom_order and args.custom_y is not None:
                custom_order = args.custom_order[curr_method]
                custom_yaxis = args.custom_y
            elif args.use_data:
                custom_order = frame['Measures'].unique().tolist()
                custom_yaxis = False
            else:
                custom_order = order_plot_dict[curr_method]
                custom_yaxis = average_parameters_dict

            if args.apply_factor:
                for metric in custom_order:
                    if metric in scaling_metrics:
                        custom_yaxis[metric][1] *= args.apply_factor

            col_wrap = 0
            if len(frame['Measures'].unique()) > 2:
                col_wrap = len(frame['Measures'].unique().tolist()) / 2

            fig = interactive_distribution_plot(
                frame, "Bundles", "Value", "Bundles", colormap=bundle_colors,
                f_column="Measures", column_wrap=int(col_wrap),
                custom_order={"Measures": custom_order}, figtitle=curr_title,
                fig_width=args.plot_size[0], fig_height=args.plot_size[1],
                print_yaxis_range=args.print_yaxis_range,
                custom_y_range=custom_yaxis)

            outname = curr_method + args.out_name

            save_figures_as(fig, args.out_dir, outname,
                            save_as_png=args.save_as_png,
                            dpi_scale=args.dpi_scale,
                            heigth_value=args.plot_size[1],
                            width_value=args.plot_size[0])

    else:

        single_method = df['Method'].unique().tolist()[0]
        curr_title = "Distribution of " + single_method + " measurements"

        if args.custom_order and args.custom_y is not None:
            custom_order = args.custom_order
            custom_yaxis = args.custom_y
        elif args.use_data:
            custom_order = df['Measures'].unique().tolist()
            custom_yaxis = False
        else:
            custom_order = order_plot_dict[single_method]
            custom_yaxis = average_parameters_dict

        if args.apply_factor:
            for metric in custom_order:
                if metric in scaling_metrics:
                    custom_yaxis[metric][1] *= args.apply_factor

        col_wrap = 0
        if len(df['Measures'].unique()) > 2:
            col_wrap = len(df['Measures'].unique().tolist()) / 2

        fig = interactive_distribution_plot(
            df, "Bundles", "Value", "Bundles", colormap=bundle_colors,
            f_column="Measures", column_wrap=int(col_wrap),
            custom_order={"Measures": custom_order}, figtitle=curr_title,
            fig_width=args.plot_size[0], fig_height=args.plot_size[1],
            print_yaxis_range=args.print_yaxis_range, custom_y_range=custom_yaxis)

        outname = single_method + args.out_name

        save_figures_as(fig, args.out_dir, outname,
                    save_as_png=args.save_as_png, dpi_scale=args.dpi_scale,
                    heigth_value=args.plot_size[1],
                    width_value=args.plot_size[0])


if __name__ == '__main__':
    main()
