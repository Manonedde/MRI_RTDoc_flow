#!/bin/bash
# Compile jsons from tractometry into csv, reshape it and generates 
# fogures suitables for rst format in Read the Doc.

# input parameters
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


echo -e "Generate compile CSV"
mkdir $output_path/convert_to_csv
# convert all concatenated_jsons into csv
python $source/df_convert_json_to_csv.py *json --save_merge_df \
                    --out_dir $output_path/convert_to_csv 

# rename and reshape csv to fit with plots functions
python $source/df_prepare_csv_scil.py merged_csv_long.csv \
                    --out_dir $output_path/convert_to_csv \
                    --rename_measure --merge_lr --longitudinal '_ses-' \
                    --compute_ecvf --apply_factor 100

# Rename session 2 to 6 for sub-003 subject
python $source/df_operations.py replace_where \
                $output_path/convert_to_csv/rtd__average.csv \
                $output_path/convert_to_csv/rtd__average_replace.csv \
                --my_cols Sid Session --pattern sub-003-hc \
                --my_dict 2=1 3=2 4=3 5=4 6=5 -f

python $source/df_operations.py replace_where \
                $output_path/convert_to_csv/rtd__profile.csv \
                $output_path/convert_to_csv/rtd__profile_replace.csv \
                --my_cols Sid Session --pattern sub-003-hc \
                --my_dict 2=1 3=2 4=3 5=4 6=5 -f

mkdir $output_path/csv_data
for curr_file in $output_path/convert_to_csv/rtd__*replace.csv;
    do 
    $file = ${curr_file/replace.csv/''}

# Measures csv : Remove volume data and std from mean csv
        python df_operations.py remove_row \
                $output_path/csv_data/$curr_file \
                $output_path/csv_data/${file}_measures.csv \
                --my_cols Statistics --pattern volume

        python df_operations.py remove_row \
                $output_path/csv_data/${file}_measures.csv \
                $output_path//csv_data/${file}_measures.csv\
                --my_cols Statistics --pattern std

# Volumes csv : Select rows corresponding to Streamlines method
        python df_operations.py get_from \
                $output_path/convert_to_csv/$file \
                ~/Data/readthedoc_results/csv_data/${file}_volume.csv\
                 --my_cols Method --pattern Streamlines

# Remove std, min and max from volume csv
        python df_operations.py remove_row \
                $output_path/csv_data/${file}_volume.csv \
                $output_path/csv_data/${file}_volume.csv\
                --my_cols Statistics --pattern min

        python df_operations.py remove_row \
                $output_path/csv_data/${file}_volume.csv \
                $output_path/csv_data/${file}_volume.csv\
                --my_cols Statistics --pattern max

        python df_operations.py remove_row \
                $output_path/csv_data/${file}_volume.csv \
                $output_path/csv_data/${file}_volume.csv \
                --my_cols Statistics --pattern std

done

cp $output_path/csv_data/rtd__average_measures.csv $output_path/csv_data/rtd__average_measures_factor.csv
cp $output_path/csv_data/rtd__profile_measures.csv $output_path/csv_data/rtd__profile_measures_factor.csv

for measure in 'AD' 'RD','MD' 'MD-FWcorrected', 'MD-FWcorrected','MD-FWcorrected';
        do
        python $source/df_operations.py factor \
                $output_path/csv_data/rtd__average_measures_factor.csv \
                rtd__average_measures_factor.csv --my_cols Measures Value \
                --value 100 --out_dir $output_path/csv_data/ --pattern $measure

        python $source/df_operations.py factor \
                $output_path/csv_data/rtd__profile_measures_factor.csv \
                rtd__average_measures_factor.csv --my_cols Measures Value \
                --value 100 --out_dir $output_path/csv_data/ --pattern $measure
done


echo -e "Generates bundle CSVs"
mkdir -p $output_path/bundles

python $source/df_operations.py split_by $output_path/csv_data/rtd_average_measures.csv\
        average_measures.csv --out_dir $output_path/bundles --my_cols Bundles

python $source/df_operations.py split_by $output_path/csv_data/rtd_profile_measures.csv\
        profile_measures.csv --out_dir $output_path/bundles --my_cols Bundles

python $source/df_operations.py split_by $output_path/csv_data/rtd_average_volume.csv\
        average_volume.csv --out_dir $output_path/bundles --my_cols Bundles

python $source/df_operations.py split_by $output_path/csv_data/rtd_profile_volume.csv\
        profile_volume.csv --out_dir $output_path/bundles --my_cols Bundles

echo -e "Generates summary Tables"
mkdir -p $output_path/tables
for curr_file in $output_path/convert_to_csv/rtd__*replace.csv;
    do 
    $file = ${curr_file/.csv/''}
    
    python $source/df_summary_table.py $output_path/bundles/AF___average.csv \
           --out_name ${file}_table.csv --out_dir $output_path/tables \
           --sort_by 'Measures'
done

echo -e "Generate figures"
# Creates folder to save results
mkdir -p $output_path/averages $output_path/profile \
                        $output_path/heatmap $output_path/correlations

# Heatmap with session as slider
python $source/rd_heatmap.py \
                $output_path/csv_data/rtd_average_measures.csv \
                --out_dir $output_path/heatmap --longitudinal \
                --use_as_slider 'Session' --reorder_measure --filter_missing

python $source/rd_heatmap.py \
                $output_path/csv_data/rtd_average_measures.csv \
                --out_dir $output_path/heatmap --add_average --longitudinal \
                --use_as_slider 'Session' --reorder_measure --filter_missing \
                --apply_on_pearson absolute --plot_size 1000 900\
                --out_name correlation_heatmap_add_average

# Correlation with menu for each bundles
python $source/rd_correlation_with_menu.py \
                $output_path/csv_data/rtd_average_measures.csv \
                --out_dir $output_path/averages_figures --longitudinal

## Distribution all bundles
# Scatter plots
python $source/rd_distribution_measures.py \
                $output_path/csv_data/rtd_average_measures.csv \
                --out_dir $output_path/averages_figures \
                --split_by 'Method' --filter_missing

python $source/rd_boxplot.py \
                $output_path/csv_data/rtd_average_measures.csv \
                --out_dir $output_path/averages_figures \
                --split_by 'Method' --filter_missing

# Boxplot
python $source/rd_boxplot.py $output_path/csv_data/rtd__average_measures.csv\
                 --out_dir $output_path/distributions \
                 --split_by 'Method' --filter_missing

python $source/rd_boxplot.py $output_path/csv_data/rtd__average_volume.csv \
                --out_dir $output_path/distributions \
                --split_by 'Method' --filter_missing

## Profiles plots
# Profile for each 
python $source/rd_profiles_measures.py \
        $output_path/csv_data/rtd__profile_measures.csv \
        Section Value 'Bundle sections' --out_dir $output_path/profile/ \
        --filter_missing --split_by Bundles --use_as_slider Session

python $source/rd_profiles_measures.py \
        $output_path/csv_data/rtd__profile_volume.csv \
        Section Value Profile --out_dir $output_path/profile/ \
        --out_name volume_profile --filter_missing --split_by Bundles \
        --use_as_slider Session
        
echo -e "Ending process"




