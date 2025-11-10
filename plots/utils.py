#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Set of functions used to prepare data for plotly figures.
"""

import os
import plotly.express as px


def generate_reorder_list(df, ordered_argument_list, with_column):
    """
    Function to generate a list of new columns name list corresponding
    to column of dataframe and based on argument list. 
    This function is mainly used to generate a list of column names to
    reorganize the columns of a dataframe  (index x N columns). 
    For example, a connectivity matrix or a dataframe in wide-format.

    df:                       Dataframe
    with_column:              Column name. Used to return unique column values. 
    ordered_argument_list:    List of arguments used as unique values.

    Return  List of column names corresponding to the argument list and
            unique value of column.

    """
    reorder_columns_list = []
    for given_arg in ordered_argument_list:
        for unique_in_col in df[with_column].unique():
            reorder_columns_list.append(given_arg + '_' + unique_in_col)
    return reorder_columns_list


def save_figures_as(fig, out_path, out_name, is_slider=False,
                    save_as_png=False, dpi_scale=6, heigth_value=1000,
                    width_value=1000, play=False):
    """
    Function to save figures as HTML or PNG files. 
    By default, figure is saved  in HTML without auto play.

    fig:            Figure structure.
    out_path:       Output path to save figure.
    out_name:       Output name to save figure without extension.
    is_slider:      If True display a warning message.
    save_as_png:    Save the figure as a PNG file. 
    dpi_scale:      PNG file resolution.
    heigth_value:   Heigth to save PNG file
    width_value:    Width to save PNG file.
    play:           Option to play automatically or not the slider.

    Return  HTML or PNG file 
    """
    if save_as_png:
        if is_slider:
            print("With PNG you don't have access to the slider option.\n")
        fig.write_image(os.path.join(out_path, out_name + '.png'),
                        scale=dpi_scale, heigth=heigth_value, width=width_value)
    else:
        fig.write_html(os.path.join(out_path, out_name + '.html'),
                       auto_play=play)


def check_df_for_columns(df, split_filter=None, profile=None):
    """
    Function that checks the presence or absence of some columns and the
    compatibility of parameters used by the script.

    df:         DataFrame
    parameters: Dictionary. parameters used by the script
    use_data:   If None, display a warning message.

    """
    if not profile:
        if 'Section' in df.columns.tolist():
            raise ValueError('The csv contains a section column.\n'
                            'This script only deals with average measurements.')

    if 'Method' not in df.columns.tolist():
        raise ValueError("The csv not contains Method column. "
                         "\nRename column or add it.")

    if len(df.Method.unique().tolist()) > 1 and split_filter is None and df.Method.unique().tolist()[0] != 'Streamlines':
        raise ValueError('Multiple method categories are found in csv files.\n'
                        'Please provide a csv file containing single Method'
                        'or use --specific_method or --split_by options.')

    if len(df.Statistics.unique().tolist()) > 1:
        if not ('count' or 'mean' or 'volume') in df.Statistics.unique().tolist():
            raise ValueError('Multiple statistics are found in csv files.\n '
                            'Please provide a csv file containing single Statistic'
                            ' or use --specific_stats options.')


def check_item_in_dict(df, check_column, dict_parameters, use_data=False):
    if df[check_column].unique().tolist()[0] not in dict_parameters:
        if use_data is None:
            raise ValueError('No match is found in default parameter.\n '
                             'Please use --use_data option or use '
                             '--custom_* options to provide specific '
                             'information.')


def check_agreement_with_dict(df, check_column, input_parameters,
                              rm_missing=False, ignore_lenght=False):
    """
    Checks whether there is a match between a dictionary or parameter list and a
    list of the unique elements of the selected column in the database. 
    To remove items not listed in the default parameters, use the rm_missing
    option, otherwise use the custom* options. 
    To ignore the length check, set ignore_length to True.
    This is the case for bundle color dictionaries, for example. 

    df:                     DataFrame
    check_column:           Column name to check.
    input_parameters:       List or dict of items/parameters
    rm_missing:             Boolean. If True the missing items in dataframe
                            are removed.
    ignore_lenght:          Check if the length of the check_column and
                            input_parameters are equal.
                            Set to True to ignore object length.

    Return                  Error message /or
                            The Dataframe without missing items if
                            rm_missing is True.
    """
    missing_items = []
    for curr_item in df[check_column].unique():
        if curr_item not in input_parameters:
            missing_items.append(curr_item)

    if not missing_items:
        if (len(input_parameters) != len(df[check_column].unique().tolist())
                and ignore_lenght is False):
            raise ValueError('No missing items are detected, but the number'
                             ' of default items and that of the dataframe'
                             ' do not match.\nUse --custom_* options to parse'
                             ' a custom list. For bundle colors put '
                             'ignore_lenght at True.')
        else:
            return df

    if len(missing_items) != 0:
        if rm_missing:
            print("With the --filter_missing option the following elements"
                  " are removed:\n", missing_items)
            return df.loc[~(df[check_column].isin(
                missing_items))].reset_index(drop=True)
        else:
            raise ValueError('The listed items in dataframe do not match'
                             ' with the default item list:\n', missing_items,
                             '\nUse --custom_* options to parse a custom'
                             ' list or --filter_missing to remove missing'
                             ' items.')


def add_ols_info(data):
    """
    Returns a string (for html) of alpha, beta and R-squared values obtained
    from a linear regression of type y=ax+b, R^2.
    """
    return 'y = {}x + {}<br>R<sup>2</sup> = {}'.format(str(round(data[1], 2)),
                                                       str(round(data[0], 2)),
                                                       str(round(data[2], 2)))


def fetch_ols_results(fig, return_all=False):
    """
    Function for extracting trend information from a figure.

    fig:         Figure structure
    return_all : if True, returns the OLS output structure.
                 Use print(val) to display it.

    Returns alpha, beta and R-squared parameters from OLS.
    """
    trend_results = px.get_trendline_results(fig)
    ols_parameters = [trend_results.iloc[0]['px_fit_results'].params[0],
                      trend_results.iloc[0]['px_fit_results'].params[1],
                      trend_results.iloc[0]["px_fit_results"].rsquared]
    if return_all:
        return trend_results
    else:
        return ols_parameters


def save_trend_from_plot(results, outpath='./', outname='', save_as='txt'):
    """
    Function to save the results in .csv or .txt format of a linear regression
    performed with OLS.

    results:    Results structure from OLS.
    outpath:    Path to output folder.
    outname:    Name to save file.
    save_as:    Format to save file (.csv or .txt).

    Save file in .csv or .txt. 
    """
    for n_result in range(len(results)):
        if outname == '':
            outname = 'trend_summary_' + str(n_result) + '.' + save_as
        else:
            outname = outname + str(n_result) + '.' + save_as
        if save_as == 'txt':
            with open(os.path.join(outpath, outname), 'w') as files:
                files.write(
                    results.px_fit_results.iloc[n_result].summary().as_text())
        elif save_as == 'csv':
            with open(os.path.join(outpath, outname), 'w') as files:
                files.write(
                    results.px_fit_results.iloc[n_result].summary().as_csv())

