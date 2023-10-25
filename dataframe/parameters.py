#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Convert json utils

column_dict_name = {"lesion_load_per_point": [["sid", "roi", "metrics", "section",
                                              "lesion_label", "value"],
                                              ["sid", "roi", "metrics", "section",
                                              "lesion_label"]],
                    "lesion_load": [["sid", "roi", "metrics", "lesion_label",
                                     "value"],
                                    ["sid", "roi", "metrics", "lesion_label"]],
                    "mean_std": [["sid", "roi", "metrics", "stats", "value"],
                                 ["sid", "roi", "metrics"]],
                    "mean_std_per_point": [["sid", "roi", "metrics", "section",
                                            "stats", "value"],
                                           ["sid", "roi", "metrics", "section"]],
                    "streamline_count": [["sid", "roi", "metrics", "value"],
                                         ['sid', 'roi', 'metrics']],
                    "length_stats": [["sid", "roi", "metrics", "value"],
                                     ['sid', 'roi', 'metrics']],
                    "volume": [["sid", "roi", "metrics", "value"],
                               ['sid', 'roi', 'metrics']],
                    "volume_per_label": [["sid", "roi", "metrics", "section",
                                          "value"],
                                         ["sid", "roi", "metrics", "section"]],
                    "lesion_load_per_point_nolist": [["sid", "roi", "metrics",
                                                      "section", "value"],
                                                     ["sid", "roi", "metrics",
                                                     "section"]],
                    "lesion_load_nolist": [["sid", "roi", "metrics", "value"],
                                           ['sid', 'roi', "metrics"]]}


# Metrics renaming
measure_dict = {"radfODF": 'Radial_fODF', "fa": 'FA', "md": 'MD', "rd": 'RD',
                "ad": 'AD', "gfa": "GFA",
                "fw": 'FW', "fat": 'FA-FWcorrected', "mdt": 'MD-FWcorrected',
                "rdt": 'RD-FWcorrected', "adt": 'AD-FWcorrected',
                "icvf": 'ICVF', "od": 'OD', "isovf": 'ISOVF', "ecvf": 'ECVF',
                "afd_total": 'AFD_total', "afd_along": 'AFD_fixel',
                "afd_sum": "AFD_sum", "nufo": 'NuFO',
                "MTR": 'MTR', "ihMTR": 'ihMTR', "MTsat": 'MTsat',
                "ihMTsat": 'ihMTsat', "ihMTdR1sat": 'ihMTdR1sat',
                "rdf": "RDF", "qsm": "QSM", "afd": "AFD", "apower": "APower",
                "volume": 'Volume', "streamline": 'Count',
                "length": 'Length', 'lesion': "Lesion",
                'lesion_total': 'Lesion_total'}


list_metrics = [['NuFO', 'nufo', 'AFD_total', 'afd_total', 'AFD_fixel', 'afd_along',
                 'Radial_fODF', 'radfODF', 'afd', 'AFD', 'AFD_sum', 'afd_sum'],
                ['FA', 'AD', 'RD', 'MD', 'fa', 'ad', 'rd', 'md'],
                ['FA-FWcorrected', 'MD-FWcorrected', 'RD-FWcorrected',
                 'AD-FWcorrected', 'fat', 'mdt', 'rdt', 'adt'],
                ['FW', 'fw'],
                ['ECVF', 'ICVF', 'ISOVF', 'OD', 'ecvf', 'icvf', 'isovf', 'od'],
                ['MTR', 'MTsat', 'ihMTR', 'ihMTdR1sat', 'ihMTsat', 'mtr', 'mtsat',
                 'ihmtr', 'ihmtsat', 'ihmtdR1sat'],
                ['APower', 'apower', 'GFA', 'gfa'],
                ['RDF', 'rdf', 'QSM', 'qsm'],
                ['Volume', 'Count', 'volume', 'streamline',
                 'Length', 'length'],
                ['lesion', "Lesion",
                'lesion_total', 'Lesion_total']]

list_method = ['FODF',
               'DTI',
               'DTI-FW',
               'FW',
               'NODDI',
               'MTI',
               'HARDI',
               'QSM',
               'Streamlines',
               'Lesion']


scaling_metrics = ['AD', 'RD', 'MD', 'ad', 'rd', 'md', 'mdt', 'rdt', 'adt',
                   'MD-FWcorrected', 'RD-FWcorrected', 'AD-FWcorrected']

replace_dict = {'roi': ['_labels', '_v10_labels', '_v10'],
                'metrics': ['_metric', 'min_', 'mean_', 'max_', 'std_', '_volume', '_count'],
                'stats': ['_length', 'lesion_total_', 'lesion_', 'streamline_']}

col_order = ['sid', 'roi', 'metrics', 'stats', 'section',
             'rbx_version', 'Method', 'value']

columns_rename = {'sid': 'Sid', 'value': 'Value', 'metrics': 'Measures',
                  'stats': 'Statistics', 'roi': 'Bundles', 'section': 'Section',
                  'lesion_label': 'Lesion_label', 'endpoint': 'Measures',
                  'timepoint': 'Session', 'grouping': 'Group'}

