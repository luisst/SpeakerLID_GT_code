from pathlib import Path
import re

def rename_wav_files(folder_path):
    folder = Path(folder_path)
    
    for file in folder.glob("*.wav"):
        match = re.match(r"(IC-[^_]+_ID-\d+_)(\d{4})(\.wav)", file.name)
        if match:
            new_name = f"{match.group(1)}0{match.group(2)}{match.group(3)}"
            new_file = file.with_name(new_name)
            file.rename(new_file)
            print(f"Renamed: {file.name} -> {new_name}")

if __name__ == "__main__":
    folder_path = r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\interviews_wavs\TTS_ready_interviews'
    rename_wav_files(folder_path)
