#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd


# Convert json
def split_col(x, delimiter_arg='.'):
    """
    Convert Text to Columns using specific delimiter.
    :param x: string or value containing text (cols, value).
    :param delimiter_arg: delimiter
    :return: Returns a list of elements divided according to the delimiter.
    """
    cols, value = x
    if not delimiter_arg in cols:
        raise ValueError('No matching delimiter found.')
    parse_val = *cols.split(delimiter_arg), value
    return parse_val


def get_row_name_from_col(df, col_name):
    return df[col_name].unique().tolist()


def filter_rows_by_values(df, column_name, set_value, superior=False,
                          inferior=False, exclude=False):
    """

    df:                 Dataframe
    column_name:        Name of column on which filter is applied.
    set_value:          Value used to filter the column.
    superior:           To select the value > to value.
    inferior:           To select the value < to value.
    exclude:            To exclude value equal to value.
    
    Return:             Filtered dataframe.
    """
    if df[column_name].dtype != type(set_value):
        raise ValueError('Type of your value not correspond to the column '
                         'dtype.')
    if superior:
        df = df[df[column_name] > set_value]
    elif inferior:
        df = df[df[column_name] < set_value]
    elif exclude:
        df = df[~df[column_name] != set_value]

    return df.reset_index(drop=True)


def get_data_from(df, column_name, row_args):
    """
    Function to extract some rows from one column using isin.() function.

    df:             Dataframe
    column_name:    Column name
    row_args:       List of string argument.

    Return Dataframe corresponding to list of arguments.
    """
    return df.loc[df[column_name].isin(row_args)].reset_index(drop=True)


def get_subset_df(df, args_dict, remove=False, op_value=''):
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

    Return Dataframe corresponding to the arguments listed in dictorionnary.
    """
    if remove:
        query_from_dict = ' and '.join(
            [f'({col} != "{row}")' if type(row) == str else f'({col} != {row})'
             for col, row in args_dict.items()])
    elif op_value != '':
        query_from_dict = ' and '.join(
            [f'{col} == "{row}"' if type(
                row) == str else f'{col} {op_value} {row}'
             for col, row in args_dict.items()])
    else:
        query_from_dict = ' and '.join(
            [f'({col} == "{row}")' if type(row) == str else f'({col} == {row})'
             for col, row in args_dict.items()])

    return df.query(query_from_dict).reset_index(drop=True)


def merged_col_csv(df1, df2, label1, label2, colname):
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


def filter_df(df, column, filter_arg):
    """
    Function to filter dataframe based on column and filter.
    :param df:
    :param column:
    :param filter_arg:
    :return:
    """
    df_filter = df[df[column] == filter_arg]
    return df_filter.reset_index(drop=True)
