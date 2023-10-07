from pathlib import Path
import re

regex = r"duration: (\d+?.\d+?), offset: (\d+?.\d+?), rW: \d.?\d*?, speaker_id: (\w+?), uW: \d.?\d*?, wav: (.*?)}"

yml_pth = Path.home().joinpath('Dropbox', 'SpeechSpring2023','shas','results_ymal','minitest_TTS')
output_csv_folder= Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TTS_minitest','inference')
#open text file in read mode
text_file = open(yml_pth, "r")
 
#read whole file to a string
data = text_file.read()
 
#close file
text_file.close()
 
print(data)

matches = re.finditer(regex, data)


prev_name = '' 
first_time_flag = True
for matchNum, match in enumerate(matches, start=1):
    # print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

    new_filename = match.group(4).split('.')[0]

    if new_filename != prev_name:
        if not(first_time_flag):
            new_file.close()
        new_transcr_path = output_csv_folder.joinpath(f'{new_filename}.txt')
        new_file = open(new_transcr_path, "w")
        first_time_flag = False


    stop_val = float(match.group(2)) + float(match.group(1))
    new_file.write(f'{match.group(4)}\t{match.group(2)}\t{stop_val}\n')

    prev_name = new_filename

new_file.close()