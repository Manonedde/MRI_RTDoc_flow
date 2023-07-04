#!/bin/bash
		
tractometryflow_path=$1
output_path=$2
scripts_path=$3		

echo -e "Merged tractometryflow jsons output"
mkdir $output_path/merged_jsons/

scil_merge_json.py $tractometryflow_path/*/Bundle_Mean_Std/*json $output_path/merged_jsons/mean_std.json
scil_merge_json.py $tractometryflow_path/*/Bundle_Mean_Std_Per_Point/*json $output_path/merged_jsons/mean_std_per_point.json
scil_merge_json.py $tractometryflow_path/*/Bundle_Streamline_Count/*json $output_path/merged_jsons/streamline_count.json
scil_merge_json.py $tractometryflow_path/*/Bundle_Length_Stats/*json $output_path/merged_jsons/length_stats.json
scil_merge_json.py $tractometryflow_path/*/Bundle_Volume/*json $output_path/merged_jsons/volume.json
scil_merge_json.py $tractometryflow_path/*/Bundle_Volume/*json $output_path/merged_jsons/volume_per_label.json

#scil_merge_json.py $tractometryflow_path/*/Bundle_Metrics_Stats_In_Endpoints/*json $output_path/merged_jsons/endpoints_metric_stats.json

echo -e "Convert json to CSV"
mkdir $output_path/convert_to_csv

python $scripts_path/convert_json_to_csv.py *json --save_merge_df --out_dir $output_path/convert_to_csv
python $scripts_path/rdt_prepare_csv_for_figures.py merged_csv_rdt.csv --out_dir $output_path/convert_to_csv

echo -e "Generate figures"
mkdir -p $output_path/averages_figures $output_path/profile_figures $output_path/heatmap

python $scripts_path/rdt_generate_heatmap.py $output_path/convert_to_csv/rtd_average.csv --out_dir $output_path/heatmap
python $scripts_path/rdt_generate_mean_measures_across_bundles_fgures.py $output_path/convert_to_csv/rtd_profile.csv --out_dir $output_path/averages_figures
python $scripts_path/rdt_generate_profile_by_technic.py $output_path/convert_to_csv/rtd_average.csv --out_dir $output_path/profile_figures

echo -e "Ending process"




