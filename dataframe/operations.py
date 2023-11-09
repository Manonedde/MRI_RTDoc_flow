#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict

import pandas as pd
import numpy as np


def get_df_ops():
    """Get a dictionary of all functions relating to dataframe operations"""
    return OrderedDict([
        ('display', display),
        ('list_column', list_column),
        ('unique', unique),
        ('check_empty', check_empty),
        ('drop_empty_column', drop_empty_column),
        ('drop_nan', drop_nan),
        ('remove_column', remove_column),
        ('upper', upper),
        ('lower', lower),
        ('exclude', exclude),
        ('select', select),
        ('get_from', get_from),
        ('get_where', get_where),
        ('remove_row_with', remove_row_with),
        ('average_on', average_on),
        ('sum_on', sum_on),
        ('replace', replace),
        ('apply_factor', apply_factor),
        ('query', get_query),
        ('merged_on', merged_on)])


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
    if min_length:
        if not len(column_list) >= length:
            raise ValueError('This operation requires at least {}'
                                ' column(s).'.format(length))
    else:
        if len(column_list) != length:
            raise ValueError('This operation requires {} '
                             'column(s).'.format(length))


def _validate_type(dtype1: type, dtype2: type):
    """Make sure that the inputs are in the same type."""
    if dtype1 != dtype2:
        raise ValueError('Type of your value not correspond to the column '
                         'dtype.')


def display(df):
    """
    display_df:         DF
                        Print Dataframe.
    """
    return print(df)


def list_column(df):
    """
    list_column:        DF
                        Print the list of columns dataframe.
    """
    return print(df.columns.tolist())


def check_empty(df):
    """
    check_empty:        DF
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
    drop_empty_column:  DF
                        Remove columns where all rows are NaN.

    """
    empty_columns = check_empty(df)
    df = df.drop(empty_columns, axis = 1).reset_index(drop=True)
    return df


def drop_nan(df):
    """
    drop_nan:           DF
                        Remove all columns and rows with NaN values.

    """
    df_nona = df.drop(df.columns[df.isnull().sum()>len(df.columns)],axis = 1)
    df_nona = df_nona.dropna(axis = 0, how='any').reset_index(drop=True)
    return df_nona


def remove_column(df, column_name: str):
    """
    remove_column:      DF COLUMN_NAME
                        Usage : --my_cols

                        Remove column.

    """
    _validate_length_column([column_name], 1)
    return df.drop(column_name, axis = 1)


def remove_row_with(df, column_name: list, string_arg: str):
    """
    remove_row_with:    DF COLUMNS_NAME PATTERN_row
                        Usage : --my_cols --pattern

                        Remove all rows corresponding to the pattern
                        for a specific column.

    """
    _validate_length_column([column_name], 1)
    return df.loc[~(df[column_name] == string_arg)].reset_index(drop=True)


def unique(df, column_name: str):
    """
    unique:         DF COLUMN_NAME
                    Usage : --my_cols

                    Return list of unique argument in specific column.

    """
    _validate_length_column([column_name], 1)
    return  df[column_name].unique().tolist()


def lower(df, column_name: str, threshold):
    """
    lower:      DF COLUMN_NAME THRESHOLD
                Usage : --my_cols --value

                Values below the threshold will be remove.

    """
    _validate_length_column([column_name], 1)
    _validate_type(df[column_name].values.dtype, type(threshold))
    return df[df[column_name] > threshold].reset_index(drop=True)


def upper(df, column_name: str, threshold):
    """
    upper:      DF COLUMN_NAME THRESHOLD
                Usage : --my_cols --value

                Values above the threshold will be remove.

    """
    _validate_length_column([column_name], 1)
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] < threshold].reset_index(drop=True)


def exclude(df, column_name: str, threshold):
    """
    exclude:    DF COLUMN_NAME THRESHOLD
                Usage : --my_cols --value

                Values equal to the threshold will be remove.

    """
    _validate_length_column([column_name], 1)
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] != threshold].reset_index(drop=True)


def select(df, column_name: str, threshold):
    """
    select:     DF COLUMN_NAME THRESHOLD
                Usage : --my_cols --value

                Values equal to the threshold will be save.
                Values not equal to the threshold will be remove.

    """
    _validate_length_column([column_name], 1)
    _validate_type(df[column_name].dtype, type(threshold))
    return df[df[column_name] == threshold].reset_index(drop=True)


def average_on(df, column_list: list):
    """
    average_on:     DF COLUMNS_LIST
                    Usage : --my_cols

                    Average the values in numeric column according to the 
                    columns in the list.
                    COLUMNS_LIST = [COLUMN_NAME(S), NUMERIC_COLUMN]

    """
    _validate_length_column([column_list[-1]], 1)
    _validate_length_column(column_list[:-1], 1, min_length=True)
    if len(check_empty(df)) > 0:
        raise ValueError('Remove column(s) with NaN value.')
    return df.groupby(column_list[:-1])[column_list[-1]].mean().reset_index()


