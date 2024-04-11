from pathlib import Path

def count_wav_files(directory='.'):
    count = 0
    directory_path = Path(directory)
    for file in directory_path.rglob('*.wav'):
        count += 1
    return count

if __name__ == "__main__":
    folder_path = Path.cwd()  # Set folder_path to the current working directory
    num_wav_files = count_wav_files(folder_path)

    print(f"Number of .wav files: {num_wav_files}")
