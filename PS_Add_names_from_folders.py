from pathlib import Path
import shutil

from utilities_functions import calculate_duration_in_folder

def add_name_in_folder(folder_dir):
    for current_path in Path(folder_dir).iterdir():
        if current_path.is_file():
            print(f'This is a file skipped: {current_path.name}')

        if current_path.is_dir():
            print(f'Speaker Folder: {current_path.name}')
            speaker_ID = current_path.name

        for wav_pth in current_path.glob('*.wav'):
            old_name = wav_pth.stem
            new_wav_pth = wav_pth.with_name(f'{old_name}_{speaker_ID}.wav')
            shutil.move(wav_pth,new_wav_pth)

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Recovery_GT_recognition')

for current_path in Path(root_dir).iterdir():
    if current_path.is_file():
        print(f'This is a file skipped: {current_path.name}')

    if current_path.is_dir():
        print(f'Session Folder: {current_path}')
        add_name_in_folder(current_path)