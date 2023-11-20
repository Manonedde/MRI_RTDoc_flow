#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict

import pandas as pd
import numpy as np


def get_df_ops():
    """Get a dictionary of all functions relating to dataframe operations"""
    return OrderedDict([
        ('display', display),
        ('column', list_column),
        ('unique', unique),
        ('info', info),
        ('check_empty', check_empty),
        ('drop_empty_column', drop_empty_column),
        ('drop_nan', drop_nan),
        ('remove_column', remove_column),
        ('rename', rename),
        ('delete', delete),
        ('convert', convert),
        ('upper', upper),
        ('lower', lower),
        ('exclude', exclude),
        ('select', select),
        ('get_from', get_from),
        ('get_where', get_where),
        ('remove_row', remove_row),
        ('average', average_on),
        ('sum', sum_on),
        ('replace', replace),
        ('replace_where', replace_where),
        ('split_col', split_col),
        ('split_by', split_by),
        ('factor', apply_factor),
        ('query', get_query),
        ('merged', merged_on)])


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


def _validate_type(dtype1: type, dtype2: type, convert=False):
    """Make sure that the inputs are in the same type."""
    if dtype1 != dtype2:
        raise ValueError('Type of your value not correspond to the column '
                         'dtype.')


def _convert_to_str(df):
    """Lists original column type and converts all non-float columns to
    structure to enable actions.
    Function written to deal with argparser strings.
    """
    original_type = df.dtypes.apply(lambda x: x.name).to_dict()
    to_convert = df.columns[(df.dtypes.values != np.dtype('float64'))]
    df[to_convert] = df[to_convert].astype(str)
    return original_type, df


def _build_query(args_dict, operator, operator_value='=='):
    """Function to build query structure compatible with df.query()
       from dictionnary.
    """
    return ' and '.join(
            [f"({col} {operator} '{row}')" 
             if type(row) == str 
             else f"({col} {operator} {row})" if type(row) == list 
             else f"({col} {operator_value} {row})"
             for col, row in args_dict.items()])


def display(df):
    """
    display:            DF
                        Print Dataframe.
    """
    return print(df)


def list_column(df):
    """
    column:             DF
                        Print the list of columns dataframe.
    """
    return print(df.columns.tolist())


def info(df):
    """
    info:               DF
                        Print summary informations of DataFrame.
    """
    return print(df.info())


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


def remove_row(df, column_name: list, string_arg: str):
    """
    remove_row:    DF COLUMNS_NAME PATTERN_row
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
    return  print(df[column_name].unique().tolist())


def rename(df, args_dict: dict()):
    """
    rename:         DF DICT
                    Usage : --my_dict

                    Rename column(s) according to dictionnary.
                    Dict must be in {old: new} format.

    """
    return  df.rename(columns=args_dict)


def delete(df, args_dict: dict()):
    """
    delete:         DF DICT
                    Usage : --my_dict

                    Remove rows based on combination of 2 or 3 arguments.
                    my_dict Measures=FA Sid=sub-002
    """
    original_dtype, df = _convert_to_str(df)
    zargs = list(args_dict.items())

    if len(zargs) > 3 or len(zargs) == 1:
        raise ValueError('This function takes only 2 or 3 arguments combined.')
    elif len(zargs) == 3:
        tmp = df[(df[zargs[0][0]] == zargs[0][1]) &
                (df[zargs[1][0]] == zargs[1][1]) &
                (df[zargs[2][0]] == zargs[2][1])]
    elif len(zargs) == 2:
        tmp = df[(df[zargs[0][0]] == zargs[0][1]) &
                (df[zargs[1][0]] == zargs[1][1])]

    df = df.drop(tmp.index, axis=0).reset_index(drop=True).astype(original_dtype)
    return  df


# Deal like this for now, need to improve it with 'int' arguments
def convert(df, colunm_name, args_type=None, param=False):
    """
    convert:            DF COLUMN_NAME DTYPE or DF DICT (param option)
                        Usage : --my_cols --pattern
                           or : --param 

                        args_type choice: 'int64', 'float64' or 'object'

                        Converts dtype of one column or multiple columns when 
                        --param is used.

    """
    _validate_length_column([colunm_name], 1, min_length=True)
    original_dtype, _ = _convert_to_str(df)

    if param:
        original_dtype = param
    elif args_type:
        original_dtype[colunm_name[0]] = args_type

    df = df.astype(original_dtype)
    return df


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


def split_col(df, column_list: list, row_args):
    """
    split_col       DF COLUMN_LIST PATTERN_row optional
                    Usage : --my_cols --pattern

                    Splits one column into multiple columns with delimiter or
                    regular expression pattern.
                    COLUMNS_LIST = [COLUMN_NAME_tosplit, NEW_COLNAME(S)]

                    If only one column is supplied, the new column names will
                    be assigned with numbers.

    """
    _validate_length_column([column_list], 1, min_length=True)
    if len([column_list]) == 1:
        df = pd.concat([df, df[column_list[0]].str.split(row_args,
                                                      expand=True)], axis=1)
    else:
        df[column_list[1:]] = df[column_list[0]].str.split(row_args,
                                                           expand=True)
    return df


def split_by(df, column_name: str):
    """
    split_by        DF COLUMN_NAME
                    Usage : --my_cols

                    Splits dataframe into multiple dataframe based on unique
                    arguments in specific column.

    """
    _validate_length_column([column_name], 1)
    df_names, multi_df = [], []
    for argument in df[column_name].unique():
        frame = df[df[column_name] == argument]
        multi_df.append(frame)
        df_names.append(argument)
    return df_names, multi_df


def replace(df, column_name: str, args_dict: dict()):
    """
    replace:        DF COLUMN_NAME DICT
                    Usage : --my_cols --my_dict or --param

                    Replaces the values provided in the dictionary for a 
                    specific column. Dict must be in {old: new} format.

    """
    _validate_length_column([column_name], 1)
    original_dtype, df = _convert_to_str(df)
    df = df.replace({column_name[0]: args_dict}).astype(original_dtype)
    return df


def replace_where(df, column_list: str, pattern: str, args_dict: dict()):
    """
    replace_where:  DF COLUMN_LIST PATTERN DICT
                    Usage : --my_cols --pattern --my_dict

                    Replaces the value provided in the dictionary on a
                    two-column basis. A column for selecting according to
                    a specific pattern and a column in which to replace
                    one or more values. Dict must be in {old: new} format.
                    COLUMN_LIST = [COLUMN_select, COLUMN_replace]

                    Ex.: ['Sid', 'Session'] 'sub-001' {'1':'2'}

    """
    _validate_length_column(column_list, 2)
    original_dtype, df = _convert_to_str(df)
    for key, val in args_dict.items():
        df.loc[((df[column_list[0]] == pattern) & 
                (df[column_list[1]] == key)), column_list[1]] = val
        
    df = df.astype(original_dtype)
    return df



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


def get_query(df, args_dict: dict(), remove=False, op_if_value=None):
    """
    query:          DF DICT [OPTION PATTERN optional]
                    Usage : --my_dict --option --pattern

                    Get a subset dataframe from larger Dataframe using dict 
                    to combine multi arguments.

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
        return df.query(_build_query(args_dict, '!=')).reset_index(drop=True)
    elif op_if_value is not None:
        return df.query(_build_query(args_dict, '==', op_if_value)
                        ).reset_index(drop=True)
    else:
        return df.query(_build_query(args_dict, '==')).reset_index(drop=True)


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