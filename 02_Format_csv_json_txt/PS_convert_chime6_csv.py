import json
import csv

# Function to convert time string (HH:MM:SS.sss) to float seconds
def time_to_seconds(time_str):
    h, m, s = map(float, time_str.split(':'))
    return round(h * 3600 + m * 60 + s, 2)

# Load the JSON data
with open('S01.json', 'r') as f:
    data = json.load(f)

# Open CSV file to write the output (tab-separated)
with open('chime_S01.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['speaker', 'start_time', 'end_time'])  # Writing header

    # Loop through each item and write the required data
    for item in data:
        speaker = item['speaker']
        start_time = time_to_seconds(item['start_time'])
        end_time = time_to_seconds(item['end_time'])
        writer.writerow([speaker, start_time, end_time])
