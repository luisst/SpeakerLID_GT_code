import random
import subprocess
from pathlib import Path
import pandas as pd
import re
import sys
import shutil

from utilities_functions import create_folder_if_missing

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

def is_overlapping(segments, start_time, end_time):
    for segment in segments:
        if start_time < segment[1] and end_time > segment[0]:
            return True, segment
    return False, (0,0,'') 


def noise_overlapping(start_time, end_time, audio_segments, total_time):
    if start_time < 0:
        print(f'ERROR, start_time is negative')
        return False

    if end_time < 0:
        print(f'ERROR, end_time is negative')
        return False
    
    if end_time > total_time:
        print(f'ERROR, end_time is larger than the duration of the audio')
        return False

    if start_time > total_time:
        print(f'ERROR, start_time is larger than the duration of the audio')
        return False

    # Sort the audio segments by start time
    audio_segments.sort(key=lambda x: x[0])

    audio_segments.insert(0, (-1, 0, 'SX'))
    max_possible_audio_length = 1*60*60*24 #1 day in seconds
    audio_segments.append((total_time, max_possible_audio_length, 'SX'))

    # Check if the user-defined segment falls between defined segments
    for i in range(1, len(audio_segments)):
        if start_time > audio_segments[i-1][1] and end_time < audio_segments[i][0]:
            print(f'\n\nFound noise space \tstart: {start_time:.2f} | end: {end_time:.2f}\nFirst: {audio_segments[i-1]}\nSecond: {audio_segments[i]}')
            return True

    # If none of the conditions were met, the segment is not undefined
    return False


def extract_segment(audio_file, start_time, end_time, output_file):
    # Use ffmpeg to extract segment from audio
    command = [
        'ffmpeg', '-i', str(audio_file), '-ss', str(start_time), '-to', str(end_time),
        '-c', 'copy', '-y', str(output_file)
    ]
    subprocess.run(command, capture_output=True)


def select_speech_segments(csv_directory, audio_directory, dict_param,
                               output_directory):
    # Iterate over CSV files in the directory
    ending_csv = dict_param['ending_csv']

    if ending_csv == '':
        pattern_to_search = '*.csv'
    else:
        pattern_to_search = f'*_{ending_csv}.csv'

    for csv_file in csv_directory.glob(pattern_to_search):
        # Get corresponding audio file
        audio_name = csv_file.stem
        audio_file = audio_directory / f'{audio_name}.wav'

        # Select speech/noise segments for each CSV file
        select_speech_segments_single(csv_file, audio_file, dict_param, output_directory)


def select_speech_segments_single(csv_file, audio_file, dict_param, 
                                  output_directory, verbose = False):

    num_segments = dict_param['num_segments']
    max_trial = dict_param['max_trial']
    min_length = dict_param['min_length'] 
    max_length = dict_param['max_length']
    speech_flag = dict_param['speech_flag']

    # Load speech segments from CSV file using pandas
    df = pd.read_csv(csv_file, header=None,  sep='\t', index_col=False)

    # Get the first value from the first column
    first_value = df.iloc[0, 0]

    # Check if the first value matches the format 'SXEng' or 'SXSpa'
    if re.match(r'^S\d[0-9]((Eng)\|(Spa))$', str(first_value)):
        #print("Src and Lang together. 3 columns")
        df.columns = ['SrcLang', 'StartTime', 'EndTime']
        # Convert start time and end time columns to float
        df['StartTime'] = df['StartTime'].astype(float)
        df['EndTime'] = df['EndTime'].astype(float)
        # Convert speech segments to list of tuples
        speech_segments = [(row['StartTime'], row['EndTime'], row['SrcLang']) for _, row in df.iterrows()]
    else:
        #print("Src and Lang separated. 4 columns")
        df.columns = ['Src', 'Lang', 'StartTime', 'EndTime']
        # Convert start time and end time columns to float
        df['StartTime'] = df['StartTime'].astype(float)
        df['EndTime'] = df['EndTime'].astype(float)
        # Convert speech segments to list of tuples
        speech_segments = [(row['StartTime'], row['EndTime'], row['Src']) for _, row in df.iterrows()]
    

    # Get audio duration
    audio_duration = get_audio_duration(audio_file)

    max_index = 0
    # Generate non-speech segments
    found_segments = []
    for i in range(num_segments):
        while True:
            if max_index >= max_trial:
                sys.exit(f'Maximum trial reached: {max_trial}')

            segment_duration = random.uniform(min_length, max_length)
            if verbose:
                print(f'segment duration: {segment_duration}')
            start_time = random.uniform(0, audio_duration)
            end_time = start_time + float(segment_duration)  # Non-speech segment duration of 1 second

            if speech_flag: 
                found_flag, segment_match = is_overlapping(speech_segments, start_time, end_time)
                current_label=segment_match[2] 
            else:
                found_flag = noise_overlapping(start_time, end_time, speech_segments, audio_duration)
                current_label = 'noises'

            max_index = max_index + 1

            if found_flag:
                found_segments.append((start_time, end_time, current_label ))
                if verbose:
                    print(f'Match {start_time}-{end_time} in \t {current_label}')
                break

    # Extract speech/noise segments as WAV files
    for i, segment in enumerate(found_segments):
        output_file = output_directory / f'{audio_file.stem}_{segment[2]}_{i:04d}.wav'
        if verbose:
            print(f'to extract: {segment}\n')
        extract_segment(audio_file, segment[0], segment[1], output_file)

    print(f'{num_segments} speech/noise segments extracted from {csv_file.name}.')



'''
    Assumptions:
        - audio format in = audio format out
        - name csv = audio file
    Process:
        - default max_tries = 10000 
        - output name: xxxxx_label_id%4.wav 
        - default length [0.7 ~ 2.2]
'''
dict_param = {'speech_flag' : False,
              'num_segments' : 10,
              'min_length' : 0.7,
              'max_length' : 2.2,
              'ending_csv' : '',
              'max_trial' : 10000}

  # Number of speech / non-speech segments to extract
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_TTS2','GT_generation_dirty')

audio_folder = root_dir.joinpath('input_audios')
csv_folder = root_dir.joinpath('input_csv_GT')

output_WAV_folder = root_dir.joinpath('segments_outputs')
create_folder_if_missing(output_WAV_folder)

select_speech_segments(csv_folder, audio_folder, dict_param, 
                           output_WAV_folder)
