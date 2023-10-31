#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from plots.utils import get_trend_from_plot


def interactive_distribution_plot(
        df, x_column, y_column, color_column, figtitle='', colormap='Set2',
        f_column=None, f_row=None, column_wrap=0, bgcolor="white",
        column_spacing=0.09, row_spacing=0.09, title_size=20, font_size=15,
        show_legend=False, custom_order=None, fig_width=900, fig_height=700,
        line_width=1, x_label='', y_label='', custom_y_range=False,
        print_yaxis_range=False, kwgs={}):
    """
    Generate interactive distribution plot according to category (x_column)
    and value (y_column) with individual color (color_column).

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


def interactive_lineplot(df, x_col, y_col, color_col=False, xrange=False,
                         yrange=False, colormap=px.colors.qualitative.Set2,
                         frame=False, group=False, y_label='', x_label='',
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
                  color_discrete_sequence=colormap,
                  title=title, **kwgs)

    fig.update_yaxes(title_text=y_label, visible=True)
    fig.update_xaxes(title_text=x_label, visible=True)

    return fig



def interactive_correlation_with_fit(
                    df, x, y, trend='ols', scope='overall', color_col=None,
                    frame=None, group=None, figtitle='', fig_width=900,
                    fig_height=700, save_trend_as=False, trend_outpath='',
                    template="plotly_white", kwgs={}):
    if not figtitle:
        figtitle= x + ' vs ' + y

    fig = px.scatter(df, x=df[x], y=df[y], title=figtitle, color=color_col,
                     trendline=trend, trendline_scope=scope, template=template,
                     animation_frame=frame, animation_group=group,
                     height=fig_height, width=fig_width, **kwgs)

    if save_trend_as:
        get_trend_from_plot(px.get_trendline_results(fig),
                            save_as=save_trend_as, outpath=trend_outpath)

    return fig


fig=interactive_correlation_with_fit(dfscat, 'ECVF', 'OD')
fig.write_html('/Users/eddm3601/Documents/DTI_measurement_distribution.html')


        

def generate_args_for_correlation(df, x, y, trend='ols',
                                  scope='overall', colorline='black'):
    """
    Function to generate arguments required to to buttons function of 
    layout.Updatemenu().

    df:             Dataframe
    x:              Column name used for X-axis.
    y:              Column name used for Y-axis.
    trend:          Fit data option. Could be "ols", "lowess", ect.
    scope:          How to fit is done, for all data or by group/color.
    colorline:      Color choose for line.

    Return  Dictionary which fit to buttons function of layout.Updatemenu().
    """
    args = {"x": [df[x], px.scatter(x=df[x], y=df[y],
                                    trendline=trend).data[1].x],
            "y": [df[y], px.scatter(x=df[x], y=df[y],
                                    trendline=trend).data[1].y],
            "trendline": [trend], "trendline_scope": [scope],
            "trendline_color_override": [colorline]}

    return args


def multi_correlation_with_menu(df, column_list=None, show_only=False,
                                fig_width=900, fig_height=700, trend='ols',
                                scope='overall', colorline='black',
                                kwgs={}):
    """
    Function to plot correlation between two measures with regression
    line and using a dropdown menu.

    df:             Dataframe.
    column_list:    List of column name from dataframe. By default, used all
                    columns from dataframe.

    Return      Figure structure that could be saved as html.
    """
    if column_list is None:
        column_list = df.columns.tolist()

    # Initialize the first scatter plot
    fig = go.Figure()
    figtitle = column_list[0] + ' vs ' + column_list[1]
    fig = px.scatter(df, x=df[column_list[0]], y=df[column_list[1]],
                     trendline=trend, trendline_scope=scope,
                     title=figtitle, trendline_color_override=colorline, **kwgs)
    # Generate the update menu args for each combinaison of columns
    button_menu_list = []
    for xaxis in column_list:
        for yaxis in column_list:
            if xaxis != yaxis:
                curr_button_dict = dict(
                    label=xaxis + ' vs ' + yaxis,
                    method="update",
                    args=[
                        generate_args_for_correlation(
                            df, xaxis, yaxis, trend=trend, scope=scope,
                            trendline_color_override=colorline, **kwgs),
                        {"title": xaxis + ' vs ' + yaxis,
                         'xaxis': {'title': xaxis},
                         'yaxis': {'title': yaxis}}
                    ])
                button_menu_list.append(curr_button_dict)

    # Update figure layout
    fig.update_layout(updatemenus=[go.layout.Updatemenu(
        type="dropdown", buttons=button_menu_list)], 
        template="plotly_white", width=fig_width, height=fig_height)

    if show_only:
        fig.show()
    else:
        return fig


def scatter_with_two_menu(df, column_list=None, show_only=False,
                          fig_width=700, fig_height=700, kwgs={}):
    """
    Function to plot correlation between two measures with regression
    line and using a dropdown menu.

    df:             Dataframe.
    column_list:    List of column name from dataframe. By default, used all
                    columns from dataframe.

    Return      Figure structure that could be saved as html.
    """
    if column_list is None:
        column_list = df.columns.tolist()

    # Initialize the first scatter plot
    fig = go.Figure()
    figtitle = column_list[0] + ' vs ' + column_list[1]
    fig = px.scatter(df, x=df[column_list[0]], y=df[column_list[1]],
                     title=figtitle, **kwgs)

    # Update layout to add menu list
    fig.update_layout(
        updatemenus=[
            {"buttons": [
                    {"label": col,
                     "method": "update",
                     "args": [{axis: [df[col]]},
                              {f"{axis}axis": {"title": {"text": col}}},
                              ],
                    }
                    for col in df.columns
                    ],
             "x": 0 if axis == "x" else 0.1,
             "y": 1.2,
            }
            for axis in "xy"],
        template="plotly_white", width=fig_width, height=fig_height)

    if show_only:
        fig.show()
    else:
        return fig