import csv
import json

import sys

from utilities_functions import check_folder_for_process
from pathlib import Path

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','Sample_dataset','GT')

current_final_csv_folder = root_dir.joinpath('final_csv')
output_folder_csv_pth = root_dir.joinpath('json_format')

transcript_pth_list = sorted(list(current_final_csv_folder.glob('*.csv')))

if not(check_folder_for_process(output_folder_csv_pth)):
    sys.exit("goodbye")

for current_csv_pth in transcript_pth_list:
    current_output_json_pth = output_folder_csv_pth.joinpath(current_csv_pth.stem +'.json')
    print(current_output_json_pth)

    # create a dictionary
    data = {}

    key = "speech_segments"
    data[key] = []
    # Open a csv reader called DictReader
    with open(current_csv_pth, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf, delimiter = '\t')
        
        # Convert each row into a dictionary
        # and add it to data
        for rows in csvReader:
            end_value = int(float(rows['EndTime'])*16000)
            start_value = int(float(rows['StartTime'])*16000)
            data[key].append({"start_time": start_value, "end_time": end_value})
            

    # Open a json writer, and use the json.dumps()
    # function to dump data
    with open(current_output_json_pth, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))
        


