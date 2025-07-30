import subprocess
from pathlib import Path
import shutil

def get_audio_duration(file_path):
    """Get the duration of the audio file using ffmpeg."""
    result = subprocess.run([
        "ffprobe", "-i", str(file_path), "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"
    ], capture_output=True, text=True)
    return float(result.stdout.strip())

def split_audio(file_path, output_folder, threshold=1.0, tolerance=0.3, min_chunk_duration=0.7):
    """Split the audio file into smaller chunks based on the threshold."""
    duration = get_audio_duration(file_path)

    # Skip files that are shorter than the minimum chunk duration
    if duration < min_chunk_duration:
        print(f"Skipping {file_path.name}, duration {duration:.2f}s")
        return
    
    # Copy file duration larger than min_chunk_duration and smaller than threshold
    if duration < threshold:
        output_file = output_folder / f"{file_path.stem}_P00.wav"
        shutil.copy2(file_path, output_file)
        print(f"Copied: {output_file.name}, Duration: {duration:.2f}s")
        return

    
    if duration <= threshold + tolerance:
        output_file = output_folder / f"{file_path.stem}_P00.wav"
        shutil.copy2(file_path, output_file)
        # print(f"Copied: {output_file.name}, Duration: {duration:.2f}s")
        return
    
    segments = []
    start = 0.0
    
    while start < duration:
        remaining = duration - start
        if remaining < min_chunk_duration:
            if segments:
                last_start, last_end = segments.pop()
                segments.append((last_start, duration))
            else:
                segments.append((start, duration))
            break
        
        # Select a segment length equal to the threshold
        segment_length = threshold
        
        end = min(start + segment_length, duration)
        segments.append((start, end))
        start = end
    
    for i, (start, end) in enumerate(segments):
        part_num = f"_P{(i):02d}"
        output_file = output_folder / f"{file_path.stem}{part_num}.wav"
        
        cmd = [
            "ffmpeg", "-i", str(file_path), "-ss", f"{start:.2f}", "-to", f"{end:.2f}",
            "-c", "copy", str(output_file), "-y"
        ]
        subprocess.run(cmd, stderr=subprocess.DEVNULL)
        segment_duration = end - start
        # print(f"Saved: {output_file.name}, Duration: {segment_duration:.2f}s")


def process_folder(input_folder, output_folder):
    """Process all WAV files in the input folder."""
    
    output_folder.mkdir(parents=True, exist_ok=True)
    for file_path in input_folder.glob("*.wav"):
        split_audio(file_path, output_folder, threshold=1.0, tolerance=0.3, min_chunk_duration=0.7)

if __name__ == "__main__":

    root_folder = Path.home().joinpath('Dropbox','DATASETS_AUDIO')
    input_folder = root_folder / 'TTS3_dt' / 'reviewed_raw_TTS3_input' / 'output_uniform_gain'

    output_folder = input_folder / 'output_chunks'
    process_folder(input_folder, output_folder)
