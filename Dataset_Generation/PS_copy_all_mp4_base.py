import shutil
from pathlib import Path

def move_mp4_files_to_folder(folder_path):
    """
    Moves all .mp4 files from subdirectories into the specified folder.

    :param folder_path: The target folder path where the .mp4 files will be moved.
    """
    # Convert the folder_path to a Path object
    target_folder = Path(folder_path)

    # Ensure the target folder exists
    if not target_folder.exists():
        print(f"The target folder {target_folder} does not exist.")
        return

    if not target_folder.is_dir():
        print(f"The path {target_folder} is not a directory.")
        return

    # Iterate through all subdirectories and find .mp4 files
    for mp4_file in target_folder.rglob("*.mp4"):
        if mp4_file.is_file():
            try:
                # Move each .mp4 file to the target folder
                destination = target_folder / mp4_file.name

                # Avoid overwriting existing files
                if destination.exists():
                    print(f"File {destination} already exists. Skipping.")
                else:
                    shutil.move(str(mp4_file), str(destination))
                    print(f"Moved {mp4_file} to {destination}")

            except Exception as e:
                print(f"Error moving {mp4_file}: {e}")

if __name__ == "__main__":
    folder_path = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\interviews_single")
    move_mp4_files_to_folder(folder_path)
