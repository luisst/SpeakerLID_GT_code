#! /bin/bash

export SHAS_LOCATION="/home/luis/Dropbox/SpeechSpring2023/shas"

### Stage 1: VAD Run SHAS on the test set

echo "1) Running SHAS on the test set"

cd $SHAS_LOCATION

# Change Conda environment
conda activate shas

export path_to_yaml_folder="${ROOT_PATH}/${DATASET_NAME}/STG1_${SHAS_NAME}/shas_output_yml"
export path_to_yaml_file="${path_to_yaml_folder}/VAD_${EXP_NAME}.yaml"

export SHAS_ROOT="${SHAS_LOCATION}/repo"
export path_to_checkpoint="${SHAS_LOCATION}/en_sfc_model_epoch-6.pt"

python3 ${SRC_PATH}/folder_verify.py $STG1_FINAL_CSV
python3 ${SRC_PATH}/folder_verify.py $path_to_yaml_folder

echo "VAD input: $STG1_WAVS"

python3 ${SHAS_ROOT}/src/supervised_hybrid/segment.py -wavs $STG1_WAVS -ckpt $path_to_checkpoint -yaml $path_to_yaml_file -max 10 

echo "VAD output: $path_to_yaml_file"

python3 ${SRC_PATH}/Stage1_convert_shasYML_csv.py $path_to_yaml_file $STG1_FINAL_CSV

echo "Converted to CSV: $STG1_FINAL_CSV"

cd $SRC_PATH