replace_bundles_dict = {"AC_": "", "AC": "", "AF_L_": "", "AF_L": "", "AF_R_": "", "AF_R": "",
                        "CC_1_": "", "CC_2a_": "", "CC_2b_": "", "CC_3_": "", "CC_4_": "",
                        "CC_5_": "", "CC_6_": "", "CC_7_": "", "CC_Te_": "", "CC_Fr_1_": "",
                        "CC_Fr_2_": "", "CC_Oc_": "", "CC_Pa_": "", "CC_Pr_Po_": "",
                        "CC_Te_": "", "CC_1": "", "CC_2a": "", "CC_2b": "", "CC_3": "", "CC_4": "",
                        "CC_5": "", "CC_6": "", "CC_7": "", "CC_Te": "", "CC_Fr_1": "",
                        "CC_Fr_2": "", "CC_Oc": "", "CC_Pa": "", "CC_Pr_Po": "", "CC_Te": "",
                        "CG_L_": "", "CG_L": "", "CG_R_": "", "CG_R": "",
                        "CST_L_": "", "CST_L": "", "CST_R_": "", "CST_R": "", "CR_L_": "",
                        "CR_L": "", "CR_R_": "", "CR_R": "", "FAT_L_": "", "FAT_L": "",
                        "FAT_R_": "", "FAT_R": "", "FPT_L_": "", "FPT_L": "",
                        "FPT_R_": "", "FPT_R": "", "FX_L_": "", "FX_L": "", "FX_R_": "",
                        "FX_R": "", "ICP_L_": "", "ICP_L": "", "ICP_R_": "",
                        "ICP_R": "", "IFOF_L_": "", "IFOF_L": "", "IFOF_R_": "",
                        "IFOF_R": "", "ILF_L_": "", "ILF_L": "", "ILF_R_": "",
                        "ILF_R": "", "MCP_": "", "MCP": "", "MdLF_L_": "", "MdLF_L": "",
                        "MdLF_R_": "", "MdLF_R": "", "OR_ML_L_": "", "OR_ML_L": "",
                        "OR_ML_R_": "", "OR_ML_R": "", "OR_L_": "", "OR_L": "",
                        "OR_R_": "", "OR_R": "", "PC_": "", "PC": "", "POPT_L_": "",
                        "POPT_L": "", "POPT_R_": "", "POPT_R": "", "PYT_L_": "",
                        "PYT_L": "", "PYT_R_": "", "PYT_R": "", "SCP_L_": "",
                        "SCP_L": "", "SCP_R_": "", "SCP_R": "", "SLF_L_": "",
                        "SLF_L": "", "SLF_R_": "", "SLF_R": "", "SLF_1_L_": "",
                        "SLF_1_L": "", "SLF_1_R_": "", "SLF_1_R": "", "SLF_2_L_": "",
                        "SLF_2_L": "", "SLF_2_R_": "", "SLF_2_R": "", "SLF_3_L_": "",
                        "SLF_3_L": "", "SLF_3_R_": "", "SLF_3_R": "", "UF_L_": "",
                        "UF_L": "", "UF_R_": "", "UF_R": ""}


measure_by_method_dict = {'DTI': ['FA', 'RD', 'MD', 'AD', 'fa', 'rd', 'md', 'ad'],
                          'DTI-FW': ['FA-FWcorrected', 'MD-FWcorrected', 'RD-FWcorrected',
                                     'AD-FWcorrected'],
                          'FW': ['FW', 'fw'],
                          'HARDI': ['AFD_total', 'NuFO'],
                          'NODDI': ['ICVF', 'OD', 'ECVF', 'ISOVf'],
                          'MTI': ['ihMTR', 'MTR', 'MTsat', 'ihMTsat'],
                          'Streamlines': ['Volume', 'Count', 'Lenght', ]}

measure_by_method_dict = {'FODF': ['NuFO', 'nufo', 'AFD_total', 'afd_total', 'AFD_fixel', 'afd_along',
                          'Radial_fODF', 'radfODF', 'afd', 'AFD', 'AFD_sum', 'afd_sum'],
                          'DTI': ['FA', 'AD', 'RD', 'MD', 'fa', 'ad', 'rd', 'md'],
                          'DTI-FW': ['FA-FWcorrected', 'MD-FWcorrected', 'RD-FWcorrected',
                                     'AD-FWcorrected', 'fat', 'mdt', 'rdt', 'adt'],
                          'FW': ['FW', 'fw'],
                          'NODDI': ['ECVF', 'ICVF', 'ISOVF', 'OD', 'ecvf', 'icvf', 'isovf', 'od'],
                          'MTI': ['MTR', 'MTsat', 'ihMTR', 'ihMTdR1sat', 'ihMTsat', 'mtr', 'mtsat',
                                  'ihmtr', 'ihmtsat', 'ihmtdR1sat'],
                          'HARDI': ['APower', 'apower', 'GFA', 'gfa'],
                          'QSM': ['RDF', 'rdf', 'QSM', 'qsm'],
                          'Streamlines': ['Volume', 'Count', 'volume', 'streamline_count',
                                          'Length', 'min_length', 'length'],
                          'Lesion': ['lesion_volume', "Lesion_volume",
                                     'lesion_total_volume', 'Lesion_total_volume',
                                     'lesion_count', 'Lesion_count']}
