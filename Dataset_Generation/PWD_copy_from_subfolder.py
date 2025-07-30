from pathlib import Path
import shutil

# Set the base directory (you can change this as needed)
base_dir = Path.cwd()  # current working directory

# Create the 'all_together' folder
all_together_dir = base_dir / 'all_together'
all_together_dir.mkdir(exist_ok=True)

# Loop through subfolders one level deep
for subfolder in base_dir.iterdir():
    if subfolder.is_dir() and subfolder.name != 'all_together':
        # Find all .wav files in the subfolder
        for wav_file in subfolder.glob('*.wav'):
            destination = all_together_dir / wav_file.name

            # Ensure we don't overwrite files with the same name
            if destination.exists():
                destination = all_together_dir / f"{wav_file.stem}_{subfolder.name}{wav_file.suffix}"
            
            shutil.copy2(wav_file, destination)

print("All .wav files copied to 'all_together' folder.")
