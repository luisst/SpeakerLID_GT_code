import os
import json
import csv
import re
import sys
from pathlib import Path

# === Configuration ===
CSV_FOLDER = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Dvectors\std15K\gt_csv")
MAPPING_JSON = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\TTS3_dt\input_TTS3_chopped_all\speaker_id_mapping.json") 
OUTPUT_FOLDER = os.path.join(CSV_FOLDER, "updated_csvs")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Load mapping ===
with open(MAPPING_JSON, "r") as f:
    id_map = json.load(f)  # {speakerName: {old_id: new_id}}

# === Compile regex for filename speakerID ===
wav_pattern = re.compile(r"IC-(?P<name>.+?)_ID-(?P<id>.+?)(?P<rest>_.*)", re.IGNORECASE)

# === Process each CSV ===
for file in os.listdir(CSV_FOLDER):
    if file.lower().endswith(".csv"):
        input_path = os.path.join(CSV_FOLDER, file)
        output_path = os.path.join(OUTPUT_FOLDER, file)

        with open(input_path, "r", newline='', encoding="utf-8") as infile, \
             open(output_path, "w", newline='', encoding="utf-8") as outfile:

            reader = csv.reader(infile, delimiter='\t')
            writer = csv.writer(outfile, delimiter='\t')

            for row in reader:
                if len(row) < 5:
                    print(f"Skipping malformed line in {file}: {row}")
                    continue

                old_id = row[0]
                wav_filename = row[4]

                match = wav_pattern.match(wav_filename)
                if match:
                    speaker_name = match.group("name")
                    wav_old_id = match.group("id")
                    rest = match.group("rest")

                    try:
                        new_id = id_map[speaker_name][wav_old_id]
                    except KeyError:
                        print(f"⚠️ Mapping not found for {speaker_name}, {wav_old_id}. Skipping line.")
                        sys.exit(1)

                    # Update ID column and wav filename
                    row[0] = new_id
                    row[4] = f"IC-{speaker_name}_ID-{new_id}{rest}"

                    writer.writerow(row)
                else:
                    print(f"⚠️ Filename does not match expected format: {wav_filename}")
                    sys.exit(1)

print(f"✅ All CSVs processed. Updated versions saved to: {OUTPUT_FOLDER}")
