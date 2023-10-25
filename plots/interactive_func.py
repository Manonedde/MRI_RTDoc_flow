#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots

# or interacive_distribution ?
def interactive_scatter(df, x_column, y_column, color_column, figtitle='',
                             colormap='Set2', f_column=None, f_row=None,
                             column_wrap=None, row_wrap=None, bgcolor="white",
                             column_spacing=0.09, row_spacing=0.09, title_size=20,
                             show_legend=False, custom_order=None, font_size=15,
                             fig_width=900, fig_height=700,line_width=1,
                             x_label='', y_label='',custom_y_range=False,
                             print_yaxis_range=False, kwgs={}):
    """
    Generate interactive distribution plot according to category (y_column).

    df :                Dataframe
    x_column:           Column corresponding to x-axis
    y_column :          Column corresponding to y-axis
    color_column:       Use column information to attribute colors
    figtitle:           Title of figure
    colormap :          Color scale used to color dot
    f_column/row :      Use to split your data as col and/or row according to columns
    column/row_wrap :   Use column information to split graph in n column and/or row
    bgcolor:            Background color of scatter plot ("white")
    column/row_spacing: Use to set the spacing between column and row
    y_label :           Y-axis label
    x_label :           X-axis label
    show_legend :       Display legend when True
    custom_order        Dictionnary correspond to {column : ['col1/row1','col2/row2']}.
                        Use with facet_col/row.
    font_size :         Set the global font size (ticks and labels axis)
    title_size :        Set the title font size
    fig_width :         Set the width of figure
    fig_height :        Set the height of figure
    kwgs:               Dictionary. Uses to parse options to plotly function
                        that are not listed in interactive function. refers
                        to plotly.express page.

    Return plotly figure structure that could be save using write_html function.
    """

    fig = px.scatter(df, x=x_column, y=y_column, color=color_column,
                     facet_col=f_column, facet_col_wrap=column_wrap,
                     facet_col_spacing=column_spacing, facet_row=f_row,
                     facet_row_spacing=row_spacing,
                     height=fig_height, width=fig_width,
                     title=figtitle, color_discrete_map=colormap,
                     category_orders=custom_order, **kwgs)

    fig.for_each_annotation(lambda anot: anot.update(
                                                text=anot.text.split("=")[-1]))
    fig.update_layout(title_x=0.5, showlegend=show_legend,
                      font={'size': font_size},
                      title_font=dict(size=title_size), plot_bgcolor=bgcolor,)
    fig.update_yaxes(matches=None, title=y_label, showticklabels=True,
                     visible=True, showline=True, linewidth=line_width,
                     linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(title=x_label, showline=True, linewidth=line_width,
                     linecolor='black')

    if custom_y_range != False:
        y_axis_name = []
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                y_axis_name.append(axis)

        y_axis_name.sort()
        for idx, yname in enumerate(y_axis_name):
            curr_key = fig.layout.annotations[idx].text
            fig.layout[yname].range = custom_y_range[curr_key]

    if print_yaxis_range:
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                print(axis, fig.layout[axis].range)

    return fig


def interactive_lineplot(df, x_col, y_col, color_col=False, use_order=False,
                         colormap=px.colors.qualitative.Set2, facetcol=False,
                         xrange=False, yrange=False, frame=False,group=False,
                         y_label='', x_label='', title='',):
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
                  color=color_col, range_x=xrange, range_y = yrange,
                  template="plotly_white", animation_group=group,
                  color_discrete_sequence=colormap,
                  title=title)

    fig.update_yaxes(title_text=y_label, visible=True)
    fig.update_xaxes(title_text=x_label,visible=True)

    return fig


def interactive_correlation(df, x_column, y_column, color_column, trend_line='ols',
                             colormap='Set2', f_column=False, f_row=False,
                             column_wrap=False, row_wrap=False, bgcolor="white",
                             column_spacing=0.09, row_spacing=0.09, title_size=20,
                             show_legend=False, custom_order=False, font_size=15,
                             fig_width=700, fig_height=700,line_width=1,
                             x_label='', y_label='',figtitle='',):
    """
    Generate interactive scatter plot.

    df :                Dataframe
    x_column:           Column corresponding to x-axis
    y_column :          Column corresponding to y-axis
    trend_line:         Type of trend line (ols)
    color_column:       Use column information to attribute colors
    figtitle:           Title of figure
    colormap :          Color scale used to color dot
    f_column/row :      Use to split your data as col and/or row according to columns
    column/row_wrap :   Use column information to split graph in n column and/or row
    bgcolor:            Background color of scatter plot ("white")
    column/row_spacing: Use to set the spacing between column and row
    y_label :           Y-axis label
    x_label :           X-axis label
    show_legend :       Display legend when True
    custom_order        Dictionnary correspond to {column : ['col/row1','col2/row2']}.
                        Use with facet_col/row.
    font_size :         Set the global font size (ticks and labels axis)
    title_size :        Set the title font size
    fig_width :         Set the width of figure
    fig_height :        Set the height of figure

    Return plotly figure structure that could be save using write_html function.
    """

    fig = px.scatter(df, x=x_column, y=y_column, trendline=trend_line,
                     color=color_column, facet_col=f_column, facet_col_wrap=column_wrap,
                     facet_col_spacing=column_spacing, facet_row=f_row,
                     facet_row_wrap=row_wrap, facet_row_spacing=row_spacing,
                     height=fig_height, width=fig_width,
                     title=figtitle, color_discrete_map=colormap,
                     category_orders=custom_order)

    fig.for_each_annotation(lambda anot: anot.update(
                                                text=anot.text.split("=")[-1]))
    fig.update_layout(title_x=0.5, showlegend=show_legend,
                      font={'size': font_size},
                      title_font=dict(size=title_size), plot_bgcolor=bgcolor,)
    fig.update_yaxes(matches=None, title=y_label, showticklabels=True,
                     visible=True, showline=True, linewidth=line_width,
                     linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(title=x_label, showline=True, linewidth=line_width,
                     linecolor='black')

    return fig
