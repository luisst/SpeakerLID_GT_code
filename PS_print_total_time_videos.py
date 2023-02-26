
from pathlib import Path

from utilities_functions import get_total_video_length, ffmpeg_split_audio, check_folder_for_process

videos_folder_pth = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Speech_vs_BackgroundNoise','Wenjing_GT','src_videos')

folder_videos_list = sorted(list(videos_folder_pth.glob('*.mp4')))
folder_videos_list.extend(sorted(list(videos_folder_pth.glob('*.mpeg'))))

total_time_folder = 0

for current_video_pth in folder_videos_list:
    # obtain total time of video
    current_length_seconds = get_total_video_length(current_video_pth)
    print(f'\tNow video: {current_video_pth.name}')

    total_time_folder = total_time_folder + current_length_seconds

print(f'The total seconds in this folder is: {total_time_folder}')
