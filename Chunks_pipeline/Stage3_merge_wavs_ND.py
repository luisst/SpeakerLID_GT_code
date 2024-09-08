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

seg_ln_ex = '1.0'
step_size_ex = '0.2'
gap_size_ex = '0.4'
consc_th_ex = 2

parser = argparse.ArgumentParser()

parser.add_argument('--stg1_long_wavs', type=valid_path, default=stg1_long_wavs_ex, help='Initial WAVs folder path')
parser.add_argument('--stg3_pred_folders', type=valid_path, default=stg3_pred_folders_ex, help='Prediction with folders per label')
parser.add_argument('--stg3_separated_wavs', type=valid_path, default=stg3_separated_wavs_ex, help='Separated per Long wav folder path')
parser.add_argument('--stg3_merged_wavs', type=valid_path, default=stg3_merged_wavs_ex, help='Merged wavs folder path')
parser.add_argument('--stg3_outliers', type=valid_path, default=stg3_outliers_ex, help='Outliers wavs folder path')

parser.add_argument('--ln', type=float, default=seg_ln_ex, help='Stg2 chunks length ihn seconds')
parser.add_argument('--st', type=float, default=step_size_ex, help='Stg2 chunks step_size in seconds')
parser.add_argument('--gap', type=float, default=gap_size_ex, help='Stg2 chunks gap in seconds')
parser.add_argument('--consc_th', type=int, default=consc_th_ex, help='Stg3 consecutive chunks threshold')

args = parser.parse_args()

stg3_pred_folders = args.stg3_pred_folders 
output_merged_audio = args.stg3_merged_wavs

output_separated_wavs = args.stg3_separated_wavs
output_wav_folder_outliers = args.stg3_outliers

original_wav_files = args.stg1_long_wavs

chunk_duration = float(args.ln)
minimum_chunk_duration = chunk_duration - 0.1 # seconds
step_length = float(args.st) 
gap_duration = float(args.gap) 

consecutive_threshold = int(args.consc_th)

counts_segments = []

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
        # print(f'\n{current_predicted_label}\tInside subfolder - {sub_folder}')
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
            time_tuples.append((start_time, stop_time))

        # Sort the time_tuples list by start_time
        time_tuples.sort(key=lambda x: float(x[0]))

        merged_segments = []
        current_start, current_stop = time_tuples[0]
        current_start = float(current_start)
        current_stop = float(current_stop)
        current_count = 1

        for start, stop in time_tuples[1:]:
            start = float(start)
            stop = float(stop)
            if start - current_stop <= gap_duration:
                current_stop = stop
                current_count += 1
            else:
                merged_segments.append((current_start, current_stop))
                counts_segments.append(current_count)
                current_start, current_stop = start, stop
                current_count = 1

        # Add the last segment only if it hasn't been added in the loop
        if not merged_segments or merged_segments[-1] != (current_start, current_stop):
            merged_segments.append((current_start, current_stop))
            counts_segments.append(current_count)

        # # Print the dictionary
        # print(f'\n')
        # pprint.pprint(successive_files)

        ############################### 3) (inner loop) FOR EACH DICT-> Merge successive files

        # sub_folder is the long wav file name
        # print(f'{current_predicted_label}\tMerging files in subfolder - {sub_folder}')

        # Iterate over the dictionary and merge the first star_time and last stop_time
        for idx_seg, current_merged_timestamps in enumerate(merged_segments):
            # Get the start and stop times
            start_time = current_merged_timestamps[0]
            stop_time = current_merged_timestamps[1]

            if counts_segments[idx_seg] < consecutive_threshold:
                continue

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
                            start_time_csv = str(start_time),
                            stop_time_csv = str(stop_time))
                           
            # print(f'\t\tCurrent Merged wav: {output_filename}')

###
print(f'\n\n\n *** Summary ***')
print(f'Stats of concatenated files:')
import pickle

counts_pickle_path = Path.joinpath(output_merged_audio.parent, 'counts_segments.pkl')

# Open a file in binary write mode
with open(str(counts_pickle_path), 'wb') as file:
    # Serialize the list and write it to the file
    pickle.dump(counts_segments, file)

