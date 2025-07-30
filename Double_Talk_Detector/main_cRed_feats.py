import os
import numpy as np
import pandas as pd
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import librosa
from tqdm import tqdm

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# Constants
SAMPLE_RATE = 16000  # Default sample rate, adjust if your files differ
MAX_LENGTH = 1  # Maximum audio length in seconds
BATCH_SIZE = 16 
NUM_EPOCHS = 100
LEARNING_RATE = 1e-4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


def extract_features(file_path):
    """
    Extract audio features from a given file path.
    
    Features include:
    - MFCCs (mean & std)
    - Spectral centroid (mean & std)
    - Zero crossing rate (mean & std)
    - Spectral rolloff (mean & std)
    - Spectral contrast (mean & std)
    - Spectral bandwidth (mean & std)
    - RMS energy (mean & std)
    - Speech rate estimation
    - Harmonic-to-noise ratio
    - Voice activity percentage
    """
    try:
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
    
    except Exception as e:
        print(f"Error extracting features from {file_path}: {e}")
        return None


def process_data_feats(data_dir):
    """Process data directory and extract features from all WAV files"""
    all_files = []
    labels = []
    
    # Walk through the directory to find all WAV files
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.wav'):
                file_path = os.path.join(root, file)
                all_files.append(file_path)
                
                # Determine label based on filename
                if file.startswith('single_'):
                    # Single speaker (0)
                    labels.append(0)
                elif file.startswith('overlap_'):
                    # Multiple speakers (1)
                    labels.append(1)
                else:
                    print(f"Warning: Unknown file pattern: {file}")
                    continue
    
    # Create a DataFrame for easier manipulation
    df = pd.DataFrame({'file_path': all_files, 'label': labels})
    
    # Extract features for each file
    features_list = []
    valid_indices = []
    
    print("Extracting features from audio files...")
    for idx, file_path in enumerate(tqdm(df['file_path'])):
        features = extract_features(file_path)
        if features is not None:
            features_list.append(features)
            valid_indices.append(idx)
    
    # Filter out files that couldn't be processed
    df = df.iloc[valid_indices].reset_index(drop=True)
    
    # Convert features list to numpy array
    X = np.array(features_list)
    y = df['label'].values
    
    # Split data into train, validation, and test sets (70%, 15%, 15%)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
    
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Save feature names for interpretation later
    feature_names = [
        # MFCCs (13 mean + 13 std)
        *[f"mfcc{i+1}_mean" for i in range(13)],
        *[f"mfcc{i+1}_std" for i in range(13)],
        # Spectral features
        "spectral_centroid_mean", "spectral_centroid_std",
        "zero_crossing_rate_mean", "zero_crossing_rate_std",
        "spectral_rolloff_mean", "spectral_rolloff_std",
        "spectral_contrast_mean", "spectral_contrast_std",
        "spectral_bandwidth_mean", "spectral_bandwidth_std",
        "rms_energy_mean", "rms_energy_std",
        "spectral_flatness_mean", "spectral_flatness_std",
        "voiced_ratio",
        "harmonic_ratio",
        "pulse_clarity",
        "energy_entropy",
        "vad_ratio",
        "spectral_flux",
        "pitch_std"
    ]
    
    return X_train, X_val, X_test, y_train, y_val, y_test, feature_names

# Dataset class for audio files
class SpeechOverlapDataset(Dataset):
    def __init__(self, file_paths, labels, transform=None):
        self.file_paths = file_paths
        self.labels = labels
        self.transform = transform
        self.max_samples = MAX_LENGTH * SAMPLE_RATE
    
    def __len__(self):
        return len(self.file_paths)
    
    def __getitem__(self, idx):
        audio_path = self.file_paths[idx]
        label = self.labels[idx]
        
        # Load audio file
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        # Resample if needed
        if sample_rate != SAMPLE_RATE:
            resampler = torchaudio.transforms.Resample(sample_rate, SAMPLE_RATE)
            waveform = resampler(waveform)
        
        # Ensure consistent length
        if waveform.shape[1] < self.max_samples:
            # Pad with zeros if shorter
            padding = self.max_samples - waveform.shape[1]
            waveform = F.pad(waveform, (0, padding))
        else:
            # Truncate if longer
            waveform = waveform[:, :self.max_samples]
        
        # Apply transforms
        if self.transform:
            waveform = self.transform(waveform)
        
        return waveform, label

