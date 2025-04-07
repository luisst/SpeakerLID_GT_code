import re
import csv
import glob
from pathlib import Path
from pydub import AudioSegment

def extract_speaker(filename):
    match = re.search(r'IC-(.*?)_ID-\d+', filename)
    return match.group(1) if match else None

def process_audio_files(input_path, output_path):
    output_path.mkdir(parents=True, exist_ok=True)
    
    speakers_dict = {}
    
    # Group files by speaker
    for filepath in input_path.glob("*.wav"):
        speaker = extract_speaker(filepath.name)
        if speaker:
            if speaker not in speakers_dict:
                speakers_dict[speaker] = []
            speakers_dict[speaker].append(filepath)
            # speakers.setdefault(speaker, []).append(filepath)
    
    silence = AudioSegment.silent(duration=2000)  # 2 seconds of silence
    
    # Process each speaker
    for speaker, files in speakers_dict.items():
        combined_audio = AudioSegment.silent(duration=0)
        metadata = []
        current_time = 0.0
        
        for filepath in sorted(files):
            audio = AudioSegment.from_wav(filepath)
            start_time = current_time
            end_time = start_time + len(audio) / 1000.0  # Convert ms to seconds
            
            metadata.append([filepath.name, start_time, end_time])
            combined_audio += audio + silence
            current_time = end_time + 2  # Adding 2 seconds gap
        
        output_wav = output_path / f"{speaker}_combined.wav"

        # # Export combined audio to WAV at float32 format
        # combined_audio.export(output_wav, format="wav")
        
        output_csv = output_path / f"{speaker}_metadata.csv"
        with output_csv.open(mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["filename", "start_time", "end_time"])
            writer.writerows(metadata)
        
        print(f"Processed: {output_wav} and {output_csv}")

# Example usage
input_folder = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\SD_interviews_TTS3\TTS_long')
output_folder = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\SD_interviews_TTS3\TTS_long\output_combined2')

process_audio_files(input_folder, output_folder)
