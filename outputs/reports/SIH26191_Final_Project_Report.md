# HAZARD-BASED RED-ZONE IDENTIFICATION FOR VULNERABLE HABITATIONS USING CLUSTERING

**Project ID:** SIH26191  
**Study Area:** Vijayawada–Guntur Region, Andhra Pradesh, India  
**Primary Hazard:** Floods (Krishna River Basin & Budameru Flood Corridor)  
**Degree / Academic Level:** B.Tech 3rd-Year Data Science / Machine Learning Project  
**Date:** November 2026  

---

> ⚠️ **ACADEMIC DISCLAIMER & ETHICAL MANDATE**  
> This project represents an exploratory unsupervised machine learning framework designed for multi-criteria risk vulnerability grouping across rural and urban settlements. Cluster designations (*"High Relative Hazard / Vulnerability"*, *"Moderate Relative Hazard / Vulnerability"*, and *"Relatively Lower Hazard / Vulnerability"*) reflect statistical grouping based on genuine environmental, hydrometeorological, and demographic features.  
> **Clustering alone does NOT constitute an official government disaster red-zone warning or statutory regulatory demarcation.** Official warning notices and evacuation mandates require statutory authority, physical levee breach verification, and real-time hydrodynamic discharge assessments from responsible disaster management bodies (APSDMA / NDMA / CWC).

---

## 1. Abstract
Coastal Andhra Pradesh is repeatedly subjected to devastating hydro-meteorological flood disasters, underscored by the catastrophic inundations of the Krishna River and Budameru drainage network in 2005, 2009, and September 2024. In the absence of comprehensive supervised damage labels for every rural village and municipal locality, unsupervised machine learning offers an objective, mathematically rigorous framework for identifying spatial habitations exhibiting common exposure and vulnerability characteristics. This academic project implements an end-to-end, reproducible unsupervised learning framework for 100 genuine habitations across NTR (Vijayawada), Guntur, and Krishna districts. The analytical pipeline integrates 24 years (2001–2024, 8,766 daily timesteps) of high-resolution 0.25° gridded precipitation data from the India Meteorological Department (IMD Pune), Copernicus DEM 90m topography, geodesic distances to the Krishna River course and Budameru floodway, empirical flood history from IIT Delhi's IFI-Impacts database, and Census of India demographic densities. Using standardized multi-criteria feature vectors, we systematically benchmark partition-based clustering (K-Means with random vs. K-Means++ initialization across K=2 to 5; K-Medoids / PAM with Manhattan L1 and Euclidean distances), hierarchical agglomerative clustering across four linkage criteria (Single, Complete, Average, Ward), and density-based clustering (DBSCAN). Dimensionality reduction via Principal Component Analysis (PCA) and t-SNE demonstrates that the top two principal components explain 65.89% of the total variance, with PC1 fundamentally capturing flood basin susceptibility and drainage stagnation. The optimal K=3 partition clearly isolates a High Relative Hazard Tier (n=47) characterized by low elevations (mean 13.1 m), near-zero slopes (0.91°), high annual rainfall (1,178 mm), severe 24h storm extremes (290.9 mm), and high drainage congestion. A fully functional interactive GIS web dashboard built in Streamlit and Folium enables spatial filtering, risk signature exploration, and transparent data auditing.

---

## 2. Introduction & Problem Statement
The twin urban and rural corridor of Vijayawada and Guntur, situated in coastal Andhra Pradesh, represents a critical economic, demographic, and agricultural engine of southern India. The region is traversed by the lower reaches of the Krishna River, controlled by the historic Prakasam Barrage, and interlaced with an intricate network of irrigation and drainage waterways, most notably the Budameru rivulet. In September 2024, a devastating flood triggered by extreme precipitation in the Budameru catchment and unprecedented inflows exceeding 11.4 lakh cusecs at Prakasam Barrage submerged large swathes of Vijayawada (including Ajit Singh Nagar, Payakapuram, Bhavanipuram, and Vidyadharapuram), displacing over 600,000 residents and paralyzing regional infrastructure.

