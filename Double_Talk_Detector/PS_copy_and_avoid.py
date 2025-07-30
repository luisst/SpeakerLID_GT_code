import random
import shutil
from pathlib import Path

# Set folder paths
folder_A = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\DoubleTalk\filtered_singles7")
txt_B = Path(r"C:\Users\luis2\Dropbox\SpeechFall2022\SpeakerLID_GT_code\likely_silent_wavs_10percent7.txt")
output_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\DoubleTalk\tocopy7")

# Create output directory if it doesn't exist
output_folder.mkdir(parents=True, exist_ok=True)

# Collect filenames from csv file txt_B
# Assuming the file contains one filename per line
with open(txt_B, "r") as f:
    excluded_filenames = [line.strip() for line in f.readlines()] 

# Filter eligible .wav files from folder_A
eligible_files = [f for f in folder_A.glob("*.wav") if f.name not in excluded_filenames]

# Make sure we don't try to sample more files than are available
sample_size = min(438, len(eligible_files))
selected_files = random.sample(eligible_files, sample_size)

# Copy selected files to output folder
for file in selected_files:
    shutil.copy(file, output_folder / file.name)

# Print results
print(f"Copied {len(selected_files)} files to {output_folder.resolve()}")
