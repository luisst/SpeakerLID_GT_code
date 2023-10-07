# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility
import sys
import re
from pathlib import Path
import subprocess as subp
import json

from utilities_functions import get_total_video_length, ffmpeg_split_audio, check_folder_for_process
from clips_samples_functions import convert_csv_2_praat

# ------------      Convert from CSV --> praat -------------------
# IMPORTANT: csv should have the same name as videos

if __name__=="__main__":
    folder_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID', 'home_TEST', 'G-C2L1P-Apr12-A-Allan_TEST')
    input_csvs_pth = folder_pth.joinpath('webapp')
    output_praat_pth = folder_pth.joinpath('praat_files') 


    convert_csv_2_praat(input_csvs_pth, output_praat_pth, praat_name = '_praat.txt')