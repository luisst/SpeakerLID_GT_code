from pathlib import Path
import sys

from utilities_functions import check_folder_for_process

transcript_folder_pth = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TTS_minitest','GT')
transcript_pth_list = sorted(list(transcript_folder_pth.glob('*.csv')))

output_folder_csv_pth = transcript_folder_pth.joinpath('joined_timestamps') 

if not(check_folder_for_process(output_folder_csv_pth)):
    sys.exit("goodbye")


tol_val = 1
verbose = False

for current_transcript_pth in transcript_pth_list:
    current_output_csv_pth = output_folder_csv_pth.joinpath(current_transcript_pth.stem +'.csv')
    print(current_output_csv_pth)

    with open(current_transcript_pth) as f:
        lines = [line.rstrip() for line in f]

    # csv_src, csv_start_time, csv_stop_time = lines[0].rstrip().split('\t')
    new_csv_list = []
    new_csv_list.append(lines[0].rstrip().split('\t'))

    for idx in range(1, len(lines)):

        _, prev_start_time, prev_stop_time = new_csv_list[-1]
        _, current_start_time, current_stop_time = lines[idx].rstrip().split('\t')

        prev_stop_time = float(prev_stop_time)
        prev_start_time = float(prev_start_time)
        current_start_time = float(current_start_time)
        current_stop_time = float(current_stop_time)

        # Sanity check
        if current_start_time < prev_start_time:
            sys.exit(f'error in timestamps: start_time {current_start_time} is less than prev start_time {prev_start_time}')

        if current_start_time < prev_stop_time:
            print(f'WARNING! overlap found! {prev_stop_time} - {current_start_time}')
        

        # Decide wheter to join or not
        if (tol_val + prev_stop_time) >= current_start_time:
            new_csv_list[-1][-1] = str(current_stop_time)
            if verbose:
                print(f'joined! ({prev_start_time}-{prev_stop_time}) with ({current_start_time}-{current_stop_time})')
        else:
            new_csv_list.append(lines[idx].rstrip().split('\t'))



    new_file = open(current_output_csv_pth, "w")
    for new_line in new_csv_list:
        new_file.write(f'{new_line[0]}\t{new_line[1]}\t{new_line[2]}\n')

    new_file.close()