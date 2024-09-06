from pathlib import Path
import csv
from utilities_functions import get_total_video_length
import argparse
from utilities_functions import create_folder_if_missing
import shutil
import os
import pickle
import matplotlib.pyplot as plt


def merge_segments_no_overlaps(segments):
    # Step 1: Sort the segments by start_time
    segments.sort()

    merged = []
    for segment in segments:
        # If the list of merged segments is empty or the current segment doesn't overlap with the previous one
        if not merged or merged[-1][1] < segment[0]:
            # Add the current segment to the list
            merged.append(segment)
        else:
            # Step 2: Merge the overlapping segments
            merged[-1] = (merged[-1][0], max(merged[-1][1], segment[1]))

    return merged


def calculate_overlap(start1, end1, start2, end2):
    return max(0, min(end1, end2) - max(start1, start2))

def calculate_iou(speaker_predictions, vad_predictions):
    total_intersection = 0
    total_union = 0

    for start_vad, end_vad in vad_predictions:
        vad_duration = end_vad - start_vad
        intersection = 0

        for start_speaker, end_speaker in speaker_predictions:
            overlap = calculate_overlap(start_vad, end_vad, start_speaker, end_speaker)
            intersection += overlap

        union = vad_duration + sum(end - start for start, end in speaker_predictions) - intersection
        total_intersection += intersection
        total_union += union

    iou = total_intersection / total_union if total_union > 0 else 0
    return iou


def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


base_path_ex = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Proposal_runs', 'TestAO-Irmast4')
merged_wav_folder_ex = base_path_ex.joinpath('STG_3','STG3_EXP001-SHAS-DV-TDA','merged_wavs')
csv_folder_ex = base_path_ex.joinpath('STG_3','STG3_EXP001-SHAS-DV-TDA','final_csv')
separated_folder_ex = base_path_ex.joinpath('STG_3','STG3_EXP001-SHAS-DV-TDA','separated_merged_wavs')
vad_folder_ex = base_path_ex.joinpath('STG_1','STG1_SHAS','shas_output_csv')
tda_flag_ex = True

parser = argparse.ArgumentParser()
parser.add_argument('--stg1_final_csv', type=valid_path, default=vad_folder_ex, help='Stg1 VAD csvs folder path')
parser.add_argument('--stg3_merged_wavs', type=valid_path, default=merged_wav_folder_ex, help='Stg3 merged WAVs folder path')
parser.add_argument('--stg4_final_csv', type=valid_path, default=csv_folder_ex, help='Stg4 final csv from merged wavs folder path')
parser.add_argument('--stg4_separated_merged_wavs', type=valid_path, default=separated_folder_ex, help='Stg4 merged wavs separated in labels folder path')
parser.add_argument('--TDA_flag', type=bool, default=tda_flag_ex, help='Flag to indicate if TDA is used or not')

args = parser.parse_args()

vad_csv_folder = args.stg1_final_csv
merged_wav_folder= args.stg3_merged_wavs 
csv_folder= args.stg4_final_csv
separated_wav_folder = args.stg4_separated_merged_wavs
tda_flag = args.TDA_flag

labels_dict = {}

merged_times_list = []
dict_merged_times = {}

# Iterate over all files in the directory
for current_wav_path in merged_wav_folder.iterdir():
    # Check if the file is a .wav file
    if current_wav_path.suffix == '.wav':
        # Split the filename into parts
        parts = current_wav_path.stem.split('_')  # use stem to get filename without extension

        # Extract the required parts
        origin_wav_filename = '_'.join(parts[:-3])
        predicted_label = parts[-3]
        start_time = parts[-2]
        end_time = parts[-1]

        # Get the duration of the .wav file
        current_duration = get_total_video_length(current_wav_path)

        # Append the duration to the list
        merged_times_list.append(current_duration)

        current_wav_name = current_wav_path.name

        value_to_store = [current_wav_name, predicted_label, start_time, end_time, current_duration]

        # Check if the origin_wav_filename is new
        if origin_wav_filename not in labels_dict:
            labels_dict[origin_wav_filename] = []

        # Append the value_to_store to the corresponding key
        labels_dict[origin_wav_filename].append(value_to_store)

        ## Extract base name
        current_base_name = '_'.join(current_wav_path.name.split('_')[:-3])

        if current_base_name not in dict_merged_times:
            dict_merged_times[current_base_name] = []
        
        dict_merged_times[current_base_name].append((float(start_time), float(end_time)))

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
    # print(f'Label {predicted_label}: {output_file_path.name}')

    # Copy the file
    shutil.copy(str(current_wav_path), str(output_file_path))


### Generate stats plot

### 1) Count the audio durations of merged files
# merged_times_list
lengths1_avg = sum(merged_times_list) / len(merged_times_list)
std1 = (sum([(x - lengths1_avg) ** 2 for x in merged_times_list]) / len(merged_times_list)) ** 0.5
title_lengths_merged1 = f'Lengths Merged {len(merged_times_list)}| Avg:{lengths1_avg:.2f}, Std:{std1:.2f}| {min(merged_times_list)} - {max(merged_times_list)}'

