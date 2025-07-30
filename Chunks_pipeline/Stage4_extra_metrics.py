import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.stats import entropy
import argparse
import os
from pathlib import Path
from utilities_pyannote_metrics import matching_basename_pathlib_gt_pred

FRAME_STEP = 0.01  # 10ms

def load_data(gt_path, pred_path, method_name=''):
    gt = pd.read_csv(gt_path, sep="\t", header=None, names=['speaker_id', 'lang', 'start_time', 'end_time'])
    pred = pd.DataFrame()
    if method_name == 'azure':
        pred = pd.read_csv(pred_path, sep="\t", header=None, names=['cluster_id', 'start_time', 'end_time','transcript', 'prob', 'lang'])
    else:
        pred = pd.read_csv(pred_path, sep="\t", header=None, names=['filename', 'cluster_id', 'start_time', 'end_time','duration'])
    return gt, pred

def time_to_frames(start, end):
    start_idx = int(np.floor(start / FRAME_STEP))
    end_idx = int(np.ceil(end / FRAME_STEP))
    return range(start_idx, end_idx)

def build_frame_label_maps(gt, pred):
    gt_frame_map = {}
    pred_frame_map = {}

    for _, row in gt.iterrows():
        speaker = row['speaker_id']
        for frame in time_to_frames(row['start_time'], row['end_time']):
            gt_frame_map[frame] = speaker

    for _, row in pred.iterrows():
        cluster = row['cluster_id']
        for frame in time_to_frames(row['start_time'], row['end_time']):
            pred_frame_map[frame] = cluster

    return gt_frame_map, pred_frame_map

def compute_entropy_per_cluster(gt_frame_map, pred_frame_map, cluster_to_speakers):

    for frame, cluster_id in pred_frame_map.items():
        speaker_id = gt_frame_map.get(frame)
        if speaker_id is not None:
            cluster_to_speakers[cluster_id].append(speaker_id)

    entropies = {}
    for cluster_id, speaker_ids in cluster_to_speakers.items():
        total = len(speaker_ids)
        if total == 0:
            entropies[cluster_id] = 0
            continue
        unique_speakers, counts = np.unique(speaker_ids, return_counts=True)
        probs = counts / counts.sum()
        entropies[cluster_id] = entropy(probs, base=2)

    return entropies, cluster_to_speakers


def compute_all_entropies(cluster_to_speakers):

    entropies = {}
    for cluster_id, speaker_ids in cluster_to_speakers.items():
        total = len(speaker_ids)
        if total == 0:
            entropies[cluster_id] = 0
            continue
        unique_speakers, counts = np.unique(speaker_ids, return_counts=True)
        probs = counts / counts.sum()
        entropies[cluster_id] = entropy(probs, base=2)

    return entropies


def compute_precision_recall(gt_frame_map, pred_frame_map):
    tp = 0
    total_pred = 0
    total_gt = 0

    cluster_speaker_counts = defaultdict(lambda: defaultdict(int))

    for frame, cluster_id in pred_frame_map.items():
        speaker_id = gt_frame_map.get(frame)
        if speaker_id is not None:
            cluster_speaker_counts[cluster_id][speaker_id] += 1

    cluster_to_major_speaker = {
        cid: max(speakers.items(), key=lambda x: x[1])[0]
        for cid, speakers in cluster_speaker_counts.items()
    }

    for frame in set(gt_frame_map.keys()).union(set(pred_frame_map.keys())):
        gt_speaker = gt_frame_map.get(frame)
        cluster_id = pred_frame_map.get(frame)
        pred_speaker = cluster_to_major_speaker.get(cluster_id)

        if gt_speaker is not None:
            total_gt += 1
        if cluster_id is not None:
            total_pred += 1
        if gt_speaker is not None and pred_speaker is not None and gt_speaker == pred_speaker:
            tp += 1

    recall = tp / total_gt if total_gt > 0 else 0
    precision = tp / total_pred if total_pred > 0 else 0
    return precision, recall, cluster_to_major_speaker


