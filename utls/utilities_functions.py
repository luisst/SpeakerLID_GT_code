# coding=utf8
import re
import os
import shutil
import time
import csv
import sys
import subprocess as subp
import json
import pdb
import pandas as pd
import datetime
from pathlib import Path


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
            Path(this_dir).mkdir( parents=True, exist_ok=True )
            compute_procedure = True

    if len(os.listdir(this_dir)) != 0:
        print(f"{this_dir} isn't empty, overwrite[o] or append[a]?")
        user_response = input().lower()
        print(f'user answered: {user_response}')
        if user_response == 'o':
            shutil.rmtree(this_dir)
            os.mkdir(this_dir)
            compute_procedure = True
        elif user_response == 'a':
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
        Path(this_dir).mkdir( parents=True, exist_ok=True )


def get_total_video_length(input_video_path):
    script_out = subp.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", input_video_path])
    ffprobe_data = json.loads(script_out)
    video_duration_seconds = float(ffprobe_data["format"]["duration"])

    return video_duration_seconds


def find_audio_duration(current_transcript_pth, audios_folder, suffix_added, verbose=False):
    # Find the path of the audio
    if suffix_added != '':
        current_basename = extract_basename(current_transcript_pth.stem, suffix_added)
        candidate_path = audios_folder.joinpath(current_basename + '.wav')
    else:
        candidate_path = audios_folder.joinpath(current_gt_pth.stem + '.wav')

    if candidate_path.exists ():
        if verbose:
            print (f'File exist: {candidate_path}')
        return get_total_video_length(candidate_path)
    else:
        sys.error(f'Error! Audio {candidate_path} was not located!')
    

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

    if verbose:
        if stop_time_csv == 'default':
            if get_platform() == 'Linux':
                cmd = f"ffmpeg -i '{input_video}' -acodec pcm_s16le -ac 1 -ar {sr} '{output_pth}'"
            else:
                cmd = f"ffmpeg -i {input_video} -acodec pcm_s16le -ac 1 -ar {sr} {output_pth}"
            subp.run(cmd, shell=True)
            return 'non_valid', 'non_valid'
    else:
        if stop_time_csv == 'default':
            if get_platform() == 'Linux':
                cmd = f"ffmpeg -i '{input_video}' -hide_banner -loglevel error -acodec pcm_s16le -ac 1 -ar {sr} '{output_pth}'"
            else:
                cmd = f"ffmpeg -i {input_video} -hide_banner -loglevel error -acodec pcm_s16le -ac 1 -ar {sr} {output_pth}"
            subp.run(cmd, shell=True)
            return 'non_valid', 'non_valid'

    video_duration_seconds = get_total_video_length(input_video)

    # Check stop time is larger than start time
    if float(start_time_csv) >= float(stop_time_csv):
        print(f'Error! Start time {start_time_csv} is larger than stop time {stop_time_csv}')
        pdb.set_trace()

    # Check stop time is less than duration of the video
    if float(stop_time_csv) > video_duration_seconds:
        print(f'Warning! [changed] Stop time {stop_time_csv} is larger than video duration {video_duration_seconds}')
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
    else:
        if output_video_flag:
            ffmpeg_params = f' -hide_banner -loglevel error -c:v libx264 -crf 30 '
        else:
            ffmpeg_params = f' -hide_banner -loglevel error -acodec pcm_s16le -ac 1 -ar {sr} '

    if get_platform() == 'Linux':
        cmd = f"ffmpeg -i '{input_video}' '{ffmpeg_params}' -ss '{start_time_format}' -to  '{stop_time_format}' '{output_pth}'"
    else:
        cmd = f"ffmpeg -i {input_video}  {ffmpeg_params} -ss {start_time_format} -to  {stop_time_format} {output_pth}"

    # print(cmd)

    subp.run(cmd, shell=True)

    return start_time_csv, stop_time_csv

def extract_basename(input_str, suffix_added):
    mymatch = re.search(r'.+(?=_{})'.format(suffix_added), input_str)
    if mymatch != None:
        mystring = mymatch.group()    
    else:
        mystring = ''
    return mystring

def matching_basename_pathlib_gt_pred(GT_pth, pred_pth, 
        gt_suffix_added='', pred_suffix_added='',
        gt_ext = 'txt', pred_ext = 'txt', verbose = False):

    if gt_suffix_added == '':
        GT_list = sorted(list(GT_pth.glob(f'*.{gt_ext}')))
    else:
        GT_list = sorted(list(GT_pth.glob(f'*_{gt_suffix_added}.{gt_ext}')))

    if pred_suffix_added == '':
        pred_list = sorted(list(pred_pth.glob(f'*.{pred_ext}')))
    else:
        pred_list = sorted(list(pred_pth.glob(f'*_{pred_suffix_added}.{pred_ext}')))


    if len(GT_list) == 0:
        print(f'ERROR GT list empty. Check suffix')
    
    if len(pred_list) == 0:
        print(f'ERROR!! Pred list is empty. Check suffix')

    # Extract basenames from pathlib

    if gt_suffix_added == '':
        gt_list_basenames = [x.stem for x in GT_list]
    else:
        gt_list_basenames = [extract_basename(x.name, gt_suffix_added) for x in GT_list]

    if pred_suffix_added == '':
        pred_list_basenames = [x.stem for x in pred_list]
    else:
        pred_list_basenames = [extract_basename(x.name, pred_suffix_added) for x in pred_list]

    if verbose:
        print(f'GT: {gt_list_basenames}\nPred: {pred_list_basenames}')

    # Check for duplicates
    if len(gt_list_basenames) != len(list(set(gt_list_basenames))):
        sys.exit(f'Duplicates found at folder {GT_pth}')

    if len(pred_list_basenames) != len(list(set(pred_list_basenames))):
        sys.exit(f'Duplicates found at folder {pred_pth}')

    gt_idxs = []
    for idx, current_gt in enumerate(gt_list_basenames):
        if current_gt in pred_list_basenames:
            gt_idxs.append(idx)

    pred_idxs = []
    for idx, current_pred in enumerate(pred_list_basenames):
        if current_pred in gt_list_basenames:
            pred_idxs.append(idx)

    # Verify same length
    if len(gt_idxs) != len(pred_idxs):
        sys.exit(f'matching indexes are not equal!')

    # Return the tuples
    matching_list = []
    for idx in range(0, len(gt_idxs)):
        matching_list.append((GT_list[gt_idxs[idx]], pred_list[pred_idxs[idx]]))

    # if verbose:
        # print(matching_list)

    return matching_list


