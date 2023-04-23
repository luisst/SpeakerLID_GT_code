from pathlib import Path

import clips_samples_functions as gt
from utilities_functions import check_folder_for_process, create_folder_if_missing
# Set the path to the folder containing the audio files


voice_TTS_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','03_Final_samples','GroupsApril23')

output_TTS_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','SD_test_pairs','Groups4speakers')

gt.divide_speakers_into_folders(voice_TTS_folder, output_TTS_folder,speaker_at_end_flag = False)

