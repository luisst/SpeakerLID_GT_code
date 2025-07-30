from pathlib import Path
import shutil

def process_audio_files(input_folder: Path, output_folder: Path):
    # Ensure the output directory exists
    output_folder.mkdir(exist_ok=True)

    # Get all .wav files
    wav_files = list(input_folder.glob("*.wav"))

    for index, wav_file in enumerate(wav_files, start=1):
        # Split the filename into parts
        parts = wav_file.stem.split("_")
        if len(parts) < 2:
            print(f"Skipping file (unexpected format): {wav_file.name}")
            continue
        
        speaker = parts[-4]
        new_filename = f"Aolme_{speaker}_{index:04d}.wav"
        new_filepath = output_folder / new_filename

        # Copy the file to the new location
        shutil.copy2(wav_file, new_filepath)
        print(f"Copied: {wav_file.name} -> {new_filename}")

# Example usage
# input_dir = Path.cwd()     # Replace with your actual input folder

input_dir = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Dvectors\wavs_test_pairs\aolme_fix_input_wavs")     # Replace with your actual input folder
output_dir = input_dir / "simplified_audio_files"  # Output folder
process_audio_files(input_dir, output_dir)
