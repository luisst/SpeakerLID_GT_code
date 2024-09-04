from pathlib import Path
import argparse
import os
from utilities_functions import create_folder_if_missing, \
    ffmpeg_split_audio

def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")

base_path_ex = Path.home().joinpath('Dropbox','DATASETS_AUDIO','TestAO-Liz')
audio_folder_ex = base_path_ex.joinpath('Testset_stage1','input_wavs')
csv_folder_ex = base_path_ex.joinpath('Testset_stage1','input_csv')
chunks_WAV_ex = base_path_ex.joinpath('Testset_stage2','wav_chunks')
seg_ln_ex = '1.0'
step_size_ex = '0.2'

parser = argparse.ArgumentParser()
parser.add_argument('--stg1_wavs', type=valid_path, default=audio_folder_ex, help='Stg1 WAVs folder path')
parser.add_argument('--stg1_final_csv', type=valid_path, default=csv_folder_ex, help='Stg1 VAD csvs folder path')
parser.add_argument('--stg2_chunks_wavs', type=valid_path, default=chunks_WAV_ex, help='Stg2 chunks wavs folder path')
parser.add_argument('--ln', type=float, default=seg_ln_ex, help='Stg2 chunks length ihn seconds')
parser.add_argument('--st', type=float, default=step_size_ex, help='Stg2 chunks step_size in seconds')
parser.add_argument('--azure_flag', type=bool, default=False, help='Flag to indicate csv line columns')

args = parser.parse_args()

audio_folder = args.stg1_wavs 
csv_folder = args.stg1_final_csv
chunks_wav_folder = args.stg2_chunks_wavs
azure_flag = args.azure_flag

chunk_duration = float(args.ln)
minimum_chunk_duration = chunk_duration - 0.1 # seconds
step_length = float(args.st) 
verbose = True



# Iterate through each of the csv files
for csv_file in csv_folder.glob('*.txt'):
    # Get the filename without extension
    csv_filename = csv_file.stem

    print(f'Processing {csv_filename}...')
    
    # Find the matching audio file in the audio folder
    audio_file = audio_folder.joinpath(csv_filename + '.wav')

    #Verify that the audio file exists
    if not audio_file.exists():
        print(f'WARNING: {audio_file} does not exist. Skipping...')
        continue

    idx_total = 0
    # Iterate each line in the csv file
    for line in csv_file.open():

        # # Get the start and stop times
        if azure_flag:
            pred_label, start_time, stop_time, text_pred, prob_pred = line.split('\t')
        else:
            filename, start_time, stop_time = line.split('\t')


        start_time = float(start_time)
        stop_time = float(stop_time)

        # Verify that the chunk duration is at least the minimum chunk duration
        if stop_time - start_time < minimum_chunk_duration:
            continue

        # Iterate through the audio file
        current_time = start_time
        while current_time < stop_time:

            # Compute the stop time
            current_stop_time = min(current_time + chunk_duration, stop_time)
            if current_time + chunk_duration > stop_time:
                if verbose:
                    print(f'\tUsed end of audio: {current_time + chunk_duration:.2f} > {stop_time:.2f}')
                current_stop_time = stop_time
            else:
                current_stop_time = current_time + chunk_duration

            # Verify that the chunk duration is at least the minimum chunk duration
            if current_stop_time - current_time < minimum_chunk_duration:
                if verbose:
                    print(f'\tBREAK\t Last iteration: {current_stop_time - current_time:.2f} < {minimum_chunk_duration:.2f}\n')
                break

            # Create the output file name
            output_filename = f'{csv_filename}_{current_time:.2f}_{current_stop_time:.2f}.wav'
            output_file = chunks_wav_folder.joinpath(output_filename)

            if verbose:
                print(f'{output_filename} - New chunk: {current_time:.2f} - {current_stop_time:.2f}')

            # Split the audio file
            _, _ = ffmpeg_split_audio(audio_file, output_file, \
                start_time_csv = str(current_time),
                stop_time_csv = str(current_stop_time),
                sr = 16000,
                verbose = False,
                formatted = False,
                output_video_flag = False,
                times_as_integers = False)

            # Update the current time
            current_time += step_length


    