Traditional disaster risk reduction approaches often rely on complex hydrodynamic hydraulic models (such as HEC-RAS or MIKE FLOOD), which require extensive bathymetric surveys, calibrated river cross-sections, and real-time gate operation telemetry that are rarely available for every rural habitation or municipal locality. Conversely, supervised machine learning models require comprehensive historical flood damage ground-truth labels for every village—labels that are frequently missing, incomplete, or biased toward major urban centers.

**Problem Statement:** How can environmental data scientists and disaster managers objectively identify, group, and rank vulnerable habitations exhibiting similar multi-criteria flood hazard and exposure characteristics using publicly accessible, genuine geospatial datasets without relying on subjective scoring or non-existent supervised labels?

---

## 3. Study Area & Dataset Provenance
The study area encompasses the Vijayawada–Guntur capital region of Andhra Pradesh, bounded between Latitudes 15.75°N to 16.75°N and Longitudes 80.00°E to 81.25°E. Five authentic, traceable public datasets were integrated into a final analysis-ready database (100 rows, 23 attributes):
1. **India Meteorological Department (IMD Pune):** High-resolution 0.25° x 0.25° gridded daily rainfall data (NetCDF & CSV) covering 17 grid cells over 2001–2024 (8,766 daily timesteps per cell). Features extracted: Mean Annual Rain (mm), Mean Monsoon Rain (mm), Rainy Days (>2.5 mm), Max 24h Daily Rain (mm), and Rainfall Inter-Annual CV.
2. **Copernicus DEM GLO-90 / SRTM:** Surface elevations above mean sea level extracted via Open-Meteo High-Resolution Elevation API for every habitation coordinate.
3. **OpenStreetMap & AP Panchayat Directory:** Centroids and administrative metadata for 100 genuine habitations across NTR, Guntur, and Krishna districts.
4. **Hydrographic Proximity:** Geodesic minimum distance (km) to the Krishna River course (Prakasam Barrage) and Budameru flood channel.
5. **IIT Delhi IFI-Impacts & APSDMA:** Documented major flood inundation events (2005, 2009, 2016, 2020, 2024).

---

## 4. Methodology & Data Preprocessing
The data preprocessing pipeline follows strict data hygiene principles:
1. **Missing Value and Duplicate Treatment:** Audited for null entries and coordinate duplicates. Exactly zero missing values and zero duplicate settlements were found.
2. **Spatial Join Architecture:** Habitations were joined to the nearest IMD 0.25° grid cell by computing great-circle geodesic distances. The mean distance from a village centroid to its assigned grid centroid was 12.8 km, ensuring spatial compatibility without assuming uniform precipitation across the entire state.
3. **Feature Scaling via StandardScaler:** Because clustering algorithms rely on distance calculations, features with large numeric spans (e.g. Population Density: 750 to 19,090 persons/km²; Annual Rainfall: 915 to 1,236 mm) would dominate features with small spans (e.g. Slope: 0.2° to 8.5°; Flood Frequency: 1 to 5). StandardScaler applies Z-score normalization:
$$z = \frac{x - \mu}{\sigma}$$
ensuring every feature exhibits mean = 0 and unit variance = 1.

---

## 5. Experimental Results & Algorithm Benchmarking

### 5.1 Partition-Based Clustering: K-Means & K-Medoids
* **K-Means Evaluation (K=2 to 5):**
  - K=2: WCSS = 567.92, Silhouette = 0.3572, Davies-Bouldin = 1.1776
  - **K=3 (Optimal):** WCSS = 420.44, **Silhouette = 0.3667**, Davies-Bouldin = 1.1202, Calinski-Harabasz = 55.32
  - K=4: WCSS = 351.79, Silhouette = 0.3715, Davies-Bouldin = 1.0069
  - K=5: WCSS = 291.16, Silhouette = 0.3599, Davies-Bouldin = 1.0272
* **K-Medoids (PAM) with Manhattan (L1) Distance:**
  - K=3: **Silhouette Score = 0.4320**, Davies-Bouldin = 1.1574
  - Selected authentic exemplar medoid habitations: **Munnangi** (delta reach), **Gorantla** (elevated Guntur ridge), and **Velagapudi** (Amaravati river terrace).

