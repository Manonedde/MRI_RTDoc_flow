#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def interactive_heatmap(corr_map, title='', colbar_title='',
                        colormap=px.colors.sequential.YlGnBu,
                        y_label='', x_label='', r_min=0.3, r_max=1,
                        tick_font_size=15, title_size=20, tick_angle=90,
                        fig_width=600, fig_height=600, kwgs={}):
    """
    Generate interactive heatmap.

    corr_map :          Correlation matrix [index,column]
    title:              Title of figure
    colormap :          Color scale used to plot heatmap
    colbar_title :      Title of colorbar
    x/y_label :         X/Y label for the heatmap
    r_min,r_max :       Minimun and maximum values used to set the colorbar
    tick_angle :        Set angle of X tick labels
    tick_font_size :    Set the tick font size
    title_size :        Set the title font size
    fig_width :         Set the width of large figure (not individual heatmap)
    fig_height :        Set the height of large figure (not individual heatmap)

    Return figure structure that could be save using write_html function.
    """
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=corr_map.values, x=corr_map.columns,
                             y=corr_map.index, colorscale=colormap,
                             zmin=r_min, zmax=r_max,
                             colorbar=dict(title=colbar_title), **kwgs))
    # fig.update_xaxes(side = "top")
    fig.update_layout(go.Layout(width=fig_width,
                                height=fig_height,
                                title=title, title_x=0.5,
                                font={'size': tick_font_size},
                                title_font=dict(size=title_size),
                                yaxis=dict(title=y_label, visible=True,
                                           autorange='reversed'),
                                xaxis=dict(title=x_label, tickangle=tick_angle,
                                           side='bottom')))
    return fig


def interactive_heatmap_with_slider(
            corr_dfs, title='', colbar_title='',
            colormap=px.colors.sequential.YlGnBu,
            slider_label='Session ', y_label='Metrics by Bundles',
            r_min=0.3, r_max=1, tick_angle=45, tick_font_size=12,
            title_size=15, fig_width=600, fig_height=600,):
    """
    Generate an interactive heatmap with a slider. Slider could be
    the sessions in time, the bundles or the subjects. The corr_dfs input
    must be a list of correlation matrix corresponding to the parameter used
    for the slider. If slider is session, corr_dfs correspond to a list of
    matrix of all subjects, bundles and metrics for each session.

    corr_dfs :          List of correlation matrix [index,column] x n_time
    title :             Label corresponding to the heatmap title
    colormap :          Color scale used to plot heatmap
    colbar_title :      Title of colorbar
    slider_label :      Label used for the set the slider
    y_label :           Y label for the heatmap
    r_min,r_max :       Minimun and maximum values used to set the colorbar
    tick_angle :        Set angle of X tick labels
    tick_font_size :    Set the tick font size
    title_size :        Set the title font size
    fig_width :         Set the width of large figure (not individual heatmap)
    fig_height :        Set the height of large figure (not individual heatmap)

    Return figure structure that could be save using write_html function.
    """

    frames = [
        go.Frame(data=go.Heatmap(z=df.values, x=df.columns, y=df.index,
                                 colorscale=colormap, zmin=r_min, zmax=r_max,
                                 colorbar=dict(title=colbar_title)),
                 name=slider_label + str(i+1))
        for i, df in enumerate(corr_dfs)]

    fig=go.Figure(data=frames[0].data, frames=frames).update_layout(
        # iterate over frames to generate steps
        sliders=[{"steps": [{"args": [[f.name],{"frame": {"duration": 0,
                                                          "redraw": True},
                                                "mode": "immediate",},],
                             "label": f.name, "method": "animate",}
                            for f in frames],}],
        # Set figure size, x and y axis and Title
        height=fig_height, width=fig_width,
        xaxis={"title": title, "tickangle": tick_angle, 'side': 'top'},
        title_x=0.5, font={'size': tick_font_size},
        title_font=dict(size=title_size),
        yaxis=dict(visible=True, autorange='reversed', title=y_label),)

    return fig


