import subprocess
import sys
from pathlib import Path
from utilities_functions import check_folder_for_process, ffmpeg_split_audio, get_total_video_length, create_folder_if_missing


# load folder with long wavs
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Speech_vs_BackgroundNoise','GT_generation')

folder_inputs = root_dir.joinpath('input_videos_irma')
output_folders_path = root_dir.joinpath('output_WAVS')

folder_videos_list = sorted(list(folder_inputs.glob('*.mp4')))
folder_videos_list.extend(sorted(list(folder_inputs.glob('*.mpeg'))))

for input_file in folder_videos_list:

    output_name = input_file.stem

    # if not(check_folder_for_process(output_folder_wavs_pth)):
    #     sys.exit("goodbye")

    if input_file.exists():
        duration = 1  # duration of each chunk in seconds
        current_output_path = output_folders_path.joinpath(output_name)

        # command = f"ffmpeg -i {input_file} -f segment -segment_time {duration} -c copy -acodec pcm_s16le -ac 1 -ar 16000 {current_output_path}_029.wav"
        command = f"ffmpeg -i {input_file} -f segment -segment_time {duration} -c copy -acodec pcm_s16le -ac 1 -ar 16000 {current_output_path}_%03d.wav"

        subprocess.run(command, shell=True)

        print("Audio file has been trimmed successfully!")
    else:
        print("The input file does not exist!")
