from pathlib import Path
import pandas as pd
import subprocess

# Define folders
input_folder_csv = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\CHIME6\aolme_base\csv_input_folder")
long_wav_input = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\CHIME6\aolme_base\long_wavs_source")
output_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\CHIME6\aolme_base\wavs_dev_eval")

# Ensure output folder exists
output_folder.mkdir(parents=True, exist_ok=True)

# Process each CSV file
for csv_file in input_folder_csv.glob("*.csv"):
    try:
        # Read CSV file (tab-separated)
        df = pd.read_csv(csv_file, sep="\t")

        # Extract min start time and max end time
        min_start = df["Start_time"].min()
        max_end = df["End_time"].max()

        # Extract audio filename from Source column (assuming the same file is used for all rows)
        unique_sources = df["Source"].unique()
        if len(unique_sources) != 1:
            print(f"Warning: Multiple source files found in {csv_file.name}, using first one: {unique_sources[0]}")

        audio_filename = str(unique_sources[0]) + ".wav"
        audio_file = long_wav_input / audio_filename

        if not audio_file.exists():
            print(f"Audio file {audio_file} not found. Skipping...")
            continue

        # Define output file
        output_file = output_folder / (csv_file.stem + "_subsegment.wav")

        # Cut audio using ffmpeg
        cmd = [
            "ffmpeg",
            "-i", str(audio_file),
            "-ss", str(min_start),
            "-to", str(max_end),
            "-c", "copy",
            str(output_file)
        ]

        subprocess.run(cmd, check=True)
        print(f"Processed {csv_file.name} -> {output_file}")

        # Update CSV file to reflect the new time offsets
        df["Start_time"] = (df["Start_time"] - min_start).round(2)
        df["End_time"] = (df["End_time"] - min_start).round(2)
        df["Source"] = output_file.name  # Update source to the new audio file



        # Save updated CSV file
        updated_csv_file = output_folder / csv_file.name
        df.to_csv(updated_csv_file, sep="\t", index=False)
        print(f"Updated CSV saved as {updated_csv_file}")

    except Exception as e:
        print(f"Error processing {csv_file.name}: {e}")
