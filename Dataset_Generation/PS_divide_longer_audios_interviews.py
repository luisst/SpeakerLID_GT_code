import subprocess
import random
from pathlib import Path
import math

def get_audio_duration(file_path):
    """Get the duration of the audio file using ffmpeg."""
    result = subprocess.run([
        "ffprobe", "-i", str(file_path), "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"
    ], capture_output=True, text=True)
    return float(result.stdout.strip())

def split_audio(file_path, output_folder, threshold=6, tolerance=2):
    """Split the audio file into smaller chunks based on the threshold."""
    duration = get_audio_duration(file_path)
    
    if duration <= threshold + tolerance:
        print(f"Skipping {file_path.name}, duration {duration:.2f}s is within tolerance.")
        output_file = output_folder / f"{file_path.stem}_P00.wav"
        cmd = [
            "ffmpeg", "-i", str(file_path), "-c", "copy", str(output_file), "-y"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Copied: {output_file.name}, Duration: {duration:.2f}s")
        return
    
    output_folder.mkdir(parents=True, exist_ok=True)
    segments = []
    start = 0.0
    
    while start < duration:
        remaining = duration - start
        if remaining <= threshold:
            if segments:
                last_start, last_end = segments.pop()
                segments.append((last_start, duration))
            else:
                segments.append((start, duration))
            break
        
        max_segment = min(threshold + tolerance, remaining)
        segment_length = random.uniform(threshold, max_segment)
        
        end = min(start + segment_length, duration)
        segments.append((start, end))
        start = end
    
    for i, (start, end) in enumerate(segments):
        part_num = f"_P{(i+1):02d}"
        output_file = output_folder / f"{file_path.stem}{part_num}.wav"
        
        cmd = [
            "ffmpeg", "-i", str(file_path), "-ss", f"{start:.2f}", "-to", f"{end:.2f}",
            "-c", "copy", str(output_file), "-y"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segment_duration = end - start
        print(f"Saved: {output_file.name}, Duration: {segment_duration:.2f}s")


def process_folder(input_folder, output_folder):
    """Process all WAV files in the input folder."""
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    
    for file_path in input_folder.glob("*.wav"):
        split_audio(file_path, output_folder)

if __name__ == "__main__":
    input_folder = Path(r'/home/luis/Dropbox/DATASETS_AUDIO/TTS3_lalal/TTS3_filtered_voice')
    output_folder = Path(r'/home/luis/Dropbox/DATASETS_AUDIO/TTS3_lalal/input_TTS3_wavs')
    process_folder(input_folder, output_folder)
