import sys
from pathlib import Path
import shutil
from mycolorpy import colorlist as mcp

import clips_samples_functions as gt
from utilities_functions import calculate_duration_in_folder, check_folder_for_process

'''
Apply to a speaker folder tree -> Generate another speaker tree
'''
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','SD_test_pairs','Interview_Groups_All','test','mytest')
new_root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','SD_test_pairs','Interview_Groups_Filtered')

my_th_seconds = 0.6

if not(check_folder_for_process(new_root_dir)):
    sys.exit('goodbye')

# Extract Number of audios, Total duration, and Duration of each audio
for current_path in Path(root_dir).iterdir():
    if current_path.is_file():
        print(f'This is a file skipped: {current_path.name}')

    if current_path.is_dir():
        print(current_path)
        speaker_ID = current_path.name

        if not(new_root_dir.joinpath(speaker_ID).exists()):
            new_root_dir.joinpath(speaker_ID).mkdir()

        gt.process_raw_long_clips(current_path, new_root_dir.joinpath(speaker_ID), 
                seg_length = 2.4,
                acceptable_length = 3,
                min_length = 0.6,
                flag_standard_names=True,
                audio_flag = True)

        # # Go inside the folder and grab time
        # list_names, list_lengths, total_time_folder = calculate_duration_in_folder(current_path,
        #                                                                 wav_flag = True,
        #                                                                 return_list = True,
        #                                                             return_names = True)

        # for current_name, current_length in list(zip(list_names, list_lengths)):
        #     if current_length > my_th_seconds:
        #         new_pth = new_root_dir.joinpath(speaker_ID, current_name)

        #         print(f'File {current_name} to copy')
        #         shutil.copy(current_path.joinpath(current_name), new_pth)
