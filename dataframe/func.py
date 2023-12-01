#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

# Convert json


def split_col(x):
    cols, value = x
    parse_val = *cols.split("."), value
    return parse_val


def get_row_name_from_col(df, col_name):
    return df[col_name].unique().tolist()

# Reshpae long type CSV to wide format


def reshape_to_wide_format(long_format_df, selected_cols):
    col_name = copy.deepcopy(selected_cols)
    wide_format = long_format_df.pivot(index=selected_cols,
                                       columns="stats")
    wide_format = wide_format.reset_index(drop=True)
    measure_names = wide_format['value'].columns.tolist()
    wide_format.columns = wide_format.columns.droplevel()
    wide_format.columns = col_name + measure_names
    return wide_format


def convert_lesion_data(df, colname_with_list, colname_without_list):
    """
    Function to deal with jsons which, when converted into a
    dataframe, creates lists in columns. For now, it's specific to
    lesion_jsons output from tractometry_flow.
    """
    # extract data with list in column
    df_list = df[df[0].apply(lambda x: isinstance(x, list))]
    # Split columns with list into multiple rows
    df_list = df_list.explode(0).reset_index(drop=True)
    # Attribute labels to each lesion
    for roi in df_list['index'].unique():
        df_list.loc[df_list['index'] == roi, 'tmp'] = np.arange(
            len(df_list[df_list['index'] == roi])) + 1
    # Associate label to first column
    df_list['index'] = df_list['index'
                               ] + '.' + df_list['tmp'].astype(int).astype(str)
    # Remove useless column
    df_list.drop('tmp', axis=1, inplace=True)
    # Split index into multiple columns
    values_with_list = [split_col(x) for x in df_list[["index", 0]].values]
    df_lesion_with_list = pd.DataFrame(columns=colname_with_list,
                                       data=values_with_list)

    # lesion json without list
    df_nolist = df[~(df[0].apply(lambda x: isinstance(x, list)))]
    values_without_list = [split_col(x)
                           for x in df_nolist[["index", 0]].values]
    df_lesion_without_list = pd.DataFrame(columns=colname_without_list,
                                          data=values_without_list)

    return pd.concat([df_lesion_with_list, df_lesion_without_list],
                     ignore_index=True, sort=False)


def apply_factor_to_metric(df, metric, factor, column='metrics'):
    tmp_met = df[(df[column] == metric) & (df.stats == 'mean')]
    if tmp_met.empty is not True:
        df.loc[(df[column] == metric) & (df.stats == 'mean'),
               'value'] = tmp_met['value'] * factor


def merged_left_right_data(df, group_col):
    """
    Function to merge left and right data.
    For lesion, volume not mean but sum() between left and right.
    """
    if 'lesion_label' in df.columns.tolist():
        lesion_label = df.loc[df.metrics == 'lesion_volume']

    df['roi'] = df.roi.replace({'_L': '', '_R': ''}, regex=True)

    # Diffusion data = group by mean()
    diffusions = df.loc[~(df.Method.isin(['Lesion']))]
    diffusions = diffusions.groupby(group_col)['value'].mean().reset_index()

    # Volume data = group by sum() of left and right volumes
    volumes = df.loc[df.Method.isin(['Lesion'])]
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
    return pd.concat([df1, df2], ignore_index=True, sort=False)


def compute_ecvf_from_df(df, select_column='metrics'):
    """
    Compute ECVF metrics using ICVF (1-ICVF) from dataframe.
    Not recommanded. Please use the scil_compute_ecvf.py .'
    """
    tmp = df[df[select_column] == 'ICVF']
    tmp['metrics'] = 'ECVF'
    tmp['value_tmp'] = 1 - tmp['value']
    tmp['value'] = tmp['value_tmp']
    tmp.drop('value_tmp', axis=1, inplace=True)
    df = pd.concat([df, tmp])
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

