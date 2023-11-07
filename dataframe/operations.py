#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict

import pandas as pd
import numpy as np


def get_df_ops():
    """Get a dictionary of all functions relating to dataframe operations"""
    return OrderedDict([
        ('display_df', display_df),
        ('list_column', list_column),
        ('list_unique_from', list_unique_from),
        ('check_empty', check_empty),
        ('drop_empty_column', drop_empty_column),
        ('drop_nan', drop_nan),
        ('average_data', average_data),
        ('query', get_query),
        ('upper_values', upper_values),
        ('lower_values', lower_values),
        ('exclude_values', exclude_values),
        ('apply_factor', apply_factor),
        ('select_values', select_values)])

def get_operations_doc(ops: dict):
    """From a dictionary mapping operation names to functions, fetch and join
    all documentations, using the provided names."""
    full_doc = []
    for func in ops.values():
        full_doc.append(func.__doc__)
    return "".join(full_doc)



def _validate_type(dtype1: type, dtype2: type):
    """Make sure that the inputs are in the same type."""
    if dtype1 != dtype2:
        raise ValueError('Type of your value not correspond to the column '
                         'dtype.')


def display_df(df):
    """ Print head of Dataframe """
    return print(df.head())


def list_column(df):
    """ Return the list of columns dataframe"""
    return df.columns.tolist()


def list_unique_from(df, column_name: str):
    """ Return list of unique argument in specific column. """
    return  df[column_name].unique().tolist()


def check_empty(df):
    """ Check and return a list of column with Nan value. """
    empty_col = []
    for column in df:
        if df[column].isnull().any():
            print('{} has {} ({}%) null values'.format(
                                column, df[column].isnull().sum(),
                                df[column].isnull().sum()/len(df)*100))
            empty_col.append(column)
    return empty_col


def drop_empty_column(df):
    """ Remove columns where all rows are NaN. """
    empty_columns = check_empty(df)
    return df.drop(empty_columns, axis = 1).reset_index(drop=True)


def drop_nan(df):
    """ Remove all columns and rows with NaN values. """
    df_nona = df.drop(df.columns[df.isnull().sum()>len(df.columns)],axis = 1)
    df_nona = df_nona.dropna(axis = 0, how='any').reset_index(drop=True)
    return df, df_nona


def average_data(df, column_list: list, column_value: str):
    """ Regroup dataframe based on column list and column value using mean().
    By default, df is average for subject column and assuming that first
    column is subjects.

    df:             Dataframe
    column_list:    List of column name considered to compute mean.
                    Must be not include column with NaN data.
    column_value:      Column name for compute average value

    Return          Dataframe
    """
    if len(check_empty(df)) > 0:
        raise ValueError('Remove column(s) with NaN value.')
    return df.groupby(column_list)[column_value].mean().reset_index()


def sum_data(df, column_list: list, column_value: str):
    """ Regroup dataframe based on column list and column value suing sum().
    Design to sum volume or count for example.

    df:             Dataframe
    column_list:    List of column name considered to compute mean.
                    Must be not include column with NaN data.
    column_value:      Column name for compute average value

    Return          Dataframe
    """
    if len(check_empty(df)) > 0:
        raise ValueError('Remove column(s) with NaN value.')

    return df.groupby(column_list)[column_value].sum().reset_index()


def apply_factor(df, column, row, column_value, factor):
    """ Apply a factor to specific row in column."""
    tmp = df[(df[column] == row)]
    if tmp.empty is True:
        raise ValueError('No data are found.')
    else:
        df.loc[(df[column] == row), column_value] = tmp[column_value] * factor


def get_data_where(df, column_name: str, string_arg: str):
    """
    Function to extract rows based on string from one column using 
    str.contains.() function.

    df:             Dataframe
    column_name:    Column name
    row_arg:        String. Could be part of or full string.

    Returns a df where each row of a column contains part or all of the string
    structure.
    """
    return df[df[column_name].str.contains(string_arg)].reset_index(drop=True)


def get_data_from(df, column_name: str, row_args):
    """
    Function to extract some rows from one column using isin.() function.

    df:             Dataframe
    column_name:    Column name
    row_args:       List of string or int/float argument.

    Return Dataframe corresponding to list of arguments.
    """
    return df.loc[df[column_name].isin(row_args)].reset_index(drop=True)


def get_query(df, args_dict: dict(), remove=False, op_value=''):
    """
    Function which use .query() method to get a subset
    dataframe from larger Dataframe.

    df:         Dataframe
    args_dict:  Dictionary of {column_name: value(s)}.
                Key must correspond to column name and value(s) correspond to
                one or multiple row argument(s), could be string or int/float.
                To include multiple criteria for value use a list.
                {'column_name1': value, 'column_name2': ['arg1', 'argN'],
                'column_nameN': "string"}
    remove:     If True, it will remove the rows corresponding to argument
                listed in dictionary.
    op_value:   Must be mathematical symbol like > or <.

    Return Dataframe corresponding to the arguments listed in dictorionnary.
    """
    if remove:
        query_from_dict = ' and '.join(
            [f'({col} != "{row}")' if type(row) == str else f'({col} != {row})'
             for col, row in args_dict.items()])
    elif op_value is not None:
        query_from_dict = ' and '.join(
            [f'{col} == "{row}"' if type(
                row) == str else f'{col} {op_value} {row}'
             for col, row in args_dict.items()])
    else:
        query_from_dict = ' and '.join(
            [f'({col} == "{row}")' if type(row) == str else f'({col} == {row})'
             for col, row in args_dict.items()])

    return df.query(query_from_dict).reset_index(drop=True)


def merged_col_csv(df1, df2, label1: str, label2: str, colname: str):
    """
    Merged two dataframe based on column.
    :param df1:
    :param df2:
    :param label1:
    :param label2:
    :param colname:
    :return:
    """
    df1[colname] = label1
    df2[colname] = label2
    return pd.concat([df1, df2], ignore_index=True, sort=False)


def lower_values(df, column_name: str, threshold):
    """
    Remove values lower to threshold.
    df:                 Dataframe
    column_name:        Name of column on which filter is applied.
    set_value:          Value used to filter the column.    
    Return:             Dataframe.
    """
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] > threshold].reset_index(drop=True)


def upper_values(df, column_name: str, threshold):
    """
    Remove values upper to threshold.
    df:                 Dataframe
    column_name:        Name of column on which filter is applied.
    set_value:          Value used to filter the column.    
    Return:             Dataframe.
    """
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] < threshold].reset_index(drop=True)


def exclude_values(df, column_name: str, threshold):
    """
    Remove values not equal to threshold.
    df:                 Dataframe
    column_name:        Name of column on which filter is applied.
    set_value:          Value used to filter the column.    
    Return:             Dataframe.
    """
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] != threshold].reset_index(drop=True)


def select_values(df, column_name: str, threshold):
    """Select all row of column equal to threshold.
    df:                 Dataframe
    column_name:        Name of column on which filter is applied.
    set_value:          Value used to filter the column.    
    Return:             Dataframe.
    """
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] == threshold].reset_index(drop=True)


def merged_on(df, column_list: list, args_dict: dict, volume=False):
    """
    Function to merge left and right data. By default, mean() function is use to average left and right data. Use Volume option to use sum() function for volume or count for example.
    column_list must include :
    [column_to_replace, column_list_include_for_merged, column_numeric].
    """
    # replace dict on roi columns
    df[column_list[0]] = df[column_list[0]].replace(args_dict, regex=True)

    if volume:
        return sum_data(df, column_list[1:-1], column_list[-1])
    else:
        return average_data(df, column_list[1:-1], column_list[-1])

