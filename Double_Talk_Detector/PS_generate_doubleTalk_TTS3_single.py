import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path

def read_csv(filename):
    """Read a tab-separated CSV file with columns: speaker_id, lang, start_time, end_time"""
    return pd.read_csv(filename, sep='\t', header=None, 
                       names=['speaker_id', 'lang', 'start_time', 'end_time'])


def process_single_csv_files(input_folder, single_output_folder, resolution=0.7):
    """Process single type of CSV files (D1_XXXX) and divide speech segments into fixed-length segments."""
    
    # Ensure output folder exists
    single_output_folder.mkdir(parents=True, exist_ok=True)
    
    # Process each file
    for i in range(0, 40, 1):  # From 0 to 39
        file1 = input_folder / f"D1_{i}.csv"
        
        # Check if the file exists
        if not file1.exists():
            print(f"Skipping file: {file1} (file missing)")
            continue
        
        print(f"Processing file: {file1}")
        
        # Read the file
        df1 = read_csv(file1)
        
        # Create a time grid for the file
        min_time = df1['start_time'].min()
        max_time = df1['end_time'].max()
        time_points = np.arange(min_time, max_time, resolution)
        time_slots = [(t, t + resolution) for t in time_points]
        
        # Map segments to the time grid
        single_speaker_segments = []
        for _, row in df1.iterrows():
            start = row['start_time']
            end = row['end_time']
            speaker = row['speaker_id']
            lang = row['lang']
            
            for slot_start, slot_end in time_slots:
                # Check if the segment covers the entire time slot
                if start <= slot_start and end >= slot_end:
                    single_speaker_segments.append({
                        'speaker_id': speaker,
                        'lang': lang,
                        'start_time': round(slot_start, 2),
                        'end_time': round(slot_end, 2)
                    })
        
        # Convert to dataframe
        single_speaker_df = pd.DataFrame(single_speaker_segments)
        
        # Save the results
        single_output_file = single_output_folder / f"single_{i}.csv"
        if not single_speaker_df.empty:
            single_speaker_df.to_csv(single_output_file, sep='\t', index=False, header=False)
            print(f"Single speaker segments saved to {single_output_file}")
        else:
            print(f"No single speaker segments found for file {i}")

if __name__ == "__main__":
    # Define input and output folders
    csv_input_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\TTS3_dt\overlapping_gt\TTS3_input_csv_single")
    single_output_folder = csv_input_folder / 'single_speaker_segments10'
    
    # Run the processing
    process_single_csv_files(csv_input_folder, single_output_folder, resolution=1.0)