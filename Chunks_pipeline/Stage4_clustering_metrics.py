from pathlib import Path
import csv
import argparse
import os

import pandas as pd
from collections import defaultdict
from utilities_pyannote_metrics import matching_basename_pathlib_gt_pred
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, fowlkes_mallows_score


def write_txt_report(report_path, run_name, results, indexes_dict, confusion_matrix, speaker_metrics):
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"==== DIARIZATION REPORT: {run_name} ====\n\n")

        # Overall Metrics
        f.write("== OVERALL METRICS ==\n")
        f.write(f"Weighted Cluster Purity: {results['overall']['weighted_purity']:.4f}\n")
        f.write(f"Weighted Speaker Coverage: {results['overall']['weighted_coverage']:.4f}\n")
        f.write(f"F1 Score: {results['overall']['f1_score']:.4f}\n\n")

        # Per-Cluster Purity
        f.write("== PER-CLUSTER PURITY ==\n")
        for cluster_id, info in results['per_cluster_purity'].items():
            f.write(f"Cluster {cluster_id}: Purity = {info['purity']:.4f}, Dominant Speaker = {info['dominant_speaker']}, Duration = {info['duration']:.2f}s\n")
        f.write("\n")

        # Per-Speaker Coverage
        f.write("== PER-SPEAKER COVERAGE ==\n")
        for speaker_id, info in results['per_speaker_coverage'].items():
            f.write(f"Speaker {speaker_id}: Coverage = {info['coverage']:.4f}, Primary Cluster = {info['primary_cluster']}, "
                    f"In Primary = {info['in_primary_cluster']:.4f}, Duration = {info['total_duration']:.2f}s\n")
        f.write("\n")

        # Clustering Metrics
        f.write("== CLUSTERING METRICS ==\n")
        f.write(f"Adjusted Rand Index (ARI): {indexes_dict['ARI']:.4f}\n")
        f.write(f"Normalized Mutual Information (NMI): {indexes_dict['NMI']:.4f}\n")
        f.write(f"Fowlkes-Mallows Index: {indexes_dict['Fowlkes-Mallows']:.4f}\n")
        f.write(f"Valid segments evaluated: {indexes_dict['valid_segments']}\n\n")

        # Confusion Matrix
        if confusion_matrix is not None and not confusion_matrix.empty:
            f.write("== CONFUSION MATRIX ==\n")
            f.write(confusion_matrix.to_string())
            f.write("\n\n")

        # Speaker Metrics
        if speaker_metrics is not None and not speaker_metrics.empty:
            f.write("== SPEAKER-LEVEL METRICS ==\n")
            f.write(speaker_metrics.to_string(index=False))
            f.write("\n")


def calculate_confusion_matrix(y_true, y_pred):
    """
    Calculate a confusion matrix between speakers and clusters.
    
    Args:
        pred_clusters: Dictionary where keys are cluster IDs and values are lists of 
                      [feature_vector, start_time, end_time]
        gt_file: Path to CSV file with [speakerID, start_time, end_time] format
        time_resolution: Time resolution for discretization (in seconds)
    
    Returns:
        pandas.DataFrame: Confusion matrix
    """
    
    if len(y_true) == 0:
        return pd.DataFrame()
    
    # Create confusion matrix
    confusion = defaultdict(lambda: defaultdict(int))
    
    for true_label, pred_label in zip(y_true, y_pred):
        confusion[true_label][pred_label] += 1
    
    # Convert to DataFrame
    speakers = sorted(set(y_true))
    clusters = sorted(set(y_pred))
    
    matrix = pd.DataFrame(index=speakers, columns=clusters, data=0)
    
    for speaker in speakers:
        for cluster in clusters:
            matrix.loc[speaker, cluster] = confusion[speaker][cluster]
    
    # Add row and column sums
    matrix['Total'] = matrix.sum(axis=1)
    matrix.loc['Total'] = matrix.sum(axis=0)
    
    return matrix


def calculate_speaker_level_metrics(confusion_matrix):
    """
    Calculate precision, recall, and F1 score for each speaker.
    
    Args:
        confusion_matrix: Pandas DataFrame containing the confusion matrix
    
    Returns:
        pandas.DataFrame: DataFrame with precision, recall, and F1 for each speaker
    """
    if confusion_matrix.empty:
        return pd.DataFrame()
    
    # Remove the 'Total' row and column for calculations
    cm = confusion_matrix.drop('Total', axis=0).drop('Total', axis=1)
    
    results = []
    
    for speaker in cm.index:
        # Maximum value in the row corresponds to the primary cluster for this speaker
        max_cluster = cm.loc[speaker].idxmax()
        
        # True positives: segments of this speaker assigned to the primary cluster
        tp = cm.loc[speaker, max_cluster]
        
        # False negatives: segments of this speaker assigned to other clusters
        fn = cm.loc[speaker].sum() - tp
        
        # False positives: segments of other speakers assigned to this speaker's primary cluster
        fp = cm[max_cluster].sum() - tp
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        results.append({
            'Speaker': speaker,
            'Primary Cluster': max_cluster,
            'Precision': precision,
            'Recall': recall,
            'F1 Score': f1,
            'Total Segments': cm.loc[speaker].sum()
        })
    
    return pd.DataFrame(results)


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

