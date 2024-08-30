#! /bin/bash

export SHAS_LOCATION="/home/luis/Dropbox/SpeechSpring2023/shas"

### Stage 1: VAD Run SHAS on the test set

echo "1) Running SHAS on the test set"

cd $SHAS_LOCATION

# Change Conda environment
conda activate shas

export path_to_yaml_folder="${ROOT_PATH}/${DATASET_NAME}/STG_1/STG1_${SHAS_NAME}/shas_output_yml"
export path_to_yaml_file="${path_to_yaml_folder}/VAD_${EXP_NAME}.yaml"

export SHAS_ROOT="${SHAS_LOCATION}/repo"
export path_to_checkpoint="${SHAS_LOCATION}/en_sfc_model_epoch-6.pt"

python3 ${SRC_PATH}/folder_verify.py $STG1_FINAL_CSV
python3 ${SRC_PATH}/folder_verify.py $path_to_yaml_folder

echo -e "\n\t>>>>> VAD input: $STG1_WAVS\n"

python3 ${SHAS_ROOT}/src/supervised_hybrid/segment.py -wavs $STG1_WAVS -ckpt $path_to_checkpoint -yaml $path_to_yaml_file -max 10 

echo -e "\t>>>>> VAD output: $path_to_yaml_file"

python3 ${SRC_PATH}/Stage1_convert_shasYML_csv.py $path_to_yaml_file $STG1_FINAL_CSV

echo -e "\t>>>>> Converted to CSV: $STG1_FINAL_CSV"

if [ "$PREDICT_ONLY" = false ]; then

echo -e "\n\t>>>>> Stage 1: Metrics \n"
export VAD_metric_folder="${ROOT_PATH}/${DATASET_NAME}/STG_1/STG1_${SHAS_NAME}/metrics"
python3 ${SRC_PATH}/folder_verify.py $VAD_metric_folder

export VAD_pred_ext="txt"
export shas_method="shas"

source STG2_DVECTORS.sh

python3 ${SRC_PATH}/Stage1b_metric_vad.py --csv_pred_folder $STG1_FINAL_CSV\
 --GT_csv_folder $STG1_GT_CSV\
 --audios_folder $STG1_WAVS\
 --metric_output_folder $VAD_metric_folder\
 --pred_extensions $VAD_pred_ext\
 --method_name $shas_method\
 --run_name $SHAS_NAME

fi

cd $SRC_PATH
