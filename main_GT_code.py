
from pathlib import Path

import clips_samples_functions as gt
from utilities_functions import check_folder_for_process, create_folder_if_missing


root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection')
longvideos_dir = root_dir.joinpath('01_Long_videos')

### Summary of Ground Truth - Speaker Diarization process 
# HAND: manually select clips (stg1)
# pc 01: convert to miniclips 
# HAND: use webappV5 for diarization (stg2)
# pc 02: convert those csv -> praat + audios
# HAND: praat fine tuning
# pc 03: convert back from praat, and create the GT

# I start in long videos folder!

pc01 , pc02, pc03 = [0,0,1]

# One folder in -> one folder out
current_folder = longvideos_dir.joinpath('G-C2L1P-Feb16-B-Shelby_q2_03-05')

clips_dir = root_dir.joinpath('02_Selected_clips')

create_folder_if_missing(clips_dir.joinpath(current_folder.name))
print(f'New path: {clips_dir.joinpath(current_folder.name)}')

GT_output_dir = root_dir.joinpath('03_Final_samples')
current_clips_output_folder = clips_dir.joinpath(current_folder.name, 'clips_raw')
current_GT_clips_output_folder = clips_dir.joinpath(current_folder.name, 'videos_for_GT')
current_csv_webapp_folder = clips_dir.joinpath(current_folder.name, 'csv_from_webapp')
current_praat_files_folder = clips_dir.joinpath(current_folder.name, 'praat_files')
current_final_csv_folder = clips_dir.joinpath(current_folder.name, 'final_csv')
current_GT_output_folder = GT_output_dir.joinpath(current_folder.name)

# create directories if doesn't exist
create_folder_if_missing(current_csv_webapp_folder)

#############  [pc01]  First step: Divide into selections + webapp      ##############
if pc01:
    gt.create_clips(current_folder, current_clips_output_folder,timestamp_flag=False)
    gt.process_raw_long_clips(current_clips_output_folder, current_GT_clips_output_folder)

#############  [pc02] Second step: Read CSV -> Praat      ##############
if pc02:
    gt.delete_tms_from_folder(current_csv_webapp_folder)
    gt.convert_csv_2_praat(current_csv_webapp_folder, current_praat_files_folder,
                            current_GT_clips_output_folder, praat_name = '_praat.txt')

#############  [pc03] Third step: Praat -> audio samples      ##############
if pc03:
    gt.convert_praat_2_csv(current_praat_files_folder, current_final_csv_folder, 
                        tag_from_praat = 'praat', tag_after_finished = 'ready')

    gt.gen_audio_samples(current_GT_clips_output_folder, current_final_csv_folder,
                            current_GT_output_folder,
                            sr = 16000,
                            praat_extension = '_' + 'praat_ready',
                            tony_flag = False,
                            )