def check_csv_exists_pathlib(csv_path):
    if csv_path.exists():
        print("CSV file already exists, do you want to overwrite? (y)")
        if input().lower() != 'y':
            print("File not modified")
            sys.exit()

def check_same_length(list1, list2):
    if len(list1) != len(list2):
        print("Error, your list1 and list2 have different lengths")
        sys.exit()


def write_2_csv(*args, **kwargs):
    """
    Function to write csv files.
    args:
        - Columns for the csv (matched to the names)
    kwargs:
        - cols: List of names for columns (matched to args)
        - path: output_path for the csv
    """
    defaultKwargs = { 'time_format': True, 'txt_flag': False }
    kwargs = { **defaultKwargs, **kwargs }

    # my_df = pd.DataFrame(index=False)
    my_df = pd.DataFrame()

    csv_path = kwargs['path']
    columns_values = kwargs['cols']

    # check if csv file exists
    check_csv_exists_pathlib(csv_path)

    if len(args) > 2:
        check_same_length(args[0], args[1])
    elif len(args) > 3:
        check_same_length(args[1], args[2])

    idx = 0
    for current_list in args:
        my_df[columns_values[idx]] = current_list
        idx = idx + 1

    today_date = '_' + str(datetime.date.today())
    datetime_object = datetime.datetime.now()
    time_f = "-{:d}_{:02d}".format(datetime_object.hour, datetime_object.minute)

    if kwargs['time_format']:
        full_output_csv_path = csv_path.with_name(csv_path.stem + today_date + time_f)
    else:
        full_output_csv_path = csv_path.with_name(csv_path.stem)

    if kwargs['txt_flag']:
        my_df.to_csv(full_output_csv_path.with_suffix('.txt'), header=False, sep='\t', index=False)
    else:
        my_df.to_csv(full_output_csv_path.with_suffix('.csv'), index=False)


def calculate_duration_in_folder(videos_folder_pth, wav_flag = False, return_list = False, return_names = False):

    if wav_flag:
        folder_videos_list = sorted(list(videos_folder_pth.glob('*.wav')))
    else:
        folder_videos_list = sorted(list(videos_folder_pth.glob('*.mp4')))
        folder_videos_list.extend(sorted(list(videos_folder_pth.glob('*.mpeg'))))

    total_time_folder = 0

    list_lengths = []
    list_names = []

    for current_video_pth in folder_videos_list:
        # obtain total time of video
        current_length_seconds = get_total_video_length(current_video_pth)
        print(f'\tNow media: {current_video_pth.name}')
        list_names.append(current_video_pth.name)
        list_lengths.append(current_length_seconds)

        total_time_folder = total_time_folder + current_length_seconds


    if return_list:
        if return_names:
            return list_names, list_lengths, total_time_folder
        else:
            return list_lengths, total_time_folder
    else:
        return total_time_folder

def has_header(csv_file_path):
    try:
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            first_row = next(csv_reader)
            return any(row.isalpha() for row in first_row)
    except FileNotFoundError:
        print(f"File not found: {csv_file_path}")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def extract_matching_csv_media(csv_folder_path, media_folder_path, 
                               audio_flag=True, ending_csv=''):
    
    if ending_csv != '':
        ending_csv = '_' + ending_csv 

    # Obtain each gt_transcript
    folder_transcripts_list = sorted(list(csv_folder_path.glob('*.csv')))
    
    if audio_flag:
        folder_media_list = sorted(list(media_folder_path.glob('*.wav')))
    else:
        folder_media_list = sorted(list(media_folder_path.glob('*.mp4')))

    csv_names_only_list = [x.stem for x in folder_transcripts_list]

    matching_media_list = []
    matching_csv_list = []

    # Check every clip and match the csv GT file
    for current_input_media in folder_media_list:
        current_media_name = current_input_media.stem
        # Verify there's a corresponding csv file
        if (current_media_name + ending_csv) in csv_names_only_list:

            match_csv_path = csv_folder_path.joinpath(current_media_name + ending_csv + '.csv')
            matching_csv_list.append(match_csv_path)
            matching_media_list.append(current_input_media)

            print(f'Match: {current_media_name}')
        else:
            print(f'SKIPPED: {current_media_name}')
            continue
    
    if len(matching_media_list) == 0:
        print(f'\n\n ERROR! No match was found at {csv_folder_path}\n{media_folder_path}\n\n') 

    return matching_csv_list, matching_media_list