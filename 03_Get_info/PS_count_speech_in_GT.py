from pathlib import Path

from utilities_functions import find_audio_duration

# Root of all results
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','Sample_dataset','All_results')
audios_folder = root_dir.parent
suffix_added = 'done_ready'

# Load GT list:
GT_pth = root_dir.parent.joinpath('GT','final_csv')

folder_transcript_list = sorted(list(GT_pth.glob('*.csv')))
folder_transcript_list.extend(sorted(list(GT_pth.glob('*.txt'))))

total_speech = 0
total_duration = 0
for current_transcript in folder_transcript_list:
    # use the matching to obtain the duration
    current_audio_duration = find_audio_duration(current_transcript, audios_folder, suffix_added)

    with open(current_transcript) as f:
        lines = [line.rstrip() for line in f]
    
    ############ This varies on the format
    # Src	StartTime	EndTime
    # s0s0	3.93	5.86
    lines.pop(0)

    speech_counter = 0
    for line in lines:
        SpeakerLang, start_time, stop_time = line.split('\t')
        speech_counter = speech_counter + float(stop_time) - float(start_time)
    
    total_speech = total_speech + speech_counter
    total_duration = total_duration + current_audio_duration
    
    print(f'\nNow processing: {current_transcript.name}\tspeech: {speech_counter:.2f} | total: {current_audio_duration:.2f}')

print(f'\n\nTotal Speech: {total_speech:.2f} | Total Audio Duration: {total_duration:.2f}')

        