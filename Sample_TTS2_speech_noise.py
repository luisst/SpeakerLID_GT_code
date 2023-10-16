import random
import subprocess
from pathlib import Path
import pandas as pd
import re
import sys
import shutil

from utilities_functions import create_folder_if_missing, extract_matching_csv_media

def export_speechnoise_segments(segment_extracts, interval_extracts, audio_file, 
                    csv_file, output_dir_base, dict_param, 
                    verbose = False):

    num_segments = dict_param['num_segments']

    ###----------------------------- Export Speech
    # function to export the segments
    if num_segments > len(segment_extracts):
        output_number = len(segment_extracts)
    else:
        output_number = num_segments

    output_path_speech = output_dir_base.joinpath(dict_param['speech_folder']) 
    # Extract speech/noise segments as WAV files
    for i in range(0, output_number):
        output_file = output_path_speech.joinpath(f'{audio_file.stem}_{segment_extracts[i][0]}_{i:04d}.wav')
        if verbose:
            print(f'to extract: {segment_extracts[i]}\n')
        extract_segment(audio_file, segment_extracts[i][1], segment_extracts[i][2], output_file)

    print(f'{output_number} speech segments extracted from {csv_file.name}.')


    ###----------------------------- Export Noises
    # function to export the segments
    if num_segments > len(interval_extracts):
        output_number = len(interval_extracts)
    else:
        output_number = num_segments

    output_path_speech = output_dir_base.joinpath(dict_param['noises_folder']) 

    # Extract speech/noise segments as WAV files
    for i in range(0, output_number):
        output_file = output_path_speech.joinpath(f'{audio_file.stem}_{interval_extracts[i][0]}_{i:04d}.wav')
        if verbose:
            print(f'to extract: {interval_extracts[i]}\n')
        extract_segment(audio_file, interval_extracts[i][1], interval_extracts[i][2], output_file)

    print(f'{output_number} noise segments extracted from {csv_file.name}.')


def merge_overlapping_segments(segments):
    if not segments:
        return []

    # Sort the segments by their start times
    sorted_segments = sorted(segments, key=lambda x: x[1])

    merged_segments = []
    current_segment = sorted_segments[0]

    for segment in sorted_segments[1:]:
        if segment[1] <= current_segment[2]:
            # Merge the current segment with the overlapping segment
            current_segment = (current_segment[0] + ", merged", current_segment[1], max(current_segment[2], segment[2]))
        else:
            merged_segments.append(current_segment)
            current_segment = segment

    merged_segments.append(current_segment)
    return merged_segments


def get_audio_duration(audio_file):
    # Use ffprobe to get audio duration
    command = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
        str(audio_file)
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    duration = float(result.stdout)
    return duration


def extract_segment(audio_file, start_time, end_time, output_file):
    # Use ffmpeg to extract segment from audio
    command = [
        'ffmpeg', '-i', str(audio_file), '-ss', str(start_time), '-to', str(end_time),
        '-c', 'copy', '-y', str(output_file)
    ]
    subprocess.run(command, capture_output=True)


def select_speech_segments(csv_directory, audio_directory, dict_param,
                               output_dir_base):
                               
    # Iterate over CSV files in the directory
    ending_csv = dict_param['ending_csv']

    matching_csv_list, matching_media_list = extract_matching_csv_media(csv_directory, 
                                                    audio_directory, 
                                                    ending_csv=ending_csv)

    for media_idx, csv_file in enumerate(matching_csv_list):

        # Select speech/noise segments for each CSV file
        select_speech_segments_single(csv_file, 
                                      matching_media_list[media_idx],
                                    dict_param,
                                      output_dir_base, verbose=True)


