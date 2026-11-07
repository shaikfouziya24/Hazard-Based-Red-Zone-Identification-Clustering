import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import folium
from folium import plugins

# Setup plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.dpi'] = 300

os.makedirs("outputs/figures", exist_ok=True)
os.makedirs("outputs/tables", exist_ok=True)

print("=== Step 8: Quantitative Cluster Profiling & Spatial GIS Mapping ===")
df = pd.read_csv("data/processed/habitations_complete_analysis.csv")

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

# 1. Compute Mean and Std Profiles for Each Relative Hazard Tier
tier_order = [
    'High Relative Hazard / Vulnerability',
    'Moderate Relative Hazard / Vulnerability',
    'Relatively Lower Hazard / Vulnerability'
]

profile_mean = df.groupby('relative_hazard_level')[feature_cols].mean().loc[tier_order]
profile_std = df.groupby('relative_hazard_level')[feature_cols].std().loc[tier_order]

profile_summary = []
for tier in tier_order:
    m = profile_mean.loc[tier]
    s = profile_std.loc[tier]
    row = {'Relative Hazard Tier': tier, 'Habitations Count': int((df['relative_hazard_level'] == tier).sum())}
    for col in feature_cols:
        row[f'{col}_mean'] = round(m[col], 2)
        row[f'{col}_std'] = round(s[col], 2)
    profile_summary.append(row)

df_profile_summary = pd.DataFrame(profile_summary)
df_profile_summary.to_csv("outputs/tables/cluster_feature_profiles.csv", index=False)
print("\n--- Quantitative Cluster Profiles (Mean Values) ---")
print(profile_mean.round(2).to_string())

# 2. Normalized Radar / Spider Chart
# Normalize means to [0, 1] range for visual comparison across different units
min_vals = df[feature_cols].min()
max_vals = df[feature_cols].max()
norm_profiles = (profile_mean - min_vals) / (max_vals - min_vals)

categories = [
    'Elevation\n(Inverted)',
    'Slope\n(Inverted)',
    'River Dist\n(Inverted)',
    'Annual Rain',
    'Monsoon Rain',
    'Extreme Rain',
    'Pop Density',
    'Drainage\nCongestion',
    'Flood\nFrequency'
]

# Invert elevation, slope, and river distance so that higher values on the radar chart consistently represent HIGHER HAZARD
radar_data = norm_profiles.copy()
radar_data['elevation_m'] = 1.0 - radar_data['elevation_m']
radar_data['slope_deg'] = 1.0 - radar_data['slope_deg']
radar_data['distance_to_river_km'] = 1.0 - radar_data['distance_to_river_km']

N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1] # Close the circle

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
plt.xticks(angles[:-1], categories, color='black', size=10, fontweight='bold')
ax.set_rlabel_position(0)
plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], color="grey", size=8)
plt.ylim(0, 1.05)

colors = {'High Relative Hazard / Vulnerability': '#d73027',
          'Moderate Relative Hazard / Vulnerability': '#fdae61',
          'Relatively Lower Hazard / Vulnerability': '#4575b4'}

for tier in tier_order:
    values = radar_data.loc[tier].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=2.2, linestyle='solid', label=tier, color=colors[tier])
    ax.fill(angles, values, color=colors[tier], alpha=0.18)

plt.title("Multi-Criteria Flood Hazard & Vulnerability Signature by Cluster", size=13, fontweight='bold', pad=25)
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1), frameon=True, fontsize=9.5)
plt.tight_layout()
plt.savefig("outputs/figures/11_cluster_radar_signature.png", dpi=300)
plt.close()
print("Saved outputs/figures/11_cluster_radar_signature.png")

# 3. Comparative Grouped Bar Charts for Key Indicators
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
bar_colors = ['#d73027', '#fdae61', '#4575b4']

# (a) Elevation
axes[0, 0].bar(tier_order, profile_mean['elevation_m'], color=bar_colors, edgecolor='black', width=0.55)
axes[0, 0].set_title("Mean Surface Elevation (m AMSL)", fontweight='bold', fontsize=12)
axes[0, 0].set_ylabel("Meters", fontweight='bold')
axes[0, 0].set_xticklabels(['High Hazard', 'Moderate', 'Lower Hazard'], fontweight='bold')
for i, v in enumerate(profile_mean['elevation_m']):
    axes[0, 0].text(i, v + 0.8, f"{v:.1f} m", ha='center', fontweight='bold')

