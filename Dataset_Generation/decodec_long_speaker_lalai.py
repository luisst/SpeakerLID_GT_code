import csv
import subprocess
from pathlib import Path

def get_speaker_name(filename):
    # return filename.stem.replace("_combined", "")
    return filename.stem.replace("_combined_bk", "")

def split_audio(input_wav, metadata_csv, output_folder):
    input_wav = Path(input_wav)
    metadata_csv = Path(metadata_csv)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    with metadata_csv.open(mode='r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip header row
        
        for row in reader:
            filename, start_time, end_time = row
            start_time = float(start_time)
            duration = float(end_time) - start_time
            bk_filename = "bk_" + filename
            # output_wav = output_folder / filename
            output_wav = output_folder / bk_filename
            
            command = [
                "ffmpeg", "-i", str(input_wav), "-ss", str(start_time), "-t", str(duration), "-acodec", "copy", str(output_wav)
            ]
            subprocess.run(command, check=True)
            print(f"Created: {output_wav}")

def process_folder(input_folder, output_folder):
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # combined_wavs = input_folder.glob("*_combined.wav")
    combined_wavs = input_folder.glob("*_combined_bk.wav")

    matched_files = []
    for combined_wav in combined_wavs:
        speaker = get_speaker_name(combined_wav)
        metadata_file = next(input_folder.glob(f"{speaker}_metadata.csv"), None)
        if metadata_file:
            matched_files.append((combined_wav, metadata_file, speaker))
        else:
            print(f"Metadata file not found for {combined_wav}")
    
    for wav_file, csv_file, speaker in matched_files:

        speaker_output_folder = output_folder / speaker
        speaker_output_folder.mkdir(parents=True, exist_ok=True)
        split_audio(wav_file, csv_file, speaker_output_folder)
        print(f"Processed: {wav_file} and {csv_file}")

# Example usage
input_folder = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\SD_interviews_TTS3\TTS_long\output_combined\Audios separados\no-voice') 
output_folder = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\SD_interviews_TTS3\TTS_long\output_combined\Audios separados\no-voice\all_noises') 
process_folder(input_folder, output_folder)
