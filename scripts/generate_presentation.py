import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

print("=== Generating 12-Slide Academic PPT Presentation ===")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette
COLOR_NAVY = RGBColor(30, 58, 138)       # Primary Header
COLOR_SLATE = RGBColor(71, 85, 105)      # Subtitle
COLOR_DARK = RGBColor(30, 41, 59)        # Body text
COLOR_RED = RGBColor(215, 48, 39)        # High hazard
COLOR_ORANGE = RGBColor(217, 119, 6)     # Moderate hazard
COLOR_BLUE = RGBColor(37, 99, 235)       # Lower hazard
COLOR_BG_CARD = RGBColor(241, 245, 249)  # Light gray card
COLOR_BORDER = RGBColor(203, 213, 225)

blank_layout = prs.slide_layouts[6]

def add_header(slide, title_text, category_text="SIH26191 | B.Tech Academic Project Presentation"):
    # Header container
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.name = 'Arial'
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_SLATE
    
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.name = 'Arial'
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY

# ----------------- SLIDE 1: TITLE SLIDE -----------------
slide1 = prs.slides.add_slide(blank_layout)

# Decorative background accent
bg_shape = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.4), Inches(7.5))
bg_shape.fill.solid()
bg_shape.fill.fore_color.rgb = COLOR_NAVY
bg_shape.line.color.rgb = COLOR_NAVY

tbox = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(3.8))
tf = tbox.text_frame
tf.word_wrap = True

p1 = tf.paragraphs[0]
p1.text = "HAZARD-BASED RED-ZONE IDENTIFICATION FOR VULNERABLE HABITATIONS USING CLUSTERING"
p1.font.name = 'Arial'
p1.font.size = Pt(28)
p1.font.bold = True
p1.font.color.rgb = COLOR_NAVY
p1.space_after = Pt(14)

p2 = tf.add_paragraph()
p2.text = "Project ID: SIH26191 | Study Area: Vijayawada–Guntur Region, Andhra Pradesh, India"
p2.font.name = 'Arial'
p2.font.size = Pt(16)
p2.font.color.rgb = COLOR_SLATE
p2.space_after = Pt(28)

p3 = tf.add_paragraph()
p3.text = "Student Presentation | B.Tech 3rd-Year Data Science & Machine Learning\nMentorship: Senior AI & GIS Research Lab | Academic Year 2026"
p3.font.name = 'Arial'
p3.font.size = Pt(13)
p3.font.bold = True
p3.font.color.rgb = COLOR_DARK

# ----------------- SLIDE 2: PROBLEM STATEMENT & MOTIVATION -----------------
slide2 = prs.slides.add_slide(blank_layout)
add_header(slide2, "1. Problem Statement & Regional Flood Motivation")

tb2 = slide2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf2 = tb2.text_frame
tf2.word_wrap = True

def add_bullet_slide(tf, title, body):
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = title + ": "
    p.font.name = 'Arial'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.space_after = Pt(8)
    
    run = p.add_run()
    run.text = body
    run.font.name = 'Arial'
    run.font.size = Pt(13)
    run.font.bold = False
    run.font.color.rgb = COLOR_DARK

add_bullet_slide(tf2, "The Reality of Recurrent Inundation", 
                 "The Vijayawada-Guntur capital region is severely prone to flash inundations and riverine surges. In September 2024, catastrophic overflows of the Budameru rivulet and 11.4 lakh cusecs discharge at Prakasam Barrage flooded over 32 wards and affected 600,000+ residents.")

add_bullet_slide(tf2, "Absence of Supervised Labels", 
                 "Disaster managers lack ground-truth damage labels for every small rural habitation or peri-urban colony. Traditional hydraulic models (HEC-RAS) require bathymetry that is unavailable across 100+ villages.")

add_bullet_slide(tf2, "Unsupervised Clustering Solution", 
                 "Unsupervised machine learning enables multi-criteria grouping of habitations based on genuine biophysical, topographic, and climatological feature profiles without subjective bias.")

