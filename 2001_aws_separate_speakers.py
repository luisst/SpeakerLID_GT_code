import sys
from pathlib import Path

folder_pth = Path.home().joinpath('Dropbox', '04_Audio_Perfomance_Evaluation','AWS_speech_recognition')

name_of_aws_results = 'ftDiarization01_aws_2022-12-18-23_05.txt'

transcript_pth = folder_pth.joinpath(name_of_aws_results)

f = open(transcript_pth, 'r')
lines = f.readlines()
f.close()

# Separate each speaker , copy line and save it in results in another folder!
files_dict = {}
for line in lines:
    filename = line.split('\t')[0]

    if filename not in files_dict:
        files_dict[filename] = [line]
    else:
        files_dict[filename].append(line)

for current_filename in files_dict:
    current_data_lines = files_dict[current_filename]
    new_transcript_name_base = '{}_awspred.txt'.format(current_filename.split('.')[0])
    new_transcript_pth = folder_pth.joinpath(new_transcript_name_base)
    print(f'\n\nNow processing {new_transcript_name_base}')

    new_file = open(new_transcript_pth, "w")
    for line in current_data_lines:
        new_file.write(line)
    new_file.close()