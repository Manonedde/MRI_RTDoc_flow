#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates summary table from data included in the input CSV.
"""

import argparse

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from dataframe.utils import load_df
from dataframe.func import generate_summary_table

def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    p.add_argument('in_csv',
                   help='CSV MRI data.')

    p.add_argument('--out_name', default='summary_table',
                   help='Output filename to save plot.')
    p.add_argument('--out_dir',
                   help='Output directory for CSV.')
    p.add_argument('--on_columns', default=['Measures', 'Value'],
                   help='List of column names used to compute summary.')
    p.add_argument('--select_columns',
                   help='List of column names to select.')
    p.add_argument('--rename_columns',
                   help='List of column names for table.')
    p.add_argument('--round_at', type=int, default=3,
                   help='List of column names for table.')

    add_overwrite_arg(p)

    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    # Load and filter Dataframe
    df = load_df(args.in_csv)

    table = generate_summary_table(df, by_cols=args.on_columns,
                                   round_at=args.round_at,
                                   select_stats_col=args.select_columns,
                                   custom_col_name=args.rename_columns)
    
    table.to_csv(os.path.join(args.out_dir, args.out_name))


if __name__ == '__main__':
    main()
