from pathlib import Path
import argparse
import os
import torch
import shutil
import torchaudio
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset, DataLoader
import numpy as np

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"Using device: {DEVICE}")


class XvectorDataset(Dataset):
    """Dataset for handling varying length tensors"""
    
    def __init__(self, tensor_list, wavs_path_list):
        """
        Args:
            tensor_list: List of varying length tensors of shape [1, seq_len, 768]
        """
        self.tensor_list = tensor_list
        self.wavs_path_list = wavs_path_list
        
        # Remove the batch dimension (1) from each tensor if it exists
        self.processed_tensors = []
        for tensor in tensor_list:
            if tensor.dim() == 3 and tensor.size(0) == 1:
                # Remove the batch dimension
                self.processed_tensors.append(tensor.squeeze(0))
            else:
                self.processed_tensors.append(tensor)
    
    def __len__(self):
        return len(self.processed_tensors)
    
    def __getitem__(self, idx):
        return self.processed_tensors[idx], self.wavs_path_list[idx]

def collate_fn(batch):
    """
    Custom collate function to handle tensors of different lengths
    Args:
        batch: List of tensors of shape [seq_len, 768]
    
    Returns:
        padded_batch: Tensor of shape [batch_size, max_seq_len, 768]
        lengths: List of sequence lengths
    """
    features = [item[0] for item in batch]
    wav_names = [item[1] for item in batch]
    
    # Pad sequences
    padded_feats = pad_sequence(features, batch_first=True)
    
    return padded_feats, wav_names 

def create_dataloader(tensor_list, wavs_list, batch_size=8, shuffle=False, num_workers=0):
    """
    Create a DataLoader for varying length tensors
    
    Args:
        tensor_list: List of tensors with shapes [1, seq_len, 768] where seq_len varies
        batch_size: Batch size for the DataLoader
        shuffle: Whether to shuffle the dataset
        num_workers: Number of workers for data loading
    
    Returns:
        DataLoader object
    """
    dataset = XvectorDataset(tensor_list, wavs_list)
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=torch.cuda.is_available()  # Speeds up the host to device transfer
    )
    
    return dataloader




# Model architecture
class OverlapDetectionModel(nn.Module):
    def __init__(self):
        super().__init__()
        # CNN for feature extraction
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        # self.dropout1 = nn.Dropout2d(0.3)  # Dropout after first convolutional layer
        
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.dropout2 = nn.Dropout2d(0.3)  # Dropout after second convolutional layer
        
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(64)
        # self.dropout3 = nn.Dropout2d(0.3)  # Dropout after third convolutional layer
        
        # Calculate flattened size

        # self._to_linear = self._get_conv_output((1, 34, 768))  # For 0.7 seconds of audioyy0
        self._to_linear = self._get_conv_output((1, 50, 768))  # For 1.0 seconds of audioyy0
        
        # Fully connected layers
        self.fc1 = nn.Linear(self._to_linear, 256)
        self.dropout_fc1 = nn.Dropout(0.5)  # Dropout in fully connected layer
        self.fc2 = nn.Linear(256, 1)
        
    def _get_conv_output(self, shape):
        bs = 1
        input = torch.rand(bs, *shape)
        output = self._forward_conv(input)
        return int(np.prod(output.shape))
    
    def _forward_conv(self, x):
        x = F.max_pool2d(F.relu(self.bn1(self.conv1(x))), (2, 2))
        # x = self.dropout1(x)  # Apply dropout
        x = F.max_pool2d(F.relu(self.bn2(self.conv2(x))), (2, 2))
        x = self.dropout2(x)  # Apply dropout
        x = F.max_pool2d(F.relu(self.bn3(self.conv3(x))), (2, 2))
        # x = self.dropout3(x)  # Apply dropout
        return x
    
    def forward(self, x):
        x = self._forward_conv(x)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout_fc1(x)  # Apply dropout
        x = self.fc2(x)
        return torch.sigmoid(x)


def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")

root_dir_ex = Path.home().joinpath('Dropbox')
dt_pretrained_ex = root_dir_ex.joinpath('SpeechFall2022','SpeakerLID_GT_code','Chunks_pipeline','best_overlap_detection_model_xvectors_May20.pth')

