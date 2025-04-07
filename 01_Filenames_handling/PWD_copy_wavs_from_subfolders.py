from pathlib import Path
import shutil

def copy_wav_to_root():
    root = Path.cwd()
    subfolders = [f for f in root.iterdir() if f.is_dir()]
    
    wav_files = []
    for subfolder in subfolders:
        current_subfolder = subfolder / "audio"

        print(f'Now: {current_subfolder.name}')
        wav_files = list(current_subfolder.glob("*.wav"))
    
        if len(wav_files) == 1:
            wav_file = wav_files[0]
            destination = root / wav_file.name
            shutil.copy(wav_file, destination)
            print(f"Copied {wav_file} to {destination}")
        elif len(wav_files) > 1:
            print("Warning: More than one .wav file found.")
        else:
            print("No .wav file found.")

if __name__ == "__main__":
    copy_wav_to_root()
