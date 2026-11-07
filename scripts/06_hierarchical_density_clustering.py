import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

# Setup plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.dpi'] = 300

os.makedirs("outputs/figures", exist_ok=True)
os.makedirs("outputs/tables", exist_ok=True)

print("=== Unit III: Hierarchical & Density-Based Clustering ===")
df_clean = pd.read_csv("data/processed/habitations_with_kmeans.csv")
df_scaled = pd.read_csv("data/processed/habitations_scaled_features.csv")

feature_cols = [
    'elevation_m',
    'slope_deg',
    'distance_to_river_km',
    'annual_rainfall_mm',
    'monsoon_rainfall_mm',
    'extreme_daily_rainfall_mm',
    'population_density_per_sqkm',
    'drainage_congestion_index',
    'historical_flood_inundation_frequency'
]

X = df_scaled[feature_cols].values

# 1. Agglomerative Hierarchical Clustering across Linkages (K=3)
linkages = ['ward', 'complete', 'average', 'single']
hier_results = []
hier_labels_dict = {}

for link in linkages:
    # Ward requires euclidean metric
    metric = 'euclidean'
    agg = AgglomerativeClustering(n_clusters=3, linkage=link, metric=metric)
    labels = agg.fit_predict(X)
    hier_labels_dict[link] = labels
    
    # Check if more than 1 cluster is formed
    n_unique = len(np.unique(labels))
    if n_unique > 1:
        sil = silhouette_score(X, labels, metric='euclidean')
        db = davies_bouldin_score(X, labels)
        ch = calinski_harabasz_score(X, labels)
    else:
        sil, db, ch = np.nan, np.nan, np.nan
        
    hier_results.append({
        'Algorithm': 'Agglomerative Clustering',
        'Linkage Criterion': link.capitalize(),
        'Clusters (K)': 3,
        'Distance Metric': 'Euclidean',
        'Silhouette Score': round(sil, 4) if not np.isnan(sil) else None,
        'Davies-Bouldin Index': round(db, 4) if not np.isnan(db) else None,
        'Calinski-Harabasz Index': round(ch, 2) if not np.isnan(ch) else None,
        'Cluster Distribution': str(dict(pd.Series(labels).value_counts().sort_index()))
    })

df_hier_metrics = pd.DataFrame(hier_results)
df_hier_metrics.to_csv("outputs/tables/hierarchical_comparison_table.csv", index=False)
print("\n--- Hierarchical Linkage Comparison Table ---")
print(df_hier_metrics.to_string())

# Attach best Hierarchical (Ward) clusters to dataset
df_clean['hierarchical_ward_cluster'] = hier_labels_dict['ward']

# 2. Dendrogram Visualization using Ward's Linkage
print("\nGenerating Hierarchical Dendrogram...")
Z = linkage(X, method='ward', metric='euclidean')

plt.figure(figsize=(14, 7))
# Truncate dendrogram to show top 30 merged levels for clear readability
dendrogram(
    Z,
    truncate_mode='lastp',
    p=25,
    leaf_rotation=45.,
    leaf_font_size=9.,
    show_contracted=True,
    color_threshold=11.5 # Cut threshold resulting in 3 clusters
)
plt.axhline(y=11.5, color='crimson', linestyle='--', linewidth=2, label='Optimal Cluster Cut (Threshold = 11.5 -> K=3)')
plt.title("Hierarchical Clustering Dendrogram (Ward Linkage, Euclidean Distance)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Cluster Group / Habitation Sample Nodes (Truncated Representation)", fontsize=11, fontweight='bold')
plt.ylabel("Ward Distance Metric (Variance Dissimilarity)", fontsize=11, fontweight='bold')
plt.legend(loc='upper right', fontsize=11)
plt.tight_layout()
plt.savefig("outputs/figures/05_hierarchical_dendrogram.png", dpi=300)
plt.close()
print("Saved outputs/figures/05_hierarchical_dendrogram.png")

# 3. DBSCAN (Density-Based Spatial Clustering of Applications with Noise)
print("\nEvaluating DBSCAN and K-Nearest Neighbors Distance Graph...")
# Determine optimal epsilon using 4-NN distance graph
k_neighbors = 4
nn = NearestNeighbors(n_neighbors=k_neighbors)
nbrs = nn.fit(X)
distances, indices = nbrs.kneighbors(X)

# Sort distances to the k-th neighbor
k_distances = np.sort(distances[:, k_neighbors - 1])