add_bullet_slide(tf2, "Defensible Academic Boundary", 
                 "Crucial Principle: Clustering identifies relative statistical vulnerability groups. It does not replace statutory government disaster warnings or official red-zone declarations.")

# ----------------- SLIDE 3: OBJECTIVES & STUDY REGION -----------------
slide3 = prs.slides.add_slide(blank_layout)
add_header(slide3, "2. Study Area & Core Academic Objectives")

tb3 = slide3.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf3 = tb3.text_frame
tf3.word_wrap = True

add_bullet_slide(tf3, "Geographic Bounding", 
                 "Latitudes 15.75°N to 16.75°N, Longitudes 80.00°E to 81.25°E. Spans NTR (Vijayawada Urban/Rural), Guntur, and Krishna delta districts along the lower Krishna River.")

add_bullet_slide(tf3, "End-to-End Pipeline", 
                 "Independently collect authentic datasets, engineer spatial features, apply normalization, benchmark partition-based, hierarchical, and density-based clustering, and build an interactive GIS interface.")

add_bullet_slide(tf3, "Comparative Rigor", 
                 "Directly evaluate K-Means (Random vs K-Means++ across K=2,3,4,5), K-Medoids (PAM with Manhattan L1), Agglomerative Hierarchical (Ward, Complete, Average, Single), and DBSCAN.")

# ----------------- SLIDE 4: TRACEABLE DATA ENGINEERING -----------------
slide4 = prs.slides.add_slide(blank_layout)
add_header(slide4, "3. Traceable Real-World Datasets & Integration")

tb4 = slide4.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf4 = tb4.text_frame
tf4.word_wrap = True

add_bullet_slide(tf4, "IMD Pune 0.25° Daily Rainfall (2001–2024)", 
                 "24 years (8,766 daily timesteps) across 17 grid cells. Extracted: Mean Annual Rain, Monsoon Rain, Extreme 24h Rain, Rainy Days count, and CV.")

add_bullet_slide(tf4, "Copernicus DEM 90m / SRTM (Open-Meteo API)", 
                 "True surface elevations above MSL and topographic slopes for all 100 catalogued settlements.")

add_bullet_slide(tf4, "River Hydrography & Proximity", 
                 "Geodesic distance (km) computed to Krishna River course (Prakasam Barrage) and Budameru flood channel.")

add_bullet_slide(tf4, "IFI-Impacts & Census 2011", 
                 "IIT Delhi national flood inventory (Saharia et al., 2024) + Census population density and drainage congestion index.")

# ----------------- SLIDE 5: SYSTEM ARCHITECTURE -----------------
slide5 = prs.slides.add_slide(blank_layout)
add_header(slide5, "4. Methodological Architecture & Workflow")

tb5 = slide5.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf5 = tb5.text_frame
tf5.word_wrap = True

add_bullet_slide(tf5, "Phase 1: Spatial Join & Preprocessing", 
                 "100 Habitations matched to nearest IMD grid centroid. Outlier inspection, zero missing values, zero duplicates. Standardization via StandardScaler (Z-score normalization).")

add_bullet_slide(tf5, "Phase 2: Partition-Based Clustering", 
                 "K-Means (WCSS Elbow, Silhouette, Davies-Bouldin) and K-Medoids (PAM) with Manhattan L1 distance.")

add_bullet_slide(tf5, "Phase 3: Hierarchical & Density Clustering", 
                 "Agglomerative Clustering with Ward Linkage + Dendrogram; DBSCAN with 4-NN distance knee calibration.")

add_bullet_slide(tf5, "Phase 4: Dimensionality Reduction & GIS Deployment", 
                 "PCA (explained variance, biplot) and t-SNE; Interactive Streamlit & Folium web map dashboard.")

# ----------------- SLIDE 6: PARTITION-BASED CLUSTERING -----------------
slide6 = prs.slides.add_slide(blank_layout)
add_header(slide6, "5. Unit II: K-Means & K-Medoids (PAM) Benchmarking")

tb6 = slide6.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf6 = tb6.text_frame
tf6.word_wrap = True

