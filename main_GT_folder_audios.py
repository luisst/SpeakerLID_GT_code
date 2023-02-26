# Input: single folder with audios already trimmed that don't require further processing
# Processing: Use praat and stg2, good time to automatically copy the name into the html
# Output: csv file for each audio

from pathlib import Path

import clips_samples_functions as gt
from utilities_functions import check_folder_for_process, create_folder_if_missing

diarization_flag = False

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','Sample_dataset','GT')

current_praat_files_folder = root_dir.joinpath('praat_files')
current_final_csv_folder = root_dir.joinpath('final_csv')
current_GT_output_folder = root_dir.joinpath('diarization_output_wavs')

#############  [pc03] Third step: Praat -> audio samples      ##############
gt.convert_praat_2_csv(current_praat_files_folder, current_final_csv_folder, 
                    tag_from_praat = 'done', tag_after_finished = 'ready')

if diarization_flag:
    gt.gen_audio_samples(root_dir.parent, current_final_csv_folder,
                            current_GT_output_folder,
                            sr = 16000,
                            praat_extension = '_' + 'praat_done_ready',
                            tony_flag = True,
                            )