import os
import pandas as pd
from pathlib import Path

# Define input and output directories
input_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Full_Commercial_Datasets_aolme\AMI_SD\GT_final")  # replace with your input folder path
output_folder = input_folder / 'mod_output'

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process each CSV file in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith('.csv'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename.replace('.csv', '.csv'))

        # Read and process the CSV
        df = pd.read_csv(input_path)
        df_sorted = df.sort_values(by='starttime')
        df_sorted = df_sorted.rename(columns={
            'participant': 'speaker_id',
            'starttime': 'start_time',
            'endtime': 'end_time',
            'transcription': 'transcription'
        })

        # Write as tab-separated file
        df_sorted.to_csv(output_path, sep='\t', index=False)
        print(f"Processed: {filename} -> {output_path}")

print("All files processed.")
