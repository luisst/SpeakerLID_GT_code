from pathlib import Path
import csv
from utilities_functions import get_total_video_length
import argparse
from utilities_functions import create_folder_if_missing
import shutil
import os

def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


base_path_ex = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Proposal_runs', 'TestAO-Liz')
merged_wav_folder_ex = base_path_ex.joinpath('Testset_stage3','merged_wav_files')
csv_folder_ex = base_path_ex.joinpath('Testset_stage4','final_csv')
separated_folder_ex = base_path_ex.joinpath('Testset_stage4','separated_merged_wavs')

parser = argparse.ArgumentParser()
parser.add_argument('--stg3_merged_wavs', type=valid_path, default=merged_wav_folder_ex, help='Stg3 merged WAVs folder path')
parser.add_argument('--stg4_final_csv', type=valid_path, default=csv_folder_ex, help='Stg4 final csv from merged wavs folder path')
parser.add_argument('--stg4_separated_merged_wavs', type=valid_path, default=separated_folder_ex, help='Stg4 merged wavs separated in labels folder path')

args = parser.parse_args()

merged_wav_folder= args.stg3_merged_wavs 
csv_folder= args.stg4_final_csv
separated_wav_folder = args.stg4_separated_merged_wavs

labels_dict = {}

# Iterate over all files in the directory
for path in merged_wav_folder.iterdir():
    # Check if the file is a .wav file
    if path.suffix == '.wav':
        # Split the filename into parts
        parts = path.stem.split('_')  # use stem to get filename without extension

        # Extract the required parts
        origin_wav_filename = '_'.join(parts[:-3])
        predicted_label = parts[-3]
        start_time = parts[-2]
        end_time = parts[-1]

        # Get the duration of the .wav file
        current_duration = get_total_video_length(path)

        current_wav_name = path.name

        # Print the name of the file
        print(f'Filename: {current_wav_name}')

        value_to_store = [current_wav_name, predicted_label, start_time, end_time, current_duration]

        # Check if the origin_wav_filename is new
        if origin_wav_filename not in labels_dict:
            labels_dict[origin_wav_filename] = []

        # Append the value_to_store to the corresponding key
        labels_dict[origin_wav_filename].append(value_to_store)

for key, value in labels_dict.items():
    output_file = csv_folder.joinpath(f'{key}_pred.csv')
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        for row in value:
            writer.writerow(row)


## Print notification
print(f'\n\n\t*** Copy merged wavs into separated folders ***\n\n')

# List with all wavs path files
merged_wavs_files = list(merged_wav_folder.glob('*.wav'))

# Iterate over all merged wavs files
for current_wav_path in merged_wavs_files:
    # Extract the required parts
    segments_wav_name = current_wav_path.stem.split('_')
    predicted_label = segments_wav_name[-3]
    start_time = segments_wav_name[-2]
    end_time = segments_wav_name[-1]

    # Create the output folder
    output_folder = separated_wav_folder.joinpath(predicted_label)
    create_folder_if_missing(output_folder)

    # Create the output file
    output_file_path = output_folder.joinpath(f'{current_wav_path.stem}.wav')

    # Print the output file
    print(f'Label {predicted_label}: {output_file_path.name}')

    # Copy the file
    shutil.copy(str(current_wav_path), str(output_file_path))