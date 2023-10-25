#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate Heatmap of the correlation across all measure and bundles.
CSV file could be the output of rdt_prepare_csv_for_figures.py
"""

import argparse

import os
import pandas as pd

from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.express as px

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from plots.utils import average_parameters, metric_colors


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV diffusion data.')

    p.add_argument('--out_name', default='Correlation_heatmap'
                   help='CSV diffusion data.')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')

    p.add_argument('--custom_order',
                   help='xx.')
    p.add_argument('--custom_yaxis',
                   help='xx.')
    p.add_argument('--use_data',
                   help='Use data to set plot parameters.')
    p.add_argument('--custom_colors',
                   help='Dictionary containing the bundle names and colors '
                        'associated in HEX format.')

    add_overwrite_arg(p)

    return p

def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    if args.out_name is None:
        args.out_name = 'Correlation_heatmap'

    if args.custom_colors is not None:
        metric_colors = args.custom_colors

    df = pd.read_csv(args.in_csv)

    # check lists
    if 'Section' not in df.columns.tolist():
        parser.error("The csv not contains a section column. "
                     "This script only deals with profile measurements.")

    if 'Method' not in df.columns.tolist():
        parser.error("The csv not contains Method column. Rename column or add it. ")

    if len(df['Method'].unique().tolist()) > 1:
        parser.error("Multiple method in csv files")

    if df['Method'].unique().tolist()[0] not in average_parameters:
        parser.error("Method does not exist in default parameter. "
                     "Please use --custom_order and --custom_yaxis options to provide specific informations.")

    for measure in df['Measures'].unique().tolist():
        if measure not in metric_colors:
            parser.error("No match colors is found for", measure, ".")
                         "Please use --custom_colors option to provide specific colors.")

    for bundle in df['Bundles'].unique():

        if args.out_name is None:
            args.out_name = bundle + '_measurement_profile'

        curr_title = 'Profile of '+ bundle + ' measures '
        curr_bundle = df[df['Bundles'] == bundle]
        col_wrap = len(curr_bundle['Method'].unique().tolist())

        fig=px.line(curr_bundle, x = "Section", y = "Mean", color = "Measures",
                    facet_col = "Method", facet_col_spacing = 0.09,
                    color_discrete_map = metric_colors, title = curr_title,
                    height = 400, width = 900, facet_col_wrap = col_wrap)

        fig.for_each_annotation(lambda anot: anot.update(text=anot.text.split("=")[-1]))
        fig.update_yaxes(matches = None, title = '', showticklabels = True,
                         visible = True)
        fig.update_xaxes(title = '', showticklabels = True, visible = True)
        fig.update_layout(title_x = 0.5, showlegend = False,
                          font = {'size' : 15}, title_font = dict(size = 25))
        fig.update_layout(yaxis3 = dict(range = [0,28]),
                          yaxis1 = dict(range = [0,0.7]),
                          yaxis4 = dict(range = [0,1.5]),
                          yaxis2 = dict(range = [0,2]))

    # Save figure
    save_figures_as(fig, args.out_dir, args.out_name, 
                    is_slider=args.use_as_slider,
                    save_as_png=args.save_as_png)


if __name__ == '__main__':
    main()
