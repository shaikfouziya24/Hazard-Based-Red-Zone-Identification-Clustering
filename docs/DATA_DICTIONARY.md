# Data Dictionary
## Dataset: `vijayawada_guntur_habitations_features.csv`
### Project ID: SIH26191 — Hazard-Based Red-Zone Identification Using Clustering

| Column Name | Data Type | Units | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `habitation_id` | String | Identifier | Project Registry | Unique sequential identifier for each habitation (`HAB_001` to `HAB_100`). |
| `habitation_name` | String | Name | Census / OSM / LGD | Official name of the settlement, municipal locality, or gram panchayat. |
| `place_category` | Categorical | Class | OSM / LGD | Category of settlement: `Urban Locality`, `Town`, `Village`, `Urban Outgrowth`. |
| `mandal` | String | Admin Unit | AP Govt. Revenue Records | Sub-district / Tahsil administration unit (e.g., `Vijayawada North`, `Thullur`, `Tenali`). |
| `district` | Categorical | Admin Unit | AP Reorganized Districts | District name (`NTR`, `Guntur`, `Krishna`, `Guntur / Bapatla`). |
| `latitude` | Float64 | Decimal Degrees | WGS84 GPS / OSM | Geographic latitude coordinate in WGS84 datum (EPSG:4326). |
| `longitude` | Float64 | Decimal Degrees | WGS84 GPS / OSM | Geographic longitude coordinate in WGS84 datum (EPSG:4326). |
| `elevation_m` | Float64 | Meters (m) | Copernicus DEM 90m | Surface elevation above mean sea level. Low values indicate flood depression zones. |
| `slope_deg` | Float64 | Degrees (°) | DEM Gradient Analysis | Topographic slope inclination. Lower slope impedes natural storm runoff. |
| `distance_to_river_km` | Float64 | Kilometers (km) | Geodesic Calculation | Minimum geodesic distance to the Krishna River or Budameru flood corridor. |
| `annual_rainfall_mm` | Float64 | Millimeters (mm) | IMD Pune 0.25° Grid | Long-term 24-year mean annual precipitation (2001–2024). |
| `monsoon_rainfall_mm` | Float64 | Millimeters (mm) | IMD Pune 0.25° Grid | Long-term 24-year mean southwest monsoon precipitation (June–September). |
| `rainy_days_gt_2_5mm` | Float64 | Days / Year | IMD Pune 0.25° Grid | 24-year mean number of rainy days per year with precipitation > 2.5 mm. |
| `extreme_daily_rainfall_mm` | Float64 | Millimeters (mm) | IMD Pune 0.25° Grid | Historical maximum single-day 24-hour rainfall recorded between 2001 and 2024. |
| `rainfall_variability_cv` | Float64 | Ratio | IMD Pune 0.25° Grid | Inter-annual Coefficient of Variation (Std / Mean) of annual rainfall. |
| `population` | Int64 | Persons | Census of India 2011 | Total resident population of the habitation. |
| `area_sqkm` | Float64 | Square Kilometers | Urban Body / Panchayat | Geographic land footprint of the habitation in square kilometers. |
| `population_density_per_sqkm` | Float64 | Persons / km² | Computed | Population per unit area (`population / area_sqkm`), measuring human exposure. |
| `drainage_congestion_index` | Int64 | Score (1 to 5) | Field / Hydro Analysis | Drainage impedance rating (1=Freely draining upland, 5=Severe canal backwater entrapment). |
| `historical_flood_inundation_frequency` | Int64 | Count (0 to 5) | IFI-Impacts / APSDMA | Documented major flood inundations between 2000 and 2024 (e.g. 2005, 2009, 2016, 2020, 2024). |
| `imd_grid_lat` | Float64 | Decimal Degrees | IMD 0.25° Centroid | Latitude of nearest matched IMD gridded observation cell. |
| `imd_grid_lon` | Float64 | Decimal Degrees | IMD 0.25° Centroid | Longitude of nearest matched IMD gridded observation cell. |
| `grid_distance_km` | Float64 | Kilometers (km) | Spatial Join Audit | Distance from habitation centroid to the nearest IMD grid cell centroid. |


---

## Real-Time Live Weather & Dynamic Alert Features (Dashboard Live API)

| Variable Name | Data Type | Units | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `temp_c` | Float64 | °C | Open-Meteo Live API | Current observed 2-meter air temperature in Celsius. |
| `feels_like_c` | Float64 | °C | Open-Meteo Live API | Apparent temperature taking into account humidity and wind. |
| `humidity_pct` | Int64 | % | Open-Meteo Live API | Current relative humidity at 2 meters. |
| `rain_rate_mmh` | Float64 | mm/h | Open-Meteo Live API | Active rainfall intensity rate in millimeters per hour. |
| `past_24h_rain_mm` | Float64 | mm | Open-Meteo Hourly API | Antecedent cumulative precipitation over the past 24 hours. |
| `weather_code` | Int64 | WMO Code | Open-Meteo Live API | World Meteorological Organization synoptic weather condition code (0=Clear, 61-65=Rain, 95=Thunderstorm). |
| `wind_kmh` | Float64 | km/h | Open-Meteo Live API | 10-meter wind speed in kilometers per hour. |
| `pressure_hpa` | Float64 | hPa | Open-Meteo Live API | Barometric surface air pressure. |
| `dynamic_flood_alert` | Categorical | Alert Level | Risk Engine Rule | Dynamic multi-hazard alert synthesizing baseline ML cluster with live 24h rain: `RED ALERT`, `ORANGE ALERT`, `YELLOW WATCH`, `GREEN STATUS`. |
