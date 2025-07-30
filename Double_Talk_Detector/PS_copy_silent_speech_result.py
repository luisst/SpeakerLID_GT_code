import os
import shutil
from pathlib import Path

# === Hardcoded Paths ===
root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/TTS3_dt/overlapping_gt/output_segments10') 
single_list_path = root_dir / "speech_single10perc.txt"
overlap_list_path = root_dir / "speech_overlap10perc.txt"

result_folder = root_dir / "dataset10"

# === Ensure result folder exists ===
os.makedirs(result_folder, exist_ok=True)

overlap_folder = root_dir / "overlap10"  # Folder containing overlap files 
single_folder = root_dir / "single10"  # Folder containing single files

overlap_keep_perc = 90

# === Read file lists ===
with open(single_list_path, "r") as f:
    single_files = [line.strip() for line in f]

with open(overlap_list_path, "r") as f:
    overlap_files = [line.strip() for line in f]


# Calculate 90% of overlap files
num_files = int(len(overlap_files) * overlap_keep_perc / 100)
print(f"Number of overlap files to keep: {num_files}, from {len(overlap_files)} total files")

# Select top-N from overlap file list
selected_overlap_speech = overlap_files[:num_files]

selected_single_speech = single_files[:num_files]


# === Copy files ===
# Overlap files
for filename in selected_overlap_speech:
    src = os.path.join(overlap_folder, filename)
    dst = os.path.join(result_folder, filename)
    shutil.copy2(src, dst)

# Speech files
for filename in selected_single_speech:
    src = os.path.join(single_folder, filename)
    dst = os.path.join(result_folder, filename)
    shutil.copy2(src, dst)

print(f"Copied {num_files} overlap|single files to {result_folder}")