# Used for imeka dataframe
def prepare_df_for_plots(df):
    """
    Function written for Stefano specific plots
    """
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df = df[df['Statistics'] == 'mean']
    df = df[~(df['Method'] == 'Streamlines')]
    rm_metric = ['AFD', 'NuFO', 'RDF', 'AFD_sum', 'APower']
    for metric in rm_metric:
        df = df[~(df['Measures'] == metric)]
    df = df[~(df['Bundles'] == 'CR')]

    df = df.loc[~(df.Sid == 'sub-003-hc_ses-2')]
    df.loc[(df.Sid == 'sub-003-hc_ses-3'), 'Sid'] = 'sub-003-hc_ses-2'
    df.loc[(df.Sid == 'sub-003-hc_ses-4'), 'Sid'] = 'sub-003-hc_ses-3'
    df.loc[(df.Sid == 'sub-003-hc_ses-5'), 'Sid'] = 'sub-003-hc_ses-4'
    df.loc[(df.Sid == 'sub-003-hc_ses-6'), 'Sid'] = 'sub-003-hc_ses-5'

    df.loc[~(df.Sid == 'sub-010-ms_ses-5')]
    df.loc[(df.Sid == 'sub-010-ms_ses-6'), 'Sid'] = 'sub-010-ms_ses-5'

    df = compute_ecvf_from_df(df)

    df[['Sid2', 'Session']] = df['Sid'].str.split('_ses-', 1, expand=True)
    df.drop(['Sid', 'Statistics', 'rbx_version'], axis=1, inplace=True)
    df = df.rename(columns={'Sid2': 'Sid'})

    rm_sid = ['sub-009-hc', 'sub-013-hc', 'sub-017-hc', 'sub-025-hc',
              'sub-001-ms', 'sub-021-ms']
    for sbj in rm_sid:
        df = df[~(df['Sid'] == sbj)]

    return df.reset_index(drop=True)


def check_reorder_measure(df, reorder_metrics_list, rm_missing_metrics=False):
    """
    Check if there is concordance between a reorder metrics list and Metrics
    listed in the dataframe.

    df:                     DataFrame
    reorder_metrics_list:   List of metrics in specific order
    rm_missing_metrics:     Boolean. If True the metrics in dataframe not
                            present in the reorder_metrics_list are removed.

    Return                  Error message /or
                            The Dataframe without missing metrics if
                            rm_missing_metrics is True.
    """
    missing_metric = []
    for metric_item in df.Measures.unique():
        if metric_item not in reorder_metrics_list:
            missing_metric.append(metric_item)

    if not missing_metric:
        return df

    if len(missing_metric) != 0:
        if rm_missing_metrics:
            print("With the --filter_measures option the following metrics"
                  " are removed.\n", missing_metric)
            return df.loc[~(df.Measures.isin(
                missing_metric))].reset_index(drop=True)
        else:
            raise ValueError('The listed metrics in df do not match with the'
                             ' default metrics list.\n  Use --custom_reorder'
                             ' option to parse a custom list or use'
                             ' --filter_measures.')


def generate_summary_table(df, by_cols=['Measures', 'Value'], round_at=3,
                           select_stats_col=[
                               'Mean', 'STD', 'Median', 'Min', 'Max','Range'],
                           custom_col_name=False):
    """
    Generate a summary table from Dataframe.

    df :                Dataframe
    by_cols :           Columns name to group dataframe : [condition_colum(s),
                                                           values_column]
                        Condition_columns is the name of the column(s) chosen
                        to group the values. If several columns are used as
                        arguments, provide a list: [['col_1,col_2','col_n'],
                                                     col_values].
                        values_column can contain only one column (stats).
    round_at :          Decimal places after the decimal point
    select_stats_col :  Use to select only certain columns. The order provided
                        will reorganize the table columns accordingly.
                        The complete list is : ['Count', 'Mean', 'STD', 'Min',
                           'Inferior Quartile 25%',  'Median',
                           'Superior Quartile 75%', 'Max', 'Range'].
    custom_col_name :   Use to rename columns corresponding to those in
                        select_stats_col. By default, all columns are renamed.

    Return table that could be save using .to_csv() or .to_latex() function.
    """

    summary_table = np.round(df.groupby(by_cols[0])[by_cols[1]].describe(),
                             round_at)
    summary_table.insert(8, 'range', summary_table['max'] -
                         summary_table['min'])
    print(summary_table)
    
    col_name = ['Count', 'Mean', 'STD', 'Min',
                'Inferior Quartile 25%',  'Median',
                'Superior Quartile 75%', 'Max', 'Range']
    
    if custom_col_name:
        col_name = custom_col_name
    
    summary_table.columns = col_name

    if select_stats_col:
        summary_table = summary_table[select_stats_col]

    return summary_table


