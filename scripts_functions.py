import re
import sys

replacements=[("File type = ", ""), 
    ("Object class = ", ""),
    ("xmin = ", ""),
    ("xmax = ", ""),
    ("tiers\? ", ""),
    ("name = ", ""),
    ("class = ", ""),

    ("item \[\]: ", ""),
    ("text = ", ""),
    ("    ", ""),
    ("item \[\d\]:", ""),

    ("(?<=\"IntervalTier\" )(\n)(?=\"[sS]\d\")", ""),
    ("(?<=intervals \[\d\]:\n)(\d+\.?\d*?) \n(\d+\.?\d*?) \n\"(.*?)\"", "\g<1>\t\g<2>\t\"\g<3>\""),
    ("(?<=intervals \[\d\d\]:\n)(\d+\.?\d*?) \n(\d+\.?\d*?) \n\"(.*?)\"", "\g<1>\t\g<2>\t\"\g<3>\""),
    ("(?<=\"IntervalTier\" \"[sS]\d\" \n)(\d )\n((\d+\.?\d*?) )", "\g<1>\g<2>"),
    ("(?<=\n)\n", ""),

    ("(?<=\"ooTextFile\"\n\"TextGrid\"\n)(\d )\n((\d+\.?\d*?) )", "\g<1>\g<2>"),
    ("(intervals: size = (\d+?) \n)", "\g<2> interval coming\n"),
    ("intervals \[\d+?\]:\n", "")]

    
def simplify_praat(tmp_praat_pth, simplified_transcr_path):
    new_file = open(str(simplified_transcr_path), "w")

    f = open(str(tmp_praat_pth), 'r')
    lines = f.read()
    f.close()

    for pat,repl in replacements:

        lines = re.sub(pat, repl, lines)

    new_file.write(lines)
    new_file.close()

    f = open(str(simplified_transcr_path), 'r')
    relines = f.readlines()
    f.close()

    new_file = open(str(simplified_transcr_path), "w")
    for line in relines:
        line = line.rstrip()
        new_file.write(f'{line}\n')

    new_file.close()


def convert_to_csv(simplified_transcr_path, final_csv_pth):

    f = open(str(simplified_transcr_path), 'r')
    lines = f.read()
    f.close()

    regex = r"(?:\"IntervalTier\" \"([sS]\d)\"\n.+?\n(\d) interval coming\n(.+?)(?=\"IntervalTier\"))|(?:\"IntervalTier\" \"([sS]\d)\"\n.+?\n(\d) interval coming\n(.+?)(?=\Z))"

    matches = re.finditer(regex, lines, re.DOTALL)

    new_file = open(final_csv_pth, "w")
    new_file.write(f'Src\tStartTime\tEndTime\n')

    # For each speaker:
    for matchNum, match in enumerate(matches, start=1):

        groups_list = []
        for groupNum in range(1, len(match.groups())+1):
            groups_list.append(str(match.group(groupNum)))

        # Extract the valuable info for each match
        if groups_list[0] == 'None':
            speaker_id = groups_list[3]
            number_intervals = groups_list[4]
            raw_text = groups_list[5]
        else:
            speaker_id = groups_list[0]
            number_intervals = groups_list[1]
            raw_text = groups_list[2]

        # print(f'\nNow processing speaker {speaker_id}')

        # iterate over each interval
        raw_text = raw_text.strip()
        interval_list = raw_text.split('\n')
        if len(interval_list) != int(number_intervals):
            sys.exit("Intervals numbers are not matching! {len(interval_list)} vs {int(number_intervals)}")
        for inter_idx, line in enumerate(interval_list):
            strt_time, end_time, data_GT = line.split('\t')
            ID_lang = speaker_id + data_GT.strip("\"")
            if data_GT != '""':
                strt_time_str = str(round(float(strt_time),2))
                strt_end_str = str(round(float(end_time),2))
                new_file.write(f'{ID_lang}\t{strt_time_str}\t{strt_end_str}\n')

    new_file.close()

def verify_video_csvNamebase(current_folder, timestamp_flag):
    # gather all csv files
    csv_selections_list = sorted(list(current_folder.glob('*.csv')))
    csv_selections_list.extend(sorted(list(current_folder.glob('*.txt'))))

    # check all have the same base name
    if timestamp_flag:
        base_name_list = [str(x)[:-28] for x in csv_selections_list]
    else:
        base_name_list = [str(x)[:-3] for x in csv_selections_list]
    if len(set(base_name_list)) != 1:
        sys.exit(f'Error in the base names, there are {len(set(base_name_list))} different names')

    # Read the only src video from folder
    src_video_list = sorted(list(current_folder.glob('*.mpeg')))
    src_video_list.extend(sorted(list(current_folder.glob('*.mp4'))))

    if len(src_video_list) != 1:
        sys.exit(f'Error, too many (or none) src videos found')

    return csv_selections_list, src_video_list[0]


def unique_entry_gen(csv_selections_list, header_present=False):
    # extract content
    all_lines_gt = []
    for current_csv in csv_selections_list:

        print(f'now csv: {current_csv}\n')
        f = open(current_csv, 'r')
        lines = f.readlines()
        f.close()

        # remove header
        if header_present:
            lines.pop(0)

        all_lines_gt.extend(lines)

    # Create a unique list with only 1 instance of each entry
    unique_lines_gt = []
    for candidate_line in all_lines_gt:
        if candidate_line not in unique_lines_gt:
            unique_lines_gt.append(candidate_line)
    
    return unique_lines_gt