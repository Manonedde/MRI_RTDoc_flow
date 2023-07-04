#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to prepare a csv file output output from convert_json_to_csv.py script
to build html figures for the Read the Doc site.
"""

import argparse
import os
import pandas as pd
import numpy as np

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist

from utils import list_metrics, list_method, scaling_metrics, measure_dict

def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)
    p.add_argument('in_csv',
                   help = 'CSV diffusion data (.csv).')
    p.add_argument('--out_name',
                   help='Filename prefix to save csv outputs (name_*).')
    p.add_argument('--out_dir',
                   help='Output directory to save CSV files. ')

    filtering = p.add_argument_group(title = 'Filtering options')
    filtering.add_argument('--rm_sid',
                          help='List of subjects to remove. ')
    filtering.add_argument('--rm_bundle',
                          help='List of bundles to remove.')
    filtering.add_argument('--rm_measure',
                          help='List of measures to remove. ')
    filtering.add_argument('--rm_stats',
                          help='List of statistics to remove. ')
    filtering.add_argument('--rm_section', type=int,
                          help='List of sections to remove. ')

    set_shape = p.add_argument_group(title = 'CSV shape options')
    set_shape.add_argument('--rename_measure', action='store_true',
                           help='Rename MRI measures. ')
    set_shape.add_argument('--rename_bundles', action='store_true',
                           help='Rename MRI measures. ')
    set_shape.add_argument('--split_by_method', action='store_true',
                           help='Rename MRI measures. ')
    set_shape.add_argument('--apply_factor', type=int,
                           help='Factor applied on MRI measure for plot. '
                                ' By default, is applied on Diffusion Measure.')
    set_shape.add_argument('--merge_lr', action='store_true',
                           help='Averaged left and right bundle values (mean). ')


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

    # Load Data frame
    df = pd.read_csv(args.in_csv)

    # Drop index column and rename some pattern fron columns
    df.drop('Unnamed: 0', axis =1, inplace=True)
    df['metrics'] = df.metrics.replace('_metric','', regex=True)
    df['metrics'] = df.metrics.replace('min_','', regex=True)
    df['stats'] = df.stats.replace('_length','', regex=True)
    df['section'] = df.section.replace(np.nan,0, regex=True)
    df['section'] = df['section'].astype('Int64')


    if args.merge_lr:
        df['roi']=df.roi.replace('_L','',regex=True)
        df['roi']=df.roi.replace('_R','',regex=True)

        df = df.groupby(['sid','roi','metrics','stats','section'])['value'].mean().reset_index()
    else:
        df['roi']=df.roi.replace('_L','_Left',regex=True)
        df['roi']=df.roi.replace('_R','_Right',regex=True)

    for idx, metric in enumerate(list_metrics):
        df.loc[df.metrics.isin(metric),'Method']=list_method[idx]

    ## Filtering dataframe
    if args.rm_sid:
        for subject in args.rm_sid:
            df = df.loc[~df['sid'].str.contains(subject)]

    if args.rm_bundle:
        for bundle in args.rm_bundle:
            df = df.loc[~df['roi'].str.contains(bundle)]

    if args.rm_measure:
        for measure in args.rm_measure:
            df = df.loc[~df['metrics'].str.contains(measure)]

    if args.rm_section:
        for section in args.rm_section:
            df = df.loc[~df['section'].str.contains(section)]

    if args.rename_measure:
        # check lists
        missing_metric = []
        for metric_item in df['metrics'].unique():
            if metric_item not in measure_dict:
                missing_metric.append(metric_item)

        if len(missing_metric) > 0:
            print("The listed metrics don't match with the default "
                  "metrics list.\nYou can add unknow metrics in "
                  " ALL requiring lists in utils.py.\n", missing_metric)
        else:
            df=df.replace({"metrics": measure_dict})

    # Remove the underscore from Bundle name
    if args.rename_bundles:
        df['roi']=df.roi.replace('_',' ',regex=True)

    # Apply a scale foactor for diffusion measure
    if args.apply_factor:
        for curr_metric in (scaling_metrics):
            #tmp_met = []
            tmp_met = df[(df.metrics == curr_metric) & (df.stats == 'mean')]
            if tmp_met.empty is not True:
                df.loc[(df.metrics == curr_metric) & (df.stats == 'mean'), 'value'] = tmp_met['value'] * args.apply_factor

    # Extract Dataframes
    # Average data
    average = df[df['section'] == 0]
    average.drop('section', axis = 1, inplace = True)
    average = average.rename(columns = {'value':'Value','metrics': 'Measures',
                                       'stats':'Statistics','roi':'Bundles',
                                       'sid':'Sid'})
    average = average.sort_values(by = ['Bundles','Method','Measures'])
    average = average.reset_index(drop=True)

    # profile data
    profile = df[df['section'] > 0]
    profile = profile.rename(columns = {'value':'Value','metrics': 'Measures',
                                        'stats':'Statistics','roi':'Bundles',
                                        'section':'Section','sid':'Sid'})
    profile = profile.sort_values(by = ['Method','Section'])
    profile = profile.reset_index(drop=True)

    ## Save new dataframes
    if args.split_by_method:
        for curr_method in average['Method'].unique():
            af_to_save = average[average['Method'] == curr_method]
            af_to_save = af_to_save.reset_index(drop=True)
            af_to_save.to_csv(os.path.join(args.out_dir,args.out_name +
                                          'average_' + curr_method + '.csv'))
            pf_to_save = profile[profile['Method'] == curr_method]
            pf_to_save = pf_to_save.reset_index(drop=True)
            pf_to_save.to_csv(os.path.join(args.out_dir, args.out_name +
                                          'profile_' + curr_method + '.csv'))
    else:
        average.to_csv(os.path.join(args.out_dir, args.out_name + 'average.csv'))
        profile.to_csv(os.path.join(args.out_dir, args.out_name + 'profile.csv'))



if __name__ == '__main__':
    main()
