import pandas as pd
import textgrid
import sys

from pathlib import Path


textgrid_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','02_Selected_clips','G-C2L1P-Apr12-A-Allan_q2_04-05','praat_files','G-C2L1P-Apr12-A-Allan_q2_04-05_003_praat_done.txt')
tgrid = textgrid.read_textgrid(str(textgrid_dir))
output_csv_pth = textgrid_dir.with_name('output_sratch.csv')
new_file = open(output_csv_pth, "w")

for current_entry in tgrid:
    speaker_lang = current_entry.name
    strt_time = current_entry.start
    end_time =  current_entry.stop
    speaker_ID = current_entry.tier 

    if speaker_ID not in ['S0', 'S1', 'S2', 'S3', 'S4']:
        sys.error(f'Tier name is wrong: {speaker_ID}')
    
    if speaker_lang != '':
        new_line = f'{speaker_ID}{speaker_lang}\t{strt_time:.2f}\t{end_time:.2f}\n'
        new_file.write(new_line)

new_file.close()