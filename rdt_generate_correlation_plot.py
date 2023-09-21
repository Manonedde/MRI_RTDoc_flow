#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to identify each lesion with individual label.
"""

import argparse
import copy
import os
import pandas as pd
import numpy as np

from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.express as px


from scilpy.io.image import get_data_as_mask
from scilpy.io.utils import add_overwrite_arg, assert_inputs_exist
from scipy.ndimage import label


df = pd.read_csv('/home/local/USHERBROOKE/eddm3601/Dropbox/IMEKA/DATA/ROC001/Data_subjects/20220412_roc001_database.csv')

for rm_metric in ['volume','afd_sum','afd_along','adt','rdt','fat','fw','mdt','gfa','apower','rdf', 'qsm','radfODF']:
    df=df.loc[~df['endpoint'].str.contains(rm_metric)]

df=df.loc[~df['grouping'].str.contains('MS')]
df=df.loc[~df['roi_src'].str.contains('_lesion')]
dfh=df.loc[~df['roi'].str.contains('__')]

dfh2=dfh.loc[dfh['roi'].str.contains('healthy')]
dfh2=dfh2.loc[~(dfh2['roi'] == '_healthy')]

dfh2['roi']=dfh2.roi.replace('_healthy','', regex=True)
dfh2['roi']=dfh2.roi.replace('_L','',regex=True)
dfh2['roi']=dfh2.roi.replace('_R','',regex=True)

tmp = dfh2.groupby(['dwi_id','roi','endpoint'])['value'].mean().reset_index()

tmp=tmp.loc[~tmp['dwi_id'].str.contains('sub-016')]
tmp=tmp.loc[~tmp['dwi_id'].str.contains('sub-009')]
tmp=tmp.loc[~tmp['dwi_id'].str.contains('sub-013')]
tmp=tmp.loc[~tmp['dwi_id'].str.contains('sub-017')]
tmp=tmp.loc[~tmp['dwi_id'].str.contains('sub-025')]

tmp['endpoint']=tmp.endpoint.replace('fa','FA',regex=True)
tmp['endpoint']=tmp.endpoint.replace('md','MD',regex=True)
tmp['endpoint']=tmp.endpoint.replace('rd','RD',regex=True)
tmp['endpoint']=tmp.endpoint.replace('ad','AD',regex=True)
tmp['endpoint']=tmp.endpoint.replace('ecvf','ECvf',regex=True)
tmp['endpoint']=tmp.endpoint.replace('icvf','ICvf',regex=True)
tmp['endpoint']=tmp.endpoint.replace('od','OD',regex=True)
tmp['endpoint']=tmp.endpoint.replace('isovf','ISOvf',regex=True)
tmp['endpoint']=tmp.endpoint.replace('afd_total','AFD total',regex=True)
tmp['endpoint']=tmp.endpoint.replace('nufo','NuFO',regex=True)
tmp['endpoint']=tmp.endpoint.replace('ihMTsat','ihMTdR1sat',regex=True)
tmp=tmp.loc[~(tmp['endpoint'] == 'afd')]


tmp2 = copy.deepcopy(tmp)
ecvf = tmp2[tmp2['endpoint'] == 'ICvf']
ecvf['evalue'] = 1 - ecvf['value']
ecvf
ecvf.drop('value', axis=1, inplace=True)
ecvf['endpoint'] = 'ECvf'
ecvf=ecvf.rename(columns={'evalue':'value'})
ecvf
tmpf = pd.concat([tmp2,ecvf])

tmpf['Bundles']=tmpf.Bundles.replace('CC2a','CC 2a',regex=True)
tmpf['Bundles']=tmpf.Bundles.replace('CC2b','CC 2b',regex=True)
tmpf['Bundles']=tmpf.Bundles.replace('CC3','CC 3',regex=True)
tmpf['Bundles']=tmpf.Bundles.replace('CC4','CC 4',regex=True)
tmpf['Bundles']=tmpf.Bundles.replace('CC5','CC 5',regex=True)
tmpf['Bundles']=tmpf.Bundles.replace('CC6','CC 6',regex=True)
tmpf['Bundles']=tmpf.Bundles.replace('CC7','CC 7',regex=True)
tmpf['Bundles']=tmpf.Bundles.replace('SLF1','SLF 1',regex=True)
tmpf['Bundles']=tmpf.Bundles.replace('SLF2','SLF 2',regex=True)
tmpf['Bundles']=tmpf.Bundles.replace('SLF3','SLF 3',regex=True)

tmpf=tmpf.loc[~tmpf['Bundles'].str.contains('CR')]
tmpf=tmpf.loc[~tmpf['Bundles'].str.contains('ICP')]
tmpf=tmpf.loc[~tmpf['Bundles'].str.contains('MCP')]
tmpf=tmpf.loc[~tmpf['Bundles'].str.contains('CC1')]

bundle_list_title=['AF', 'CC 2a', 'CC 2b', 'CC 3', 'CC 4', 'CC 5', 'CC 6', 'CC 7', 'CG', 'CST', 'IFOF', 'ILF', 'OR', 'SLF 1','SLF 2', 'SLF 3', 'UF']
bundle_list=['AF', 'CC_2a', 'CC_2b', 'CC_3', 'CC_4', 'CC_5', 'CC_6', 'CC_7', 'CG', 'CST', 'IFOF', 'ILF', 'OR', 'SLF_1','SLF_2', 'SLF_3', 'UF']
outpath = '/home/local/USHERBROOKE/eddm3601/Dropbox/Collaborations/Roche-SCIL/Web_supplementary/results/correlations_zip'

for idx, bundle in enumerate(bundle_list_title):
    bdl = tmpf[tmpf['Bundles'] == bundle]
    bdl=bdl.pivot(index='Subject',columns='Measures', values='value')
    metric_list=bdl.columns.tolist()

    for i in metric_list:
        for j in metric_list:
            if i != j:
                x=bdl[i]
                y=bdl[j]
                # pearson correlation
                slope, intercept, r, p, stderr = scipy.stats.linregress(x, y)
                line = f'Pearson coefficient: r={r:.2f}, p={p:.2f}'
                figtitle = bundle + ' - Correlation between '+ i + ' and ' + j

                scatter_with_regression_line(x,y, intercept + slope * x,
                                             xlabel=i, ylabel=j,
                                             marker_color='#FFFFFF',
                                             marker_edgecolors='#0066cc',
                                             line_label=line,
                                             line_color='#ff0000',
                                             figtitle=figtitle)
                curr_foler = bundle_list[idx]
                outname=bundle_list[idx] + '_' + i + '_' + j + '_Pearson_Correlation.png'
                plt.savefig(os.path.join(outpath,curr_foler,outname),
                            dpi=500, bbox_inches='tight')
                #plt.savefig(os.path.join(outpath_ms,outname), dpi=500, bbox_inches='tight')
                plt.close('all')


if __name__ == '__main__':
    main()