def sum_on(df, column_list: list):
    """
    sum_on:     DF COLUMNS_LIST
                Usage : --my_cols

                Sum the values in numeric column according to the columns
                in the list. Design to sum volume or count for example.
                COLUMNS_LIST = [COLUMN_NAME(S), NUMERIC_COLUMN]

    """
    _validate_length_column([column_list[-1]], 1)
    _validate_length_column(column_list[:-1], 1, min_length=True)
    if len(check_empty(df)) > 0:
        raise ValueError('Remove column(s) with NaN value.')
    return df.groupby(column_list[:-1])[column_list[-1]].sum().reset_index()


def apply_factor(df, column_list: list, row_arg, factor):
    """
    apply_factor:   DF COLUMNS_LIST PATTERN_row FACTOR
                    Usage : --my_cols --pattern --value

                    Apply a factor (multiplication) to the numeric column for
                    specific rows in a specific column.
                    COLUMNS_LIST = [COLUMN_NAME, NUMERIC_COLUMN]

    """
    _validate_length_column(column_list, 2)
    tmp = df[(df[column_list[0]] == row_arg)]
    if tmp.empty is True:
        raise ValueError('No data are found.')
    else:
        df.loc[(df[column_list[0]] == row_arg),
               column_list[1]] = tmp[column_list[1]] * factor


def replace(df, column_name: str, args_dict: dict()):
    """
    replace:        DF COLUMN_NAME DICT
                    Usage : --my_cols --my_dict or --param

                    Replaces the values provided in the dictionary for a specific column. Dict must be in {old: new} format.

    """
    _validate_length_column([column_name], 1)
    return df.replace({column_name[0]: args_dict})


def get_where(df, column_name: str, string_arg: str):
    """
    get_where:      DF COLUMN_NAME PATTERN_row
                    Usage : --my_cols --pattern

                    Selects all rows if the given pattern is contained in
                    the string of each element of a specific column.

    """
    _validate_length_column([column_name], 1)
    return df.loc[df[column_name].str.contains(string_arg)
                  ].reset_index(drop=True)


def get_from(df, column_name: str, row_args):
    """
    get_from:       DF COLUMN_NAME PATTERN_row
                    Usage : --my_cols --pattern

                    Selects rows with one specific value in
                    a specific column.

    """
    _validate_length_column([column_name], 1)
    return df.loc[df[column_name].isin([row_args])].reset_index(drop=True)


def get_query(df, args_dict: dict(), remove=False, op_value=''):
    """
    get_query:      DF DICT [OPTION PATTERN optional]
                    Usage : --my_dict --option --pattern

                    Get a subset dataframe from larger Dataframe using dict.

                    DICT:  Dictionary of {column_name: value(s)}.
                           Key must correspond to column name and value(s)
                           correspond to one or multiple row argument(s),
                           could be string or int/float.
                           To include multiple criteria for value use a list:
                           {'column_name1': value, 
                           'column_name2': ['arg1', 'argN'], 
                           'column_nameN': "string"/float/int}

                    OPTION: If True, it will remove the rows corresponding to
                            argument listed in dictionary.

                    PATTERN: Must be mathematical symbol like > or <,
                             default is '=='. Only affects numeric columns.

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
    merged_on:      DF COLUMNS_LIST DICT [OPTION optional] 
                    Usage : --my_cols --my_dict --option

                    Replace values based on dict and average data on column list
                    using groupby() function of pandas.

                    By default, mean() function is use to average data.
                    Use OPTION to use sum() function (volume or count for ex.).

                    COLUMN_LIST :
                        the order in which columns are supplied is important>
                        [column_for_replace, column_list_include_for_merged,
                        column_numeric]

                        column_for_replace:
                            Column name used to replace dictionary elements
                            (in --my_dict)
                        column_list_include_for_merge:
                            List of included columns to merge data. All columns
                            not included will be averaged. the column in 
                            column_for_replace is included to this list.
                        column_numeric:
                            Column name containing values to be merged.

                    To merge left and right bundle
                    > df_opretaions merged_on data.csv
                        --my_cols Bundles Measures Section Method Value
                        --my_dict _L='' _R=''

    """
    _validate_length_column(column_list[1:-1], 1, min_length=True)

    if len(check_empty(df)) > 0:
        raise ValueError('Remove column(s) with NaN value.')

    df[column_list[0]] = df[column_list[0]].replace(args_dict, regex=True)

    if volume:
        return sum_on(df, column_list)
    else:
        return average_on(df, column_list)


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