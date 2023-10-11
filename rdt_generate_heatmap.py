#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate Heatmap of the Pearson correlation coefficient across
all measure and bundles provide in CSV data.
CSV file could be the output of rdt_prepare_csv_for_figures.py

By default, script generate figure in html, add --save_as_png to save figure
in PNG format.

script qui ne genere qu'un seule heatmap, il faut fournir une dataframe
qui ne contient qu'une seule vague de donnee.
"""

import argparse

import os
import pandas as pd
import numpy as np

import plotly.graph_objs as go
import plotly.express as px

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from plot.utils import new_order_measure
from plot.heatmap import interactive_heatmap


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV diffusion data.')

    p.add_argument('--out_name',
                   help='Output filename to save heatmap.')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')
    p.add_argument('--reorder_measure',
                   help='Use to custom reorder measure for heatmap.\nBy '
                        'default measure are reordered as follow : \n'
                        'DTI, DTI-FW, HARDI, NODDI, MTI.')
    p.add_argument('--square_value', action='store_true',
                   help='Use to convert Pearson R to square Pearson r.')
    p.add_argument('--absolute_value',action='store_true',
                   help='Use to convert Pearson R to absolute Pearson r.')
    p.add_argument('--specific_stats',
                   help='Use to select a specific statistic.\nBy default '
                        'mean values are used.')
    p.add_argument('--use_as_slider', nargs=1,
                   help='Column name. Generates a heatmap for each unique'
                        ' argument corresponding to the column.')

    frames = p.add_argument_group(title='Dataframe options')
    frames.add_argument('--split_by_time', action='store_true',
                        help='Generate heatmap for each Session/Time. '
                             'By default merged all sessions')
    frames.add_argument('--split_by_method', action='store_true',
                        help='Generate heatmap for each Method (DTI, NODDI).')
    frames.add_argument('--split_by_bundle', action='store_true',
                        help='Generate heatmap for each bundle.')

    plot_opts = p.add_argument_group(title='Heatmap display options')
    plot_opts.add_argument('--z_range', nargs=2, type=float,
                           metavar=('z_min', 'z_max'), default=(0.3, 1),
                           help='Minimum and maximum values for colorbar. ')
    plot_opts.add_argument('--plot_size', nargs=2, type=int,
                           metavar=('p_width', 'p_height'),
                           default=(1080, 1080),
                           help='Width and Height of heatmap. ')
    plot_opts.add_argument('--colormap',
                           help='Color map applied on Heatmap. \n'
                                'By default YlGnBu is used.')
    plot_opts.add_argument('--title',
                           help='Main title of correlation heatmap.')

    plot_opts.add_argument('--save_as_png', action='store_true',
                           help='Save plot as png. Require kaleido.')


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

    if args.title is None:
        args.title = "Pearson correlation across measures and bundles"

    if args.specific_stats is None:
        args.specific_stats = 'mean'

    # Filter dataframe for figure
    df = pd.read_csv(args.in_csv)
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df = df[df['Statistics'] == args.specific_stats]
    df = df[~(df['Method'].isin(['Streamlines','Lesion']))]

    if args.reorder_measure is None:
        args.reorder_measure = new_order_measure

    # Create a list to reorder measure
    new_order = []
    for measure in args.reorder_measure:
        if len(args.reorder_measure) != len(df.Measures.unique().tolist()):
            if args.filter_measures:
                missing_metric = []
                for metric_item in df.Measures.unique():
                    if metric_item not in measure_dict:
                        missing_metric.append(metric_item)
                df.loc[~(df.Measures.isin(missing_metric))]
                print("The following metrics are removed.\n", missing_metric)
            else:
                print("The listed metrics don't match with the default "
                      "metrics list.\n Use --reorder_measure option to parse "
                      " a custom list or use --filter_measures.\n")

        for bundle in df['Bundles'].unique():
            reorder_measure = measure + '_' + bundle
            new_order.append(reorder_measure)

    # Generate merged column for pivot
    df['Measures_Bundles'] = df['Measures'] + '_' + df['Bundles']

    # Default colorbar title
    colorbar_title = 'Pearson r'

    # Generate Heatmap
    # Heatmap with slider
    if args.use_as_slider:
        corr_map = []
        for slider_arg in df[args.use_as_slider].unique():
            tmp = df.loc[df[args.use_as_slider] == slider_arg]
            corr_tmp = tmp.pivot(index=['Sid'], columns='Measures_Bundles',
                                 values='Value').reset_index().reindex(
                                                    columns=new_order).corr())

            if args.absolute_value:
                corr_tmp = np.absolute(corr_tmp)
                colorbar_title = 'Absolute Pearson r'

            if args.square_value:
                corr_tmp = np.square(corr_tmp)
                colorbar_title = 'Squared Pearson r'

            corr_map.append(corr_tmp)

        # Generate figure
        fig = interactive_heatmap_with_slider(corr_map,title=args.title,
                                  colbar_title=colorbar_title,
                                  colormap=px.colors.sequential.YlGnBu,
                                  y_label='Metrics by Bundles',
                                  z_min=args.z_range[0], z_max=args.z_range[1],
                                  tick_font_size=12, title_size=25, tick_angle=90,
                                  fig_width=args.plot_size[0],
                                  fig_height=args.plot_size[1])
        if args.out_name is None:
            args.out_name = 'correlation_heatmap_with_slider'

    else:
        # Heatmap without slider (i.e. averaged values)
        corr_map = df.pivot(index=['Sid'],
                            columns='Measures_Bundles',
                            values='Value'
                            ).reset_index().reindex(columns=new_order).corr()

        if args.absolute_value:
            corr_map = np.absolute(corr_map)
            colorbar_title = 'Absolute Pearson r'

        if args.square_value:
            corr_map = np.square(corr_map)
            colorbar_title = 'Squared Pearson r'

        # Generate figure
        fig = interactive_heatmap(corr_map, title=args.title,
                                  colbar_title=colorbar_title,
                                  colormap=px.colors.sequential.YlGnBu,
                                  y_label='Metrics by Bundles',
                                  z_min=args.z_range[0], z_max=args.z_range[1],
                                  tick_font_size=12, title_size=25, tick_angle=90,
                                  fig_width=args.plot_size[0],
                                  fig_height=args.plot_size[1])

        if args.out_name is None:
            args.out_name = 'correlation_heatmap'

    # Save figure
    if args.save_as_png:
        if args.use_as_slider:
            print("Be careful, with PNG you don't have access to the "
                  "slider option.\n")
        fig.write_image(os.path.join(args.out_dir, args.out_name + '.png'))
    else:
        fig.write_html(os.path.join(args.out_dir, args.out_name + '.html'))


if __name__ == '__main__':
    main()
