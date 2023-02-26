import pandas as pd
import sys

from pathlib import Path
from utilities_functions import check_folder_for_process, write_2_csv


root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','Sample_dataset','All_results','whisper')

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

    all_items = data['segments']
    lang_all = data['language']

    for idx, current_entry in enumerate(all_items):
        list_start_time.append(current_entry['start'])
        list_end_time.append(current_entry['end'])
        list_text.append(current_entry['text'].strip())
        list_prob.append(current_entry['no_speech_prob'])
        list_speaker.append('Speech')
        list_lang.append(lang_all[idx])

    columns = ['speaker', 'lang', 'start_time', 'end_time', 'prediction', 'prob']

    write_2_csv(list_speaker, list_lang, list_start_time, list_end_time, list_text ,list_prob, \
            path=current_output_pth, cols = columns, txt_flag =  True, time_format=False)
