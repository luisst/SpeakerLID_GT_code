# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 23:17:22 2022

@author: luis
"""

import sys
import os
import shutil
import subprocess as subp
import json
import time

from pathlib import Path
from utilities_functions import check_folder_for_process, get_total_video_length, ffmpeg_split_audio 

from clips_samples_functions import process_raw_long_clips


if __name__=="__main__":
    root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection')
    home_clips_folder = root_dir.joinpath('Selected_clips')


    # One folder in -> one folder out
    current_folder = home_clips_folder.joinpath('G-C3L1P-Mar21-A-Venkatesh_q2_02-05', 'clips_raw')
    current_GT_clips_output_folder = current_folder.parent.joinpath('videos_for_GT')

    process_raw_long_clips(current_folder, current_GT_clips_output_folder)