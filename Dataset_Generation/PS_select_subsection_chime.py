import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def plot_segment_density(approved_file, rejected_file):
    # Read the CSV files
    approved_df = pd.read_csv(approved_file, sep='\t')
    rejected_df = pd.read_csv(rejected_file, sep='\t')
    
    # Find the overall start and end times
    min_start_time = min(approved_df['Start_time'].min(), rejected_df['Start_time'].min())
    max_end_time = max(approved_df['End_time'].max(), rejected_df['End_time'].max())
    
    # Create bins of 10 seconds
    bins = np.arange(min_start_time, max_end_time + 10, 10)
    
    # Function to calculate segment density
    def calculate_segment_density(dataframe):
        segment_density = np.zeros(len(bins) - 1)
        
        for _, row in dataframe.iterrows():
            start, end = row['Start_time'], row['End_time']
            
            # Find which bins this segment overlaps
            bin_indices = np.digitize([start, end], bins) - 1
            
            # Calculate the portion of the bin covered
            for i in range(bin_indices[0], bin_indices[1]):
                bin_start = bins[i]
                bin_end = bins[i+1]
                
                # Calculate overlap
                overlap_start = max(start, bin_start)
                overlap_end = min(end, bin_end)
                overlap_duration = max(0, overlap_end - overlap_start)
                
                segment_density[i] = max(segment_density[i], overlap_duration)
        
        return segment_density
    
    # Calculate segment density for approved and rejected segments
    approved_density = calculate_segment_density(approved_df)
    rejected_density = calculate_segment_density(rejected_df)
    
    # Plot the results
    plt.figure(figsize=(15, 6))
    
    # Bin centers for x-axis
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    plt.bar(bin_centers, approved_density, width=10, alpha=0.5, label='Approved Segments', color='green')
    plt.bar(bin_centers, rejected_density, width=10, alpha=0.5, label='Rejected Segments', color='red')
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('Segment Duration in 10-second Bin (seconds)')
    plt.title('Segment Density Visualization')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.show()

# Example usage

# Load CSV files
def load_segments(approved_csv, rejected_csv):
    approved = pd.read_csv(approved_csv, sep='\t', encoding='utf-8')
    rejected = pd.read_csv(rejected_csv, sep='\t', encoding='utf-8')
    return approved, rejected

# Merge overlapping intervals
def merge_intervals(intervals):
    intervals.sort()
    merged = []
    for start, end in intervals:
        if merged and merged[-1][1] >= start:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged

# Find optimal subsections
def find_suitable_subsections(approved, rejected, min_length=480):
    approved_intervals = merge_intervals(list(zip(approved['start_time'], approved['end_time'])))
    rejected_intervals = merge_intervals(list(zip(rejected['start_time'], rejected['end_time'])))
    
    suitable_subsections = []
    
    current_start = None
    current_end = None
    
    for start, end in approved_intervals:
        if current_start is None:
            current_start = start
            current_end = end
        elif start - current_end <= 10:  # Allow small gaps
            current_end = max(current_end, end)
        else:
            if (current_end - current_start) >= min_length:
                suitable_subsections.append((current_start, current_end))
            current_start, current_end = start, end
    
    if current_start is not None and (current_end - current_start) >= min_length:
        suitable_subsections.append((current_start, current_end))
    
    # Filter out sections with too many rejected segments
    final_subsections = []
    for start, end in suitable_subsections:
        rejected_time = sum(min(end, r_end) - max(start, r_start) for r_start, r_end in rejected_intervals if r_start < end and r_end > start)
        if rejected_time / (end - start) < 0.1:  # Less than 10% rejected
            final_subsections.append((start, end))
    
    return final_subsections

# Main function
def main(approved_csv, rejected_csv):
    approved, rejected = load_segments(approved_csv, rejected_csv)
    # suitable_subsections = find_suitable_subsections(approved, rejected)
    # print("Selected subsections:")
    # for start, end in suitable_subsections:
    #     print(f"Start: {start} sec, End: {end} sec, Duration: {end - start} sec")

    # Plot a histogram of the durations
    durations = rejected['End_time'] - rejected['Start_time']
    plt.hist(durations, bins=50, edgecolor='black')
    plt.title('Histogram of segment durations')
    plt.xlabel('Duration (seconds)')
    plt.ylabel('Count')
    plt.show()

    # durations = approved['End_time'] - approved['Start_time']
    # plt.hist(durations, bins=50, edgecolor='black')
    # plt.title('Histogram of segment durations')
    # plt.xlabel('Duration (seconds)')
    # plt.ylabel('Count')
    # plt.show()

def plot_start_time_histogram(approved_file, rejected_file):
    # Read the CSV files
    approved_df = pd.read_csv(approved_file, sep='\t')
    rejected_df = pd.read_csv(rejected_file, sep='\t')

    # Plot histograms of Start_time
    plt.figure(figsize=(15, 6))
    
    plt.hist(approved_df['Start_time'], bins=50, alpha=0.5, label='Approved Start Times', color='blue', edgecolor='black')
    plt.hist(rejected_df['Start_time'], bins=50, alpha=0.5, label='Rejected Start Times', color='orange', edgecolor='black')
    
    plt.xlabel('Start Time (seconds)')
    plt.ylabel('Count')
    plt.title('Histogram of Start Times')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.show()


def print_rejected_segments_before_1000(rejected_file):
    # Read the rejected CSV file
    rejected_df = pd.read_csv(rejected_file, sep='\t')
    
    # Filter segments that start before 1000 seconds
    filtered_segments = rejected_df[rejected_df['Start_time'] < 1000]
    
    # Print the filtered segments
    print("Rejected segments starting before 1000 seconds:")
    for _, row in filtered_segments.iterrows():
        print(f"Start: {row['Start_time']} sec, End: {row['End_time']} sec, Duration: {row['End_time'] - row['Start_time']} sec")

# Example usage
if __name__ == "__main__":
    base_path = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\CHIME6\aolme_base\output_base\S02')
    approved_csv_path = base_path / 'approved_S02_U02.CH1.csv' 
    rejected_csv_path = base_path / 'skipped_S02_U02.CH1.csv' 
    # main(str(approved_csv_path), str(rejected_csv_path))
    # plot_start_time_histogram(str(approved_csv_path), str(rejected_csv_path))
    plot_segment_density(approved_csv_path, rejected_csv_path)
    # print_rejected_segments_before_1000(str(rejected_csv_path))