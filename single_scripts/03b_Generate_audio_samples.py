
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 21:50:22 2022

@author: luis
"""
from pathlib import Path

from utilities_functions import check_folder_for_process, ffmpeg_split_audio
from clips_samples_functions import gen_audio_samples

if __name__=="__main__":
    # Give the audios + csv folder
    current_folder_videos = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID', 'home_TEST', 'G-C2L1P-Apr12-A-Allan_TEST')
    current_folder_csv = current_folder_videos.joinpath('final_csv')

    GT_audio_output_folder = current_folder_videos.joinpath('GT_audio_output_folder')


    gen_audio_samples(current_folder_videos,
    current_folder_csv,
    GT_audio_output_folder,
    sr = 16000,
    praat_extension = '_' + 'praat_done_ready',
    tony_flag = False,
    )