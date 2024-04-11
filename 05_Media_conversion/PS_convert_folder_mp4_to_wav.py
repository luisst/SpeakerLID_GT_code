import sys
import re
import shutil
from pathlib import Path

from utilities_functions import check_folder_for_process, ffmpeg_split_audio


# current_folder = Path.home().joinpath('Dropbox', 'DATASETS_AUDIO','VAD_aolme','TestSet_for_VAD','WAV_FILES')
current_folder = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\TestSet\02_Selected_clips\G-C2L1P-Apr26-E-Krithika_q2_03-06\tmp_video_input')
output_wav_folder = current_folder.joinpath('wav_output')

if not(check_folder_for_process(output_wav_folder)):
    sys.exit('goodbye')

for mp4_pth in current_folder.glob( '*.mp4' ):
    print(f'\n This is the wav: {mp4_pth.name}\n---------------------\n')

    # Generate audio mono 16K audio from video
    current_audio_name = mp4_pth.stem
    current_audio_name = current_audio_name.split('.')[0] + '.wav'
    new_audio_path = Path.joinpath(output_wav_folder, current_audio_name)

    _, _ = ffmpeg_split_audio(mp4_pth, new_audio_path)