# Feature extraction functions
class FeatureExtractor(nn.Module):
    def __init__(self, sample_rate=SAMPLE_RATE, n_mels=128, n_fft=1024, hop_length=512):
        super().__init__()
        self.mel_spectrogram = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            n_mels=n_mels,
        )
        self.amplitude_to_db = torchaudio.transforms.AmplitudeToDB()
        
    def forward(self, waveform):
        mel_spec = self.mel_spectrogram(waveform)
        log_mel_spec = self.amplitude_to_db(mel_spec)
        return log_mel_spec

# Model architecture
class OverlapDetectionModel(nn.Module):
    def __init__(self, n_mels=128):
        super().__init__()
        # CNN for feature extraction
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        # self.conv3 = nn.Conv2d(8, 16, kernel_size=3, stride=1, padding=1)
        # self.bn3 = nn.BatchNorm2d(16)
        # self.conv4 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        # self.bn4 = nn.BatchNorm2d(32)
        
        # Calculate flattened size
        # self._to_linear = self._get_conv_output((1, n_mels, MAX_LENGTH * SAMPLE_RATE // 512))
        self._to_linear = self._get_conv_output((1, n_mels, 32))
       
        # Fully connected layers
        self.fc1 = nn.Linear(self._to_linear, 64)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(64, 1)
        
    def _get_conv_output(self, shape):
        print(f"Input shape for conv layers: {shape}")  # Debugging line
        bs = 1
        input = torch.rand(bs, *shape)
        output = self._forward_conv(input)
        # Print shape for debugging
        num_elements = int(np.prod(output.shape))
        # Print shape for debugging
        # print(f"Output shape after conv layers: {output.shape}, Number of elements: {num_elements}")
        return int(np.prod(output.shape))
    
    def _forward_conv(self, x):
        # Print shape for debugging
        # print(f"Input shape before conv layers: {x.shape}")  # Debugging line
        x = F.max_pool2d(F.relu(self.bn1(self.conv1(x))), (2, 2))
        # Print shape for debugging
        # print(f"Shape after conv1: {x.shape}")  # Debugging line
        x = F.max_pool2d(F.relu(self.bn2(self.conv2(x))), (2, 2))
        # Print shape for debugging
        # print(f"Shape after conv2: {x.shape}")  # Debugging line
        # x = F.max_pool2d(F.relu(self.bn3(self.conv3(x))), (2, 2))
        # Print shape for debugging
        # print(f"Shape after conv3: {x.shape}")  # Debugging line
        # x = F.max_pool2d(F.relu(self.bn4(self.conv4(x))), (2, 2))
        # Print shape for debugging
        # print(f"Shape after conv4: {x.shape}")

        return x
    
    def forward(self, x):
        x = self._forward_conv(x)
        # print(f"Shape after conv layers: {x.shape}")  # Debugging line
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return torch.sigmoid(x)

def process_data(data_dir):
    """Process data directory and create train/val/test splits"""
    all_files = []
    labels = []
    
    # Walk through the directory to find all WAV files
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.wav'):
                file_path = os.path.join(root, file)
                all_files.append(file_path)
                
                # Determine label based on filename
                if file.startswith('single_'):
                    # Single speaker (0)
                    labels.append(0)
                elif file.startswith('overlap_'):
                    # Multiple speakers (1)
                    labels.append(1)
                else:
                    print(f"Warning: Unknown file pattern: {file}")
                    continue
    
    # Create a DataFrame for easier manipulation
    df = pd.DataFrame({'file_path': all_files, 'label': labels})
    
    # Split data into train, validation, and test sets (70%, 15%, 15%)
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42, stratify=df['label'])
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label'])
    
    print(f"Training samples: {len(train_df)}")
    print(f"Validation samples: {len(val_df)}")
    print(f"Testing samples: {len(test_df)}")
    
    return train_df, val_df, test_df