def interactive_heatmap_group(corr_group1, corr_group2, label_group1,
                              label_group2, colbar_title="Pearson r",
                              colormap=px.colors.sequential.YlGnBu,
                              y_label='', r_min=0.3, r_max=1,
                              tick_font_size=15, title_size=20, tick_angle=90,
                              fig_width=700, fig_height=700, kwgs={}):
    """
    Generate two interactive heatmaps.

    corr_group(1/2) :   List of correlation matrix [index,column] x n_time
    label_group(1/2) :  Label corresponding to the two groups
    title:              Title of figure
    colormap :          Color scale used to plot heatmap
    colbar_title :      Title of colorbar
    y_label :           Y label for the heatmap
    r_min,r_max :       Minimun and maximum values used to set the colorbar
    tick_angle :        Set angle of X tick labels
    tick_font_size :    Set the tick font size
    title_size :        Set the title font size
    fig_width :         Set the width of large figure (not individual heatmap)
    fig_height :        Set the height of large figure (not individual heatmap)

    Return figure structure that could be save using write_html function.
    """

    # Check if the number of correlation matrix is identifical between groups
    if len(corr_group1) != len(corr_group2):
        print("The number of correlation matrix is not equal between groups.\n"
              " Please provide a same number of correlation matrix. ")

    # Create facetgrid to plot two heatmap corresponding to the two groups
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, shared_xaxes=True)

    fig.append_trace(
        go.Heatmap(z=corr_group1.values, x=corr_group1.columns,
                   y=corr_group1.index, colorscale=colormap,
                   colorbar=dict(title=colbar_title), zmin=r_min, zmax=r_max,
                   name=label_group1, **kwgs),row=1, col=1)

    fig.append_trace(
        go.Heatmap(z=corr_group2.values, x=corr_group2.columns,
                   y=corr_group2.index, colorscale=colormap,
                   colorbar=dict(title=colbar_title), zmin=r_min, zmax=r_max,
                   name=label_group2, **kwgs), row=1, col=2)

    # Update axis heatmap group 1
    fig.update_yaxes(title_text=y_label,visible=True,
                    autorange='reversed', tickfont={'size': tick_font_size},
                    title_font=dict(size=title_size),row=1, col=1)
    fig.update_xaxes(title_text=label_group1,visible=True, side='top',
                    tickangle=tick_angle, tickfont={'size': tick_font_size},
                    title_font=dict(size=title_size),row=1, col=1)
    # Update axis heatmap group 2
    fig.update_yaxes(title_text="", visible=False,autorange='reversed',
                    tickfont={'size': tick_font_size},row=1, col=2)
    fig.update_xaxes(title_text=label_group2,visible=True, side='top',
                    tickangle=tick_angle,tickfont={'size': tick_font_size},
                    title_font=dict(size=title_size),row=1, col=2)

    # Update legend and colorbar
    fig.update_layout(
            legend=dict(x=0.5, xanchor='center', y=1, yanchor='bottom',
            orientation='h'),
            coloraxis1=dict(colorscale=colormap,
                            colorbar_x=-0.3, colorbar_thickness=10),
            coloraxis2=dict(colorscale=colormap,
                            colorbar_x=1.00, colorbar_thickness=10),
            width=600, height=300)
    # Final update of figure size
    fig.update_layout(template ="plotly_white", width=fig_width,
                      height=fig_height)

    return fig


