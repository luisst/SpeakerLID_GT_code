from pathlib import Path
import pandas as pd


csv_file = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\CHIME6\aolme_base\wavs_dev_eval\S09_U06_living.csv")
print(f"Processing {csv_file.name}")
# Read CSV file (tab-separated)
df = pd.read_csv(csv_file, sep="\t")

# Extract min start time and max end time
offset_start = 5203.0


# Update CSV file to reflect the new time offsets
df["Start_time"] = (df["Start_time"] - offset_start).round(2)
df["End_time"] = (df["End_time"] - offset_start).round(2)

# Save updated CSV file
updated_csv_file = csv_file.parent / csv_file.name.replace(".csv", "_GT.csv")
df.to_csv(updated_csv_file, sep="\t", index=False)
print(f"Updated CSV saved as {updated_csv_file}")
