import numpy as np
import soundfile as sf
from pathlib import Path

# Function to calculate the RMS gain of an audio signal
def calculate_rms_gain(audio):
    return np.sqrt(np.mean(np.square(audio)))

# Function to modify the gain of an audio signal to match a desired RMS gain
def modify_audio_gain(audio, desired_gain):
    current_gain = calculate_rms_gain(audio)
    scale_factor = desired_gain / current_gain
    return audio * scale_factor


def list_folders(path, not_folder = None):
    """
    Given a pathlib path, list all paths of folders inside it.
    """
    folders = []
    for item in path.iterdir():
        if item.is_dir() and item != not_folder:
            folders.append(item)
            folders += list_folders(item)
    return folders

# Get list of audio files in the master folder
root_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO','WAV_TTS','Sound_effects','output_WAVS')
# master_folder = root_folder.joinpath('WAV_E1_typing')

# master for E2
master_folder = root_folder.joinpath('WAV_E2_fasttyping')
master_files = list(master_folder.glob('*.wav'))

# Calculate average RMS gain of master audio files
master_rms_gains = []
for file in master_files:
    audio, _ = sf.read(file)
    rms_gain = calculate_rms_gain(audio)
    master_rms_gains.append(rms_gain)

avg_master_rms_gain = np.mean(master_rms_gains)
print(f"Average RMS gain of master audio files: {avg_master_rms_gain}")

# Loop over all other folders and modify audio files to have the same RMS gain as the master files
other_folders_E1 = [root_folder.joinpath('WAV_E1_drawing'),
                 root_folder.joinpath('WAV_E1_highlighting'),
                 root_folder.joinpath('WAV_E1_pen'),
                 root_folder.joinpath('WAV_E1_sharpie')] 

other_folders_E2 = [root_folder.joinpath('WAV_E2_tapping'),
                 root_folder.joinpath('WAV_E2_book'),
                 root_folder.joinpath('WAV_E2_scratching')] 

other_all = list_folders(root_folder, master_folder)

for folder in other_folders_E2:
    files = list(folder.glob('*.wav'))
    current_rms_gain_list = []
    for file in files:
        audio, sr = sf.read(file)
        rms_gain = calculate_rms_gain(audio)
        current_rms_gain_list.append(rms_gain)

        modified_audio = modify_audio_gain(audio, avg_master_rms_gain)
        sf.write(file, modified_audio, sr)

    avg_rms_gain = np.mean(current_rms_gain_list)
    print(f"Average RMS {folder.name}: {avg_rms_gain:.4f}")

# Print RMS after
for folder in other_folders_E2:
    files = list(folder.glob('*.wav'))
    current_rms_gain_list = []
    for file in files:
        audio, sr = sf.read(file)
        rms_gain = calculate_rms_gain(audio)
        current_rms_gain_list.append(rms_gain)

    avg_rms_gain = np.mean(current_rms_gain_list)
    print(f"After RMS {folder.name}: {avg_rms_gain:.4f}")
