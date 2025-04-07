from sklearn.metrics import adjusted_rand_score


# Example usage of adjusted_rand_score
labels_true = [0, 0, 1, 1, 2, 2]
labels_pred = [0, 0, 1, 2, 1, 2]

ari = adjusted_rand_score(labels_true, labels_pred)
print("ARI:", ari)

# Example usage of normalized_mutual_info_score
from sklearn.metrics import normalized_mutual_info_score

nmi = normalized_mutual_info_score(labels_true, labels_pred)
print("NMI:", nmi)

# Example of Fowlkes-Mallows Index (FMI)
from sklearn.metrics import fowlkes_mallows_score

fmi = fowlkes_mallows_score(labels_true, labels_pred)
print("FMI:", fmi)

### Measures for cluster Integrity

# Example of silhouette score
from sklearn.metrics import silhouette_score
from sklearn.datasets import make_blobs

X, labels_true_blb = make_blobs(n_samples=300, centers=3, return_centers=False, random_state=42)
# Assuming labels_pred are your predicted labels
silhouette = silhouette_score(X, labels_pred)
print("Silhouette Score:", silhouette)

# Example of Davies-Bouldin Index (DBI)
from sklearn.metrics import davies_bouldin_score

dbi = davies_bouldin_score(X, labels_pred)
print("Davies-Bouldin Index:", dbi)

# Example homegeneity, completeness, and V-measure
from sklearn.metrics import homogeneity_score, completeness_score, v_measure_score

homogeneity = homogeneity_score(labels_true, labels_pred)
completeness = completeness_score(labels_true, labels_pred)
v_measure = v_measure_score(labels_true, labels_pred)

print("Homogeneity:", homogeneity)
print("Completeness:", completeness)
print("V-Measure:", v_measure)