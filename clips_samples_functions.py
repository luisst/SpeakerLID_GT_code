import os
import sys
import re
import shutil
from pathlib import Path
from utilities_functions import check_folder_for_process, ffmpeg_split_audio, get_total_video_length
from scripts_functions import verify_video_csvNamebase, unique_entry_gen, simplify_praat, convert_to_csv

from config_params import speaker_swapping 


########################    01a Separate into selected videos #################################

def create_clips(current_folder, current_clips_output_folder,  header_flag = True):

    # Check if output audios are present
    if not(check_folder_for_process(current_clips_output_folder)):
        print(f'Not modified! Goodbye!')

    csv_selections_list, current_video_path = verify_video_csvNamebase(current_folder)
    current_video_name = current_video_path.name

    unique_lines_gt = unique_entry_gen(csv_selections_list, header_flag)


    new_transcr_path = current_clips_output_folder.joinpath('Timestamps_AppendedHere.txt')
    # For loop over each entry
    new_file = open(new_transcr_path, "w")
    for idx in range(0, len(unique_lines_gt)):
        current_selection_path = current_clips_output_folder.joinpath(current_video_name[:-5] + '_' + str(idx).zfill(3) + '.mp4')

        speaker_lang_csv, start_time_csv, stop_time_csv = unique_lines_gt[idx].strip().split('\t')

        start_time_csv, stop_time_csv = ffmpeg_split_audio(current_video_path, 
                                                current_selection_path,
                                                start_time_csv = start_time_csv,
                                                stop_time_csv = stop_time_csv,
                                                sr = 16000,
                                                verbose = False,
                                                formatted = False,
                                                output_video_flag=True)

        # Add new entry at the csv output file
        new_line = f'{current_video_name}\t{start_time_csv}\t{stop_time_csv}\n'
        new_file.write(new_line)

    new_file.close()


########################    01b Cut selected clip into smaller clips #################################

def process_raw_long_clips(current_folder, current_GT_clips_output_folder, 
        seg_length = 15,
        acceptable_length = 10,
        min_length = 5,
        flag_standard_names=True):

    # Check if output audios are present
    if not(check_folder_for_process(current_GT_clips_output_folder)):
        sys.exit(f'Not modified! Goodbye!')

    folder_videos_list = sorted(list(current_folder.glob('*.mp4')))

    list_to_segment = []
    list_passed = []
    # determine how many 15' segments would be
    for current_video_path in folder_videos_list:
        current_video_name = current_video_path.name

        duration_seconds = get_total_video_length(current_video_path)
        print(f'name: {current_video_name} \n duration: {duration_seconds}')

        if duration_seconds < seg_length + min_length  + 2 :
            list_passed.append([current_video_path, duration_seconds])
        else:
            list_to_segment.append([current_video_path, duration_seconds])

    # Segment videos process
    for idx in range(0, len(list_to_segment)):
        current_video_path, total_duration = list_to_segment[idx]
        current_video_name = current_video_path.name
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
                current_segment_path = current_GT_clips_output_folder.joinpath(current_video_name[:-4] + '-sample_' + str(idx_sample).zfill(2) + '.mp4')

                _, _ = ffmpeg_split_audio(current_video_path, 
                                                        current_segment_path,
                                                        start_time_csv = start_time,
                                                        stop_time_csv = stop_time,
                                                        times_as_integers=True,
                                                        output_video_flag=True)
                idx_sample += 1

                break
            elif remainder_length < (seg_length + acceptable_length): # Case B: cut remainder in half
                # Calculate our stop time
                stop_time = start_time + remainder_length / 2

                # Update remainder
                remainder_length = remainder_length / 2

                # call function cut segment
                print(f'\n ss {start_time} to {stop_time} | r: {remainder_length}')

                # Generate new name | Use -4 because 'mp4', use -5 because 'mpeg'
                current_segment_path = current_GT_clips_output_folder.joinpath(current_video_name[:-4] + '-sample_' + str(idx_sample).zfill(2) + '.mp4')

                _, _ = ffmpeg_split_audio(current_video_path, 
                                                        current_segment_path,
                                                        start_time_csv = start_time,
                                                        stop_time_csv = stop_time,
                                                        times_as_integers=True,
                                                        output_video_flag=True)
                idx_sample += 1

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
                current_segment_path = current_GT_clips_output_folder.joinpath(current_video_name[:-4] + '-sample_' + str(idx_sample).zfill(2) + '.mp4')

                _, _ = ffmpeg_split_audio(current_video_path, 
                                                        current_segment_path,
                                                        start_time_csv = start_time,
                                                        stop_time_csv = stop_time,
                                                        times_as_integers=True,
                                                        output_video_flag=True)
                idx_sample += 1

                # update counters
                start_time = start_time + seg_length

        # cut finding the most segments that adds less than 15 secs


    # Pass videos process
    for idx in range(0, len(list_passed)):
        current_video_path, total_duration = list_passed[idx]
        current_video_name = current_video_path.name 
        print(f'\n\nVideo passed: {current_video_name} \t duration: {total_duration}')

        current_segment_path = current_GT_clips_output_folder.joinpath(current_video_name[:-4] + '-sample_' + str(idx_sample).zfill(2) + '.mp4')

        shutil.move(current_video_path, current_segment_path)


    if flag_standard_names:
        folder_videos_list = sorted(list(current_GT_clips_output_folder.glob('*.mp4')))

        # iterate over all audio sorted
        for idx_seg, current_video_path in enumerate(folder_videos_list):
            current_video_name = current_video_path.name
            new_video_name = '-'.join(current_video_name.split('-')[0:-2]) + '-segment_' + str(idx_seg).zfill(3) + '.mp4'
            new_video_path = current_video_path.parent.joinpath(new_video_name)
            print(f'{current_video_path}\n{new_video_path}\n\n')
            os.rename(current_video_path, new_video_path)



