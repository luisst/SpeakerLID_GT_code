from pathlib import Path
import shutil

# Parameters
folder_path = Path.cwd()
offset = 20
output_folder = folder_path / "renamed_files"

# Create the output folder if it doesn't exist
output_folder.mkdir(exist_ok=True)

# Copy and rename files
for wav_file in folder_path.glob("*.wav"):
    stem = wav_file.stem
    parts = stem.rsplit("_", 1)

    if len(parts) == 2 and parts[1].isdigit():
        base, index_str = parts
        new_index = int(index_str) + offset
        new_name = f"{base}_{new_index}{wav_file.suffix}"
        new_path = output_folder / new_name
        shutil.copy(wav_file, new_path)
        print(f"Copied {wav_file.name} -> {new_name}")