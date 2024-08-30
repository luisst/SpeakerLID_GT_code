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


# Function to convert MPEG to MP4 using ffmpeg
def convert_mpeg_to_mp4(input_file, destination_file):
    # Check if input file exists
    if not input_file.exists():
        print(f"Input file '{input_file}' does not exist.")
        return

    mp4_command = [
        "ffmpeg",
        "-i", str(input_file),  # Input file
        "-c:v", "libx264",  # Video codec
        "-c:a", "aac",  # Audio codec
        "-strict", "experimental",
        str(destination_file)
    ]

    try:
        subprocess.run(mp4_command, check=True)
        print(f"Conversion of '{input_file}' successful!")
    except subprocess.CalledProcessError as e:
        print(f"Error converting '{input_file}': {e}")


input_folder = Path.cwd()
output_folder_audio = input_folder / "input_wavs"
output_folder_video = input_folder / "input_mp4"

# Create output folder if it doesn't exist
output_folder_audio.mkdir(parents=True, exist_ok=True)
output_folder_video.mkdir(parents=True, exist_ok=True)

# Iterate over each WAV file in the input folder
for input_file in input_folder.glob("*.mpeg"):
    output_file_video = output_folder_video / input_file.name
    convert_mpeg_to_mp4(input_file, output_file_video)
    print(f"\n\n\t\tConverted {input_file.name} to {output_file_video.name}")

    # output_file_audio = output_folder_audio / input_file.name
    # convert_audio(input_file, output_file_audio)
    # print(f"\n\n\t\tConverted {input_file.name} to {output_file_audio.name}")