add_bullet_slide(tf6, "K-Means++ Superiority", 
                 "K-Means++ consistently achieved lower inertia and higher silhouette scores than random initialization. Elbow curve demonstrates clear inflection at K=3 (WCSS = 420.44, Silhouette = 0.3667).")

add_bullet_slide(tf6, "K-Medoids with Manhattan (L1 / cityblock) Distance", 
                 "K-Medoids (PAM) achieved an optimal Silhouette Score of 0.4320 at K=3. Selected authentic exemplar medoid habitations: Munnangi, Gorantla, and Velagapudi.")

add_bullet_slide(tf6, "Important Note on Scikit-Learn K-Means", 
                 "Standard sklearn KMeans does NOT support Manhattan distance because Lloyd's algorithm computes mathematical cluster centroids (means) that minimize squared Euclidean distance.")

# ----------------- SLIDE 7: HIERARCHICAL CLUSTERING & DENDROGRAM -----------------
slide7 = prs.slides.add_slide(blank_layout)
add_header(slide7, "6. Unit III: Hierarchical Agglomerative Clustering")

tb7 = slide7.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf7 = tb7.text_frame
tf7.word_wrap = True

add_bullet_slide(tf7, "Linkage Comparison", 
                 "Ward's Linkage produced balanced, compact clusters (sizes: 47, 32, 21), perfectly corroborating the K-Means++ grouping. Complete, Average, and Single linkages suffered from chaining and singleton isolation.")

add_bullet_slide(tf7, "Ward Dendrogram Interpretation", 
                 "A horizontal cut at dissimilarity threshold 11.5 isolates the 3 primary risk branches corresponding to low-lying delta, river terrace, and elevated upland habitations.")

# ----------------- SLIDE 8: DENSITY-BASED CLUSTERING: DBSCAN -----------------
slide8 = prs.slides.add_slide(blank_layout)
add_header(slide8, "7. Unit III: Density-Based Clustering (DBSCAN)")

tb8 = slide8.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf8 = tb8.text_frame
tf8.word_wrap = True

add_bullet_slide(tf8, "Parameter Tuning via 4-NN Knee", 
                 "The sorted 4-nearest neighbor distance curve exhibits a sharp knee at epsilon = 1.85 (min_samples = 4).")

add_bullet_slide(tf8, "Noise Point Isolation (12 Habitations)", 
                 "DBSCAN successfully identified 12 noise points (-1). Unlike K-Means, DBSCAN isolates true demographic/topographic anomalies: extreme urban flood disaster nodes (Ajit Singh Nagar, Payakapuram, Bhavanipuram, Undavalli) and high-elevation hilltop habitations (Mylavaram, Jaggayyapeta).")

# ----------------- SLIDE 9: DIMENSIONALITY REDUCTION (PCA & t-SNE) -----------------
slide9 = prs.slides.add_slide(blank_layout)
add_header(slide9, "8. Unit IV: Dimensionality Reduction Analysis")

tb9 = slide9.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf9 = tb9.text_frame
tf9.word_wrap = True

add_bullet_slide(tf9, "PCA Explained Variance", 
                 "Top 3 components explain 81.53% of total dataset variance (PC1 = 48.56%, PC2 = 17.33%, PC3 = 15.64%).")

add_bullet_slide(tf9, "Physical Interpretation of PC1", 
                 "PC1 is fundamentally the 'Flood Exposure & Basin Entrapment Dimension' (+Annual Rain, +Monsoon Rain, +Drainage Congestion, +Flood Frequency vs -Elevation, -Slope, -River Distance).")

add_bullet_slide(tf9, "2D Projection Verification", 
                 "Both PCA and t-SNE scatterplots show distinct, non-overlapping cluster boundaries supporting the defensibility of the 3-tier grouping.")

# ----------------- SLIDE 10: CLUSTER RISK PROFILES -----------------
slide10 = prs.slides.add_slide(blank_layout)
add_header(slide10, "9. Quantitative Cluster Hazard & Vulnerability Profiles")

tb10 = slide10.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf10 = tb10.text_frame
tf10.word_wrap = True

