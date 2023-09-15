#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to plot average measurements based on two conditions ('Correction') from
CSV output of rdt_prepare_csv for figures.py.
Written for the PK Oirnetation ihMT Paper!
It needs to be adapted for any other data.

# To display the two conditions side by side
mi_plot_mean_measure.py merged_csv_long_modify.csv --merge_lr

# To display the two conditions in two separate graphs
mi_plot_mean_measure.py merged_csv_long_modify.csv --merge_lr --split_visu
"""

import argparse
import os

import numpy as np
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
                   help='Output filename to save plots.')
    p.add_argument('--out_dir',
                   help='Output directory to save plots.')
    p.add_argument('--colormap',
                    help='Dictionnary of colormap to use for each metric.'),
    p.add_argument('--merge_lr', action='store_true',
                   help='Averaged left and right bundle values (mean). ')
    p.add_argument('--specific_stats',  default='mean',
                   help='Use to select a specific statistic. '
                        '[%(default)s]')
    p.add_argument('--split_visu', action='store_true',
                   help='To generate two graphs according to correction '
                        ' condition. ')

    add_overwrite_arg(p)
    return p


bundle_colors = {"AF": "#368a6b", "CC_7": "#047b3c", "CC_6": "#00ffea",
                 "CC_5": "#0544c4","CC_4":"#fa7e08", "CC_3": "#82830e",
                 "CC_2b": "#bcbb73", "CC_2a": "#fe8ad5", "CC_1":"#ff4707",
                 "CG": "#ffff00", "CST": "#1b0385","IFOF": "#f9c306", "ILF": "#11d473",
                 "SLF_1": "#d9cef5","SLF_2": "#9a82d7", "SLF_3": "#615481",
                 "OR": "#7ab5af", "UF": "#7541f8", "MCP":"#C34095",
                 "ICP":"#CD5C5C"}

# Could be optimize
def set_x_position(df_ref, df_adapt, start_point=1, step_point=0.8,
                   step_cat=2.5):
    """
    Redefine the position of the bundles on the x axis in order to
    display the 2 conditions side by side.

    Parameters
    ----------
    df_ref         frame corresponding to condition 1, first on the x axis
    df_adapt       frame corresponding to condition 2, second on the x axis
    start_point    starting point on the x axis
    step_point     space between condition 1 and 2
    step_cat       space between 2 bundles

    Return
    ------
    the df_ref and df_adapt dataframes with a column corresponding to the
    new position on the x axis for each bundle.
    """
    j=start_point

    for i in df_ref['Bundles'].unique():
        tmp = df_ref.loc[df_ref.Bundles == i]
        tmp['x_psotion'] = j
        df_ref.loc[df_ref.Bundles == i, 'x_psotion'] = tmp['x_psotion']
        tmp['x_psotion'] = j + step_point
        df_adapt.loc[df_adapt.Bundles == i, 'x_psotion'] = tmp['x_psotion'].values
        j+=step_cat

    return df_ref, df_adapt



def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    if args.out_prefix is None:
        args.out_prefix = 'mean_'

    df = pd.read_csv(args.in_csv)
    df.drop('Unnamed: 0', axis=1, inplace=True)

    df = df[df['Statistics'] == args.specific_stats]

    if 'Section' in df.columns.tolist():
        df=df[df['Section'].isnull()]
        df.drop('Section', axis=1, inplace=True)

    if args.merge_lr:
        df['Bundles'] = df['Bundles'].replace('_L','', regex=True)
        df['Bundles'] = df['Bundles'].replace('_R','', regex=True)
        df=df.groupby(['Sid','Bundles','Statistics','Measures','Correction'])['Value'].mean().reset_index()

    df = df[~(df['Bundles'] == 'CR')]
    df = df[~(df['Bundles'] == 'CC_1')]
    df = df[~(df['Bundles'] == 'ICP')]
    df = df.reset_index(drop=True)

    # print(df[df['Bundles'] == 'AF_L'][df['Correction'] == "corrected"][df['Statistics'] == "mean"][df['Value'] > 3])
    print(df.loc[(df['Value'] > 3) & (df['Measures'] == "ihMTsat")])

    # Set seaborn display settings
    sns.set_style("whitegrid")
    sns.set_context("paper",
                    rc={"font.size":15,"axes.titlesize":20,
                        "axes.linewidth":0.5,"axes.edgecolor":'k',
                        "axes.labelsize":20, "xtick.labelsize":18,
                        "ytick.labelsize":20, "axes.labelpad":6,
                        "axes.titlepad":3,"legend.fontsize":10,
                        "legend.borderaxespad":3,"legend.columnspacing":3,
                        "figure.dpi":300, "legend.title_fontsize":12,
                        'legend.frameon': False, 'grid.linewidth': 0})

    # Loop to generate the graphs of each MRI measurement
    for metric in df['Measures'].unique():
        curr_df=df[df['Measures'] == metric]

        curr_title = "Mean " + metric + " across bundles"

        if args.colormap is not None:
            col_map = args.colormap
        else:
            col_map = bundle_colors

        if args.split_visu:

            # mean = np.mean(curr_df['Value'])
            curr_df_original = curr_df[curr_df['Correction'] == 'original']
            curr_df_corrected = curr_df[curr_df['Correction'] == 'corrected']
            mean_ori = curr_df_original['Value'].mean()
            mean_cor = curr_df_corrected['Value'].mean()

            # To display the two conditions in two separate graphs
            kws = {"s": 70, "facecolor": "none", "linewidth": 0}
            p = sns.relplot(data = curr_df, x ='Bundles',y ='Value',
                            hue = 'Bundles',
                            col = 'Correction', col_order=['original','corrected'],
                            legend = False, height = 6, aspect = 1.4,
                            facet_kws={'sharey': True,'sharex': True},
                            palette=col_map, markers=["s", "o"],
                            style="Correction", **kws, )
            p.axes[0,0].axhline(y=mean_ori, color='grey', linestyle='--', alpha=0.5)
            p.axes[0,1].axhline(y=mean_cor, color='grey', linestyle='--', alpha=0.5)
            # p.set_titles('{col_name}')
            # p.set_titles("")
            p.set_xticklabels(rotation=60)
            p.set(ylabel=metric)
            if metric == 'MTR' or metric == 'MTsat':
                p.axes[0,0].set_title('Original')
                p.axes[0,1].set_title('Corrected')
            else:
                p.set_titles("")
            # remove Legend title
            #p._legend.texts[0].set_text("")

        else:

            # To display the two conditions side by side
            # Reorganization of the dataframe to set the new
            # positions on the x axis
            curr_df = curr_df.sort_values(by = ['Bundles','Correction'])
            curr_df['x_psotion'] = 1
            curr_df = curr_df.reset_index(drop=True)
            curr_df_original = curr_df[curr_df['Correction'] == 'original']
            curr_df_corrected = curr_df[curr_df['Correction'] == 'corrected']

            curr_df_original, curr_df_corrected = set_x_position(curr_df_original,
                                                                 curr_df_corrected)

            # Create fig and ax to add scatterplot
            fig, ax = plt.subplots(figsize=(15,8))

            # Add scatter corresponding to first dataframe
            kws = {"s": 55, "facecolor": "none", "linewidth": 0}
            g1=sns.scatterplot(ax=ax, data=curr_df_original, x='x_psotion',
                               y='Value', hue='Bundles', marker="o",
                               edgecolor="none", palette=col_map, **kws, )
            g1.tick_params(right=False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.set(title='Title', ylabel='ihMTR', xlabel='Bundles')

            # Duplicate ax to plot the second dataframe
            ax2 = ax.twinx()
            kws = {"s": 55, "facecolor": "none", "linewidth": 0}
            g2=sns.scatterplot(ax=ax, data=curr_df_corrected, x='x_psotion',
                               y='Value', hue='Bundles', marker="s",
                               edgecolor="none", palette=col_map,
                               legend=None, **kws, )
            ax2.spines['right'].set_visible(False)
            ax2.spines['top'].set_visible(False)
            plt.setp(ax2.get_yticklabels(), visible=False)
            plt.tick_params(right=False)
            plt.xticks(fontsize=15)
            plt.yticks(fontsize=15)

            # Adapt set x-position to match with bundles
            new_labels = curr_df_original['Bundles'].unique().tolist()
            x_new_position = curr_df_original['x_psotion'].unique().tolist()
            g2.set_xticks(x_new_position)
            g2.set_xticklabels(new_labels, size=13, rotation=40)

            # Update legend box correspoding to bundles
            g_ax=g1.axes
            handles, labels = g_ax.get_legend_handles_labels()
            ax.legend(handles, labels, title="Bundles")
            sns.move_legend(g1, "right", bbox_to_anchor=(1.15, 0.5))

        # Save plot
        plt.savefig(os.path.join(args.out_dir, args.out_prefix + metric + '.png'),
                    dpi=300, bbox_inches='tight')



if __name__ == '__main__':
    main()
