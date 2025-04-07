from pathlib import Path

# Get the current working directory
current_directory = Path.cwd()

# Iterate over all the WAV files in the current directory
for file_path in current_directory.glob('*.wav'):
    new_stem = file_path.stem.replace('June28', 'jun28')
    new_file_path = current_directory / (new_stem + file_path.suffix)
    
    # Rename the file
    file_path.rename(new_file_path)
    print(f'Renamed "{file_path.name}" to "{new_file_path.name}"')


print('File renaming completed.')