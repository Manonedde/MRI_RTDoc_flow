#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to plot prpfile from CSV ouput from rdt_prepare_csv_for_figures.py.
"""

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
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

    df = df[~(df['Bundles'] == 'CR')]

    df = df[~(df['Measures'] == 'MTsat')]
    df = df[~(df['Measures'] == 'ihMTsat')]
    # df = df[~(df['Measures'] == 'ihMTR')]

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
                        rc={"font.size":25,"axes.titlesize":25,
                            "axes.linewidth":0.5,"axes.edgecolor":'k',
                            "axes.labelsize":25, "xtick.labelsize":25,
                            "ytick.labelsize":25, "axes.labelpad":6,
                            "axes.titlepad":3,"legend.fontsize":25,
                            "legend.borderaxespad":3,"legend.columnspacing":3,
                            "figure.dpi":300, "legend.title_fontsize":0, "legend.title":None,
                            'grid.linewidth': 0})

        # p = sns.relplot(data = tmp, y ='Section', x ='Value', hue = 'Measures', col='Measures',
        #             linewidth = 3, style='Correction', kind ='line', col_order=['MTR','ihMTR'],
        #             legend = False, facet_kws={'sharey': True,'sharex': False},
        #             height = 10, aspect = 0.4, palette=col_map, orient="y")
        # p.set(yticks=np.linspace(1,10,10))
        # p.axes[0,0].set_xlabel('MTR')
        # p.axes[0,1].set_xlabel('ihMTR')
        p = sns.relplot(data = tmp, x ='Section', y ='Value', hue = 'Measures', row='Measures',
                    linewidth = 3, style='Correction', kind ='line', row_order=['MTR','ihMTR'],
                    legend = False, facet_kws={'sharey': False,'sharex': True},
                    height = 5, aspect = 1.8, palette=col_map, orient="x")
        p.set(xticks=np.linspace(1,10,10))
        p.axes[0,0].set_ylabel('MTR')
        p.axes[1,0].set_ylabel('ihMTR')
        p.set_titles("")

        plt.savefig(os.path.join(args.out_dir, args.out_prefix + bundle + '.png'),
                    dpi=300, bbox_inches='tight')



if __name__ == '__main__':
    main()
