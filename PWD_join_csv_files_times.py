from pathlib import Path
import csv
import pandas as pd
from utilities_functions import get_total_video_length

## Path to the audios folder to read their duration
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','TestSet','02_Selected_clips','G-C1L1P-Apr27-E-Irma_q2_03-08')

input_csv_folder = root_dir.joinpath('final_csv')
output_folder_csv_pth = input_csv_folder 
# Path to the folder
path_to_audios = root_dir.joinpath('praat_files')

# Get the audio files
audio_files = list(path_to_audios.glob('*.wav'))

# Get the csv files
csv_files = list(input_csv_folder.glob('*.csv'))

# Initialize an empty list to store the pairs of csv and wav files
csv_wav_pairs = []

# For each csv file in the csv_files list
for csv_file in csv_files:
    # Extract the base name of the csv file (without extension)
    base_name = csv_file.stem
    base_name = base_name.replace('_praat_ready', '')


    # Find the corresponding wav file in the audio_files list by matching the base name
    wav_file = next((audio_file for audio_file in audio_files if audio_file.stem == base_name), None)

    # If the wav file is found
    if wav_file is not None:
        # Use the find_audio_duration function to get the duration of the wav file
        duration = get_total_video_length(wav_file)

        # Append a list containing the csv file path, wav file path, and the duration to the list
        csv_wav_pairs.append([csv_file, wav_file, duration])


# For each index in the range from 0 to the length of csv_wav_pairs - 1
for i in range(len(csv_wav_pairs) - 1):
    # Get the current pair and the next pair
    current_pair = csv_wav_pairs[i]
    next_pair = csv_wav_pairs[i + 1]

    # Extract the base name of the current pair's csv file (without extension) and remove the '_praat_ready' suffix
    current_base_name = current_pair[0].stem.replace('_praat_ready', '')
    # Extract the last 3 digits from the base name
    current_last_three_digits = int(current_base_name.split('_')[-1])

    # Repeat the above two steps for the next pair's csv file
    next_base_name = next_pair[0].stem.replace('_praat_ready', '')
    next_last_three_digits = int(next_base_name.split('_')[-1])

    # If the last 3 digits of the current pair's csv file incremented by 1 is not equal to the last 3 digits of the next pair's csv file
    if current_last_three_digits + 1 != next_last_three_digits:
        # Raise an error and print the paths of the two csv files that are not consecutive
        raise ValueError(f"The csv files {current_pair[0]} and {next_pair[0]} are not consecutive.")

# If the loop completes without raising an error, print that the csv pairs are all consecutive
print(f'CSV pairs are all consecutive')


# Initialize a variable to store the total duration of all previous csv files
total_duration = 0

current_output_json_pth = f'{root_dir.parts[-1]}_GT.csv'
new_transcr_path = output_folder_csv_pth.joinpath(current_output_json_pth)
new_file = open(new_transcr_path, "w")

for csv_file, wav_file, duration in csv_wav_pairs:

    ## Read all lines from current csv file
    for current_line in open(csv_file, 'r'):

        # Read the current line
        speaker, lang, start_time, stop_time = current_line.strip().split('\t')

        new_start_time = float(start_time) + total_duration
        new_stop_time = float(stop_time) + total_duration

        new_file.write(f'{speaker}\t{lang}\t{new_start_time:.2f}\t{new_stop_time:.2f}\n')

    # Add the duration of the current csv file to the total duration
    total_duration += duration


new_file.close()