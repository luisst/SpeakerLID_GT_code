import os
from pathlib import Path
import torch
import torchaudio
import torchaudio.transforms as T
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Step 1: Dataset Class
class OverlapDataset(Dataset):
    def __init__(self, folder_path, max_len_sec=5):
        self.filepaths = []
        self.labels = []
        self.max_len_sec = max_len_sec
        self.sr = 16000  # WavLM expects 16kHz

        for fname in os.listdir(folder_path):
            if fname.endswith(".wav"):
                self.filepaths.append(os.path.join(folder_path, fname))
                label = 1 if "overlap" in fname.lower() else 0
                self.labels.append(label)

        self.processor = torchaudio.pipelines.WAVLM_BASE.get_model().to(device)
        self.resampler = T.Resample(orig_freq=44100, new_freq=self.sr)

    def __len__(self):
        return len(self.filepaths)

    def __getitem__(self, idx):
        wav_path = self.filepaths[idx]
        label = self.labels[idx]

        waveform, sr = torchaudio.load(wav_path)
        if sr != self.sr:
            waveform = self.resampler(waveform)

        waveform = waveform[:, :self.max_len_sec * self.sr]  # trim/pad to fixed length
        if waveform.shape[1] < self.max_len_sec * self.sr:
            pad = self.max_len_sec * self.sr - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, pad))

        with torch.no_grad():
            emb = self.processor.extract_features(waveform.to(device))[0][-1]  # last layer
            emb = emb.mean(dim=1).squeeze().cpu().numpy()  # Mean pooling

        return emb, label

# Step 2: Load Dataset and Extract Features
def extract_all_embeddings(dataset):
    embeddings, labels = [], []
    loader = DataLoader(dataset, batch_size=1, shuffle=False)

    for x, y in loader:

        # Print x shape for debugging
        print(f"x shape: {x.shape}")
        print(f"y shape: {y.shape}")

        # Print x type for debugging
        print(f"x type: {type(x)}")
        print(f"y type: {type(y)}")

        embeddings.append(x.squeeze(0).numpy())
        labels.append(y.item())
    return np.array(embeddings), np.array(labels)

# Step 3: Train Logistic Regression Classifier
def train_classifier(X, y):
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2)

    clf = LogisticRegression(max_iter=1000, class_weight={0: 1.0, 1: 2.0})  # weight overlap class more
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("Classification Report:\n", classification_report(y_test, y_pred, target_names=["Single", "Overlap"]))
    return clf

# ==== Run the pipeline ====
root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/DoubleTalk/')
folder = root_dir / "double_talk_dataset7"
dataset = OverlapDataset(folder)
X, y = extract_all_embeddings(dataset)
clf = train_classifier(X, y)
