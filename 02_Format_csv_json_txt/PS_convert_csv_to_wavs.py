import os
from pathlib import Path
import subprocess

def trim_wav(input_path, output_path, start_time, end_time):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-ss', str(start_time),
        '-to', str(end_time),
        '-c', 'copy',
        output_path
    ]
    subprocess.run(command)

    
if __name__ == "__main__":
    input_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\ValAO-Windy\STG_1\STG1_SHAS\shas_filtered_output_csv")
    wav_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\ValAO-Windy\input_wavs")

    input_folder = Path(input_folder)


    for txt_file in input_folder.glob('*.txt'):

        print(f"Processing file: {txt_file.stem}")

        output_folder = input_folder.joinpath(f'{txt_file.stem}_WAVS')
        output_folder.mkdir(exist_ok=True)

        with open(txt_file, 'r') as file:
            for line in file:
                filename, start_time, end_time = line.strip().split('\t')
                start_time = round(float(start_time), 2)
                end_time = round(float(end_time), 2)

                input_path = wav_folder / f"{filename}.wav" 
                output_filename = f"{input_path.stem}_{start_time}-{end_time}.wav"
                output_path = Path(output_folder) / output_filename
                trim_wav(input_path, output_path, start_time, end_time)

                print(f'File {output_filename}')