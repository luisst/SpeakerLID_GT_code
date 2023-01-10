# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 23:43:04 2022

@author: luis
"""
import glob
import subprocess as subp
import os
import time
import json

from pathlib import Path
from utilities_functions import check_folder_for_process, ffmpeg_split_audio
from scripts_functions import verify_video_csvNamebase, unique_entry_gen
from clips_samples_functions import create_clips

if __name__=="__main__":
    header_present = True

    # Give the audios + csv folder
    root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection')
    home_dir = root_dir.joinpath('Long_videos')
    clips_folder = root_dir.joinpath('Selected_clips')

    # One folder in -> one folder out
    current_folder = home_dir.joinpath('G-C3L1P-Mar21-A-Venkatesh_q2_02-05')
    current_clips_output_folder = clips_folder.joinpath(current_folder.name, 'clips_raw')

    create_clips(current_folder, current_clips_output_folder)