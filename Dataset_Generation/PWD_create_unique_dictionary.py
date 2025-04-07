from pathlib import Path
import sys
import shutil

def get_wav_filenames(current_dir):
    wav_files = [file.name for file in current_dir.glob('*.wav')]
    return wav_files


def extract_speaker_name(filename):
    parts = filename[15:].split('_', 1)  # Extract from 10th position and split at first underscore
    output_name = ''
    if parts:
        output_name = parts[0]
    else:
        output_name = ''
        sys.exit(f'Error: Could not extract speaker name from filename: {filename}')  # Exit if no speaker name found
            
    return output_name


def get_speaker_dict(input_wav_folder):
    wav_filenames = get_wav_filenames(input_wav_folder)
    all_speaker_names = []

    for filename in wav_filenames:
        all_speaker_names.append(extract_speaker_name(filename))

    unique_speaker_names = set(all_speaker_names)

    ## Create a dictionary with unique speaker names and their corresponding speaker IDs
    speaker_dict = {speaker: f'{i:02d}' for i, speaker in enumerate(unique_speaker_names)}   

    return speaker_dict


if __name__ == "__main__":

    wavs_dir = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\interviews_wavs\All_dialogues_output')  # Current directory
    output_wavs_dir = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\interviews_wavs\TTS_ready_interviews')  # Current directory

    speaker_dict_ID = get_speaker_dict(wavs_dir)

    print(speaker_dict_ID)

    ## Copy wav files to new directory with unique speaker IDs
    for wav_file in get_wav_filenames(wavs_dir):
        speaker_name = extract_speaker_name(wav_file)
        current_file_number = wav_file.split('_')[-1].split('.')[0]
        speaker_ID = speaker_dict_ID[speaker_name]

        new_wav_file = output_wavs_dir / f'IC-{speaker_name}_ID-{speaker_ID}_{current_file_number}.wav'

        # Copy file to new directory
        shutil.copy(wavs_dir / wav_file, new_wav_file)

    

