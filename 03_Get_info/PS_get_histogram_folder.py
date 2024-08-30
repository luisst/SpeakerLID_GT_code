import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import stats
from pathlib import Path

def get_audio_lengths(input_wav_path):
    audio_lengths = []
    for filename in os.listdir(input_wav_path):
        if filename.endswith(".wav"):
            file_path = os.path.join(input_wav_path, filename)
            sample_rate, data = wavfile.read(file_path)
            duration = len(data) / sample_rate
            audio_lengths.append(duration)
    return audio_lengths

def plot_histogram(audio_lengths):
    mean_length = np.mean(audio_lengths)
    std_dev = np.std(audio_lengths)
    num_audios = len(audio_lengths)

    plt.figure(figsize=(10, 6))
    n, bins, patches = plt.hist(audio_lengths, bins='auto', edgecolor='black')
    
    plt.xlabel('Duration (seconds)')
    plt.ylabel('Frequency')
    plt.title(f'Histogram of Audio Lengths\n'
              f'Number of audios: {num_audios}\n'
              f'Mean: {mean_length:.2f}s, Std Dev: {std_dev:.2f}s')
    
    plt.grid(True, alpha=0.3)
    plt.show()

# Replace 'input_wav_path' with the actual path to your folder
input_wav_path = Path.cwd()  # Set input_wav_path to the current working directory 
audio_lengths = get_audio_lengths(input_wav_path)
plot_histogram(audio_lengths)