########################  02a delete timestamps after the GT webapp   #################################

def delete_tms_from_folder(current_folder, idx_neg = 29):

   folder_csv_list = [x for x in os.listdir(current_folder) if re.search(r'\d\d\dZ.csv', x)]

   folder_csv_cleared = [(x[:-idx_neg]+'.csv') for x in folder_csv_list]

   print(folder_csv_cleared)

   # iterate over all audio sorted
   for idx_csv, current_csv_path in enumerate(folder_csv_list):
      os.rename(current_csv_path, folder_csv_cleared[idx_csv])


########################  02b convert csv file into simple praat + generate audios  #################################

# IMPORTANT: csv should have the same name as videos

def convert_csv_2_praat(input_csvs_pth, output_praat_pth, praat_name = '_praat.txt'):

    if not(check_folder_for_process(output_praat_pth)):
        sys.exit('goodbye')

    for csv_pth in input_csvs_pth.glob( '*.csv' ):
        print( csv_pth )
        # Src folder with all csv file to transform (future)
        csv_name = csv_pth.stem

        # Load name of the video those clips came from
        mp4_pth = csv_pth.parent.with_name(csv_name).with_suffix('.mp4')
        print(mp4_pth)

        # Generate audio mono 16K audio from video
        current_audio_name = mp4_pth.stem
        current_audio_name = current_audio_name.split('.')[0] + '.wav'
        new_audio_path = Path.joinpath(output_praat_pth, current_audio_name)

        _, _ = ffmpeg_split_audio(mp4_pth, new_audio_path)

        # Open the file into lines,
        new_transcript_name = csv_pth.stem + praat_name
        new_transcr_path = output_praat_pth.joinpath(new_transcript_name)
        new_file = open(new_transcr_path, "w")

        # Load 1 csv file
        f = open(csv_pth, 'r')
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
        video_duration_seconds =  get_total_video_length(mp4_pth)  
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


########################    03a After praat finetuning, convert back to csv   ##################

def convert_praat_2_csv(folder_pth, final_csv_pth, 
                    tag_from_praat = 'done', tag_after_finished = 'ready'):

    if not(check_folder_for_process(final_csv_pth)):
        sys.exit('goodbye')

    for praat_pth in folder_pth.glob( f'*_{tag_from_praat}.txt' ):
        print(f'\tNow processing: {praat_pth}\n')
        conrrected_praat_name = praat_pth.stem

        new_transcript_name = conrrected_praat_name.split('.')[0] + f'_{tag_after_finished}.csv'
        simplified_transcr_path = final_csv_pth.joinpath(new_transcript_name)

        simplify_praat(praat_pth, simplified_transcr_path)

        convert_to_csv(simplified_transcr_path, simplified_transcr_path)


########################    03b Generate audio samples #################################

def gen_audio_samples(current_folder_videos, current_folder_csv,
            GT_audio_output_folder,
            sr = 16000,
            praat_extension = '_' + 'praat_done_ready',
            tony_flag = True,
            ):

    # Check if output audios are present
    if not(check_folder_for_process(GT_audio_output_folder)):
        sys.exit(f'Not modified! Goodbye!')

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