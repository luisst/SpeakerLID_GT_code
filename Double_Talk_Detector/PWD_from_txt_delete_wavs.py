import os
from pathlib import Path

def delete_wav_files_from_list(list_path, folder_path):
    # Read list of .wav files from the text file
    with open(list_path, 'r') as f:
        wav_files_to_delete = [line.strip() for line in f if line.strip()]
    
    missing_files = []
    
    for wav_file in wav_files_to_delete:
        current_wav_file = wav_file + '.wav'
        file_path = os.path.join(folder_path, current_wav_file)
        
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        else:
            missing_files.append(current_wav_file)
    
    if missing_files:
        raise FileNotFoundError(f"The following files were not found in '{folder_path}':\n" +
                                "\n".join(missing_files))

# Example usage
current_folder = Path.cwd()
delete_wav_files_from_list('files_to_delete_300.txt', current_folder)
