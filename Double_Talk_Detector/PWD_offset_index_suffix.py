from pathlib import Path

# Parameters
folder_path = Path.cwd()
offset = 120

# Rename files
for wav_file in folder_path.glob("*.wav"):
    stem = wav_file.stem
    parts = stem.rsplit("_", 1)

    if len(parts) == 2 and parts[1].isdigit():
        base, index_str = parts
        new_index = int(index_str) + offset
        new_name = f"{base}_{new_index}{wav_file.suffix}"
        new_path = wav_file.with_name(new_name)
        wav_file.rename(new_path)
        print(f"Renamed {wav_file.name} -> {new_name}")
