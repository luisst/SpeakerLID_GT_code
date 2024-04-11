import pandas as pd
import sys
import json

from pathlib import Path
from utilities_functions import check_folder_for_process, write_2_csv




root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TestSet_for_VAD','All_results','azure')

current_input_folder = root_dir.joinpath('json_raw_v31')
output_folder_csv_pth = root_dir.joinpath('final_csv_v31')

transcript_pth_list = sorted(list(current_input_folder.glob('*.json')))

if not(check_folder_for_process(output_folder_csv_pth)):
    sys.exit("goodbye")



for current_json_pth in transcript_pth_list:
    current_output_pth = output_folder_csv_pth.joinpath(current_json_pth.stem +'.csv')
    print(current_output_pth)

    with open(current_json_pth) as json_data:
        data = json.load(json_data)

    list_start_time = []
    list_end_time = []
    list_text = []
    list_prob = []
    list_speaker = []

    all_items = data['recognizedPhrases']

    for idx, current_entry in enumerate(all_items):

        start_pd = pd.Timedelta(current_entry['offset'])
        current_start_seconds = float(start_pd.total_seconds())

        stop_pd = pd.Timedelta(current_entry['duration'])
        current_duration = float(stop_pd.total_seconds())
        current_stop_seconds = current_start_seconds + current_duration

        list_start_time.append("{:.2f}".format(current_start_seconds))
        list_end_time.append("{:.2f}".format(current_stop_seconds))
        list_text.append(current_entry['nBest'][0]['display'])
        list_prob.append(str(current_entry['nBest'][0]['confidence']))
        list_speaker.append(str(current_entry['speaker']))


    columns = ['speaker', 'start_time', 'end_time', 'prediction', 'prob']

    write_2_csv(list_speaker, list_start_time, list_end_time, list_text ,list_prob, \
            path=current_output_pth, cols = columns, txt_flag =  True, time_format=False)