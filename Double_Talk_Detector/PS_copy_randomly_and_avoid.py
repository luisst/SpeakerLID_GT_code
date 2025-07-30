import random
import shutil
from pathlib import Path

# Set folder paths
folder_A = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\DoubleTalk\output_segments7\single7")
folder_B = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\DoubleTalk\double_talk_dataset7")
folder_C = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\DoubleTalk\silent_files")
output_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\DoubleTalk\filtered_singles7")

# Create output directory if it doesn't exist
output_folder.mkdir(parents=True, exist_ok=True)

# Collect filenames from folder_B and folder_C
excluded_filenames = {f.name for f in folder_B.glob("*.wav")} | {f.name for f in folder_C.glob("*.wav")}

# Filter eligible .wav files from folder_A
eligible_files = [f for f in folder_A.glob("*.wav") if f.name not in excluded_filenames]

# Make sure we don't try to sample more files than are available
sample_size = min(5000, len(eligible_files))
selected_files = random.sample(eligible_files, sample_size)

# Copy selected files to output folder
for file in selected_files:
    shutil.copy(file, output_folder / file.name)

# Print results
print(f"Copied {len(selected_files)} files to {output_folder.resolve()}")

# Optionally save the list
with open("selected_wavs.txt", "w") as out_file:
    for file in selected_files:
        out_file.write(str(output_folder / file.name) + "\n")
