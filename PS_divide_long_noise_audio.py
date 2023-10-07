import subprocess
import sys
from pathlib import Path
from utilities_functions import check_folder_for_process, ffmpeg_split_audio, get_total_video_length, create_folder_if_missing


# load folder with long wavs
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','WAV_TTS','Sound_effects')

folder_inputs = root_dir.joinpath('input_long_mp3s')
output_folders_path = root_dir.joinpath('output_WAVS')

# iterate each long wav
long_mp3_list = sorted(list(folder_inputs.glob(f'*.mp3')))

for input_file in long_mp3_list:

    output_name = input_file.stem

    output_dir = output_folders_path.joinpath(f'WAV_{output_name}')
    output_dir.mkdir(exist_ok=True)

    # if not(check_folder_for_process(output_folder_wavs_pth)):
    #     sys.exit("goodbye")

    if input_file.exists():
        duration = 4  # duration of each chunk in seconds

        # Use FFmpeg to split the file into chunks of 8 seconds
        command = f"ffmpeg -i {input_file} -f segment -segment_time {duration} -c copy -acodec pcm_s16le -ac 1 -ar 16000 {output_dir}/{output_name}_%03d.wav"
        subprocess.run(command, shell=True)

        print("Audio file has been trimmed successfully!")
    else:
        print("The input file does not exist!")
