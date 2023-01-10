import sys
import os
import glob
import re

from pathlib import Path
from clips_samples_functions import delete_tms_from_folder

if __name__=="__main__":
   test_script_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','Long_videos','G-C3L1P-Mar21-A-Venkatesh_q2_02-05')
   delete_tms_from_folder(test_script_folder)