### 5.2 Hierarchical Clustering: Linkage Comparison
* **Ward's Linkage (K=3):** Balanced clusters (sizes 47, 32, 21), perfectly mirroring K-Means++. Silhouette = 0.3283, Davies-Bouldin = 1.0843.
* **Complete Linkage:** Unbalanced (68, 30, 2).
* **Average Linkage:** 83 habitations merged into one group.
* **Single Linkage:** Severe chaining effect (98 in one cluster, 2 singletons).
* **Ward Dendrogram:** Horizontal cut at dissimilarity threshold 11.5 cleanly separates the three risk branches.

### 5.3 Density-Based Clustering: DBSCAN
* Parameter selection using 4-NN distance knee curve: **eps = 1.85, min_samples = 4**.
* Identified 2 dense core clusters and **12 noise points (-1)** (12% of dataset).
* Crucially, DBSCAN isolated true geographic/demographic extremes:
  - Extreme urban flood disaster nodes: Ajit Singh Nagar, Payakapuram, Bhavanipuram, Vidyadharapuram, Undavalli.
  - Extreme upland ridge habitations: Mylavaram, Jaggayyapeta, Perecherla.

### 5.4 Dimensionality Reduction: PCA & t-SNE
* **PC1 (48.56% of variance):** Flood Exposure & Basin Entrapment Dimension (+Rainfall, +Congestion, +Flood Frequency vs -Elevation, -Slope, -River Distance).
* **PC2 (17.33% of variance):** Extreme Precipitation Gradient.
* **PC3 (15.64% of variance):** Topographic gradient.
* Cumulative variance of top 3 components: **81.53%**.
* 2D PCA Biplot and t-SNE scatterplots confirm crisp cluster separation.

---

## 6. Cluster Profile Interpretation

| Feature | High Relative Hazard Tier (n=47) | Moderate Relative Hazard Tier (n=32) | Relatively Lower Hazard Tier (n=21) |
| :--- | :--- | :--- | :--- |
| **Mean Elevation (AMSL)** | **13.11 m** | 24.72 m | **37.95 m** |
| **Mean Slope** | **0.91°** | 1.79° | **3.85°** |
| **Mean River Distance** | **6.75 km** | 6.14 km | **29.23 km** |
| **Mean Annual Rain** | **1,178.4 mm** | 1,032.3 mm | **1,023.3 mm** |
| **Max 24h Extreme Rain** | **290.9 mm** | 177.9 mm | **201.8 mm** |
| **Drainage Congestion (1-5)**| **3.53** | 3.25 | **1.67** |
| **Historical Floods (0-5)** | **3.38** | 3.44 | **1.43** |
| **Population Density** | **4,707 /km²** | 3,610 /km² | **4,279 /km²** |
| **Representative Settlements**| Ajit Singh Nagar, Payakapuram, Bhavanipuram, Tadepalle, Undavalli, Kollipara, Kollur, Avanigadda | Amaravati Heritage Town, Velagapudi, Thullur, Mangalagiri, Tenali, Chebrolu | Guntur Central (Brodipet), Arundelpet, Gorantla, Mylavaram, Jaggayyapeta |

---

## 7. Pan-India Multi-State Expansion & All 26 Districts of Andhra Pradesh

Following the core Vijayawada–Guntur study, the analytical framework was scaled nationally across **15 Indian States and Union Territories**, encompassing **92 Districts** and **229 authentic habitations**:
- **Andhra Pradesh (Complete 26-District Coverage):** All 26 post-bifurcation districts are catalogued with 163 settlements spanning river confluence cities, coastal delta reaches, floodway corridors, and upland plateaus (*Alluri Sitharama Raju, Anakapalli, Ananthapuramu, Annamayya, Bapatla, Chittoor, Dr. B.R. Ambedkar Konaseema, East Godavari, Eluru, Guntur, Kakinada, Krishna, Kurnool, Nandyal, NTR, Palnadu, Parvathipuram Manyam, Prakasam, Srikakulam, Sri Potti Sriramulu Nellore, Sri Sathya Sai, Tirupati, Visakhapatnam, Vizianagaram, West Godavari, YSR Kadapa*).
- **National Flood-Prone States:** Key river basin settlements across Assam (Brahmaputra), Bihar (Kosi & Ganga), Kerala (Periyar & Pamba), Odisha (Mahanadi), West Bengal (Hooghly & Sundarbans), Maharashtra (Krishna & Konkan), Uttar Pradesh (Ganga & Yamuna), Tamil Nadu (Adyar & Cauvery), Gujarat (Tapi & Narmada), Karnataka (Krishna & Netravati), Delhi (Yamuna), Punjab (Sutlej & Ghaggar), Uttarakhand, and Himachal Pradesh.

