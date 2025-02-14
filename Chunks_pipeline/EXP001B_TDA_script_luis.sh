#! /bin/bash
export MOVE_ON=true
#### Root folder from dropbox 
export ROOT_PATH="/home/luis/Dropbox/DATASETS_AUDIO/Proposal_runs"
export SRC_PATH=$(pwd)

export EXP_NAME="EXP010C"
export DATASET_NAME="TestAO-Irmadb"
# export DATASET_NAME="TestAO-Liz"

export SHAS_NAME="SHAS"
export FEAT_NAME="DV"
export METHOD_NAME="TDA6"

## Segmentation Parameters
export seg_ln="1.0"
export step_size="0.3"
export gap_size="0.4"

## Minium number of nodes and consecutive segments
export nodes_th="1"
export consc_th="1"

## Keppler Mapper parameters
export KM_N_CUBES="4"
export KM_OVERLAP="0.4"

echo -e "\t>>>>> TDA Keppler Mapper Chunks SCRIPT <<<<<"


#### Stage 1 VAD
export STG1_WAVS="${ROOT_PATH}/${DATASET_NAME}/input_wavs/"
export STG1_FINAL_CSV="${ROOT_PATH}/${DATASET_NAME}/STG_1/STG1_${SHAS_NAME}/shas_output_csv/"
# source STG1_SHAS.sh

#### Stage 2 Feature Extraction
export current_stg2="${ROOT_PATH}/${DATASET_NAME}/STG_2/STG2_${EXP_NAME}-${SHAS_NAME}-${FEAT_NAME}"
export STG2_FEATS_PICKLE="${current_stg2}/${DATASET_NAME}_${SHAS_NAME}_${FEAT_NAME}_feats.pkl"

# if [ "$MOVE_ON" = true ]; then
# source STG2_DVECTORS.sh
# fi

#### Stage 3 Unsupervised Method
export current_stg3="${ROOT_PATH}/${DATASET_NAME}/STG_3/STG3_${EXP_NAME}-${SHAS_NAME}-${FEAT_NAME}-${METHOD_NAME}"
export STG3_MERGED_WAVS="${current_stg3}/merged_wavs"
export STG3_FINAL_CSV="${current_stg3}/final_csv"


export pca_elem="16"

# ## TDA HDBSCAN parameters
# export min_cluster_size="9"
# export hdb_mode="eom"
# export min_samples="5"

# ## TDA Projection PCA 
export min_cluster_size="5"
export hdb_mode="leaf"
export min_samples="5"

export RUN_PARAMS="pca${pca_elem}_mcs${min_cluster_size}_ms${min_samples}_${hdb_mode}"


cd $SRC_PATH
if [ "$MOVE_ON" = true ]; then
source STG3_META_TDA.sh
fi

### Stage 4 Metrics
export STG1_GT_CSV="${ROOT_PATH}/${DATASET_NAME}/GT_final/"
export STG4_METRICS="${current_stg3}/metrics"
export STG4_METRIC_RUNNAME="${DATASET_NAME}_${SHAS_NAME}_${FEAT_NAME}_${METHOD_NAME}"

export pred_suffix_added="pred"
export pred_ext="csv"

cd $SRC_PATH
if [ "$MOVE_ON" = true ]; then
    source STG4_ENTROPY.sh
fi

## Add Azure comparison

#### Get Back to where you once belonged
cp $SRC_PATH/EXP001B_TDA_script_luis.sh $current_stg3/script_contents.txt
conda activate
cd $SRC_PATH