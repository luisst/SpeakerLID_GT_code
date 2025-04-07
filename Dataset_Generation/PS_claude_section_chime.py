import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def optimize_segment_range(approved_file, rejected_file, min_duration=480):
    """
    Optimize the start and end points to minimize rejected segments.
    
    Parameters:
    - approved_file: Path to CSV with approved segments
    - rejected_file: Path to CSV with rejected segments
    - min_duration: Minimum duration in seconds (default 8 minutes = 480 seconds)
    
    Returns:
    - Optimal start time
    - Optimal end time
    - Number of rejected segments in the optimal range
    """
    # Read the CSV files
    approved_df = pd.read_csv(approved_file, sep='\t')
    rejected_df = pd.read_csv(rejected_file, sep='\t')
    
    # Get overall time range
    min_start = min(approved_df['Start_time'].min(), rejected_df['Start_time'].min())
    max_end = max(approved_df['End_time'].max(), rejected_df['End_time'].max())
    
    # Function to count rejected segments in a given range
    def count_rejected_segments(start, end):
        return len(rejected_df[
            ((rejected_df['Start_time'] >= start) & (rejected_df['Start_time'] <= end)) |
            ((rejected_df['End_time'] >= start) & (rejected_df['End_time'] <= end)) |
            ((rejected_df['Start_time'] <= start) & (rejected_df['End_time'] >= end))
        ])
    
    # Sliding window approach
    best_start = min_start
    best_end = min_start + min_duration
    min_rejected = float('inf')
    optimal_start = min_start
    optimal_end = min_start + min_duration
    
    while best_end <= max_end:
        # Count rejected segments in current window
        rejected_count = count_rejected_segments(best_start, best_end)
        
        # Update optimal range if fewer rejected segments
        if rejected_count < min_rejected:
            min_rejected = rejected_count
            optimal_start = best_start
            optimal_end = best_end
        
        # Slide the window
        best_start += 1
        best_end += 1
    
    return optimal_start, optimal_end, min_rejected

def plot_optimized_segments(approved_file, rejected_file):
    """
    Plot segments with the optimized range highlighted
    """
    # Optimize segment range
    start_time, end_time, rejected_count = optimize_segment_range(approved_file, rejected_file)
    
    # Read the CSV files
    approved_df = pd.read_csv(approved_file, sep='\t')
    rejected_df = pd.read_csv(rejected_file, sep='\t')
    
    # Create bins of 10 seconds
    bins = np.arange(start_time, end_time + 10, 10)
    
    # Function to calculate segment density
    def calculate_segment_density(dataframe):
        segment_density = np.zeros(len(bins) - 1)
        
        for _, row in dataframe.iterrows():
            start, end = row['Start_time'], row['End_time']
            
            # Clip segments to the optimized range
            start = max(start, start_time)
            end = min(end, end_time)
            
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
    
    # Highlight the optimized range
    plt.axvspan(start_time, end_time, color='yellow', alpha=0.2)
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('Segment Duration in 10-second Bin (seconds)')
    plt.title(f'Segment Density Visualization\nOptimal Range: {start_time:.2f}-{end_time:.2f} (Rejected Segments: {rejected_count})')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.show()
    
    # Return the optimization details
    return {
        'start_time': start_time,
        'end_time': end_time,
        'duration': end_time - start_time,
        'rejected_segment_count': rejected_count
    }

# Example usage
if __name__ == "__main__":
    base_path = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\CHIME6\aolme_base\output_base\S02')
    approved_csv_path = base_path / 'approved_S02_U02.CH1.csv' 
    rejected_csv_path = base_path / 'skipped_S02_U02.CH1.csv' 

    # Example usage
    optimization_results = plot_optimized_segments(approved_csv_path, rejected_csv_path)
    print(optimization_results)