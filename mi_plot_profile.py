#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to plot prpfile from CSV ouput from rdt_prepare_csv_for_figures.py.
"""

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from scilpy.viz.utils import get_colormap

def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV MRI data.')

    p.add_argument('--out_prefix',
                   help='Output filename to save plot.')
    p.add_argument('--out_dir',
                   help='Output directory for the labeled mask.')
    p.add_argument('--colormap',
                    help='Dictionnary of colormap to use for each metric.'),
    p.add_argument('--specific_stats',  default='mean',
                   help='Use to select a specific statistic. '
                        '[%(default)s]')

    add_overwrite_arg(p)
    return p


metrics_colors ={'AD': '#ffcc00', 'FA': '#cc0000', 'MD': '#cc6600',
                 'RD': '#ff5500', 'AFD total': '#33cc33', 'NuFO': '#993333',
                 'ECVF': '#009999', 'ICVF': '#33cccc', 'ISOVF': '#00ffcc',
                 'OD': '#999966', 'MTR': '#8000ff','MTsat': '#9999ff',
                 'ihMTR': '#e600ac','ihMTdR1sat': '#ac39ac','ihMTsat': '#ac39ac'}

def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    if args.out_prefix is None:
        args.out_prefix = 'profile_'

    df = pd.read_csv(args.in_csv)
    df.drop('Unnamed: 0', axis =1, inplace=True)

    df = df[df['Statistics'] == args.specific_stats]

    df = df.reset_index(drop=True)


    for bundle in df['Bundles'].unique():
        tmp=df[df['Bundles'] == bundle]

        curr_title = "Profile of " + bundle + " measurements"

        if args.colormap is not None:
            col_map = args.colormap
        else:
            col_map = metrics_colors

        sns.set_style("whitegrid")
        sns.set_context("paper",
                        rc={"font.size":17,"axes.titlesize":15,
                            "axes.linewidth":0.5,"axes.edgecolor":'k',
                            "axes.labelsize":20, "xtick.labelsize":17,
                            "ytick.labelsize":19, "axes.labelpad":6,
                            "axes.titlepad":3,"legend.fontsize":20,
                            "legend.borderaxespad":3,"legend.columnspacing":3,
                            "figure.dpi":200, "legend.title_fontsize":0,
                            'grid.linewidth': 0})

        #style='correction', ajouter pour effect correction
        p = sns.relplot(data = tmp, x ='Section',y ='Value',hue = 'Measures',
                    ci = None, linewidth = 3, col = 'Method', kind ='line',
                    legend = False, facet_kws={'sharey': False,'sharex': True},
                    height = 7, aspect = 1.4, palette=col_map)

        plt.savefig(os.path.join(args.out_dir, args.out_prefix + bundle + '.png'),
                    dpi=200, bbox_inches='tight')



if __name__ == '__main__':
    main()
