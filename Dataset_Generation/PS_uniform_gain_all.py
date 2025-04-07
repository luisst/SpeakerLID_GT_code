from pathlib import Path
from pydub import AudioSegment

# Set parameters
input_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\SD_interviews_TTS3\TTS_ready_interviews_nonUniform")
output_folder = input_folder / "output"
target_dBFS = -20.0  # Adjust target loudness as needed

# Ensure output folder exists
output_folder.mkdir(parents=True, exist_ok=True)

def normalize_audio(input_path, output_path, target_dBFS):
    """Normalize audio to the target dBFS level."""
    audio = AudioSegment.from_wav(input_path)
    change_in_dBFS = target_dBFS - audio.dBFS
    normalized_audio = audio.apply_gain(change_in_dBFS)
    normalized_audio.export(output_path, format="wav")

# Process all WAV files in the folder
for wav_file in input_folder.glob("*.wav"):
    output_path = output_folder / wav_file.name
    normalize_audio(wav_file, output_path, target_dBFS)
    print(f"Normalized: {wav_file.name}")

print("Volume normalization complete!")
