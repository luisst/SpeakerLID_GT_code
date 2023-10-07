import random
import math
from pathlib import Path

from utilities_functions import get_total_video_length, ffmpeg_split_audio, check_folder_for_process

def eval_for_overlap(all_list, start_candidate, end_candidate):
    for curr_start, curr_end in all_list:
        late_start = max(curr_start, start_candidate)
        early_end = min(curr_end, end_candidate)
        if early_end - late_start > 0: # Overlap of any kind 
            return True
    return False



clip_length = 4
tag_output = 'SampleLarge'
max_rnd_audios = 1900 

videos_folder_pth = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Speech_vs_BackgroundNoise','Wenjing_GT','src_videos')
# videos_folder_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID','Stg1_src','longvideos')
output_folder_random_audios = Path.home().joinpath('Dropbox', 'DATASETS_AUDIO','VAD_aolme','sample_large')

folder_videos_list = sorted(list(videos_folder_pth.glob('*.mp4')))
folder_videos_list.extend(sorted(list(videos_folder_pth.glob('*.mpeg'))))

if not check_folder_for_process(output_folder_random_audios):
    print("goodbye")

all_extr_dict = {} 
idx = 0

while True:
    # randomly select a video from the src folder
    random_video_pth = random.choice(folder_videos_list)
    rnd_name = random_video_pth.name

    # obtain total time of video
    total_length_seconds = get_total_video_length(random_video_pth)
    # generate random start and end
    rnd_stop_val = math.floor(total_length_seconds-clip_length)
    random_start = random.randrange(2, rnd_stop_val)	
    random_end = random_start + clip_length

    # Add to dict using videoname as key
    if rnd_name not in all_extr_dict:
        all_extr_dict[rnd_name] = []
    else:
        # Evaluate for even slight overlap
        if eval_for_overlap(all_extr_dict[rnd_name], random_start, random_end):
            print(f'\tOverlap found at {rnd_name}: {random_start} - {random_end}')
            continue

    # Add to collection

    print(f'New {rnd_name}: {random_start} - {random_end}')
    all_extr_dict[rnd_name].append((random_start, random_end))

    # modify the name and add index number
    output_suffix = tag_output + '-' + str(idx).zfill(3)
    output_audio_pth = output_folder_random_audios.joinpath(random_video_pth.stem + f'_{output_suffix}.wav')

    print(output_audio_pth)

    # execute clipping
    ffmpeg_split_audio(random_video_pth, output_audio_pth,
                start_time_csv = random_start,
                stop_time_csv = random_end,
                times_as_integers=True)

    idx = idx + 1
    if idx == max_rnd_audios:
        break