from pathlib import Path

import clips_samples_functions as gt
from utilities_functions import check_folder_for_process, create_folder_if_missing

interviews_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','01_Long_videos','Interviews','wav_output')

### Summary of Ground Truth - Speaker Diarization process 
# HAND: praat fine tuning
# pc 03: convert back from praat, and create the GT

output_root_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','03_Final_samples')
output_interview_folder = output_root_folder.joinpath('Interviews_output')

# create directories if doesn't exist
create_folder_if_missing(output_interview_folder)

# gt.convert_praat_interviews_csv(interviews_folder, interviews_folder)

# # Interview version of gen_audio_samples
# #   Important to find the matching audios with the CSV file
# gt.gen_audio_samples(interviews_folder, interviews_folder,
#                         output_interview_folder,
#                         sr = 16000,
#                         praat_extension = '',
#                         audio_flag = True,
#                         interviews_flag = True,
#                         )

gt.divide_speakers_into_folders(output_interview_folder, output_interview_folder)