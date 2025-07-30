import os
import torch
import torchaudio
import numpy as np
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional

# Load the model and utility functions
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=True)

# Extract utility functions
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

section_length = 0.9 
prob_avg = 0.8  # Average probability threshold for speech detection

# Configuration
root_dir = Path.home().joinpath('Dropbox/DATASETS_AUDIO/Dvectors/wavs_test_pairs')
WAV_FOLDER = root_dir / "groups_wavs_raw"
run_id = "sub_section08min"

output_dir = root_dir / run_id
output_dir.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 16000  # VAD expects 16kHz
DEVICE = torch.device('cpu')
    
class SpeechSegmentSelector:
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 512):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.chunk_duration = chunk_size / sample_rate  # Duration per chunk in seconds
        self.min_threshold = prob_avg - 0.1 # Minimum threshold for speech detection
        self.min_target_length = section_length - 0.1  # Minimum length of a segment in seconds
        self.min_target_length_chunks = int(np.ceil(self.min_target_length / self.chunk_duration))
        
    def select_best_segments(self, 
                           probabilities: List[float], 
                           filename: Optional[str] = None,
                           selected_time: float = 1.0,
                           min_probability: float = 0.5,
                           min_consecutive_chunks: int = 3,
                           overlap_tolerance: float = 0.1) -> List[Tuple[int, int, float]]:
        """
        Select the best speech segments from probability sequence.
        
        Args:
            probabilities: List of VAD probabilities for each chunk
            selected_time: Target duration in seconds
            min_probability: Minimum average probability threshold
            min_consecutive_chunks: Minimum number of consecutive chunks required
            overlap_tolerance: Allow slight overlap between segments
            
        Returns:
            List of tuples (start_chunk, end_chunk, avg_probability)
        """
        probs = np.array(probabilities)
        mean_probs = np.mean(probs)
        target_chunks = int(np.ceil(selected_time / self.chunk_duration))
        
        # Find consecutive high-probability regions
        speech_regions = self._find_speech_regions(probs, min_probability, min_consecutive_chunks)
        
        if not speech_regions:
            print(f"No speech regions found in {filename} with mean_prob={mean_probs}")
            return []

        # Score and select best segments
        segments = []
        for region_start, region_end in speech_regions:
            segment = self._select_best_subsegment(
                probs, region_start, region_end, target_chunks, selected_time
            )
            if segment:
                segments.append(segment)
        
        # Remove overlapping segments, keeping the best ones
        segments = self._remove_overlaps(segments, overlap_tolerance)
        
        return segments
    
    def _find_speech_regions(self, probabilities: np.ndarray, 
                           min_prob: float, min_chunks: int) -> List[Tuple[int, int]]:
        """Find consecutive regions above probability threshold."""
        # Apply hysteresis thresholding for more stable regions
        high_thresh = min_prob + 0.1
        low_thresh = min_prob - 0.05
        
        # Find high-confidence starts
        above_high = probabilities >= high_thresh
        regions = []
        
        i = 0
        while i < len(probabilities):
            if above_high[i]:
                start = i
                # Extend region while above low threshold
                while i < len(probabilities) and probabilities[i] >= low_thresh:
                    i += 1
                end = i
                
                if end - start >= min_chunks:
                    regions.append((start, end))
            else:
                i += 1
        
        return regions
    
    def _select_best_subsegment(self, probabilities: np.ndarray, 
                              region_start: int, region_end: int, 
                              target_chunks: int, selected_time: float) -> Optional[Tuple[int, int, float]]:
        """Select the best subsegment within a speech region using multiple criteria."""
        region_length = region_end - region_start
        
        if region_length < target_chunks and region_length > self.min_target_length_chunks:
            # Region is shorter than target - use entire region if it's good enough
            avg_prob = np.mean(probabilities[region_start:region_end])
            if avg_prob >= self.min_threshold:  # Slightly higher threshold for short segments
                print(f"Using short region {region_start}-{region_end} (length: {region_length * self.chunk_duration:.2f}s) ({avg_prob:.2f}) for {selected_time:.2f}s target")
                return (region_start, region_end, avg_prob)

            return None
        
        # Region is longer than target - find best subsegment
        best_score = -1
        best_segment = None
        
        # Allow slight extension beyond target time
        max_chunks = min(target_chunks + 2, region_length)
        
        for length in range(target_chunks, max_chunks + 1):
            for start in range(region_start, region_end - length + 1):
                end = start + length
                segment_probs = probabilities[start:end]
                
                # Multi-criteria scoring
                score = self._calculate_segment_score(segment_probs, start, end, region_start, region_end)
                
                if score > best_score:
                    best_score = score
                    best_segment = (start, end, np.mean(segment_probs))
        
        return best_segment if best_score > 0 else None
    
    def _calculate_segment_score(self, segment_probs: np.ndarray, 
                               start: int, end: int, 
                               region_start: int, region_end: int) -> float:
        """Calculate multi-criteria score for segment quality."""
        # Base score from average probability
        avg_prob = np.mean(segment_probs)
        if avg_prob < 0.5:
            return -1  # Skip low-quality segments
        
        score = avg_prob
        
        # Bonus for high minimum probability (consistency)
        min_prob = np.min(segment_probs)
        score += 0.2 * min_prob
        
        # Bonus for being centered in the region (avoid edges)
        region_length = region_end - region_start
        segment_center = (start + end) / 2
        region_center = (region_start + region_end) / 2
        center_distance = abs(segment_center - region_center) / (region_length / 2)
        center_bonus = 0.1 * (1 - center_distance)
        score += center_bonus
        
        # Bonus for stability (low variance)
        stability_bonus = 0.05 * (1 - np.std(segment_probs))
        score += max(0, stability_bonus)
        
        # Penalty for segments at the very edges of regions
        edge_penalty = 0
        if start == region_start or end == region_end:
            edge_penalty = 0.05
        score -= edge_penalty
        
        return score
    
    def _remove_overlaps(self, segments: List[Tuple[int, int, float]], 
                        tolerance: float) -> List[Tuple[int, int, float]]:
        """Remove overlapping segments, keeping the best ones."""
        if not segments:
            return []
        
        # Sort by quality (average probability)
        segments.sort(key=lambda x: x[2], reverse=True)
        
        selected = []
        tolerance_chunks = int(tolerance / self.chunk_duration)
        
        for segment in segments:
            start, end, prob = segment
            
            # Check if this segment overlaps significantly with any selected segment
            overlaps = False
            for sel_start, sel_end, _ in selected:
                overlap_start = max(start, sel_start)
                overlap_end = min(end, sel_end)
                
                if overlap_end > overlap_start:
                    overlap_length = overlap_end - overlap_start
                    if overlap_length > tolerance_chunks:
                        overlaps = True
                        break
            
            if not overlaps:
                selected.append(segment)
        
        # Sort by time order for output
        selected.sort(key=lambda x: x[0])
        return selected
    
    def get_time_ranges(self, segments: List[Tuple[int, int, float]]) -> List[Tuple[float, float, float]]:
        """Convert chunk indices to time ranges."""
        time_segments = []
        for start_chunk, end_chunk, avg_prob in segments:
            start_time = start_chunk * self.chunk_duration
            end_time = end_chunk * self.chunk_duration
            time_segments.append((start_time, end_time, avg_prob))
        return time_segments
    
    def visualize_selection(self, probabilities: List[float], segments_flags: bool, 
                          segments: List[Tuple[int, int, float]], 
                          title: str = "Speech Segment Selection"):
        """Visualize the probability sequence and selected segments."""
        plt.figure(figsize=(12, 6))
        
        # Plot probability sequence
        time_axis = np.arange(len(probabilities)) * self.chunk_duration
        plt.plot(time_axis, probabilities, 'b-', alpha=0.7, label='VAD Probability')
        
        if segments_flags:
            # Highlight selected segments
            for i, (start, end, avg_prob) in enumerate(segments):
                start_time = start * self.chunk_duration
                end_time = end * self.chunk_duration
                plt.axvspan(start_time, end_time, alpha=0.3, color='red', 
                        label=f'Selected Segment {i+1}' if i < 3 else '')
                
                # Add text annotation
                mid_time = (start_time + end_time) / 2
                plt.text(mid_time, avg_prob + 0.05, f'{avg_prob:.2f}', 
                        ha='center', va='bottom', fontsize=9)
        
        plt.xlabel('Time (seconds)')
        plt.ylabel('Speech Probability')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

