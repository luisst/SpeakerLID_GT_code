from pathlib import Path
import timeit
import sys

from utilities_functions import check_folder_for_process


# For each INDEX -> write SX that is going to replace 
new_spkr_ID_list = ['S1', 'S0', 'S2', 'S3', 'S4']


starttime = timeit.default_timer()
print("The start time is :",starttime)

current_dir = Path.cwd()
transcript_pth_list = sorted(list(current_dir.glob('*.csv')))
output_folder_csv = current_dir.joinpath('corrected_files')

check_folder_for_process(output_folder_csv)

for current_transcript_pth in transcript_pth_list:
    current_output_csv_pth = output_folder_csv.joinpath(current_transcript_pth.stem +'.csv')
    print(current_output_csv_pth.name)

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    new_file = open(current_output_csv_pth, "w")

    # Copy header
    new_file.write(f'{lines.pop(0)}\n')

    for line in lines:

        # Extract data
        srcLang, start_str, end_str = line.split('\t')
        speaker_str = srcLang[0:2]
        lang_str = srcLang[2:]

        # Swap speaker ID
        new_speaker_str = new_spkr_ID_list[int(speaker_str[1])] 

        # Join all together
        new_line = f'{new_speaker_str}{lang_str}\t{start_str}\t{end_str}\n'

        # Save line into new csv
        new_file.write(new_line)
    
    new_file.close()

print("The total time:", timeit.default_timer() - starttime)