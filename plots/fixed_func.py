
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from df_func import compute_ecvf_from_df

def boxplot_with_mean_line(df, x_col, y_col, color_col, use_order=False,
                           colormap="Set2", box_line_width=2,mean_line_width=3,
                           transparency=0.4, use_marker='o', error_bar=None,
                           y_label='', x_label='', title='', legend_title='',
                           plot_size=(18,7)):

      plt.figure(figsize=plot_size)
      sns.set(style="ticks", rc={"lines.linewidth": 1.5})

      fig = sns.boxplot(data=df, x=x_col, y=y_col, hue=color_col,
                       hue_order=use_order, palette=colormap,
                       linewidth=box_line_width, saturation=transparency)
      sns.pointplot(data=df, x=x_col, y=y_col, hue=color_col, hue_order=use_order,
                    dodge=.6 - .6 / 3, scale=1, marker=use_marker,
                    errorbar=error_bar,  palette=colormap)

      handles, labels = ax.get_legend_handles_labels()
      ax.legend(handles=handles[:3], labels=labels[:2] + ["means"],
                title=legend_title, bbox_to_anchor=(1.02, 1.02),
                loc='upper left')

      for l in ax.lines:
          #print(l.get_linewidth())
          plt.setp(l,linewidth=mean_line_width)

      ax.set_ylabel(y_label)
      ax.set_xlabel(x_label)
      plt.title(title)
      plt.tight_layout()

      return fig


# Lineplot
def longitudinal_lineplot(df, x_col, y_col, color_col, split_col=False,
                          use_order=False, title_size=22, title_loc=1.1,
                           colormap="viridis", box_line_width=2,line_width=1.3,
                           transparency=0.4, use_marker='o', error_bar=None,
                           y_label='', x_label='', title='', legend_ncol=None,
                           style=False,height = 7, aspect = 1.4,
                           split_col_wrap=False,x_lim=False):

    fig = sns.relplot(data=df, x=x_col, y=y_col, hue=color_col,
                    kind='line', col=split_col, linewidth=line_width,
                    palette=colormap)
    if x_lim:
        fig.set(xlim=x_lim)

    fig.set_titles('{col_name}')
    fig.set_ylabels(y_label)
    fig.set_xlabels(x_label)
    plt.suptitle(title, fontsize=title_size, y=title_loc)
    sns.move_legend(p, "lower center", bbox_to_anchor=(0.45, -0.4), ncol=legend_ncol)
    plt.subplots_adjust(top=0.9, hspace=0.1, wspace=0.1)

    return fig


def scatter_with_regression_line(x,y, y_line, xlabel='', ylabel='',figtitle='',
                                 marker_type='o', marker_color='k',
                                 marker_edgecolors='k', marker_width = 0.5,
                                 marker_size = 10, line_label='',line_color='r',
                                 line_width=0.5,transparency=0.8,):

    fig, ax = plt.subplots()
    # Plot data points
    ax.scatter(x, y, color=marker_color, edgecolors=marker_edgecolors,
               marker=marker_type, linewidth=marker_width, s=marker_size,
               alpha=transparency)

    # plot fit line
    ax.plot(x, y_line, label=line_label, color=line_color,
            linewidth=line_width)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(facecolor='white')
    plt.legend(loc='best', frameon=False,
                bbox_to_anchor = (0.2,-0.1,0.5,0), prop={'size': 10})

    fig_title = figtitle
    plt.title(fig_title)

    return fig, ax
