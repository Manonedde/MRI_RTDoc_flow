#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to prepare a csv file output from Imeka dmri-human
to build html figures for the Read the Doc site.
"""

import argparse
import os
import pandas as pd
import numpy as np

from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist

from utils import (list_metrics, list_method, scaling_metrics, measure_dict,
                   columns_rename, replace_bundles_dict)

def _build_arg_parser():
    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)
    p.add_argument('in_csv',
                   help = 'CSV MRI data (.csv).')
    p.add_argument('--out_name',
                   help='Filename prefix to save csv outputs (name_*).')
    p.add_argument('--out_dir',
                   help='Output directory to save CSV files. ')
    p.add_argument('--longitudinal', action='store_true',
                   help='Use this option if data is longitudinal. ')
    p.add_argument('--groups', action='store_true',
                   help='Use this option if data contains groups. ')

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
    set_shape.add_argument('--apply_factor', type=int, default=100,
                           help='Factor applied on MRI measure for plot. '
                                ' By default, is applied on Diffusion Measure'
                                ' [%(default)s].')
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
        args.out_name = (os.path.splitext(os.path.basename(args.in_csv))[0])

    # Load Data frame
    specific_cols=['dwi_id','roi','roi_src','sid','endpoint', 'value']
    merge_cols = ['sid','Bundles','endpoint','Section','rbx_version',
                  'Category_wm','Category_metrics']

    if (args.longitudinal & args.groups):
        specific_cols=['dwi_id','roi','roi_src','sid','endpoint', 'value',
                       'timepoint','grouping']
        merge_cols = ['sid','Bundles','endpoint','Section','timepoint',
                      'grouping','rbx_version','Category_wm','Category_metrics']
    if args.longitudinal:
        specific_cols=['dwi_id','roi','roi_src','sid','endpoint', 'value',
                       'timepoint']
        merge_cols = ['sid','Bundles','endpoint','Section','timepoint',
                      'rbx_version','Category_wm','Category_metrics']
    if args.groups:
        specific_cols=['dwi_id','roi','roi_src','sid','endpoint', 'value',
                       'grouping']
        merge_cols = ['sid','Bundles','endpoint','Section','grouping',
                      'rbx_version','Category_wm','Category_metrics']

    df = pd.read_csv(args.in_csv, usecols=specific_cols)

    df[['tmp', 'Section']] = df.roi.str.extract('(.*)__(.*)',expand=True)
    df.drop(['tmp'], axis=1, inplace=True)
    df['Section'] = df['Section'].astype('float').astype('Int64')
    # replace NaN i.e. non section by 0
    df['Section']=df['Section'].replace(np.nan,0).astype('Int64')

    df.loc[~(df['roi_src'].str.contains('lesion|healthy')) &
            (df['roi_src'].str.contains('_safe')), 'Category_wm'] = 'safe'
    df.loc[(df['roi_src'].str.contains('lesion')) &
            ~(df['roi_src'].str.contains('_safe|safe_')), 'Category_wm'] = 'lesion'
    df.loc[~(df['roi_src'].str.contains('lesion')) &
            (df['roi_src'].str.contains('healthy')) &
            (df['roi_src'].str.endswith('_safe')), 'Category_wm'] = 'healthy_safe'
    df.loc[~(df['roi_src'].str.contains('lesion')) &
            (df['roi_src'].str.contains('safe')) &
            (df['roi_src'].str.endswith('_healthy')), 'Category_wm'] = 'safe_healthy'
    df.loc[~(df['roi_src'].str.contains('healthy')) &
            (df['roi_src'].str.contains('lesion')) &
            (df['roi_src'].str.endswith('_safe')), 'Category_wm'] = 'lesion_safe'
    df.loc[~(df['roi_src'].str.contains('healthy')) &
            (df['roi_src'].str.contains('safe')) &
            (df['roi_src'].str.endswith('_lesion')), 'Category_wm'] = 'safe_lesion'
    df.loc[(df['roi_src'].str.contains('healthy')) &
            ~(df['roi_src'].str.contains('safe|lesion')), 'Category_wm'] = 'healthy'
    df['Category_wm']=df['Category_wm'].replace(np.nan,'full')
    #df['Category_wm']=df.Category_wm.replace(replace_bundles_dict, regex=True) ## too long and memory consuming

    df.loc[df.endpoint.str.contains('volume'),'Category_metrics'] = 'volume'
    df.loc[~df.endpoint.str.contains('volume'),'Category_metrics'] = 'metric'

    remove_text = ['_healthy_safe','_safe_lesion','_safe_healthy',
                   '_lesion_safe','_safe','_v10_safe','_v10','_healthy',
                   '_lesion','_lesions_penumbra_6','_lesions_penumbra_4',
                   '_lesions_penumbra_2','_full_lesions','_T1_hypo_lesions',
                   '_New_T2_lesions','_T2_lesions']

    #df['Bundles'] = df['roi_src']
    for reg_text in remove_text:
        df['Bundles']=df.roi_src.replace(reg_text,'',regex=True)

    df.loc[df.roi_src.isin(['_v10','_v10_']),'rbx_version']= 'v10'
    df.loc[~df.roi_src.isin(['_v10','_v10_']),'rbx_version']= 'v1'

    if args.merge_lr:
        df['roi_src']=df.roi_src.replace('_L','',regex=True)
        df['roi_src']=df.roi_src.replace('_R','',regex=True)

        df = df.groupby(merge_cols)['value'].mean().reset_index()
    else:
        df['roi_src']=df.roi_src.replace('_L','_Left',regex=True)
        df['roi_src']=df.roi_src.replace('_R','_Right',regex=True)

    for idx, metric in enumerate(list_metrics):
        df.loc[df.endpoint.isin(metric),'Method']=list_method[idx]

    ## Filtering dataframe
    if args.rm_sid:
        for subject in args.rm_sid:
            df = df.loc[~df['sid'].str.contains(subject)]

    if args.rm_bundle:
        for bundle in args.rm_bundle:
            df = df.loc[~df['Bundles'].str.contains(bundle)]

    if args.rm_measure:
        for measure in args.rm_measure:
            df = df.loc[~df['endpoint'].str.contains(measure)]

    if args.rm_section:
        for section in args.rm_section:
            df = df.loc[~df['Section'].str.contains(section)]

    if args.rename_measure:
        # check lists
        missing_metric = []
        for metric_item in df['endpoint'].unique():
            if metric_item not in measure_dict:
                missing_metric.append(metric_item)

        if len(missing_metric) > 0:
            print("The listed metrics don't match with the default "
                  "metrics list.\nYou can add unknow metrics in "
                  " ALL requiring lists in utils.py.\n", missing_metric)
        else:
            df=df.replace({"endpoint": measure_dict})

    # Remove the underscore from Bundle name
    if args.rename_bundles:
        df['Bundles']=df.Bundles.replace('_',' ',regex=True)

    # Apply a scale foactor for diffusion measure
    if args.apply_factor:
        for curr_metric in (scaling_metrics):
            #tmp_met = []
            tmp_met = df[(df.endpoint == curr_metric)]
            if tmp_met.empty is not True:
                df.loc[(df.endpoint == curr_metric), 'value'] = tmp_met['value'] * args.apply_factor

    # Extract Dataframes
    # Average data
    average = df[df['Section'] == 0]
    average.drop('Section', axis = 1, inplace = True)
    average = average.rename(columns = columns_rename)
    average = average.sort_values(by = ['Bundles','Method','Measures'])
    average = average.reset_index(drop=True)

    # profile data
    profile = df[df['Section'] > 0]
    profile = profile.rename(columns = columns_rename)
    profile = profile.sort_values(by = ['Bundles','Method','Section'])
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
        average.to_csv(os.path.join(args.out_dir, args.out_name + '_average.csv'))
        profile.to_csv(os.path.join(args.out_dir, args.out_name + '_profile.csv'))


if __name__ == '__main__':
    main()
