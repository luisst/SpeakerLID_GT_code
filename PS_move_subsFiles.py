import shutil
import pathlib

# Define the parent directory path and iterate over all subdirectories
parent_dir = pathlib.Path.cwd()
for subdir in parent_dir.iterdir():
    # Check if the subdirectory is actually a directory and not a file
    if subdir.is_dir():
        # Iterate over all files in the subdirectory and move them to the parent directory
        for file in subdir.iterdir():
            if file.is_file() and file.suffix == '.wav':
                shutil.move(str(file), str(parent_dir))
