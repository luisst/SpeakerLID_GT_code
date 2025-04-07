import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import warnings
import pickle
from sklearn.exceptions import UndefinedMetricWarning

import os
from pathlib import Path
import argparse

def calculate_internal_metrics(features, labels):
    """
    Calculate internal clustering evaluation metrics.
    
    Args:
        features: numpy array of feature vectors
        labels: numpy array of cluster labels
    
    Returns:
        dict: Dictionary containing calculated metrics
    """
    results = {}
    
    # Check if we have enough data and clusters
    if len(features) < 2 or len(np.unique(labels)) < 2:
        print("Warning: Not enough data or clusters for internal metrics calculation")
        return {
            'silhouette_score': None,
            'davies_bouldin_score': None,
            'calinski_harabasz_score': None
        }
    
    # Calculate Silhouette Score
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UndefinedMetricWarning)
            results['silhouette_score'] = silhouette_score(features, labels)
    except Exception as e:
        print(f"Error calculating Silhouette Score: {e}")
        results['silhouette_score'] = None
    
    # Calculate Davies-Bouldin Index
    try:
        results['davies_bouldin_score'] = davies_bouldin_score(features, labels)
    except Exception as e:
        print(f"Error calculating Davies-Bouldin Index: {e}")
        results['davies_bouldin_score'] = None
    
    # Calculate Calinski-Harabasz Index
    try:
        results['calinski_harabasz_score'] = calinski_harabasz_score(features, labels)
    except Exception as e:
        print(f"Error calculating Calinski-Harabasz Index: {e}")
        results['calinski_harabasz_score'] = None
    
    return results


def valid_path(path):
    if os.path.exists(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


base_path_ex = Path.home().joinpath('Dropbox','DATASETS_AUDIO','VAD_aolme','TestAO-Irmadb')
feats_pickle_ex = base_path_ex.joinpath('Testset_stage3','HDBSCAN_pred_output','features.pkl')
feats_reduced_pickle_ex = base_path_ex.joinpath('Testset_stage3','HDBSCAN_pred_output','features_reduced.pkl')

stg3_pred_lbl_pickle_ex = base_path_ex.joinpath('Testset_stage3','HDBSCAN_pred_output','stg3_final_csv')
clustering_metric_output_folder_ex = base_path_ex.joinpath('Testset_stage3','HDBSCAN_pred_output','metrics')


parser = argparse.ArgumentParser()

parser.add_argument('--input_feats_pickle', default=feats_pickle_ex, help='Path to the folder to store the D-vectors features')
parser.add_argument('--input_feats_reduced_pickle', default=feats_reduced_pickle_ex, help='Stg3 predicted labels from clustering')
parser.add_argument('--stg3_pred_lbl', type=valid_path, default=stg3_pred_lbl_pickle_ex, help='Stg3 predicted labels from clustering')
parser.add_argument('--stg3_clustering_metrics', type=valid_path, default=clustering_metric_output_folder_ex, help='Path to the folder to store the clustering metrics')

args = parser.parse_args()

feats_pickle_path = args.input_feats_pickle
labels_pred_path = args.stg3_pred_lbl
stg3_clustering_metrics = args.stg3_clustering_metrics
feats_reduced_pickle_path = args.input_feats_reduced_pickle

with open(f'{feats_pickle_path}', "rb") as file:
    X_data_and_labels = pickle.load(file)
Mixed_X_data, Mixed_X_paths, Mixed_y_labels = X_data_and_labels

with open(f'{labels_pred_path}', "rb") as file:
    pred_labels = pickle.load(file)

with open(f'{feats_reduced_pickle_path}', "rb") as file:
    reduced_feats = pickle.load(file)

### Metrics calculation
metrics = calculate_internal_metrics(Mixed_X_data, pred_labels)
import matplotlib.pyplot as plt

# Create a bar plot to visualize the metrics
metric_names = ['Silhouette Score', 'Davies-Bouldin Index', 'Calinski-Harabasz Index']
metric_values = [
    metrics['silhouette_score'] if metrics['silhouette_score'] is not None else 0,
    metrics['davies_bouldin_score'] if metrics['davies_bouldin_score'] is not None else 0,
    metrics['calinski_harabasz_score'] if metrics['calinski_harabasz_score'] is not None else 0
]

# Set up the figure
plt.figure(figsize=(8, 6))
bars = plt.bar(metric_names, metric_values, color=['blue', 'orange', 'green'])

# Add value annotations on top of the bars
for bar, value in zip(bars, metric_values):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), 
             f'{value:.4f}' if value != 0 else 'N/A', 
             ha='center', va='bottom', fontsize=10)

