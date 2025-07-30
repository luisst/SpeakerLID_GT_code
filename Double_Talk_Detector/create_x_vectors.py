import os
import torch
import torchaudio
import glob
from tqdm import tqdm
from pathlib import Path

root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/TTS3_dt/overlapping_gt/output_segments10')
input_folder = root_dir / "dataset10"
output_folder = input_folder / "features"  # Output folder for features 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Check if output folder exists, if not create it
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get all wav files
wav_files = glob.glob(os.path.join(input_folder, "*.wav"))
print(f"Found {len(wav_files)} wav files")

# Load WavLM model
device = torch.device(device if torch.cuda.is_available() and device == 'cuda' else 'cpu')
print(f"Using device: {device}")

wavlm_model = torchaudio.pipelines.WAVLM_BASE.get_model().to(device)
wavlm_model.eval()

# Process each wav file
for wav_path in tqdm(wav_files):
    # Extract label from filename
    filename = os.path.basename(wav_path)
    if 'overlap' in filename:
        label = 1
    elif 'single' in filename:
        label = 0
    else:
        print(f"Warning: Could not determine label for {filename}, skipping")
        continue

    # Load waveform
    waveform, sample_rate = torchaudio.load(wav_path)
    
    # Extract features
    with torch.no_grad():
        features = wavlm_model(waveform.to(device))
        
    # Create output filename (replace .wav with .pt)
    output_filename = os.path.splitext(filename)[0] + '.pt'
    output_path = os.path.join(output_folder, output_filename)
    
    # Save features and label
    torch.save({
        'features': features[0].cpu(),
        'label': label,
        'original_path': wav_path
    }, output_path)

print(f"Feature extraction completed. Features saved to {output_folder}")