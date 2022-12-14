# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 23:43:04 2022

@author: luis
"""
import glob
import subprocess as subp
import os
import time
import json

from UtilsTranscripts import check_folder_for_process


header_present = True

# Give the audios + csv folder
src_dir = '/home/luis/Dropbox/SpeechFall2022/GT_speakerLID/G-C3L1P-Mar21-A-Venkatesh_q2_02-05_src'

# One folder in -> one folder out
current_folder = src_dir
GT_clips_output_folder = src_dir + '/' + 'GT_selected_clips_output_folder'

new_transcr_path = GT_clips_output_folder + '/' + 'Stg1_timestamps_AppendHere.txt'

# gather all csv files
csv_selections_list = sorted(glob.glob("{}/*.csv".format(current_folder)))

# check all have the same base name
base_name_list = [x[:-28] for x in csv_selections_list]
if len(set(base_name_list)) != 1:
    print(f'Error in the base names, there are {len(set(base_name_list))} different names')

# Read the only src video from folder
src_video_list = sorted(glob.glob("{}/*.mpeg".format(current_folder)))
if len(src_video_list) != 1:
    print(f'Error, too many (or none) src videos found')
current_video_path = src_video_list[0]
current_video_name = current_video_path.split('/')[-1]

# Check if output audios are present
if check_folder_for_process(GT_clips_output_folder):

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


    # For loop over each entry
    new_file = open(new_transcr_path, "w")
    for idx in range(0, len(unique_lines_gt)):
        current_selection_path = GT_clips_output_folder + '/' + current_video_name[:-5] + \
            '-clip_' + str(idx).zfill(2) + '.mp4'

        # convert the starting time/stop time from seconds -> 00:00:00
        speaker_lang_csv, start_time_csv, stop_time_csv = unique_lines_gt[idx].strip().split('\t')

        current_start_time_format = time.strftime("%H:%M:%S", time.gmtime(int(start_time_csv.split('.')[0]))) + \
            '.' + start_time_csv.split('.')[-1][0:2]
        current_stop_time_format = time.strftime("%H:%M:%S", time.gmtime(int(stop_time_csv.split('.')[0]))) + \
            '.' + stop_time_csv.split('.')[-1][0:2]

        # Check stop time is larger than start time
        if start_time_csv >= stop_time_csv:
            print(f'Error! Start time {start_time_csv} is larger than stop time {stop_time_csv}')

        # Check stop time is less than duration of the video
        script_out = subp.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", current_video_path])
        ffprobe_data = json.loads(script_out)
        video_duration_seconds = float(ffprobe_data["format"]["duration"])

        if stop_time_csv > video_duration_seconds:
            print(f'Error! Stop time {start_time_csv} is larger than video duration {video_duration_seconds}')

        # print(f'{current_start_time_format} - {current_stop_time_format}')

        cmd = f"ffmpeg -i '{current_video_path}' -c:v libx264 -crf 30 -ss '{current_start_time_format}' \
        -to  '{current_stop_time_format}' '{current_selection_path}'"

        # Add new entry at the csv output file
        new_line = f'{current_video_name}\t{current_start_time_format}\t{current_stop_time_format}\n'
        new_file.write(new_line)
        # print(cmd)

        subp.run(cmd, shell=True)

    new_file.close()
