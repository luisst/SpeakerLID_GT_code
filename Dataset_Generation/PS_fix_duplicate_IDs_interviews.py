import os
import re
import json
from collections import defaultdict
import pprint
from pathlib import Path

# Set your folder path here
FOLDER_PATH = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\TTS3_dt\input_TTS3_chopped_all") 
MAPPING_FILE = "speaker_id_mapping.json"

# Configuration
ID_DIGITS = 2  # for IDs like '00', '01', ..., '99'

# Regex pattern to extract components
pattern = re.compile(r"IC-(?P<name>.+?)_ID-(?P<id>.+?)(?P<rest>_.*)\.wav", re.IGNORECASE)

# Step 1: Scan and collect file info
speaker_original_ids = defaultdict(set)
file_info = []

for filename in os.listdir(FOLDER_PATH):
    if filename.lower().endswith(".wav"):
        match = pattern.match(filename)
        if match:
            speaker_name = match.group("name")
            original_id = match.group("id")
            rest = match.group("rest")
            speaker_original_ids[speaker_name].add(original_id)
            file_info.append((filename, speaker_name, original_id, rest))

pprint.pprint(speaker_original_ids)

# Step 2: Assign unique 2-digit IDs to each speaker name
speaker_name_to_final_id = {}
used_ids = set()

for idx, speaker_name in enumerate(sorted(speaker_original_ids.keys())):
    final_id = f"{idx:0{ID_DIGITS}d}"
    if final_id in used_ids:
        raise ValueError(f"ID collision: {final_id} already used")
    speaker_name_to_final_id[speaker_name] = final_id
    used_ids.add(final_id)

# Step 3: Create final mapping: (speakerName, originalID) → final 2-digit ID
final_mapping = {}
for speaker_name, original_ids in speaker_original_ids.items():
    target_id = speaker_name_to_final_id[speaker_name]
    for orig_id in original_ids:
        final_mapping[(speaker_name, orig_id)] = target_id

# Mapping:
print(f'Mapping')
pprint.pprint(final_mapping)

# Step 4: Rename files using the final 2-digit ID
for filename, speaker_name, original_id, rest in file_info:
    new_id = final_mapping[(speaker_name, original_id)]
    new_filename = f"IC-{speaker_name}_ID-{new_id}{rest}.wav"
    src = os.path.join(FOLDER_PATH, filename)
    dst = os.path.join(FOLDER_PATH, new_filename)
    print(f"Renaming: {filename} → {new_filename}")
    os.rename(src, dst)

# Step 5: Save final mapping
json_mapping = {
    speaker: {
        orig_id: speaker_name_to_final_id[speaker]
        for orig_id in orig_ids
    }
    for speaker, orig_ids in speaker_original_ids.items()
}

with open(os.path.join(FOLDER_PATH, MAPPING_FILE), "w") as f:
    json.dump(json_mapping, f, indent=2)

print(f"✅ Done. Mapping saved to: {MAPPING_FILE}")
