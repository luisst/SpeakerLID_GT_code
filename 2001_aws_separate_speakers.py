import sys
from pathlib import Path

from utilities_functions import check_folder_for_process

folder_pth = Path.home().joinpath('Dropbox','DATASETS_AUDIO', 'Conversation_SpeakerDiarization','SDpart1','All_results', 'aws')
name_of_aws_results = 'aws_audios_dec22_aws_2022-12-24-15_04.txt'

transcript_pth = folder_pth.joinpath(name_of_aws_results)

output_folder_pth = folder_pth.joinpath('final_csv')

if not(check_folder_for_process(output_folder_pth)):
    sys.exit("goodbye")

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
    new_transcript_pth = output_folder_pth.joinpath(new_transcript_name_base)
    print(f'\n\nNow processing {new_transcript_name_base}')

    new_file = open(new_transcript_pth, "w")
    for line in current_data_lines:
        new_file.write(line)
    new_file.close()