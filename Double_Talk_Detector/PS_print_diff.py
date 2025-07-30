# Define the file paths
file1_path = 'likely_silent_wavs_10percent.txt'
file2_path = 'likely_silent_wavs_5percent.txt'

# Read lines from each file into sets
with open(file1_path, 'r') as f1:
    lines1 = set(line.strip() for line in f1 if line.strip())

with open(file2_path, 'r') as f2:
    lines2 = set(line.strip() for line in f2 if line.strip())

# Find lines that are in only one of the files (symmetric difference)
unique_lines = lines1.symmetric_difference(lines2)

# Print the result
print("Lines that are not in both files:")
for line in unique_lines:
    print(line)
