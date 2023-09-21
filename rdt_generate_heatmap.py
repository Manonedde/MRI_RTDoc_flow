#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate Heatmap of the Pearson correlation coefficient across
all measure and bundles provide in CSV data.
CSV file could be the output of rdt_prepare_csv_for_figures.py

By default, script generate figure in html, add --save_as_png to save figure
in PNG format.
"""

import argparse

import os
import pandas as pd
import numpy as np

import plotly.graph_objs as go
import plotly.express as px

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from utils import new_order_measure


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV diffusion data.')

    p.add_argument('--out_name', default='Correlation_heatmap',
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

    if args.out_name is None:
        args.out_name = 'correlation_heatmap'

    if args.colormap is None:
        args.colormap = px.colors.sequential.YlGnBu

    if args.title is None:
        args.title = "Pearson correlation across measures and bundles"

    if args.specific_stats is None:
        args.specific_stats = 'mean'

    df = pd.read_csv(args.in_csv)
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df = df[df['Statistics'] == args.specific_stats]
    df = df[~(df['Method'] == 'Streamlines')]

    if args.reorder_measure is None:
        args.reorder_measure = new_order_measure

    new_order = []
    for measure in args.reorder_measure:
        if len(args.reorder_measure) != len(df.Measures.unique().tolist()):
            print("The listed metrics don't match with the default "
                  "metrics list.\n Use --reorder_measure option to parse "
                  " a custom list.\n")
        for bundle in df['Bundles'].unique():
            reorder_measure = measure + '_' + bundle
            new_order.append(reorder_measure)

    df['Measures_Bundles'] = df['Measures'] + '_' + df['Bundles']
    df = df.pivot(index=['Sid'], columns='Measures_Bundles',
                  values='Value').reset_index()
    df = df.reindex(columns=new_order)

    corr_map = df.corr()

    colorbar_title = 'Pearson r'

    if args.absolute_value:
        corr_map = np.absolute(corr_map)
        colorbar_title = 'Absolute Pearson r'

    if args.square_value:
        corr_map = np.square(corr_map)
        colorbar_title = 'Squared Pearson r'

    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=corr_map.values, x=corr_map.columns,
                             y=corr_map.index,
                             colorscale=args.colormap,
                             colorbar=dict(title=colorbar_title),
                             zmin=args.z_range[0], zmax=args.z_range[1]))
    # fig.update_xaxes(side = "top")
    fig.update_layout(go.Layout(width=args.plot_size[0],
                                height=args.plot_size[1],
                                title=args.title, title_x=0.5,
                                font={'size': 12},
                                title_font=dict(size=25),
                                yaxis=dict(visible=True,
                                           autorange='reversed')))

    if args.save_as_png:
        fig.write_image(os.path.join(args.out_dir, args.out_name + '.png'))
    else:
        fig.write_html(os.path.join(args.out_dir, args.out_name + '.html'))


if __name__ == '__main__':
    main()