# Example usage and testing
def select_subs(probabilities, current_file, selected_time, min_prob = 0.5, sample_rate=16000, chunk_size=512, visualize=True):
    
    # Initialize selector
    selector = SpeechSegmentSelector(sample_rate=sample_rate, chunk_size=chunk_size)
    
    # Add debugging information
    target_chunks = int(np.ceil(selected_time / selector.chunk_duration))
    total_chunks = len(probabilities)
    total_duration = total_chunks * selector.chunk_duration
    
    # Check speech regions before selection
    speech_regions = selector._find_speech_regions(np.array(probabilities), min_prob, 3)
    print(f"Found {len(speech_regions)} speech regions:")
    for i, (start, end) in enumerate(speech_regions):
        region_duration = (end - start) * selector.chunk_duration
        region_avg_prob = np.mean(probabilities[start:end])
        # print(f"  Region {i+1}: {start}-{end} chunks ({region_duration:.3f}s), avg_prob: {region_avg_prob:.3f}")
    
    # Select best segments
    segments = selector.select_best_segments(
        probabilities=probabilities,
        filename=current_file,
        selected_time=selected_time,
        min_probability=min_prob,
        min_consecutive_chunks=3
    )
    
    print("Selected Speech Segments:")
    print("=" * 50)

    if len(segments) > 0:
        time_segments = selector.get_time_ranges(segments)
        for i, (start_time, end_time, avg_prob) in enumerate(time_segments):
            duration = end_time - start_time
            print(f"Segment {i+1}:")
            print(f"  Time: {start_time:.3f}s - {end_time:.3f}s ({duration:.3f}s)")
            print(f"  Average Probability: {avg_prob:.3f}")
            if duration < selected_time:
                print(f"  ⚠️  WARNING: Segment is {duration:.3f}s")
            print()
    
    else:
        # Visualize results
        # selector.visualize_selection(probabilities, False, segments=segments)
        time_segments = []

    return time_segments


