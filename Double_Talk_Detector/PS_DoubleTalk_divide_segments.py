import csv
import subprocess
from pathlib import Path



def extract_segments(csv_path, wav_path, output_prefix, output_index):
    with open(csv_path, "r", newline='') as f:
        reader = csv.reader(f, delimiter="\t")
        for i, row in enumerate(reader):
            start = float(row[2])
            end = float(row[3])
            duration = end - start

            segment_filename = f"{output_prefix}_{i}.wav"
            # segment_filename = f"{output_prefix}_{output_index}.wav"
            current_type = output_prefix.split("_")[0]
            if "single" == current_type:
                segment_path = output_folder_single / segment_filename
            elif "overlap" == current_type:
                segment_path = output_folder_overlap / segment_filename
            else:
                raise ValueError(f"Unknown output prefix: {current_type}")

            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output
                "-i", str(wav_path),
                "-ss", str(start),
                "-t", str(duration),
                "-acodec", "copy",
                str(segment_path)
            ]

            # print(cmd)

            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            output_index += 1
    
    return output_index

def process_folder(csv_folder, wav_folder, prefix):
    output_index = 0
    for csv_file in sorted(csv_folder.glob(f"{prefix}_*.csv")):
        index = csv_file.stem.split("_")[-1]
        wav_file = wav_folder / f"D1_{index}.wav"
        if not wav_file.exists():
            print(f"[WARNING] Missing WAV file for index {index}")
            continue

        output_index = extract_segments(csv_file, wav_file, f"{prefix}_{index}", output_index)
        # output_index = extract_segments(csv_file, wav_file, prefix, output_index)

if __name__ == "__main__":
    # === Input folders ===
    root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/TTS3_dt/overlapping_gt')
    single_csv_folder = root_dir / "TTS3_input_csv_single" / "single_speaker_segments10"
    overlap_csv_folder = root_dir / "TTS3_input_csv" /"overlapping_segments10"
    single_wav_folder = root_dir / "WAVS_single"
    overlap_wav_folder = root_dir / "WAVS_overlap" 

    # === Output folder ===
    output_folder_path = root_dir / "output_segments10"
    output_folder_single = output_folder_path / "single10"
    output_folder_overlap = output_folder_path / "overlap10"

    output_folder_single.mkdir(parents=True, exist_ok=True)
    # output_folder_overlap.mkdir(parents=True, exist_ok=True)

    # === Run for both types of CSVs ===
    process_folder(single_csv_folder, single_wav_folder, "single")
    # process_folder(overlap_csv_folder, overlap_wav_folder, "overlap")

    print("Segment extraction completed.")
