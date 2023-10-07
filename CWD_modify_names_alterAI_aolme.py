from pathlib import Path
import re

# Define the folder containing the WAV files
folder_path = Path.cwd()

# Define a regular expression pattern to match the input filenames
pattern = r'Phuong_Apr11_C_q2_(\d{2})-05_E(\d{5})\.(\d+)\.(\w+)\.Timbre-2\.5'

# Iterate over the WAV files in the folder
for idx_file, input_file in enumerate(folder_path.glob('*.wav')):
    # Extract information from the input filename using the regex pattern
    match = re.match(pattern, input_file.stem)
    if match:
        session_number, segment_number, _,  speaker_name = match.groups()

        # Generate the new filename using the provided pattern
        output_filename = f'S-C3L1P-Apr11-C-Phuong_q2_{session_number}-05-segment_{segment_number.zfill(3)}_{speaker_name}_{str(idx_file).zfill(5)}.wav'
        output_file = input_file.with_name(output_filename)

        # Rename the file
        input_file.rename(output_file)
        print(f'\nRenamed: {input_file.name} -> {output_file.name}\n')
    else:
        print(f'Skipped: {input_file.name} (Invalid format)')

print("Done.")

