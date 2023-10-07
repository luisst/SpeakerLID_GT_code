from pathlib import Path

# Root of all results
root_dir = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TTS_minitest')

# Load GT list:
GT_pth = root_dir.joinpath('GT')
pred_pth = root_dir.joinpath('inference')

base_name = "minitest_TTS"  # Replace with the new base name you want to use

for file_path in GT_pth.glob(f"*"):
    if file_path.is_file() and file_path.suffix == ".csv":
        old_path = file_path

        parts = file_path.stem.split("_") 
        new_filename = f"{base_name}_{parts[-1]}.csv"
        new_path = file_path.with_name(new_filename)
        old_path.rename(new_path)
        print(f"Renamed {old_path} to {new_path}")

print(f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> NEXT FOLDER')

for file_path in pred_pth.glob(f"*"):
    if file_path.is_file() and (file_path.suffix == ".csv" or file_path.suffix == ".txt"):
        old_path = file_path
        parts = file_path.stem.split("_")
        new_filename = f"{base_name}_{parts[-1]}.csv"
        new_path = file_path.with_name(new_filename)
        old_path.rename(new_path)
        print(f"Renamed {old_path} to {new_path}")
