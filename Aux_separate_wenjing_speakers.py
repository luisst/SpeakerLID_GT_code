
from pathlib import Path
import clips_samples_functions as gt

from utilities_functions import create_folder_if_missing

interviews_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','03_Final_samples','groups_feb2023')

output_root_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','03_Final_samples')
output_interview_folder = output_root_folder.joinpath('Groups_Feb23')

# create directories if doesn't exist
create_folder_if_missing(output_interview_folder)


gt.divide_speakers_into_folders(interviews_folder, output_interview_folder, speaker_at_end_flag = False)