from pathlib import Path

# Set the path to your folder
folder = Path(r"/home/luis/Dropbox/DATASETS_AUDIO/Dvectors/wavs_test_pairs/input_feats")

my_ext = "pkl"  # Specify the file extension to look for

# Loop through all .pkl files
for file in folder.glob(f"*.{my_ext}"):
    if "_" in file.stem:
        index, speaker_id = file.stem.split("_")
        new_name = f"Aolme_{speaker_id}_{index}.{my_ext}"
        new_path = file.with_name(new_name)
        file.rename(new_path)
        print(f"Renamed: {file.name} -> {new_name}")
