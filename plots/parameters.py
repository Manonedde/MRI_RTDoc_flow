#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Set of parameters used to generate plotly figures.
"""

######### Distribution plots setting #####
order_plot_dict = {
                    'DTI': ['FA', 'RD', 'MD', 'AD'],
                    'DTI-FW': [
                        'FA-FWcorrected', 'RD-FWcorrected',
                        'MD-FWcorrected', 'AD-FWcorrected'],
                    'FW': ['FW'],
                    'FODF': ['AFD_total', 'NuFO'],
                    'HARDI': ['GFA', 'APower'],
                    'NODDI': ['ICVF', 'OD', 'ECVF', 'ISOVF'],
                    'MTI': ['ihMTR', 'MTR', 'MTsat', 'ihMTsat'],
                    'Streamlines': ['Volume', 'Count', 'Length']}

average_parameters_dict = {
    "FA": [0, 0.8], "MD": [0, 0.0016], "RD": [0, 0.0016], "AD": [0, 0.0018],
    "FW": [0, 1],
    "FA-FWcorrected": [0, 0.8], "MD-FWcorrected": [0, 0.0012],
    "RD-FWcorrected": [0, 0.0012], "AD-FWcorrected": [0, 0.002],
    "ECVF": [0, 1], "ICVF": [0, 1], "OD": [0, 0.8], "ISOVF": [0, 0.5],
    "AFD_total": [0, 1], "NuFO": [0, 3], "AFD": [0, 2], "AFD_sum": [0, 2],
    "AFD fixel": [0, 1],
    "Radial ODF": [0, 1], "GFA": [0, 0.8], "APower": [0, 10],
    "MTR": [0, 30], "ihMTR": [0, 18], "MTsat": [0, 6], "ihMTsat": [0, 0.4],
    "ihMTdR1sat": [0, 0.4],
    "Volume": [0,250000], "Count": [0, 65000], "Length": [0, 220]}

boxplot_parameters_dict = {
    "FA": [0.25, 0.65], "MD": [0.0005, 0.001], "RD": [0.0004, 0.0008], "AD": [0.0008, 0.0014],
    "FW": [0, 0.1],
    "FA-FWcorrected": [0.3, 0.6], "MD-FWcorrected": [0.0005, 0.001],
    "RD-FWcorrected": [0.0004, 0.0008], "AD-FWcorrected": [0.0008, 0.0014],
    "ECVF": [0, 0.6], "ICVF": [0.2, 0.8], "OD": [0.1, 0.4], "ISOVF": [0, 0.2],
    "AFD_total": [0.1, 0.5], "NuFO": [1.5, 3], "AFD": [0, 2], "AFD_sum": [0, 2],
    "AFD fixel": [0, 1],
    "Radial ODF": [0, 1], "GFA": [0, 0.8], "APower": [0, 10],
    "MTR": [18, 28], "ihMTR": [4, 12], "MTsat": [2, 5], "ihMTsat": [0, 0.2],
    "ihMTdR1sat": [0, 0.4],
    "Volume": [0,250000], "Count": [0, 65000], "Length": [0, 220]}

######### Profile setting #####
order_plot_profile = ['DTI', 'DTI-FW', 'FW', 'FODF', 'HARDI', 'MTI', 'NODDI']
dict_plot_profile = {"DTI": [0, 0.8], "DTI-FW": [0, 0.8], "FW": [0, 0.7],
                     "FODF": [0, 3], "HARDI": [0, 3], "MTI": [0, 30],
                     "NODDI": [0, 1], 'Streamlines': [0, 100000]}

# Reorder heatmap matrice 'ECVF',
new_order_measure = [
    'FA', 'AD', 'MD', 'RD',
    'FA-FWcorrected', 'AD-FWcorrected', 'MD-FWcorrected', 'RD-FWcorrected',
    'FW',
    'AFD_total', 'NuFO',
    'ICVF', 'ISOVF', 'OD', 'ECVF',
    'MTR', 'MTsat', 'ihMTR', 'ihMTsat']

# Metrics color list
metric_colors = {
    'AD': '#FEC840', 'FA': '#EE0000', 'MD': '#C57019', 'RD': '#FE9637',
    'ad': '#FEC840', 'fa': '#EE0000', 'md': '#C57019', 'rd': '#FE9637',
    'AFD_total': '#33cc33', 'NuFO': '#877B04', 'AFD fixel': '#198032',
    'afd_total': '#33cc33', 'nufo': '#877B04', 'afd_along': '#198032',
    'Radial ODF': '#00CCAA', 'radODF': '#00CCAA',
    'ECVF': '#4CBDD5', 'ICVF': '#1395A9', 'ISOVF': '#4CBDD5', 'OD': '#00AEA1',
    'ecvf': '#4CBDD5', 'icvf': '#1395A9', 'isovf': '#4CBDD5', 'od': '#00AEA1',
    'MTR': '#8000FF', 'MTsat': '#A291F3', 'mtr': '#8000FF', 'mtsat': '#A291F3',
    'ihMTR': '#C03EEA', 'ihMTdR1sat': '#FC66AB', 'ihmtr': '#C03EEA',
    'ihmtdR1sat': '#FC66AB', 'ihMTsat': '#FC66AB', 'ihmtsat': '#FC66AB',
    'FW': '#178DFF', 'fw': '#178DFF',
    'AD-FWcorrected': '#E9EC38', 'FA-FWcorrected': '#FC6666',
    'MD-FWcorrected': '#E6891E', 'RD-FWcorrected': '#FEBE17',
    'adt': '#E9EC38', 'fat': '#FC6666', 'mdt': '#E6891E', 'rdt': '#FEBE17',
    'Volume': '#333333', 'Count': '#770302', 'volume': '#333333',
    'count': '#770302', 'length': '#cc3300','Length': '#cc3300'}


# Bundles color list
bundle_dict_color_v1 = {
    "AF": "#368a6b", "AF Left": "#368a6b", "AF Right": "#368a6b",
    "CC 7": "#047b3c", "CC 6": "#00ffea", "CC 5": "#0544c4", "CC 4": "#fa7e08",
    "CC 3": "#82830e", "CC 2b": "#bcbb73", "CC 2a": "#fe8ad5", "CC 1": "#ff4707",
    "CC_7": "#047b3c", "CC_6": "#00ffea", "CC_5": "#0544c4", "CC_4": "#fa7e08",
    "CC_3": "#82830e", "CC_2b": "#bcbb73", "CC_2a": "#fe8ad5", "CC_1": "#ff4707",
    "CG": "#ffff00", "CG Left": "#ffff00", "CG Right": "#ffff00",
    "CG_L": "#ffff00", "CG_R": "#ffff00", "CST": "#1b0385", "CST Left": "#1b0385",
    "CST Right": "#1b0385", "CST_L": "#1b0385", "CST_R": "#1b0385",
    "IFOF": "#f9c306", "IFOF Left": "#f9c306", "IFOF Right": "#f9c306",
    "IFOF_L": "#f9c306", "IFOF_R": "#f9c306", "ILF": "#11d473",
    "ILF Left": "#11d473", "ILF Right": "#11d473", "ILF_L": "#11d473",
    "ILF_R": "#11d473", "SLF 1": "#d9cef5", "SLF 1 Left": "#d9cef5",
    "SLF 1 Right": "#d9cef5", "SLF_1": "#d9cef5", "SLF_1_L": "#d9cef5",
    "SLF_1_R": "#d9cef5", "SLF 2": "#9a82d7", "SLF 2 Left": "#9a82d7",
    "SLF 2 Right": "#9a82d7", "SLF_2": "#9a82d7", "SLF_2_L": "#9a82d7",
    "SLF_2_R": "#9a82d7", "SLF 3": "#615481", "SLF 3 Left": "#615481",
    "SLF 3 Right": "#615481", "SLF_3": "#615481", "SLF_3_L": "#615481",
    "SLF_3_R": "#615481", "OR": "#7ab5af", "OR Left": "#7ab5af",
    "OR Right": "#7ab5af", "OR_L": "#7ab5af", "OR_R": "#7ab5af",
    "UF": "#7541f8", "UF Left": "#7541f8", "UF Right": "#7541f8",
    "UF_L": "#7541f8", "UF_R": "#7541f8", "CR_L": "#a9a9a9", "CR_R": "#a9a9a9",
    "CR": "#a9a9a9", "CR Left": "#a9a9a9", "CR Right": "#a9a9a9",
    "MCP": "#C34095", "ICP": "#400080", "ICP Left": "#400080",
    "ICP Right": "#400080", "ICP_L": "#400080", "ICP_R": "#400080"}

bundle_dict_color_v10 = {
    "AC": "#D31558", "AF": "#368a6b", "AF Left": "#368a6b",
    "AF Right": "#368a6b", "AF_L": "#368a6b", "AF_R": "#368a6b",
    "CC Temporal": "#91F7C0", "CC_Te": "#91F7C0", "CC PrePost": "#B5706F",
    "CC_Pr_Po": "#B5706F", "CC Parietal": "#F75D6A", "CC_Pa": "#F75D6A",
    "CC Occipital": "#7F8F22", "CC_Oc": "#7F8F22",
    "CC Frontal Superior": "#C1BB62", "CC_Fr_1": "#C1BB62",
    "CC Frontal Inferior": "#E7BEF0", "CC_Fr_2": "#E7BEF0", "CG": "#FFFF00",
    "CG Left": "#FFFF00", "CG Right": "#FFFF00", "CG_L": "#FFFF00",
    "CG_R": "#FFFF00", "CG Anterior": "#FFED7F", "CG_An": "#FFED7F",
    "CG Anterior Left": "#FFED7F", "CG_L_An": "#FFED7F",
    "CG Anterior Right": "#FFED7F", "CG_R_An": "#FFED7F", "CG Curve": "#FFEC00",
    "CG_curve": "#FFEC00", "CG Curve Left": "#FFEC00", "CG_L_curve": "#FFEC00",
    "CG Curve Right": "#FFEC00", "CG_R_curve": "#FFEC00",
    "CG Posterior": "#F69A00", "CG_Po": "#F69A00",
    "CG Posterior Left": "#F69A00", "CG_L_Po": "#F69A00",
    "CG Posterior Right": "#F69A00", "CG_R_Po": "#F69A00",
    "FAT": "#A5CCBF", "FAT Left": "#A5CCBF", "FAT Right": "#A5CCBF",
    "FAT_L": "#A5CCBF", "FAT_R": "#A5CCBF", "FTP": "#247DB6",
    "FTP Left": "#247DB6", "FTP Right": "#247DB6", "FTP_L": "#247DB6",
    "FTP_R": "#247DB6", "Fornix": "#191919", "fornix group": "#191919",
    "Fornix Left": "#191919", "Fornix Right": "#191919", "FX": "#191919",
    "FX_L": "#191919", "FX_R": "#191919", "ICP": "#400080",
    "ICP Left": "#400080", "ICP Right": "#400080", "ICP_L": "#400080",
    "ICP_R": "#400080", "IFOF": "#7F6FC1", "IFOF Left": "#7F6FC1",
    "IFOF_L": "#7F6FC1", "IFOF Right": "#7F6FC1", "IFOF_R": "#7F6FC1",
    "ILF": "#11D473", "ILF Left": "#11D473", "ILF_L": "#11D473",
    "ILF Right": "#11D473", "ILF_R": "#11D473", "MCP": "#C34095",
    "MdLF": "#D9CEF5", "MdLF Left": "#D9CEF5", "MdLF_L": "#D9CEF5",
    "MdLF Right": "#D9CEF5", "MdLF_R": "#D9CEF5", "OR": "#95D0CC",
    "OR Left": "#95D0CC", "OR_L": "#95D0CC", "OR Right": "#95D0CC",
    "OR_R": "#95D0CC", "PC": "#ED000A", "POPT": "#2A38F3",
    "POPT Left": "#2A38F3", "POPT_L": "#2A38F3", "POPT Right": "#2A38F3",
    "POPT_R": "#2A38F3", "PYT": "#1B0385", "PYT Left": "#1B0385",
    "PYT_L": "#1B0385", "PYT Right": "#1B0385", "PYT_R": "#1B0385",
    "SCP": "#C6F1EA", "SCP Left": "#C6F1EA", "SCP_L": "#C6F1EA",
    "SCP Right": "#C6F1EA", "SCP_R": "#C6F1EA", "SLF": "#9A82D7",
    "SLF Left": "#9A82D7", "SLF_L": "#9A82D7", "SLF Right": "#9A82D7",
    "SLF_R": "#9A82D7", "UF": "#7541F8", "UF Left": "#7541F8", "UF_L": "#7541F8",
    "UF Right": "#7541F8", "UF_R": "#7541F8"}


replace_bundles_dict = {"AC_": "", "AC": "", "AF_L_": "", "AF_L": "",
                        "AF_R_": "", "AF_R": "", "CC_1_": "", "CC_2a_": "",
                        "CC_2b_": "", "CC_3_": "", "CC_4_": "", "CC_5_": "",
                        "CC_6_": "", "CC_7_": "", "CC_Te_": "", "CC_Fr_1_": "",
                        "CC_Fr_2_": "", "CC_Oc_": "", "CC_Pa_": "",
                        "CC_Pr_Po_": "", "CC_Te_": "", "CC_1": "", "CC_2a": "",
                        "CC_2b": "", "CC_3": "", "CC_4": "", "CC_5": "",
                        "CC_6": "", "CC_7": "", "CC_Te": "", "CC_Fr_1": "",
                        "CC_Fr_2": "", "CC_Oc": "", "CC_Pa": "", "CC_Pr_Po": "",
                        "CC_Te": "", "CG_L_": "", "CG_L": "", "CG_R_": "",
                        "CG_R": "", "CST_L_": "", "CST_L": "", "CST_R_": "",
                        "CST_R": "", "CR_L_": "", "CR_L": "", "CR_R_": "",
                        "CR_R": "", "FAT_L_": "", "FAT_L": "", "FAT_R_": "",
                        "FAT_R": "", "FPT_L_": "", "FPT_L": "", "FPT_R_": "",
                        "FPT_R": "", "FX_L_": "", "FX_L": "", "FX_R_": "",
                        "FX_R": "", "ICP_L_": "", "ICP_L": "", "ICP_R_": "",
                        "ICP_R": "", "IFOF_L_": "", "IFOF_L": "", "IFOF_R_": "",
                        "IFOF_R": "", "ILF_L_": "", "ILF_L": "", "ILF_R_": "",
                        "ILF_R": "", "MCP_": "", "MCP": "", "MdLF_L_": "",
                        "MdLF_L": "", "MdLF_R_": "", "MdLF_R": "",
                        "OR_ML_L_": "", "OR_ML_L": "", "OR_ML_R_": "",
                        "OR_ML_R": "", "OR_L_": "", "OR_L": "", "OR_R_": "",
                        "OR_R": "", "PC_": "", "PC": "", "POPT_L_": "",
                        "POPT_L": "", "POPT_R_": "", "POPT_R": "", "PYT_L_": "",
                        "PYT_L": "", "PYT_R_": "", "PYT_R": "", "SCP_L_": "",
                        "SCP_L": "", "SCP_R_": "", "SCP_R": "", "SLF_L_": "",
                        "SLF_L": "", "SLF_R_": "", "SLF_R": "", "SLF_1_L_": "",
                        "SLF_1_L": "", "SLF_1_R_": "", "SLF_1_R": "",
                        "SLF_2_L_": "", "SLF_2_L": "", "SLF_2_R_": "",
                        "SLF_2_R": "", "SLF_3_L_": "", "SLF_3_L": "",
                        "SLF_3_R_": "", "SLF_3_R": "", "UF_L_": "",
                        "UF_L": "", "UF_R_": "", "UF_R": ""}
