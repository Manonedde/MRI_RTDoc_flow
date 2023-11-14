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
import numpy as np

from dataframe.parameters import column_dict_name
from dataframe.func import (split_col, reshape_to_wide_format,
                            convert_lesion_data)
from scilpy.io.utils import (add_overwrite_arg,
                             assert_inputs_exist, assert_outputs_exist)


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_json', nargs='+',
                   help='File(s) containing the json stats (.json).')

    p.add_argument('--out_csv',
                   help='Output CSV filename for the stats (.csv).')
    p.add_argument('--out_dir',
                   help='Output directory to save CSV. \n'
                   'By default is current folder.')
    p.add_argument('--wide', action='store_true',
                   help='Option to save in wide format the statistic '
                   'measurements. By default is long format.')
    p.add_argument('--save_merge_df', action='store_true',
                   help='Save all jsons into a single dataframe in long \n'
                   'format. By default, each json is saved in an '
                   'independent csv. ')

    add_overwrite_arg(p)

    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_json)

    if args.out_dir is None:
        args.out_dir = './'

    # Load, reshape and save multi json data
    tmp_df = []
    for curr_json in args.in_json:
        if 'stats' in curr_json:
            print("The lesion_stats and lesion_streamlines_stats jsons\n"
                  "cannot be processed with this script. \n"
                  "Remove these jsons from the input.\n")

        key_columns = os.path.splitext(os.path.basename(curr_json))[0]
        if args.out_csv is None:
            args.out_csv = key_columns

        # Load json data
        df = pd.json_normalize(json.load(open(curr_json))).T
        df = df.reset_index(drop=False)

        if 'lesion' in curr_json:
            long_columns_list = column_dict_name[key_columns][0]
            long_columns_nolist = column_dict_name[key_columns + '_nolist'][0]

            long_df = convert_lesion_data(df, long_columns_list,
                                          long_columns_nolist)

        else:
            # Define the column names based on number of columns
            # This assumes that columns always have the same organization
            long_columns, wide_columns = column_dict_name[key_columns]
            # Store json data in dataframe
            values = [split_col(x) for x in df[["index", 0]].values]
            long_df = pd.DataFrame(columns=long_columns, data=values)

        if args.save_merge_df:
            tmp_df.append(long_df)

        else:
            long_df.to_csv(os.path.join(args.out_dir,
                                        args.out_csv + '_long.csv',
                                        index=False))
            long_df.to_csv(os.path.join(args.out_dir,
                                        args.out_csv + '_wide.csv'),
                           index=False)
        # Reshape long to wide dataframe
        if args.wide:
            if 'sats' in long_df.column.tolist():
                long_df = reshape_to_wide_format(long_df, wide_columns)
                # Save dataframe
            long_df.to_csv(os.path.join(args.out_dir,
                                        args.out_csv + '_wide.csv'),
                           index=False)

    if args.save_merge_df:
        merged_long_df = pd.concat(tmp_df[:], ignore_index=True)
        merged_long_df = merged_long_df.reset_index(drop=True)
        merged_long_df.to_csv(os.path.join(args.out_dir,
                                           'merged_csv_long.csv'), index=False)


if __name__ == '__main__':
    main()
