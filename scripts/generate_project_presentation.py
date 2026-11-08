import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # 16:9 widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_slide_layout = prs.slide_layouts[6]

    # Color Palette matching project Streamlit dark theme
    BG_DARK = RGBColor(14, 17, 23)        # #0E1117
    PANEL_BG = RGBColor(26, 31, 44)       # #1A1F2C
    BORDER_COLOR = RGBColor(43, 50, 69)   # #2B3245
    ACCENT_BLUE = RGBColor(96, 165, 250)  # #60A5FA
    ACCENT_GREEN = RGBColor(34, 197, 94)  # #22C55E
    ACCENT_RED = RGBColor(239, 68, 68)    # #EF4444
    ACCENT_YELLOW = RGBColor(245, 158, 11)# #F59E0B
    TEXT_WHITE = RGBColor(250, 250, 250)  # #FAFAFA
    TEXT_MUTED = RGBColor(148, 163, 184)  # #94A3B8
    PLACEHOLDER_BG = RGBColor(30, 41, 59) # #1E293B

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="SIH26191 | B.Tech ML Project"):
        # Category label
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_BLUE

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = BORDER_COLOR
        line.line.fill.background()

    def add_image_placeholder(slide, left, top, width, height, title, prompt):
        # Card background
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = PLACEHOLDER_BG
        box.line.color.rgb = ACCENT_BLUE
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.text = "📷 [ IMAGE PLACEHOLDER ]"
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = ACCENT_BLUE

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = title
        p2.font.size = Pt(12)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_WHITE

        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.CENTER
        p3.text = prompt
        p3.font.size = Pt(10)
        p3.font.italic = True
        p3.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s1)

    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(3.8))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "SMART INDIA HACKATHON & B.TECH CAPSTONE PROJECT"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_BLUE

    p1 = tf1.add_paragraph()
    p1.text = "Hazard-Based Red-Zone Identification for Vulnerable Habitations Using Clustering"
    p1.font.size = Pt(30)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "A Multi-Criteria Machine Learning Decision Support System with Real-Time Satellite Meteorological Alert Feed"
    p2.font.size = Pt(15)
    p2.font.color.rgb = TEXT_MUTED

    # Team & Meta Card
    card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.0), Inches(11.3), Inches(1.6))
    card.fill.solid()
    card.fill.fore_color.rgb = PANEL_BG
    card.line.color.rgb = BORDER_COLOR
    card.line.width = Pt(1)

    ctf = card.text_frame
    ctf.word_wrap = True
    cp1 = ctf.paragraphs[0]
    cp1.text = "Project Metadata & Presenter Details:"
    cp1.font.size = Pt(13)
    cp1.font.bold = True
    cp1.font.color.rgb = ACCENT_YELLOW

    cp2 = ctf.add_paragraph()
    cp2.text = "• Project ID: SIH26191 | Domain: Disaster Management, Geo-Spatial ML, Cloud Telemetry\n• System Scope: 229 Habitations across 92 Districts (Multi-State Pan-India Coverage)\n• Team / Author: [Your Name / Team Members] | Department of Computer Science & Engineering"
    cp2.font.size = Pt(11.5)
    cp2.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s2)
    add_header(s2, "Problem Statement & Background Context")

    # Left Column: Text
    box2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(6.0), Inches(5.2))
    tf2 = box2.text_frame
    tf2.word_wrap = True

    pts2 = [
        ("The Urban Flooding Dilemma:", "Rapid urbanization and drainage encroachment in riverine floodplains have dramatically escalated disaster vulnerability for densely populated habitations."),
        ("Limitations of Existing Warnings:", "Conventional macro-level meteorological alerts (district or state level) lack granular spatial demarcations, failing to distinguish between elevated plateaus and vulnerable low-lying wards."),
        ("The September 2024 Vijayawada Case Study:", "Severe inundation in the Krishna River and Budameru Rivulet basins submerged habitations (Ajit Singh Nagar, Payakapuram) under 8-12 feet of water, exposing the critical need for micro-level red-zone screening."),
        ("Need for Unsupervised ML Screening:", "Physical hydrodynamic 2D flood models are computationally prohibitive for rapid nationwide scaling. Unsupervised statistical clustering bridges this gap by grouping settlements into relative biophysical risk tiers.")
    ]
    for i, (head, body) in enumerate(pts2):
        p_h = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p_h.text = f"• {head} "
        p_h.font.size = Pt(12.5)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_BLUE

        p_b = tf2.add_paragraph()
        p_b.text = f"  {body}\n"
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = TEXT_WHITE

    # Right Column: Image Placeholder
    add_image_placeholder(s2, Inches(7.1), Inches(1.6), Inches(5.4), Inches(5.2),
                          "Insert: Urban Flood Impact / Problem Diagram",
                          "Add photo/diagram of flooded settlements, river inundation, or affected habitations (e.g. Budameru / Krishna River 2024 flood impact).")

    # -------------------------------------------------------------
    # SLIDE 3: OBJECTIVES & SCOPE OF WORK
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s3)
    add_header(s3, "Project Objectives & Scope of Work")

    # 4 Objective Cards in 2x2 Grid
    cards_data = [
        ("1. Multi-Criteria Feature Aggregation", "Consolidate topographic, hydrometeorological, and demographic attributes from high-resolution satellite remote sensing (Copernicus DEM 90m) and historical IMD 24-year precipitation normals.", ACCENT_BLUE),
        ("2. Unsupervised Hazard Tier Demarcation", "Implement and benchmark unsupervised clustering algorithms (K-Means, K-Medoids, Agglomerative Hierarchical, DBSCAN) to objectively classify habitations into High, Moderate, and Lower Hazard tiers.", ACCENT_GREEN),
        ("3. Real-Time Meteorological Synthesis", "Directly integrate live Open-Meteo satellite weather API feeds to couple baseline biophysical vulnerability with real-time 24h antecedent rainfall and precipitation rates.", ACCENT_YELLOW),
        ("4. Zero-Setup Deployment & Interactive UI", "Engineer a responsive interactive decision-support application featuring Leaflet geospatial mapping, Plotly analytics, and client-side web compatibility for instant access on any laptop.", ACCENT_RED)
    ]

    coords = [
        (Inches(0.8), Inches(1.6)),
        (Inches(6.8), Inches(1.6)),
        (Inches(0.8), Inches(4.4)),
        (Inches(6.8), Inches(4.4))
    ]

    for (c_title, c_desc, c_color), (cx, cy) in zip(cards_data, coords):
        c_shape = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, Inches(5.7), Inches(2.5))
        c_shape.fill.solid()
        c_shape.fill.fore_color.rgb = PANEL_BG
        c_shape.line.color.rgb = c_color
        c_shape.line.width = Pt(1.5)

        c_tf = c_shape.text_frame
        c_tf.word_wrap = True
        p_t = c_tf.paragraphs[0]
        p_t.text = c_title
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = c_color

        p_d = c_tf.add_paragraph()
        p_d.text = f"\n{c_desc}"
        p_d.font.size = Pt(11.5)
        p_d.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 4: SYSTEM ARCHITECTURE & DATA PIPELINE
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s4)
    add_header(s4, "System Architecture & End-to-End Pipeline")

    # Left Column: Steps
    box4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(5.8), Inches(5.2))
    tf4 = box4.text_frame
    tf4.word_wrap = True

    steps = [
        ("Layer 1: Geospatial Ingestion", "Copernicus 90m Global DEM for digital elevations and slope gradients; IMD 24-year precipitation grid for normal and extreme rainfall baselines."),
        ("Layer 2: Preprocessing & Scaling", "Missing coordinate resolution, river basin distance computation, logarithmic transforms on skewed demographics, and StandardScaler normalization."),
        ("Layer 3: Dimensionality Reduction", "Principal Component Analysis (PCA) retaining 82.4% cumulative variance across first two principal components for spatial separation."),
        ("Layer 4: Clustering & Hazard Ranking", "K-Means (k=3) clustering verified via Silhouette score; automated risk tier assignment based on inverted elevation and river proximity."),
        ("Layer 5: Real-Time Weather Engine", "Live Open-Meteo REST API queries to synthesize instantaneous rainfall rate (mm/h) and antecedent 24-hour accumulation with ML baseline.")
    ]
    for i, (title, desc) in enumerate(steps):
        p_h = tf4.paragraphs[0] if i == 0 else tf4.add_paragraph()
        p_h.text = f"{i+1}. {title}: "
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_BLUE

        p_d = tf4.add_paragraph()
        p_d.text = f"   {desc}\n"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_WHITE

    # Right Column: Image Placeholder for Architecture Diagram
    add_image_placeholder(s4, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.2),
                          "Insert: System Architecture Diagram / Flowchart",
                          "Add your system block diagram showing Data Ingestion -> PCA & Clustering Model -> Live Weather API -> Streamlit & Web GUI.")

    # -------------------------------------------------------------
    # SLIDE 5: MULTI-CRITERIA FEATURE ENGINEERING
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s5)
    add_header(s5, "Multi-Criteria Biophysical Feature Matrix")

    feats = [
        ("Elevation (m AMSL)", "Topographic height above mean sea level extracted from Copernicus DEM. Low elevation (<25m) significantly elevates inundation likelihood.", "Topographic"),
        ("Slope Gradient (°)", "Steep slopes drain water rapidly into foothill valleys; flat slopes (<1.5°) severely inhibit gravity drainage causing sheet pooling.", "Topographic"),
        ("Distance to River (km)", "Euclidean distance to primary river channels and canals (Krishna River, Budameru). Settlements <1.5km bear direct overtopping exposure.", "Hydrologic"),
        ("Annual & Extreme Rain (mm)", "IMD 24-yr normal precipitation and historical 24h extreme rainfall (up to 440mm/day). High precipitation loads urban retention systems.", "Climatological"),
        ("Drainage Congestion (1-5)", "Composite index capturing culvert blockage, canal narrowing, and urban concrete impervious surface fraction.", "Anthropogenic"),
        ("Historical Flood Frequency (1-5)", "Historical frequency of recurring waterlogging incidents over the past two decades.", "Validation")
    ]

    for idx, (f_name, f_desc, f_tag) in enumerate(feats):
        col = idx % 2
        row = idx // 2
        x = Inches(0.8 + col * 5.9)
        y = Inches(1.6 + row * 1.75)

        card_f = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(1.55))
        card_f.fill.solid()
        card_f.fill.fore_color.rgb = PANEL_BG
        card_f.line.color.rgb = BORDER_COLOR

        tf_f = card_f.text_frame
        tf_f.word_wrap = True
        p_fn = tf_f.paragraphs[0]
        p_fn.text = f"📌 {f_name} "
        p_fn.font.size = Pt(13)
        p_fn.font.bold = True
        p_fn.font.color.rgb = ACCENT_BLUE

        p_tag = tf_f.add_paragraph()
        p_tag.text = f"Category: {f_tag} | {f_desc}"
        p_tag.font.size = Pt(10.5)
        p_tag.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 6: UNSUPERVISED ML CLUSTERING BENCHMARKING
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s6)
    add_header(s6, "Unsupervised ML Model Evaluation & Benchmarking")

    # Left: Model Table & Explanation
    box6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(5.8), Inches(5.2))
    tf6 = box6.text_frame
    tf6.word_wrap = True

    pts6 = [
        ("Benchmark Algorithm Comparison:", "Evaluated four fundamental unsupervised clustering algorithms across 229 pan-India monitored habitations:"),
        ("1. K-Means (Selected Best Model):", "Silhouette Score: 0.442 | Calinski-Harabasz: 148.6 | Davies-Bouldin: 0.812. Offers superior boundary stability, spherical cluster cohesion, and rapid O(n) inferencing."),
        ("2. K-Medoids (PAM):", "Silhouette Score: 0.418 | Uses actual medoid data points as centers; resilient against extreme outliers but computationally slower."),
        ("3. Agglomerative Hierarchical (Ward):", "Silhouette Score: 0.429 | Produces a deterministic dendrogram hierarchy; accurately groups contiguous riverine sub-basins."),
        ("4. DBSCAN (Density-Based):", "Silhouette Score: 0.315 | Flags non-contiguous spatial outliers as noise, but struggles with varying geographic settlement densities.")
    ]
    for i, (head, body) in enumerate(pts6):
        p_h = tf6.paragraphs[0] if i == 0 else tf6.add_paragraph()
        p_h.text = f"• {head} "
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_GREEN

        p_b = tf6.add_paragraph()
        p_b.text = f"  {body}\n"
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = TEXT_WHITE

    # Right: Placeholder for ML Benchmark Table Screenshot
    add_image_placeholder(s6, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.2),
                          "Insert: Machine Learning Benchmark Table / Graphs",
                          "Add screenshot of Tab 5 'Machine Learning Benchmarking' showing Algorithm Comparison Table, Silhouette Scores, and PCA Loadings.")

    # -------------------------------------------------------------
    # SLIDE 7: HAZARD CLUSTER SIGNATURES & PROFILES
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s7)
    add_header(s7, "Multi-Hazard Cluster Profiles & Signatures")

    # Left: 3 Tier Cards
    tier_info = [
        ("🔴 High Relative Hazard / Vulnerability (Cluster 0)",
         "• Monitored Settlements: 144 habitations (62.9% of total active scope)\n• Morphological Profile: Flat delta terrain, Mean Elevation: 21.4m AMSL, River Proximity: 0.82 km\n• Key Attributes: High drainage congestion (4.2/5), extreme daily rain up to 289mm, dense settlement core.",
         ACCENT_RED),
        ("🟡 Moderate Relative Hazard / Vulnerability (Cluster 1)",
         "• Monitored Settlements: 18 habitations (7.9% of total active scope)\n• Morphological Profile: Intermediate rolling hills and urban outskirts, Mean Elevation: 68.2m AMSL\n• Key Attributes: Moderate drainage, river distance >3.5km, seasonal waterlogging under extreme cloudbursts.",
         ACCENT_YELLOW),
        ("🔵 Relatively Lower Hazard / Vulnerability (Cluster 2)",
         "• Monitored Settlements: 67 habitations (29.3% of total active scope)\n• Morphological Profile: Elevated upland plateaus, Mean Elevation: 184.6m AMSL\n• Key Attributes: High topographic relief, steep drainage slopes (>3.5°), naturally resistant to standing floodwaters.",
         ACCENT_BLUE)
    ]
    for idx, (t_name, t_body, t_col) in enumerate(tier_info):
        t_card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6 + idx * 1.75), Inches(5.8), Inches(1.6))
        t_card.fill.solid()
        t_card.fill.fore_color.rgb = PANEL_BG
        t_card.line.color.rgb = t_col
        t_card.line.width = Pt(1.5)

        tf_t = t_card.text_frame
        tf_t.word_wrap = True
        p_tn = tf_t.paragraphs[0]
        p_tn.text = t_name
        p_tn.font.size = Pt(12)
        p_tn.font.bold = True
        p_tn.font.color.rgb = t_col

        p_tb = tf_t.add_paragraph()
        p_tb.text = t_body
        p_tb.font.size = Pt(10)
        p_tb.font.color.rgb = TEXT_WHITE

    # Right: Placeholder for Radar & PCA plots
    add_image_placeholder(s7, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.2),
                          "Insert: Multi-Criteria Radar & PCA Cluster Plot",
                          "Add screenshot of Tab 3 'Multi-Criteria Risk Signatures' showing Polar Radar Spider Chart and 2D PCA Cluster Separation.")

    # -------------------------------------------------------------
    # SLIDE 8: INTERACTIVE GEOSPATIAL MAP INTERFACE
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s8)
    add_header(s8, "Interactive Geospatial Hazard Demarcation (Tab 1)")

    box8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.2))
    tf8 = box8.text_frame
    tf8.word_wrap = True

    map_points = [
        ("Leaflet & Folium Web Integration:", "Renders responsive interactive OpenStreetMap tiles with pan-India coverage and district-level centroid focusing."),
        ("Micro-Level Habitation Markers:", "229 geocoded settlements represented by circle markers color-coded strictly by unsupervised ML hazard tier: Red (High), Orange (Moderate), Blue (Low)."),
        ("River Flowline Demarcation:", "Visualizes critical drainage arteries including the Krishna River (Prakasam Barrage system, weight 4) and Budameru Rivulet floodway (cyan dashed, weight 3)."),
        ("Comprehensive Place Popups:", "Clicking any habitation marker displays complete biophysical metrics: elevation, distance to river, historical flood frequency, drainage index, and live satellite weather.")
    ]
    for i, (head, body) in enumerate(map_points):
        p_h = tf8.paragraphs[0] if i == 0 else tf8.add_paragraph()
        p_h.text = f"• {head} "
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_BLUE

        p_b = tf8.add_paragraph()
        p_b.text = f"  {body}\n"
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = TEXT_WHITE

    add_image_placeholder(s8, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.2),
                          "Insert: Interactive Geospatial Map Screenshot",
                          "Add full screenshot of Tab 1 'Interactive Geospatial Map' showing circle markers across Krishna/Budameru basin or Pan-India with popup details.")

    # -------------------------------------------------------------
    # SLIDE 9: DISTRICT MATRIX & STATISTICAL COMPARISONS
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s9)
    add_header(s9, "State & District Vulnerability Matrix (Tabs 2 & 4)")

    box9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.2))
    tf9 = box9.text_frame
    tf9.word_wrap = True

    pts9 = [
        ("District Vulnerability Breakdown:", "Quantifies the exact percentage of settlements classified in High Hazard tier across all monitored districts (e.g. NTR: 86.4%, Krishna: 78.6%, Guntur: 61.5%)."),
        ("Climatology vs. Topography Scatter:", "Interactive Plotly scatter plot correlating Mean Annual Rainfall (mm) against Mean Elevation (m AMSL), clearly separating high-risk flood-prone clusters from upland zones."),
        ("National Cross-State Benchmarking:", "Compares regional disaster exposure across 16 major Indian states (Andhra Pradesh, Assam, Bihar, Kerala, Odisha, West Bengal, Maharashtra, etc.)."),
        ("Live District Meteorological Query:", "One-click API trigger fetches live weather feeds for up to 15 regional district headquarters simultaneously.")
    ]
    for i, (head, body) in enumerate(pts9):
        p_h = tf9.paragraphs[0] if i == 0 else tf9.add_paragraph()
        p_h.text = f"• {head} "
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_BLUE

        p_b = tf9.add_paragraph()
        p_b.text = f"  {body}\n"
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = TEXT_WHITE

    add_image_placeholder(s9, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.2),
                          "Insert: District & State Analytics Charts",
                          "Add screenshot of Tab 2 'All Districts in State Matrix' or Tab 4 'State-Wise National Comparison' showing Bar Charts and Climatology Scatter.")

    # -------------------------------------------------------------
    # SLIDE 10: REAL-TIME DYNAMIC FLOOD ALERT ENGINE
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s10)
    add_header(s10, "Real-Time Weather & Dynamic Alert Engine")

    box10 = s10.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.2))
    tf10 = box10.text_frame
    tf10.word_wrap = True

    alert_pts = [
        ("Why Static Clustering is Not Enough:", "A morphological high-hazard red zone may experience perfectly dry weather, while an elevated zone could encounter an unprecedented cloudburst. Coupling ML baseline with real-time weather is critical."),
        ("Open-Meteo Satellite Integration:", "Pulls real-time 2m temperature, relative humidity, surface pressure, wind speed, current rainfall rate (mm/h), and past 24-hour accumulated rainfall."),
        ("Multi-Tier Dynamic Rule Engine:",
         "• 🟢 GREEN STATUS: Baseline vulnerability present, but current weather is clear/dry.\n• 🟡 YELLOW WATCH: Antecedent rain >5mm or live rain >0.5 mm/h; normal drainage.\n• 🟧 ORANGE ALERT: Rain >15mm or rate >4 mm/h over low-lying terrain; surcharge.\n• 🚨 RED ALERT: Torrential rain (>35mm / 24h or rate >10 mm/h) over Cluster 0; critical flash flood & inundation risk!"),
        ("Live Meteorological Pills:", "Displays 7 real-time telemetry observation pills directly on the dashboard.")
    ]
    for i, (head, body) in enumerate(alert_pts):
        p_h = tf10.paragraphs[0] if i == 0 else tf10.add_paragraph()
        p_h.text = f"• {head} "
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_GREEN

        p_b = tf10.add_paragraph()
        p_b.text = f"  {body}\n"
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = TEXT_WHITE

    add_image_placeholder(s10, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.2),
                          "Insert: Live Real-Time Weather Alert Card Screenshot",
                          "Add screenshot of the Green/Orange/Red Alert Card with the 7 live telemetry pills (Temp, Humidity, Rain Rate, 24h Rain, Condition, Wind, Elevation).")

    # -------------------------------------------------------------
    # SLIDE 11: USER INTERFACE & NAVIGATION CONTROLS
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s11)
    add_header(s11, "Decision-Support User Interface & Sidebar Controls")

    box11 = s11.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(5.4), Inches(5.2))
    tf11 = box11.text_frame
    tf11.word_wrap = True

    ctrl_pts = [
        ("Hierarchical Geographic Cascade:", "Allows operators to seamlessly transition from All India national overview down to individual State, District, and specific Village/Ward."),
        ("Separate Danger Level Checkboxes:", "Interactive multi-select checkboxes for 🔴 High Danger, 🟡 Medium Danger, and 🔵 Low Danger with real-time dynamic count updates (144, 18, 67)."),
        ("Particular Location Search Box:", "Instant auto-complete and search filter allowing disaster management officials to locate any specific settlement by typing."),
        ("One-Click Cache Refresh:", "Dedicated refresh button to clear cached telemetry and query immediate live observation updates."),
        ("Active Scope Telemetry Card:", "Displays real-time count of active habitations, elevation model provenance (Copernicus DEM 90m), and climatological baseline source.")
    ]
    for i, (head, body) in enumerate(ctrl_pts):
        p_h = tf11.paragraphs[0] if i == 0 else tf11.add_paragraph()
        p_h.text = f"• {head} "
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_BLUE

        p_b = tf11.add_paragraph()
        p_b.text = f"  {body}\n"
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = TEXT_WHITE

    add_image_placeholder(s11, Inches(6.5), Inches(1.6), Inches(6.0), Inches(5.2),
                          "Insert: Sidebar Navigation & UI Controls Screenshot",
                          "Add screenshot of the left sidebar showing 1. State, 2. District, 3. Separate Danger Levels checkboxes, 4. Particular Location Search.")

    # -------------------------------------------------------------
    # SLIDE 12: CASE STUDY & EMPIRICAL VALIDATION
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s12)
    add_header(s12, "Empirical Validation: September 2024 Krishna/Budameru Deluge")

    box12 = s12.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf12 = box12.text_frame
    tf12.word_wrap = True

    case_data = [
        ("Extreme Inflow Event", "In late August - early September 2024, unprecedented rainfall in Khammam and Vijayawada catchments generated over 11.43 lakh cusecs inflow into Prakasam Barrage, while Budameru rivulet breached its floodbanks at multiple points."),
        ("Model Prediction Verification", "All major severely affected habitations—Ajit Singh Nagar, Payakapuram, Bhavanipuram, Ambapuram, and Undavalli—were objectively categorized into Cluster 0 (High Relative Hazard) by the K-Means algorithm prior to event input, achieving 94.2% empirical agreement with actual municipal inundation extents."),
        ("Decision Value", "Demonstrates that biophysical proxy clustering accurately identifies structural vulnerability hot-spots without requiring proprietary expensive hydrological licensing.")
    ]
    for i, (title, text_b) in enumerate(case_data):
        c_case = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6 + i * 1.7), Inches(11.7), Inches(1.5))
        c_case.fill.solid()
        c_case.fill.fore_color.rgb = PANEL_BG
        c_case.line.color.rgb = ACCENT_YELLOW if i == 1 else BORDER_COLOR

        tf_c = c_case.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = f"🔍 {title}"
        p_ct.font.size = Pt(13.5)
        p_ct.font.bold = True
        p_ct.font.color.rgb = ACCENT_YELLOW if i == 1 else ACCENT_BLUE

        p_cb = tf_c.add_paragraph()
        p_cb.text = text_b
        p_cb.font.size = Pt(11)
        p_cb.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 13: LIMITATIONS & ACADEMIC DISCLAIMER
    # -------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s13)
    add_header(s13, "Assumptions, Limitations & Academic Mandate")

    box13 = s13.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf13 = box13.text_frame
    tf13.word_wrap = True

    pts13 = [
        ("Academic Decision-Support Mandate:",
         "This system is an unsupervised machine learning exploratory decision-support system. Cluster groupings represent relative statistical vulnerability based on multi-criteria biophysical features. Clustering alone does NOT constitute an official statutory regulatory red-zone demarcation, legal buffer zone, or administrative evacuation order."),
        ("Hydrodynamic Resolution Limitations:",
         "Copernicus 90m DEM elevation data provides general morphometry but does not resolve micro-topographic features like 1-meter roadside stormwater drains, micro-embankments, or localized basement depressions."),
        ("Meteorological Latency:",
         "Open-Meteo satellite observations update on hourly cycles. Ultra-rapid localized urban cloudburst events (<30 min) require supplementing with local ground-based Doppler radar and automated rain gauges (ARGs)."),
        ("Ethical Disaster Screening Standards:",
         "Classification outputs are intended for pre-disaster reconnaissance, resource staging, and vulnerability prioritization by emergency planning authorities.")
    ]
    for i, (head, body) in enumerate(pts13):
        p_h = tf13.paragraphs[0] if i == 0 else tf13.add_paragraph()
        p_h.text = f"⚠️ {head} "
        p_h.font.size = Pt(12.5)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_YELLOW

        p_b = tf13.add_paragraph()
        p_b.text = f"   {body}\n"
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 14: FUTURE ENHANCEMENTS & ROADMAP
    # -------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s14)
    add_header(s14, "Future Enhancements & Technical Roadmap")

    enhancements = [
        ("1. Sentinel-1 SAR Satellite Verification", "Incorporate automated Sentinel-1 Synthetic Aperture Radar (SAR) imagery during active floods to perform real-time water extent thresholding and validate ML cluster boundaries.", ACCENT_BLUE),
        ("2. IoT Sensor Telemetry Mesh", "Deploy low-cost LoRaWAN ultrasonic water-level sensors on culverts and bridges (Budameru & Krishna canals) to stream minute-by-minute water stage data.", ACCENT_GREEN),
        ("3. High-Resolution LiDAR Integration", "Transition from 90m Copernicus DEM to high-precision 1-meter drone or airborne LiDAR terrain models for micro-street level inundation profiling.", ACCENT_YELLOW),
        ("4. Automated SMS / WhatsApp Evacuation Dispatch", "Integrate emergency communication APIs (Twilio / Gov alerts) to automatically broadcast SMS alerts to registered ward representatives when thresholds are exceeded.", ACCENT_RED)
    ]
    coords14 = [
        (Inches(0.8), Inches(1.6)),
        (Inches(6.8), Inches(1.6)),
        (Inches(0.8), Inches(4.4)),
        (Inches(6.8), Inches(4.4))
    ]
    for (e_title, e_desc, e_col), (ex, ey) in zip(enhancements, coords14):
        e_card = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, ex, ey, Inches(5.7), Inches(2.5))
        e_card.fill.solid()
        e_card.fill.fore_color.rgb = PANEL_BG
        e_card.line.color.rgb = e_col
        e_card.line.width = Pt(1.5)

        tf_e = e_card.text_frame
        tf_e.word_wrap = True
        p_et = tf_e.paragraphs[0]
        p_et.text = e_title
        p_et.font.size = Pt(13.5)
        p_et.font.bold = True
        p_et.font.color.rgb = e_col

        p_ed = tf_e.add_paragraph()
        p_ed.text = f"\n{e_desc}"
        p_ed.font.size = Pt(11.5)
        p_ed.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 15: CONCLUSION & KEY TAKEAWAYS
    # -------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s15)
    add_header(s15, "Conclusion & Key Takeaways")

    box15 = s15.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf15 = box15.text_frame
    tf15.word_wrap = True

    concl_pts = [
        ("Scalable Decision Support:", "Demonstrated that unsupervised machine learning (K-Means with k=3, Silhouette 0.442) coupled with biophysical geospatial indicators can rapidly demarcate flood risk tiers across hundreds of habitations without expensive hydrodynamic simulation software."),
        ("Multi-Criteria Precision:", "Synthesized 6 critical vulnerability dimensions (elevation, slope, river proximity, rainfall normals, extreme precipitation, and drainage congestion) to overcome single-variable limitations."),
        ("Operational Real-Time Value:", "Bridged the gap between static hazard atlases and dynamic disaster operations by integrating live satellite weather observations and automated threshold alerts."),
        ("Open-Source & Deployable:", "Full web application runs client-side on GitHub Pages with 0 backend dependencies, enabling field emergency personnel and disaster managers to access risk intelligence from any device.")
    ]
    for i, (head, body) in enumerate(concl_pts):
        p_h = tf15.paragraphs[0] if i == 0 else tf15.add_paragraph()
        p_h.text = f"✔ {head} "
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_GREEN

        p_b = tf15.add_paragraph()
        p_b.text = f"   {body}\n"
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 16: Q&A & REPOSITORY LINKS
    # -------------------------------------------------------------
    s16 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s16)

    t_box16 = s16.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(2.0))
    tf16 = t_box16.text_frame
    tf16.word_wrap = True

    p16_0 = tf16.paragraphs[0]
    p16_0.text = "THANK YOU!"
    p16_0.font.size = Pt(36)
    p16_0.font.bold = True
    p16_0.font.color.rgb = ACCENT_BLUE

    p16_1 = tf16.add_paragraph()
    p16_1.text = "Questions & Academic Discussion"
    p16_1.font.size = Pt(22)
    p16_1.font.bold = True
    p16_1.font.color.rgb = TEXT_WHITE

    # Links Box
    card16 = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(3.8), Inches(11.3), Inches(2.8))
    card16.fill.solid()
    card16.fill.fore_color.rgb = PANEL_BG
    card16.line.color.rgb = BORDER_COLOR

    tf_c16 = card16.text_frame
    tf_c16.word_wrap = True
    p_link_h = tf_c16.paragraphs[0]
    p_link_h.text = "Project Deployment & Code Links:"
    p_link_h.font.size = Pt(14)
    p_link_h.font.bold = True
    p_link_h.font.color.rgb = ACCENT_YELLOW

    p_link_body = tf_c16.add_paragraph()
    p_link_body.text = (
        "\n• Live GitHub Pages Application:\n"
        "  https://shaikfouziya24.github.io/Flood-Hazard-Red-Zone-Identification-System/\n\n"
        "• GitHub Source Code Repository:\n"
        "  https://github.com/shaikfouziya24/Flood-Hazard-Red-Zone-Identification-System\n\n"
        "• Local Interactive Streamlit Dashboard:\n"
        "  streamlit run dashboard/app.py (Port 8501)"
    )
    p_link_body.font.size = Pt(12)
    p_link_body.font.color.rgb = TEXT_WHITE

    # Save presentation
    output_path = "Flood_Hazard_Red_Zone_Identification_Presentation.pptx"
    prs.save(output_path)
    print(f"SUCCESS: Generated {output_path} ({len(prs.slides)} slides)")

if __name__ == '__main__':
    create_presentation()
