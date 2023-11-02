#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to plot 3-dimensional graphes with and without interactive format.
"""
import itertools
import numpy as np
import math
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from mpl_toolkits.mplot3d import Axes3D #axes3d
import matplotlib.pyplot as plt
import matplotlib.cm as cm           # import colormap stuff!
from matplotlib.cm import get_cmap



## from fixed3dbar.py
def bar_charts3d(
        df, x_col_name, y_col_name, color='x',
        x_title='',y_title='', z_title='', title='',
        opacity_val=0.9, nan_value=False,figure_size=(15,9),
        xy_elevation=15, z_rotation=250, camera_dist=15,
        add_legend_box=False, legen_labels='', colors_name='jet',):
    """
    Generate a barchart in 3D or a sparse barchart in 3D
    z_rotation : the rotation around the z axis,
                 0 : looking from x, (-)90 : looking from y, 270 looking from z
    xy_elevation : the angle between the eye and the xy plane
    camera_dist : the distance from the center visible point in data coordinates
    """

    plt.style.use('seaborn-white')

    df = df.set_index([x_col_name, y_col_name])

    #if nan in csv files
    if nan_value:
        df = df.unstack().fillna(0).stack()

    if x_title is None:
        x_title = x_col_name
    if y_title is None:
        y_title = y_col_name
    if x_title is None:
        z_title = list(df.columns)

    xlabels = df.index.get_level_values(x_col_name).unique()
    ylabels = df.index.get_level_values(y_col_name).unique()
    x = np.arange(xlabels.shape[0])
    y = np.arange(ylabels.shape[0])

    # Create the meshgrid for axes
    x_mesh_position, y_mesh_position = np.meshgrid(x, y, copy=False)

    list_z_value = []
    for i, group in df.groupby(level=1)['value']:
        list_z_value.append(group.values)
    z = np.hstack(list_z_value).ravel()

    # create figure
    fig = plt.figure(figsize=figure_size)
    ax = fig.add_subplot(111, projection='3d')

    # Making the intervals in the axes match with their respective entries
    # Renaming the ticks as they were before
    ax.w_xaxis.set_ticks(x + 0.5/2.)
    ax.w_yaxis.set_ticks(y + 0.5/2.)
    ax.w_xaxis.set_ticklabels(xlabels)
    ax.w_yaxis.set_ticklabels(ylabels)

    # Labeling the 3 dimensions
    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title)
    ax.set_zlabel(z_title)

    # optional view configurations
    #ax.view_init(elev=xy_elevation, azim=z_rotation)
    ax.elev=xy_elevation
    ax.azim=z_rotation
    ax.dist = camera_dist

    # Selecting an appropriate colormap +
    # Choosing the range of values to be extended in the set colormap
    values = np.linspace(0.2, 1., x_mesh_position.ravel().shape[0])
    colorname = get_cmap(colors_name)
    colors = colorname(values)

    #change the width of the axis
    ax.bar3d(xpos,ypos,zpos, 1, 1, dz,   alpha=0.7, zsort='max',color=colors)
    ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([1,0.4, 1, 1]))

    #max_height = np.max(z)   # get range of colorbars
    #min_height = np.min(z)

    ax.bar3d(x_mesh_position.ravel(), y_mesh_position.ravel(),
             z*0, dx=0.2, dy=0.2, dz=z, color=colors, alpha=0.9)
    #dx and dy are are the width and depth of bars

    if add_legend_box:
        Segment1_proxy = plt.Rectangle((0, 0), 1, 1, fc="#FFC04C")
        Segment2_proxy = plt.Rectangle((0, 0), 1, 1, fc="blue")
        Segment3_proxy = plt.Rectangle((0, 0), 1, 1, fc="#3e9a19")

        ax.legend([Segment1_proxy, Segment2_proxy, Segment3_proxy],
                  [legen_labels[0], legen_labels[1], legen_labels[2]])

    return fig



## from barchatd3d.py
def interactive_barchart3d(labels, z_data, title, z_title,
               n_row=0, width=900, height=900, thikness=0.7,
               colorscale='Viridis', **kwargs):
    """
    Draws a 3D barchart
    labels      Array_like of bar labels
    z_data      Array_like of bar heights (data coords)
    title       Chart title
    z_title     Z-axis title
    n_row       Number of x-rows
    width       Chart width (px)
    height      Chart height (px)
    thikness    Bar thikness (0; 1)
    colorscale  Barchart colorscale
    **kwargs    Passed to Mesh3d()

    return 3D barchart figure
    """

    if n_row < 1:
        n_row = math.ceil(math.sqrt(len(z_data)))
    thikness *= 0.5
    ann = []

    fig = go.Figure()

    for iz, z_max in enumerate(z_data):
        x_cnt, y_cnt = iz % n_row, iz // n_row
        x_min, y_min = x_cnt - thikness, y_cnt - thikness
        x_max, y_max = x_cnt + thikness, y_cnt + thikness

        fig.add_trace(go.Mesh3d(
            x=[x_min, x_min, x_max, x_max, x_min, x_min, x_max, x_max],
            y=[y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min],
            z=[0, 0, 0, 0, z_max, z_max, z_max, z_max],
            alphahull=0,
            intensity=[0, 0, 0, 0, z_max, z_max, z_max, z_max],
            coloraxis='coloraxis',
            hoverinfo='skip',
            **kwargs))

        ann.append(dict(
            showarrow=False, x=x_cnt, y=y_cnt, z=z_max,
            text=f'<b>#{iz+1}</b>', font=dict(color='white', size=11),
            bgcolor='rgba(0, 0, 0, 0.3)', xanchor='center', yanchor='middle',
            hovertext=f'{z_max} {labels[iz]}'))

    # mesh3d doesn't currently support showLegend param, so
    # add invisible scatter3d with names to show legend
    for i, label in enumerate(labels):
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            opacity=0,
            name=f'#{i+1} {label}'))

    fig.update_layout(
        width=width, height=height,
        title=title, title_x=0.5,
        scene=dict(
            xaxis=dict(showticklabels=False, title=''),
            yaxis=dict(showticklabels=False, title=''),
            zaxis=dict(title=z_title),
            annotations=ann),
        coloraxis=dict(
            colorscale=colorscale,
            colorbar=dict(
                title=dict(
                    text=z_title,
                    side='right'),
                xanchor='right', x=1.0,
                xpad=0,
                ticks='inside')),
        legend=dict(
            yanchor='top', y=1.0,
            xanchor='left', x=0.0,
            bgcolor='rgba(0, 0, 0, 0)',
            itemclick=False,
            itemdoubleclick=False),
        showlegend=True)
    return fig



## From barchart_latest_m.py
def generate_3dmesh(x_min, x_max, y_min, y_max, z_min, z_max, color_value,
                  flat_shading, hover_info, opacity: float = 1):
    return go.Mesh3d(
        x=[x_min, x_min, x_max, x_max,
            x_min, x_min, x_max, x_max,],
        y=[y_min, y_max, y_max, y_min,
            y_min, y_max, y_max, y_min,],
        z=[z_min, z_min, z_min, z_min,
            z_max, z_max, z_max, z_max,],
        color=color_value,
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        opacity=opacity,
        flatshading=flat_shading,
        hovertext='text',
        hoverinfo=hover_info,)


def create_z_grid(len_x, len_y, z_df):
    z_temp_df = []

    for x, y in itertools.product(range(len_x), range(len_y)):
        if x == y:
            z_temp_df.append(z_df[x])
        else:
            z_temp_df.append(None)
    return z_temp_df

    

def figure_layout(fig: go.Figure, xaxis_legend: str, len_xaxis, yaxis_legend,
                  len_yaxis, x_min, x_title, y_title,  z_legend, z_title,
                  title,):
    y_min = 0
    fig.update_layout(
        scene=dict(xaxis=dict(tickmode='array', ticktext=xaxis_legend,
                              tickvals=np.arange(x_min, len_xaxis * 2, step=2),
                              title=x_title,),
                   yaxis=dict(tickmode='array', ticktext=yaxis_legend,
                              tickvals=np.arange(y_min, len_yaxis * 2, step=2),
                              title=y_title,),
                   zaxis=dict(title=z_title),),
                   )

    if z_legend is None:
        fig.update_layout(
            scene=dict(zaxis=dict(tickmode='array', ticktext=z_legend,
                                  title=z_title,),), template='plotly_white',
                         )

    fig.update_layout(title=dict(text=title,x=0.5,y=0.950,
                      font=dict(size=25,family="Arial", color='black')))
    return fig



def bar_charts3d_categorical(x, y, z, x_min=0, y_min=0, z_min='auto',
                            step=1, color='x', x_legend='auto', y_legend='auto',
                            z_legend='auto', flat_shading=True, x_title='',
                            y_title='', z_title='', hover_info='z',
                            title='',opacity_val=0.9,) -> go.Figure:

    # Load data as Series
    x_values, y_values, z_values = pd.Series(x), pd.Series(y), pd.Series(z)

    # Extract labels and numbers of labels
    x_labels = x_values.unique()
    y_labels = y_values.unique()
    len_x_labels = len(x_labels)
    len_y_labels = len(y_labels)

    # Generic parameters for mesh
    colormap = px.colors.qualitative.Prism #Plotly
    curr_color = 0

    # Based on idx from pd.Series of z (set to -1 to have 0)
    # add 1 at each loop to have corresponding z-value to x and y
    z_idx_count = -1

    if z_min == 'auto':
        z_min = 0.5 * min(z_values)

    # Generate mesh for x,y and associated z-value with colors
    curr_mesh = []
    for idx_x, x_label in enumerate(x_labels):
        if color == 'x':
            curr_color = colormap[idx_x % 9]
        for idx_y, y_label in enumerate(y_labels):
            z_idx_count += 1
            if color == 'x+y':
                curr_color = colormap[(idx_x + idx_y * len_y_labels) % 9]
            elif color == 'y':
                curr_color = colormap[idx_y % 9]

            x_max = x_min + step
            y_max = y_min + step
            z_max=z_values[z_idx_count]

            curr_mesh.append(generate_3dmesh(x_min, x_max, y_min, y_max,
                                             z_min, z_max, curr_color,
                                             flat_shading, hover_info,
                                             opacity=opacity_val),)
            x_min += 2 * step
        y_min += 2 * step
        x_min = 0

    # Set legends of 3d layout axis
    if x_legend == 'auto':
        x_legend = [str(xlab) for xlab in x_labels]
    if y_legend == 'auto':
        y_legend = [str(ylab) for ylab in y_labels]
    if z_legend == 'auto':
        z_legend = None

    # Generate figure based on mesh
    fig = go.Figure(curr_mesh)

    # Update layout scene for legends
    fig = figure_layout(fig, y_legend, len_y_labels, x_legend, len_x_labels,
                         x_min, x_title, y_title,  z_legend,
                        z_title, title,)
    return fig


def plots_3d_scatter(df, xcol, ycol, zcol, xlabel, ylabel, zlabel):

    sns.set(style = "whitegrid")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')

    x, y, z = df[xcol], df[ycol], df[zcol]

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

    ax.scatter(x, y, z)

    return fig, ax


def get_slider_dict_for_3dvolume(z_length, use_prefix='', start_at=1):
    return [dict(
        steps=[dict(
            method='animate',
            args=[[f'frame{single_slice+1}'],
                  dict(mode='immediate',
                       frame=dict(duration=10, redraw=True),
                       transition=dict(duration=0))],
            label=f'{single_slice+1}') 
            for single_slice in range(int(start_at), z_length)],
        active=17, transition=dict(duration=0), x=0, y=0,
        currentvalue=dict(font=dict(size=12), prefix=use_prefix + ': ',
                          visible=True, xanchor='center'),
        len=1.0)]


def frame_arguments(duration):
    return {"frame": {"duration": duration}, "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"}, }


def generate_3d_volume(volume, z_max, z_n_slices, z_step, x_size, y_size,
                       colorname, title='', start_at=1, add_buttons=True,
                       prefix_slider='z slice',  show_scale=False):

    # Create initial surface grid corresponding to image size and color
    init_surface = go.Surface(z=z_max*np.ones((x_size, y_size)),
                              surfacecolor=np.flipud(volume[-1]),
                              colorscale=colorname, showscale=show_scale)

    # Create frame from data
    set_frames = [go.Frame(
        data=[dict(type='surface', 
                   z=z_max-curr_slice*z_step * np.ones((x_size, y_size)),
                   surfacecolor=np.flipud(volume[-1-curr_slice]))],
        name=f'frame{curr_slice+1}')
                for curr_slice in range(int(start_at), z_n_slices)]

    # Interactive view configuration
    slider_dict = get_slider_dict_for_3dvolume(z_n_slices, prefix_slider, 
                                               start_at)

    # Create layout with slicer for interactive view
    set_layout = dict(title_text=title, title_x=0.5, width=900, height=700,
                         sliders=slider_dict)

    # Generate 3D figure
    fig = go.Figure(data=[init_surface], layout=set_layout, frames=set_frames)

    # Axis parameters
    set_axis = dict(showaxeslabels=True, showbackground=False,
                    showgrid=False, gridwidth=1, gridcolor='black',
                    tickfont=dict(color='white', size=1))

    z_axis = dict(showaxeslabels=True, showbackground=False,
                  showgrid=False, gridwidth=1, gridcolor='black',
                  tickfont=dict(color='white', size=1),
                  range=[-0.1, z_max], autorange=False)

    # Update 3D figure with parameters
    fig.update_layout(scene=dict(zaxis=z_axis, yaxis=set_axis,
                                 xaxis=set_axis, bgcolor='white',
                                 aspectratio=dict(x=1, y=1.2, z=1)),
                      plot_bgcolor='rgb(255,255,255)',
                      scene_camera=dict(up=dict(x=0, y=0, z=0),
                                        eye=dict(x=0, y=0, z=1.5)))

    # Add Menu with play and stop buttons
    if add_buttons:
        fig.update_layout(updatemenus=[
                {"buttons": [{"args": [None, frame_arguments(0)],
                              "label": "&#9654;",  # play symbol
                              "method": "animate",},
                            {"args": [[None], frame_arguments(0)],
                             "label": "&#9724;",  # stop symbol
                             "method": "animate",},
                             ],
                 "direction": "left",
                 "pad": {"r": 10, "t": 70},
                 "type": "buttons", "x": 0.1, "y": 0,}],
                          sliders=slider_dict)

    return fig