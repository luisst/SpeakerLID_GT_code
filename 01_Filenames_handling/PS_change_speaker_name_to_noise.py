from pathlib import Path

# Set the path to the folder containing the audio files
path = Path.cwd()
# Loop through each file in the folder
idx = 0
for file_path in path.glob("*.wav"):
    file_name = file_path.name
    parts = file_name.split("_")
    
    # Replace the last subsection with 'noise'
    parts[-1] = f'noise_{idx:03d}.wav'
    idx = idx + 1
    
    # Construct the new file name and rename the file
    new_name = "_".join(parts)
    new_path = file_path.with_name(new_name)
    file_path.rename(new_path)