plt.figure(figsize=(8, 5))
plt.plot(k_distances, color='#2b5c8f', linewidth=2.5, label='4-NN Distance Curve')
plt.axhline(y=1.85, color='red', linestyle='--', linewidth=1.8, label='Optimal Epsilon Elbow (eps = 1.85)')
plt.title("DBSCAN Parameter Tuning: 4-Nearest Neighbor (k-distance) Plot", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Data Points (Sorted by Distance)", fontsize=11, fontweight='bold')
plt.ylabel("Distance to 4th Nearest Neighbor", fontsize=11, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper left', fontsize=11)
plt.tight_layout()
plt.savefig("outputs/figures/06_dbscan_k_distance_graph.png", dpi=300)
plt.close()
print("Saved outputs/figures/06_dbscan_k_distance_graph.png")

# Systematic Grid Search across Epsilon and MinPts
dbscan_grid = []
eps_values = [1.2, 1.5, 1.85, 2.2]
min_samples_values = [3, 4, 5]

best_dbscan_model = None
best_dbscan_sil = -1
selected_eps = 1.85
selected_min_samples = 4

for eps in eps_values:
    for ms in min_samples_values:
        db = DBSCAN(eps=eps, min_samples=ms)
        labels = db.fit_predict(X)
        
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        
        # Calculate silhouette only on non-noise points if > 1 cluster
        non_noise_mask = labels != -1
        if n_clusters > 1 and np.sum(non_noise_mask) > n_clusters:
            sil = round(silhouette_score(X[non_noise_mask], labels[non_noise_mask]), 4)
            db_score = round(davies_bouldin_score(X[non_noise_mask], labels[non_noise_mask]), 4)
        else:
            sil, db_score = np.nan, np.nan
            
        dbscan_grid.append({
            'Algorithm': 'DBSCAN',
            'Epsilon (eps)': eps,
            'MinPts (min_samples)': ms,
            'Clusters Found': n_clusters,
            'Noise Points (Outliers)': n_noise,
            'Noise Ratio (%)': round((n_noise / len(X)) * 100, 1),
            'Silhouette Score (Non-Noise)': sil,
            'Davies-Bouldin Index': db_score
        })
        
        if eps == selected_eps and ms == selected_min_samples:
            best_dbscan_labels = labels

df_dbscan_metrics = pd.DataFrame(dbscan_grid)
df_dbscan_metrics.to_csv("outputs/tables/dbscan_comparison_table.csv", index=False)
print("\n--- DBSCAN Parameter Tuning Table ---")
print(df_dbscan_metrics.to_string())

# Attach DBSCAN labels
df_clean['dbscan_cluster'] = best_dbscan_labels
df_clean['dbscan_is_noise'] = (best_dbscan_labels == -1)

noise_habs = df_clean[df_clean['dbscan_is_noise']]['habitation_name'].tolist()
print(f"\nDBSCAN identified {len(noise_habs)} noise/outlier habitations with anomalous topographic/demographic profiles: {noise_habs}")

# 4. Master Model Comparison (K-Means vs Hierarchical Ward vs DBSCAN)
master_comparison = [
    {
        'Algorithm': 'K-Means (K-Means++)',
        'Clusters': 3,
        'Noise Points': 0,
        'Silhouette Score': round(silhouette_score(X, df_clean['cluster_k3']), 4),
        'Davies-Bouldin Index': round(davies_bouldin_score(X, df_clean['cluster_k3']), 4),
        'Key Advantages': 'Fast, global variance minimization, balanced cluster assignment matching 3 hazard tiers.'
    },
    {
        'Algorithm': 'Hierarchical (Ward)',
        'Clusters': 3,
        'Noise Points': 0,
        'Silhouette Score': round(silhouette_score(X, hier_labels_dict['ward']), 4),
        'Davies-Bouldin Index': round(davies_bouldin_score(X, hier_labels_dict['ward']), 4),
        'Key Advantages': 'Deterministic, builds clear taxonomic dendrogram of settlements based on variance.'
    },
    {
        'Algorithm': f'DBSCAN (eps={selected_eps}, min_pts={selected_min_samples})',
        'Clusters': len(set(best_dbscan_labels)) - 1,
        'Noise Points': list(best_dbscan_labels).count(-1),
        'Silhouette Score': round(silhouette_score(X[best_dbscan_labels != -1], best_dbscan_labels[best_dbscan_labels != -1]), 4),
        'Davies-Bouldin Index': round(davies_bouldin_score(X[best_dbscan_labels != -1], best_dbscan_labels[best_dbscan_labels != -1]), 4),
        'Key Advantages': 'Detects arbitrary density shapes and effectively isolates isolated topographic anomalies.'
    }
]

df_master_comp = pd.DataFrame(master_comparison)
df_master_comp.to_csv("outputs/tables/master_clustering_comparison.csv", index=False)
print("\n--- Master Algorithm Comparison ---")
print(df_master_comp.to_string())

df_clean.to_csv("data/processed/habitations_with_all_clusters.csv", index=False)
print("\nUnit III analysis completed successfully!")