args = parser.parse_args()

csv_pred_folder = args.csv_pred_folder
GT_csv_folder = args.GT_csv_folder
metric_output_folder = args.metric_output_folder
run_name = args.run_name

pred_suffix_added = args.pred_suffix
pred_ext = args.pred_extensions

#G-C1L1P-Apr27-E-Irma_q2_03-08-377_GT
#G-C1L1P-Apr27-E-Irma_q2_03-08-377_pred


if pred_suffix_added == 'xx':
    pred_suffix_added = ''
    print('updating pred_suffix_added to empty string')

# print(f'>>>>>>> pred_suffix: {pred_suffix_added} \t ext: {pred_ext}')

# print(f'Metrics folder: {metric_output_folder}')

suffix_ext_list = [pred_ext, pred_suffix_added]

# print elements in suffix_ext_list
# print(f' main suffix: {suffix_ext_list[1]} \t main ext: {suffix_ext_list[0]}')
# print(f'suffix: {suffix_ext_list[1]} \t ext: {suffix_ext_list[0]}')

method_matches = matching_basename_pathlib_gt_pred(GT_csv_folder, csv_pred_folder, 
        gt_suffix_added='GT', pred_suffix_added=suffix_ext_list[1],
        gt_ext = 'csv', pred_ext = suffix_ext_list[0])

#### ---------------------- ####