def compute_purity(gt_frame_map, pred_frame_map):
    cluster_speaker_counts = defaultdict(lambda: defaultdict(int))

    for frame, cluster_id in pred_frame_map.items():
        speaker_id = gt_frame_map.get(frame)
        if speaker_id is not None:
            cluster_speaker_counts[cluster_id][speaker_id] += 1

    correct = sum(max(speaker_counts.values()) for speaker_counts in cluster_speaker_counts.values())
    total = sum(sum(speaker_counts.values()) for speaker_counts in cluster_speaker_counts.values())
    return correct / total if total > 0 else 0


def compute_bcubed(gt_frame_map, pred_frame_map):
    # Build reverse maps
    speaker_to_frames = defaultdict(set)
    cluster_to_frames = defaultdict(set)

    for frame, speaker_id in gt_frame_map.items():
        speaker_to_frames[speaker_id].add(frame)
    for frame, cluster_id in pred_frame_map.items():
        cluster_to_frames[cluster_id].add(frame)

    common_frames = set(gt_frame_map.keys()).intersection(pred_frame_map.keys())
    precisions = []
    recalls = []

    for frame in common_frames:
        cluster_id = pred_frame_map[frame]
        speaker_id = gt_frame_map[frame]

        cluster_frames = cluster_to_frames[cluster_id]
        speaker_frames = speaker_to_frames[speaker_id]

        intersection = cluster_frames.intersection(speaker_frames)
        precision = len(intersection) / len(cluster_frames) if cluster_frames else 0
        recall = len(intersection) / len(speaker_frames) if speaker_frames else 0

        precisions.append(precision)
        recalls.append(recall)

    b_precision = np.mean(precisions)
    b_recall = np.mean(recalls)
    return b_precision, b_recall


def compute_der(gt_frame_map, pred_frame_map, cluster_to_major_speaker):
    incorrect = 0
    total_gt = 0

    for frame, gt_speaker in gt_frame_map.items():
        cluster_id = pred_frame_map.get(frame)
        pred_speaker = cluster_to_major_speaker.get(cluster_id)
        total_gt += 1
        if pred_speaker != gt_speaker:
            incorrect += 1

    return incorrect / total_gt if total_gt > 0 else 0


def compute_per_speaker_metrics(gt_frame_map, pred_frame_map, cluster_to_major_speaker):
    speaker_frames = defaultdict(set)
    for frame, speaker in gt_frame_map.items():
        speaker_frames[speaker].add(frame)

    pred_speaker_frames = defaultdict(set)
    for frame, cluster_id in pred_frame_map.items():
        pred_speaker = cluster_to_major_speaker.get(cluster_id)
        if pred_speaker is not None:
            pred_speaker_frames[pred_speaker].add(frame)

    per_speaker = {}

    for speaker_id in speaker_frames:
        gt_set = speaker_frames[speaker_id]
        pred_set = pred_speaker_frames.get(speaker_id, set())
        intersection = gt_set.intersection(pred_set)

        tp = len(intersection)
        recall = tp / len(gt_set) if gt_set else 0
        precision = tp / len(pred_set) if pred_set else 0
        der = (len(gt_set) - tp) / len(gt_set) if gt_set else 0

        per_speaker[speaker_id] = {
            "Precision": precision,
            "Recall": recall,
            "DER": der,
            "Frames": len(gt_set)
        }

    return per_speaker


