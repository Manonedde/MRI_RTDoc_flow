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


def _validate_length_column(column_list, length, min_length=False):
    """Make sure that the number of column in the list match to the expected
    number."""
    if len(column_list) != length:
         if len(column_list) < length and not min_length:
            raise ValueError('This operation requires at least {}'
                             ' column(s).'.format(length))
         else:
              raise ValueError('This operation requires {} column(s).'.format(
                                                                      length))


def _validate_type(dtype1: type, dtype2: type):
    """Make sure that the inputs are in the same type."""
    if dtype1 != dtype2:
        raise ValueError('Type of your value not correspond to the column '
                         'dtype.')


def display_df(df):
    """
    display_df: DF
        Print head of Dataframe.
    """
    return print(df.head())


def list_column(df):
    """
    list_column: DF
        Return the list of columns dataframe.
    """
    return df.columns.tolist()


def check_empty(df):
    """
    check_empty: DF
        Check and return a list of column with Nan value.
    """
    empty_col = []
    for column in df:
        if df[column].isnull().any():
            print('{} has {} ({}%) null values'.format(
                                column, df[column].isnull().sum(),
                                df[column].isnull().sum()/len(df)*100))
            empty_col.append(column)
    return empty_col


def drop_empty_column(df):
    """
    drop_empty_column: DF
        Remove columns where all rows are NaN.
    """
    empty_columns = check_empty(df)
    return df.drop(empty_columns, axis = 1).reset_index(drop=True)


def drop_nan(df):
    """
    drop_nan: DF
        Remove all columns and rows with NaN values.
    """
    df_nona = df.drop(df.columns[df.isnull().sum()>len(df.columns)],axis = 1)
    df_nona = df_nona.dropna(axis = 0, how='any').reset_index(drop=True)
    return df, df_nona


def list_unique_from(df, column_name: str):
    """
    list_unique_from: DF
        Return list of unique argument in specific column.
    """
    _validate_length_column([column_name], 1)
    return  df[column_name].unique().tolist()


def lower_values(df, column_name: str, threshold):
    """
    lower_values: DF COLUMN_NAME THRESHOLD
        Values below the threshold will be remove.
    """
    _validate_length_column([column_name], 1)
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] > threshold].reset_index(drop=True)


def upper_values(df, column_name: str, threshold):
    """
    upper_values: DF COLUMN_NAME THRESHOLD
        Values above the threshold will be remove.
    """
    _validate_length_column([column_name], 1)
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] < threshold].reset_index(drop=True)


def exclude_values(df, column_name: str, threshold):
    """
    exclude_values: DF COLUMN_NAME THRESHOLD
        Values equal to the threshold will be remove.
    """
    _validate_length_column([column_name], 1)
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] != threshold].reset_index(drop=True)


def select_values(df, column_name: str, threshold):
    """
    select_values: DF COLUMN_NAME THRESHOLD
        Values not equal to the threshold will be remove.
        Values equl to the threshold will be save.
    """
    _validate_length_column([column_name], 1)
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] == threshold].reset_index(drop=True)


def average_data(df, column_list: list, column_value: str):
    """
    average_data: DF COLUMNS_LIST COLUMN_NUMERIC
        Average the values in numeric column according to the columns in the
        list.
    """
    _validate_length_column([column_value], 1)
    _validate_length_column(column_list, 1, min_n=True)
    if len(check_empty(df)) > 0:
        raise ValueError('Remove column(s) with NaN value.')
    return df.groupby(column_list)[column_value].mean().reset_index()


def sum_data(df, column_list: list, column_value: str):
    """
    sum_data: DF COLUMNS_LIST COLUMN_NUMERIC
        Sum the values in numeric column according to the columns in the list.
        Design to sum volume or count for example.
    """
    _validate_length_column([column_value], 1)
    _validate_length_column(column_list, 1, min_n=True)
    if len(check_empty(df)) > 0:
        raise ValueError('Remove column(s) with NaN value.')
    return df.groupby(column_list)[column_value].sum().reset_index()


def apply_factor(df, column_list: list, row_arg, factor):
    """
    apply_factor: DF COLUMNS_LIST ROW_ARG FACTOR
        Apply a factor (multiplication) to the numeric column for specific
        rows in a specific column.
        COLUMNS_LIST = [COLUMN_NAME, NUMERIC_COLUMN]
    """
    _validate_length_column(column_list, 2)
    tmp = df[(df[column_list[0]] == row_arg)]
    if tmp.empty is True:
        raise ValueError('No data are found.')
    else:
        df.loc[(df[column_list[0]] == row_arg),
               column_list[1]] = tmp[column_list[1]] * factor


def get_data_where(df, column_name: str, string_arg: str):
    """
    get_data_from: DF COLUMN_NAME ROW_ARGS
        Selects all rows if the given pattern is contained in the string of
        each element of a specific column.
    """
    _validate_length_column([column_name], 1)
    return df.loc[df[column_name].str.contains(string_arg)
                  ].reset_index(drop=True)


def get_data_from(df, column_name: str, row_args):
    """
    get_data_from: DF COLUMN_NAME ROW_ARGS
        Selects rows with one or multiple specific value(s) in a specific
        column.
    """
    _validate_length_column([column_name], 1)
    return df.loc[df[column_name].isin(row_args)].reset_index(drop=True)


def get_query(df, args_dict: dict(), remove=False, op_value=''):
    """
    get_query: DF DICT [OPTIONS]
        Get a subset dataframe from larger Dataframe using dictionary.
        OPTIONS : remove: Boolean, operation_value (<, >).
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


def merged_on(df, column_list: list, args_dict: dict, volume=False):
    """
    merged_on: DF COLUMNS_LIST DICT OPTION
        Replace values based on dict and average data on column list.
        COLUMN_LIST : [column_to_replace_dict, 
                       column_list_include_for_merged, 
                       column_numeric]

        By default, mean() function is use to average data.
        Use OPTION to use sum() function for volume or count for example.
    """
    _validate_length_column(column_list[1:-1], 1, min_n=True)

    if len(check_empty(df)) > 0:
        raise ValueError('Remove column(s) with NaN value.')

    df[column_list[0]] = df[column_list[0]].replace(args_dict, regex=True)

    if volume:
        return sum_data(df, column_list[1:-1], column_list[-1])
    else:
        return average_data(df, column_list[1:-1], column_list[-1])


def merged_col_csv(df1, df2, label1: str, label2: str, colname: str):
    """
    Merged two dataframe based on column. Not used new, will see
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