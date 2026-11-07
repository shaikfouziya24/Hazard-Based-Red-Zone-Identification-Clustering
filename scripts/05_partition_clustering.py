import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, silhouette_samples

# Setup plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.dpi'] = 300

os.makedirs("outputs/figures", exist_ok=True)
os.makedirs("outputs/tables", exist_ok=True)

print("=== Unit II: Partition-Based Clustering Analysis ===")
df_clean = pd.read_csv("data/processed/vijayawada_guntur_habitations_features.csv")
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

# 1. Systematic Evaluation of K-Means (Random vs K-Means++, K = 2, 3, 4, 5)
k_values = [2, 3, 4, 5]
kmeans_results = []

for init_method in ['random', 'k-means++']:
    for k in k_values:
        km = KMeans(n_clusters=k, init=init_method, n_init=30, max_iter=300, random_state=42)
        labels = km.fit_predict(X)
        
        inertia = km.inertia_
        sil = silhouette_score(X, labels, metric='euclidean')
        db = davies_bouldin_score(X, labels)
        ch = calinski_harabasz_score(X, labels)
        
        kmeans_results.append({
            'Algorithm': 'K-Means',
            'Initialization': init_method,
            'K (Clusters)': k,
            'Inertia (WCSS)': round(inertia, 2),
            'Silhouette Score': round(sil, 4),
            'Davies-Bouldin Index': round(db, 4),
            'Calinski-Harabasz Index': round(ch, 2)
        })

df_km_metrics = pd.DataFrame(kmeans_results)
df_km_metrics.to_csv("outputs/tables/kmeans_comparison_table.csv", index=False)
print("\n--- K-Means Evaluation Table ---")
print(df_km_metrics.to_string())

# 2. Elbow Curve & Silhouette Score Visualization
fig, ax1 = plt.subplots(figsize=(9, 5))

df_kpp = df_km_metrics[df_km_metrics['Initialization'] == 'k-means++']

