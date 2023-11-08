#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Performs an operation on a dataframe using column and/or row. 
The supported operations are listed below.

Some operations to threshold, select or exclude value accept string/float/int
value as parameters.
> df_operations.py lower_value data.csv 'Section' 2

Dictionary option :
    Use --my_args to provide a sequence of parameters in the form key=value
    or key=[list of values].
    > df_operations.py get_query Measures=[FA, MD, ihMTR]
                            Bundles=[AF_Left, UF_Right] Section=1


Operation merged_on:
    Function uses groupby() function of pandas.
    By default merged_on uses the mean() function to merge. 
    To sum() instead of average, as for bundle volumes/streamline counts for
    example, use --options.

    --my_col: the order in which columns are supplied is important, 
          [column_for_replace, column_list_include_for_merge, column_numeric]

    column_for_replace: column used to replace dictionary elements (my_dict)
    column_list_include_for_merge: List of included columns to merge data.
                                   All columns not included will be averaged.
    column_numerique: Column name containing values to be merged.

    Ex. to merge left and right bundle:
    df_opretaions merged_on data.csv 
        --my_cols Bundles Measures Section Method Value 
        --my_dict _L='' _R=''

    Function replaces '_L' and '_R' by '' on 'Bundles' column and compute
    mean() value on 'Value' column keeping information from
    'Measures', 'Section' and 'Method' colunm.


Operation get_query:
    args_dict:  Dictionary of {column_name: value(s)}.
                Key must correspond to column name and value(s) correspond to
                one or multiple row argument(s), could be string or int/float.
                To include multiple criteria for value use a list.
                {'column_name1': value, 'column_name2': ['arg1', 'argN'],
                'column_nameN': "string"}
    options:     If True, it will remove the rows corresponding to argument
                listed in dictionary.
    pattern:   Must be mathematical symbol like > or <.

"""

import argparse
import logging
import os

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from dataframe.utils import load_df
from dataframe.operations import get_df_ops, get_operations_doc

OPERATIONS = get_df_ops()

__doc__ += get_operations_doc(OPERATIONS)

class ParseDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)
    p.add_argument('operation',
                   choices=OPERATIONS.keys(),
                   help='The type of operation to be performed on the '
                        'dataframe.')
    p.add_argument('in_csv',
                   help='CSV data (.csv).')
    p.add_argument('out_name',
                   help='Filename to save csv outputs.')

    p.add_argument('--my_args', nargs='*', action=ParseDict,
                   help='Parameters used to build a dictionary. Example: '
                        'key=value or key=[list of values],. Use a space to ' 'provide multiple keys.')
    p.add_argument('--my_cols', nargs='+',
                   help='A column name or list of column names. ')
    p.add_argument('--pattern',
                   help='String or column name used as argument on columns '
                        'or rows.')
    p.add_argument('--value',
                   help='Value used for numeric operations on rows.')
    p.add_argument('--options', action='store_true',
                   help='Use for additional options.')
    p.add_argument('--out_dir',
                   help='Output directory to save CSV files. ')

    add_overwrite_arg(p)

    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    df = load_df(args.in_csv)

    if args.operation not in OPERATIONS.keys():
        parser.error('Operation {} not implement.'.format(args.operation))

    single_operations = [display_df, list_column, check_empty,
                         drop_empty_column, drop_nan]

    if args.operation in single_operations:
        try:
            output_df = OPERATIONS[args.operation](df)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                    args.operation.capitalize()))
            logging.error(msg)
        return

    operations_on_value = [lower_values, upper_values,
                           exclude_values, select_values]

    if args.operation in operations_on_value:
        if not args.value:
            parser.error('Value operations must be used with --value.')
        try:
            output_df = OPERATIONS[args.operation](df, args.my_cols,
                                                   args.value)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                args.operation.capitalize()))
            logging.error(msg)
            return

    operations_on_column = [get_data_where, average_data, sum_data]

    if args.operation in operations_on_column:
        if not args.pattern:
            parser.error('This operation must be used with --pattern.')
        try:
            output_df = OPERATIONS[args.operation](df, args.my_cols,
                                                   args.pattern)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                args.operation.capitalize()))
            logging.error(msg)
            return

    if args.operation == 'merged_on':
        if not args.my_cols and not args.my_args:
            parser.error('Merge operation must be used with --my_cols and '
                         '--my_args.')
        try:
            output_df = OPERATIONS[args.operation](df, args.my_cols,
                                                   args.my_args)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                args.operation.capitalize()))
            logging.error(msg)
            return

    if args.operation == 'get_query':
        if not args.my_args:
            parser.error('Query operation must be used with --my_args.')
        try:
            output_df = OPERATIONS[args.operation](df, args.my_args,
                                                   remove=args.remove,
                                                   op_value=args.pattern)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                args.operation.capitalize()))
            logging.error(msg)
            return


    output_df.to_csv(os.path.join(args.out_dir, args.out_name + '.csv'),
                     index=False)


if __name__ == '__main__':
    main()
