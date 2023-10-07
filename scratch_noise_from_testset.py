import random
import subprocess
from pathlib import Path
import pandas as pd
import re
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
            return True
    return False

def extract_segment(audio_file, start_time, end_time, output_file):
    # Use ffmpeg to extract segment from audio
    command = [
        'ffmpeg', '-i', str(audio_file), '-ss', str(start_time), '-to', str(end_time),
        '-c', 'copy', '-y', str(output_file)
    ]
    subprocess.run(command, capture_output=True)


def select_non_speech_segments(csv_directory, audio_directory, num_segments, output_directory):
    output_directory = Path(output_directory)
    output_directory.mkdir(exist_ok=True)

    # Iterate over CSV files in the directory
    for csv_file in csv_directory.glob('*_praat_ready.csv'):
        # Get corresponding audio file
        audio_name = csv_file.stem.replace('_praat_ready', '')
        audio_file = audio_directory / f'{audio_name}.wav'

        # Select non-speech segments for each CSV file
        select_non_speech_segments_single(csv_file, audio_file, num_segments, output_directory)

    print('Non-speech segments extraction complete.')

def select_non_speech_segments_single(csv_file, audio_file, num_segments, output_directory):
    # Create output directory for the current file
    file_output_dir = output_directory / csv_file.stem
    file_output_dir.mkdir(exist_ok=True)

    # Load speech segments from CSV file using pandas
    df = pd.read_csv(csv_file, header=None,  sep='\t', index_col=False)

    # Get the first value from the first column
    first_value = df.iloc[0, 0]

    # Check if the first value matches the format 'SXEng' or 'SXSpa'
    if re.match(r'^S\d[0-9]((Eng)\|(Spa))$', first_value):
        #print("Src and Lang together. 3 columns")
        df.columns = ['SrcLang', 'StartTime', 'EndTime']
    else:
        #print("Src and Lang separated. 4 columns")
        df.columns = ['Src', 'Lang', 'StartTime', 'EndTime']

    # Check if the dataframe has no header

    # Convert start time and end time columns to float
    df['StartTime'] = df['StartTime'].astype(float)
    df['EndTime'] = df['EndTime'].astype(float)

    # Convert speech segments to list of tuples
    speech_segments = [(row['StartTime'], row['EndTime']) for _, row in df.iterrows()]

    # Get audio duration
    audio_duration = get_audio_duration(audio_file)

    # Generate non-speech segments
    non_speech_segments = []
    for i in range(num_segments):
        while True:
            noise_duration = random.uniform(0.7, 2.2)
            start_time = random.uniform(0, audio_duration)
            end_time = start_time + float(noise_duration)  # Non-speech segment duration of 1 second
            if not is_overlapping(speech_segments, start_time, end_time):
                non_speech_segments.append((start_time, end_time))
                break

    # Extract non-speech segments as WAV files
    for i, segment in enumerate(non_speech_segments):
        output_file = file_output_dir / f'non_speech_{i+1}.wav'
        extract_segment(audio_file, segment[0], segment[1], output_file)

    print(f'{num_segments} non-speech segments extracted from {csv_file.name}.')


def move_wav_files(root_folder):

    idx = 0
    # Iterate through subfolders and move WAV files to the current directory
    for file_path in root_folder.glob('**/*.wav'):
        index_str = str(idx).zfill(4)
        new_file_path = root_folder.joinpath(f'group_background_noises_{index_str}.wav')
        # file_path.rename(new_file_path)
        shutil.copy(file_path, new_file_path)
        idx = idx + 1


def delete_empty_subfolders(root_folder):
    root_folder = Path(root_folder)

    # Iterate through subfolders recursively
    for folder in root_folder.glob('**/*'):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
            print(f'Deleted empty subfolder: {folder}')


def iterate_subfolders(root_folder, num_segments):

    # Iterate through subfolders
    for subfolder in root_folder.iterdir():
        if subfolder.is_dir():
            current_folder = subfolder 
            if current_folder.name.startswith('G-C') and len(current_folder.name) > 10:
                final_csv_folder = current_folder.joinpath('final_csv')

                if final_csv_folder.exists() and final_csv_folder.is_dir():
                    print(f'Found final_csv in {final_csv_folder.name}')

                    audio_directory = current_folder.joinpath('praat_files')
                    csv_directory = current_folder.joinpath('final_csv')

                    output_directory = current_folder.joinpath('noise_extracts')
                    create_folder_if_missing(output_directory)

                    select_non_speech_segments(csv_directory, audio_directory, num_segments, output_directory)

                    move_wav_files(output_directory)
                else:
                    print(f'Not found final_csv in {current_folder.name}')



root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','TestSet','02_Selected_clips')

num_segments = 20  # Number of non-speech segments to extract
iterate_subfolders(root_dir, num_segments)
