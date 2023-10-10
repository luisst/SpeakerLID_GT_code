from pathlib import Path

# Get the current working directory
current_directory = Path.cwd()

# List all files in the current directory with a .wav extension
wav_files = list(current_directory.glob('*.wav'))

# Iterate through the WAV files and rename them
for index, wav_file in enumerate(wav_files):
    new_name = f'noises_{index:04d}.wav'  # Generate the new name with a 4-digit index and .wav extension
    wav_file.rename(current_directory / new_name)

print("WAV files renamed successfully.")
