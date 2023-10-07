from pathlib import Path

folder_path = Path.cwd()


for file_path in folder_path.iterdir():
    if file_path.suffix == ".wav":
        if "-" in file_path.name:
            old_path = file_path
            new_filename = file_path.name.replace("-", "_")
            new_path = file_path.with_name(new_filename)
            old_path.rename(new_path)
            print(f"Renamed {old_path} to {new_path}")
        else:
            print(f"Skipping {file_path.name} - no dash found")
    else:
        print(f"Skipping {file_path.name} - not a WAV file")
