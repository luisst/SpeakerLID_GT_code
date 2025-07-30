# File paths
empty_list_path = 'files_to_delete_300.txt'
full_paths_file = 'balanced_dataset_min0_bal300.txt'        # File with full Unix paths
filtered_output_file = f'filtered_{full_paths_file}'  # Output file

# Read the list of empty audio filenames (without .wav)
with open(empty_list_path, 'r') as f:
    empty_filenames = set(line.strip() for line in f if line.strip())

# Read the full paths, filter, and write output
with open(full_paths_file, 'r') as infile, open(filtered_output_file, 'w') as outfile:
    for line in infile:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        basename = stripped_line.split('/')[-1].replace('.wav', '')
        if basename not in empty_filenames:
            outfile.write(stripped_line + '\n')
        else:
            print(f"Filtered out: {stripped_line}")
