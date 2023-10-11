#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots

from plotly.subplots import make_subplots

# or interacive_distribution ?
def interactive_scatter(df, x_column, y_column, color_column, figtitle='',
                             colormap='Set2', f_column=False, f_row=False,
                             column_wrap=False, row_wrap=False, bgcolor="white",
                             column_spacing=0.09, row_spacing=0.09, title_size=20,
                             show_legend=False, custom_order=False, font_size=15,
                             fig_width=700, fig_height=700,line_width=1,
                             x_label='', y_label='',):
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

    Return plotly figure structure that could be save using write_html function.
    """

    fig = px.scatter(df, x=x_column, y=y_column, color=color_column,
                     facet_col=f_column, facet_col_wrap=column_wrap,
                     facet_col_spacing=column_spacing, facet_row=f_row,
                     facet_row_wrap=row_wrap, facet_row_spacing=row_spacing,
                     height=fig_height, width=fig_width,
                     title=figtitle, color_discrete_map=colormap,
                     category_orders=custom_order, print_yaxis_range=False,
                     custom_y_range=False,)

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

        for idx, yname in enumerate(y_axis_name):
            curr_key = fig.layout.annotations[idx].text
            fig.layout[yname].range = custom_y_range[curr_key]

    if print_yaxis_range:
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                print(axis, fig.layout[axis].range)

    return fig



def interactive_lineplot(df, x_col, y_col, color_col=None, use_order=None,
                         colormap=px.colors.qualitative.Set2, facetcol=None,
                         xrange=None, yrange=None, frame=None,group=None,
                         y_label='', x_label='', title='',):
    """
    Generate an interactive lineplot.

    df :                Dataframe containing columns for x and y
    x/y_col :           Columns names corresponding to x and y
    colormap :          Color scale used to plot heatmap
    facetcol:           Use to split lineplot with criterion (Group for instance)
    x/y_label :         X and Y label for the axis
    frame :             Column name used for animation frame
    group :             Column name used for animation group
    x/yrange :          Min-Max for x or y axis
    title :             Set the title of the figure
    fig_width :         Set the width of figure
    fig_height :        Set the height of figure

    Return figure structure that could be save using write_html function.
    """

    fig = px.line(df, x=x_col, y=y_col, animation_frame=frame,
                  color=color_col, range_x=xrange, range_y = yrange,
                  template="plotly_white", animation_group=group,
                  color_discrete_sequence=colormap,
                  title=title, facet_col=facetcol)

    fig.update_yaxes(title_text=y_label, visible=True)
    fig.update_xaxes(title_text=x_label,visible=True)

    return fig



def interactive_boxplot(df, x_col, y_col, color_col=None, use_order=None,
                         colormap=px.colors.qualitative.Set2, facetcol=None,
                         xrange=None, yrange=None, frame=None,group=None,
                         y_label='', x_label='', title='',):
    """
    Generate an interactive boxplot.

    df :                Dataframe containing columns for x and y
    x/y_col :           Columns names corresponding to x and y
    colormap :          Color scale used to plot heatmap
    facetcol:           Use to split lineplot with criterion (Group for instance)
    x/y_label :         X and Y label for the axis
    frame :             Column name used for animation frame
    group :             Column name used for animation group
    x/yrange :          Min-Max for x or y axis
    title :             Set the title of the figure
    fig_width :         Set the width of figure
    fig_height :        Set the height of figure

    Return figure structure that could be save using write_html function.
    """

    fig = px.box(df, x=x_col, y=y_col, animation_frame=frame,
                  color=color_col, range_x=xrange, range_y = yrange,
                  template="plotly_white", animation_group=group,
                  color_discrete_sequence=colormap,
                  title=title, facet_col=facetcol)

    fig.update_yaxes(title_text=y_label, visible=True)
    fig.update_xaxes(title_text=x_label,visible=True)

    return fig


def interactive_correlation(df, x_column, y_column, color_column, trend_line='ols',
                             colormap='Set2', f_column=None, f_row=None,
                             column_wrap=None, row_wrap=None, bgcolor="white",
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



def interactive_evolution_lineplot(df, colums_as_labels, x_col, y_col,
                                   colors_labels='', xy_label='',
                                   title='',marker_size=[12, 8, 8, 8],
                                   line_size = [4, 2, 2, 2],
                                   fig_width=700, fig_height=500,):
    """
    Generate an interactive individual line according to Category in
    colums_as_labels. Colors labels, marker and line size must be set in order
    of colums_as_labels. Most of the time colums_as_labels is Lesion_group with:
    HC, NAWM, Penumbra and Lesion. Marker and Line size first value represents
    HC data that's why, values are different from others. Use options to
    modify it.

    df :                Dataframe containing columns for x and y
    x/y_col :           Columns names corresponding to x and y
    colums_as_labels:   Colums used as label to plot individual line
    colors_labels :     List of color corresponding to each category
    facetcol:           Use to split lineplot with criterion (Group for instance)
    x/y_label :         X and Y label for the axis
    title :             Set the title of the figure
    fig_width :         Set the width of figure
    fig_height :        Set the height of figure

    Return figure structure that could be save using write_html function.
    """

    labels = df[colums_as_labels].unique().tolist()
    if not colors_labels:
        colors_labels = ['rgb(49,130,189)','rgb(67,67,67)',
                         'rgb(115,115,115)', 'rgb(189,189,189)']

    if not xy_label:
        xy_label = x_col, y_col

    fig = go.Figure()
    annotations = []

    for idx, label in enumerate(labels):
        tmp = df.loc[df[colums_as_labels] == label]

        fig.add_trace(go.Scatter(x=tmp[x_col].values, y=tmp[y_col].values,
                                 mode='lines',name=label,
                                 line=dict(color=colors_labels[idx],
                                 width=line_size[idx]),
                                 connectgaps=True,))

        # Add first and ending data point
        fig.add_trace(go.Scatter(x=[tmp[x_col].values[0], tmp[x_col].values[-1]],
                                 y=[tmp[y_col].values[0], tmp[y_col].values[-1]],
                                mode='markers',
                                marker=dict(color=colors_labels[idx],
                                size=marker_size[idx])))

        # Add annotations at first and ending point
        annotations.append(dict(xref='paper', x=0.05, y=tmp[y_col].values[0],
                                xanchor='right', yanchor='middle',
                                text=labels[idx] + ' {}'.format(
                                                round(tmp[y_col].values[0],2)),
                                font=dict(family='Arial',size=16),
                                showarrow=False))

        annotations.append(dict(xref='paper', x=0.95, y=tmp[y_col].values[-1],
                               xanchor='left',yanchor='middle',
                               text='{}'.format(round(tmp[y_col].values[-1],2)),
                               font=dict(family='Arial',size=16),
                               showarrow=False))

    # Title
    annotations.append(dict(xref='paper', yref='paper', x=0.0, y=1.05,
                            xanchor='left', yanchor='bottom',
                            text=title, showarrow=False,
                            font=dict(family='Arial', size=30,
                                      color='rgb(37,37,37)')))
    # X label
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.1,
                            xanchor='center', yanchor='top',
                            text=xy_label[0], showarrow=False,
                            font=dict(family='Arial', size=17,
                                      color='rgb(150,150,150)'),))
    # Y label
    annotations.append(dict(xref='paper', yref='paper', x=0, y=1,
                            xanchor='left', yanchor='middle',
                            text=xy_label[1], showarrow=False,
                            font=dict(family='Arial', size=17,
                                      color='rgb(150,150,150)'),))

    fig.update_layout(annotations=annotations)

    fig.update_layout(width=fig_width, height=fig_height,
                      xaxis=dict(showline=True, showgrid=False,
                                 showticklabels=True, linewidth=2,
                                 linecolor='rgb(204, 204, 204)', ticks='outside',
                                 tickfont=dict(family='Arial', size=12,
                                               color='rgb(82, 82, 82)',),),
                      yaxis=dict(showgrid=False, zeroline=False, showline=False,
                                 showticklabels=False,), autosize=False,
                                 margin=dict(autoexpand=False,
                                             l=100, r=20, t=110,),
                      showlegend=False, plot_bgcolor='white')

    return fig
