import torch
import torchaudio
from pathlib import Path
from transformers import Wav2Vec2Processor, Wav2Vec2Model
import os
import numpy as np
from tqdm import tqdm

# Load pretrained Wav2Vec2
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
model.eval()

# Set device (GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Audio loading function
def load_audio(path, sample_rate=16000):
    waveform, sr = torchaudio.load(path)
    if sr != sample_rate:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=sample_rate)
        waveform = resampler(waveform)
    return waveform.squeeze(0)  # Remove channel dimension

# Extract Wav2Vec2 embeddings
def extract_embedding(audio_tensor):
    inputs = processor(audio_tensor, sampling_rate=16000, return_tensors="pt", padding=True)
    input_values = inputs.input_values.to(device)

    with torch.no_grad():
        outputs = model(input_values)
        hidden_states = outputs.last_hidden_state  # Shape: (batch_size, time_steps, hidden_dim)

    # Aggregate time dimension (e.g., mean pooling)
    embedding = hidden_states.mean(dim=1)  # Shape: (batch_size, hidden_dim)
    return embedding.squeeze(0).cpu().numpy()

# Process all WAV files in a directory
def process_directory(wav_dir, output_npy="embeddings.npy"):
    file_list = [f for f in os.listdir(wav_dir) if f.endswith(".wav")]
    all_labels = []
    all_embeddings = []
    for fname in tqdm(file_list, desc="Extracting embeddings"):
        current_label = 1 if "overlap" in fname.lower() else 0
        audio_path = os.path.join(wav_dir, fname)
        audio_tensor = load_audio(audio_path)
        embedding = extract_embedding(audio_tensor)
        all_embeddings.append(embedding)
        all_labels.append(current_label)

    # Save as NumPy array
    all_embeddings = np.stack(all_embeddings)
    np.save(output_npy, all_embeddings)
    print(f"Saved {len(all_embeddings)} embeddings to {output_npy}")

    # Save labels as well if needed
    all_labels = np.array(all_labels)
    np.save(output_npy.replace(".npy", "_labels.npy"), all_labels)
    print(f"Saved {len(all_labels)} labels to {output_npy.replace('.npy', '_labels.npy')}")

# Example usage
if __name__ == "__main__":

    root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/DoubleTalk/')
    wav_directory = root_dir / "double_talk_dataset"
    process_directory(wav_directory, output_npy="wav2vec2_embeddings.npy")
