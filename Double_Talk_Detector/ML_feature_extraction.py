import numpy as np
import librosa

# Constants
SAMPLE_RATE = 16000  # Default sample rate, adjust if your files differ
MAX_DURATION = 1  # Maximum audio length in seconds to analyze (in seconds)


def extract_features(file_path):

    # Load audio file (limit duration to reduce computation time if needed)
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE, duration=MAX_DURATION)
    
    # Ensure minimum length
    if len(y) < sr * 0.5:  # At least 0.5s of audio
        return None
        
    # Feature list to store all extracted features
    features = []
    
    # 1. MFCC features (captures spectral characteristics of speech)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    features.extend([np.mean(mfcc) for mfcc in mfccs])
    features.extend([np.std(mfcc) for mfcc in mfccs])
    
    # 2. Spectral Centroid (indicates where the "center of mass" of the spectrum is)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    features.extend([np.mean(spectral_centroid), np.std(spectral_centroid)])
    
    # 3. Zero Crossing Rate (useful for distinguishing voiced/unvoiced speech)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
    features.extend([np.mean(zero_crossing_rate), np.std(zero_crossing_rate)])
    
    # 4. Spectral Rolloff (indicates the frequency below which a specified percentage of the total energy is contained)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    features.extend([np.mean(spectral_rolloff), np.std(spectral_rolloff)])
    
    # 5. Spectral Contrast (useful for music/speech discrimination)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    features.extend([np.mean(np.mean(spectral_contrast, axis=1)), 
                    np.mean(np.std(spectral_contrast, axis=1))])
    
    # 6. Spectral Bandwidth (indicates the width of the spectral band)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    features.extend([np.mean(spectral_bandwidth), np.std(spectral_bandwidth)])
    
    # 7. RMS Energy (indicates amplitude/energy of the signal)
    rms = librosa.feature.rms(y=y)[0]
    features.extend([np.mean(rms), np.std(rms)])
    
    # 8. Spectral Flatness (distinguishes between noisy and tonal sounds)
    flatness = librosa.feature.spectral_flatness(y=y)[0]
    features.extend([np.mean(flatness), np.std(flatness)])
    
    # 9. Voiced-to-unvoiced ratio estimation (crude approximation)
    # Use zero crossing rate as a proxy - higher ZCR often indicates unvoiced segments
    zcr_segments = librosa.feature.zero_crossing_rate(
        y, frame_length=2048, hop_length=512)[0]
    voiced_frames = sum(1 for zcr in zcr_segments if zcr < 0.1)  # Threshold can be adjusted
    voiced_ratio = voiced_frames / len(zcr_segments) if len(zcr_segments) > 0 else 0
    features.append(voiced_ratio)
    
    # 10. Estimate harmonics-to-noise ratio
    # Using spectral flatness as a rough proxy (lower flatness = more harmonic)
    harmonic_ratio = 1.0 - np.mean(flatness)  # Invert flatness as proxy
    features.append(harmonic_ratio)
    
    # 11. Tempo/rhythmic features - may help detect conversational patterns
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    # Pulse clarity - higher for clearer rhythmic patterns
    pulse_clarity = np.mean(onset_env) / (np.std(onset_env) + 1e-10)  # Avoid div by zero
    features.append(pulse_clarity)
    
    # 12. Energy entropy - measure of abrupt changes (useful for speech/music discrimination)
    # Split signal into frames
    frame_length = int(sr * 0.025)  # 25ms frames
    hop_length = int(sr * 0.010)   # 10ms hop
    frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
    
    # Calculate energy per frame
    energy_frames = np.sum(frames**2, axis=0) + 1e-10  # Add small constant to avoid log(0)
    
    # Normalize energies
    energy_frames_norm = energy_frames / np.sum(energy_frames)
    
    # Calculate entropy
    entropy = -np.sum(energy_frames_norm * np.log2(energy_frames_norm))
    features.append(entropy)
    
    # 13. Voice activity detection - percentage of speech vs silence
    # Simple energy-based VAD
    energy_thresh = 0.01 * np.max(energy_frames)  # Adjust threshold as needed
    speech_frames = sum(1 for e in energy_frames if e > energy_thresh)
    vad_ratio = speech_frames / len(energy_frames) if len(energy_frames) > 0 else 0
    features.append(vad_ratio)
    
    # 14. Spectral flux - measure of how quickly the spectrum changes
    # Higher for multiple speakers often
    spec = np.abs(librosa.stft(y))
    spec_flux = np.mean(librosa.onset.onset_strength(sr=sr, S=librosa.amplitude_to_db(spec)))
    features.append(spec_flux)
    
    # 15. Pitch variability - multiple speakers often have more pitch variance
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_mean = []
    for i in range(pitches.shape[1]):
        index = magnitudes[:, i].argmax()
        pitch = pitches[index, i]
        if pitch > 0:  # Consider only non-zero pitches
            pitch_mean.append(pitch)
    
    if len(pitch_mean) > 0:
        features.append(np.std(pitch_mean))
    else:
        features.append(0)
    
    return np.array(features)
    
