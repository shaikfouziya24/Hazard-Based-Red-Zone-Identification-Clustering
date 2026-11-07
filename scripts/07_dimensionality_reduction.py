import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# Setup plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.dpi'] = 300

os.makedirs("outputs/figures", exist_ok=True)
os.makedirs("outputs/tables", exist_ok=True)

print("=== Unit IV: Dimensionality Reduction Analysis (PCA & t-SNE) ===")
df = pd.read_csv("data/processed/habitations_with_all_clusters.csv")
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

feature_display_names = [
    'Elevation (m)',
    'Slope (°)',
    'River Dist (km)',
    'Annual Rain (mm)',
    'Monsoon Rain (mm)',
    'Extreme Rain (mm)',
    'Pop Density (/km²)',
    'Drainage Congestion',
    'Flood Frequency'
]

X = df_scaled[feature_cols].values

# 1. Principal Component Analysis (Full 9 Components)
pca_full = PCA(n_components=len(feature_cols), random_state=42)
pca_full.fit(X)

exp_var = pca_full.explained_variance_ratio_
cum_exp_var = np.cumsum(exp_var)

pca_variance_table = pd.DataFrame({
    'Principal Component': [f'PC{i+1}' for i in range(len(feature_cols))],
    'Eigenvalue': np.round(pca_full.explained_variance_, 3),
    'Explained Variance Ratio (%)': np.round(exp_var * 100, 2),
    'Cumulative Variance Ratio (%)': np.round(cum_exp_var * 100, 2)
})
pca_variance_table.to_csv("outputs/tables/pca_explained_variance.csv", index=False)
print("\n--- PCA Explained Variance Table ---")
print(pca_variance_table.to_string())

# 2. Scree Plot & Cumulative Variance
fig, ax1 = plt.subplots(figsize=(9, 5))
components = np.arange(1, len(feature_cols) + 1)

color = '#1f77b4'
ax1.set_xlabel('Principal Component', fontsize=12, fontweight='bold')
ax1.set_ylabel('Individual Explained Variance (%)', color=color, fontsize=12, fontweight='bold')
bars = ax1.bar(components, exp_var * 100, color=color, alpha=0.7, width=0.55, label='Individual Variance')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xticks(components)
ax1.set_xticklabels([f'PC{i}' for i in components])

ax2 = ax1.twinx()
color = '#d62728'
ax2.set_ylabel('Cumulative Explained Variance (%)', color=color, fontsize=12, fontweight='bold')
ax2.plot(components, cum_exp_var * 100, color=color, marker='o', linewidth=2.5, markersize=7, label='Cumulative Variance')
ax2.axhline(y=80, color='gray', linestyle='--', linewidth=1, label='80% Variance Threshold')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(0, 105)

plt.title('PCA Scree Plot & Cumulative Explained Variance (Vijayawada-Guntur)', fontsize=13, fontweight='bold', pad=15)
fig.tight_layout()
plt.savefig("outputs/figures/07_pca_scree_plot.png", dpi=300)
plt.close()
print("Saved outputs/figures/07_pca_scree_plot.png")

# 3. PCA 2D Fit & Loadings
pca_2d = PCA(n_components=2, random_state=42)
X_pca = pca_2d.fit_transform(X)

df['pca_1'] = np.round(X_pca[:, 0], 4)
df['pca_2'] = np.round(X_pca[:, 1], 4)

# Loadings matrix (Correlation of original features with PC1 and PC2)
loadings = pd.DataFrame(
    pca_2d.components_.T,
    columns=['PC1_Loading', 'PC2_Loading'],
    index=feature_display_names
)
loadings['PC1_Contribution_%'] = np.round((loadings['PC1_Loading']**2) * 100, 2)
loadings['PC2_Contribution_%'] = np.round((loadings['PC2_Loading']**2) * 100, 2)
loadings.to_csv("outputs/tables/pca_loadings.csv")
print("\n--- PCA Feature Loadings Matrix ---")
print(loadings.to_string())

# 4. 2D PCA Cluster Projection
tier_palette = {
    'High Relative Hazard / Vulnerability': '#d73027',    # Red
    'Moderate Relative Hazard / Vulnerability': '#fdae61',# Orange
    'Relatively Lower Hazard / Vulnerability': '#4575b4' # Blue
}

plt.figure(figsize=(9, 6.5))
for tier, color in tier_palette.items():
    subset = df[df['relative_hazard_level'] == tier]
    plt.scatter(
        subset['pca_1'], subset['pca_2'],
        c=color, label=f"{tier} (n={len(subset)})",
        s=80, alpha=0.85, edgecolors='black', linewidth=0.6
    )

