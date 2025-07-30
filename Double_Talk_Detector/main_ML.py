import os
import numpy as np
import pandas as pd
import librosa
import pickle
from tqdm import tqdm
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings('ignore')

# Constants
SAMPLE_RATE = 16000  # Default sample rate, adjust if your files differ
MAX_DURATION = 1  # Maximum audio length in seconds to analyze (in seconds)


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


def process_data(data_dir):
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


def train_models(X_train, y_train, X_val, y_val):
    """Train and compare multiple ML models"""
    # Initialize models to test
    models = {
        'Random Forest': RandomForestClassifier(random_state=42),
        'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss'),
        'SVM': SVC(probability=True, random_state=42)
    }
    
    # Parameter grids for each model
    param_grids = {
        'Random Forest': {
            'n_estimators': [100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        },
        'XGBoost': {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.1, 0.2],
            'subsample': [0.8, 1.0],
            'colsample_bytree': [0.8, 1.0]
        },
        'SVM': {
            'C': [1, 10],
            'gamma': ['scale', 'auto'],
            'kernel': ['rbf', 'linear']
        }
    }
    
    best_models = {}
    best_val_score = 0
    best_model_name = None
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    # Save scaler for later use
    joblib.dump(scaler, 'feature_scaler.joblib')
    
    # Train and tune each model
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Create and train pipeline with Grid Search
        pipeline = GridSearchCV(
            model,
            param_grids[name],
            cv=5,
            scoring='f1',
            n_jobs=-1,
            verbose=1
        )
        
        pipeline.fit(X_train_scaled, y_train)
        
        # Evaluate on validation set
        y_val_pred = pipeline.predict(X_val_scaled)
        val_accuracy = accuracy_score(y_val, y_val_pred)
        val_f1 = f1_score(y_val, y_val_pred)
        
        print(f"{name} - Validation Accuracy: {val_accuracy:.4f}, F1: {val_f1:.4f}")
        print(f"Best parameters: {pipeline.best_params_}")
        
        # Save model
        best_models[name] = pipeline
        
        # Track best model
        if val_f1 > best_val_score:
            best_val_score = val_f1
            best_model_name = name
    
    print(f"\nBest model: {best_model_name} with F1 score: {best_val_score:.4f}")
    
    # Save best model
    joblib.dump(best_models[best_model_name], f'best_model_{best_model_name.lower().replace(" ", "_")}.joblib')
    
    return best_models, best_model_name


def evaluate_model(model, X_test, y_test, feature_names=None):
    """Evaluate the best model on the test set"""
    # Load scaler
    scaler = joblib.load('feature_scaler.joblib')
    X_test_scaled = scaler.transform(X_test)
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    
    # Print results
    print("\nTest Results:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print("\nClassification Report:")
    print(report)
    
    # Plot confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Single', 'Multiple'],
                yticklabels=['Single', 'Multiple'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig('confusion_matrix_ml.png')
    plt.close()
    
    # Feature importance analysis (if applicable)
    if hasattr(model, 'feature_importances_') or (hasattr(model, 'best_estimator_') and hasattr(model.best_estimator_, 'feature_importances_')):
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            importances = model.best_estimator_.feature_importances_
        
        if feature_names is not None:
            # Create a DataFrame for better visualization
            feature_importance = pd.DataFrame({
                'Feature': feature_names,
                'Importance': importances
            })
            feature_importance = feature_importance.sort_values('Importance', ascending=False)
            
            # Plot feature importance
            plt.figure(figsize=(12, 10))
            sns.barplot(x='Importance', y='Feature', data=feature_importance.head(20))
            plt.title('Top 20 Feature Importances')
            plt.tight_layout()
            plt.savefig('feature_importance.png')
            plt.close()
            
            print("\nTop 10 Important Features:")
            for idx, row in feature_importance.head(10).iterrows():
                print(f"{row['Feature']}: {row['Importance']:.4f}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': conf_matrix,
        'y_pred': y_pred,
        'y_prob': y_prob
    }


def inference(model_path, audio_file):
    """Run inference on a single audio file"""
    # Load model and scaler
    model = joblib.load(model_path)
    scaler = joblib.load('feature_scaler.joblib')
    
    # Extract features
    features = extract_features(audio_file)
    
    if features is None:
        print(f"Could not extract features from {audio_file}")
        return None, None
    
    # Scale features
    features_scaled = scaler.transform(features.reshape(1, -1))
    
    # Make prediction
    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0][prediction]
    
    result = "Multiple speakers" if prediction == 1 else "Single speaker"
    
    print(f"Prediction: {result}")
    print(f"Confidence: {probability:.4f}")
    
    return result, probability


def analyze_errors(best_model, X_test, y_test, file_paths=None):
    """Analyze errors made by the model"""
    # Load scaler
    scaler = joblib.load('feature_scaler.joblib')
    X_test_scaled = scaler.transform(X_test)
    
    # Make predictions
    y_pred = best_model.predict(X_test_scaled)
    y_prob = best_model.predict_proba(X_test_scaled)[:, 1]
    
    # Identify incorrect predictions
    incorrect_indices = np.where(y_pred != y_test)[0]
    
    # Sort by confidence (probability)
    confidences = np.maximum(y_prob, 1 - y_prob)  # Get confidence regardless of class
    incorrect_data = list(zip(incorrect_indices, confidences[incorrect_indices]))
    incorrect_data.sort(key=lambda x: x[1], reverse=True)
    
    print("\nMost confident errors:")
    for idx, conf in incorrect_data[:10]:  # Show top 10 confident errors
        true_label = "Multiple speakers" if y_test[idx] == 1 else "Single speaker"
        pred_label = "Multiple speakers" if y_pred[idx] == 1 else "Single speaker"
        
        print(f"Sample {idx} - True: {true_label}, Predicted: {pred_label}, Confidence: {conf:.4f}")
        if file_paths is not None:
            print(f"  File: {file_paths[idx]}")
    
    return incorrect_indices


def main():
    # Define data directory

    root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/TTS3_dt/overlapping_gt/output_segments7')
    data_dir = root_dir / "dataset7"
    
    # Process data and extract features
    X_train, X_val, X_test, y_train, y_val, y_test, feature_names = process_data(data_dir)
    
    # # Save the processed data for future use
    # np.save('X_train.npy', X_train)
    # np.save('X_val.npy', X_val)
    # np.save('X_test.npy', X_test)
    # np.save('y_train.npy', y_train)
    # np.save('y_val.npy', y_val)
    # np.save('y_test.npy', y_test)
    
    # Train models
    best_models, best_model_name = train_models(X_train, y_train, X_val, y_val)
    
    # Evaluate best model
    best_model = best_models[best_model_name]
    metrics = evaluate_model(best_model, X_test, y_test, feature_names)
    
    print(f"\nTrained and evaluated {best_model_name} model successfully!")
    print(f"F1 Score: {metrics['f1']:.4f}")
    
    # Optionally analyze errors
    analyze_errors(best_model, X_test, y_test)


if __name__ == "__main__":
    main()