#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to convert jsons output by TractometryFlow into CSV files.

To run this script, individual jsons must be merged with scil_merge_json.py
(without option). It does not work with jsons provided in the Statistics
folder.

> scil_merge_json.py results_tractometry/sub*/Bundle_**/*json your_output.json

By default, when several jsons are given as input, this script converts
each json into an individual CSV file in long format (for wide format
use --wide). To convert all jsons into a single CSV file,
use the --save_merge_df option.

>> convert_json_to_csv.py *json --save_merge_df

"""


import argparse
import copy
import json
import os

import pandas as pd

from scilpy.io.utils import (add_overwrite_arg,
                             assert_inputs_exist, assert_outputs_exist)

def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_json', nargs = '+',
                   help = 'File(s) containing the json stats (.json).')

    p.add_argument('--out_csv',
                   help = 'Output CSV filename for the stats (.csv).')
    p.add_argument('--out_dir',
                   help = 'Output directory to save CSV. \n'
                          'By default is current folder.')
    p.add_argument('--wide', action = 'store_true',
                   help = 'Option to save in wide format the statistic '
                          'measurements. By default is long format.')
    p.add_argument('--save_merge_df', action = 'store_true',
                   help = 'Save all jsons into a single dataframe in long \n'
                          'format. By default, each json is saved in an '
                          'independent csv. ')

    add_overwrite_arg(p)

    return p

# Split index into multiple columns
def split_col(x):
    cols, value = x
    parse_col_value = *cols.split("."), value
    return parse_col_value

# Reshpae long type CSV to wide format
def reshape_to_wide_format(long_format_df, selected_cols):
    col_name = copy.deepcopy(selected_cols)
    wide_format = long_format_df.pivot(index = selected_cols,
                                       columns = "stats")
    wide_format = wide_format.reset_index(drop = True)
    measure_names = wide_format['value'].columns.tolist()
    wide_format.columns = wide_format.columns.droplevel()
    wide_format.columns = col_name + measure_names
    return wide_format


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_json)

    if args.out_dir is None:
        args.out_dir = './'

    # Load, reshape and save multi json data
    tmp_df = []
    for curr_json in args.in_json:

        if args.out_csv is None:
            args.out_csv = os.path.splitext(os.path.basename(curr_json))[0]

        # Load json data
        df = pd.json_normalize(json.load(open(curr_json))).T
        df = df.reset_index(drop=False)

        # Split index into multiple columns
        values = [split_col(x) for x in df[["index", 0]].values]
        nb_var = (len(values[0])-1)

        # Define the column names based on number of columns
        # This assumes that columns always have the same organization
        # Perhaps we need to find another way of doing this
        if nb_var > 4 and ('001' in values[0]) is True:
            tmp_columns = ["sid","roi","metrics", "section",
                           "stats","value"]
            base_columns = ["sid", "roi","metrics","section"]
        elif nb_var == 4 and ('001' in values[0]) is True:
            tmp_columns = ["sid","roi","stats", "section","value"]
            base_columns = ["sid","roi","section"]
        elif nb_var == 4:
            tmp_columns = ["sid", "roi", "metrics", "stats", "value"]
            base_columns = tmp_columns[0:3]
        else:
            tmp_columns = ["sid", "roi", "stats", "value"]
            base_columns = tmp_columns[0:2]

        # Store json data in dataframe
        long_df = pd.DataFrame(columns = tmp_columns, data = values)
        if args.save_merge_df:
            if len(long_df.columns.tolist()) < 5:
                long_df.insert(2,'metrics',values[0][2])
                if ('001' in values[0]) is True:
                    long_df.insert(3,'section','averaged')
            tmp_df.append(long_df)
        else:
            long_df.to_csv(os.path.join(args.out_dir,
                                        args.out_csv + '_long.csv'))

        # Reshape long to wide dataframe
        if args.wide:
            wide_df = reshape_to_wide_format(long_df, base_columns)
            # Save dataframe
            wide_df.to_csv(os.path.join(args.out_dir,
                                        args.out_csv + '_wide.csv'))

    if args.save_merge_df:
        merged_long_df = pd.concat(tmp_df[:], ignore_index=True)
        merged_long_df = merged_long_df.reset_index(drop=True)
        merged_long_df.to_csv(os.path.join(args.out_dir,
                                           'merged_csv_long.csv'))


if __name__ == "__main__":
    main()
