import librosa
import numpy as np
import matplotlib.pyplot as plt

def calculate_rms_segments(audio_file, segment_duration=0.5):
    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None)

    # Calculate the total number of samples in each segment
    segment_samples = int(segment_duration * sr)

    # Calculate the number of segments
    num_segments = len(y) // segment_samples

    # Initialize an empty list to store RMS values for each segment
    rms_values = []

    # Iterate over each segment and calculate RMS value
    for i in range(num_segments):
        # Extract the segment
        segment = y[i * segment_samples: (i + 1) * segment_samples]

        # Calculate RMS value for the segment
        rms = np.sqrt(np.mean(segment**2))

        # Append RMS value to the list
        rms_values.append(rms)

    return rms_values


def rms_to_db(rms_values):
    """
    Convert RMS values to Full Scale dB assuming PCM_16 format at 16 kHz sampling rate.
    """
    # Convert rms_values to a NumPy array
    rms_values = np.array(rms_values)

    # Calculate maximum possible amplitude for PCM_16
    max_amplitude = 2 ** 15  # 16-bit PCM, so max amplitude is 2^15

    # Calculate full scale level in dB
    full_scale_db = 20 * np.log10(max_amplitude)

    # Convert RMS values to dB
    rms_db = 20 * np.log10(rms_values / max_amplitude)

    # Convert to full scale dB
    full_scale_rms_db = full_scale_db + rms_db

    return full_scale_rms_db


def plot_audio_and_rms(audio_file, full_scale_rms_db, segment_duration=0.5):
    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None)

    # Calculate time array for audio
    audio_duration = len(y) / sr
    time_audio = np.linspace(0, audio_duration, len(y))

    # Create time array for RMS values
    time_rms = np.arange(0, audio_duration, segment_duration)

    # Plot audio waveform
    plt.figure(figsize=(10, 6))
    plt.plot(time_audio, y, color='b', label='Audio Waveform')

    # Plot RMS values as horizontal lines
    for i, rms_db in enumerate(full_scale_rms_db):
        plt.hlines(rms_db, xmin=i*segment_duration, xmax=(i+1)*segment_duration, colors='r', linewidth=0.5, label='RMS Value')

    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude (dB)')
    plt.title('Audio Waveform with RMS Values (Full Scale dB)')
    plt.legend()
    plt.show()

def plot_audio_and_rms2(audio_file, full_scale_rms_db, segment_duration=0.5):
    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None)

    # Calculate time array for audio
    audio_duration = len(y) / sr
    time_audio = np.linspace(0, audio_duration, len(y))

    # Create time array for RMS values
    time_rms = np.arange(0, audio_duration, segment_duration)

    # Create a new figure
    plt.figure(figsize=(10, 6))

    # Plot audio waveform with transparency
    plt.plot(time_audio, y, color='b', alpha=0.4, label='Audio Waveform')

    # Create a second y-axis for Full Scale dB
    plt.twinx()

    # Plot RMS values as horizontal lines
    for i, rms_db in enumerate(full_scale_rms_db):
        plt.hlines(rms_db, xmin=i*segment_duration, xmax=(i+1)*segment_duration, colors='r', linewidth=1.5, label='FSDB Value')

    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude (dB)')
    plt.title('Audio Waveform with Full Scale dB (FSDB) Values')
    plt.show()


audio_file = 'Silent_detection/G-C2L1P-Apr26-A-Allan_q2_03-05_000.wav'
full_scale_rms_db = rms_to_db(calculate_rms_segments(audio_file))
plot_audio_and_rms2(audio_file, full_scale_rms_db)
