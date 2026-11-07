# Data Source Register (Pan-India Multi-State System)
## Project ID: SIH26191
### Hazard-Based Red-Zone Identification for Vulnerable Habitations Using Clustering
**Coverage:** Pan-India (15 States / UTs, 92 Districts, 229 Habitations) + Complete 26 Districts of Andhra Pradesh + Real-Time Live Weather Feed

---

### Source 1: India Meteorological Department (IMD) High-Resolution Gridded & Climatological Rainfall
* **Dataset Name:** IMD Daily Gridded Rainfall Data (0.25° x 0.25° Resolution) & National Climatological Rainfall Normals
* **Provider:** India Meteorological Department (IMD), Ministry of Earth Sciences, Govt. of India / IMD Pune
* **Portal / Download URL:** https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html
* **File Formats:** NetCDF (`imdweb_nbdLkllF.nc`), Gridded CSV (`Guntur_Vijayawada_Rainfall_Summary.csv`), and IMD Climatological Atlas
* **Geographic Coverage:** Latitudes 8.0°N to 35.0°N, Longitudes 68.0°E to 96.0°E (Pan-India coverage with high-density grid for Andhra Pradesh)
* **Time Period:** 2001 – 2024 (24 full consecutive years, 8,766 daily timesteps)
* **License / Access:** Open Access for Academic & Research Use
* **Features Extracted:** Mean Annual Rainfall (mm), Mean Monsoon Rainfall (Jun–Sep mm), Rainy Days count (> 2.5 mm), Maximum Single-Day Extreme Rainfall (mm), Rainfall Inter-Annual Coefficient of Variation (CV).

---

### Source 2: Copernicus Global Digital Elevation Model (DEM) / SRTM via Open-Meteo API
* **Dataset Name:** Copernicus DEM GLO-90 / GLO-30 & Shuttle Radar Topography Mission (SRTM)
* **Provider:** European Space Agency (ESA) / Copernicus Programme & NASA/USGS, served via Open-Meteo High-Resolution Elevation API
* **Portal / Download URL:** https://open-meteo.com/en/docs/elevation-api
* **Geographic Coverage:** Exact point-level elevations for all 166 catalogued habitations across 15 Indian States
* **Time Period:** Static baseline topographic model (2020 release)
* **License / Access:** Open Data Commons / Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Features Extracted:** Ground Elevation above Mean Sea Level (meters), Topographic Slope (degrees).

---

### Source 3: India Flood Inventory-Impacts (IFI-Impacts) [1967–2023]
* **Dataset Name:** India Flood Inventory-Impacts (IFI-Impacts): A multi-source national geospatial database to facilitate comprehensive flood research
* **Provider / Authors:** Dr. Manabendra Saharia, HydroSense Lab, Department of Civil Engineering, Indian Institute of Technology Delhi (IIT Delhi)
* **Repository / DOI:** Zenodo, DOI: 10.5281/zenodo.16994648 (https://doi.org/10.5281/zenodo.16994648)
* **Geographic Coverage:** National India coverage across all major flood basins (Brahmaputra, Ganga, Kosi, Krishna, Godavari, Mahanadi, Tapi, Narmada, Periyar, Cauvery)
* **Time Period:** 1967 – 2023
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Features Extracted:** Historical flood event frequencies, affected sub-districts/mandals, flood severity impact tiers.

---

### Source 4: OpenStreetMap (OSM) & Local Government Directory (LGD) Administrative Registry
* **Dataset Name:** Habitations, Municipal Localities, and Gram Panchayats of India
* **Provider:** OpenStreetMap Contributors (ODbL) & Ministry of Panchayati Raj / Census of India 2011
* **Portal / Download URL:** https://www.openstreetmap.org / https://lgdirectory.gov.in / https://censusindia.gov.in
* **Geographic Coverage:** 166 genuine settlements across 15 States/UTs:
  - Andhra Pradesh (100 habitations)
  - Assam (8 habitations: Guwahati, Majuli Island, Kaziranga, Silchar, Dibrugarh, Barpeta, Mayang, Dhubri)
  - Bihar (8 habitations: Patna, Nirmali/Kosi, Kahalgaon, Kusheshwar Asthan, Aurai/Bagmati, Alauli, Rosera, Gaya)
  - Kerala (6 habitations: Champakkulam/Kuttanad, Aluva/Periyar, Chalakudy, Ranni, Mananthavady, Munnar)
  - Odisha (6 habitations: Marsaghai/Mahanadi, Cuttack, Kanas/Daya, Kujang, Jaleswar, Sambalpur)
  - West Bengal (6 habitations: Kolkata, Ghatal/Silabati, Gosaba/Sundarbans, Manikchak/Ganga, Jalpaiguri, Purulia)
  - Maharashtra (6 habitations: Kurla/Mithi, Chiplun/Vashishti, Kolhapur/Panchaganga, Sangli, Mahad, Sambhajinagar)
  - Uttar Pradesh (5 habitations: Gorakhpur/Rapti, Varanasi, Prayagraj, Ayodhya, Jhansi)
  - Tamil Nadu (5 habitations: Velachery/Adyar, Cuddalore, Nagapattinam, Thoothukudi, Coimbatore)
  - Gujarat (4 habitations: Surat/Tapi, Vadodara, Bharuch, Bhuj)
  - Karnataka (4 habitations: Chikkodi/Krishna, Jamkhandi, Mangaluru, Bengaluru)
  - Delhi (3 habitations: Yamuna Bazar, Mayur Vihar, Chanakyapuri)
  - Punjab (3 habitations: Rupnagar/Sutlej, Samana/Ghaggar, Bathinda)
  - Uttarakhand (1 habitation: Haridwar)
  - Himachal Pradesh (1 habitation: Kullu)
* **Features Extracted:** Habitation Name, State, District, Mandal/Subdistrict, WGS84 Coordinates, Population, Population Density (/km²).

---

### Source 5: River Hydrography & River Basins (Central Water Commission)
* **Dataset Name:** Major River Basin Floodways of India
* **Provider:** Central Water Commission (CWC) / Survey of India Open Topo
* **Portal / Download URL:** https://cwc.gov.in
* **Features Extracted:** Geodesic Distance to Primary River/Floodway (km), Drainage Congestion Index (1–5 scale), Major River Basin classification.


---

### Source 6: Open-Meteo High-Resolution Real-Time Weather & Precipitation Forecast API
* **Dataset Name:** Open-Meteo Seamless Numerical Weather Prediction & Real-Time Observations Grid
* **Provider:** Open-Meteo GmbH / WMO Data Sources (DWD ICON, NOAA GFS, ECMWF IFS)
* **Portal / Endpoint:** https://api.open-meteo.com/v1/forecast
* **Geographic Coverage:** Point-level real-time observations for all 229 catalogued habitations and district centroids
* **Time Period:** Real-time live observation feed (15-minute resolution) + past 24-hour antecedent rainfall
* **License:** Open Access / Attribution (Non-commercial & research use under CC BY 4.0)
* **Features Extracted:** Current Ambient Temperature (°C), Apparent Temperature (°C), Relative Humidity (%), Active Rain Rate (mm/h), Past 24-Hour Accumulated Rainfall (mm), WMO Weather Code / Conditions, Wind Speed (km/h), Surface Atmospheric Pressure (hPa).
