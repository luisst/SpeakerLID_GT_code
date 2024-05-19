import subprocess
from pathlib import Path

def convert_audio(input_file, output_file):
    # Check if input file exists
    if not input_file.exists():
        print(f"Input file '{input_file}' does not exist.")
        return
    
    # Define ffmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", str(input_file),
        "-ar", "16000",  # 16K sampling rate
        "-ac", "1",      # Mono channel
        "-acodec", "pcm_s16le",  # PCM16 codec
        str(output_file)
    ]
    
    # Execute ffmpeg command
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Conversion of '{input_file}' successful!")
    except subprocess.CalledProcessError as e:
        print(f"Error converting '{input_file}': {e}")



input_folder = Path.cwd()
output_folder = input_folder / "output_wavs_16k"

# Create output folder if it doesn't exist
output_folder.mkdir(parents=True, exist_ok=True)

# Iterate over each WAV file in the input folder
for input_file in input_folder.glob("*.wav"):
    output_file = output_folder / input_file.name
    convert_audio(input_file, output_file)