#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate Heatmap of the Pearson correlation coefficient across
all measure and bundles provide in CSV data.
CSV file could be the output of rdt_prepare_csv_scil.py

By default, script generate figure in html, add --save_as_png to save figure
in PNG format.

Warning : Require kaleido to save in png.
"""

import argparse

import pandas as pd
import plotly.express as px

from dataframe.func import get_multi_corr_map, get_corr_map
from dataframe.utils import get_row_name_from_col, check_reorder_measure
from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from plots.parameters import new_order_measure
from plots.utils import save_figures_as, generate_reorder_list
from plots.heatmap import interactive_heatmap, interactive_heatmap_with_slider


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV data. Recommended output from prep_csv.py. ')

    p.add_argument('--out_name', default='correlation_heatmap',
                   help='Output filename to save heatmap. [%(default)s]')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')
    p.add_argument('--save_as_png', action='store_true',
                   help='Save plot as png. Require kaleido.')

    frames = p.add_argument_group(title='Dataframe options')
    frames.add_argument('--split_by',
                        help='Column name. Generate heatmap for each unique '
                             'argument from the parse column')
    frames.add_argument('--use_as_slider',
                        help='Column name. Generates a heatmap for each unique'
                             ' argument corresponding to the column.')
    frames.add_argument('--use_stats', default='mean',
                        help='Use to select a specific statistic. '
                             '[%(default)s]')
    frames.add_argument('--custom_reorder',
                        help='List. Use to custom reorder measure for heatmap.'
                             '\nRequire --reorder_measure option.')
    frames.add_argument('--reorder_measure', action='store_true',
                        help='Use to reorder measure for heatmap.\nBy '
                             'default measure are reordered as follow : \n'
                             'DTI, DTI-FW, HARDI, NODDI, MTI.')
    frames.add_argument('--filter_measures', action='store_true',
                        help='Use to filter missing metrics when you reorder.')
    frames.add_argument('--apply_on_pearson',
                        choices=['None', 'square', 'absolute'],
                        default="None",
                        help="Use to convert Pearson r to square or absolute "
                             "Pearson r. [%(default)s].\n "
                             " (square) Apply square on Pearson r. \n"
                             " (absolute) Apply an absolute on Pearson r.\n")
    frames.add_argument('--longitudinal', action='store_true',
                        help='In case of longitudinal data, some plots option '
                             'require to group by using mean().')

    plot_opts = p.add_argument_group(title='Heatmap display options')
    plot_opts.add_argument('--r_range', nargs=2, type=float,
                           metavar=('r_min', 'r_max'), default=(0.3, 1),
                           help='Minimum and maximum values for colorbar. '
                                '[%(default)s]')
    plot_opts.add_argument('--plot_size', nargs=2, type=int,
                           metavar=('p_width', 'p_height'),
                           default=(900, 900),
                           help='Width and Height of heatmap. [%(default)s]')
    plot_opts.add_argument('--colormap',
                           help='Color map applied on Heatmap. \n'
                                'By default YlGnBu is used.')
    plot_opts.add_argument('--title', default="Pearson correlation",
                           help='Main title of correlation heatmap.'
                                '[%(default)s]')
    plot_opts.add_argument('--xlabel', default='',
                           help='X axis title of correlation heatmap. '
                                '[%(default)s]')
    plot_opts.add_argument('--ylabel', default='Metrics by Bundles',
                           help='Y axis title of correlation heatmap. '
                                '[%(default)s]')

    add_overwrite_arg(p)

    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    if args.colormap is None:
        args.colormap = px.colors.sequential.YlGnBu

    # Load and Filter dataframe for figure
    df = pd.read_csv(args.in_csv)

    if 'Unnamed: 0' in df.columns.tolist():
        df.drop('Unnamed: 0', axis=1, inplace=True)
    df = df[df['Statistics'] == args.use_stats]

    if args.custom_reorder is not None:
        reorder_metrics = args.custom_reorder
    else:
        reorder_metrics = new_order_measure

    if args.reorder_measure:
        df = check_reorder_measure(df, 'Measures', reorder_metrics,
                                   rm_missing_metrics=args.filter_measures)
        # Create a list to reorder measure
        new_order = generate_reorder_list(df, reorder_metrics, 'Bundles')
    else:
        new_order = False

    # Generate merged column for pivot
    df['Measures_Bundles'] = df['Measures'] + '_' + df['Bundles']

    # Generate Heatmap
    if args.split_by:
        split_arg_names = get_row_name_from_col(df, args.split_by)
        corr_map, colorbar_title = (get_multi_corr_map(
            df, args.split_by, 'Sid', 'Measures_Bundles', 'Value',
            reorder_col=new_order, longitudinal=args.longitudinal,
            post_pearson=args.apply_on_pearson))

        for corr_name, corr in zip(split_arg_names, corr_map):
            if args.ylabel is None:
                args.ylabel = 'Metrics of ' + args.split_by + ' ' + str(
                    corr_name)
            fig = interactive_heatmap(
                corr, title=args.title, title_size=25, tick_angle=90,
                colbar_title=colorbar_title, tick_font_size=12,
                colormap=px.colors.sequential.YlGnBu,
                r_min=args.r_range[0], r_max=args.r_range[1],
                y_label=args.ylabel, fig_width=args.plot_size[0],
                fig_height=args.plot_size[1])

            # Save figure
            outname = args.out_name + '_' + args.split_by + '_' + str(
                corr_name)
            save_figures_as(fig, args.out_dir, outname,
                            is_slider=args.use_as_slider,
                            save_as_png=args.save_as_png)

    # Heatmap with slider
    if args.use_as_slider:
        corr_map, colorbar_title = get_multi_corr_map(
            df, args.use_as_slider, 'Sid',
            'Measures_Bundles', 'Value',
            reorder_col=new_order,
            post_pearson=args.apply_on_pearson,
            longitudinal=args.longitudinal)

        # Generate figure
        fig = interactive_heatmap_with_slider(
            corr_map, title=args.title, colbar_title=colorbar_title,
            colormap=px.colors.sequential.YlGnBu, tick_angle=90,
            y_label=args.ylabel, tick_font_size=12, title_size=25,
            r_min=args.r_range[0], r_max=args.r_range[1],
            fig_width=args.plot_size[0],
            fig_height=args.plot_size[1])

        args.out_name = args.out_name + '_with_slider'

    else:
        # Heatmap without slider (i.e. averaged values)
        corr_map, colorbar_title = get_corr_map(
            df, 'Sid', 'Measures_Bundles', 'Value',
            reorder_col=new_order,
            post_pearson=args.apply_on_pearson)
        # Generate figure
        fig = interactive_heatmap(
            corr_map, title=args.title, title_size=25, tick_angle=90,
            colbar_title=colorbar_title, colormap=px.colors.sequential.YlGnBu,
            x_label=args.xlabel, y_label=args.ylabel, r_min=args.r_range[0],
            r_max=args.r_range[1], tick_font_size=12,
            fig_width=args.plot_size[0], fig_height=args.plot_size[1])

    # Save figure
    if args.split_by is not None:
        pass
    else:
        save_figures_as(fig, args.out_dir, args.out_name,
                        is_slider=args.use_as_slider,
                        save_as_png=args.save_as_png)


if __name__ == '__main__':
    main()
