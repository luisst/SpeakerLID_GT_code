import os
import xml.etree.ElementTree as ET
import csv
from pathlib import Path
import re
from collections import OrderedDict


def parse_words_file(words_file):
    tree = ET.parse(words_file)
    root = tree.getroot()
    
    word_dict = OrderedDict()  # Use OrderedDict to maintain order

    namespace = "http://nite.sourceforge.net/"
    for word in root:
        word_id = word.attrib.get(f"{{{namespace}}}id")
        text = word.text if word.text else ""
        word_dict[word_id] = text
    
    return word_dict


def extract_ids(input_href):
    id_line = input_href.split("#id(")[1]


    id_list = []
    pattern = re.compile(r'\b([A-Za-z0-9]+\.[A-Z]\.[A-Za-z0-9]+)\)')
    
    matches = pattern.findall(id_line)
    if matches:
        id_list.extend(matches)
    
    # print(f'Word IDs: {id_list}')

    return id_list

def process_segment(segment, word_dict, segs_file, data):

    # participant = segment.attrib.get("participant", "Unknown")
    starttime = segment.attrib.get("transcriber_start", "")
    endtime = segment.attrib.get("transcriber_end", "")

    # Check if starttime and endtime are present
    if not starttime or not endtime:
        print(f">>>>>>>>>>>>>> Warning: Missing starttime or endtime in segment: {segment.attrib}")
        return data, word_dict
    
    words = []
    # Check if segment has more than one child
    if len(segment) > 1:
        print(f">>>>>>>>>>>>>> Warning: Segment has more than one child: {segment.attrib}")
        return data, word_dict

    # Since each segment has only one child, directly access it
    child = list(segment)[0]  # Get the single child
    # print(f'Processing {segs_file.split(os.sep)[-1]} |\n {child.attrib}')
    href = child.attrib["href"]

    # Extract participant ID (single Capital letter before .words.xml)
    participant = href.split(".")[1]

    # Check if participant ID is valid (single capital letter)
    if not re.match(r'^[A-Z]$', participant):
        print(f">>>>>>>>>>>>>> Warning: Invalid participant ID: {participant}")
        return data, word_dict

    # Check if href contains "#id("
    if not("#id("  in href):
        print(f">>>>>>>>>>>>>>>> Warning: No ID found in href: {href}")
        return data, word_dict

    # Extract word IDs from href
    word_ids = extract_ids(href)

    words_to_delete = []

    if len(word_ids) == 0:
        return data, word_dict
    if len(word_ids) > 2:
        print(f">>>>>>>>>>>>>>>> Warning: More than 2 word IDs found: {word_ids}")
        return data, word_dict
    # Handle single word ID or range of word IDs
    if len(word_ids) == 1 and word_ids[0] in word_dict:
        words.append(word_dict[word_ids[0]])
    elif len(word_ids) == 2:
        start_id, end_id = word_ids
        capturing = False
        for word_id, word_text in word_dict.items():
            if word_id == start_id:
                capturing = True
            if capturing:
                words.append(word_text)
                words_to_delete.append(word_id)  # Mark for deletion
            if word_id == end_id:
                break               

        for delete_id in words_to_delete:
            if delete_id in word_dict:
                del word_dict[delete_id]
    
    transcription = " ".join(words)
    # Remove extra spaces
    transcription = re.sub(r'\s+', ' ', transcription)

    # Remove spaces before punctuation
    transcription = re.sub(r'\s([?.!,:;])', r'\1', transcription)

    # Remove surrounding quotes
    transcription = re.sub(r'^\s*["“]', '', transcription)
    transcription = re.sub(r'["”]\s*$', '', transcription)


    # Remove leading and trailing spaces
    transcription = transcription.strip()

    data.append([participant, round(float(starttime), 2), round(float(endtime), 2), transcription])

    return data, word_dict

def process_session(segs_file, words_file, output_csv):
    tree = ET.parse(segs_file)
    root = tree.getroot()
    
    word_dict = parse_words_file(words_file)
    
    data = []
    
    for segment in root:
        data, word_dict = process_segment(segment, word_dict, segs_file, data)

    
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        # Write header with field names
        writer.writerow(["participant", "starttime", "endtime", "transcription"])
        writer.writerows(data)


def process_directory(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".segments.xml"):
            base_name = filename.replace(".segments.xml", "")
            segs_file = os.path.join(input_dir, filename)
            words_file = os.path.join(input_dir, f"{base_name}.words.xml")
            output_csv = os.path.join(output_dir, f"{base_name}.csv")
            
            if os.path.exists(words_file):
                process_session(segs_file, words_file, output_csv)
                # print(f"Processed {filename}")
            else:
                print(f"Skipping {filename}, missing words file {words_file}")

# Example usage
input_directory = Path(r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AMI-dataset\xml_input_files')
output_directory = input_directory.joinpath('my_output_separated')
process_directory(str(input_directory), str(output_directory))
