from pathlib import Path

from utilities_functions import find_audio_duration

root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TestSet_for_VAD')
audios_folder = root_dir.joinpath('WAV_FILES')

suffix_added = ''
has_header = False
GT_pth = root_dir.joinpath('GT_csv')

folder_transcript_list = sorted(list(GT_pth.glob('*.csv')))
folder_transcript_list.extend(sorted(list(GT_pth.glob('*.txt'))))

total_speech = 0
total_duration = 0
for current_transcript in folder_transcript_list:
    current_audio_duration = find_audio_duration(current_transcript, audios_folder, suffix_added)

    with open(current_transcript) as f:
        lines = [line.rstrip() for line in f]

    if has_header:
        print(f'File has header: {current_transcript.name}')
        lines.pop(0)

    speech_counter = 0
    for line in lines:
        columns = line.split('\t')
        start_time, stop_time = columns[-2:]

        speech_counter += float(stop_time) - float(start_time)

    total_speech += speech_counter
    total_duration += current_audio_duration

    print(f'\nNow processing: {current_transcript.name}\tspeech: {speech_counter:.2f} | total: {current_audio_duration:.2f}')

print(f'\n\nTotal Speech: {total_speech:.2f} | Total Audio Duration: {total_duration:.2f}')
        