# (b) Distance to Major River / Canal
axes[0, 1].bar(tier_order, profile_mean['distance_to_river_km'], color=bar_colors, edgecolor='black', width=0.55)
axes[0, 1].set_title("Mean Distance to Major River / Floodway (km)", fontweight='bold', fontsize=12)
axes[0, 1].set_ylabel("Kilometers", fontweight='bold')
axes[0, 1].set_xticklabels(['High Hazard', 'Moderate', 'Lower Hazard'], fontweight='bold')
for i, v in enumerate(profile_mean['distance_to_river_km']):
    axes[0, 1].text(i, v + 0.6, f"{v:.1f} km", ha='center', fontweight='bold')

# (c) Historical Flood Inundation Frequency
axes[1, 0].bar(tier_order, profile_mean['historical_flood_inundation_frequency'], color=bar_colors, edgecolor='black', width=0.55)
axes[1, 0].set_title("Historical Flood Inundation Frequency (2000-2024)", fontweight='bold', fontsize=12)
axes[1, 0].set_ylabel("Documented Events (0-5)", fontweight='bold')
axes[1, 0].set_xticklabels(['High Hazard', 'Moderate', 'Lower Hazard'], fontweight='bold')
for i, v in enumerate(profile_mean['historical_flood_inundation_frequency']):
    axes[1, 0].text(i, v + 0.08, f"{v:.2f}", ha='center', fontweight='bold')

# (d) Extreme Daily Rainfall
axes[1, 1].bar(tier_order, profile_mean['extreme_daily_rainfall_mm'], color=bar_colors, edgecolor='black', width=0.55)
axes[1, 1].set_title("Historical Maximum Daily Rainfall (mm)", fontweight='bold', fontsize=12)
axes[1, 1].set_ylabel("24h Rain (mm)", fontweight='bold')
axes[1, 1].set_xticklabels(['High Hazard', 'Moderate', 'Lower Hazard'], fontweight='bold')
for i, v in enumerate(profile_mean['extreme_daily_rainfall_mm']):
    axes[1, 1].text(i, v + 4.0, f"{v:.1f} mm", ha='center', fontweight='bold')

plt.suptitle("Cluster Profile Comparison: Key Biophysical and Hazard Features", fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig("outputs/figures/12_cluster_feature_bars.png", dpi=300)
plt.close()
print("Saved outputs/figures/12_cluster_feature_bars.png")

# 4. Interactive GIS Map with Folium
print("\nBuilding Interactive Folium GIS Map...")
center_lat, center_lon = 16.42, 80.60
m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="CartoDB positron")

# Add tile layer choices
folium.TileLayer('OpenStreetMap').add_to(m)

# Add River Polylines
krishna_river_coords = [
    [16.580, 80.360],
    [16.592, 80.450],
    [16.590, 80.522],
    [16.550, 80.565],
    [16.507, 80.605], # Prakasam Barrage
    [16.480, 80.640],
    [16.440, 80.720],
    [16.360, 80.780],
    [16.320, 80.825],
    [16.185, 80.795],
    [16.122, 80.932],
    [16.022, 80.918],
    [15.945, 80.915]
]
folium.PolyLine(
    krishna_river_coords,
    color="#0066cc",
    weight=5,
    opacity=0.85,
    tooltip="Krishna River Main Channel (Prakasam Barrage System)"
).add_to(m)

budameru_coords = [
    [16.630, 80.540],
    [16.562, 80.615],
    [16.538, 80.638],
    [16.522, 80.665],
    [16.520, 80.750]
]
folium.PolyLine(
    budameru_coords,
    color="#0099ff",
    weight=3.5,
    dash_array='8, 8',
    opacity=0.85,
    tooltip="Budameru Rivulet & Drainage Diversion Floodway"
).add_to(m)