def get_multi_corr_map(df, multi_col_arg, pivot_index, pivot_columns,
                       pivot_value, reorder_col=None, post_pearson=None,
                       colbar_title='Pearson r', longitudinal=False):
    corr = []
    for multi_col in df[multi_col_arg].unique().tolist():
        tmp = df.loc[df[multi_col_arg] == multi_col]
        if longitudinal:
            tmp = tmp.groupby([pivot_index,
                               pivot_columns])[pivot_value].mean().reset_index()
        if reorder_col is not None:
            corr_tmp = tmp.pivot(index=pivot_index, columns=pivot_columns,
                                 values=pivot_value
                                 ).reset_index().reindex(columns=reorder_col
                                                         ).corr()
        else:
            corr_tmp = tmp.pivot(index=pivot_index, columns=pivot_columns,
                                 values=pivot_value).reset_index().corr()

        if post_pearson == 'absolute':
            corr_tmp = np.absolute(corr_tmp)
            colbar_title = 'Absolute Pearson r'

        if post_pearson == 'square':
            corr_tmp = np.square(corr_tmp)
            colbar_title = 'Squared Pearson r'

        corr.append(corr_tmp)

    return corr, colbar_title


def get_corr_map(df, pivot_index, pivot_columns, pivot_value,
                 reorder_col=False, post_pearson=None,
                 colbar_title='Pearson r'):

    df = df.groupby([pivot_index,
                     pivot_columns])[pivot_value].mean().reset_index()
    if reorder_col:
        corr = df.pivot(index=pivot_index, columns=pivot_columns,
                        values=pivot_value).reset_index().reindex(
            columns=reorder_col).corr()
    else:
        corr = df.pivot(index=pivot_index, columns=pivot_columns,
                        values=pivot_value).reset_index().corr()
    if post_pearson == 'absolute':
        corr = np.absolute(corr)
        colbar_title = 'Absolute Pearson r'

    if post_pearson == 'square':
        corr = np.square(corr)
        colbar_title = 'Squared Pearson r'

    return corr, colbar_title


def get_subset_data(df, keep_columns=None, select_row_by_colum=None,
                    combine=False, ):
    if keep_columns:
        df = df[keep_columns]

    if select_row_by_colum:
        df.loc[(df.Bundles.isin(['AC_v10', 'UF_v10']))
               & (df.Measures.isin(['AD', 'FA']))]


def get_data_from(df, column_name, row_name):
    return df.loc[df[column_name].isin(row_name)]


def split_df_by(df, col_arg):
    """
    Function to split large Dataframe into multiple smaller dataframe based
    on unique argument on column.

    df:         Dataframe.
    col_arg:    Column name used to split dataframe.

    Returns     Two lists of smaller dataframes and argument names
                whose len() corresponds to the number of unique arguments
                in the selected column.
    """
    split_df, split_name = [], []
    for unique_arg in df[col_arg].unique().tolist():
        split_name.append(unique_arg)
        df_tmp = df.loc[df[col_arg] == unique_arg].reset_index(drop=True)
        split_df.append(df_tmp)
    return split_df, split_name


def pivot_to_wide(df, pivot_index, pivot_columns, pivot_value,
                  longitudinal=False):
    """
    """
    if longitudinal:
        df = df.groupby([pivot_index,
                         pivot_columns])[pivot_value].mean().reset_index()
        df = df.pivot(index=pivot_index, columns=pivot_columns,
                      values=pivot_value).reset_index()
    else:
        df = df.pivot(index=pivot_index, columns=pivot_columns,
                      values=pivot_value).reset_index()
    return df
