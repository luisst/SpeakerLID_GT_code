import os
import shutil
from pathlib import Path

def move_files_from_list(file_list_path, src_folder, dst_folder):
    # Make sure destination folder exists
    os.makedirs(dst_folder, exist_ok=True)

    with open(file_list_path, 'r') as f:
        filenames = [line.strip() for line in f if line.strip()]

    for filename in filenames:
        src_path = os.path.join(src_folder, filename)
        dst_path = os.path.join(dst_folder, filename)

        # Count how many files have the 'single' prefix
        if "single" in filename.lower():
            prefix_count = sum(1 for f in os.listdir(src_folder) if f.startswith("single"))
            print(f"Prefix 'single' found in {prefix_count} files.")
        
        # Count how many files have the 'double' prefix
        if "overlap" in filename.lower():
            prefix_count = sum(1 for f in os.listdir(src_folder) if f.startswith("overlap"))
            print(f"Prefix 'overlap' found in {prefix_count} files.")

        if os.path.exists(src_path):
            shutil.move(src_path, dst_path)
            print(f"Moved: {filename}")
        else:
            print(f"File not found: {filename}")

# Example usage
if __name__ == "__main__":
    file_list = Path(r"C:\Users\luis2\Dropbox\SpeechFall2022\SpeakerLID_GT_code\likely_silent_wavs_5percent.txt")
    source_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\DoubleTalk\double_talk_dataset7")
    destination_folder = source_folder.parent / "silent_files" 

    move_files_from_list(file_list, source_folder, destination_folder)
