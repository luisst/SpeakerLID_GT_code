from pathlib import Path

# Set the base name and initialize an index
base_name = 'TTS2_audios'
index = 0

# Get the current working directory
current_directory = Path.cwd()

# Find all WAV files in the current directory
wav_files = sorted(current_directory.glob('*.wav'))

# Rename and move the WAV files
for wav_file in wav_files:
    new_name = f'{base_name}_{index:04d}.wav'
    wav_file.rename(current_directory / new_name)
    index += 1

print("WAV files have been renamed and sorted.")