### 2) Count the number of merged files
if tda_flag:
    counts_pickle_path = Path.joinpath(merged_wav_folder.parent, 'counts_segments.pkl')

    # Open the pickle file in binary read mode
    with open(str(counts_pickle_path), 'rb') as file:
        # Deserialize the list from the file
        counts_segments = pickle.load(file)
    
    counts2_avg = sum(counts_segments) / len(counts_segments)
    std2 = (sum([(x - counts2_avg) ** 2 for x in counts_segments]) / len(counts_segments)) ** 0.5
    title_cnc2_merged=f'CNC seg merged {len(counts_segments)}| Avg:{counts2_avg:.2f}, Std:{std2:.2f}| {min(counts_segments)} - {max(counts_segments)}'


### 3) Merged overlapping
time_segments_all = []

# Iterate over the values of the dictionary and extend the combined list
for value_list in dict_merged_times.values():
    time_segments_all.extend(value_list)

# Step 1: Sort the segments by start_time
time_segments_all.sort()

merged_overlaps = []
for i in range(len(time_segments_all)):
    for j in range(i + 1, len(time_segments_all)):
        # Get start and end times of the current segment and the next segment
        start1, end1 = time_segments_all[i]
        start2, end2 = time_segments_all[j]

        # Step 2: Check if there's an overlap
        if start2 < end1:
            # Step 3: Calculate the overlap
            overlap_start = max(start1, start2)
            overlap_end = min(end1, end2)
            
            # Add the overlap tuple to the list
            merged_overlaps.append((overlap_start, overlap_end))

overlaps_durations = []
for start_time, end_time in merged_overlaps:
    duration = end_time - start_time
    overlaps_durations.append(duration)


### 4) VAD overlapping
## At this point I don't care about labels, just the overlapping
csv_files = list(vad_csv_folder.glob('*.txt'))

total_vad_overlaps_durations = []

# Total duration of merged segments without overlaps
no_overlaps_total = 0
iou_list = []

for csv_file_path in csv_files:
    # Initialize an empty list to store the tuples
    current_vad_time_intervals = []

    # Open the CSV file in read mode
    with open(csv_file_path, 'r', newline='') as csvfile:
        # Create a CSV reader object with tab delimiter
        csvreader = csv.reader(csvfile, delimiter='\t')
        
        # Iterate over each row in the CSV file
        for row in csvreader:
            # Extract start_time and stop_time and store them as a tuple
            start_time = row[1]
            stop_time = row[2]
            current_vad_time_intervals.append((float(start_time), float(stop_time)))
    
    # Extract the base name of the CSV file
    vad_base_name = csv_file_path.stem

    # Extract the list of merged times
    raw_merged_times = dict_merged_times[vad_base_name]

    # Remove overlapping segments
    no_overlaps_segments = merge_segments_no_overlaps(raw_merged_times)

    # Accumulate the total duration of the segments without overlaps
    no_overlaps_total += sum([end - start for start, end in no_overlaps_segments])

    vad_overlaps = []

    # Step 1 & 2: Iterate through each tuple in list1 and list2 and check for overlaps
    for start1, end1 in current_vad_time_intervals:
        for start2, end2 in no_overlaps_segments:
            # Find the overlapping segment
            overlap_start = max(start1, start2)
            overlap_end = min(end1, end2)

            # Step 3: If there's an overlap, add it to the result
            if overlap_start < overlap_end:
                vad_overlaps.append((overlap_start, overlap_end))
    
    # Calculate the duration of the overlaps
    overlaps_durations = [end - start for start, end in vad_overlaps]

    # Accumulate the total duration of the overlaps
    total_vad_overlaps_durations.extend(overlaps_durations)


    iou_value = calculate_iou(no_overlaps_segments, current_vad_time_intervals)
    iou_list.append(iou_value)
    
iou_avg = sum(iou_list) / len(iou_list) * 100
title_vad4_merged=f'VAD overlaps merged. IoU: {iou_avg:.2f}'
### 5) Plot histograms of the four lists    

sum_overlaps = sum(overlaps_durations)
if no_overlaps_total == 0:
    overlap_percentage = 0
    print(f'>>>>>>>>>> No overlaps found in the merged segments')
else:
    overlap_percentage = sum_overlaps / no_overlaps_total * 100
title_over3_merged=f'Overlaps merged {(len(overlaps_durations))}| {overlap_percentage:.2f}% ({sum_overlaps:.2f} / {no_overlaps_total:.2f})'

# Creating subplots
fig, axs = plt.subplots(2, 2, figsize=(10, 8))

# Plotting histograms
axs[0, 0].hist(merged_times_list, bins=9, color='blue', alpha=0.7)
axs[0, 0].set_title(title_lengths_merged1)

if tda_flag:
    axs[0, 1].hist(counts_segments, bins=8, color='green', alpha=0.7)
    axs[0, 1].set_title(title_cnc2_merged)

axs[1, 0].hist(overlaps_durations, bins=2, color='red', alpha=0.7)
axs[1, 0].set_title(title_over3_merged)

axs[1, 1].hist(total_vad_overlaps_durations, bins=5, color='purple', alpha=0.7)
axs[1, 1].set_title(title_vad4_merged)

# General title
# fig.suptitle('Histograms of Four Lists', fontsize=16)

# Adjusting layout
plt.tight_layout()

histogram_path = csv_folder.joinpath('histograms_summary.png')
# Saving the figure
plt.savefig(histogram_path, dpi=300)
