import pandas as pd
from pathlib import Path
 

excel_base_pth = Path.home().joinpath('Dropbox', 'DATASETS_AUDIO', 'Speech_vs_BackgroundNoise', 'Wenjing_GT')
excel_pth = excel_base_pth.joinpath('wenjing_excel_all.xlsx')
csv_folder_pth = excel_base_pth.joinpath('output_csv')

# read by default 1st sheet of an excel file
df = pd.read_excel(excel_pth)

current_video_name = 'Null'

new_transcr_path = csv_folder_pth.joinpath(f'{current_video_name}.txt')
new_file = open(new_transcr_path, "w")

for index, row in df.iterrows():
    current_start_time = str(row['start time'])
    current_end_time = str(row['end time'])
    current_speaker = str(row['speaker'])
    current_speaker = current_speaker.split()[0]

    if str(row['video name']) != 'nan':
        # if current_video_name != 'Null' or current_video_name != 'NaN':
        if current_video_name != 'Null':
            new_file.close()
        current_video_name = str(row['video name'])
        current_video_name = current_video_name.split('.')[0]
        new_transcr_path = csv_folder_pth.joinpath(f'{current_video_name}.txt')
        new_file = open(new_transcr_path, "w")
    else:
        new_file.write(f'{current_video_name}\t{current_start_time}\t{current_end_time}\t{current_speaker}\n')     


new_file.close()