base_dir_ex = root_dir_ex.joinpath('DATASETS_AUDIO/Proposal_runs/TTS3_dt/STG_2/STG2_EXP040-SHAS-DV')
chunks_wavs_ex = base_dir_ex / "wav_chunks_raw"
filtered_chunks_wavs_ex = base_dir_ex / "wav_chunks2"

# Create the output folder if it doesn't exist with pathlib
filtered_chunks_wavs_ex.mkdir(parents=True, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('--stg2_chunks_wavs', type=valid_path, default=chunks_wavs_ex, help='Stg2 chunks wavs folder path')
parser.add_argument('--stg2_dt_pretrained', type=valid_path, default=dt_pretrained_ex, help='Stg2 Pretrained CNN X-vectors model')
parser.add_argument('--stg2_filtered_chunks_wavs', type=valid_path, default=filtered_chunks_wavs_ex, help='Stg1 VAD csvs folder path')
parser.add_argument('--stg2_dt_th', type=float, default=0.8, help='Stg2 double talk detection threshold')

args = parser.parse_args()

wav_folder_path = args.stg2_chunks_wavs
pretrained_model_path = args.stg2_dt_pretrained 
output_wav_folder_path = args.stg2_filtered_chunks_wavs
binary_th = args.stg2_dt_th

# Temp extra output folder
overlap_output_wav_folder_path = output_wav_folder_path / "overlap_segments"

# Create the output folder if it doesn't exist with pathlib
overlap_output_wav_folder_path.mkdir(parents=True, exist_ok=True)

verbose = True

"""Run inference on a single audio file"""
# Load model
model = OverlapDetectionModel()
model.load_state_dict(torch.load(pretrained_model_path, map_location=DEVICE))
model.to(DEVICE)
model.eval()

# Get all wav files
wav_files = list(wav_folder_path.glob("*.wav"))
print(f"Found {len(wav_files)} wav files")

wavlm_model = torchaudio.pipelines.WAVLM_BASE.get_model().to(DEVICE)
wavlm_model.eval()

unpadded_features = []
# Process each wav file
for current_wav_path in wav_files:
    # Load waveform
    waveform, sample_rate = torchaudio.load(current_wav_path)

    with torch.no_grad():
        current_features = wavlm_model(waveform.to(DEVICE))
        unpadded_features.append(current_features[0].to('cpu'))

    
# Create dataloader
dataloader = create_dataloader(unpadded_features, wav_files, batch_size=32)
    
# Example of inference loop
with torch.no_grad():
    for current_batch, current_wavs_paths in dataloader:
        # Move batch to device
        current_batch = current_batch.to(DEVICE)

        # Reshape to [batch_size, 1, seq_len, 768]
        current_batch = current_batch.unsqueeze(1)
        
        print(f"Batch shape: {current_batch.shape}")
            
        output = model(current_batch)

        # Calculate the prediction for the batch
        predictions = (output >= binary_th).int()

        # Confidence: if pred == 1, use x; if pred == 0, use 1 - x
        confidence = predictions * output + (1 - predictions) * (1 - output)

        # Print predictions and confidence along with the wav file names
        for wav_path, pred, conf in zip(current_wavs_paths, predictions, confidence):
            print(f"Wav: {wav_path.stem}, Prediction: {pred.item()}, Confidence: {conf.item()}")

        # Save the wav files with prediction = 1 in output folder
        for wav_path, pred in zip(current_wavs_paths, predictions):
            if pred.item() == 0:
                # Copy the wav file to the output folder
                shutil.copy(wav_path, output_wav_folder_path / wav_path.name)
            else:
                # Copy the wav file to the overlap output folder
                shutil.copy(wav_path, overlap_output_wav_folder_path / wav_path.name)
        
        # Store a csv file with the wav names and predictions
        csv_filename = os.path.join(output_wav_folder_path, "dt_predictions.csv")
        with open(csv_filename, 'a') as f:
            for wav_path, pred, conf in zip(current_wavs_paths, predictions, confidence):
                # start_time and end_time are the last 2 substrings of the wav_path name with underscore
                wav_path_parts = wav_path.stem.split('_')
                start_time = wav_path_parts[-2]
                end_time = wav_path_parts[-1]
                # write confidence with 2 decimal points
                current_conf = round(conf.item(), 2)
                f.write(f"{wav_path.name}\t{start_time}\t{end_time}\t{pred.item()}\t{current_conf}\n")


