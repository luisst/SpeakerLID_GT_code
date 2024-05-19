import librosa
import numpy as np
from pathlib import Path
import os
import pandas as pd
import argparse

from utilities_pyannote_metrics import matching_basename_pathlib_gt_pred

def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def convert_consecutive(arr, X):
    new_arr = arr[:]
    count = 0
    
    for i in range(len(arr)):
        if arr[i]:
            count += 1
        else:
            if count <= X:
                for j in range(i - count, i):
                    new_arr[j] = False
            count = 0
    
    # Handling the case where the last X elements are True
    if count <= X:
        for j in range(len(arr) - count, len(arr)):
            new_arr[j] = False
    
    return new_arr

def calculate_rms_segments_db(audio_file,
                              output_folder_path,
                              segment_duration=0.2,
                              th_db=-24,
                              verbose=False):
    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None)

    # Calculate the total number of samples in each segment
    segment_samples = int(segment_duration * sr)

    # Calculate the number of segments
    num_segments = len(y) // segment_samples

    # Initialize an empty list to store RMS values for each segment
    rms_values = []

    # Iterate over each segment and calculate RMS value
    for i in range(num_segments):
        # Extract the segment
        segment = y[i * segment_samples: (i + 1) * segment_samples]

        # Calculate RMS value for the segment
        rms = np.sqrt(np.mean(segment**2))

        # Append RMS value to the list
        rms_values.append(rms)

    # Convert rms_values to a NumPy array
    rms_values = np.array(rms_values)

    # Calculate maximum possible amplitude for PCM_16
    max_amplitude = 2 ** 15  # 16-bit PCM, so max amplitude is 2^15

    # Calculate full scale level in dB
    full_scale_db = 20 * np.log10(max_amplitude)

    # Convert RMS values to dB
    rms_db = 20 * np.log10(rms_values / max_amplitude)

    # Convert to full scale dB
    full_scale_rms_db = full_scale_db + rms_db

    # Convert full_scale_rms_db to boolean numpy array with threshold -24 dB
    mask_bool = full_scale_rms_db < th_db 

    # Convert consecutive True values to False if the number of True values is less than 2
    mask_bool_1st = convert_consecutive(mask_bool, 2)

    # Invert the mask_bool_1st
    mask_bool_1st_inverse = ~mask_bool_1st

    # Second pass
    mask_bool_2nd_inverse = convert_consecutive(mask_bool_1st_inverse, 2)

    # Invert the mask_bool_2nd_inverse
    mask_bool_2nd = ~mask_bool_2nd_inverse

    if verbose:
        # Print the number of segments
        print(f'Number of segments: {len(full_scale_rms_db)}')

        # Length of audio in seconds
        audio_duration_seconds = len(y) / sr
        audio_duration_from_segments = len(full_scale_rms_db)*segment_duration

        # Print both audio duration and audio duration from segments
        print(f'Audio duration: {audio_duration_seconds} seconds')
        print(f'Audio duration from segments: {audio_duration_from_segments} seconds')

    # Write into a csv file the full scale rms values in steps of 0.2 seconds
    output_csv_path = output_folder_path / f'{audio_file.stem}.txt' 

    # Print the output path
    print(f'\nOutput CSV path: {output_csv_path}')

    with open(str(output_csv_path), 'w') as f:
        for i in range(len(full_scale_rms_db)):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration
            f.write(f'{audio_file.name}\t{start_time:.2f}\t{end_time:.2f}\t{mask_bool_2nd[i]}\t{full_scale_rms_db[i]:.2f}\n')

    return full_scale_rms_db


# Define the function to split prediction segments based on mask
def split_segments(prediction_start_time, prediction_stop_time, current_mask, X):
    high_db_segments = []
    current_segment_start = prediction_start_time
    current_segment_stop = prediction_stop_time
    consecutive_low_db_count = 0

    current_mask = current_mask.reset_index(drop=True)

    silence_flag = False

    # Number of rows in the mask dataframe
    num_rows = current_mask.shape[0]
    
    for index, row in current_mask.iterrows():

        if row['mask_val']: # If the segment is silent
            consecutive_low_db_count += 1

            # If consecutive low dB segments reach X, split the segment
            if consecutive_low_db_count == X:

                if index-X < 0:
                    print(f'...Started with Silence: {current_segment_start}')
                else:
                    # Assign the start_time value of X rows before in the current_mask dataframe
                    current_segment_stop = current_mask.loc[index-X, 'end_time']

                    # Add the segment before the low dB portion
                    high_db_segments.append((current_segment_start, current_segment_stop))

                    # Print the segment
                    print(f">>>>>\tSegment: {current_segment_start} - {current_segment_stop}")

                silence_flag = True

        else:
            if silence_flag:
                # Reset the start time for the next segment
                current_segment_start = row['start_time']
                consecutive_low_db_count = 0
                silence_flag = False

                # Print
                print(f">\tStart new segment: {current_segment_start}")
            
            # Verify last iteration
            if index == num_rows-1 and consecutive_low_db_count < X:
                high_db_segments.append((current_segment_start, prediction_stop_time))
                print(f'>>>>>\tEnded with Speech: {current_segment_start} - {prediction_stop_time}')
    

    low_db_segments = []
    last_stop_time = prediction_start_time

    for high_db_segment in high_db_segments:
        current_segment_start, current_segment_stop = high_db_segment
        if last_stop_time < current_segment_start:
            low_db_segments.append((last_stop_time, current_segment_start))
        last_stop_time = current_segment_stop

    if last_stop_time < prediction_stop_time:
        low_db_segments.append((last_stop_time, prediction_stop_time)) 


    return high_db_segments, low_db_segments