# Create FeatureGroups for the 3 clusters
fg_high = folium.FeatureGroup(name="High Relative Hazard / Vulnerability (Red)")
fg_mod = folium.FeatureGroup(name="Moderate Relative Hazard / Vulnerability (Orange)")
fg_low = folium.FeatureGroup(name="Relatively Lower Hazard / Vulnerability (Blue)")

color_map = {
    'High Relative Hazard / Vulnerability': ('#d73027', fg_high),
    'Moderate Relative Hazard / Vulnerability': ('#fdae61', fg_mod),
    'Relatively Lower Hazard / Vulnerability': ('#4575b4', fg_low)
}

for _, r in df.iterrows():
    c_hex, fg = color_map[r['relative_hazard_level']]
    
    popup_html = f"""
    <div style="font-family: Arial; width: 260px; font-size: 12px;">
        <h4 style="margin: 0 0 6px 0; color: {c_hex}; border-bottom: 2px solid {c_hex}; padding-bottom: 4px;">
            {r['habitation_name']}
        </h4>
        <b>District:</b> {r['district']}<br>
        <b>Mandal:</b> {r['mandal']}<br>
        <b>Category:</b> {r['place_category']}<br>
        <hr style="margin: 6px 0;">
        <b>Relative Cluster:</b> <span style="color: {c_hex}; font-weight: bold;">{r['relative_hazard_level']}</span><br>
        <b>Elevation:</b> {r['elevation_m']:.1f} m AMSL<br>
        <b>Distance to River/Channel:</b> {r['distance_to_river_km']:.2f} km<br>
        <b>Historical Flood Events:</b> {r['historical_flood_inundation_frequency']}/5<br>
        <b>Drainage Congestion:</b> {r['drainage_congestion_index']}/5<br>
        <b>Annual Rain:</b> {r['annual_rainfall_mm']:.1f} mm<br>
        <b>Max Daily Rain:</b> {r['extreme_daily_rainfall_mm']:.1f} mm<br>
        <b>Pop Density:</b> {r['population_density_per_sqkm']:,.0f} /km²<br>
    </div>
    """
    
    folium.CircleMarker(
        location=[r['latitude'], r['longitude']],
        radius=7 if r['relative_hazard_level'] == 'High Relative Hazard / Vulnerability' else 5.5,
        color='black',
        weight=0.8,
        fill=True,
        fill_color=c_hex,
        fill_opacity=0.85,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{r['habitation_name']} ({r['relative_hazard_level']})"
    ).add_to(fg)

fg_high.add_to(m)
fg_mod.add_to(m)
fg_low.add_to(m)

# Add Legend
legend_html = '''
<div style="position: fixed; 
     bottom: 30px; left: 30px; width: 330px; height: 185px; 
     background-color: white; border:2px solid #888; z-index:9999; font-size:11.5px;
     padding: 10px; border-radius: 6px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
     <b>SIH26191: Flood Hazard & Vulnerability Tiers</b><br>
     <i>Vijayawada–Guntur Study Area (AP)</i><br>
     <hr style="margin: 5px 0;">
     <i class="fa fa-circle" style="color:#d73027"></i> &nbsp;<b>High Relative Hazard / Vulnerability</b> (n=47)<br>
     <i class="fa fa-circle" style="color:#fdae61"></i> &nbsp;<b>Moderate Relative Hazard / Vulnerability</b> (n=32)<br>
     <i class="fa fa-circle" style="color:#4575b4"></i> &nbsp;<b>Relatively Lower Hazard / Vulnerability</b> (n=21)<br>
     <span style="color:#0066cc; font-weight:bold;">―</span> &nbsp;Krishna River / Prakasam Barrage<br>
     <span style="color:#0099ff; font-weight:bold;">- -</span> &nbsp;Budameru Drainage Diversion<br>
     <small style="color: #666;">Note: Academic unsupervised classification; not an official disaster warning.</small>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))
folium.LayerControl(collapsed=False).add_to(m)

map_path = "outputs/figures/vijayawada_guntur_flood_hazard_map.html"
m.save(map_path)
print(f"Saved interactive GIS map to {map_path}")
print("Step 8 completed successfully!")