def my_store_audio(file_path, audio_data, sample_rate):
    """
    Save audio data to a file.
    
    Args:
        file_path: Path to save the audio file
        audio_data: Audio data as a 1D numpy array or torch tensor
        sample_rate: Sample rate of the audio
    """
    # if isinstance(audio_data, torch.Tensor):
    #     audio_data = audio_data.numpy()
    
    # Use ffmpeg to save audio as 16000 FS mono float32
    torchaudio.save(file_path, torch.tensor(audio_data).unsqueeze(0), sample_rate=sample_rate, format='wav', encoding='PCM_S', bits_per_sample=32)
    


if __name__ == "__main__":
    mean_probs = []
    max_probs = []
    file_paths = []

    output_file_tsv = output_dir / f"speech_segments_{run_id}.tsv"
    file_rows = []

    print("Processing WAVs...")
    for fname in tqdm(os.listdir(WAV_FOLDER)):
        if fname.endswith('.wav'):
            fpath = os.path.join(WAV_FOLDER, fname)
            long_wav = read_audio(
                fpath,                    # Path to audio file
                sampling_rate=16000      # Target sampling rate
            )

            # Process audio in chunks
            window_size_samples = 512

            speech_probs = []
            for i in range(0, len(long_wav), window_size_samples):
                chunk = long_wav[i:i + window_size_samples]
                if len(chunk) < window_size_samples:
                    # Pad the last chunk if necessary
                    chunk = torch.nn.functional.pad(chunk, (0, window_size_samples - len(chunk)))
                
                speech_prob = model(chunk, SAMPLE_RATE).item()
                speech_probs.append(speech_prob)
            
            speech_probs = np.array(speech_probs)
            # Print the speech_probs for debugging
            # print(f"Speech probabilities for {fname}: {speech_probs}")

            time_segments = select_subs(speech_probs, fname, section_length, min_prob=prob_avg, sample_rate=SAMPLE_RATE, chunk_size=window_size_samples, visualize=False)

            # Store results in a tsv file
            file_rows.append(f"=======================================================")
            file_rows.append(f"{fname}\t{len(time_segments)}")
            print(f"Processed {fname}: {len(time_segments)} segments found.")
            for start_time, end_time, avg_prob in time_segments:
                file_rows.append(f"{start_time:.3f}\t{end_time:.3f}\t{avg_prob:.3f}")
            
            # Save only 1 segment per file as wav
            if time_segments:
                start_time, end_time, avg_prob = time_segments[0]
                segment_duration = end_time - start_time
                if segment_duration > 0:
                    segment_wav = long_wav[int(start_time * SAMPLE_RATE):int(end_time * SAMPLE_RATE)]
                    output_segment_path = output_dir / f"{fname[:-4]}_segment.wav"
                    my_store_audio(output_segment_path, segment_wav, SAMPLE_RATE)
                    print(f"Saved segment to {output_segment_path}")
                else:
                    print(f"Segment duration is zero for {fname}, skipping save.")


            # Reset model states after processing
            model.reset_states()
    

    with open(output_file_tsv, 'w') as f:
        for row in file_rows:
            f.write(row + "\n")
