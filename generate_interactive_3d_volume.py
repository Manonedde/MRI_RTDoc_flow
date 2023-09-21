#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate an interactive visualization of MRI images.
It's best to crop the images first.


List of available colors: Blackbody, Bluered, Blues, Vividis, Earth, Electric,
                          Greens, Hot, Jet, Picnic, Rainbow, RdBu, Reds,
                          Viridis, YlGnBu, YlOrRd.

"""

import argparse
import os

import nibabel as nib
import numpy as np
import plotly
import plotly.graph_objects as go

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from scilpy.utils.filenames import split_name_with_nii


def _build_arg_parser():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)

    p.add_argument('in_image',
                   help='Brain MRI image.')

    p.add_argument('--out_html',
                   help='Output html filename.')
    p.add_argument('--out_dir',
                   help='Output directory to save html page.')

    visu = p.add_argument_group(title='visualization options')
    visu.add_argument('--title', default='Brain MRI',
                      help='Use the provided info for the histogram title.'
                           ' [%(default)s]')
    visu.add_argument('--colormap', default='Greys',
                      help='Use to display brain maps according to a '
                           'specific colormap using the list of possible '
                           'colormaps provided. [%(default)s]')
    visu.add_argument('--add_buttons', action='store_true',
                      help='Add two buttons play and stop to the scroll bar. ')


    p.add_argument('--show_only', action='store_true',
                   help='Do not save the figure, only display.')


    add_overwrite_arg(p)

    return p


def frame_arguments(duration):
    return {"frame": {"duration": duration}, "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"},}


def main():
    p = _build_arg_parser()
    args = p.parse_args()

    assert_inputs_exist(p, args.in_image)

    if args.out_dir is None:
        args.out_dir = './'

    if args.out_html is None:
        args.out_html = split_name_with_nii(os.path.basename(args.in_image))[0]

    # load image
    volume = nib.load(args.in_image).get_fdata().T

    # Define parameters for grid
    x_size, y_size = volume[0].shape
    z_slices = volume.shape[0]
    rescale_max_z = (volume.shape[0]-1) / 10
    grid = np.linspace(0, rescale_max_z, z_slices)
    z_step = grid[1] - grid[0]

    # Define custom colorscale for brain
    if args.colormap is None :
        args.colormap=[[0.0, 'rgb(0, 0, 0)'],[0.05, 'rgb(10, 10, 14)'],
                       [0.1, 'rgb(21, 21, 30)'],[0.15, 'rgb(33, 33, 46)'],
                       [0.2, 'rgb(44, 44, 62)'],[0.25, 'rgb(56, 55, 77)'],
                       [0.3, 'rgb(66, 66, 92)'],[0.35, 'rgb(77, 77, 108)'],
                       [0.4, 'rgb(89, 92, 121)'],[0.45, 'rgb(100, 107, 132)'],
                       [0.5, 'rgb(112, 123, 143)'], [0.55, 'rgb(122, 137, 154)'],
                       [0.6, 'rgb(133, 153, 165)'],[0.65, 'rgb(145, 169, 177)'],
                       [0.7, 'rgb(156, 184, 188)'],[0.75, 'rgb(168, 199, 199)'],
                       [0.8, 'rgb(185, 210, 210)'], [0.85, 'rgb(203, 221, 221)'],
                       [0.9, 'rgb(220, 233, 233)'],[0.95, 'rgb(238, 244, 244)'],
                       [1.0, 'rgb(255, 255, 255)']]

    # Create initial surface grid corresponding to image size and color
    init_surface = go.Surface(z = rescale_max_z*np.ones((x_size, y_size)),
                              surfacecolor = np.flipud(volume[-1]),
                              colorscale = args.colormap,
                              showscale = False)

    # Create frame from data
    set_frames = [go.Frame(data = [dict(type ='surface',
                           z = (rescale_max_z-curr_slice*z_step)*np.ones((x_size, y_size)),
                           surfacecolor = np.flipud(volume[-1-curr_slice]))],
                  name = f'frame{curr_slice+1}')
                  for curr_slice in range(1, z_slices)]

    # Interactive view configuration
    set_slider = [dict(steps = [dict(method = 'animate',
                                args = [[f'frame{curr_slice+1}'],
                                        dict(mode = 'immediate',
                                        frame = dict(duration = 10, redraw = True),
                                        transition = dict(duration = 0))],
                                label = f'{curr_slice+1}')
                                for curr_slice in range(z_slices)],
                       active = 17,
                       transition = dict(duration = 0 ), x = 0, y = 0,
                       currentvalue = dict(font = dict(size = 12),
                                         prefix ='z slice: ',
                                         visible = True,
                                         xanchor = 'center'),len = 1.0)]

    # Create layout with slicer for interactive view
    set_3d_layout = dict(title_text = args.title, title_x = 0.5,
                         width = 900, height = 700,
                         sliders = set_slider)

    # Generate 3D figure
    fig = go.Figure(data = [init_surface], layout = set_3d_layout,
                    frames = set_frames)

    # Point of view parameters
    camera = dict(up = dict(x = 0, y = 0, z = 0),
                  eye = dict(x = 0, y = 0, z = 1.5))

    # Axis parameters
    set_axis = dict(showaxeslabels = True, showbackground = False,
                    showgrid = False, gridwidth = 1, gridcolor = 'black',
                    tickfont = dict(color = 'white',size = 1))

    z_axis = dict(showaxeslabels = True, showbackground = False,
                    showgrid = False, gridwidth = 1, gridcolor = 'black',
                    tickfont = dict(color = 'white', size = 1),
                    range=[-0.1, rescale_max_z], autorange=False)

    # Update 3D figure with parameters
    fig.update_layout(scene = dict(zaxis = z_axis, yaxis = set_axis,
                                 xaxis = set_axis, bgcolor ='white',
                                 aspectratio=dict(x=1, y=1.2, z=1)),
                      plot_bgcolor = 'rgb(255,255,255)',
                      scene_camera = camera)

    # Add Menu with play and stop buttons
    if args.add_buttons:
        fig.update_layout(
                 updatemenus = [
                    {
                        "buttons": [
                            {
                                "args": [None, frame_arguments(0)],
                                "label": "&#9654;", # play symbol
                                "method": "animate",
                            },
                            {
                                "args": [[None], frame_arguments(0)],
                                "label": "&#9724;", # stop symbol
                                "method": "animate",
                            },
                        ],
                        "direction": "left",
                        "pad": {"r": 10, "t": 70},
                        "type": "buttons",
                        "x": 0.1,
                        "y": 0,
                    }
                 ],
                 sliders=set_slider)


    # Show or save html page
    if args.show_only:
        fig.show()
    else:
        fig.write_html(os.path.join(args.out_dir,args.out_html + '.html'))

if __name__ == "__main__":
    main()
