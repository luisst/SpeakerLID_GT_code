

from pathlib import Path
import os
import subprocess as subp

sr = 16000


#Iterate all csv files in folder
folder_pth = Path.home().joinpath('Dropbox', 'DATASETS_AUDIO','VAD_aolme','Groups_Irma_division','input_videos_irma')
audios_output_path = Path.joinpath(folder_pth,'output_audios')
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
