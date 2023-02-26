import pandas as pd
import sys

from utilities_functions import check_folder_for_process
from pathlib import Path

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','Sample_dataset','All_results','BAS')

current_input_folder = root_dir.joinpath('raw')
output_folder_csv_pth = root_dir.joinpath('simplified')

transcript_pth_list = sorted(list(current_input_folder.glob('*.csv')))

if not(check_folder_for_process(output_folder_csv_pth)):
    sys.exit("goodbye")

for current_csv_pth in transcript_pth_list:
    current_output_json_pth = output_folder_csv_pth.joinpath(current_csv_pth.stem +'.csv')
    print(current_output_json_pth)

    new_transcr_path = output_folder_csv_pth.joinpath(current_output_json_pth)
    new_file = open(new_transcr_path, "w")

    df = pd.read_csv(current_csv_pth,index_col=False , sep=';')

    for index, row in df.iterrows():
        current_start_time = float(row['BEGIN'])
        current_duration = float(row['DURATION'])
        current_stop_time = current_start_time + current_duration
        current_speech = row['VAD'].replace('<','').replace('>','')
        start_time_seconds = current_start_time/16000
        stop_time_seconds = current_stop_time/16000

        if current_speech == 'speech':
            new_file.write(f'{current_speech}\t{start_time_seconds:.2f}\t{stop_time_seconds:.2f}\n')
    
    new_file.close()
