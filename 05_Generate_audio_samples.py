
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 21:50:22 2022

@author: luis
"""
from pathlib import Path

from UtilsTranscripts import check_folder_for_process, ffmpeg_split_audio
from speaker_swapping_config import speaker_swapping

    # # Check if output audios are present
    # if check_folder_for_process(GT_audio_output_folder):



# Give the audios + csv folder
current_folder_videos = Path.home().joinpath('Dropbox', 'SpeechFall2022','GT_speakerLID', 'home_TEST', 'G-C2L1P-Apr12-A-Allan_TEST')
current_folder_csv = current_folder_videos.joinpath('final_csv')

GT_audio_output_folder = current_folder_videos.joinpath('GT_audio_output_folder')

def gen_audio_samples(current_folder_videos,
current_folder_csv,
GT_audio_output_folder,
sr = 16000,
praat_extension = '_' + 'praat_done_ready',
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
