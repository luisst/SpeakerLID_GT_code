import os
import torch
import torchaudio
import numpy as np
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt

# Load silero VAD model
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=True)
(get_speech_ts, _, read_audio, _, _) = utils

# Configuration
root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/TTS3_dt')
WAV_FOLDER = root_dir / "output_chunks"

run_id = "single10perc"
output_dir = root_dir / run_id

output_dir.mkdir(parents=True, exist_ok=True)




SAMPLE_RATE = 16000  # VAD expects 16kHz
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Move model to the appropriate device
model.to(DEVICE)

def compute_vad_score(wav_path):

    # Load audio file and resample if necessary
    if not wav_path.endswith('.wav'):
        raise ValueError("Only .wav files are supported.")
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"File not found: {wav_path}")

    wav = read_audio(wav_path, sampling_rate=SAMPLE_RATE)
    
    # Silero VAD expects chunks of 512 samples for 16kHz
    chunk_size = 512
    all_probs = []
    
    # Use no_grad() for inference - more efficient and cleaner
    with torch.no_grad():
        # Process audio in chunks of 512 samples
        for i in range(0, len(wav), chunk_size):
            chunk = wav[i:i + chunk_size]
            
            # Pad the last chunk if it's shorter than chunk_size
            if len(chunk) < chunk_size:
                chunk = torch.nn.functional.pad(chunk, (0, chunk_size - len(chunk)))
            
            speech_prob = model(chunk.unsqueeze(0).to(DEVICE), SAMPLE_RATE).cpu().numpy()
            all_probs.extend(speech_prob)
    
    all_probs = np.array(all_probs)
    return np.mean(all_probs), np.max(all_probs)

def main():
    mean_probs = []
    max_probs = []
    file_paths = []
    perc_val = int(10)  # Percentile for thresholding

    print("Processing WAVs...")
    for fname in tqdm(os.listdir(WAV_FOLDER)):
        if fname.endswith('.wav'):
            fpath = os.path.join(WAV_FOLDER, fname)
            try:
                mean_p, max_p = compute_vad_score(fpath)
                mean_probs.append(mean_p)
                max_probs.append(max_p)
                file_paths.append(fname)
            except Exception as e:
                print(f"Error with {fname}: {e}")

    mean_probs = np.array(mean_probs)
    max_probs = np.array(max_probs)

    # Optional: Plot histogram
    plt.hist(mean_probs, bins=50, alpha=0.7, label='Mean Speech Prob')
    plt.hist(max_probs, bins=50, alpha=0.7, label='Max Speech Prob')
    plt.axvline(np.percentile(mean_probs, perc_val), color='red', linestyle='--', label=f'{perc_val}th Percentile Threshold')
    plt.legend()
    plt.title("Speech Probability Distribution")
    plt.xlabel("Probability")
    plt.ylabel("Frequency")
    plt.show()

    # Suggest threshold — conservative: 5th percentile of mean speech probability
    threshold = np.percentile(mean_probs, perc_val)
    print(f"\n📌 Suggested threshold (mean prob): {threshold:.3f}")

    # # List of files below threshold = likely silent
    # silent_files = [file_paths[i] for i, prob in enumerate(mean_probs) if prob < threshold]
    # print(f"\nDetected {len(silent_files)} likely silent files out of {len(file_paths)}")
    # number_of_silent_files = len(silent_files)

    # # Optional: Save to file
    # silent_path = output_dir / f"silent_{run_id}.txt"
    # with open(silent_path, "w") as f:
    #     for fname in silent_files:
    #         f.write(fname + "\n")
    
    # Select the top percent of files with the highest mean probability
    top_files = sorted(zip(file_paths, mean_probs), key=lambda x: x[1], reverse=True)
    top_file_names = [f[0] for f in top_files]
    
    # Optional: Save top files to a separate file
    speech_path = output_dir / f"speech_{run_id}.txt"
    with open(speech_path, "w") as f:
        for fname in top_file_names:
            f.write(fname + "\n")

if __name__ == "__main__":
    main()
