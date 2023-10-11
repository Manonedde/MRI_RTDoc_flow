#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
import pandas as pd
import numpy as np

# Convert json

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


def convert_lesion_data(df, colname_with_list, colname_without_list):
    """
    Function for dealing with jsons which, when converted into a
    dataframe, creates lists in columns.
    """
    # extract data with list in column
    df_list = df[df[0].apply(lambda x: isinstance(x, list))]
    # Split columns with list into multiple rows
    df_list = df_list.explode(0).reset_index(drop=True)
    # Attribute labels to each lesion
    for roi in df_list['index'].unique():
        df_list.loc[df_list['index'] == roi,'tmp'] = np.arange(
                            len(df_list[df_list['index'] == roi])) + 1
    # Associate label to first column
    df_list['index'] = df_list['index'
                        ] + '.' + df_list['tmp'].astype(int).astype(str)
    # Remove useless column
    df_list.drop('tmp', axis=1, inplace=True)
    # Split index into multiple columns
    values_with_list = [split_col(x) for x in df_list[["index", 0]].values]
    df_lesion_with_list = pd.DataFrame(columns = colname_with_list,
                                       data = values_with_list)

    # lesion json without list
    df_nolist = df[~(df[0].apply(lambda x: isinstance(x, list)))]
    values_without_list = [split_col(x) for x in df_nolist[["index", 0]].values]
    df_lesion_without_list = pd.DataFrame(columns = colname_without_list,
                                          data = values_without_list)

    return pd.concat([df_lesion_with_list, df_lesion_without_list],
                     ignore_index=True, sort=False)


def apply_factor_to_metric(df, metric, factor, column = 'metrics'):
    tmp_met = df[(df[column] == metric) & (df.stats == 'mean')]
    if tmp_met.empty is not True:
        df.loc[(df[column] == metric) & (df.stats == 'mean'),
                'value'] = tmp_met['value'] * factor


def merged_left_right_data(df, group_col):
    """
    Function to merge left and right data.
    """
    if 'lesion_label' in df.columns.tolist():
        lesion_label = df.loc[df.metrics == 'lesion_volume']

    df['roi'] = df.roi.replace({'_L':'','_R':''}, regex=True)

    # Diffusion data = group by mean()
    diffusions = df.loc[~(df.Method.isin(['Lesion','Streamlines']))]
    diffusions = diffusions.groupby(group_col)['value'].mean().reset_index()

    # Volume data = group by sum() of left and right volumes
    volumes = df.loc[df.Method.isin(['Lesion','Streamlines'])]
    volumes = volumes.groupby(group_col)['value'].sum().reset_index()

    if 'lesion_label' in df.columns.tolist():
        return pd.concat([diffusions, volumes, lesion_label],
                          ignore_index=True, sort=False)
    else:
        return pd.concat([diffusions, volumes],
                          ignore_index=True, sort=False)



def merged_csv(df1, df2, label1, label2, colname):
    df1[colname] = label1
    df2[colname] = label2
    return pd.concat([df1,df2], ignore_index=True, sort=False)


def compute_ecvf_from_df(df):
    """
    Compute ECVF metrics using ICVF (1-ICVF) from dataframe.
    Not recommanded. Please use the scil_compute_ecvf.py .'
    """
    tmp = df[df.Measures == 'ICVF']
    tmp['Measures']= 'ECVF'
    tmp['Value_tmp']= 1 - tmp['Value']
    tmp['Value'] = tmp['Value_tmp']
    tmp.drop('Value_tmp', axis=1, inplace=True)
    df = pd.concat([df,tmp])
    return df.reset_index(drop=True)


def filter_df(df, column, filter):
    """
    Function to filter dataframe based on column and filter.
    """
    df_filter = df[df[column] == filter]
    return df_filter.reset_index(drop=True)


def extract_average_and_profile(df):
    """
    Function written for Stefano specific plots
    """
    # average data
    average = df[df['Section'] == 0]
    average.drop('Section', axis=1, inplace=True)
    average = average.sort_values(by=['Bundles', 'Method', 'Measures'])

    # profile data
    profile = df[df['Section'] > 0]
    profile = profile.sort_values(by=['Method', 'Section'])

    return average.reset_index(drop=True), profile.reset_index(drop=True)


def prepare_df_for_plots(df):
        """
        Function written for Stefano specific plots
        """
        df.drop('Unnamed: 0', axis=1, inplace=True)
        df = df[df['Statistics'] == 'mean']
        df = df[~(df['Method'] == 'Streamlines')]
        rm_metric = ['AFD','NuFO','RDF','AFD_sum','APower']
        for metric in rm_metric:
            df = df[~(df['Measures'] == metric)]
        df = df[~(df['Bundles'] == 'CR')]

        df=df.loc[~(df.Sid == 'sub-003-hc_ses-2')]
        df.loc[(df.Sid == 'sub-003-hc_ses-3'), 'Sid'] = 'sub-003-hc_ses-2'
        df.loc[(df.Sid == 'sub-003-hc_ses-4'), 'Sid'] = 'sub-003-hc_ses-3'
        df.loc[(df.Sid == 'sub-003-hc_ses-5'), 'Sid'] = 'sub-003-hc_ses-4'
        df.loc[(df.Sid == 'sub-003-hc_ses-6'), 'Sid'] = 'sub-003-hc_ses-5'

        df.loc[~(df.Sid == 'sub-010-ms_ses-5')]
        df.loc[(df.Sid == 'sub-010-ms_ses-6'), 'Sid'] = 'sub-010-ms_ses-5'

        df = compute_ecvf_from_df(df)

        df[['Sid2','Session']] = df['Sid'].str.split('_ses-', 1,expand=True)
        df.drop(['Sid','Statistics','rbx_version'], axis=1, inplace=True)
        df=df.rename(columns={'Sid2':'Sid'})

        rm_sid = ['sub-009-hc', 'sub-013-hc', 'sub-017-hc','sub-025-hc','sub-001-ms','sub-021-ms']
        for sbj in rm_sid:
            df = df[~(df['Sid'] == sbj)]

        return df.reset_index(drop=True)
