from pathlib import Path

def rename_files(directory, start_number):
    path = Path(directory)
    
    if not path.is_dir():
        print(f"Error: {directory} is not a valid directory.")
        return
    
    file_list = sorted(path.glob("*.wav"))  # Change the file extension to 'wav'
    
    for index, old_path in enumerate(file_list, start=start_number):
        new_name = f"group_background_noises_{index:04d}.wav"  # Change the format and extension to 'wav'
        new_path = path / new_name
        old_path.rename(new_path)
        print(f"Renamed {old_path.name} to {new_name}")

if __name__ == "__main__":
    starting_number = 300
    current_directory = Path.cwd()
    rename_files(current_directory, starting_number)
