

from pathlib import Path
import os
import subprocess as subp

sr = 16000


#Iterate all csv files in folder
folder_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID', 'G-C2L1P-Apr12-A-Allan_q2_04-05')

audios_output_path = Path.joinpath(folder_pth,'output_audios_praat')
try:
    audios_output_path.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    print("Folder is already there")
else:
    print("Folder was created")

for input_video_pth in folder_pth.glob( '*.mp4' ):
    print( input_video_pth)

    # Src folder with all csv file to transform (future)

    current_audio_name = input_video_pth.stem
    current_audio_name = current_audio_name.split('.')[0] + '.wav'
    new_audio_path = Path.joinpath(audios_output_path, current_audio_name)

    cmd = f"ffmpeg -i '{input_video_pth}' -acodec pcm_s16le -ac 1 -ar {sr} '{new_audio_path}'"

    # print(cmd)
    subp.run(cmd, shell=True)
