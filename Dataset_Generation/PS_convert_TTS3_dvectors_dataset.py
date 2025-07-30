import csv
import subprocess
from pathlib import Path

# Set paths
root_folder = Path.home().joinpath("Dropbox", "DATASETS_AUDIO")
csv_folder = root_folder / "Dvectors" / "noisy_16K" / "gt_csv"
wav_folder = root_folder / "Dvectors" / "noisy_16K" / "long_wavs"
output_folder = wav_folder.parent / "input_wavs" 
output_folder.mkdir(parents=True, exist_ok=True)

# Global index counter
global_index = 0

# Process each CSV file
for csv_file in sorted(csv_folder.glob("*.csv")):
    stem = csv_file.stem
    wav_file = wav_folder / f"{stem}.wav"
    if not wav_file.exists():
        print(f"Warning: WAV file not found for {stem}")
        continue

    # Read the CSV (tab-separated, no header)
    with csv_file.open("r", newline='') as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) != 5:
                print(f"Skipping malformed row in {csv_file}: {row}")
                continue
            speaker_id, lang, start_time, end_time, _ = row
            output_filename = f"{stem}_{speaker_id}_{global_index}.wav"
            output_path = output_folder / output_filename

            # Use ffmpeg to extract the segment
            cmd = [
                "ffmpeg", "-y",
                "-i", str(wav_file),
                "-ss", start_time,
                "-to", end_time,
                "-c", "copy",
                str(output_path)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            global_index += 1

print("Extraction complete.")
