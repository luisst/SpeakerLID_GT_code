#! /bin/bash
export MOVE_ON=true
#### Root folder from dropbox 
export ROOT_PATH="/home/luis/Dropbox/DATASETS_AUDIO/Proposal_runs"
export SRC_PATH=$(pwd)

export EXP_NAME="EXP003"
export DATASET_NAME="TestAO-Irma"
# export DATASET_NAME="TestAO-Liz"

export SHAS_NAME="SHASfiltE"
export FEAT_NAME="DV"
export METHOD_NAME="TDA"

echo -e "\t>>>>> TDA Keppler Mapper Chunks SCRIPT <<<<<"


#### Stage 1 VAD
export STG1_WAVS="${ROOT_PATH}/${DATASET_NAME}/input_wavs/"
export STG1_FINAL_CSV="${ROOT_PATH}/${DATASET_NAME}/STG_1/STG1_${SHAS_NAME}/shas_filtered_output_csv/"
source STG1_SHAS.sh

#### Stage 2 Feature Extraction
export current_stg2="${ROOT_PATH}/${DATASET_NAME}/STG_2/STG2_${EXP_NAME}-${SHAS_NAME}-${FEAT_NAME}"
export STG2_FEATS_PICKLE="${current_stg2}/${DATASET_NAME}_${SHAS_NAME}_${FEAT_NAME}_feats"

# if [ "$MOVE_ON" = true ]; then
#     source STG2_DVECTORS.sh
# fi

#### Stage 3 Unsupervised Method
export current_stg3="${ROOT_PATH}/${DATASET_NAME}/STG_3/STG3_${EXP_NAME}-${SHAS_NAME}-${FEAT_NAME}-${METHOD_NAME}"
export STG3_MERGED_WAVS="${current_stg3}/merged_wavs"
export STG3_FINAL_CSV="${current_stg3}/final_csv"


## TDA Projection PCA 
export pca_elem="16"

## TDA HDBSCAN parameters
# export min_cluster_size="5"
# export hdb_mode="eom"
# export min_samples="5"

export min_cluster_size="5"
export hdb_mode="leaf"
export min_samples="5"
export RUN_PARAMS="pca${pca_elem}_mcs${min_cluster_size}_ms${min_samples}_${hdb_mode}"

# cd $SRC_PATH
# if [ "$MOVE_ON" = true ]; then
#     source STG3_META_TDA.sh
# fi

### Stage 4 Metrics
export STG1_GT_CSV="${ROOT_PATH}/${DATASET_NAME}/GT_final/"
export STG4_METRICS="${current_stg3}/metrics"
export STG4_METRIC_RUNNAME="${DATASET_NAME}_${SHAS_NAME}_${FEAT_NAME}_${METHOD_NAME}"

export pred_suffix_added="pred"
export pred_ext="csv"

# cd $SRC_PATH
# if [ "$MOVE_ON" = true ]; then
#     source STG4_ENTROPY.sh
# fi

## Add Azure comparison

#### Get Back to where you once belonged
cp $SRC_PATH/EXP003B_TDA_script_luis.sh $current_stg3/script_contents.txt
conda activate
cd $SRC_PATH