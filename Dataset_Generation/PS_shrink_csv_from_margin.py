import os
from pathlib import Path
import pandas as pd

def shrink_segments(input_folder, output_folder, shrink_by=0.5):
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.endswith('.csv'):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file)

            try:
                df = pd.read_csv(input_path, sep=',')
                df.columns = [col.strip() for col in df.columns]  # Strip whitespace

                required_columns = {'filename', 'start_time', 'end_time'}
                if not required_columns.issubset(df.columns):
                    print(f"[SKIPPED] {file}: Missing required columns. Found: {df.columns.tolist()}")
                    continue

                # Shrink start and end times
                df['start_time'] = df['start_time'].apply(lambda x: max(0, x + shrink_by))
                df['end_time'] = df['end_time'].apply(lambda x: max(0, x - shrink_by))

                df['start_time'] = df['start_time'].round(2)
                df['end_time'] = df['end_time'].round(2)

                # Ensure valid segments
                df = df[df['start_time'] < df['end_time']]

                df.to_csv(output_path, sep=',', index=False)
                print(f"[OK] {file} -> {output_path}")
            except Exception as e:
                print(f"[ERROR] {file}: {e}")

    print(f"Processed files saved to: {output_folder}")

# Example usage
input_folder = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\SD_interviews_TTS3\TTS_long\output_combined\csv_with_margin_old') 
output_folder = input_folder.parent / 'output_shrinked'
shrink_segments(input_folder, output_folder)
