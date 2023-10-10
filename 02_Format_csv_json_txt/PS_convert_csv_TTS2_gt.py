import csv
import json

import sys

from utilities_functions import check_folder_for_process
from pathlib import Path

# Define the dictionary mapping substrings to values
name_mapping = {
    'James': 'S0',
    'Morgan': 'S1',
    'Jennifer': 'S2',
    'Sofia': 'S3',
    'Edward': 'S4',
    'Keira': 'S5'
}


root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AlterAI_morph_PhuongYeti_English','VAD_synthetic')

current_final_csv_folder = root_dir.joinpath('GT_logs')
output_folder_csv_pth = root_dir.joinpath('gt_format')

transcript_pth_list = sorted(list(current_final_csv_folder.glob('*.csv')))

if not(check_folder_for_process(output_folder_csv_pth)):
    sys.exit("goodbye")

for current_csv_pth in transcript_pth_list:
    current_output_csv_pth = output_folder_csv_pth.joinpath(current_csv_pth.stem +'_praat_ready.csv')
    print(current_output_csv_pth)

    # Open the input CSV file for reading and the output CSV file for writing
    with open(current_csv_pth, mode='r', newline='') as csv_infile, \
            open(current_output_csv_pth, mode='w', newline='') as csv_outfile:

        # Create CSV reader and writer objects
        reader = csv.reader(csv_infile, delimiter='\t')
        writer = csv.writer(csv_outfile, delimiter='\t')

        # Process each row in the input CSV file
        for row in reader:
            if len(row) > 0:
                # Split the first column by underscores and extract the substring
                first_column_parts = row[0].split('_')
                if len(first_column_parts) >= 2:
                    substring = first_column_parts[-2]
                    row.insert(1, 'Eng')  # Insert 'Eng' as the second column
                    # Lookup the substring in the dictionary and replace it with the corresponding value
                    if substring in name_mapping:
                        row[0] = name_mapping[substring]
                    else:
                        raise ValueError(f"Substring '{substring}' not found in the dictionary.")

            # Write the modified row to the output CSV file
            writer.writerow(row)

    print("CSV file processed and modified successfully.")

        


