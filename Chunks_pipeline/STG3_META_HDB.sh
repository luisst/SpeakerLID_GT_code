#! /bin/bash

export HDBSCAN_LOCATION="/home/luis/Dropbox/clustering/meta-SR"

export STG3_HDBSCAN_PRED_OUTPUT="${current_stg3}/HDBSCAN_pred_output"
export STG3_SEPARATED_WAVS="${current_stg3}/separated_wavs"
export STG3_OUTLIERS_WAVS="${current_stg3}/outliers_wavs"

export STG3_SEPARATED_MERGED_WAVS="${current_stg3}/separated_merged_wavs"

export RUN_ID="${EXP_NAME}_${DATASET_NAME}_${METHOD_NAME}"
export RUN_PARAMS="pca${pca_elem}_mcs${min_cluster_size}_ms${min_samples}_${hdb_mode}"

export STG3_REDUCED_FEATS="${current_stg3}/reduced_feats.pickle"
export STG3_CLUSTERING_LBLS="${current_stg3}/clustering_labels.pickle"

export STG3_CLUSTERING_METRICS="${current_stg3}/clustering_metrics"

python3 ${SRC_PATH}/folder_verify.py $STG3_HDBSCAN_PRED_OUTPUT
python3 ${SRC_PATH}/folder_verify.py $STG3_SEPARATED_WAVS
python3 ${SRC_PATH}/folder_verify.py $STG3_MERGED_WAVS
python3 ${SRC_PATH}/folder_verify.py $STG3_OUTLIERS_WAVS
python3 ${SRC_PATH}/folder_verify.py $STG3_CLUSTERING_METRICS

python3 ${SRC_PATH}/folder_verify.py $STG3_FINAL_CSV
python3 ${SRC_PATH}/folder_verify.py $STG3_SEPARATED_MERGED_WAVS

cd $HDBSCAN_LOCATION
conda activate metaSR2

cd ~/Dropbox/SpeechFall2022/SpeakerLID_GT_code/utls
pip install -e .
echo -e "\t>>>>> Installed utls library"

cd $HDBSCAN_LOCATION

## Run the HDBSCAN prediction
echo -e "\n\t>>>>> Output from HDB-SCAN pred: $STG3_HDBSCAN_PRED_OUTPUT\n"

python3 ${HDBSCAN_LOCATION}/main_hdbscan_pred_output.py --input_feats_pickle $STG2_FEATS_PICKLE\
 --output_pred_folder $STG3_HDBSCAN_PRED_OUTPUT\
 --run_params $RUN_PARAMS --exp_name $RUN_ID\
 --pred_lbl_picke $STG3_CLUSTERING_LBLS --pred_reduced_feats $STG3_REDUCED_FEATS\

# Check if the Python script was successful
if [ $? -ne 0 ]; then
    export MOVE_ON=false
    echo "Move on: $MOVE_ON"
    return 1
fi

## Print Clustering metrics
echo -e "\n\t>>>>> Clustering metrics: $STG3_CLUSTERING_METRICS\n"

python3 ${SRC_PATH}/Stage3_internal_clusters.py --input_feats_pickle $STG2_FEATS_PICKLE\
    --input_feats_reduced_pickle $STG3_REDUCED_FEATS\
 --stg3_pred_lbl $STG3_CLUSTERING_LBLS --stg3_clustering_metrics $STG3_CLUSTERING_METRICS 

# Check if the Python script was successful
if [ $? -ne 0 ]; then
    export MOVE_ON=false
    echo "Move on: $MOVE_ON"
    return 1
fi

## Join the predictions chunks into a merged wav files
echo -e "\n\t>>>>> Merged WAVs: $STG3_MERGED_WAVS\n"

python3 ${SRC_PATH}/Stage3_merge_wavs_ND.py --stg1_long_wavs $STG1_WAVS\
 --stg3_pred_folders $STG3_HDBSCAN_PRED_OUTPUT --stg3_separated_wavs $STG3_SEPARATED_WAVS\
 --stg3_merged_wavs $STG3_MERGED_WAVS --stg3_outliers $STG3_OUTLIERS_WAVS\
 --ln $seg_ln --st $step_size --gap $gap_size --consc_th $consc_th

# Check if the Python script was successful
if [ $? -ne 0 ]; then
    export MOVE_ON=false
    echo "Move on: $MOVE_ON"
    return 1
fi

## Create the final csv file
echo -e "\n\t>>>>> Output Final CSV prediction: $STG3_FINAL_CSV\n"

python3 ${SRC_PATH}/Stage3b_create_csv_from_merged.py --stg3_merged_wavs $STG3_MERGED_WAVS\
 --stg4_final_csv $STG3_FINAL_CSV --stg4_separated_merged_wavs $STG3_SEPARATED_MERGED_WAVS

# Check if the Python script was successful
if [ $? -ne 0 ]; then
    export MOVE_ON=false
    echo "Move on: $MOVE_ON"
    return 1
fi

