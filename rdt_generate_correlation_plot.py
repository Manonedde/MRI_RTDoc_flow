#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to identify each lesion with individual label.
"""

import argparse
import os
import pandas as pd
import numpy as np

from scipy.ndimage import label
from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from plot_fixed_func import scatter_with_regression_line



def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)
    p.add_argument('in_csv',
                   help='CSV diffusion data (.csv).')

    p.add_argument('--out_suffix',
                   help='Filename prefix to save figures.')
    p.add_argument('--out_dir',
                   help='Output directory to save figures. ')

    plot_opts = p.add_argument_group(title='Heatmap display options')
    plot_opts.add_argument('--marker',
                           help='Marker shape used for scatter. ')
    plot_opts.add_argument('--markercolor', default='#FFFFFF',
                           help='Color of marker. ')
    plot_opts.add_argument('--marker_edgecolor', default='#0066cc',
                           help='Color of marker edge. ')
    plot_opts.add_argument('--regression_line_color',default='#ff0000',
                           help='Color of regression line. \n'
                                'By default YlGnBu is used.')

    add_overwrite_arg(p)

    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    if args.out_suffix is None:
        args.out_suffix = '_Pearson_Correlation.png'

    # Load Data frame
    df = pd.read_csv(args.in_csv)

    bundle_list = df.Bundles.unique().tolist()
    bundle_list_title = bundle_list.replace('_', ' ', regex=True)

    for idx, bundle in enumerate(bundle_list_title):
        bdl = df[df.Bundles == bundle]
        bdl=bdl.pivot(index='Sid',columns='Measures', values='Value')
        metric_list=bdl.columns.tolist()

        for i in metric_list:
            for j in metric_list:
                if i != j:
                    x=bdl[i]
                    y=bdl[j]
                    # pearson correlation
                    slope, intercept, r, p, stderr = scipy.stats.linregress(x, y)
                    line = f'Pearson coefficient: r={r:.2f}, p={p:.2f}'
                    figtitle = bundle + ' - Correlation between '+ i + ' and ' + j

                    scatter_with_regression_line(x,y, intercept + slope * x,
                                                 xlabel=i, ylabel=j,
                                                 marker = args.marker, 
                                                 marker_color=args.markercolor,
                                                 marker_edgecolors=args.marker_edgecolor,
                                                 line_label=line,
                                                 line_color=args.regression_line_color,
                                                 figtitle=figtitle)
                    curr_foler = bundle_list[idx]
                    outname = bundle_list[idx] + '_' + i + '_' + j + args.out_suffix
                    plt.savefig(os.path.join(args.out_dir, curr_foler, outname),
                                dpi=500, bbox_inches='tight')
                    plt.close('all')


if __name__ == '__main__':
    main()
