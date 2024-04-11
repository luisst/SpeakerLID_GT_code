import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from pyannote.core import Segment, Timeline
from pyannote.metrics.segmentation import SegmentationPurity, SegmentationCoverage, SegmentationPurityCoverageFMeasure, SegmentationPrecision, SegmentationRecall

# Define your audio files and their corresponding timestamps
# Replace 'audio1' and 'audio2' with your actual audio files
audio1 = 'path/to/audio1.wav'

# Load audio waveform
audio1_waveform, sample_rate = sf.read(audio1)

# Plot audio waveform
plt.figure(figsize=(10, 5))
plt.plot(np.linspace(0, len(audio1_waveform) / sample_rate, num=len(audio1_waveform)), audio1_waveform, color='black')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Audio Waveform')

# Load ground truth and hypothesis segmentations
# Replace these with your actual segmentations
ground_truth = Timeline([Segment(start, end) for start, end in [(0, 10), (20, 30), (40, 50)]])
hypothesis = Timeline([Segment(start, end) for start, end in [(0, 10), (15, 25), (35, 45)]])

# Calculate metrics
purity = SegmentationPurity()
coverage = SegmentationCoverage()
f_measure = SegmentationPurityCoverageFMeasure()
precision = SegmentationPrecision()
recall = SegmentationRecall()

purity_val = purity(ground_truth, hypothesis)
coverage_val = coverage(ground_truth, hypothesis)
f_measure_val = f_measure(ground_truth, hypothesis)
precision_val = precision(ground_truth, hypothesis)
recall_val = recall(ground_truth, hypothesis)

# Print metrics with descriptions
print("Segmentation Purity: The fraction of the duration of correctly assigned segments in the hypothesis.")
print("Segmentation Coverage: The fraction of the duration of correctly assigned segments in the ground truth.")
print("Segmentation F-Measure (Purity-Coverage F-Measure): The harmonic mean of purity and coverage, providing a balanced measure of both.")
print("Segmentation Precision: The fraction of correctly assigned segments in the hypothesis.")
print("Segmentation Recall: The fraction of correctly assigned segments in the ground truth.")

# Print metric values
print("\nMetrics Values:")
print(f"Segmentation Purity: {purity_val:.2f}")
print(f"Segmentation Coverage: {coverage_val:.2f}")
print(f"Segmentation F-Measure: {f_measure_val:.2f}")
print(f"Segmentation Precision: {precision_val:.2f}")
print(f"Segmentation Recall: {recall_val:.2f}")

# Plot metrics annotations
plt.axvline(x=0, ymin=0, ymax=1, color='red', linestyle='--', label='Ground Truth')
plt.axvline(x=10, ymin=0, ymax=1, color='red', linestyle='--')
plt.axvline(x=20, ymin=0, ymax=1, color='red', linestyle='--')
plt.axvline(x=30, ymin=0, ymax=1, color='red', linestyle='--')
plt.axvline(x=40, ymin=0, ymax=1, color='red', linestyle='--')
plt.axvline(x=50, ymin=0, ymax=1, color='red', linestyle='--')

# Plot metrics
metrics = ['Purity', 'Coverage', 'F-Measure', 'Precision', 'Recall']
values = [purity_val, coverage_val, f_measure_val, precision_val, recall_val]

for i, metric in enumerate(metrics):
    plt.text(0.1, 0.9 - i * 0.1, f'{metric}: {values[i]:.2f}', transform=plt.gca().transAxes, color='blue')

plt.legend()
plt.show()