# Add labels and title
plt.title('D-vectors - Internal Clustering Evaluation Metrics', fontsize=14)
plt.ylabel('Metric Value', fontsize=12)
plt.xlabel('Metrics', fontsize=12)
plt.ylim(0, max(metric_values) * 1.2 if max(metric_values) > 0 else 1)


# Add explanatory text to the plot
explanatory_text = """A higher silhouette score (~0.7 to 1.0) if speakers’ voices are well-separated.\n
    A lower silhouette score (~0.2 to 0.5) if there is overlap (e.g., similar voice features, background noise).\n
    A negative score if some segments are misclassified."""

explanatory_text_DBI = """0.3 – 0.5	Very good clustering (tight & well-separated)\n
~0.6 – 0.8	Acceptable, moderate overlap\n
~0.9 – 1.5	Poor separation, some clusters too close"""

# Save the plot
output_plot_path = stg3_clustering_metrics.joinpath('clustering_metrics_plot.png')
plt.savefig(output_plot_path)
plt.close()


print(f"Plot saved to {output_plot_path}")
print("\n===== INTERNAL CLUSTERING EVALUATION METRICS =====\n")

print("OVERALL METRICS:")
if metrics['silhouette_score'] is not None:
    print(f"Silhouette Score: {metrics['silhouette_score']:.4f} (higher is better, range: [-1, 1])")
else:
    print("Silhouette Score: Not calculated")
    
if metrics['davies_bouldin_score'] is not None:
    print(f'Silhouette focuses on how well a point fits into its own cluster, while DBI compares between clusters')
    print(f"Davies-Bouldin Index: {metrics['davies_bouldin_score']:.4f} (lower is better)")
else:
    print("Davies-Bouldin Index: Not calculated")
    
if metrics['calinski_harabasz_score'] is not None:
    print(f"Calinski-Harabasz Index: {metrics['calinski_harabasz_score']:.4f} (higher is better)")
else:
    print("Calinski-Harabasz Index: Not calculated")

### Metrics calculation for reduced features
metrics_reduced = calculate_internal_metrics(reduced_feats, pred_labels)

# Create a bar plot to visualize the metrics for reduced features
metric_values_reduced = [
    metrics_reduced['silhouette_score'] if metrics_reduced['silhouette_score'] is not None else 0,
    metrics_reduced['davies_bouldin_score'] if metrics_reduced['davies_bouldin_score'] is not None else 0,
    metrics_reduced['calinski_harabasz_score'] if metrics_reduced['calinski_harabasz_score'] is not None else 0
]

# Set up the figure
plt.figure(figsize=(8, 6))
bars_reduced = plt.bar(metric_names, metric_values_reduced, color=['blue', 'orange', 'green'])

# Add value annotations on top of the bars
for bar, value in zip(bars_reduced, metric_values_reduced):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), 
             f'{value:.4f}' if value != 0 else 'N/A', 
             ha='center', va='bottom', fontsize=10)

# Add labels and title
plt.title('Reduced Features - Internal Clustering Evaluation Metrics', fontsize=14)
plt.ylabel('Metric Value', fontsize=12)
plt.xlabel('Metrics', fontsize=12)
plt.ylim(0, max(metric_values_reduced) * 1.2 if max(metric_values_reduced) > 0 else 1)

# Save the plot
output_plot_path_reduced = stg3_clustering_metrics.joinpath('clustering_metrics_plot_reduced.png')
plt.savefig(output_plot_path_reduced)
plt.close()

print(f"Plot for reduced features saved to {output_plot_path_reduced}")
print("\n===== INTERNAL CLUSTERING EVALUATION METRICS (REDUCED FEATURES) =====\n")

print("OVERALL METRICS (REDUCED FEATURES):")
if metrics_reduced['silhouette_score'] is not None:
    print(f"Silhouette Score: {metrics_reduced['silhouette_score']:.4f} (higher is better, range: [-1, 1])")
else:
    print("Silhouette Score: Not calculated")
    
if metrics_reduced['davies_bouldin_score'] is not None:
    print(f"Davies-Bouldin Index: {metrics_reduced['davies_bouldin_score']:.4f} (lower is better)")
else:
    print("Davies-Bouldin Index: Not calculated")
    
if metrics_reduced['calinski_harabasz_score'] is not None:
    print(f"Calinski-Harabasz Index: {metrics_reduced['calinski_harabasz_score']:.4f} (higher is better)")
else:
    print("Calinski-Harabasz Index: Not calculated")