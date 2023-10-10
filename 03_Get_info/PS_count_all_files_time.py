import pathlib
from utilities_functions import calculate_duration_in_folder


def count_files(directory):
    count = 0
    total_time_folders = 0
    for path in directory.iterdir():
        if path.is_file():
            count += 1
        elif path.is_dir():
            current_time = calculate_duration_in_folder(path, wav_flag = True)
            total_time_folders = total_time_folders + current_time
            for subpath in path.iterdir():
                if subpath.is_file():
                    count += 1
    return count, total_time_folders






# Example usage:
directory_path = pathlib.Path.cwd()
file_count, total_time_folders  = count_files(directory_path)
print(f"Number of files: {file_count}")

total_min = total_time_folders/60
total_hours = total_min/60

print(f'The total seconds in this folder is: {total_time_folders:.2f}')
print(f'In minutes: {total_min:.2f} \t In hours: {total_hours:.2f}')