#! /bin/bash

export HDBSCAN_LOCATION="/home/luis/Dropbox/clustering/meta-SR"
export STG2_CHUNKS_WAVS="${current_stg2}/wav_chunks"
export STG2_MFCC_FILES="${current_stg2}/MFCC_files"

python3 ${SRC_PATH}/folder_verify.py $STG2_CHUNKS_WAVS
python3 ${SRC_PATH}/folder_verify.py $STG2_MFCC_FILES

cd $HDBSCAN_LOCATION
conda activate metaSR

cd ~/Dropbox/SpeechFall2022/SpeakerLID_GT_code/utls
pip install -e .
echo "Installed utls library"


cd $HDBSCAN_LOCATION

echo "Divide into chunks: $STG2_CHUNKS_WAVS"
python3 ${SRC_PATH}/Stage2_divide_into_chunks.py $STG1_WAVS $STG1_FINAL_CSV $STG2_CHUNKS_WAVS 

echo "Feature Extraction pre-proc: $STG2_MFCC_FILES"
python3 ${HDBSCAN_LOCATION}/feature_extraction.py $STG2_CHUNKS_WAVS $STG2_MFCC_FILES

echo "Feature Extraction : $STG2_FEATS_PICKLE"
python3 ${HDBSCAN_LOCATION}/main_d_vectors_pred.py $STG2_CHUNKS_WAVS $STG2_MFCC_FILES $STG2_FEATS_PICKLE