for current_gt, current_pred in method_matches:
    print(f'Processing GT: {current_gt.stem} \t Prediction: {current_pred.stem}')

    method_name = run_name.split('_')[0]
    pred_name_stem = current_pred.stem
    output_run_name = f'{pred_name_stem}-{method_name}'
    pred_clusters= defaultdict(list)

    with open(current_pred, 'r', newline='') as file:
        reader = csv.DictReader(file, delimiter='\t', fieldnames=['filename', 'cluster_id', 'start_time', 'end_time', 'duration'])
        
        for row in reader:
            cluster_id = row['cluster_id']
            start_time = float(row['start_time'])
            end_time = float(row['end_time'])
            
            pred_clusters[cluster_id].append((start_time, end_time))

    # Sort the time intervals for each cluster by start_time
    for cluster_id in pred_clusters:
        pred_clusters[cluster_id].sort(key=lambda x: x[0])

    # Load ground truth data
    gt_data = pd.read_csv(current_gt, sep='\t', header=None, names=['speakerID', 'lang', 'start_time', 'end_time'])

    # Create a time-to-speaker mapping
    # For simplicity, we'll discretize time into small segments (e.g., 10ms)
    time_resolution = 0.01  # 10ms

    # Find the maximum end time in both GT and predictions
    max_end_time_gt = gt_data['end_time'].max()
    max_end_time_pred = max([sample[1] for cluster in pred_clusters.values() for sample in cluster])
    max_time = max(max_end_time_gt, max_end_time_pred)

    # Create arrays to track speaker for each time segment
    num_segments = int(max_time / time_resolution) + 1
    gt_timeline = [None] * num_segments

    # Fill the ground truth timeline
    for _, row in gt_data.iterrows():
        speaker_id, start, end = row['speakerID'], row['start_time'], row['end_time']
        start_idx = int(start / time_resolution)
        end_idx = int(end / time_resolution)
        for i in range(start_idx, min(end_idx + 1, num_segments)):
            gt_timeline[i] = speaker_id

    # Count total duration per speaker
    speaker_total_duration = defaultdict(float)
    for _, row in gt_data.iterrows():
        speaker_id, start, end = row['speakerID'], row['start_time'], row['end_time']
        speaker_total_duration[speaker_id] += (end - start)

    # Calculate overlap between each cluster and each speaker
    overlap_matrix = defaultdict(lambda: defaultdict(float))
    cluster_durations = defaultdict(float)

    for cluster_id, samples in pred_clusters.items():
        for start, end in samples:
            cluster_durations[cluster_id] += (end - start)
            
            start_idx = int(start / time_resolution)
            end_idx = int(end / time_resolution)
            
            for i in range(start_idx, min(end_idx + 1, num_segments)):
                if i < len(gt_timeline) and gt_timeline[i] is not None:
                    speaker_id = gt_timeline[i]
                    overlap_matrix[cluster_id][speaker_id] += time_resolution

    ## 
    # Calculate purity for each cluster
    cluster_purity = {}
    for cluster_id, speaker_overlaps in overlap_matrix.items():
        if cluster_durations[cluster_id] > 0:
            # Find speaker with maximum overlap
            max_speaker = max(speaker_overlaps.items(), key=lambda x: x[1], default=(None, 0))
            if max_speaker[0] is not None:
                purity = max_speaker[1] / cluster_durations[cluster_id]
                cluster_purity[cluster_id] = {
                    'purity': purity,
                    'dominant_speaker': max_speaker[0],
                    'duration': cluster_durations[cluster_id]
                }
            else:
                cluster_purity[cluster_id] = {'purity': 0, 'dominant_speaker': None, 'duration': cluster_durations[cluster_id]}
        else:
            cluster_purity[cluster_id] = {'purity': 0, 'dominant_speaker': None, 'duration': 0}

    # Calculate coverage for each speaker
    speaker_coverage = {}
    for speaker_id in speaker_total_duration.keys():
        # Find all clusters that contain this speaker
        speaker_in_clusters = {
            cluster_id: overlap 
            for cluster_id, speaker_overlaps in overlap_matrix.items() 
            for spk, overlap in speaker_overlaps.items() 
            if spk == speaker_id
        }
        
        # Total time this speaker was correctly identified (in any cluster)
        total_covered = sum(speaker_in_clusters.values())
        
        if speaker_total_duration[speaker_id] > 0:
            coverage = total_covered / speaker_total_duration[speaker_id]
        else:
            coverage = 0
            
        # Find primary cluster for this speaker
        primary_cluster = max(speaker_in_clusters.items(), key=lambda x: x[1], default=(None, 0))
        
        speaker_coverage[speaker_id] = {
            'coverage': coverage,
            'primary_cluster': primary_cluster[0],
            'in_primary_cluster': primary_cluster[1] / speaker_total_duration[speaker_id] if speaker_total_duration[speaker_id] > 0 else 0,
            'total_duration': speaker_total_duration[speaker_id]
        }

    # Calculate overall metrics
    total_duration = sum(cluster_durations.values())
    weighted_purity = sum(info['purity'] * info['duration'] for info in cluster_purity.values()) / total_duration if total_duration > 0 else 0

    total_gt_duration = sum(speaker_total_duration.values())
    weighted_coverage = sum(info['coverage'] * info['total_duration'] for info in speaker_coverage.values()) / total_gt_duration if total_gt_duration > 0 else 0

    # Compile results
    results = {
        'overall': {
            'weighted_purity': weighted_purity,
            'weighted_coverage': weighted_coverage,
            'f1_score': 2 * (weighted_purity * weighted_coverage) / (weighted_purity + weighted_coverage) if (weighted_purity + weighted_coverage) > 0 else 0
        },
        'per_cluster_purity': cluster_purity,
        'per_speaker_coverage': speaker_coverage
    }

    ##### ---------------------- ####
    # Convert gt_timeline segments into y_true and y_pred
    y_true = [speaker_id if speaker_id is not None else 'NoiseBck' for speaker_id in gt_timeline]

    # Initialize y_pred with 'Unknown' for all time segments
    y_pred = ['NoiseBck'] * num_segments

    # Fill y_pred based on predicted clusters
    for cluster_id, intervals in pred_clusters.items():
        for start, end in intervals:
            start_idx = int(start / time_resolution)
            end_idx = int(end / time_resolution)
            for i in range(start_idx, min(end_idx + 1, num_segments)):
                y_pred[i] = cluster_id

    # Now y_pred contains the predicted cluster for each time segment

    indexes_dict = {}
    if len(y_true) == 0 or len(y_pred) == 0:
        indexes_dict = {
            'ARI': 0,
            'NMI': 0,
            'Fowlkes-Mallows': 0,
            'valid_segments': 0
        }
        
    # Calculate metrics
    ari = adjusted_rand_score(y_true, y_pred)
    nmi = normalized_mutual_info_score(y_true, y_pred)
    fm = fowlkes_mallows_score(y_true, y_pred)

    indexes_dict = {
        'ARI': ari,
        'NMI': nmi,
        'Fowlkes-Mallows': fm,
        'valid_segments': len(y_true)
    }

    confusion_matrix = calculate_confusion_matrix(y_true, y_pred)
    speaker_metrics = calculate_speaker_level_metrics(confusion_matrix)

    # Create output file path
    report_file = metric_output_folder / f"{output_run_name}_report.txt"

    # Write the full text report
    write_txt_report(report_file, output_run_name, results, indexes_dict, confusion_matrix, speaker_metrics)

    print(f"\n✅ Report written to: {report_file}\n")