# Annotate landmark habitations
key_habs = ['Ajit Singh Nagar', 'Tadepalle', 'Undavalli', 'Kollipara', 'Amaravati', 'Guntur Central (Brodipet)', 'Mylavaram', 'Jaggayyapeta']
for _, r in df[df['habitation_name'].isin(key_habs)].iterrows():
    plt.annotate(
        r['habitation_name'],
        (r['pca_1'], r['pca_2']),
        xytext=(5, 5), textcoords='offset points',
        fontsize=8.5, fontweight='bold', alpha=0.9
    )

pc1_pct = round(exp_var[0] * 100, 1)
pc2_pct = round(exp_var[1] * 100, 1)
plt.title(f"2D PCA Projection of Habitations by Relative Hazard Tier (PC1: {pc1_pct}%, PC2: {pc2_pct}%)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel(f"Principal Component 1 ({pc1_pct}% variance) [<- High Flood Inundation & Congestion vs Upland Elevation ->]", fontsize=10.5, fontweight='bold')
plt.ylabel(f"Principal Component 2 ({pc2_pct}% variance) [<- Rainfall Extremes vs Inland Dry ->]", fontsize=10.5, fontweight='bold')
plt.axhline(0, color='gray', linestyle=':', linewidth=0.8)
plt.axvline(0, color='gray', linestyle=':', linewidth=0.8)
plt.legend(loc='lower left', frameon=True, fontsize=9.5)
plt.tight_layout()
plt.savefig("outputs/figures/08_pca_2d_clusters.png", dpi=300)
plt.close()
print("Saved outputs/figures/08_pca_2d_clusters.png")

# 5. PCA Biplot (Observations + Vector Loadings)
plt.figure(figsize=(10, 7))
for tier, color in tier_palette.items():
    subset = df[df['relative_hazard_level'] == tier]
    plt.scatter(subset['pca_1'], subset['pca_2'], c=color, label=tier, s=60, alpha=0.5, edgecolors='none')

# Scaling factor for loading vectors
scale_vec = 4.2
for i, feature_name in enumerate(feature_display_names):
    dx = pca_2d.components_[0, i] * scale_vec
    dy = pca_2d.components_[1, i] * scale_vec
    plt.arrow(0, 0, dx, dy, color='darkred', width=0.03, head_width=0.15, alpha=0.9, zorder=5)
    plt.text(dx * 1.15, dy * 1.15, feature_name, color='black', fontsize=9, fontweight='bold', ha='center', va='center', zorder=6)

plt.title("PCA Biplot: Hazard Feature Vectors Driving Habitation Separability", fontsize=13, fontweight='bold', pad=12)
plt.xlabel(f"PC1 ({pc1_pct}%)", fontsize=11, fontweight='bold')
plt.ylabel(f"PC2 ({pc2_pct}%)", fontsize=11, fontweight='bold')
plt.axhline(0, color='gray', linestyle=':', linewidth=0.8)
plt.axvline(0, color='gray', linestyle=':', linewidth=0.8)
plt.legend(loc='upper right', frameon=True, fontsize=9)
plt.tight_layout()
plt.savefig("outputs/figures/09_pca_biplot.png", dpi=300)
plt.close()
print("Saved outputs/figures/09_pca_biplot.png")

# 6. t-SNE Non-Linear Manifold Projection
print("\nComputing 2D t-SNE Manifold Projection...")
tsne = TSNE(n_components=2, perplexity=20, random_state=42, max_iter=1000)
X_tsne = tsne.fit_transform(X)

df['tsne_1'] = np.round(X_tsne[:, 0], 4)
df['tsne_2'] = np.round(X_tsne[:, 1], 4)

plt.figure(figsize=(9, 6.5))
for tier, color in tier_palette.items():
    subset = df[df['relative_hazard_level'] == tier]
    plt.scatter(
        subset['tsne_1'], subset['tsne_2'],
        c=color, label=f"{tier} (n={len(subset)})",
        s=80, alpha=0.85, edgecolors='black', linewidth=0.6
    )

plt.title("t-SNE Non-Linear Manifold Projection of Habitation Clusters (Perplexity=20)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("t-SNE Dimension 1", fontsize=11, fontweight='bold')
plt.ylabel("t-SNE Dimension 2", fontsize=11, fontweight='bold')
plt.legend(loc='upper right', frameon=True, fontsize=9.5)
plt.tight_layout()
plt.savefig("outputs/figures/10_tsne_clusters.png", dpi=300)
plt.close()
print("Saved outputs/figures/10_tsne_clusters.png")

# Save final comprehensive analysis CSV
df.to_csv("data/processed/habitations_complete_analysis.csv", index=False)
print("Saved data/processed/habitations_complete_analysis.csv")
print("Unit IV Dimensionality Reduction completed successfully!")
