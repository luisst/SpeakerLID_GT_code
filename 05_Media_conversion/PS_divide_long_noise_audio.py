import subprocess
import sys
from pathlib import Path
from utilities_functions import check_folder_for_process, ffmpeg_split_audio, get_total_video_length, create_folder_if_missing


# load folder with long wavs
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_TTS2','Generate_noises_TTS2_crosstalk')

folder_inputs = root_dir.joinpath('input_WAVS_TTS2')
output_folders_path = root_dir.joinpath('output_WAVS')
output_folders_path.mkdir(exist_ok=True)

# iterate each long wav
long_mp3_list = sorted(list(folder_inputs.glob(f'*.wav')))

for input_file in long_mp3_list:

    output_name = input_file.stem

    # ### Create a folder per audio
    # output_dir = output_folders_path.joinpath(f'WAV_{output_name}')
    # output_dir.mkdir(exist_ok=True)

    # if not(check_folder_for_process(output_folder_wavs_pth)):
    #     sys.exit("goodbye")

    if input_file.exists():
        duration = 3  # duration of each chunk in seconds
        output_path = output_folders_path.joinpath(output_name)

        # Use FFmpeg to split the file into chunks of 8 seconds
        command = f"ffmpeg -i {input_file} -f segment -segment_time {duration} -c copy -acodec pcm_s16le -ac 1 -ar 16000 {output_path}_%03d.wav"
        subprocess.run(command, shell=True)

        print("Audio file has been trimmed successfully!")
    else:
        print("The input file does not exist!")
