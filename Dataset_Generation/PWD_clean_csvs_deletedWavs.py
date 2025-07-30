import os
import pandas as pd
from pathlib import Path

# CONFIGURE THESE PATHS
csv_folder = Path.cwd()             # Folder with original CSV files
output_folder = csv_folder / "filtered_csvs"   # Folder to save filtered CSVs
txt_file = csv_folder / "wavs_to_delete_ALL.txt"            # TXT file with filenames to remove (no .wav)

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Read filenames to remove
with open(txt_file, "r") as f:
    filenames_to_remove = set(line.strip() for line in f if line.strip())

# Process each CSV file
for csv_filename in os.listdir(csv_folder):
    if csv_filename.endswith(".csv"):
        csv_path = os.path.join(csv_folder, csv_filename)
        
        # Read the CSV file
        df = pd.read_csv(csv_path, sep="\t", header=False, dtype=str)

        # Rename columns for clarity
        df.columns = ["speaker_id", "language", "start_time", "end_time", "filename"]
        # Ensure the 'filename' column is treated as a string
        df["filename"] = df["filename"].astype(str)
        
        # Identify rows to remove
        to_remove = df[df["filename"].isin(filenames_to_remove)]
        
        # Print removed entries if any
        if not to_remove.empty:
            print(f"\nRemoved entries from {csv_filename}:")
            print(to_remove.to_string(index=False))
        
        # Keep only non-matching rows
        df_filtered = df[~df["filename"].isin(filenames_to_remove)]
        
        # Save filtered DataFrame to output folder
        output_path = os.path.join(output_folder, csv_filename)
        df_filtered.to_csv(output_path, sep="\t", index=False)

print("\nAll files processed. Filtered CSVs saved to:", output_folder)