def export_report(metrics, per_speaker_metrics, clustering_report_path):
    with open(clustering_report_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(["Metric", "Value"])
        for key, value in metrics.items():
            writer.writerow([key, f"{value:.2f}"])

        writer.writerow([])
        writer.writerow(["Per-Speaker Metrics"])
        writer.writerow(["Speaker ID", "Precision", "Recall", "DER", "Frames"])
        for speaker_id, values in sorted(per_speaker_metrics.items(), key=lambda x: x[1]["DER"], reverse=True):
            writer.writerow([
                speaker_id,
                f"{values['Precision']:.2f}",
                f"{values['Recall']:.2f}",
                f"{values['DER']:.2f}",
                values['Frames']
            ])

    print(f"\n✅ Report exported to: {clustering_report_path}")



def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


base_path_ex = Path.home().joinpath('Dropbox','DATASETS_AUDIO','Proposal_runs')
csv_pred_folder_ex = base_path_ex / r'TestAO-Irmadb\STG_3\STG3_EXP010C-SHAS-DV-umap1H10\final_csv'
GT_csv_folder_ex = base_path_ex / r'TestAO-Irmadb\GT_final'
metric_output_folder_ex = base_path_ex / r'TestAO-Irmadb\STG_3\STG3_EXP010C-SHAS-DV-umap1H10\clustering_metrics'

parser = argparse.ArgumentParser()

parser.add_argument('--csv_pred_folder', type=valid_path, default=csv_pred_folder_ex, help='Folder with csv with predictions')
parser.add_argument('--GT_csv_folder', type=valid_path, default=GT_csv_folder_ex, help='Folder with GT csv files')
parser.add_argument('--metric_output_folder', type=valid_path, default=metric_output_folder_ex, help='Folder to save metrics')
parser.add_argument('--pred_suffix', default='pred', help='Suffix added to the prediction files')
parser.add_argument('--pred_extensions', default='csv', help='extension of the prediction files')
parser.add_argument('--run_name', default='default_name', help='Run ID name')
parser.add_argument('--method_name', default='default_name', help='Run ID name')

args = parser.parse_args()

csv_pred_folder = args.csv_pred_folder
GT_csv_folder = args.GT_csv_folder
metric_output_folder = args.metric_output_folder
run_name = args.run_name
method_name = args.method_name

pred_suffix_added = args.pred_suffix
pred_ext = args.pred_extensions

#G-C1L1P-Apr27-E-Irma_q2_03-08-377_GT
#G-C1L1P-Apr27-E-Irma_q2_03-08-377_pred

if pred_suffix_added == 'xx':
    pred_suffix_added = ''
    print('updating pred_suffix_added to empty string')

suffix_ext_list = [pred_ext, pred_suffix_added]

method_matches = matching_basename_pathlib_gt_pred(GT_csv_folder, csv_pred_folder, 
        gt_suffix_added='GT', pred_suffix_added=suffix_ext_list[1],
        gt_ext = 'csv', pred_ext = suffix_ext_list[0])



cluster_to_speakers = defaultdict(list)
metrics_list = []
per_speaker_metrics_list = []
pred_names_list = []

for current_gt, current_pred in method_matches:

    gt, pred = load_data(current_gt, current_pred, method_name=method_name)
    gt_frame_map, pred_frame_map = build_frame_label_maps(gt, pred)

    # Metrics
    entropies, cluster_to_speakers = compute_entropy_per_cluster(gt_frame_map, pred_frame_map, cluster_to_speakers)
    precision, recall, cluster_to_major_speaker = compute_precision_recall(gt_frame_map, pred_frame_map)
    purity = compute_purity(gt_frame_map, pred_frame_map)
    b_precision, b_recall = compute_bcubed(gt_frame_map, pred_frame_map)
    der = compute_der(gt_frame_map, pred_frame_map, cluster_to_major_speaker)
    per_speaker_metrics = compute_per_speaker_metrics(gt_frame_map, pred_frame_map, cluster_to_major_speaker)

    avg_entropy = np.mean(list(entropies.values())) if entropies else 0

    # Calculate total seconds in GT and prediction
    total_gt_seconds = sum(row['end_time'] - row['start_time'] for _, row in gt.iterrows())
    total_pred_seconds = sum(row['end_time'] - row['start_time'] for _, row in pred.iterrows())
    prediction_to_gt_ratio = total_pred_seconds / total_gt_seconds if total_gt_seconds > 0 else 0

    metrics = {
        "Precision": precision,
        "Recall": recall,
        "Purity": purity,
        "B³ Prec": b_precision,
        "B³ Recall": b_recall,
        "DER": der,
        "Avg Entropy": avg_entropy,
        "Pred/GT": prediction_to_gt_ratio
    }
    
    metrics_list.append(metrics)
    per_speaker_metrics_list.append(per_speaker_metrics)
    pred_names_list.append(current_pred.stem)


# Export CSV
clustering_report_path = metric_output_folder / f"{method_name}_ExtraReport.csv"

# Compute entropy for all clusters
all_entropies = compute_all_entropies(cluster_to_speakers)

# Calculate average entropy
overall_avg_entropy = np.mean(list(all_entropies.values())) if entropies else 0

# Calculate the average metrics for all pairs
overall_avg_precision = np.mean([metrics["Precision"] for metrics in metrics_list])
overall_avg_recall = np.mean([metrics["Recall"] for metrics in metrics_list])
overall_avg_purity = np.mean([metrics["Purity"] for metrics in metrics_list])
overall_avg_b_precision = np.mean([metrics["B³ Prec"] for metrics in metrics_list])
overall_avg_b_recall = np.mean([metrics["B³ Recall"] for metrics in metrics_list])
overall_avg_der = np.mean([metrics["DER"] for metrics in metrics_list])
overall_avg_prediction_to_gt_ratio = np.mean([metrics["Pred/GT"] for metrics in metrics_list])

# Create a dictionary to store the overall metrics
overall_dict = {
    "Precision": overall_avg_precision,
    "Recall": overall_avg_recall,
    "Purity": overall_avg_purity,
    "DER": overall_avg_der,
    "Avg Entropy": overall_avg_entropy,
    "Pred/GT": overall_avg_prediction_to_gt_ratio
}

with open(clustering_report_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t')

    for idx, current_metrics in enumerate(metrics_list):
        writer.writerow([f"Metrics for {pred_names_list[idx]}"])
        writer.writerow(["Metric", "Value"])
        for key, value in metrics.items():
            writer.writerow([key, f"{value:.2f}"])
        writer.writerow([])
        writer.writerow(["Speaker ID", "Precision", "Recall", "DER"])
        for speaker_id, values in sorted(per_speaker_metrics.items(), key=lambda x: x[1]["DER"], reverse=True):
            writer.writerow([
                speaker_id,
                f"{values['Precision']:.2f}",
                f"{values['Recall']:.2f}",
                f"{values['DER']:.2f}"
            ])
        writer.writerow([])
        writer.writerow([])
    
    writer.writerow([])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['---------------','---------------'])
    writer.writerow(["Overall Metrics"])
    writer.writerow(["Metric", "Value"])
    for key, value in overall_dict.items():
        writer.writerow([key, f"{value:.2f}"])
    writer.writerow([])
    writer.writerow(["Speaker ID", "Precision"])
    for speaker_id, values in sorted(per_speaker_metrics.items(), key=lambda x: x[1]["DER"], reverse=True):
        writer.writerow([
            speaker_id,
            f"{values['Precision']:.2f}",
        ])
    writer.writerow([])
    writer.writerow(["Speaker ID", "Recall"])
    for speaker_id, values in sorted(per_speaker_metrics.items(), key=lambda x: x[1]["DER"], reverse=True):
        writer.writerow([
            speaker_id,
            f"{values['Recall']:.2f}",
        ])
    writer.writerow([])
    writer.writerow(["Speaker ID", "DER"])
    for speaker_id, values in sorted(per_speaker_metrics.items(), key=lambda x: x[1]["DER"], reverse=True):
        writer.writerow([
            speaker_id,
            f"{values['DER']:.2f}"
        ])


print(f"\n✅ Report exported to: {clustering_report_path}")