import pandas as pd
import sys
import json
import os
import shutil
import datetime
from pathlib import Path


def check_folder_for_process(this_dir):
    '''If {this_dir} exists, ask if okay to overwrite.
        Return True to start process'''
    compute_procedure = False

    this_dir = str(this_dir)

    if not os.path.isdir(this_dir):
            Path(this_dir).mkdir( parents=True, exist_ok=True )
            compute_procedure = True

    if len(os.listdir(this_dir)) != 0:
        print(f"{this_dir} isn't empty, overwrite[o] or append[a]?")
        user_response = input().lower()
        print(f'user answered: {user_response}')
        if user_response == 'o':
            shutil.rmtree(this_dir)
            os.mkdir(this_dir)
            compute_procedure = True
        elif user_response == 'a':
            print("Append content")
            compute_procedure = True
        else:
            print('Content was not modified')
    else:
        print('Folder: {} is empty. Proceed with computation.'.format(this_dir))
        compute_procedure = True

    return compute_procedure


def check_csv_exists_pathlib(csv_path):
    if csv_path.exists():
        print("CSV file already exists, do you want to overwrite? (y)")
        if input().lower() != 'y':
            print("File not modified")
            sys.exit()


def check_same_length(list1, list2):
    if len(list1) != len(list2):
        print("Error, your list1 and list2 have different lengths")
        sys.exit()


def write_2_csv(*args, **kwargs):
    """
    Function to write csv files.
    args:
        - Columns for the csv (matched to the names)
    kwargs:
        - cols: List of names for columns (matched to args)
        - path: output_path for the csv
    """
    defaultKwargs = { 'time_format': True, 'txt_flag': False }
    kwargs = { **defaultKwargs, **kwargs }

    # my_df = pd.DataFrame(index=False)
    my_df = pd.DataFrame()

    csv_path = kwargs['path']
    columns_values = kwargs['cols']

    # check if csv file exists
    check_csv_exists_pathlib(csv_path)

    if len(args) > 2:
        check_same_length(args[0], args[1])
    elif len(args) > 3:
        check_same_length(args[1], args[2])

    idx = 0
    for current_list in args:
        my_df[columns_values[idx]] = current_list
        # my_df[columns_values[idx]] = [round(value, 2) if isinstance(value, float) else value for value in current_list]
        idx = idx + 1

    today_date = '_' + str(datetime.date.today())
    datetime_object = datetime.datetime.now()
    time_f = "-{:d}_{:02d}".format(datetime_object.hour, datetime_object.minute)

    if kwargs['time_format']:
        full_output_csv_path = csv_path.with_name(csv_path.stem + today_date + time_f)
    else:
        full_output_csv_path = csv_path.with_name(csv_path.stem)

    if kwargs['txt_flag']:
        my_df.to_csv(full_output_csv_path.with_suffix('.txt'), header=False, sep='\t', index=False)
    else:
        my_df.to_csv(full_output_csv_path.with_suffix('.csv'), index=False)



root_dir = Path.home().joinpath('Dropbox') / r'DATASETS_AUDIO\interviews_wavs\little_test'

current_input_folder = root_dir.joinpath('json_raw_v3.3')
output_folder_csv_pth = root_dir.joinpath('final_csv_v3.3')

transcript_pth_list = sorted(list(current_input_folder.glob('*.json')))

if not(check_folder_for_process(output_folder_csv_pth)):
    sys.exit("goodbye")



for current_json_pth in transcript_pth_list:
    current_output_pth = output_folder_csv_pth.joinpath(current_json_pth.stem +'.csv')
    print(current_output_pth)

    with open(current_json_pth, encoding='utf-8') as json_data:
        data = json.load(json_data)

    list_start_time = []
    list_end_time = []
    list_text = []
    list_prob = []
    list_speaker = []
    list_language = []

    all_items = data['recognizedPhrases']

    for idx, current_entry in enumerate(all_items):

        start_pd = pd.Timedelta(current_entry['offset'])
        current_start_seconds = float(start_pd.total_seconds())

        stop_pd = pd.Timedelta(current_entry['duration'])
        current_duration = float(stop_pd.total_seconds())
        current_stop_seconds = current_start_seconds + current_duration

        list_start_time.append("{:.2f}".format(current_start_seconds))
        list_end_time.append("{:.2f}".format(current_stop_seconds))
        list_text.append(str(current_entry['nBest'][0]['display']))
        list_prob.append(str(current_entry['nBest'][0]['confidence']))
        list_speaker.append(str(current_entry['speaker']))
        list_language.append(str(current_entry['locale']))



    columns = ['speaker', 'start_time', 'end_time', 'prediction', 'prob', 'language']

    write_2_csv(list_speaker, list_start_time, list_end_time, list_text ,list_prob, list_language, \
            path=current_output_pth, cols = columns, txt_flag =  True, time_format=False)