def select_speech_segments_single(csv_file, audio_file, dict_param, output_dir_base,
                                  verbose = False):

    min_length = dict_param['min_length'] 
    max_length = dict_param['max_length']

    # Load speech segments from CSV file using pandas
    df = pd.read_csv(csv_file, header=None,  sep='\t', index_col=False)
    # Get the first value from the first column
    first_value = df.iloc[0, 0]
    # Check if the first value matches the format 'SXEng' or 'SXSpa'
    if re.match(r'^S\d[0-9]((Eng)\|(Spa))$', str(first_value)):
        gt_segments = df.values.tolist()
    else:
        df = df.drop(df.columns[1], axis=1)
        gt_segments = df.values.tolist()

    # Get audio duration
    audio_duration = get_audio_duration(audio_file)

    segment_extracts, interval_extracts = extract_audio_segments(gt_segments, audio_duration,
                                                                 min_length,
                                                                max_length)

    print("Random Order of Segment Extracts:")
    for extract in segment_extracts:
        print(extract)

    print("\nRandom Order of Interval Extracts:")
    for extract in interval_extracts:
        print(extract)
    
    ## Actually perform the audio extraction
    export_speechnoise_segments(segment_extracts, interval_extracts,  audio_file, 
                        csv_file, output_dir_base, dict_param, 
                        verbose = True)


def extract_audio_segments(gt_segments, total_time,
                           min_extract_length, max_extract_length):

    # Create a list to store the 3-second extracts within segments
    segment_extracts = []

    # Create a list to store the 3-second extracts between segments
    interval_extracts = []

    # Iterate through the rows of the DataFrame
    for row in gt_segments:
        label, start, end = row[0], row[1], row[2]
        
        # Calculate the duration of the segment
        segment_duration = end - start

        # Check if the segment is at least as long as the minimum extract length
        if segment_duration >= min_extract_length:
            current_start = start

            while current_start + min_extract_length + max_extract_length/2 <= end:
                # Generate a random extract length between min and max
                extract_length = round(random.uniform(min_extract_length, max_extract_length), 2)

                # Create non-overlapping extracts within the segment
                if current_start + extract_length <= end:
                    current_end = current_start + extract_length
                    segment_extracts.append((label, current_start, current_end))
                    current_start = current_end
                else:
                    break
        else:
            print(f"Segment '{label}' is less than {min_extract_length} seconds long and will be skipped.")

    merged_gt_segments = merge_overlapping_segments(gt_segments)
    max_possible_audio_length = 1*60*60*24 #1 day in seconds
    merged_gt_segments.insert(0, ('SX', -1, 0))
    merged_gt_segments.append(('SX', total_time, max_possible_audio_length))

    # Iterate through the sorted rows to create interval extracts
    for i in range(1, len(merged_gt_segments)):
        prev_end = merged_gt_segments[i - 1][-1]
        current_start = merged_gt_segments[i][-2]

        while current_start - prev_end >= min_extract_length + max_extract_length/2:
            # Generate a random extract length between min and max
            extract_length = round(random.uniform(min_extract_length, max_extract_length), 2)

            if current_start - extract_length >= prev_end:
                interval_extracts.append(('Interval', prev_end, prev_end + extract_length))
                prev_end += extract_length
            else:
                break

    # Shuffle the lists in a random order
    random.shuffle(segment_extracts)
    random.shuffle(interval_extracts)

    return segment_extracts, interval_extracts


'''
    Assumptions:
        - audio format in = audio format out
        - name csv = audio file
    Process:
        - default max_tries = 10000 
        - output name: xxxxx_label_id%4.wav 
        - default length [0.7 ~ 2.2]
'''
dict_param = {
              'num_segments' : 40,
              'min_length' : 0.7,
              'max_length' : 2.2,
              'ending_csv' : 'praat_ready',
              'speech_folder': 'segments_output_speech',
              'noises_folder': 'segments_output_noises'}


# Number of speech / non-speech segments to extract
# root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_TTS2','GT_generation_dirty')
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','Testset_Irma_noises_sampling')

audio_folder = root_dir.joinpath('input_audios')
csv_folder = root_dir.joinpath('input_csv_GT')

output_WAV_speech = root_dir.joinpath(dict_param['speech_folder'])
output_WAV_noises = root_dir.joinpath(dict_param['noises_folder'])
create_folder_if_missing(output_WAV_speech)
create_folder_if_missing(output_WAV_noises)

select_speech_segments(csv_folder, audio_folder, dict_param, 
                           root_dir)

# TO-DO: length vary from min and max