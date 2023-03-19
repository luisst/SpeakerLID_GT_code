from pathlib import Path
import shutil

from utilities_functions import calculate_duration_in_folder

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Speech_vs_BackgroundNoise','Wenjing_GT','output_wav_files')

for wav_pth in root_dir.glob('*.wav'):
    old_name = wav_pth.stem
    speaker_ID = old_name.split('_')[-1]
    old_name_base = '_'.join(old_name.split('_')[:-1])

    numbering = old_name_base.split('-')[-1]
    name_first_part = '-'.join(old_name_base.split('-')[:-2])

    new_name = name_first_part + '_' + speaker_ID + '_' + numbering 

    new_wav_pth = wav_pth.with_name(f'{new_name}.wav')
    print(f'New path: {new_wav_pth}')
    shutil.move(wav_pth,new_wav_pth)
