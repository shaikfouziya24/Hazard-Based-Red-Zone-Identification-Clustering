import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

# Set aesthetic styling for academic publication
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

os.makedirs("outputs/figures", exist_ok=True)
os.makedirs("outputs/tables", exist_ok=True)

print("=== Step 1: Loading Processed Dataset ===")
df = pd.read_csv("data/processed/vijayawada_guntur_habitations_features.csv")
print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")

print("\n=== Step 2: Missing Value and Duplicate Audit ===")
null_counts = df.isnull().sum()
print("Missing values per column:\n", null_counts[null_counts > 0] if null_counts.sum() > 0 else "Zero missing values detected!")
duplicates = df.duplicated(subset=['habitation_name', 'latitude', 'longitude']).sum()
print(f"Exact coordinate duplicates: {duplicates}")

# Define the 9 Core Clustering Features
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

print("\n=== Step 3: Statistical Summary of Feature Set ===")
summary_stats = df[feature_cols].describe().T[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
summary_stats.to_csv("outputs/tables/feature_summary_statistics.csv")
print(summary_stats.round(2))

# Correlation Matrix
plt.figure(figsize=(10, 8))
corr = df[feature_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1,
            cbar_kws={'label': 'Pearson Correlation Coefficient'}, linewidths=0.5)
plt.title("Correlation Matrix of Hazard & Vulnerability Features (Vijayawada-Guntur)", fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig("outputs/figures/01_correlation_matrix.png", dpi=300)
plt.close()
print("Saved outputs/figures/01_correlation_matrix.png")

# Outlier and Distribution Boxplots
plt.figure(figsize=(14, 8))
df_box = df[feature_cols].copy()
scaler_temp = StandardScaler()
scaled_box = scaler_temp.fit_transform(df_box)
df_scaled_box = pd.DataFrame(scaled_box, columns=[c.replace('_', '\n') for c in feature_cols])

sns.boxplot(data=df_scaled_box, palette="Set2", fliersize=4)
plt.title("Standardized Distribution and Outlier Inspection across Features", fontsize=14, fontweight='bold', pad=12)
plt.ylabel("Standardized Score (Z-Score)", fontsize=11)
plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
plt.tight_layout()
plt.savefig("outputs/figures/02_feature_outlier_boxplots.png", dpi=300)
plt.close()
print("Saved outputs/figures/02_feature_outlier_boxplots.png")

# Normalization using StandardScaler
print("\n=== Step 4: Standardization (Z-Score Normalization) ===")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[feature_cols])

# Save normalized dataset for modeling
df_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
df_scaled['habitation_id'] = df['habitation_id']
df_scaled['habitation_name'] = df['habitation_name']
df_scaled['district'] = df['district']
df_scaled.to_csv("data/processed/habitations_scaled_features.csv", index=False)
print("Standardized dataset saved to data/processed/habitations_scaled_features.csv")
print("Preprocessing completed successfully!")
