# Pan-India Hazard-Based Red-Zone Identification for Vulnerable Habitations Using Clustering
### Project ID: SIH26191
**B.Tech 3rd-Year Data Science / Machine Learning Project**  
**Coverage:** Pan-India (15 States / UTs, 92 Districts, 229 Habitations) + Complete 26 Districts of Andhra Pradesh + Real-Time Live Weather & Dynamic Flood Alerts  
**Primary Hazard:** Floods (Krishna, Godavari, Brahmaputra, Ganga, Kosi, Mahanadi, Periyar, Tapi, Yamuna Basins)  
**Academic Year:** 2026  

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=shaikfouziya24/Hazard-Based-Red-Zone-Identification-Clustering&branch=main&mainModule=dashboard/app.py)

---

> ⚠️ **ACADEMIC & REGULATORY DISCLAIMER**  
> This system is an unsupervised machine learning research decision-support tool. Cluster designations (*"High Relative Hazard / Vulnerability"*, *"Moderate"*, and *"Relatively Lower Hazard"*) represent relative statistical grouping across multi-criteria environmental, topographic, and demographic indicators.  
> **Clustering alone does NOT constitute an official government disaster warning or statutory red-zone demarcation.**

---

## 1. Project Directory Structure
```
flood_redzone_clustering/
├── data/
│   ├── raw/
│   │   ├── Guntur_Vijayawada_Rainfall_Summary.csv   # IMD 0.25° 24-year daily rainfall summary
│   │   ├── imdweb_nbdLkllF.nc                       # Original IMD NetCDF daily gridded file (8,766 days)
│   │   └── habitations_raw.csv                      # 100 genuine AP habitations catalogued
│   └── processed/
│       ├── imd_grid_summary.csv                     # Long-term 24-yr IMD grid indicators
│       ├── vijayawada_guntur_habitations_features.csv # Unified AP master dataset (1 row per village)
│       ├── habitations_complete_analysis.csv        # AP dataset with cluster assignments & PCA
│       └── india_habitations_complete.csv           # Master Pan-India Multi-State Dataset (166 settlements)
├── scripts/
│   ├── build_pan_india_dataset.py                   # Compiles & clusters Pan-India multi-state data
│   ├── generate_pan_india_map.py                    # Generates standalone national HTML Folium map
│   ├── 03_enrich_and_integrate_gis.py               # Copernicus DEM API & Geodesic spatial joins
│   ├── 04_eda_and_preprocessing.py                  # Missing value audit, correlation & Z-score scaling
│   ├── 05_partition_clustering.py                   # K-Means++ and K-Medoids (PAM) with Manhattan L1
│   ├── 06_hierarchical_density_clustering.py        # Ward, Complete, Single linkages & DBSCAN
│   ├── 07_dimensionality_reduction.py               # PCA (explained variance, biplot) & t-SNE
│   ├── 08_cluster_profiling_and_radar.py            # Multi-criteria radar signatures & Folium HTML map
│   ├── build_and_execute_notebook.py                # Compiles & executes complete Jupyter Notebook
│   ├── generate_academic_report.py                  # Generates DOCX academic report
│   └── generate_presentation.py                     # Generates 12-slide PPTX presentation
├── notebooks/
│   └── Hazard_RedZone_Clustering_Analysis.ipynb     # Fully executed Jupyter Notebook with all outputs
├── dashboard/
│   └── app.py                                       # Interactive Pan-India Streamlit & Folium web dashboard
├── outputs/
│   ├── figures/                                     # 13 high-resolution figures & Folium HTML maps
│   │   ├── pan_india_flood_hazard_map.html          # Standalone Pan-India Interactive Folium Map
│   │   ├── vijayawada_guntur_flood_hazard_map.html  # High-density AP Folium Map
│   │   └── ... (01 to 12 analysis plots)
│   ├── tables/                                      # CSV evaluation tables & feature statistics
│   ├── reports/
│   │   ├── SIH26191_Final_Project_Report.docx       # Full academic project report (Word)
│   │   └── SIH26191_Final_Project_Report.md         # Full academic project report (Markdown)
│   └── presentation/
│       └── SIH26191_Project_Presentation.pptx       # 12-slide professional academic presentation
├── docs/
│   ├── DATA_SOURCE_REGISTER.md                      # Provenance, licenses, URLs, and coverage
│   ├── DATA_DICTIONARY.md                           # Schema, data types, units, and definitions
│   └── VIVA_QUESTIONS_ANSWERS.md                    # 20 comprehensive viva Q&A for faculty defense
├── requirements.txt
└── README.md
```

