#! /bin/bash

echo -e "\n\t>>>>> Stage 1b: Silent Detector FSDB \n"

export output_mask_csv_folder="${ROOT_PATH}/${DATASET_NAME}/STG_1/STG1_${SHAS_NAME}/mask_output_csv"
export filtered_output_csv_folder="${ROOT_PATH}/${DATASET_NAME}/STG_1/STG1_${SHAS_NAME}/filtered_output_csv"

python3 ${SRC_PATH}/folder_verify.py $output_mask_csv_folder
python3 ${SRC_PATH}/folder_verify.py $filtered_output_csv_folder

export segment_duration="0.25"
export thres="-29"

python3 ${SRC_PATH}/Stage1b_silent_detector.py --input_wav_folder $STG1_WAVS\
 --output_mask_csv_folder $output_mask_csv_folder\
 --vad_results_folder $STG1_FINAL_CSV\
 --output_csv_folder $filtered_output_csv_folder\
 --segment_duration $segment_duration\
 --thres $thres

echo -e "\n\t>>>>> Stage 1b: Metrics \n"

export FILTERED_metric_folder="${ROOT_PATH}/${DATASET_NAME}/STG_1/STG1_${SHAS_NAME}/filtered_metrics"
python3 ${SRC_PATH}/folder_verify.py $FILTERED_metric_folder 

export VAD_pred_ext="txt"
export shas_method="shas"
export filtered_run_id="filtered_${SHAS_NAME}_thres${thres}_seg${segment_duration}" 

python3 ${SRC_PATH}/Stage1b_metric_vad.py --csv_pred_folder $filtered_output_csv_folder\
 --GT_csv_folder $STG1_GT_CSV\
 --audios_folder $STG1_WAVS\
 --metric_output_folder $FILTERED_metric_folder\
 --pred_extensions $VAD_pred_ext\
 --method_name $shas_method\
 --run_name $filtered_run_id

cd $SRC_PATH
