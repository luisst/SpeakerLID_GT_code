from pathlib import Path
import sys

from utilities_functions import check_folder_for_process

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','Sample_dataset','All_results','vad-crdnn-libriparty')

input_csv_folder = root_dir.joinpath('raw_csv_spc')
output_folder_csv_pth = root_dir.joinpath('final_csv') 

transcript_pth_list = sorted(list(input_csv_folder.glob('*.txt')))

if not(check_folder_for_process(output_folder_csv_pth)):
    sys.exit("goodbye")


verbose = False

for current_transcript_pth in transcript_pth_list:
    current_output_csv_pth = output_folder_csv_pth.joinpath(current_transcript_pth.stem +'.csv')
    print(current_output_csv_pth)

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    new_file = open(current_output_csv_pth, "w")

    for line in lines:

        # Replace 2+ white spaces -> 1 spc
        line = ' '.join(line.split())

        # Replace space for tabs
        line = line.replace(' ', '\t')

        # Add new line at the end
        line = line + '\n'

        # Save line into new csv
        new_file.write(line)
    
    new_file.close()




