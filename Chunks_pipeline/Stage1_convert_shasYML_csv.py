import argparse
import os
from pathlib import Path
import re
import sys

def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")

def process_files(yml_pth, output_csv_folder):
    """
    Process YML files and generate CSV files.

    Args:
        yml_pth (str): The path to the YML file.
        output_csv_folder (str): The path to the output CSV folder.
    """
    regex = r"duration: (\d+?.\d+?), offset: (\d+?.\d+?), rW: \d.?\d*?, speaker_id: (\w+?), uW: \d.?\d*?, wav: (.*?)}"

    print(f'Processing {yml_pth.stem}...')
    #open text file in read mode
    text_file = open(yml_pth, "r")
    
    #read whole file to a string
    data = text_file.read()
    
    #close file
    text_file.close()
    
    # print(data)

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
        new_file.write(f'{new_filename}\t{match.group(2)}\t{stop_val}\n')

        prev_name = new_filename

    new_file.close()

# Define the command-line arguments
parser = argparse.ArgumentParser(description='Process some files.')
parser.add_argument('yml_pth', type=valid_path, help='The path to the YML file')
parser.add_argument('output_csv_folder', type=valid_path, help='The path to the output CSV folder')


# Parse the command-line arguments
args = parser.parse_args()

# Now you can use args.yml_pth and args.output_csv_folder instead of sys.argv[1] and sys.argv[2]
yml_pth = args.yml_pth
output_csv_folder = args.output_csv_folder

# Call the process_files function
process_files(yml_pth, output_csv_folder)
