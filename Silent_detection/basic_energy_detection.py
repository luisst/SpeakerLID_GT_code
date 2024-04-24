import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav

def calculate_rms_energy(signal):
    return np.sqrt(np.mean(signal**2))


def normalize(signal):
    return signal / np.max(np.abs(signal))


## Function to normalize from 0 to 1
def normalize_0_1(signal):
    return (signal - np.min(signal)) / (np.max(signal) - np.min(signal))

def plot_waveform_and_rms_energy(waveform, sampling_rate, rms_energy):
    plt.figure(figsize=(12, 6))
    
    # Normalize waveform and RMS energy
    normalized_waveform = normalize(waveform)
    # normalized_rms_energy = normalize(rms_energy)
    normalized_rms_energy = normalize_0_1(rms_energy)
    
    # Plot waveform
    time_waveform = np.arange(len(normalized_waveform)) / sampling_rate
    plt.plot(time_waveform, normalized_waveform, label='Waveform')
    
    # Interpolate RMS energy to match the time axis of the waveform
    time_rms_energy = np.linspace(0, time_waveform[-1], len(normalized_rms_energy))
    plt.plot(time_rms_energy, normalized_rms_energy, marker='o', linestyle='', color='r', label='RMS Energy')
     
    plt.title('Normalized Waveform and RMS Energy')
    plt.xlabel('Time (s)')
    plt.ylabel('Normalized Amplitude / Energy')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    # Load WAV file
    filename = 'Silent_detection/G-C2L1P-Apr26-A-Allan_q2_03-05_000.wav'
    sampling_rate, waveform = wav.read(filename)
    
    # Calculate RMS energy
    window_size = 0.1 # seconds
    window_samples = int(window_size * sampling_rate)
    rms_energy = []
    for i in range(0, len(waveform) - window_samples + 1, window_samples):
        segment = waveform[i:i+window_samples]
        rms_energy.append(calculate_rms_energy(segment))
    rms_energy = np.array(rms_energy)
    
    # Plot waveform and RMS energy
    plot_waveform_and_rms_energy(waveform, sampling_rate, rms_energy)

if __name__ == "__main__":
    main()
