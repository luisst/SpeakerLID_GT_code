import os
import shutil
import random
from pathlib import Path

# Set your source and destination folders here

root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/TTS3_dt/overlapping_gt/output_segments7')
x_folder = root_dir / "overlap7"
y_folder = root_dir / "dataset7"
number_of_files = 7202

# Ensure destination folder exists
os.makedirs(y_folder, exist_ok=True)

# Get a list of all files in the source folder
all_files = [f for f in os.listdir(x_folder) if os.path.isfile(os.path.join(x_folder, f))]

# Check that there are enough files
if len(all_files) < number_of_files:
    raise ValueError(f"Not enough files in source folder. Found {len(all_files)}, need 13029.")

# Randomly sample 13,029 files
sampled_files = random.sample(all_files, number_of_files)

# Copy the sampled files to the destination folder
for file_name in sampled_files:
    src_path = os.path.join(x_folder, file_name)
    dst_path = os.path.join(y_folder, file_name)
    shutil.copy2(src_path, dst_path)

print(f"Copied {number_of_files} files from '{x_folder}' to '{y_folder}'")
