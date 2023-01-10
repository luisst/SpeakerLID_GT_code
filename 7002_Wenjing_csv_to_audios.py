from pathlib import Path
 
from utilities_functions import check_folder_for_process, ffmpeg_split_audio


base_folder_pth = Path.home().joinpath('Dropbox', 'DATASETS_AUDIO', 'Speech_vs_BackgroundNoise', 'Wenjing_GT')
input_csv_pth = base_folder_pth.joinpath('output_csv')
videos_folder_pth = base_folder_pth.joinpath('src_videos')

# Obtain each gt_transcript
folder_txt_list = sorted(list(input_csv_pth.glob('*.txt')))
folder_videos_list = sorted(list(videos_folder_pth.glob('*.mp4')))
folder_videos_list.extend(sorted(list(videos_folder_pth.glob('*.mpeg'))))

txt_names_only_list = [x.stem for x in folder_txt_list]

# New transcript per folder
output_wav_pth = base_folder_pth.joinpath('output_wav_files') 

if not check_folder_for_process(output_wav_pth):
    print("goodbye")

new_transcr_path = output_wav_pth.joinpath('transcript.txt')
new_file = open(new_transcr_path, "w")


# Check every clip and match the csv GT file
for current_input_video in folder_videos_list:
    current_video_name = current_input_video.stem

    # Verify there's a corresponding csv file
    if current_video_name in txt_names_only_list:
        indx_txt = txt_names_only_list.index(current_video_name)
        f = open(folder_txt_list[indx_txt], 'r')
        lines = f.readlines()
        f.close()
        print(f'\nnow video: {current_input_video}\n')
    else:
        print(f'\nVideo SKIPPED: {current_input_video}\n')
        continue

    # Create samples audio from each clip
    for idx in range(0, len(lines)):
        video_name, start_time_txt, stop_time_txt, speaker_id = lines[idx].strip().split('\t')

        current_audio_sample_name = current_video_name + '-sample-' + \
            str(idx).zfill(4) + '_' + speaker_id + '.wav'
        current_audio_sample_path = output_wav_pth.joinpath(current_audio_sample_name)

        start_mod, end_mod = ffmpeg_split_audio(input_video=current_input_video, 
        output_video = current_audio_sample_path,
        start_time_csv = start_time_txt,
        stop_time_csv = stop_time_txt,

        sr = 16000,
        formatted = True)

        # Add new entry at the csv output file
        current_filename_transcript = current_audio_sample_path.stem
        new_line = f'{current_filename_transcript}\t{start_mod}\t{end_mod}\t{speaker_id}\n'
        new_file.write(new_line)

new_file.close()
