#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def generate_reorder_list(df, ordered_argument_list, with_column):
    """
    Function to generate a list of new columns name list corresponding
    to column of dataframe and based on argument list. 
    This function is mainly used to generate a list of column names to reorganize the columns of a dataframe  (index x N columns). For example, a connectivity matrix or a dataframe in wide-format.

    df:                       Dataframe
    with_column:              Column name. Used to return unique column values. 
    ordered_argument_list:    List of arguments used as unique values.

    Return  List of column names corresponding to the argument list and unique value of column.
    
    """
    reorder_columns_list = []
    for given_arg in ordered_argument_list:
        for unique_in_col in df[with_column].unique():
            reorder_columns_list.append(given_arg + '_' + unique_in_col)
    return 



def save_figures_as(fig, out_path, out_name, is_slider=False, 
                    save_as_png=False):
    """
    Function to save figures as HTML or PNG files. By default, figure is saved  in HTML.

    fig:            Figure structure.
    out_path:       Output path to save figure.
    out_name:       Output name to save figure without extension.
    is_slider:      If True display a warning message.
    save_as_png:    Save the figure as a PNG file. 
    """
    if save_as_png:
        if is_slider:
            print("With PNG you don't have access to the "
                  "slider option.\n")
        fig.write_image(os.path.join(out_path, out_name  + '.png'))
    else:
        fig.write_html(os.path.join(out_path, out_name  + '.html'))

