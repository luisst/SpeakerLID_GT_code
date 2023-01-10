import random
import math
from pathlib import Path

from utilities_functions import get_total_video_length, ffmpeg_split_audio, check_folder_for_process


clip_length = 40
tag_output = 'RNDshort'
max_rnd_audios = 20

videos_folder_pth = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Speech_vs_BackgroundNoise','Wenjing_GT','src_videos')
# videos_folder_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID','Stg1_src','longvideos')
output_folder_random_audios = Path.home().joinpath('Dropbox', 'DATASETS_AUDIO','VAD_aolme','random_audios_extracted')

folder_videos_list = sorted(list(videos_folder_pth.glob('*.mp4')))
folder_videos_list.extend(sorted(list(videos_folder_pth.glob('*.mpeg'))))

if not check_folder_for_process(output_folder_random_audios):
    print("goodbye")

# for loop as many as needed
for idx in range(0, max_rnd_audios):

    # randomly select a video from the src folder
    random_video_pth = random.choice(folder_videos_list)

    # obtain total time of video
    total_length_seconds = get_total_video_length(random_video_pth)
    # generate random start and end
    rnd_stop_val = math.floor(total_length_seconds-clip_length)
    random_start = random.randrange(2, rnd_stop_val)	
    random_end = random_start + clip_length

    # modify the name and add index number
    output_suffix = tag_output + '-' + str(idx).zfill(3)
    output_audio_pth = output_folder_random_audios.joinpath(random_video_pth.stem + f'_{output_suffix}.wav')

    print(output_audio_pth)

    # execute clipping
    ffmpeg_split_audio(random_video_pth, output_audio_pth,
                start_time_csv = random_start,
                stop_time_csv = random_end,
                times_as_integers=True)