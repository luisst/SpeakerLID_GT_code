import os
import random
from pathlib import Path
import subprocess
from utilities_functions import get_total_video_length, ffmpeg_split_audio

def create_folders(output_folder_mp4, output_folder_wavs):
    Path(output_folder_mp4).mkdir(parents=True, exist_ok=True)
    Path(output_folder_wavs).mkdir(parents=True, exist_ok=True)

def extract_audio(input_video, output_audio):
    subprocess.run(['ffmpeg', '-i', input_video, '-vn', '-ac', '1', '-ar', '16000', '-acodec', 'pcm_s16le', output_audio])

def main(input_folders, output_folder_mp4, output_folder_wavs, n=10, clip_duration=40):
    create_folders(output_folder_mp4, output_folder_wavs)

    mp4_output_path = Path(output_folder_mp4)
    wavs_output_path = Path(output_folder_wavs)

    # Get a list of all mp4 files in the input folders
    mp4_files = []
    for input_folder in input_folders:
        mp4_files.extend(list(Path(input_folder).glob('*.mp4')))
        mp4_files.extend(list(Path(input_folder).glob('*.mpeg')))

    for idx in range(n):
        # Randomly select a video clip
        clip = random.choice(mp4_files)

        video_duration_seconds = get_total_video_length(clip)

        # Generate a random start time within the allowed range
        start_time = random.uniform(0, max(0, video_duration_seconds - clip_duration))

        # Create output file paths
        output_wav = wavs_output_path / (clip.stem + '_' + str(idx).zfill(3) + '.wav')
        output_mp4 = output_folder_mp4 / (clip.stem + '_' + str(idx).zfill(3) + '.mp4')

        stop_time = start_time + clip_duration + 1

        _, _ = ffmpeg_split_audio(clip, output_wav, \
            start_time_csv = str(int(start_time)),
            stop_time_csv = str(int(stop_time)),
            sr = 16000,
            verbose = True,
            formatted = False,
            output_video_flag = False,
            times_as_integers = False)

        _, _ = ffmpeg_split_audio(clip, output_mp4, \
            start_time_csv = str(int(start_time)),
            stop_time_csv = str(int(stop_time)),
            sr = 16000,
            verbose = True,
            formatted = False,
            output_video_flag = True,
            times_as_integers = False)

if __name__ == "__main__":
    input_folders = [Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\TestSet\00_Single_videos'),
                     Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\VAD_aolme\LongAudios_IrmaAllan_VAD'),
                     Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\01_Long_videos\G-C2L1P-Mar08-D-Chaitu_q2_02-05'),  
                     Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\01_Long_videos\G-C3L1P-Mar21-A-Venkatesh_q2_02-05'),  
                     Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\01_Long_videos\G-C3L1P-Apr11-C-Phuong_q2_02-05'),  
                     Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\01_Long_videos\G-C3L1P-Mar21-B-Jenny_q2_02-06'),  
                     Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\01_Long_videos\G-C2L1P-Apr12-A-Allan_q2_03-05'),  
                     Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\01_Long_videos\G-C2L1P-Apr12-E-Krithika_q2_03-06'),  
                     Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\01_Long_videos\G-C2L1P-Apr12-B-Liz_q2_03-05')]

    output_folder_mp4 = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\VAD_aolme\random_40s_clips\video_mp4')
    output_folder_wavs = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\VAD_aolme\random_40s_clips\wav_clips')

    main(input_folders, output_folder_mp4, output_folder_wavs)





















