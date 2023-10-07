import sys
from pathlib import Path


def extract_start_stop_diarization(line):
    path_name, spk, lang, start_csv_format, stop_csv_format = line.split('\t')
    return spk, start_csv_format, stop_csv_format


def csv2float(time_csv_format):

    (hstart, mstart, sstart) = time_csv_format.split(':')
    float_val = float(hstart) * 3600 + float(mstart) * 60 + float(sstart)

    return float_val

def extract_time_csv(current_csv_pth, format_type):
    with open(current_csv_pth) as f:
        lines = [line.rstrip() for line in f]
    
    durations_accumulator = 0
    for line in lines:
        if format_type == 'diarization':
            _, start_csv_format, stop_csv_format = extract_start_stop_diarization(line)
        else:
            start_csv_format = 0
            stop_csv_format = 0
            print(f'Format type error!')

        duration_line = csv2float(stop_csv_format) - csv2float(start_csv_format)
        durations_accumulator += duration_line

    return durations_accumulator

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection')
GT_output_dir = root_dir.joinpath('03_Final_samples')

# State
format_type = 'diarization'

total_time_csv = 0
# Iterate through all folders in results
for current_path in Path(GT_output_dir).iterdir():
    # Select only folders NOT empty
    if current_path.is_dir() and any(Path(current_path).iterdir()):
        csv_candidates_list = sorted(list(current_path.glob('*.csv')))
        csv_candidates_list.extend(sorted(list(current_path.glob('*.txt'))))

        # Verify there is only 1 transcript
        if len(csv_candidates_list) != 1:
            sys.exit(f'More than 1 transcript! {len(csv_candidates_list)}')

        current_csv_pth = csv_candidates_list[0]
        print(current_csv_pth)

        current_csv_total_time = extract_time_csv(current_csv_pth, format_type)
        total_time_csv += current_csv_total_time

print(f'Total time in ALL csv files: {total_time_csv}')

