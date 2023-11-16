#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Performs an operation on a dataframe using column and/or row.
The supported operations are listed below.
Most operations are column-based. To combine multiple columns, use query to
select or remove data (--option).
To select data :
    > df_operations.py query data.csv Measures=['FA','MD] Bundle=AF
To remove data :
    > df_operations.py query data.csv Measures=['FA','MD] Bundle=AF --option

Some operations to threshold, select or exclude value accept string/float/int
value as parameters.
> df_operations.py lower data.csv 'Section' 2

Dictionary option :
    Use --my_dict to provide a sequence of parameters in the form key=value
    or key=[list of values].

> df_operations.py query Measures=[FA, ihMTR] Section=1

______________________________________________________________________________

OPERATION LIST:

"""

import argparse
import json
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
             parse_dict[parse_key] = parse_val.split(',')
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

    dict_fct = p.add_mutually_exclusive_group()
    dict_fct.add_argument('--my_dict', nargs='+', action=ParseDictArgs,
                          metavar="KEY=VAL",
                          help='Parameters used to build a dictionary. '
                               'Example: key=value or key=value1,value2. '
                               'Use a space to provide multiple keys.')
    dict_fct.add_argument('--param',
                          help='Json file used to replace several elements '
                               'in a specific column. See ex. in data.')

    p.add_argument('--my_cols', nargs='+',
                   help='A column name or list of column names. ')
    p.add_argument('--pattern',
                   help='String or column name used as argument on columns '
                        'or rows.')
    p.add_argument('--value',
                   help='Value used for numeric operations on rows.')
    p.add_argument('--option', action='store_true',
                   help='Use for additional options depending on operation.')
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

    if args.param:
        input_param = json.load(open(args.param))

    df = load_df(args.in_csv)
    result_df = []
    operations_args = []

    # Operations requires only dataframe
    print_function = ['display', 'column', 'info', 'check_empty']
    if args.operation in print_function:
        try:
            OPERATIONS[args.operation](df)
        except ValueError as msg:
            logging.error('{} operation failed.'.format(
                    args.operation.capitalize()))
            logging.error(msg)
            return
        exit()

    # Operations requires only dataframe and save it
    single_operations = ['drop_empty_column', 'drop_nan']
    if args.operation in single_operations:
        operations_args = [df]

    # Operations requires dataframe and dictionnary
    operations_on_column_with_dict = ['rename']
    if args.operation in operations_on_column_with_dict:
        if not args.my_dict:
            parser.error('This operation must be used with --my_dict.')
        operations_args = [df, args.my_dict]

    # Single column operations
    # Operations requires dataframe and single column
    operations_on_column = ['unique', 'remove_column']
    if args.operation in operations_on_column:
        operations_args = [df, str(args.my_cols[0])]

    # Operations requires dataframe, single column and specific pattern
    operations_on_column_with_pattern = ['get_where', 'get_from', 'remove_row']
    if args.operation in operations_on_column_with_pattern:
        if not args.pattern:
            parser.error('This operation must be used with --pattern.')
        operations_args = [df, str(args.my_cols[0]), args.pattern]

    # Operations requires dataframe, single column and specific value
    operations_on_value = ['lower', 'upper', 'exclude', 'select']
    if args.operation in operations_on_value:
        if not args.value:
            parser.error('Value operations must be used with --value.')
        operations_args = [df, str(args.my_cols[0]), args.value]

    # Multi columns operations
    # Operations requires dataframe and multi columns
    operations_on_multi_columns = ['average', 'sum']
    if args.operation in operations_on_multi_columns:
        operations_args = [df, args.my_cols]

    # Operations requires dataframe, multi columns and specific pattern
    operations_on_multi_columns_with_pattern = ['convert', 'split']
    if args.operation in operations_on_multi_columns_with_pattern:
        if not args.pattern:
            parser.error('This operation must be used with --pattern.')
        operations_args = [df, args.my_cols, args.pattern]

    # Operations requires dataframe, multi columns and dictionnary
    if args.operation == 'replace':
        if not args.my_cols and not (args.my_dict or args.param):
            parser.error('Merge operation must be used with --my_cols and '
                         '--my_dict or --param.')
        if args.param:
            args.my_dict = input_param
        operations_args = [df, args.my_cols, args.my_dict]

    # Operations requires dataframe, multi columns and dictionnary with option
    if args.operation == 'merged':
        if not args.my_cols and not (args.my_dict or args.param):
            parser.error('Merge operation must be used with --my_cols and '
                         '--my_dict or --param.')
        if args.param:
            args.my_dict = input_param
        operations_args = [df, args.my_cols, args.my_dict, args.option]

    # Operations requires dataframe, multi columns, pattern and value
    if args.operation == 'factor':
        if not args.my_cols and not args.pattern and not args.value:
            parser.error('Factor operation must be used with --my_cols and '
                         '--pattern and --value.')
        if args.param:
            args.my_dict = input_param
        operations_args = [df, args.my_cols, args.pattern, args.value]

    # Operations requires dataframe, dictionnary, pattern and options
    if args.operation == 'query':
        if not (args.my_dict or args.param):
            parser.error('Query operation must be used with --my_dict or '
                         ' --param.')
        if args.param:
            args.my_dict = input_param
        operations_args = [df, args.my_dict, args.option, args.pattern]

    # Called and run operations with specific arguments required
    try:
        result_df = OPERATIONS[args.operation](*operations_args)
    except ValueError as msg:
        logging.error('{} operation failed.'.format(
            args.operation.capitalize()))
        logging.error(msg)
        return

    # Save output dataframe
    output_df = result_df
    if len(output_df) == 0:
        raise ValueError('Dataframe is empty.')
    else:
        output_df.to_csv(os.path.join(args.out_dir, args.out_name + '.csv'),
                         index=False)


if __name__ == '__main__':
    main()
