import os
from pathlib import Path

# Get the current working directory as the folder path
folder_path = Path.cwd()


index = 0
# Iterate over all files in the folder
for file_path in folder_path.glob("*.wav"):
    # Extract the filename from the file path
    filename = os.path.basename(file_path)

    # Extract the codename and index from the filename
    parts = filename.split("_")
    codename = parts[-2]

    # Create the new filename
    new_filename = f"{codename}_{str(index).zfill(4)}.wav"

    index = index + 1

    # Rename the file with the new filename
    os.rename(file_path, os.path.join(folder_path, new_filename))
