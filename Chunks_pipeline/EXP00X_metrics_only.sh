! /bin/bash
export MOVE_ON=true
#### Root folder from dropbox 
export ROOT_PATH="/home/luis/Dropbox/DATASETS_AUDIO/Proposal_runs"
export SRC_PATH=$(pwd)

export EXP_NAME="EXP010C"
export DATASET_NAME="TestAO-Irmadb"

# export DATASET_NAME="TestAO-Liz"
export SHAS_NAME="SHAS"
export FEAT_NAME="DV"
export METHOD_NAME="umap1H9"

## Segmentation Parameters
export seg_ln="1.0"
export step_size="0.3"
export gap_size="0.4"

export consc_th="1"


#### Stage 3 Unsupervised Method
export current_stg3="${ROOT_PATH}/${DATASET_NAME}/STG_3/STG3_${EXP_NAME}-${SHAS_NAME}-${FEAT_NAME}-${METHOD_NAME}"
export STG3_FINAL_CSV="${current_stg3}/final_csv"

#### Stage 4 Metrics
export STG1_GT_CSV="${ROOT_PATH}/${DATASET_NAME}/GT_final/"
export STG4_METRICS="${current_stg3}/metrics"
export STG4_METRIC_RUNNAME="${DATASET_NAME}_${SHAS_NAME}_${FEAT_NAME}_${METHOD_NAME}"

export pred_suffix_added="pred"
export pred_ext="csv"


cd $SRC_PATH
if [ "$MOVE_ON" = true ]; then
    source STG4_ENTROPY.sh
fi

# # Unset all the variables
# unset ROOT_PATH
# unset SRC_PATH
# unset EXP_NAME
# unset DATASET_NAME
# unset SHAS_NAME
# unset FEAT_NAME
# unset METHOD_NAME
# unset STG1_WAVS
# unset STG1_FINAL_CSV
# unset current_stg2
# unset STG2_FEATS_PICKLE
# unset current_stg3
# unset STG3_MERGED_WAVS
# unset min_cluster_size
# unset pca_elem
# unset hdb_mode
# unset min_samples
# unset RUN_ID
# unset RUN_PARAMS

# unset SHAS_LOCATION
# unset path_to_yaml_folder
# unset path_to_yaml_file
# unset SHAS_ROOT
# unset path_to_checkpoint
# unset STG1_WAVS
# unset STG1_FINAL_CSV
# unset SRC_PATH

# unset HDBSCAN_LOCATION
# unset STG2_CHUNKS_WAVS
# unset STG2_MFCC_FILES
# unset SRC_PATH
# unset STG2_FEATS_PICKLE

# unset HDBSCAN_LOCATION
# unset STG3_HDBSCAN_PRED_OUTPUT
# unset STG3_SEPARATED_WAVS
# unset STG3_OUTLIERS_WAVS
# unset STG4_FINAL_CSV
# unset STG4_SEPARATED_MERGED_WAVS