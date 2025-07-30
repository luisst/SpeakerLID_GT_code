import os
import torch
import torchaudio
from pathlib import Path
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Dataset class (same as before)
class OverlapDataset(Dataset):
    def __init__(self, folder_path, max_len_sec=5):
        self.filepaths = []
        self.labels = []
        self.max_len_sec = max_len_sec
        self.sr = 16000

        for fname in os.listdir(folder_path):
            if fname.endswith(".wav"):
                self.filepaths.append(os.path.join(folder_path, fname))
                label = 1 if "overlap" in fname.lower() else 0
                self.labels.append(label)

        self.processor = torchaudio.pipelines.WAVLM_BASE.get_model().to(device)
        self.resampler = torchaudio.transforms.Resample(orig_freq=44100, new_freq=self.sr)

    def __len__(self):
        return len(self.filepaths)

    def __getitem__(self, idx):
        wav_path = self.filepaths[idx]
        label = self.labels[idx]

        waveform, sr = torchaudio.load(wav_path)
        if sr != self.sr:
            waveform = self.resampler(waveform)

        waveform = waveform[:, :self.max_len_sec * self.sr]
        if waveform.shape[1] < self.max_len_sec * self.sr:
            pad = self.max_len_sec * self.sr - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, pad))

        with torch.no_grad():
            emb = self.processor.extract_features(waveform.to(device))[0][-1]
            emb = emb.mean(dim=1).squeeze().cpu().numpy()

        return emb, label

# Feature extraction
def extract_embeddings(dataset):
    loader = DataLoader(dataset, batch_size=1, shuffle=False)
    embeddings, labels = [], []

    for x, y in loader:
        embeddings.append(x.squeeze(0).numpy())
        labels.append(y.item())
    return np.array(embeddings), np.array(labels)

# Run clustering
def run_clustering(X, y_true, n_clusters=2):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    y_pred = kmeans.fit_predict(X)

    # Map cluster labels to real labels via majority voting
    cluster_map = {}
    for cluster in range(n_clusters):
        indices = np.where(y_pred == cluster)[0]
        majority_label = int(np.round(np.mean(y_true[indices])))
        cluster_map[cluster] = majority_label

    y_pred_mapped = np.array([cluster_map[c] for c in y_pred])
    print("Clustering Classification Report:\n", classification_report(y_true, y_pred_mapped, target_names=["Single", "Overlap"]))
    return y_pred, y_pred_mapped, kmeans

# Visualization
def plot_pca(X, y_pred):
    X_pca = PCA(n_components=2).fit_transform(X)
    plt.figure(figsize=(8, 6))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y_pred, cmap='viridis', alpha=0.6)
    plt.title("PCA of Embeddings with Cluster Assignments")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.grid(True)
    plt.show()

# === Run pipeline ===

root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/DoubleTalk/')
folder = root_dir / "double_talk_dataset7"
dataset = OverlapDataset(folder)
X, y = extract_embeddings(dataset)
y_pred, y_pred_mapped, kmeans = run_clustering(X, y)
plot_pca(X, y_pred)