# Example usage
input_wavs_folder_ex = Path('./Silent_detection')
output_mask_csv_folder_ex = Path('./Silent_detection/mask_output_csv')
VAD_results_folder_ex = Path('./Silent_detection/VAD_results')
output_csv_folder_ex = Path('./Silent_detection/filtered_csv')

# Define the command-line arguments
parser = argparse.ArgumentParser(description='Process some files.')
parser.add_argument('--input_wav_folder', type=valid_path, default=input_wavs_folder_ex, help='Folder with long audio files')
parser.add_argument('--output_mask_csv_folder', type=valid_path, default=output_mask_csv_folder_ex, help='Output folder for mask output CSV')
parser.add_argument('--vad_results_folder', type=valid_path, default=VAD_results_folder_ex ,help='Folder with VAD output csv files')
parser.add_argument('--output_csv_folder', type=valid_path, default=output_csv_folder_ex , help='Output folder for Filtered VAD csv')

parser.add_argument('--segment_duration', default='0.3' , help='Duration of each segment in seconds')
parser.add_argument('--thres', default='-24' , help='Threshold in FS dB for silence detection')

# Parse the command-line arguments
args = parser.parse_args()

input_wav_folder = args.input_wav_folder
output_mask_csv_folder = args.output_mask_csv_folder
vad_results_folder = args.vad_results_folder
output_csv_folder = args.output_csv_folder

segment_duration = float(args.segment_duration)
th_db = int(args.thres)

# List of all wav files in wav_folder
wav_files = list(input_wav_folder.glob('*.wav'))

# Generate the mask for each wav file
for current_audio_path in wav_files: 
    calculate_rms_segments_db(current_audio_path,
                                output_mask_csv_folder,
                                segment_duration=segment_duration,
                                th_db=th_db,
                                verbose=True)

## Apply the mask to the VAD csv output

# Match each mask with the corresponding VAD output
matches_for_masking = \
    matching_basename_pathlib_gt_pred(vad_results_folder, 
                                    output_mask_csv_folder, 
                                    gt_suffix_added='',
                                    pred_suffix_added='',
                                    gt_ext = 'txt',
                                    pred_ext = 'txt')

### !!! in boolean mask values TRUE: Silence 

# for each pair
for current_gt_pth, current_pred_pth in matches_for_masking:
    print(f'\n\n\t{current_gt_pth.stem}')
    print(f'GT: {current_gt_pth}')
    print(f'Pred: {current_pred_pth}')

    # Read the VAD csv file
    vad_df = pd.read_csv(current_gt_pth, sep='\t', header=None)
    vad_df.columns = ['audio_file', 'start_time', 'end_time']

    # Read the mask csv file
    mask_df = pd.read_csv(current_pred_pth, sep='\t', header=None)
    mask_df.columns = ['audio_file', 'start_time', 'end_time', 'mask_val', 'rms_db']

    # Initialize a list to store the filtered VAD segments
    filtered_vad_segments = []

    filtered_noise_segments = []

    # Iterate over each VAD segment
    for i in range(len(vad_df)):
        # Extract the VAD segment
        current_vad_segment = vad_df.iloc[i]

        # Extract the start and end time of the VAD segment
        start_time = current_vad_segment['start_time']
        end_time = current_vad_segment['end_time']

        # Extract the corresponding mask segment
        mask_segment = mask_df[(mask_df['start_time'] >= start_time) & (mask_df['end_time'] <= end_time)]

        high_db_segments, low_db_segments = split_segments(start_time, end_time, mask_segment, 3)

        # Extend the filtered VAD segments with the high_db_segments
        filtered_vad_segments.extend(high_db_segments)
        filtered_noise_segments.extend(low_db_segments)

    # Write the filtered VAD segments to a CSV file
    current_output_csv_path = output_csv_folder / f'{current_gt_pth.stem}.txt'

    current_output_noises_csv_path = output_csv_folder / f'{current_gt_pth.stem}_NOISES.txt'

    with open(str(current_output_csv_path), 'w') as f:
        for segment in filtered_vad_segments:
            f.write(f'{current_gt_pth.stem}\t{segment[0]:.2f}\t{segment[1]:.2f}\n')
    
    print(f'Wrote to TXT path: {current_output_csv_path}\n')

    with open(str(current_output_noises_csv_path), 'w') as f:
        for segment in filtered_noise_segments:
            f.write(f'{current_gt_pth.stem}\t{segment[0]:.2f}\t{segment[1]:.2f}\n')
    
    print(f'Wrote to TXT path: {current_output_noises_csv_path}\n')

