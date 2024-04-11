#! /bin/bash

export HDBSCAN_LOCATION="/home/luis/Dropbox/clustering/meta-SR"

export STG3_HDBSCAN_PRED_OUTPUT="${current_stg3}/HDBSCAN_pred_output"
export STG3_SEPARATED_WAVS="${current_stg3}/separated_wavs"
export STG3_OUTLIERS_WAVS="${current_stg3}/outliers_wavs"

export STG3_SEPARATED_MERGED_WAVS="${current_stg3}/separated_merged_wavs"

export RUN_ID="${EXP_NAME}_${DATASET_NAME}_${METHOD_NAME}"
export RUN_PARAMS="pca${pca_elem}_mcs${min_cluster_size}_ms${min_samples}_${hdb_mode}"

python3 ${SRC_PATH}/folder_verify.py $STG3_HDBSCAN_PRED_OUTPUT
python3 ${SRC_PATH}/folder_verify.py $STG3_SEPARATED_WAVS
python3 ${SRC_PATH}/folder_verify.py $STG3_MERGED_WAVS
python3 ${SRC_PATH}/folder_verify.py $STG3_OUTLIERS_WAVS

python3 ${SRC_PATH}/folder_verify.py $STG3_FINAL_CSV
python3 ${SRC_PATH}/folder_verify.py $STG3_SEPARATED_MERGED_WAVS

cd $HDBSCAN_LOCATION
conda activate metaSR

cd ~/Dropbox/SpeechFall2022/SpeakerLID_GT_code/utls
pip install -e .
echo "Installed utls library"

cd $HDBSCAN_LOCATION

## Run the HDBSCAN prediction
python3 ${HDBSCAN_LOCATION}/main_hdbscan_pred_output.py $STG2_FEATS_PICKLE $STG3_HDBSCAN_PRED_OUTPUT $RUN_PARAMS $RUN_ID

## Join the predictions chunks into a merged wav files
python3 ${SRC_PATH}/Stage3_merge_wavs_per_folder.py $STG1_WAVS $STG3_HDBSCAN_PRED_OUTPUT $STG3_SEPARATED_WAVS $STG3_MERGED_WAVS $STG3_OUTLIERS_WAVS 

## Create the final csv file
python3 ${SRC_PATH}/Stage3b_create_csv_from_merged.py $STG3_MERGED_WAVS $STG3_FINAL_CSV $STG3_SEPARATED_MERGED_WAVS

