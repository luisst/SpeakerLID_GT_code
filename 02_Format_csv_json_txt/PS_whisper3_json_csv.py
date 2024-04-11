import pandas as pd
import sys

from pathlib import Path
from utilities_functions import check_folder_for_process, write_2_csv


root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TestSet_for_VAD','All_results','whisper3_results','whisper3')
current_input_folder = root_dir.joinpath('json_files')
output_folder_csv_pth = root_dir.joinpath('final_csv')

transcript_pth_list = sorted(list(current_input_folder.glob('*.json')))

if not(check_folder_for_process(output_folder_csv_pth)):
    sys.exit("goodbye")

list_start_time = []
list_end_time = []
list_text = []
list_prob = []
list_speaker = []
list_lang = []

for current_csv_pth in transcript_pth_list:
    current_output_pth = output_folder_csv_pth.joinpath(current_csv_pth.stem +'.csv')
    print(current_output_pth)

    data = pd.read_json(current_csv_pth)

    all_items = data['chunks']

    for idx, current_entry in enumerate(all_items):
        list_start_time.append(current_entry['timestamp'][0])
        list_end_time.append(current_entry['timestamp'][1])
        list_text.append(current_entry['text'].strip())
        list_lang.append('en')
        list_speaker.append('S0')

    columns = ['speaker', 'lang', 'start_time', 'end_time', 'text']

    write_2_csv(list_speaker, list_lang, list_start_time, list_end_time, list_text , \
            path=current_output_pth, cols = columns, txt_flag =  True, time_format=False)
