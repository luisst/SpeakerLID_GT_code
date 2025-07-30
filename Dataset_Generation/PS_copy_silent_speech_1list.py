import os
import shutil
from pathlib import Path

# === Hardcoded Paths ===
root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO') 
single_folder = root_dir / "TTS3_dt" / "output_chunks"
single_list_path = single_folder / "speech_single10perc.txt"
result_folder = root_dir / "TTS4_dvec" / "TTS4_input_wavs" 

# === Ensure result folder exists ===
os.makedirs(result_folder, exist_ok=True)


keep_perc = 90

# === Read file lists ===
with open(single_list_path, "r") as f:
    single_files = [line.strip() for line in f]


# Calculate 90% of overlap files
num_files = int(len(single_files) * keep_perc / 100)

print(f"Selecting {num_files} files from {len(single_files)} total single speech files.")

selected_single_speech = single_files[:num_files]


# Speech files
for filename in selected_single_speech:
    src = os.path.join(single_folder, filename)
    dst = os.path.join(result_folder, filename)
    shutil.copy2(src, dst)

print(f"Copied {num_files} overlap|single files to {result_folder}")
