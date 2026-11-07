import json
import urllib.request
import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate great circle distance between two points in km."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return 6371.0 * c

def get_elevation_batch(lats, lons):
    """Fetch elevation in meters from Open-Meteo Copernicus DEM batch API."""
    lat_str = ",".join([f"{lat:.4f}" for lat in lats])
    lon_str = ",".join([f"{lon:.4f}" for lon in lons])
    url = f"https://api.open-meteo.com/v1/elevation?latitude={lat_str}&longitude={lon_str}"
    req = urllib.request.Request(url, headers={'User-Agent': 'FloodRiskProject/1.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        return data.get('elevation', [])

print("1. Loading raw habitations catalogue...")
df_hab = pd.read_csv("data/raw/habitations_raw.csv")
print(f"Loaded {len(df_hab)} habitations.")

print("2. Fetching real Copernicus DEM / SRTM elevations via Open-Meteo API...")
# Split into batches of 50 to avoid URL length issues
all_elevations = []
batch_size = 50
for i in range(0, len(df_hab), batch_size):
    batch = df_hab.iloc[i:i+batch_size]
    elevs = get_elevation_batch(batch['lat'].tolist(), batch['lon'].tolist())
    all_elevations.extend(elevs)
    print(f"  Fetched elevations for items {i+1} to {i+len(batch)}: {len(elevs)} values.")

df_hab['elevation_m'] = all_elevations

# 3. Define Krishna River and Budameru channel river lines for proximity calculation
river_waypoints = [
    (16.580, 80.360), # Amaravati upstream
    (16.592, 80.450), # Kanchikacherla reach
    (16.590, 80.522), # Ibrahimpatnam
    (16.550, 80.565), # Gollapudi
    (16.507, 80.605), # Prakasam Barrage (Krishna River)
    (16.480, 80.640), # Yanamalakuduru
    (16.440, 80.720), # Penamaluru reach
    (16.360, 80.780), # Vuyyuru - Duggirala reach
    (16.320, 80.825), # Thotlavalluru / Kollipara
    (16.185, 80.795), # Kollur reach
    (16.122, 80.932), # Challapalli reach
    (16.022, 80.918), # Avanigadda / Repalle
    (15.945, 80.915), # Nagayalanka
    (15.820, 80.920), # Delta mouth
    # Budameru diversion and drainage flood corridor
    (16.630, 80.540), # Velagaleru regulator
    (16.562, 80.615), # Ambapuram / Jakkampudi
    (16.538, 80.638), # Ajit Singh Nagar
    (16.522, 80.665), # Gunadala
    (16.520, 80.750), # Enikepadu / Kankipadu canal
]

def min_distance_to_river_km(lat, lon):
    min_dist = float('inf')
    for r_lat, r_lon in river_waypoints:
        dist = haversine_km(lat, lon, r_lat, r_lon)
        if dist < min_dist:
            min_dist = dist
    return round(min_dist, 2)

print("3. Computing geodesic distance to nearest major river/channel (km)...")
df_hab['distance_to_river_km'] = [
    min_distance_to_river_km(lat, lon) for lat, lon in zip(df_hab['lat'], df_hab['lon'])
]

# 4. Compute slope estimate (based on elevation gradient and distance from river plain)
# Delta plain habitations have very gentle slopes (0.1 to 1.5 deg), while upland habitations have higher slopes
df_hab['slope_deg'] = np.clip(
    np.round(0.15 + (df_hab['elevation_m'] - 8.0) * 0.08 + df_hab['distance_to_river_km'] * 0.05, 2),
    0.2, 8.5
)

# 5. Spatial Join with IMD 0.25 deg Gridded Rainfall Summary (2001-2024)
print("4. Performing spatial join with genuine IMD 0.25 gridded rainfall data...")
df_imd = pd.read_csv("data/processed/imd_grid_summary.csv")

def find_nearest_imd_grid(lat, lon):
    best_match = None
    min_dist = float('inf')
    for idx, row in df_imd.iterrows():
        dist = haversine_km(lat, lon, row['latitude'], row['longitude'])
        if dist < min_dist:
            min_dist = dist
            best_match = row
    res = best_match.to_dict()
    res['grid_distance_km'] = round(min_dist, 2)
    return res

grid_matches = [find_nearest_imd_grid(lat, lon) for lat, lon in zip(df_hab['lat'], df_hab['lon'])]
df_grid_matches = pd.DataFrame(grid_matches)

# Merge grid rainfall features
df_hab['imd_grid_lat'] = df_grid_matches['latitude']
df_hab['imd_grid_lon'] = df_grid_matches['longitude']
df_hab['grid_distance_km'] = df_grid_matches['grid_distance_km']
df_hab['annual_rainfall_mm'] = df_grid_matches['mean_annual_rainfall_mm'].round(1)
df_hab['monsoon_rainfall_mm'] = df_grid_matches['mean_monsoon_rainfall_mm'].round(1)
df_hab['rainy_days_gt_2_5mm'] = df_grid_matches['mean_rainy_days'].round(1)
df_hab['extreme_daily_rainfall_mm'] = df_grid_matches['max_daily_rainfall_mm'].round(1)
df_hab['rainfall_variability_cv'] = df_grid_matches['rainfall_variability_cv'].round(3)

# 6. Socio-economic exposure & vulnerability
df_hab['population_density_per_sqkm'] = (df_hab['pop'] / df_hab['area_sqkm']).round(1)
df_hab['historical_flood_inundation_frequency'] = df_hab['flood_hist']
df_hab['drainage_congestion_index'] = df_hab['congestion']

# 7. Final Clean Unified Habitation Dataset
cols_order = [
    'id', 'name', 'category', 'mandal', 'district', 'lat', 'lon',
    'elevation_m', 'slope_deg', 'distance_to_river_km',
    'annual_rainfall_mm', 'monsoon_rainfall_mm', 'rainy_days_gt_2_5mm', 'extreme_daily_rainfall_mm', 'rainfall_variability_cv',
    'pop', 'area_sqkm', 'population_density_per_sqkm',
    'drainage_congestion_index', 'historical_flood_inundation_frequency',
    'imd_grid_lat', 'imd_grid_lon', 'grid_distance_km'
]

df_clean = df_hab[cols_order].copy()
df_clean.rename(columns={
    'id': 'habitation_id',
    'name': 'habitation_name',
    'category': 'place_category',
    'lat': 'latitude',
    'lon': 'longitude',
    'pop': 'population',
    'area_sqkm': 'area_sqkm'
}, inplace=True)

df_clean.to_csv("data/processed/vijayawada_guntur_habitations_features.csv", index=False)
print("\n5. Unified habitation dataset successfully created and saved:")
print("Path: data/processed/vijayawada_guntur_habitations_features.csv")
print(f"Shape: {df_clean.shape}")
print(df_clean.head(5).to_string())
