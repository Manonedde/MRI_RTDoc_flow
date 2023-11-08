#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Performs an operation on a dataframe using column and/or row. 
The supported operations are listed below. 
Most operations are column-based. To combine multiple columns, use query.

Some operations to threshold, select or exclude value accept string/float/int
value as parameters.
> df_operations.py lower_value data.csv 'Section' 2

Dictionary option :
    Use --my_dict to provide a sequence of parameters in the form key=value
    or key=[list of values].

> df_operations.py query Measures=[FA, ihMTR] Section=1

______________________________________________________________________________

OPERATION LIST:

"""

import argparse
import logging
import os

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from dataframe.utils import load_df
from dataframe.operations import get_df_ops, get_operations_doc

OPERATIONS = get_df_ops()

__doc__ += get_operations_doc(OPERATIONS)


class ParseDictArgs(argparse.Action):
     def __init__(self, option_strings, dest, nargs=None, **kwargs):
         self._nargs = nargs
         super(ParseDictArgs, self).__init__(option_strings, dest, 
                                             nargs=nargs, **kwargs)
     def __call__(self, parser, namespace, values, option_string=None):
         parse_dict = {}
         for key_val in values:
             parse_key, parse_val = key_val.split("=")
             parse_dict[parse_key] = parse_val
         setattr(namespace, self.dest, parse_dict)


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

    p.add_argument('--my_dict', nargs='+', action=ParseDictArgs,
                   metavar="KEY=VAL",
                   help='Parameters used to build a dictionary. Example: '
                        'key=value or key=[list of values]. Use a space to '
                        'provide multiple keys.')
    p.add_argument('--my_cols', nargs='+',
                   help='A column name or list of column names. ')
    p.add_argument('--pattern',
                   help='String or column name used as argument on columns '
                        'or rows.')
    p.add_argument('--value', type=float,
                   help='Value used for numeric operations on rows.')
    p.add_argument('--option', action='store_true',
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

    if args.operation not in OPERATIONS.keys():
        parser.error('Operation {} not implement.'.format(args.operation))

    single_operations = ['display', 'list_column', 'check_empty',
                         'drop_empty_column', 'drop_nan']

    df = load_df(args.in_csv)
    result_df = []

    if args.operation in single_operations:
        try:
            result_df = OPERATIONS[args.operation](df)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                    args.operation.capitalize()))
            logging.error(msg)
            return

    operations_on_value = ['lower_values', 'upper_values',
                           'exclude_values', 'select_values']

    if args.operation in operations_on_value:
        if not args.value:
            parser.error('Value operations must be used with --value.')
        try:
            result_df = OPERATIONS[args.operation](df, str(args.my_cols[0]),
                                                   args.value)
            print(result_df)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                args.operation.capitalize()))
            logging.error(msg)
            return

    operations_on_single_column = ['get_data_where', 'get_data_from',
                                   'remove_row']

    if args.operation in operations_on_single_column:
        if not args.pattern:
            parser.error('This operation must be used with --pattern.')
        try:
            result_df = OPERATIONS[args.operation](df, str(args.my_cols[0]),
                                                   args.pattern)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                args.operation.capitalize()))
            logging.error(msg)
            return

    operations_on_multi_columns = ['average_data', 'sum_data']

    if args.operation in operations_on_multi_columns:
        try:
            result_df = OPERATIONS[args.operation](df, args.my_cols)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                args.operation.capitalize()))
            logging.error(msg)
            return

    if args.operation == 'merged_on':
        if not args.my_cols and not args.my_dict:
            parser.error('Merge operation must be used with --my_cols and '
                         '--my_dict.')
        try:
            result_df = OPERATIONS[args.operation](df, args.my_cols,
                                                   args.my_dict, args.option)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                args.operation.capitalize()))
            logging.error(msg)
            return

    if args.operation == 'query':
        if not args.my_dict:
            parser.error('Query operation must be used with --my_dict.')
        try:
            result_df = OPERATIONS[args.operation](df, args.my_dict,
                                                   remove=args.option,
                                                   op_value=args.pattern)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                args.operation.capitalize()))
            logging.error(msg)
            return

    output_df = result_df
    if len(output_df) == 0:
        raise ValueError('Dataframe is empty.')
    else:
        output_df.to_csv(os.path.join(args.out_dir, args.out_name + '.csv'),
                         index=False)


if __name__ == '__main__':
    main()
