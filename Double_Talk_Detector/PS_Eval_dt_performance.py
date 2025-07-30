from pyannote.core import Segment, Timeline
from pyannote.metrics.detection import DetectionPrecisionRecallFMeasure
import pandas as pd
from pathlib import Path
from pyannote.core import Annotation
import numpy as np

gt_path = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\TTS3_dt\GT_final\DT_merged_gt.csv")
pred_path = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\TTS3_dt\STG_2\STG2_EXP040-SHAS-DV\wav_chunks\dt_predictions.csv")
vad_path = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\TTS3_dt\STG_1\STG1_SHAS\shas_output_csv\dt_test.txt")

gt_df = pd.read_csv(gt_path, sep='\t')
pred_df = pd.read_csv(pred_path, sep='\t')
vad_df = pd.read_csv(vad_path, sep='\t', header=None, names=['filename', 'start_time', 'end_time'])

# Convert 'start_time' and 'end_time' columns to float
gt_df['start_time'] = gt_df['start_time'].astype(float)
gt_df['end_time'] = gt_df['end_time'].astype(float)
pred_df['start_time'] = pred_df['start_time'].astype(float)
pred_df['end_time'] = pred_df['end_time'].astype(float)
vad_df['start_time'] = vad_df['start_time'].astype(float)
vad_df['end_time'] = vad_df['end_time'].astype(float)


# --- Helper: Check if a segment overlaps any VAD region ---
def overlaps_vad(row, vad_df):
    seg_start, seg_end = row['start_time'], row['end_time']
    overlaps = ((vad_df['start_time'] < seg_end) & (vad_df['end_time'] > seg_start)).any()
    return overlaps

# --- Filter GT: Only double-talk and overlaps VAD ---
# Step 1: Convert 'speaker_id' column to string type (in case it's not already)
gt_df['speaker_id'] = gt_df['speaker_id'].astype(str)

# Step 2: Create a boolean mask where 'speaker_id' contains the '+' character
double_talk_mask = gt_df['speaker_id'].str.contains('+', regex=False)

# Step 3: Filter the DataFrame using the mask to keep only double-talk segments
gt_df_filtered = gt_df[double_talk_mask]
gt_df_filtered = gt_df_filtered[gt_df_filtered.apply(lambda row: overlaps_vad(row, vad_df), axis=1)]

# --- Filter Predictions: Only overlap==1 and overlaps VAD ---
pred_df_filtered = pred_df[pred_df['overlap'] == 1]
pred_df_filtered = pred_df_filtered[pred_df_filtered.apply(lambda row: overlaps_vad(row, vad_df), axis=1)]

# --- Convert filtered DataFrames to Timelines ---


# Example: gt_df_filtered with 'start_time', 'end_time', 'speaker_id'
gt_annotation = Annotation()
for _, row in gt_df_filtered.iterrows():
    gt_annotation[Segment(row['start_time'], row['end_time'])] = 'overlap' 

pred_annotation = Annotation()
for _, row in pred_df_filtered.iterrows():
    pred_annotation[Segment(row['start_time'], row['end_time'])] = 'overlap'

# --- VAD Timeline for UEM ---
vad_timeline = Timeline()
for _, row in vad_df.iterrows():
    seg = Segment(row['start_time'], row['end_time'])
    vad_timeline.add(seg)

# --- Evaluate ---
prec_recall_f1 = DetectionPrecisionRecallFMeasure()
results_components = prec_recall_f1.compute_components(reference=gt_annotation, hypothesis=pred_annotation, uem=vad_timeline)
results_metrics = prec_recall_f1.compute_metrics(results_components)

# results_metrics = [precision, recall, f1_score]
# Print results
print(f"Precision: {results_metrics[0]:.3f}")
print(f"Recall: {results_metrics[1]:.3f}")
print(f"F1 Score: {results_metrics[2]:.3f}")

# Save gt_filtered and pred_filtered to CSV
output_gt_path = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\TTS3_dt\GT_final\DT_merged_gt_filtered.csv")
output_pred_path = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Proposal_runs\TTS3_dt\STG_2\STG2_EXP040-SHAS-DV\wav_chunks\dt_predictions_filtered.csv")
gt_df_filtered.to_csv(output_gt_path, sep='\t', index=False)
pred_df_filtered.to_csv(output_pred_path, sep='\t', index=False)
print(f"Filtered GT saved to: {output_gt_path}")
print(f"Filtered Predictions saved to: {output_pred_path}")


### Add an extra and simple metric.
## Count how many of the pred_df_filtered segments are in the gt_df, use 1 second resolution, allow for some tolerance

# Accuracy of 1 second resolution


def count_fully_overlapped_1s_segments(gt_df, pred_df):
    # Find global min/max time
    min_time = min(gt_df['start_time'].min(), pred_df['start_time'].min())
    max_time = max(gt_df['end_time'].max(), pred_df['end_time'].max())
    # Create 1s bins
    bins = np.arange(np.floor(min_time), np.ceil(max_time), 1.0)
    count = 0
    for b_start in bins:
        b_end = b_start + 1.0
        # Check if this 1s segment is fully covered by any GT and any Pred segment
        gt_covers = ((gt_df['start_time'] <= b_start) & (gt_df['end_time'] >= b_end)).any()
        pred_covers = ((pred_df['start_time'] <= b_start) & (pred_df['end_time'] >= b_end)).any()
        if gt_covers and pred_covers:
            count += 1
    return count


# Count overlapping segments
overlapping_count = count_fully_overlapped_1s_segments(gt_df_filtered, pred_df_filtered)
print(f"Number of overlapping segments (with tolerance): {overlapping_count}")
# Save the count to a text file
output_count_path = output_pred_path.parent / "overlapping_count.txt"
with open(output_count_path, 'w') as f:
    f.write(f"Number of overlapping segments (with tolerance): {overlapping_count}\n")
print(f"Overlapping count saved to: {output_count_path}")