def interactive_heatmap_group_with_slider(
                corr_group1, corr_group2, label_group1, label_group2,
                colormap=px.colors.sequential.YlGnBu, colbar_title="Pearson r",
                slider_label='Session ', y_label='Metrics by Bundles',
                r_min=0.3, r_max=1, tick_angle=45, tick_font_size=12,
                title_size=15, fig_width=1150, fig_height=600,):

    """
    Generate two interactive heatmaps with a slider. Slider could be
    the sessions in time, the bundles or the subjects. The corr_group input
    must be a list of correlation matrix corresponding to the parameter used
    for the slider. If slider is session, corr_group correspond to a list of
    matrix of all subjects, bundles and metrics for each session and each group.

    corr_group(1/2) :   List of correlation matrix [index,column] x n_time
    label_group(1/2) :  Label corresponding to the two groups
    colormap :          Color scale used to plot heatmap
    colbar_title :      Title of colorbar
    slider_label :      Label used for the set the slider
    y_label :           Y label for the heatmap
    r_min,r_max :       Minimun and maximum values used to set the colorbar
    tick_angle :        Set angle of X tick labels
    tick_font_size :    Set the tick font size
    title_size :        Set the title font size
    fig_width :         Set the width of large figure (not individual heatmap)
    fig_height :        Set the height of large figure (not individual heatmap)

    Return figure structure that could be save using write_html function.
    """

    # Check if the number of correlation matrix is identifical between groups
    if len(corr_group1) != len(corr_group2):
        print("The number of correlation matrix is not equal between groups.\n"
              " Please provide a same number of correlation matrix. ")
    # Create facetgrid to plot two heatmap corresponding to the two groups
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, shared_xaxes=True)

    for curr_corr in range(len(corr_group1)):
        fig.append_trace(
            go.Heatmap(
                z=corr_group1[curr_corr].values, x=corr_group1[curr_corr].columns,
                y=corr_group1[curr_corr].index,
                colorscale=colormap,
                colorbar=dict(title=colbar_title), zmin=r_min, zmax=r_max,
                name=slider_label + str(curr_corr+1)
                ),row=1, col=1)

        fig.append_trace(
            go.Heatmap(
                z=corr_group2[curr_corr].values, x=corr_group2[curr_corr].columns,
                y=corr_group2[curr_corr].index, zmin=r_min, zmax=r_max,
                colorscale=colormap,
                colorbar=dict(title=colbar_title),
                name=slider_label + str(curr_corr+1)
                ), row=1, col=2)

    # # Create and set the steps for slider : here reference to session
    slider_steps = []
    n_slider = 0
    for i in range(0, len(fig.data), 2):
        n_slider +=1
        slider_step = dict(method="restyle",
                           args=["visible", [False] * len(fig.data)])
        slider_step["args"][1][i:i+2] = [True, True]
        slider_step["label"] = slider_label + str(n_slider)
        slider_steps.append(slider_step)

    sliders = [dict(active=0,steps=slider_steps)]

    # Update legend and colorbar
    fig.update_layout(
            legend=dict(x=0.5, xanchor='center', y=1, yanchor='bottom',
            orientation='h'),
            coloraxis1=dict(colorscale=colormap,
                            colorbar_x=-0.3, colorbar_thickness=10),
            coloraxis2=dict(colorscale=colormap,
                            colorbar_x=1.00, colorbar_thickness=10),
            width=600, height=300)

    # Update axis heatmap group 1
    fig.update_yaxes(title_text=y_label,visible=True,
                    autorange='reversed', tickfont={'size': tick_font_size},
                    title_font=dict(size=title_size),row=1, col=1)
    fig.update_xaxes(title_text=label_group1,visible=True, side='top',
                    tickangle=tick_angle, tickfont={'size': tick_font_size},
                    title_font=dict(size=title_size),row=1, col=1)
    # Update axis heatmap group 2
    fig.update_yaxes(title_text="", visible=False,autorange='reversed',
                    tickfont={'size': tick_font_size},row=1, col=2)
    fig.update_xaxes(title_text=label_group2,visible=True, side='top',
                    tickangle=tick_angle,tickfont={'size': tick_font_size},
                    title_font=dict(size=title_size),row=1, col=2)

    # Add sliders and set global appearance
    fig.update_layout(sliders=sliders, template ="plotly_white")
    # Final update of figure size
    fig.update_layout(width=fig_width, height=fig_height)

    return fig
