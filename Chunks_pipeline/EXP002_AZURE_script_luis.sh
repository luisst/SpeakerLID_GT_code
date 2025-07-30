#! /bin/bash
#### Root folder from dropbox 
export ROOT_PATH="/home/luis/Dropbox/DATASETS_AUDIO/Proposal_runs"
export SRC_PATH=$(pwd)

export EXP_NAME="EXP002"
export DATASET_NAME="TestAO-Irmadb"
export METHOD_NAME="Azure33"

echo -e "\t>>>>> AZURE SCRIPT <<<<<"

### Stage 4 Metrics
cd $SRC_PATH

export STG1_GT_CSV="${ROOT_PATH}/${DATASET_NAME}/GT_final/"
export STG3_FINAL_CSV="${ROOT_PATH}/${DATASET_NAME}/${METHOD_NAME}"

export current_stg3="${ROOT_PATH}/${DATASET_NAME}/STG_3/AZURE_${EXP_NAME}-${METHOD_NAME}"
export STG4_METRICS="${current_stg3}/metrics"
export STG4_METRIC_RUNNAME="${DATASET_NAME}_${METHOD_NAME}"

export pred_suffix_added="xx"
export pred_ext="txt"

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
export AZURE_NAME="azure"

python3 ${SRC_PATH}/Stage4_entropy_azure.py --csv_pred_folder $STG3_FINAL_CSV\
 --GT_csv_folder $STG1_GT_CSV --metric_output_folder $STG4_METRICS\
 --pred_suffix $pred_suffix_added --pred_extensions $pred_ext\
 --min_overlap_pert $min_overlap_percentage\
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
 --run_name $STG4_METRIC_RUNNAME --method_name $AZURE_NAME

# Check if the Python script was successful
if [ $? -ne 0 ]; then
    export MOVE_ON=false
    echo "Move on: $MOVE_ON"
    return 1
fi

#### Get Back to where you once belonged
conda activate
cd $SRC_PATH