---

## 2. Quick-Start Guide: Running the Pan-India Dashboard

### Prerequisites
- Python 3.11 installed (available in `.venv` or system Python)
- Windows PowerShell

### Step 1: Open PowerShell and Navigate to Project Directory
```powershell
cd "C:\Users\Murthy\.gemini\antigravity\scratch\flood_redzone_clustering"
```

### Step 2: Activate the Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Launch the Interactive Web Dashboard
Run the Streamlit application:
```powershell
python -m streamlit run dashboard\app.py
```
Open your browser to: **http://localhost:8501**

---

## 3. How to Use State, District, and Real-Time Weather Features
1. **Multi-Level Geographic Navigation (Sidebar):**
   - **🇮🇳 1. Select State / Territory:** Choose from 15 Indian States or "All India (Pan-India Overview)".
   - **📍 2. Select District:** Dynamically cascades based on the selected state. For **Andhra Pradesh, all 26 official districts** are fully integrated:
     *(Alluri Sitharama Raju, Anakapalli, Ananthapuramu, Annamayya, Bapatla, Chittoor, Dr. B.R. Ambedkar Konaseema, East Godavari, Eluru, Guntur, Kakinada, Krishna, Kurnool, Nandyal, NTR, Palnadu, Parvathipuram Manyam, Prakasam, Srikakulam, Sri Potti Sriramulu Nellore, Sri Sathya Sai, Tirupati, Visakhapatnam, Vizianagaram, West Godavari, YSR Kadapa)*.
   - **🏘️ 3. Select Specific Place / Habitation:** Choose any individual settlement from the 229 catalogued places across India.
   - **⚠️ 4. Filter by Hazard Tier:** Filter by High, Moderate, or Relatively Lower Hazard tiers.

2. **⚡ Live Real-Time Weather & Dynamic Flood Alert Engine:**
   - **Live Meteorological Feed:** Directly connected to Open-Meteo High-Resolution Numerical Weather API.
   - **Real-Time Indicators:** Live ambient temperature (°C), feels-like (°C), relative humidity (%), active rain rate (mm/h), antecedent past 24-hour accumulated rainfall (mm), WMO weather code/icon, wind speed (km/h), and observation timestamp in IST.
   - **Dynamic Alert Synthesis:** Combines unsupervised ML baseline cluster hazard with active real-time rainfall:
     - 🚨 **RED ALERT (Critical Risk):** Baseline High Hazard + Live 24h Rain ≥ 35 mm or Live Rain Rate ≥ 10 mm/h.
     - 🟧 **ORANGE ALERT (Elevated Risk):** Baseline High Hazard + Live 24h Rain 15–35 mm, or Baseline Moderate + Live 24h Rain ≥ 25 mm.
     - 🟨 **YELLOW WATCH (Monitor):** Baseline Moderate + Live Rain 8–25 mm, or Baseline High + Live Rain 5–15 mm.
     - 🟢 **GREEN STATUS (Normal/Dry):** Baseline dry conditions within safe drainage thresholds.

3. **🏛️ Tab 2: All Districts in State Matrix:**
   - Displays all districts in the state ranked by High Hazard percentage.
   - Morphometry charts: Elevation vs Annual Rainfall.
   - **"📡 Query Live Weather for All Districts":** Queries live meteorological readings across all districts in the state simultaneously!

4. **🗺️ Tab 1: Interactive Geospatial Map:**
   - Auto-centers and zooms to state, district, or exact place.
   - Circle markers color-coded by hazard tier with full biophysical popups.
   - River courses rendered for Krishna River (Prakasam Barrage) and Budameru Floodway.

5. **📋 Tab 6: Data Explorer & Download:**
   - Full tabular view of all places.
   - 1-click CSV export for any state or district selection.
