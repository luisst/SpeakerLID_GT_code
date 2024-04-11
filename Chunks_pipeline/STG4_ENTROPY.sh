#! /bin/bash


conda activate pyannote

cd ~/Dropbox/SpeechFall2022/SpeakerLID_GT_code/utls
pip install -e .
echo "Installed utls library"

cd $SRC_PATH

python3 ${SRC_PATH}/folder_verify.py $STG4_METRICS

readonly min_overlap_percentage="0.3"
readonly pred_suffix_added="pred"
readonly pred_ext="csv"

python3 ${SRC_PATH}/Stage4_entropy_single.py $STG3_FINAL_CSV $STG1_GT_CSV $STG4_METRICS\
 $pred_suffix_added $pred_ext $min_overlap_percentage $METHOD_NAME $STG4_METRIC_RUNNAME