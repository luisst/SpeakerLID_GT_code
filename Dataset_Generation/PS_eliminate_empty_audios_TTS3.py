def extract_empty_audio_filenames(input_path, output_path):
    import re

    empty_filenames = set()

    with open(input_path, 'r', encoding='utf-8') as file:
        for line in file:
            if ">>>>> Audio is empty:" in line:
                # Extract the part after the colon
                parts = line.split(">>>>> Audio is empty:")
                if len(parts) > 1:
                    filename = parts[1].strip().split(' ')[1]  # Get the first word after the colon
                    empty_filenames.add(filename)

    # Write unique filenames to the output file
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for filename in sorted(empty_filenames):
            outfile.write(filename + '\n')

    print(f"Extracted {len(empty_filenames)} unique empty audio filenames.")


# Example usage
input_txt = r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\TTS3_dt\TTS3_bal4-sp_gain0.7-bk_num6-bk_gain0.5-ns_gain0.6\TTS3_bal4-sp_gain0.7-bk_num6-bk_gain0.5-ns_gain0.6_log.txt"
output_txt = r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\TTS3_dt\TTS3_bal4-sp_gain0.7-bk_num6-bk_gain0.5-ns_gain0.6\empty_audios_200.txt" 
extract_empty_audio_filenames(input_txt, output_txt)
