#!/bin/bash
"""
"""
tractometryflow_path=$1
output_path=$2	

source='/home/local/USHERBROOKE/eddm3601/Research/Sources/Github/MRI_RTDoc_flow'

echo -e "Merged tractometryflow jsons output"
mkdir $output_path/merged_jsons/

scil_merge_json.py $tractometryflow_path/*/Bundle_Mean_Std/*json  \
                            $output_path/merged_jsons/mean_std.json

scil_merge_json.py $tractometryflow_path/*/Bundle_Mean_Std_Per_Point/*json \
                            $output_path/merged_jsons/mean_std_per_point.json

scil_merge_json.py $tractometryflow_path/*/Bundle_Streamline_Count/*json  \
                            $output_path/merged_jsons/streamline_count.json

scil_merge_json.py $tractometryflow_path/*/Bundle_Length_Stats/*json  \
                            $output_path/merged_jsons/length_stats.json

scil_merge_json.py $tractometryflow_path/*/Bundle_Volume/*json  \
                            $output_path/merged_jsons/volume.json

scil_merge_json.py $tractometryflow_path/*/Bundle_Volume/*json  \
                            $output_path/merged_jsons/volume_per_label.json

#scil_merge_json.py $tractometryflow_path/*/Bundle_Metrics_Stats_In_Endpoints/*json $output_path/merged_jsons/endpoints_metric_stats.json

echo -e "Generate compile CSV"
mkdir $output_path/convert_to_csv

python $source/df_convert_json_to_csv.py *json --save_merge_df \
                    --out_dir $output_path/convert_to_csv \
                    --save_merge_df

python $source/df_prepare_csv_scil.py merged_csv_long.csv \
                    --out_dir $output_path/convert_to_csv \
                    --rename_measure --merge_lr --longitudinal '_ses-'

echo -e "Generate figures"
mkdir -p $output_path/averages $output_path/profile \
                        $output_path/heatmap $output_path/correlations

python $source/rd_generate_heatmap.py \
                $output_path/convert_to_csv/rtd_average.csv \
                --out_dir $output_path/heatmap \
                --use_as_slider 'Session' --reorder_measure --filter_missing \
                --longitudinal

python $source/rd_generate_correlation_plot.py \
                $output_path/convert_to_csv/rtd_average.csv \
                --out_dir $output_path/averages_figures --longitudinal

python $source/rd_generate_distribution_measures.py \
                $output_path/convert_to_csv/rtd_average.csv \
                --out_dir $output_path/averages_figures \
                --split_by 'Method' --filter_missing

python $source/rd_generate_measures_profile.py \
                $output_path/convert_to_csv/rtd_profile.csv \
                --out_dir $output_path/profile_figures

echo -e "Ending process"