color = '#1f77b4'
ax1.set_xlabel('Number of Clusters (K)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Inertia / WCSS', color=color, fontsize=12, fontweight='bold')
ax1.plot(df_kpp['K (Clusters)'], df_kpp['Inertia (WCSS)'], marker='o', color=color, linewidth=2.5, markersize=8, label='WCSS (Inertia)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xticks(k_values)
ax1.grid(True, linestyle='--', alpha=0.6)

# Overlay Silhouette Score on secondary y-axis
ax2 = ax1.twinx()
color = '#d62728'
ax2.set_ylabel('Silhouette Score', color=color, fontsize=12, fontweight='bold')
ax2.plot(df_kpp['K (Clusters)'], df_kpp['Silhouette Score'], marker='s', color=color, linewidth=2.5, markersize=8, linestyle='--', label='Silhouette Score')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('K-Means Optimization: Elbow Method & Silhouette Score (K=2 to 5)', fontsize=13, fontweight='bold', pad=15)
fig.tight_layout()
plt.savefig("outputs/figures/03_kmeans_elbow_silhouette.png", dpi=300)
plt.close()
print("Saved outputs/figures/03_kmeans_elbow_silhouette.png")

# 3. K-Medoids (Partitioning Around Medoids - PAM)
# Implementation supporting Manhattan (L1, cityblock) and Euclidean (L2) distance
class KMedoidsPAM:
    def __init__(self, n_clusters=3, metric='cityblock', max_iter=300, random_state=42):
        self.n_clusters = n_clusters
        self.metric = metric
        self.max_iter = max_iter
        self.random_state = random_state
        self.medoid_indices_ = None
        self.labels_ = None
        self.inertia_ = None

    def fit(self, X):
        rng = np.random.RandomState(self.random_state)
        n_samples = X.shape[0]
        # cdist uses 'cityblock' for Manhattan L1 distance
        dist_metric = 'cityblock' if self.metric == 'manhattan' else self.metric
        D = cdist(X, X, metric=dist_metric)
        
        # Greedy farthest point initialization (k-medoids++)
        medoids = [rng.choice(n_samples)]
        for _ in range(1, self.n_clusters):
            dists = np.min(D[:, medoids], axis=1)
            probs = dists / dists.sum()
            medoids.append(rng.choice(n_samples, p=probs))
        medoids = np.array(medoids)

        for _ in range(self.max_iter):
            labels = np.argmin(D[:, medoids], axis=1)
            new_medoids = np.copy(medoids)
            
            for k in range(self.n_clusters):
                cluster_members = np.where(labels == k)[0]
                if len(cluster_members) > 0:
                    sub_dists = D[np.ix_(cluster_members, cluster_members)]
                    best_member = cluster_members[np.argmin(np.sum(sub_dists, axis=1))]
                    new_medoids[k] = best_member
            
            if np.array_equal(np.sort(medoids), np.sort(new_medoids)):
                break
            medoids = new_medoids

        self.medoid_indices_ = medoids
        self.labels_ = np.argmin(D[:, medoids], axis=1)
        self.inertia_ = float(np.sum(np.min(D[:, medoids], axis=1)))
        return self

kmedoids_results = []
for metric in ['manhattan', 'euclidean']:
    for k in k_values:
        pam = KMedoidsPAM(n_clusters=k, metric=metric, random_state=42)
        pam.fit(X)
        labels = pam.labels_
        
        sil_metric = 'cityblock' if metric == 'manhattan' else metric
        sil = silhouette_score(X, labels, metric=sil_metric)
        db = davies_bouldin_score(X, labels)
        ch = calinski_harabasz_score(X, labels)
        
        medoid_hab_names = df_clean.iloc[pam.medoid_indices_]['habitation_name'].tolist()
        
        kmedoids_results.append({
            'Algorithm': 'K-Medoids (PAM)',
            'Distance Metric': metric,
            'K (Clusters)': k,
            'Inertia (Sum of Distances)': round(pam.inertia_, 2),
            'Silhouette Score': round(sil, 4),
            'Davies-Bouldin Index': round(db, 4),
            'Calinski-Harabasz Index': round(ch, 2),
            'Exemplar Medoids': ", ".join(medoid_hab_names)
        })

df_kmed_metrics = pd.DataFrame(kmedoids_results)
df_kmed_metrics.to_csv("outputs/tables/kmedoids_comparison_table.csv", index=False)
print("\n--- K-Medoids Evaluation Table ---")
print(df_kmed_metrics[['Algorithm', 'Distance Metric', 'K (Clusters)', 'Inertia (Sum of Distances)', 'Silhouette Score', 'Davies-Bouldin Index', 'Exemplar Medoids']].to_string())

# 4. Fit Best K=3 Model (K-Means++) and Assign Relative Hazard Tiers
best_km = KMeans(n_clusters=3, init='k-means++', n_init=30, random_state=42)
best_km_labels = best_km.fit_predict(X)
df_clean['raw_cluster_k3'] = best_km_labels

# Rank clusters by relative hazard and vulnerability level
cluster_hazard_means = df_clean.groupby('raw_cluster_k3').apply(
    lambda g: g['historical_flood_inundation_frequency'].mean() + g['drainage_congestion_index'].mean() - (g['elevation_m'].mean() / 15.0),
    include_groups=False
).to_dict()

# Sort clusters: highest composite score = High Relative Hazard/Vulnerability
sorted_clusters = sorted(cluster_hazard_means.keys(), key=lambda c: cluster_hazard_means[c], reverse=True)
tier_mapping = {
    sorted_clusters[0]: "High Relative Hazard / Vulnerability",
    sorted_clusters[1]: "Moderate Relative Hazard / Vulnerability",
    sorted_clusters[2]: "Relatively Lower Hazard / Vulnerability"
}
tier_code_mapping = {
    sorted_clusters[0]: 1, # Red
    sorted_clusters[1]: 2, # Yellow
    sorted_clusters[2]: 3  # Green / Blue
}

df_clean['cluster_k3'] = df_clean['raw_cluster_k3'].map(tier_code_mapping)
df_clean['relative_hazard_level'] = df_clean['raw_cluster_k3'].map(tier_mapping)

# 5. Detailed Silhouette Plot for Selected K=3 Model
sample_silhouette_values = silhouette_samples(X, df_clean['cluster_k3'].values)

fig, ax = plt.subplots(figsize=(8, 6))
y_lower = 10
tier_colors = {
    1: '#d73027', # High hazard (Red)
    2: '#fdae61', # Moderate hazard (Orange/Yellow)
    3: '#4575b4'  # Lower hazard (Blue)
}

for tier_code in [1, 2, 3]:
    tier_name = [k for k, v in tier_code_mapping.items() if v == tier_code][0]
    tier_label = tier_mapping[tier_name]
    ith_cluster_silhouette_values = sample_silhouette_values[df_clean['cluster_k3'] == tier_code]
    ith_cluster_silhouette_values.sort()
    size_cluster_i = ith_cluster_silhouette_values.shape[0]
    y_upper = y_lower + size_cluster_i
    ax.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_silhouette_values,
                     facecolor=tier_colors[tier_code], edgecolor='black', linewidth=0.5, alpha=0.85)
    ax.text(-0.05, y_lower + 0.5 * size_cluster_i, f"Tier {tier_code} (n={size_cluster_i})\n{tier_label[:14]}...", fontsize=9, fontweight='bold')
    y_lower = y_upper + 10

avg_sil = silhouette_score(X, df_clean['cluster_k3'])
ax.axvline(x=avg_sil, color="black", linestyle="--", linewidth=1.5, label=f"Mean Silhouette = {avg_sil:.3f}")
ax.set_title("Silhouette Profile for K-Means (K=3) Relative Hazard Tiers", fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel("Silhouette Coefficient Values", fontsize=11, fontweight='bold')
ax.set_ylabel("Habitations Ordered by Cluster", fontsize=11, fontweight='bold')
ax.set_yticks([])
ax.legend(loc="upper right")
plt.tight_layout()
plt.savefig("outputs/figures/04_silhouette_plot_k3.png", dpi=300)
plt.close()
print("Saved outputs/figures/04_silhouette_plot_k3.png")

# Save updated dataset
df_clean.to_csv("data/processed/habitations_with_kmeans.csv", index=False)
print("\nCluster counts:")
print(df_clean['relative_hazard_level'].value_counts())
print("\nPartition-based clustering analysis completed successfully!")
