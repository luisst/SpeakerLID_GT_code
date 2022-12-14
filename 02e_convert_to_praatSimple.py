# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
from pathlib import Path
import subprocess as subp
import json


# ------------      Convert from CSV --> praat -------------------

#Iterate all csv files in folder
folder_pth = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID', 'G-C2L1P-Apr12-A-Allan_q2_04-05', 'to_praat')
for csv_pth in folder_pth.glob( '*.csv' ):
    print( csv_pth )
    # Src folder with all csv file to transform (future)
    csv_name = csv_pth.stem

    # Load name of the video those clips came from
    mp4_pth = csv_pth.parent.with_name(csv_name).with_suffix('.mp4')

    print(mp4_pth)
    # Open the file into lines,
    new_transcript_name = csv_name.split('.')[0] + '_praat.txt'
    new_transcr_path = csv_pth.with_name(new_transcript_name)
    new_file = open(str(new_transcr_path), "w")

    # Load 1 csv file
    f = open(str(csv_pth), 'r')
    lines = f.readlines()
    f.close()

    # For loop -> 5 different speakers (dict)
    gt_dict = {'S0':[],
            'S1':[],
            'S2':[],
            'S3':[],
            'S4':[]}

    lines.pop(0)
    for line in lines:
        speaker_IDLang, strt_time, end_time = line.split('\t')
        speaker_ID = speaker_IDLang[:2]
        speaker_lang = speaker_IDLang[2:]
        end_time = end_time.strip()

        gt_dict[speaker_ID].append([speaker_lang, strt_time, end_time])

    # Include total length of the video
    script_out = subp.check_output(["ffprobe", "-v", "quiet", "-show_format",
                                    "-print_format", "json", str(mp4_pth)])
    ffprobe_data = json.loads(script_out)
    video_duration_seconds = float(ffprobe_data["format"]["duration"])

    total_time = str(video_duration_seconds)

    # Generate top header of praat
    praat_manual_header = f'''"ooTextFile"
"TextGrid"
0 {total_time}
<exists>
5 tiers'''

    new_file.write(praat_manual_header + '\n')

    # write one section at a time (total 5)
    #### ASSUMED: all timestamps are unique and in order
    for key in gt_dict.keys():
        current_speaker_intervals = gt_dict[key]
        n_inter = len(current_speaker_intervals) + 2 + len(current_speaker_intervals) - 1
        speaker_header = f'"IntervalTier" "{key}"\n0 {total_time}\n{n_inter} interval coming'
        new_file.write(speaker_header + '\n')

        current_speaker_intervals = sorted(current_speaker_intervals, key=lambda x: float(x[1]))
        # Make new array
        current_speaker_timestamps_ordered = [0]

        for interval in current_speaker_intervals:
            current_speaker_timestamps_ordered.append(interval[1])
            current_speaker_timestamps_ordered.append(interval[2])
        current_speaker_timestamps_ordered.append(total_time)

        for int_idx in range(0, n_inter):
            int_start = current_speaker_timestamps_ordered[int_idx]
            int_end = current_speaker_timestamps_ordered[int_idx+1]
            if (int_idx+1)%2 == 0:
                int_lang = current_speaker_intervals[int((int_idx + 1)/2 -1)][0]
            else:
                int_lang = ""

            new_line = f'{int_start} {int_end} "{int_lang}"\n'
            new_file.write(new_line)

    new_file.close()


