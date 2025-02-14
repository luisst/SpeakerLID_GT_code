import csv
from collections import defaultdict
import os
import sys

def calculate_speaker_times(file_path):
    speaker_times = defaultdict(float)
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                if len(row) >= 4:
                    speaker, _, start_time, end_time = row[:4]
                    try:
                        duration = float(end_time) - float(start_time)
                        speaker_times[speaker] += duration
                    except ValueError:
                        print(f"Skipping invalid row in {file_path}: {row}")
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
    
    return speaker_times

def process_all_csv_files(directory='.'):
    total_speaker_times = defaultdict(float)
    
    for filename in os.listdir(directory):
        if filename.lower().endswith('.csv'):
            file_path = os.path.join(directory, filename)
            file_speaker_times = calculate_speaker_times(file_path)
            
            for speaker, time in file_speaker_times.items():
                total_speaker_times[speaker] += time
    
    return dict(total_speaker_times)

def main():
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = '.'
    
    print(f"Processing CSV files in directory: {os.path.abspath(directory)}")
    result = process_all_csv_files(directory)

    print("\nTotal speaking time for each speaker across all CSV files:")
    for speaker, total_time in result.items():
        print(f"{speaker}: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()