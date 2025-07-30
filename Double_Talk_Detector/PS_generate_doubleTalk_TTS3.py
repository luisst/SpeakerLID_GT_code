import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path


def read_csv(filename):
    """Read a tab-separated CSV file with columns: speaker_id, lang, start_time, end_time"""
    return pd.read_csv(filename, sep='\t', header=None, 
                       names=['speaker_id', 'lang', 'start_time', 'end_time'])

def create_time_grid(df1, df2, resolution=0.3):
    """Create a unified time grid with the specified resolution spanning all segments"""
    # Find global min and max time
    min_time = min(df1['start_time'].min(), df2['start_time'].min())
    max_time = max(df1['end_time'].max(), df2['end_time'].max())
    
    # Create time grid
    time_points = np.arange(min_time, max_time, resolution)
    time_slots = [(t, t + resolution) for t in time_points]
    
    return time_slots

def map_segments_to_grid(df, time_slots):
    """Map speech segments to the time grid"""
    slot_mapping = defaultdict(set)
    
    for _, row in df.iterrows():
        start = row['start_time']
        end = row['end_time']
        speaker = row['speaker_id']
        lang = row['lang']
        
        for slot_start, slot_end in time_slots:
            # Check if the segment covers the entire time slot
            if start <= slot_start and end >= slot_end:
                slot_mapping[(slot_start, slot_end)].add((speaker, lang))
    
    return slot_mapping

def process_speech_segments(file1, file2, resolution=0.3):
    """Process two CSV files to find single speaker and overlapping segments"""
    # Read the files
    df1 = read_csv(file1)
    df2 = read_csv(file2)
    
    # Create a unified time grid
    time_slots = create_time_grid(df1, df2, resolution)
    
    # Map segments from both files to the time grid
    slots1 = map_segments_to_grid(df1, time_slots)
    slots2 = map_segments_to_grid(df2, time_slots)
    
    # Process all slots
    single_speaker_segments = []
    overlapping_segments = []
    
    for slot in time_slots:
        speakers1 = slots1.get(slot, set())
        speakers2 = slots2.get(slot, set())
        
        # If segment appears only in one file
        if speakers1 and not speakers2:
            for speaker, lang in speakers1:
                single_speaker_segments.append({
                    'speaker_id': speaker,
                    'lang': lang,
                    'start_time': round(slot[0], 2),
                    'end_time': round(slot[1], 2),
                    'source': 'file1'
                })
        elif speakers2 and not speakers1:
            for speaker, lang in speakers2:
                single_speaker_segments.append({
                    'speaker_id': speaker,
                    'lang': lang,
                    'start_time': round(slot[0], 2),
                    'end_time': round(slot[1], 2),
                    'source': 'file2'
                })
        # If segment appears in both files (overlapping)
        elif speakers1 and speakers2:
            # Create a combined entry for overlapping segments
            speaker_ids = [s[0] for s in speakers1.union(speakers2)]
            langs = [s[1] for s in speakers1.union(speakers2)]
            if len(speaker_ids) > 1:
                overlapping_segments.append({
                    'speaker_ids': '+'.join(map(str, speaker_ids)),
                    'langs': '+'.join(langs),
                    'start_time': round(slot[0], 2),
                    'end_time': round(slot[1], 2)
                })
            else:
                print(f"Warning: {speaker_ids}")
    
    # Convert to dataframes
    single_speaker_df = pd.DataFrame(single_speaker_segments)
    overlapping_df = pd.DataFrame(overlapping_segments)
    
    return single_speaker_df, overlapping_df

def merge_consecutive_segments(df):
    """Merge consecutive segments with the same speakers"""
    if df.empty:
        return df
    
    result = []
    
    # Sort by start time
    df = df.sort_values('start_time')
    
    # Initialize with the first segment
    current = df.iloc[0].to_dict()
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        
        # Check if this segment is consecutive to the current one
        if 'speaker_id' in df.columns and 'source' in df.columns:
            # For single speaker segments
            if (current['speaker_id'] == row['speaker_id'] and
                current['lang'] == row['lang'] and
                abs(current['end_time'] - row['start_time']) < 1e-6 and
                current['source'] == row['source']):
                current['end_time'] = row['end_time']
            else:
                result.append(current)
                current = row.to_dict()
        elif 'speaker_ids' in df.columns:
            # For overlapping segments
            if (current['speaker_ids'] == row['speaker_ids'] and
                current['langs'] == row['langs'] and
                abs(current['end_time'] - row['start_time']) < 1e-6):
                current['end_time'] = row['end_time']
            else:
                result.append(current)
                current = row.to_dict()
    
    # Add the last segment
    result.append(current)
    
    return pd.DataFrame(result)


def process_all_csv_pairs(input_folder, single_output_folder, overlap_output_folder, resolution=0.3):
    
    # Ensure output folders exist
    single_output_folder.mkdir(parents=True, exist_ok=True)
    overlap_output_folder.mkdir(parents=True, exist_ok=True)
    
    # Process each pair of files
    for i in range(0, 40, 1):  # From 0 to 49
        file1 = input_folder / f"D1_{i}.csv"
        file2 = input_folder / f"D2_{i}.csv"
        
        # Check if both files exist
        if not file1.exists() or not file2.exists():
            print(f"Skipping pair: {file1} and {file2} (one or both files missing)")
            continue
        
        print(f"Processing pair: {file1} and {file2}")
        
        # Process the files
        single_speaker_df, overlapping_df = process_speech_segments(file1, file2, resolution)
        
        # Save the results
        single_output_file = single_output_folder / f"single_{i}.csv"
        overlap_output_file = overlap_output_folder / f"overlap_{i}.csv"
        
        if not single_speaker_df.empty:
            single_speaker_df.to_csv(single_output_file, sep='\t', index=False, header=False)
            print(f"Single speaker segments saved to {single_output_file}")
        else:
            print(f"No single speaker segments found for pair {i}")
        
        if not overlapping_df.empty:
            overlapping_df.to_csv(overlap_output_file, sep='\t', index=False, header=False)
            print(f"Overlapping segments saved to {overlap_output_file}")
        else:
            print(f"No overlapping segments found for pair {i}")

if __name__ == "__main__":
    # Define input and output folders
    csv_input_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\TTS3_dt\overlapping_gt\TTS3_input_csv")
    single_output_folder = csv_input_folder / 'single_speaker_segments10_fromscript'
    overlap_output_folder = csv_input_folder / 'overlapping_segments10'
    
    # Run the processing
    process_all_csv_pairs(csv_input_folder, single_output_folder, overlap_output_folder, resolution=1.0)