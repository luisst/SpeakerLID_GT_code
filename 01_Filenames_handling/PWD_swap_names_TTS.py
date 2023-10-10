from pathlib import Path

# Get the current working directory
current_directory = Path.cwd()

# Iterate over all the WAV files in the current directory
for file_path in current_directory.glob('*.wav'):
    # Split the file name into parts
    parts = file_path.stem.split('_')
    
    # Check if the filename has the expected format (DA-XXXX_YYYY.wav)
    if len(parts) == 2:
        part1, part2 = parts
        new_filename = f"{part1.split('-')[0]}-{part2}_{part1.split('-')[1]}.wav"
        
        # Create a new file path with the swapped parts
        new_file_path = current_directory.joinpath(new_filename)

        # IF A WORD NEEDS TO BE CHANGED
        # new_stem = file_path.stem.replace('noise', 'noises')
        # new_file_path = current_directory / (new_stem + file_path.suffix)
        
        # Rename the file
        file_path.rename(new_file_path)
        print(f'Renamed "{file_path.name}" to "{new_file_path.name}"')
    else:
        print(f'Skipped "{file_path.name}" as it does not have the expected format.')

print('File renaming completed.')