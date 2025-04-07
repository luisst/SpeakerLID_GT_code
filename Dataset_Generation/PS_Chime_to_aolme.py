import json
import csv
from pathlib import Path
import re
import subprocess


def divide_csv_by_source(output_csv, skipped_csv, output_folder):
    """
    Divides the output and skipped CSV files into separate CSV files based on the source_audio_stem.

    :param output_csv: Path to the output CSV file with approved segments.
    :param skipped_csv: Path to the skipped CSV file with skipped segments.
    :param output_folder: Path to the folder where divided CSV files will be saved.
    """
    def write_to_csv(data, headers, file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(headers)
            writer.writerows(data)

    # Read the approved segments CSV
    with open(output_csv, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        headers = next(reader)
        approved_data = list(reader)

    # Read the skipped segments CSV
    with open(skipped_csv, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        skipped_headers = next(reader)
        skipped_data = list(reader)

    # Group data by source_audio_stem for approved segments
    approved_by_source = {}
    for row in approved_data:
        source_audio_stem = row[-1]  # Assuming the last column is source_audio_stem
        if source_audio_stem not in approved_by_source:
            approved_by_source[source_audio_stem] = []
        approved_by_source[source_audio_stem].append(row)

    # Group data by source_audio_stem for skipped segments
    skipped_by_source = {}
    for row in skipped_data:
        source_audio_stem = row[-1]  # Assuming the last column is source_audio_stem
        if source_audio_stem not in skipped_by_source:
            skipped_by_source[source_audio_stem] = []
        skipped_by_source[source_audio_stem].append(row)

    # Write grouped approved segments to separate CSV files
    for source_audio_stem, rows in approved_by_source.items():
        output_file = output_folder / f'approved_{source_audio_stem}.csv'
        write_to_csv(rows, headers, output_file)

    # Write grouped skipped segments to separate CSV files
    for source_audio_stem, rows in skipped_by_source.items():
        output_file = output_folder / f'skipped_{source_audio_stem}.csv'
        write_to_csv(rows, skipped_headers, output_file)

    print("CSV files divided by source_audio_stem and saved successfully.")


def read_json_file(file_path):
    """
    Reads a JSON file and converts it into a dictionary.
    
    :param file_path: Path to the JSON file
    :return: Dictionary representation of the JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


def time_to_seconds(time_str):
    """
    Converts a time string in HH:MM:SS.xx format to seconds.milliseconds.
    
    :param time_str: Time string in HH:MM:SS.xx format
    :return: Time in seconds.milliseconds as a float
    """
    match = re.match(r"(\d+):(\d+):(\d+\.\d+)", time_str)
    if not match:
        raise ValueError(f"Invalid time format: {time_str}")
    hours, minutes, seconds = map(float, match.groups())
    return round(hours * 3600 + minutes * 60 + seconds, 3)


def extract_audio_segment(source_file, output_file, start_time, end_time):
    """
    Extracts an audio segment using ffmpeg.
    
    :param source_file: Path to the source audio file
    :param output_file: Path to save the extracted segment
    :param start_time: Start time in HH:MM:SS.xx format
    :param end_time: End time in HH:MM:SS.xx format
    """
    command = [
        "ffmpeg", "-loglevel", "error", "-i", str(source_file), "-ss", str(start_time), "-to", str(end_time),
        "-c", "copy", str(output_file)
    ]
    subprocess.run(command, check=True)


def process_json_and_extract_audio(json_file, output_folder, location_audio_files, session="S01"):
    """
    Processes the JSON file, extracts audio segments, and writes to a CSV file.
    
    :param json_file: Path to the JSON file
    :param output_folder: Path to the output folder
    :param location_audio_files: Dictionary mapping locations to audio file names
    """
    data_list = read_json_file(json_file)
    if not data_list:
        return
    
    output_folder.mkdir(parents=True, exist_ok=True)
    output_csv = output_folder / f'approved_{json_file.stem}.csv'
    skipped_csv = output_folder / f'skipped_{json_file.stem}.csv'
    csv_header = ["Filename", "SpeakerID", "Lang", "Start_time", "End_time", "Transcript", "Prob", "Source"]
    skipped_csv_header = ["Reason", "SpeakerID", "Start_time", "End_time", "Transcript", "Source"]
    skipped_short_segments = 0

    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t')
        writer.writerow(csv_header)

        skipped_lines = []
        
        for data in data_list:
            start_seconds = time_to_seconds(data['start_time'])
            end_seconds = time_to_seconds(data['end_time'])
            duration = end_seconds - start_seconds

            source_audio = location_audio_files.get(data.get("location", ""), "unknown.wav")
            output_audio_filename = f"{session}_{data['speaker']}_{start_seconds}.wav"
            output_audio = output_folder / output_audio_filename

            # Add a margin of 0.5 seconds
            start_seconds_margin = max(0, start_seconds - 0.5)  # Ensure start time is not negative
            end_seconds_margin = end_seconds + 0.5           

            source_audio_stem = Path(source_audio).stem

            try:

                if duration < 2.0:
                    # print(f"Skipping segment: {data['start_time']} to {data['end_time']} (too short)")
                    skipped_short_segments += 1
                    skipped_lines.append(["Too short", data['speaker'], start_seconds, end_seconds, data['words'], source_audio_stem])
                    continue

                if "inaudible" in data['words'].lower():
                    # print(f"Skipping segment due to 'inaudible' in transcript: {data['start_time']} to {data['end_time']}")
                    skipped_lines.append(["Inaudible", data['speaker'], start_seconds, end_seconds, data['words'], source_audio_stem])
                    continue

                if "[" in data['words'].lower() and len(data['words']) < 40:
                    print(f'{data["words"]}')
                    # print(f"Skipping segment due to '[]' in transcript: {data['start_time']} to {data['end_time']}")
                    skipped_lines.append(["laughs mostly", data['speaker'], start_seconds, end_seconds, data['words'], source_audio_stem])
                    continue

                extract_audio_segment(source_audio, output_audio, start_seconds_margin, end_seconds_margin)
            except Exception as e:
                print(f"Failed to extract audio: {e}")
                output_audio = ""
            
            
            writer.writerow([ output_audio_filename,
                data['speaker'], "Eng", start_seconds, end_seconds,
                data['words'], 1.0, source_audio_stem
            ])
    
    # Write skipped lines to the skipped CSV file
    with open(skipped_csv, 'w', newline='', encoding='utf-8') as skipped_file:
        skipped_writer = csv.writer(skipped_file, delimiter='\t')
        skipped_writer.writerow(skipped_csv_header)
        skipped_writer.writerows(skipped_lines)

    divide_csv_by_source(output_csv, skipped_csv, output_folder)
    print(f"Total segments skipped due to being too short: {skipped_short_segments}")


# Example usage
if __name__ == "__main__":
    root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/CHIME6/aolme_base')
    input_folder = root_dir.joinpath('json_input_folder')  # Replace with the actual input folder
    output_base_path = root_dir.joinpath('output_base')  # Replace with the actual output base path
    folder_source = root_dir.joinpath('long_wavs_source')

    input_dict_jsons = {'S01':['U02', 'U01', 'U05'],
                        'S21':['U01', 'U03', 'U06'],
                        'S02':['U02', 'U03', 'U06'],
                        'S09':['U01', 'U04', 'U06']}


    
    for session, location_root_wavs in input_dict_jsons.items():

        current_json_file = input_folder / f'{session}.json'

        # Run the rest if the json file exists
        if not current_json_file.exists():
            print(f"Skipping {current_json_file} as it does not exist")
            continue


        output_folder = output_base_path / session 

        current_location_audio_files = {
            "kitchen": str(folder_source.joinpath(f'{session}_{location_root_wavs[0]}.CH1.wav')),
            "dining": str(folder_source.joinpath(f'{session}_{location_root_wavs[1]}.CH1.wav')),
            "living": str(folder_source.joinpath(f'{session}_{location_root_wavs[2]}.CH1.wav'))
        }

        process_json_and_extract_audio(current_json_file, \
                                       output_folder, \
                                       current_location_audio_files, \
                                       session=session)
