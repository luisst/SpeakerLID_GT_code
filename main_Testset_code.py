
from pathlib import Path

import clips_samples_functions as gt
from utilities_functions import check_folder_for_process, create_folder_if_missing


# Install textgrid script from:
# https://github.com/kylerbrown/textgrid
# DO NOT USE: pip install textgrid or (https://github.com/kylebgorman/textgrid)

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','TestSet')
longvideos_dir = root_dir.joinpath('00_Single_videos')

### Summary of Ground Truth - Speaker Diarization process 

# HAND: use webappV5 for diarization (stg2)
# pc 02: convert those csv -> praat + audios
# HAND: praat fine tuning
# pc 03: convert back from praat, and create the GT


pc01 , pc02, pc03 = [0,0,1]

clips_dir = root_dir.joinpath('02_Selected_clips')
# GT_output_dir = root_dir.joinpath('03_Final_samples')
current_folder = clips_dir.joinpath('G-C2L1P-Apr26-E-Krithika_q2_04-06')
current_csv_webapp_folder = current_folder.joinpath('csv_from_webapp')

current_GT_clips_output_folder = current_folder.joinpath('videos_for_GT')
current_praat_files_folder = current_folder.joinpath('praat_files')
current_final_csv_folder = current_folder.joinpath('final_csv')
current_GT_output_folder = current_folder.joinpath(current_folder.name + '_final')

#############  [pc01]  First step: For EACH 23-min video in folder -> create GT 45-seconds  ##############
if pc01:
    gt.random_select_segment(longvideos_dir, clips_dir)

# #############  [pc02] Second step: Read CSV -> Praat      ##############
if pc02:
    gt.delete_tms_from_folder(current_csv_webapp_folder, input_is_txt=False)

    gt.convert_csv_2_praat(current_csv_webapp_folder, current_praat_files_folder,
                            current_GT_clips_output_folder, praat_name = '_praat.txt')

#############  [pc03] Third step: Praat -> audio samples      ##############
if pc03:
    gt.convert_praat_2_csv(current_praat_files_folder, current_final_csv_folder, 
                        tag_from_praat = 'praat', tag_after_finished = 'ready')

    # gt.gen_audio_samples(current_GT_clips_output_folder, current_final_csv_folder,
    #                         current_GT_output_folder,
    #                         sr = 16000,
    #                         praat_extension = '_' + 'praat_ready',
    #                         tony_flag = False,
    #                         )

    gt.generate_final_csv(current_final_csv_folder,
                          current_praat_files_folder,
                          current_final_csv_folder,
                          current_folder,
                          praat_extension = '_' + 'praat_ready')