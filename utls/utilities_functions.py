# coding=utf8

import os
import shutil
import time
import sys
import subprocess as subp
import json
import pdb


def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    
    return platforms[sys.platform]


def check_folder_for_process(this_dir):
    '''If {this_dir} exists, ask if okay to overwrite.
        Return True to start process'''
    compute_procedure = False

    this_dir = str(this_dir)

    if not os.path.isdir(this_dir):
            os.mkdir(this_dir)
            compute_procedure = True

    if len(os.listdir(this_dir)) != 0:
        print(f"{this_dir} isn't empty, overwrite[o] or append[a]?")
        if input().lower() == 'o':
            shutil.rmtree(this_dir)
            os.mkdir(this_dir)
            compute_procedure = True
        elif input().lower() == 'a':
            print("Append content")
            compute_procedure = True
        else:
            print('Content was not modified')
    else:
        print('Folder: {} is empty. Proceed with computation.'.format(this_dir))
        compute_procedure = True

    return compute_procedure


def create_folder_if_missing(this_dir):
    this_dir = str(this_dir)

    if not os.path.isdir(this_dir):
            os.mkdir(this_dir)


def get_total_video_length(input_video_path):
    script_out = subp.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", input_video_path])
    ffprobe_data = json.loads(script_out)
    video_duration_seconds = float(ffprobe_data["format"]["duration"])

    return video_duration_seconds


def ffmpeg_split_audio(input_video, output_pth,
            start_time_csv = '0.00',
            stop_time_csv = 'default',
            sr = 16000,
            verbose = False,
            formatted = False,
            output_video_flag = False,
            times_as_integers = False):

    if times_as_integers:
        start_time_csv = str(start_time_csv)
        stop_time_csv = str(stop_time_csv)

    if formatted:
        (hstart, mstart, sstart) = start_time_csv.split(':')
        start_time_csv = str(float(hstart) * 3600 + float(mstart) * 60 + float(sstart))

        (hstop, mstop, sstop) = stop_time_csv.split(':')
        stop_time_csv = str(float(hstop) * 3600 + float(mstop) * 60 + float(sstop))

    if stop_time_csv == 'default':
        if get_platform() == 'Linux':
            cmd = f"ffmpeg -i '{input_video}' -acodec pcm_s16le -ac 1 -ar {sr} '{output_video}'"
        else:
            cmd = f"ffmpeg -i {input_video} -acodec pcm_s16le -ac 1 -ar {sr} {output_video}"
        subp.run(cmd, shell=True)
        return 'non_valid', 'non_valid'

    video_duration_seconds = get_total_video_length(input_video)

    # Check stop time is larger than start time
    if float(start_time_csv) >= float(stop_time_csv):
        print(f'Error! Start time {start_time_csv} is larger than stop time {stop_time_csv}')
        pdb.set_trace()

    # Check stop time is less than duration of the video
    if float(stop_time_csv) > video_duration_seconds:
        print(f'Error! Stop time {stop_time_csv} is larger than video duration {video_duration_seconds}')
        stop_time_csv = str(video_duration_seconds)
    
    # convert the starting time/stop time from seconds -> 00:00:00
    start_time_format = time.strftime("%H:%M:%S", time.gmtime(int(start_time_csv.split('.')[0]))) + \
        '.' + start_time_csv.split('.')[-1][0:2]
    stop_time_format = time.strftime("%H:%M:%S", time.gmtime(int(stop_time_csv.split('.')[0]))) + \
        '.' + stop_time_csv.split('.')[-1][0:2]

    if verbose:
        print(f'{start_time_format} - {stop_time_format}')

    if output_video_flag:
        ffmpeg_params = f' -c:v libx264 -crf 30 '
    else:
        ffmpeg_params = f' -acodec pcm_s16le -ac 1 -ar {sr} '

    if get_platform() == 'Linux':
        cmd = f"ffmpeg -i '{input_video}' '{ffmpeg_params}' -ss '{start_time_format}' -to  '{stop_time_format}' '{output_pth}'"
    else:
        cmd = f"ffmpeg -i {input_video}  {ffmpeg_params} -ss {start_time_format} -to  {stop_time_format} {output_pth}"

    # print(cmd)

    subp.run(cmd, shell=True)

    return start_time_csv, stop_time_csv
