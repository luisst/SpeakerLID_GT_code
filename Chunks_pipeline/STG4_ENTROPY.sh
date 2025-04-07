#! /bin/bash

echo -e "\t>>>>> Using the CSV files from: $STG3_FINAL_CSV"
echo -e "\t>>>>> Results stored in: $STG4_METRICS"

conda activate pyannote

cd ~/Dropbox/SpeechFall2022/SpeakerLID_GT_code/utls
pip install -e .
echo -e "\t>>>>> Installed utls library"

cd $SRC_PATH

python3 ${SRC_PATH}/folder_verify.py $STG4_METRICS

export min_overlap_percentage="0.3"

echo -e "\n\t>>>>> Using the CSV files from: $STG3_FINAL_CSV \n"
echo -e "\n\t>>>>> Results stored in: $STG4_METRICS\n"

export RUN_PARAMS="pca0_mcs0_ms0_0"

python3 ${SRC_PATH}/Stage4_entropy_single.py --csv_pred_folder $STG3_FINAL_CSV\
 --GT_csv_folder $STG1_GT_CSV --metric_output_folder $STG4_METRICS\
 --pred_suffix $pred_suffix_added --pred_extensions $pred_ext\
 --min_overlap_pert $min_overlap_percentage --method_name $METHOD_NAME\
 --run_name $STG4_METRIC_RUNNAME --run_params $RUN_PARAMS

# Check if the Python script was successful
if [ $? -ne 0 ]; then
    export MOVE_ON=false
    echo "Move on: $MOVE_ON"
    return 1
fi

python3 ${SRC_PATH}/Stage4_extra_metrics.py --csv_pred_folder $STG3_FINAL_CSV\
 --GT_csv_folder $STG1_GT_CSV --metric_output_folder $STG4_METRICS\
 --pred_suffix $pred_suffix_added --pred_extensions $pred_ext\
 --run_name $STG4_METRIC_RUNNAME

# Check if the Python script was successful
if [ $? -ne 0 ]; then
    export MOVE_ON=false
    echo "Move on: $MOVE_ON"
    return 1
fi

python3 ${SRC_PATH}/Stage4_clustering_metrics.py --csv_pred_folder $STG3_FINAL_CSV\
 --GT_csv_folder $STG1_GT_CSV --metric_output_folder $STG4_METRICS\
 --pred_suffix $pred_suffix_added --pred_extensions $pred_ext\
 --run_name $STG4_METRIC_RUNNAME

# Check if the Python script was successful
if [ $? -ne 0 ]; then
    export MOVE_ON=false
    echo "Move on: $MOVE_ON"
    return 1
fi