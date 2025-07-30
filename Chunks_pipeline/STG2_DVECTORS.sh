#! /bin/bash

export HDBSCAN_LOCATION="/home/luis/Dropbox/clustering/meta-SR"
export STG2_RAW_CHUNKS_WAVS="${current_stg2}/wav_chunks_raw"
export STG2_CHUNKS_WAVS="${current_stg2}/wav_chunks"
export STG2_MFCC_FILES="${current_stg2}/MFCC_files"

# python3 ${SRC_PATH}/folder_verify.py $STG2_RAW_CHUNKS_WAVS
python3 ${SRC_PATH}/folder_verify.py $STG2_CHUNKS_WAVS
python3 ${SRC_PATH}/folder_verify.py $STG2_MFCC_FILES

cd $HDBSCAN_LOCATION
conda activate metaSR2

cd ~/Dropbox/SpeechFall2022/SpeakerLID_GT_code/utls
pip install -e .
echo -e "\t>>>>> Installed utls library"

cd $HDBSCAN_LOCATION

# echo -e "\t>>>>> Divide into chunks: $STG2_RAW_CHUNKS_WAVS"
# python3 ${SRC_PATH}/Stage2_divide_into_chunks.py --stg1_wavs $STG1_WAVS\
#  --stg1_final_csv $STG1_FINAL_CSV \
#  --stg2_chunks_wavs $STG2_RAW_CHUNKS_WAVS\
#  --ln $seg_ln --st $step_size 

# # Check if the Python script was successful
# if [ $? -ne 0 ]; then
#     export MOVE_ON=false
#     echo "Move on: $MOVE_ON"
#     return 1
# fi

if [ $DOUBLE_TALK_FLAG=true ]; then
    conda activate dtp11
    # Add Double-Talk detection
    echo -e "\t>>>>> Double-Talk detection: $STG2_RAW_CHUNKS_WAVS"
    python3 ${SRC_PATH}/Stage2_double_talk_detection.py --stg2_chunks_wavs $STG2_RAW_CHUNKS_WAVS\
    --stg2_dt_pretrained $STG2_DT_PRETRAINED \
    --stg2_filtered_chunks_wavs $STG2_CHUNKS_WAVS \
    --stg2_dt_th $DT_THRESHOLD

    # Check if the Python script was successful
    if [ $? -ne 0 ]; then
        export MOVE_ON=false
        echo "Move on: $MOVE_ON"
        return 1
    fi
else
    # No Double-Talk detection
    echo -e "\t>>>>> No Double-Talk detection: $STG2_RAW_CHUNKS_WAVS"
    cp -r $STG2_RAW_CHUNKS_WAVS/* $STG2_CHUNKS_WAVS
    # Check if the copy was successful
    if [ $? -ne 0 ]; then
        export MOVE_ON=false
        echo "Move on: $MOVE_ON"
        return 1
    fi

fi


# conda activate metaSR2
# echo -e "\t>>>>> Feature Extraction pre-proc: $STG2_MFCC_FILES"
# python3 ${HDBSCAN_LOCATION}/feature_extraction.py --wavs_folder $STG2_CHUNKS_WAVS\
#  --output_feats_folder $STG2_MFCC_FILES

# # Check if the Python script was successful
# if [ $? -ne 0 ]; then
#     export MOVE_ON=false
#     echo "Move on: $MOVE_ON"
#     return 1
# fi


# echo -e "\t>>>>> Feature Extraction: $STG2_FEATS_PICKLE"
# python3 ${HDBSCAN_LOCATION}/main_d_vectors_pred.py --wavs_folder $STG2_CHUNKS_WAVS\
#  --input_mfcc_folder $STG2_MFCC_FILES  --output_feats_pickle $STG2_FEATS_PICKLE

# # Check if the Python script was successful
# if [ $? -ne 0 ]; then
#     export MOVE_ON=false
#     echo "Move on: $MOVE_ON"
#     return 1
# fi