
from pathlib import Path

from utilities_functions import calculate_duration_in_folder

videos_folder_pth = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','TestSet')
# videos_folder_pth = Path.cwd()

wav_flag = True

total_time_folder = calculate_duration_in_folder(videos_folder_pth, wav_flag = False)

total_min = total_time_folder/60
total_hours = total_min/60

print(f'The total seconds in this folder is: {total_time_folder:.2f}')
print(f'In minutes: {total_min:.2f} \t In hours: {total_hours:.2f}')