def create_dataloaders(train_df, val_df, test_df):
    """Create DataLoader objects for training, validation, and testing"""
    feature_extractor = FeatureExtractor()
    
    # Custom transform function
    def transform(waveform):
        with torch.no_grad():
            return feature_extractor(waveform)
    
    # Create datasets
    train_dataset = SpeechOverlapDataset(
        train_df['file_path'].values,
        train_df['label'].values,
        transform=transform
    )
    
    val_dataset = SpeechOverlapDataset(
        val_df['file_path'].values,
        val_df['label'].values,
        transform=transform
    )
    
    test_dataset = SpeechOverlapDataset(
        test_df['file_path'].values,
        test_df['label'].values,
        transform=transform
    )
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=4,
        pin_memory=True if DEVICE.type == 'cuda' else False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=4,
        pin_memory=True if DEVICE.type == 'cuda' else False
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=4,
        pin_memory=True if DEVICE.type == 'cuda' else False
    )
    
    return train_loader, val_loader, test_loader

def train_model(output_dir, model, train_loader, val_loader, criterion, optimizer, scheduler=None, num_epochs=NUM_EPOCHS):
    """Train the model and validate after each epoch"""
    model.to(DEVICE)
    best_val_loss = float('inf')
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs} [Train]")
        for inputs, targets in progress_bar:
            inputs = inputs.to(DEVICE)
            targets = targets.float().unsqueeze(1).to(DEVICE)
            
            # Zero the parameter gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            
            # Statistics
            train_loss += loss.item() * inputs.size(0)
            predicted = (outputs >= 0.5).float()
            train_correct += (predicted == targets).sum().item()
            train_total += targets.size(0)
            
            progress_bar.set_postfix({
                'loss': loss.item(),
                'acc': train_correct / train_total
            })
        
        avg_train_loss = train_loss / len(train_loader.dataset)
        train_accuracy = train_correct / train_total
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            progress_bar = tqdm(val_loader, desc=f"Epoch {epoch+1}/{num_epochs} [Val]")
            for inputs, targets in progress_bar:
                inputs = inputs.to(DEVICE)
                targets = targets.float().unsqueeze(1).to(DEVICE)
                
                # Forward pass
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                
                # Statistics
                val_loss += loss.item() * inputs.size(0)
                predicted = (outputs >= 0.5).float()
                val_correct += (predicted == targets).sum().item()
                val_total += targets.size(0)
                
                progress_bar.set_postfix({
                    'loss': loss.item(),
                    'acc': val_correct / val_total
                })
        
        avg_val_loss = val_loss / len(val_loader.dataset)
        val_accuracy = val_correct / val_total
        
        # Update learning rate scheduler if provided
        if scheduler:
            scheduler.step(avg_val_loss)
        
        # Print statistics
        print(f"Epoch {epoch+1}/{num_epochs}")
        print(f"Train Loss: {avg_train_loss:.4f}, Train Acc: {train_accuracy:.4f}")
        print(f"Val Loss: {avg_val_loss:.4f}, Val Acc: {val_accuracy:.4f}")
        print("-" * 50)
        
        # Save model if it's the best so far
        chk_path = output_dir / 'best_overlap_detection_model.pth'
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), chk_path )
            print("Saved new best model!")
        
        # Update history
        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        history['train_acc'].append(train_accuracy)
        history['val_acc'].append(val_accuracy)
    
    return model, history

