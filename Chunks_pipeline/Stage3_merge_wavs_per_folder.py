from pathlib import Path
from utilities_functions import create_folder_if_missing, \
    get_total_video_length, ffmpeg_split_audio

import glob
import os
import argparse
import shutil
import pprint

def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")

base_path_ex = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TestAO-Liz')
stg3_pred_folders_ex = base_path_ex.joinpath('Testset_stage3','HDBSCAN_pred_output')
stg3_merged_wavs_ex = base_path_ex.joinpath('Testset_stage3','merged_wavs')

stg3_separated_wavs_ex = base_path_ex.joinpath('Testset_stage3','separated_LONG_wav')
stg3_outliers_ex = base_path_ex.joinpath('Testset_stage3','outliers_wavs')

stg1_long_wavs_ex = base_path_ex.joinpath('Testset_stage1','input_wav')

parser = argparse.ArgumentParser()

parser.add_argument('--stg1_long_wavs', type=valid_path, default=stg1_long_wavs_ex, help='Initial WAVs folder path')
parser.add_argument('--stg3_pred_folders', type=valid_path, default=stg3_pred_folders_ex, help='Prediction with folders per label')
parser.add_argument('--stg3_separated_wavs', type=valid_path, default=stg3_separated_wavs_ex, help='Separated per Long wav folder path')
parser.add_argument('--stg3_merged_wavs', type=valid_path, default=stg3_merged_wavs_ex, help='Merged wavs folder path')
parser.add_argument('--stg3_outliers', type=valid_path, default=stg3_outliers_ex, help='Outliers wavs folder path')


args = parser.parse_args()

stg3_pred_folders = args.stg3_pred_folders 
output_merged_audio = args.stg3_merged_wavs

output_separated_wavs = args.stg3_separated_wavs
output_wav_folder_outliers = args.stg3_outliers

original_wav_files = args.stg1_long_wavs


chunk_duration = 1.0 # seconds  
minimum_chunk_duration = 0.7 # seconds
step_length = 0.2 # seconds
gap_duration = 0.5

verbose = True

label_subfolders = [f for f in stg3_pred_folders.iterdir() if f.is_dir()]

for current_pred_label_path in label_subfolders:

    current_predicted_label = current_pred_label_path.name 


    ############################### 1) Copying chunk wavs -> separated folders 

    # INFO: Pointing at folder generated from HDBSCAN / TDA
    current_label_folder = stg3_pred_folders.joinpath(current_predicted_label)

    ## TODO: can be changed to current_pred_label_path
    # List all .wav files in the directory
    all_stg2_wav_files = list(current_pred_label_path.glob('*.wav'))


    # Get the base name of each file, excluding the last substring divided by a dash
    base_names = [('_'.join(Path(f).name.split('_')[:-3])) for f in all_stg2_wav_files]

    # Create sub-directories for each unique base name
    for base_name in set(base_names):
        sub_directory = output_separated_wavs.joinpath(current_predicted_label, base_name)
        create_folder_if_missing(sub_directory)

    # Iterate over each .wav file and copy it to the corresponding sub-directory
    for idx, wav_file in enumerate(all_stg2_wav_files):
        dst_folder = output_separated_wavs.joinpath(current_predicted_label, base_names[idx])
        dst_file = dst_folder.joinpath(wav_file.name)
        shutil.copy(str(wav_file), str(dst_file))

    print(f'\n\nCopied wavs from lbl: {current_predicted_label}')


    ############################### 2) Create DICT successive files (per long audio) 

    for sub_folder in set(base_names):
        print(f'\n{current_predicted_label}\tInside subfolder - {sub_folder}')
        current_sub_directory = output_separated_wavs.joinpath(current_predicted_label, sub_folder)

        # List all .wav files in the sub - directory
        sub_wav_files = list(current_sub_directory.glob('*.wav'))

        # Initialize an empty list to store the tuples
        time_tuples = []

        # Iterate over each .wav file
        for wav_file in sub_wav_files:
            # Split the filename by underscores
            segments = wav_file.stem.split('_')

            # Get the last two segments as start_time and stop_time
            start_time = segments[-3]
            stop_time = segments[-2]

            # Append the tuple to the list
            time_tuples.append((start_time, stop_time, str(wav_file.stem)))


        # Initialize an empty dictionary to store the successive files
        successive_files = {}

        # Initialize a key counter
        key_counter = 0

        # Sort the time_tuples list by start_time
        time_tuples.sort(key=lambda x: float(x[0]))

        # Iterate over the sorted list
        for i in range(len(time_tuples) - 1):
            # Get the current and next tuples
            current_tuple = time_tuples[i]
            next_tuple = time_tuples[i + 1]
            # Calculate the time gap between the current and next tuples
            time_gap = float(next_tuple[0]) - float(current_tuple[1])

            # Check if the time gap is greater than or equal to the desired gap duration
            if  gap_duration >= time_gap:
                # If the time gap is sufficient, add the file paths to the dictionary
                current_file = f"{current_tuple[0]}_{current_tuple[1]}_{current_tuple[2]}"
                next_file = f"{next_tuple[0]}_{next_tuple[1]}_{next_tuple[2]}"

                # If the key already exists in the dictionary, append the next file to its value
                if key_counter in successive_files:
                    successive_files[key_counter].append(str(next_file))
                # Otherwise, create a new key with the current and next files as its value
                else:
                    successive_files[key_counter] = [str(current_file), str(next_file)]
            # If the time gap is not sufficient, increment the key counter
            else:
                key_counter += 1

        # # Print the dictionary
        # print(f'\n')
        # pprint.pprint(successive_files)

        ############################### 3) (inner loop) FOR EACH DICT-> Merge successive files

        # sub_folder is the long wav file name
        print(f'{current_predicted_label}\tMerging files in subfolder - {sub_folder}')

        # Iterate over the dictionary and merge the first star_time and last stop_time
        for key, value in successive_files.items():
            # Get the first and last files in the list
            first_file = value[0]
            last_file = value[-1]

            # Get the start and stop times
            start_time = first_file.split('_')[0]
            stop_time = last_file.split('_')[1]

            # Create the output filename
            output_filename = f"{sub_folder}_{current_predicted_label}_{start_time}_{stop_time}.wav"

            if current_predicted_label == '-1':
                current_merged_wav_path = output_wav_folder_outliers.joinpath(output_filename)
            else:
                current_merged_wav_path = output_merged_audio.joinpath(output_filename)

            # Get the list of input files

            # TODO: locate the original wav files to extract from them the audio
            # Extract audio name
            current_original_wav_filename = f'{sub_folder}.wav' 
            original_wav_path = original_wav_files.joinpath(current_original_wav_filename)


            # Merge the input files into the output file
            ffmpeg_split_audio(original_wav_path,
                               current_merged_wav_path,
                            start_time_csv = start_time,
                            stop_time_csv = stop_time)
                           
            print(f'\t\tCurrent Merged wav: {output_filename}')