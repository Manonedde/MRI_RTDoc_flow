#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to prepare a csv file output from convert_json_to_csv.py script
to build html figures for the Read the Doc site.
"""

import argparse
import os
import pandas as pd
import numpy as np

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from dataframe.utils import (list_metrics, list_method, scaling_metrics,
                            measure_dict, replace_dict, columns_rename,
                            col_order)
from dataframe.func import (filter_df, extract_average_and_profile,
                            compute_ecvf_from_df, merged_left_right_data)


def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)
    p.add_argument('in_csv',
                   help='CSV diffusion data (.csv).')
    p.add_argument('--out_name',
                   help='Filename prefix to save csv outputs (name_*).')
    p.add_argument('--out_dir',
                   help='Output directory to save CSV files. ')

    filtering = p.add_argument_group(title='Filtering options')
    filtering.add_argument('--rm_sid', nargs='+',
                           help='List of subjects to remove. ')
    filtering.add_argument('--rm_bundle', nargs='+',
                           help='List of bundles to remove.')
    filtering.add_argument('--rm_measure', nargs='+',
                           help='List of measures to remove. ')
    filtering.add_argument('--rm_stats', nargs='+',
                           help='List of statistics to remove. ')
    filtering.add_argument('--rm_section', type=int, nargs='+',
                           help='List of sections to remove. ')
    filtering.add_argument('--rm_rbx',
                           choices=["v1", "v10"],
                           help='List of RBX version to remove. ')

    set_shape = p.add_argument_group(title='CSV shape options')
    set_shape.add_argument('--rename_measure', action='store_true',
                           help='Rename MRI measures. ')
    set_shape.add_argument('--rename_bundles', action='store_true',
                           help='Rename MRI measures. ')
    set_shape.add_argument('--compute_ecvf', action='store_true',
                           help='Compute ECVF using ICVF from dataframe. '
                                'Not recommended.')
    set_shape.add_argument('--longitudinal',
                           help='Separator or delimiter used to split Sid '
                                'column in two columns. [%(default)s].')
    set_shape.add_argument('--split_by_method', action='store_true',
                           help='Rename MRI measures. ')
    set_shape.add_argument('--apply_factor_metric',
                           help='List of metrics where a factor must be '
                                'applied.\nBy default, is applied on Diffusion '
                                'Measure (including FW-corrected).')
    set_shape.add_argument('--apply_factor', type=int, default=100,
                           help='Factor applied on MRI measure for plot. '
                                ' [%(default)s].')
    set_shape.add_argument('--merge_lr', action='store_true',
                           help='Merge left and right bundles using mean() '
                                'for MRI measurements and sum() for '
                                'volume and count. ')

    add_overwrite_arg(p)

    return p


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    assert_inputs_exist(parser, args.in_csv)

    if args.out_dir is None:
        args.out_dir = './'

    if args.out_name is None:
        args.out_name = 'rtd_'

    # Load Data frame without
    df = pd.read_csv(args.in_csv)

    # Drop index column and rename some pattern from columns
    for key in replace_dict:
        df[key] = df[key].replace(replace_dict[key],'', regex=True)

    df.loc[df.metrics.str.contains('volume'), 'stats'] = 'volume'
    df.loc[df.metrics.str.contains('count'), 'stats'] = 'count'
    df['section'] = df.section.replace(np.nan, 0, regex=True)
    df['section'] = df['section'].astype(int)

    df.loc[df.roi.str.contains('v10'),'rbx_version']= 'v10'
    df.loc[~df.roi.str.contains('v10'),'rbx_version']= 'v1'

    # Filtering dataframe
    if args.rm_rbx:
        df = df.loc[~df['rbx_version'].str.contains(args.rm_rbx)]

    if args.rm_sid:
        for subject in args.rm_sid:
            df = df.loc[~df['sid'].str.contains(subject)]

    if args.rm_bundle:
        for bundle in args.rm_bundle:
            df = df.loc[~(df.roi == bundle)]

    if args.rm_measure:
        for measure in args.rm_measure:
            df = df.loc[~(df.metrics == measure)]

    if args.rm_section:
        for section in args.rm_section:
            df = df.loc[~(df.section == section)]

    # Attribute Method corresponding to metrics based on lists
    for idx, metric in enumerate(list_metrics):
        df.loc[df.metrics.isin(metric), 'Method'] = list_method[idx]

    # Merge Left and right : remove L and R and mean row
    if args.merge_lr:
        df = merged_left_right_data(df, col_order[:-1])
    else:
        df['roi'] = df.roi.replace({'_L':'_Left','_R':'_Right'}, regex=True)

    if args.rename_measure:
        # check lists
        missing_metric = []
        for metric_item in df['metrics'].unique():
            if metric_item not in measure_dict:
                missing_metric.append(metric_item)

        if len(missing_metric) > 0:
            print("The listed metrics don't match with the default "
                  "metrics list.\nYou can add missing metrics in "
                  " ALL requiring lists in utils.py.\n", missing_metric)
        else:
            # Rename measures using a dictionnary
            df = df.replace({"metrics": measure_dict})

    # Remove the underscore from Bundle name
    if args.rename_bundles:
        df['roi'] = df.roi.replace('_', ' ', regex=True)

    # Apply a scale factor for diffusion measure
    if args.apply_factor:
        if args.apply_factor_metric is not None:
            scaling_metrics = args.apply_factor_metric
            for curr_metric in scaling_metrics:
                apply_factor_to_metric(df, curr_metric, args.apply_factor)

    # Compute ECVF values from ICVF in dataframe
    if args.compute_ecvf:
        df = compute_ecvf_from_df(df)

    # Split Sid columns into Sid and Session columns
    if args.longitudinal:
        col_order.insert(4, 'Session')
        df[['tmp','Session']] = df['sid'].str.split(args.longitudinal,
                                                    1, expand=True)
        df.drop('sid', axis=1, inplace=True)
        df = df.rename(columns={'tmp':'sid'})

        if 'lesion_label' in df.columns.tolist():
            col_order.insert(6, 'lesion_label')

        df = df[col_order]

    # Reorder columns and extract average and profile data
    if 'lesion_label' in df.columns.tolist() and args.longitudinal is None:
        col_order.insert(5, 'lesion_label')

    df = df[col_order]
    df = df.rename(columns=columns_rename)
    average, profile = extract_average_and_profile(df)

    # Save new dataframes
    if args.split_by_method:
        for curr_method in average.unique():
            average_by_method = filter_df(average, 'Method', curr_method)
            average_by_method.to_csv(os.path.join(args.out_dir, args.out_name +
                                                  'average_' + curr_method +
                                                   '.csv'), index=False)
            profile_by_method = filter_df(profile, 'Method', curr_method)
            profile_by_method.to_csv(os.path.join(args.out_dir, args.out_name +
                                                  'profile_' + curr_method +
                                                   '.csv'), index=False)
    else:
        average.to_csv(os.path.join(args.out_dir,
                                    args.out_name + '_average.csv'),
                                    index=False)
        profile.to_csv(os.path.join(args.out_dir,
                                    args.out_name + '_profile.csv'),
                                    index=False)


if __name__ == '__main__':
    main()
