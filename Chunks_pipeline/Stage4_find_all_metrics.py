import sys
from pathlib import Path
import re


def append_to_summary(output_summary_path, metrics_folder):
    # Store in a list all 'csv' files inside the 'metrics' folder
    csv_files = list(metrics_folder.glob('*.txt'))

    new_file = open(output_summary_path, "a")

    new_file.write('New Method\n----------\n')

    for csv_file in csv_files:
        # Open csv_file and read all lines
        with open(csv_file, 'r') as f:
            lines = f.read()
        
        # Current name of the file
        current_file = csv_file.name

        # Regex to extract valuable info
        pattern = r'Entropy \d:.+'

        # Find the first match
        match = re.search(pattern, lines, re.DOTALL)

        print(f'\n\t\tCurrent file: {current_file}')

        if match:
            # Extract the matched substring
            result = match.group(0)
            print(f'\t{result}')
            new_file.write(f'\n----------\n{current_file}\n\t{result}\n')
        else:
            sys.exit("Substring not found.")
        


    new_file.close()

dataset_name = 'TestAO-Liz'

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Proposal_runs',dataset_name)
output_summary_path = root_dir.joinpath('entropy_summary.txt')

# Delete summary file if it exists
if output_summary_path.exists():
    output_summary_path.unlink()

# Iterate over all subfolders starting with 'STG3_'
for folder in root_dir.iterdir():
    if folder.is_dir() and folder.name.startswith('STG3_'):

        # Check if there is a folder called 'metrics' inside
        metrics_folder = folder.joinpath('metrics')
        if not metrics_folder.exists():
            print(f'No metrics folder found\tSkipped: {folder.name}')
        else:
            print('Metrics folder found')
            append_to_summary(output_summary_path, metrics_folder)


