#! /bin/bash
#### Root folder from dropbox 
export ROOT_PATH="/home/luis/Dropbox/DATASETS_AUDIO/Proposal_runs"
export SRC_PATH=$(pwd)

export EXP_NAME="EXP002"
# export DATASET_NAME="TestAO-Liz"
export DATASET_NAME="TestAO-Irmadb"
export SHAS_NAME="xx"
export FEAT_NAME="xx"
export METHOD_NAME="Azure"

echo -e "\t>>>>> AZURE SCRIPT <<<<<"

### Stage 4 Metrics
cd $SRC_PATH

export STG1_GT_CSV="${ROOT_PATH}/${DATASET_NAME}/GT_final/"
export STG3_FINAL_CSV="${ROOT_PATH}/${DATASET_NAME}/${METHOD_NAME}"

export current_stg3="${ROOT_PATH}/${DATASET_NAME}/STG_3/STG3_${EXP_NAME}-${SHAS_NAME}-${FEAT_NAME}-${METHOD_NAME}"
export STG4_METRICS="${current_stg3}/metrics"
export STG4_METRIC_RUNNAME="${DATASET_NAME}_${SHAS_NAME}_${FEAT_NAME}_${METHOD_NAME}"

export pred_suffix_added="xx"
export pred_ext="txt"

echo -e "\t>>>>> Direct metric computation"

source STG4_ENTROPY.sh

## Add Azure comparison

#### Get Back to where you once belonged
conda activate
cd $SRC_PATH