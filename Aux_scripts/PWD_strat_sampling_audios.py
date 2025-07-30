import random
import shutil
import sys
from pathlib import Path
from collections import defaultdict

def extract_label_processed(wav_filename):
    parts = wav_filename.stem.split("_")
    if len(parts) < 2:
        print(f"Skipping file with unexpected format: {wav_filename.name}")
        sys.exit("Unexpected file format. Expected 'ID-XX_...' format.")
    speaker_id = f"ID-{parts[1][-2:]}"  # Take last 2 characters of second substring
    return speaker_id

def extract_label_raw(wav_filename):
    parts = wav_filename.stem.split("_")
    if len(parts) < 4:
        print(f"Skipping file with unexpected format: {wav_filename.name}")
        sys.exit("Unexpected file format. Expected 'ID-XX_...' format.")
    speaker_id = parts[1] + parts[2]
    return speaker_id

def stratified_sample_by_speaker(input_path: Path, M: int):
    output_path = input_path / "stratified_samples"
    output_path.mkdir(exist_ok=True)
    # Group files by speaker ID
    speaker_dict = defaultdict(list)

    for wav_file in input_path.glob("*.wav"):
        # speaker_id = extract_label_processed(wav_file)
        speaker_id = extract_label_raw(wav_file)
        speaker_dict[speaker_id].append(wav_file)


    total_copied = 0
    for speaker_id, files in speaker_dict.items():
        sample_count = min(M, len(files))
        selected = random.sample(files, sample_count)

        for wav_file in selected:
            shutil.copy(wav_file, output_path / wav_file.name)
            total_copied += 1

    print(f"Copied {total_copied} wav files into '{output_path}' from {len(speaker_dict)} speakers.")

# Example usage:
# stratified_sample_by_speaker("path/to/your/input_folder", 3)

if __name__ == "__main__":
    # current_folder = Path.cwd()
    # current_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\TTS3_dt\input_TTS3_chopped_all")
    current_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\TTS3_dt\input_raw_TTS3_wavs")
    stratified_sample_by_speaker(current_folder, 6)