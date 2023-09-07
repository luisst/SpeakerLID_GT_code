import wave
import numpy as np
from pathlib import Path

# Set the root folder as the current working directory
root_folder = Path.cwd()

# Get a list of all subfolders within the root folder
subfolders = [folder for folder in root_folder.iterdir() if folder.is_dir()]

# Process each subfolder
for folder_path in subfolders:
    # Get a list of all WAV files in the subfolder
    audio_files = list(folder_path.glob("*.wav"))

    # Create an empty list to store the audio data
    audio_data = []

    # Read and append the audio data from each file
    for file in audio_files:
        with wave.open(str(file), 'rb') as wav:
            # Check audio format compatibility
            if wav.getsampwidth() != 2 or wav.getcomptype() != 'NONE':
                print(f"Skipping file {file} due to unsupported format.")
                continue

            # Read audio data and convert to PCM_16
            frames = wav.readframes(wav.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16)
            audio_data.append(audio)

    # Concatenate the audio data
    result_audio = np.concatenate(audio_data)

    # Create a new WAV file for the concatenated audio in the subfolder
    output_path = folder_path / "output.wav"
    with wave.open(str(output_path), 'wb') as wav_out:
        # Set the audio parameters
        wav_out.setnchannels(1)  # Mono
        wav_out.setsampwidth(2)  # PCM_16
        wav_out.setframerate(16000)  # Sample rate
        wav_out.writeframes(result_audio.tobytes())

    print(f"Concatenation complete for subfolder: {folder_path}")

print("Processing of all subfolders complete.")
