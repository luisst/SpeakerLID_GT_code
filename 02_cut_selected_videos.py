# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 23:17:22 2022

@author: luis
"""

import os
import glob
import shutil
import subprocess as subp
import json
import time

from LID_gt_utils import check_folder_for_process

seg_length = 15
acceptable_length = 10
min_length = 5

# Modify names at the end to make it compatible with the rest of the GT
#   you should have a very good reason to change this to False
flag_standard_names = True 

# Load source folder
src_videos = '/home/luis/Dropbox/SpeechFall2022/GT_speakerLID/G-C3L1P-Mar21-A-Venkatesh_q2_02-05_src/GT_selected_clips_output_folder'

# create folder and copy html file
base_folder = '/home/luis/Dropbox/SpeechFall2022/GT_speakerLID'
GT_selections_output_folder = base_folder + '/' + 'G-C3L1P-Mar21-A-Venkatesh_q2_02-05'

# Check if folder is already used
if check_folder_for_process(GT_selections_output_folder):

    folder_videos_list = sorted(glob.glob("{}/*.mp4".format(src_videos)))

    list_to_segment = []
    list_passed = []
    # determine how many 15' segments would be
    for current_video_path in folder_videos_list:
        current_video_name = current_video_path.split('/')[-1]

        # Obtain video length
        script_out = subp.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", current_video_path])

        ffprobe_data = json.loads(script_out)
        duration_seconds = float(ffprobe_data["format"]["duration"])
        print(f'name: {current_video_name} \n duration: {duration_seconds}')
        if duration_seconds < seg_length + min_length  + 2 :
            list_passed.append([current_video_path, duration_seconds])
        else:
            list_to_segment.append([current_video_path, duration_seconds])

    # Segment videos process
    for idx in range(0, len(list_to_segment)):
        current_video_path, total_duration = list_to_segment[idx]
        current_video_name = current_video_path.split('/')[-1]
        print(f'\n\nVideo: {current_video_name} \t duration: {total_duration}')
        # Init the counter values
        idx_sample = 0
        remainder_length = total_duration
        start_time = 0

        while(1):
            if remainder_length < min_length:
                print(f'Error! Segment remainder_length is too short! {remainder_length}')
            elif remainder_length < seg_length: # Case C: last piece less than seg length
                stop_time = total_duration
                print(f'Last bit - segment is passed')
                print(f'\n ss {start_time} to {stop_time} | r: {remainder_length}')

                # Generate new name | Use -4 because 'mp4', use -5 because 'mpeg'
                current_segment_path = GT_selections_output_folder + '/' + \
                    current_video_name[:-4] + '-sample_' + str(idx_sample).zfill(2) + '.mp4'

                current_start_time_format = time.strftime("%H:%M:%S", time.gmtime(int(str(start_time).split('.')[0]))) + \
                    '.' + str(start_time).split('.')[-1][0:2]
                current_stop_time_format = time.strftime("%H:%M:%S", time.gmtime(int(str(stop_time).split('.')[0]))) + \
                    '.' + str(stop_time).split('.')[-1][0:2]

                cmd = f"ffmpeg -i '{current_video_path}' -c:v libx264 -crf 30 -ss '{current_start_time_format}' \
                -to  '{current_stop_time_format}' '{current_segment_path}'"

                idx_sample += 1

                # print(cmd)
                subp.run(cmd, shell=True)

                break
            elif remainder_length < (seg_length + acceptable_length): # Case B: cut remainder in half
                # Calculate our stop time
                stop_time = start_time + remainder_length / 2

                # Update remainder
                remainder_length = remainder_length / 2

                # call function cut segment
                print(f'\n ss {start_time} to {stop_time} | r: {remainder_length}')

                # Generate new name | Use -4 because 'mp4', use -5 because 'mpeg'
                current_segment_path = GT_selections_output_folder + '/' + \
                    current_video_name[:-4] + '-sample_' + str(idx_sample).zfill(2) + '.mp4'

                current_start_time_format = time.strftime("%H:%M:%S", time.gmtime(int(str(start_time).split('.')[0]))) + \
                    '.' + str(start_time).split('.')[-1][0:2]
                current_stop_time_format = time.strftime("%H:%M:%S", time.gmtime(int(str(stop_time).split('.')[0]))) + \
                    '.' + str(stop_time).split('.')[-1][0:2]

                cmd = f"ffmpeg -i '{current_video_path}' -c:v libx264 -crf 30 -ss '{current_start_time_format}' \
                -to  '{current_stop_time_format}' '{current_segment_path}'"

                idx_sample += 1
                # print(cmd)
                subp.run(cmd, shell=True)

                # update counters
                start_time = start_time + remainder_length / 2

            else: # Case A: cut first seg from video
                # Calculate our stop time
                stop_time = start_time + seg_length

                # Update remainder
                remainder_length = remainder_length - seg_length

                # call function cut segment
                print(f'\n ss {start_time} to {stop_time} | r: {remainder_length}')

                # Generate new name | Use -4 because 'mp4', use -5 because 'mpeg'
                current_segment_path = GT_selections_output_folder + '/' + \
                    current_video_name[:-4] + '-sample_' + str(idx_sample).zfill(2) + '.mp4'

                current_start_time_format = time.strftime("%H:%M:%S", time.gmtime(int(str(start_time).split('.')[0]))) + \
                    '.' + str(start_time).split('.')[-1][0:2]
                current_stop_time_format = time.strftime("%H:%M:%S", time.gmtime(int(str(stop_time).split('.')[0]))) + \
                    '.' + str(stop_time).split('.')[-1][0:2]

                cmd = f"ffmpeg -i '{current_video_path}' -c:v libx264 -crf 30 -ss '{current_start_time_format}' \
                -to  '{current_stop_time_format}' '{current_segment_path}'"

                idx_sample += 1
                # print(cmd)
                subp.run(cmd, shell=True)

                # update counters
                start_time = start_time + seg_length

        # cut finding the most segments that adds less than 15 secs


    # Pass videos process
    for idx in range(0, len(list_passed)):
        current_video_path, total_duration = list_passed[idx]
        current_video_name = current_video_path.split('/')[-1]
        print(f'\n\nVideo passed: {current_video_name} \t duration: {total_duration}')

        dst_path = GT_selections_output_folder + '/' + \
                    current_video_name[:-4] + '-sample_' + str(0).zfill(2) + '.mp4'

        shutil.move(current_video_path, dst_path)


if flag_standard_names:
    folder_videos_list = sorted(glob.glob("{}/*.mp4".format(GT_selections_output_folder)))

    # iterate over all audio sorted
    for idx_seg, current_video_path in enumerate(folder_videos_list):
        current_video_name = current_video_path.split('/')[-1]
        new_video_name = '-'.join(current_video_name.split('-')[0:-2]) + '-segment_' + str(idx_seg).zfill(3) + '.mp4'
        new_video_path = '/'.join(current_video_path.split('/')[:-1]) + '/' + new_video_name
        print(f'{current_video_path}\n{new_video_path}\n\n')
        os.rename(current_video_path, new_video_path)


# # TODO: modify html with base video name