---

## 8. Real-Time Live Weather Integration & Dynamic Multi-Hazard Alert Engine

To bridge the gap between static unsupervised risk profiling and operational disaster readiness, a **Live Real-Time Meteorological Feed** was connected via the Open-Meteo High-Resolution Numerical Weather API (WMO-compliant):
1. **Live Observation Variables:** Ingests live ambient temperature (°C), apparent feels-like temperature (°C), relative humidity (%), active rainfall rate (mm/h), antecedent past 24-hour accumulated precipitation (mm), WMO weather code/icon, wind speed (km/h), and barometric surface pressure (hPa).
2. **Dynamic Alert Synthesis Engine:** Synthesizes the baseline unsupervised ML cluster hazard tier with active precipitation metrics:
   - 🚨 **RED ALERT (Critical Immediate Risk):** Baseline High Hazard Tier with Live 24h Rain ≥ 35 mm or Live Rain Rate ≥ 10 mm/h.
   - 🟧 **ORANGE ALERT (Elevated Risk):** Baseline High Hazard Tier with Live 24h Rain 15–35 mm, or Baseline Moderate Tier with Live 24h Rain ≥ 25 mm.
   - 🟨 **YELLOW WATCH (Precautionary Monitoring):** Baseline Moderate Tier with Live 24h Rain 8–25 mm, or Baseline High Tier with Live Rain 5–15 mm.
   - 🟢 **GREEN STATUS (Normal / Dry):** Optimal or dry meteorological conditions within safe drainage absorption limits.

---

## 9. Interactive GIS Dashboard Implementation

The Streamlit web dashboard (`http://localhost:8501`) provides an interactive interface featuring:
- **Hierarchical Navigation:** Seamless switching between Pan-India, 15 individual states, all districts, and 229 individual places.
- **Dedicated Real-Time Weather Station:** Live sensor metrics and dynamic alert badges for any chosen settlement or district centroid.
- **All Districts Matrix Tab:** Tabular and graphical ranking of all districts in the state by flood vulnerability, alongside a one-click multi-district live weather query button.
- **Interactive Folium Map:** Auto-zooming cartography, highlighted place pinpointing, and Krishna/Budameru waterway traces.
- **Multicriteria Radar Signatures & 2D PCA Biplots:** Real-time visual comparison of biophysical risk drivers.

---

## 10. Limitations & Ethical Considerations
1. **Static vs. Dynamic:** Our model uses static climatological and topographic averages. It does not model dynamic unsteady hydrodynamics (e.g. real-time dam gate opening hydrographs at Prakasam Barrage).
2. **Rainfall Resolution:** IMD 0.25° grid (~27 km) cannot detect micro-cloudbursts over a single municipal ward.
3. **Regulatory Prudence:** Unsupervised clusters MUST NOT be published as official government "Red Zones" or legally binding regulatory hazard lines. Premature labeling of habitations without administrative verification can cause property devaluation, public panic, and insurance distortions.

---

## 8. Conclusion & Future Directions
This project demonstrates that unsupervised machine learning—when coupled with genuine, traceable geospatial and hydrometeorological datasets—provides an objective, transparent, and mathematically defensible framework for grouping habitations based on multi-criteria flood hazard and vulnerability characteristics. In the Vijayawada-Guntur region, K-Means++ and K-Medoids (PAM) with Manhattan distance successfully delineate three distinct vulnerability regimes that closely reflect the real-world experiences of the 2005, 2009, and 2024 flood disasters.

Future research will couple this unsupervised screening pipeline with 2D hydrodynamic numerical models (such as HEC-RAS 2D or TUFLOW) and high-resolution Sentinel-1 Synthetic Aperture Radar (SAR) flood extent inundation masks to achieve dynamic, near-real-time early warning capabilities.
