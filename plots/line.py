#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def interactive_lineplot(df, x_col, y_col, color_col=False, xrange=None,
                         yrange=None, custom_y_dict=None, colormap=px.colors.qualitative.Set2,
                         frame=None, group=None, y_label='', x_label='',
                         title='', template="plotly_white", kwgs={}):
    """
    Generate an interactive lineplot.

    df :                Dataframe containing columns for x and y
    x/y_col :           Columns names corresponding to x and y
    colormap :          Color scale used to plot heatmap
    x/y_label :         X and Y label for the axis
    frame :             Column name used for animation frame
    group :             Column name used for animation group
    x/yrange :          Min-Max for x or y axis
    title :             Set the title of the figure
    fig_width :         Set the width of large figure (not individual heatmap)
    fig_height :        Set the height of large figure (not individual heatmap)

    Return figure structure that could be save using write_html function.
    """
    fig = px.line(df, x=x_col, y=y_col, animation_frame=frame,
                  color=color_col, range_x=xrange, range_y=yrange,
                  template=template, animation_group=group,
                  color_discrete_map=colormap, title=title, **kwgs)

    fig.update_yaxes(title_text=y_label, visible=True)
    fig.update_xaxes(title_text=x_label, visible=True)

    if custom_y_dict:
        for f in fig.frames:
            if f.name in custom_y_dict:
                f.layout.update(yaxis_range = custom_y_dict[(f.name)])

    return fig
