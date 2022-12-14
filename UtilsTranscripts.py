# coding=utf8

import re
import os
import shutil
import time
import sys
import subprocess as subp
import json
import pdb

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

    ("(?<=\"IntervalTier\" )(\n)(?=\"S\d\")", ""),
    ("(?<=intervals \[\d\]:\n)(\d+\.?\d*?) \n(\d+\.?\d*?) \n(\"\S*?\")", "\g<1> \g<2> \g<3>"),
    ("(?<=\"IntervalTier\" \"S\d\" \n)(\d )\n((\d+\.?\d*?) )", "\g<1>\g<2>"),
    ("(?<=\n)\n", ""),

    ("(?<=\"ooTextFile\"\n\"TextGrid\"\n)(\d )\n((\d+\.?\d*?) )", "\g<1>\g<2>"),
    ("(intervals: size = (\d+?) \n)", "\g<2> interval coming\n"),
    ("intervals \[\d+?\]:\n", "")]


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

    regex = r"(?:\"IntervalTier\" \"(S\d)\"\n.+?\n(\d) interval coming\n(.+?)(?=\"IntervalTier\"))|(?:\"IntervalTier\" \"(S\d)\"\n.+?\n(\d) interval coming\n(.+?)(?=\Z))"

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
            strt_time, end_time, data_GT = line.split()
            ID_lang = speaker_id + data_GT.strip("\"")
            if data_GT != '""':
                strt_time_str = str(round(float(strt_time),2))
                strt_end_str = str(round(float(end_time),2))
                new_file.write(f'{ID_lang}\t{strt_time_str}\t{strt_end_str}\n')

    new_file.close()

def get_total_video_length(input_video_path):
    script_out = subp.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", input_video_path])
    ffprobe_data = json.loads(script_out)
    video_duration_seconds = float(ffprobe_data["format"]["duration"])

    return video_duration_seconds


def ffmpeg_split_audio(input_video, output_video,
            start_time_csv = '0.00',
            stop_time_csv = 'default',
            sr = 16000,
            verbose = False):

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

    if get_platform() == 'Linux':
        cmd = f"ffmpeg -i '{input_video}' -acodec pcm_s16le -ac 1 -ar {sr} -ss '{start_time_format}' -to  '{stop_time_format}' '{output_video}'"
    else:
        cmd = f"ffmpeg -i {input_video} -acodec pcm_s16le -ac 1 -ar {sr} -ss {start_time_format} -to  {stop_time_format} {output_video}"


    # print(cmd)

    subp.run(cmd, shell=True)

    return start_time_csv, stop_time_csv


def gen_audio_samples(current_folder_videos,
current_folder_csv,
GT_audio_output_folder,
sr = 16000,
praat_extension = '_' + 'praat_done_ready'
tony_flag = True,
):
    print(f'\n\tCurrent Folder: {current_folder_videos.stem}\n')

    # Obtain each gt_transcript
    folder_transcripts_list = sorted(list(current_folder_csv.glob('*.csv')))
    folder_videos_list = sorted(list(current_folder_videos.glob('*.mp4')))
    csv_names_only_list = [x.stem for x in folder_transcripts_list]

    # New transcript per folder
    new_transcr_path = GT_audio_output_folder.joinpath('transcript.txt')
    new_file = open(new_transcr_path, "w")

    # Check every clip and match the csv GT file
    for current_input_video in folder_videos_list:
        current_video_name = current_input_video.stem

        # Verify there's a corresponding csv file
        if (current_video_name + praat_extension) in csv_names_only_list:
            indx_csv = csv_names_only_list.index(current_video_name + praat_extension)
            f = open(folder_transcripts_list[indx_csv], 'r')
            lines = f.readlines()
            f.close()
            print(f'\nnow video: {current_input_video}\n')
        else:
            print(f'\nVideo SKIPPED: {current_input_video}\n')
            continue

        lines.pop(0)
        # Create samples audio from each clip
        for idx in range(0, len(lines)):
            speaker_lang_csv, start_time_csv, stop_time_csv = lines[idx].strip().split('\t')

            if tony_flag:
                speaker_ID = speaker_swapping(speaker_lang_csv[0:2])
            else:
                speaker_ID = speaker_lang_csv[0:2]

            current_audio_sample_name = current_video_name + '-sample-' + \
                str(idx).zfill(4) + '_' + speaker_ID + '.wav'
            current_audio_sample_path = GT_audio_output_folder.joinpath(current_audio_sample_name)

            start_mod, end_mod = ffmpeg_split_audio(input_video=current_input_video, 
            output_video = current_audio_sample_path,
            start_time_csv = start_time_csv,
            stop_time_csv = stop_time_csv,
            sr = sr)

            # Add new entry at the csv output file
            current_filename_transcript = current_audio_sample_path.stem
            new_line = f'{current_filename_transcript}\t{speaker_ID}\t{speaker_lang_csv[2:]}\t{start_mod}\t{end_mod}\n'
            new_file.write(new_line)

    new_file.close()