add_bullet_slide(tf10, "🔴 High Relative Hazard / Vulnerability (n = 47)", 
                 "Elev: 13.1 m AMSL | Slope: 0.91° | River Dist: 6.75 km | Annual Rain: 1,178 mm | Max Daily Rain: 290.9 mm | Congestion: 3.53/5 | Flood Freq: 3.38/5. Includes Ajit Singh Nagar, Tadepalle, Undavalli, Kollipara, Kollur, Avanigadda.")

add_bullet_slide(tf10, "🟡 Moderate Relative Hazard / Vulnerability (n = 32)", 
                 "Elev: 24.7 m AMSL | Slope: 1.79° | River Dist: 6.14 km | Annual Rain: 1,032 mm | Max Daily Rain: 177.9 mm | Congestion: 3.25/5. Includes Amaravati Heritage Town, Velagapudi, Mangalagiri, Tenali.")

add_bullet_slide(tf10, "🔵 Relatively Lower Hazard / Vulnerability (n = 21)", 
                 "Elev: 38.0 m AMSL | Slope: 3.85° | River Dist: 29.23 km | Annual Rain: 1,023 mm | Congestion: 1.67/5 | Flood Freq: 1.43/5. Includes Guntur Central, Gorantla, Mylavaram, Jaggayyapeta.")

# ----------------- SLIDE 11: INTERACTIVE STREAMLIT DASHBOARD -----------------
slide11 = prs.slides.add_slide(blank_layout)
add_header(slide11, "10. Pan-India Dashboard, All 26 AP Districts & Real-Time Alerts")

tb11 = slide11.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf11 = tb11.text_frame
tf11.word_wrap = True

add_bullet_slide(tf11, "Multi-Level National Navigation & All 26 AP Districts", 
                 "Hierarchical state selector covering 15 States and 92 Districts (229 habitations). Includes all 26 official districts of Andhra Pradesh with authentic biophysical and demographic indicators.")

add_bullet_slide(tf11, "⚡ Live Real-Time Weather Integration (Open-Meteo)", 
                 "Queries real-time numerical weather feeds with 0 latency: live ambient temp (°C), humidity (%), live rain rate (mm/h), past 24h accumulated rainfall (mm), WMO weather code, and wind speed.")

add_bullet_slide(tf11, "🚨 Dynamic Multi-Hazard Alert Synthesis Engine", 
                 "Combines unsupervised ML baseline cluster tier with active 24h rainfall into actionable Red (Critical), Orange (Elevated), Yellow (Watch), and Green (Normal) alerts.")

add_bullet_slide(tf11, "Interactive Cartography & Multi-District Monitor", 
                 "Folium map with auto-zoom, selected place spotlight, Krishna/Budameru waterways, and a one-click multi-district real-time query table.")

# ----------------- SLIDE 12: CONCLUSION & DEFENSE SUMMARY -----------------
slide12 = prs.slides.add_slide(blank_layout)
add_header(slide12, "11. Conclusion, Limitations & Viva Defense Summary")

tb12 = slide12.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
tf12 = tb12.text_frame
tf12.word_wrap = True

add_bullet_slide(tf12, "Key Academic Takeaway", 
                 "Unsupervised learning objectively resolves habitations into distinct hazard regimes using genuine multi-source Indian geospatial datasets, validated by K-Means, K-Medoids, and Ward's Hierarchical clustering.")

add_bullet_slide(tf12, "Limitations Acknowledged", 
                 "IMD gridded rainfall (0.25°) is coarse for micro-ward cloudbursts; static clustering does not simulate real-time hydrodynamic dam breach waves.")

add_bullet_slide(tf12, "Defensible Stance for Faculty", 
                 "Clustering produces data-driven *relative vulnerability prioritization*, serving as an exploratory pre-screening tool for disaster managers rather than a legal warning.")

# Save presentation
ppt_path = "outputs/presentation/SIH26191_Project_Presentation.pptx"
prs.save(ppt_path)
print(f"Academic Presentation successfully generated and saved to {ppt_path}!")
