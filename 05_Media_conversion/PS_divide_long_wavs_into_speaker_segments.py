import subprocess
from pathlib import Path

# Set input and output directories (customize as needed)
input_dir = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\Dvectors\tts3_test_pairs\long_wavs')
output_dir = input_dir / 'segments'
output_dir.mkdir(exist_ok=True)

# Find all .tsv files (your CSVs are actually TSVs)
tsv_files = sorted(input_dir.glob("*.csv"))  # Or use *.tsv if you rename them

global_index = 0

for tsv_file in tsv_files:
    stem = tsv_file.stem
    wav_file = input_dir / f"{stem}.wav"

    if not wav_file.exists():
        print(f"Warning: WAV file for {tsv_file.name} not found.")
        continue

    with tsv_file.open('r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) != 5:
                print(f"Skipping malformed line: {line}")
                continue

            speaker_index, _, start_time, end_time, filename = parts

            # Extract speaker ID from filename
            try:
                speaker_id_raw = filename.split('_')[0]  # e.g., "IC-Ethan"
                speaker_id = speaker_id_raw[3:]  # remove "IC-"
            except Exception as e:
                print(f"Error parsing speaker_id from '{filename}': {e}")
                continue

            start = float(start_time)
            duration = float(end_time) - float(start_time)

            # Output file name
            out_name = f"tts3_{speaker_id}_{global_index:05d}.wav"
            out_path = output_dir / out_name

            # ffmpeg command
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel", "error",
                "-y",  # Overwrite without asking
                "-ss", str(start),
                "-t", str(duration),
                "-i", str(wav_file),
                str(out_path)
            ]

            # Run the command
            try:
                subprocess.run(cmd, check=True)
                print(f"Created {out_path.name}")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg failed for {out_path.name}: {e}")

            global_index += 1