def evaluate_model(model, test_loader):
    """Evaluate the model on the test set"""
    model.eval()
    model.to(DEVICE)
    
    all_predictions = []
    all_targets = []
    
    with torch.no_grad():
        for inputs, targets in tqdm(test_loader, desc="Evaluating"):
            inputs = inputs.to(DEVICE)
            targets = targets.float().to(DEVICE)
            
            # Forward pass
            outputs = model(inputs)
            predicted = (outputs >= 0.5).float().squeeze().cpu().numpy()
            
            # Store predictions and targets
            all_predictions.extend(predicted.tolist() if isinstance(predicted, np.ndarray) else [predicted])
            all_targets.extend(targets.cpu().numpy().tolist())
    
    # Calculate metrics
    accuracy = accuracy_score(all_targets, all_predictions)
    precision = precision_score(all_targets, all_predictions, zero_division=0)
    recall = recall_score(all_targets, all_predictions, zero_division=0)
    f1 = f1_score(all_targets, all_predictions, zero_division=0)
    conf_matrix = confusion_matrix(all_targets, all_predictions)
    
    print("\nTest Results:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print("Confusion Matrix:")
    print(conf_matrix)
    
    # Plot confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Single', 'Multiple'],
                yticklabels=['Single', 'Multiple'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig('confusion_matrix.png')
    plt.close()
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': conf_matrix
    }

def plot_training_history(history, output_dir):
    """Plot training and validation loss/accuracy over epochs"""
    plt.figure(figsize=(12, 5))
    
    # Plot loss
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    
    # Plot accuracy
    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Accuracy')
    plt.plot(history['val_acc'], label='Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.legend()
    
    plt.tight_layout()
    fig_path = output_dir / 'cnn_training_history.png' 
    plt.savefig(fig_path)
    plt.close()

def inference(model_path, audio_file):
    """Run inference on a single audio file"""
    # Load model
    model = OverlapDetectionModel()
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    
    # Load and preprocess audio
    waveform, sample_rate = torchaudio.load(audio_file)
    
    # Convert to mono if stereo
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    
    # Resample if needed
    if sample_rate != SAMPLE_RATE:
        resampler = torchaudio.transforms.Resample(sample_rate, SAMPLE_RATE)
        waveform = resampler(waveform)
    
    # Ensure consistent length
    max_samples = MAX_LENGTH * SAMPLE_RATE
    if waveform.shape[1] < max_samples:
        # Pad with zeros if shorter
        padding = max_samples - waveform.shape[1]
        waveform = F.pad(waveform, (0, padding))
    else:
        # Truncate if longer
        waveform = waveform[:, :max_samples]
    
    # Extract features
    feature_extractor = FeatureExtractor()
    features = feature_extractor(waveform).unsqueeze(0).to(DEVICE)
    
    # Make prediction
    with torch.no_grad():
        output = model(features)
        prediction = (output >= 0.5).float().item()
        confidence = output.item() if prediction == 1 else 1 - output.item()
    
    result = "Multiple speakers" if prediction == 1 else "Single speaker"
    
    print(f"Prediction: {result}")
    print(f"Confidence: {confidence:.4f}")
    
    return result, confidence

def main():
    # Define data directory

    root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/TTS3_dt/overlapping_gt/output_segments7')
    data_dir = root_dir / "dataset7"
    output_dir = root_dir / "CNNred_15K_4"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process data
    train_df, val_df, test_df = process_data(data_dir)
    
    # Create data loaders
    train_loader, val_loader, test_loader = create_dataloaders(train_df, val_df, test_df)
    
    # Initialize model, loss function, and optimizer
    model = OverlapDetectionModel()
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=3, verbose=True)
    
    # Train model
    model, history = train_model(
        output_dir, model, train_loader, val_loader, criterion, optimizer, scheduler, NUM_EPOCHS
    )
    
    # Plot training history
    plot_training_history(history, output_dir)
    
    # Load best model and evaluate
    chk_path = output_dir / 'best_overlap_detection_model.pth'
    model.load_state_dict(torch.load(chk_path))
    metrics = evaluate_model(model, test_loader)
    
    print("\nTraining and evaluation complete!")

if __name__ == "__main__":
    main()