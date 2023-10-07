from pathlib import Path
import sys

from utilities_functions import check_folder_for_process


current_csv_folder = Path.cwd() 

transcript_pth_list = sorted(list(current_csv_folder.glob('*.csv')))

for current_transcript_pth in transcript_pth_list:
    current_output_csv_pth = current_csv_folder.joinpath(current_transcript_pth.stem +'.csv')
    print(current_output_csv_pth)

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    new_file = open(current_output_csv_pth, "w")

    for line in lines:

        # Replace 2+ white spaces -> 1 spc
        line = ' '.join(line.split())

        # Replace space for tabs
        line = line.replace(',', '\t')

        # Add new line at the end
        line = line + '\n'

        # Save line into new csv
        new_file.write(line)
    
    new_file.close()




