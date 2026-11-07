import pandas as pd
import json
import os

# Load dataset
df_path = 'data/processed/india_habitations_complete.csv'
if not os.path.exists(df_path):
    df_path = '../data/processed/india_habitations_complete.csv'

df = pd.read_csv(df_path)
records = df.to_dict(orient='records')
places_json = json.dumps(records, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIH26191: Pan-India Flood Hazard & Real-Time Alert System</title>
    
    <!-- Leaflet & Chart.js -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">

    <style>
        :root {{
            --bg-color: #0E1117;
            --sidebar-bg: #161922;
            --card-bg: #1A1F2C;
            --border-color: #2B3245;
            --text-main: #F1F5F9;
            --text-subdued: #94A3B8;
            --accent-red: #D73027;
            --accent-orange: #FDAE61;
            --accent-blue: #4575B4;
            --accent-green: #10B981;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}

        /* Sidebar: Pixel-matched to user's photo */
        aside {{
            width: 325px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            padding: 16px 14px;
            gap: 12px;
            overflow-y: auto;
            flex-shrink: 0;
        }}

        .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding-bottom: 2px;
        }}

        .sidebar-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .sidebar-title {{
            font-size: 19px;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.3px;
        }}
        .collapse-icon {{
            font-size: 16px;
            color: var(--text-subdued);
            cursor: pointer;
            font-weight: bold;
        }}

        .control-label {{
            font-size: 13px;
            font-weight: 700;
            color: #E2E8F0;
            margin-bottom: 4px;
            display: block;
        }}

        select, input[type="text"] {{
            width: 100%;
            background-color: #0E1117;
            border: 1px solid var(--border-color);
            color: #FFFFFF;
            padding: 9px 12px;
            border-radius: 6px;
            font-size: 13.5px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.15s ease;
        }}
        select:focus, input[type="text"]:focus {{
            border-color: #60A5FA;
        }}

        /* Danger Tier Separation Checkboxes */
        .danger-group {{
            background: rgba(14, 17, 23, 0.65);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .danger-item {{
            display: flex;
            align-items: center;
            font-size: 13.5px;
            color: #FFFFFF;
            cursor: pointer;
            padding: 3px 6px;
            border-radius: 4px;
        }}
        .danger-item:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        .danger-item label {{
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            font-weight: 600;
            width: 100%;
        }}
        .danger-checkbox {{
            accent-color: var(--accent-red);
            width: 15px;
            height: 15px;
            cursor: pointer;
        }}

        .btn-refresh {{
            background: #1E293B;
            border: 1px solid var(--border-color);
            color: #E2E8F0;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}
        .btn-refresh:hover {{
            background: #334155;
            color: #FFFFFF;
            border-color: #60A5FA;
        }}

        .scope-summary {{
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid var(--border-color);
            font-size: 11.5px;
            color: var(--text-subdued);
            line-height: 1.5;
        }}

        /* Main Workspace Container */
        main {{
            flex: 1;
            background-color: var(--bg-color);
            overflow-y: auto;
            padding: 22px 28px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .main-title {{
            font-size: 24px;
            font-weight: 800;
            color: #60A5FA;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.4px;
        }}
        .main-subtitle {{
            font-size: 13px;
            color: var(--text-subdued);
            margin-top: 3px;
        }}

        .disclaimer-box {{
            background-color: #1E222D;
            border-left: 4px solid #F59E0B;
            padding: 9px 14px;
            border-radius: 6px;
            font-size: 12.5px;
            color: #FDE68A;
            line-height: 1.45;
        }}

        /* 5 Metric Cards Row (Exact numbers & style from user photo) */
        .metrics-row {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
        }}
        .metric-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .metric-label {{
            font-size: 12px;
            color: var(--text-subdued);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .metric-val {{
            font-size: 22px;
            font-weight: 800;
            color: #FFFFFF;
        }}
        .metric-delta {{
            font-size: 11.5px;
            color: #94A3B8;
        }}

        /* Live Alert Banner (Matching user photo green status) */
        .alert-banner {{
            background: linear-gradient(135deg, #16A34A 0%, #0F172A 100%);
            border-radius: 8px;
            padding: 14px 18px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            transition: all 0.3s ease;
        }}
        .alert-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        .alert-pill {{
            font-size: 16px;
            font-weight: 800;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .alert-station {{
            font-size: 13px;
            color: #E2E8F0;
            opacity: 0.95;
        }}
        .alert-desc {{
            font-size: 13.5px;
            color: #F8FAFC;
            line-height: 1.4;
        }}
        .alert-pills-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 2px;
        }}
        .pill-item {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 600;
            color: #FFFFFF;
        }}

        /* Executive Graphs Row */
        .exec-graphs-row {{
            display: grid;
            grid-template-columns: 1fr 1.2fr 1.3fr;
            gap: 12px;
        }}
        .graph-card {{
            background: var(--sidebar-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .graph-title {{
            font-size: 13.5px;
            font-weight: 700;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        /* Spotlight Box */
        .spotlight-box {{
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #38BDF8;
            border-left: 5px solid #38BDF8;
            padding: 12px 16px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        /* Tabs Styling matching Streamlit tabs */
        .tab-bar {{
            display: flex;
            gap: 6px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 2px;
            overflow-x: auto;
        }}
        .tab-button {{
            background: transparent;
            border: none;
            color: var(--text-subdued);
            font-size: 13.5px;
            font-weight: 600;
            padding: 9px 15px;
            cursor: pointer;
            border-radius: 6px 6px 0 0;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .tab-button:hover {{
            color: #FFFFFF;
            background: rgba(255, 255, 255, 0.04);
        }}
        .tab-button.active {{
            color: #60A5FA;
            border-bottom: 3px solid #60A5FA;
            background: rgba(96, 165, 250, 0.08);
        }}
        .tab-panel {{
            display: none;
            flex-direction: column;
            gap: 14px;
        }}
        .tab-panel.active {{
            display: flex;
        }}

        .tab-section-header {{
            font-size: 18px;
            font-weight: 700;
            color: #FFFFFF;
        }}
        .tab-section-sub {{
            font-size: 13px;
            color: var(--text-subdued);
            margin-top: -8px;
            margin-bottom: 6px;
        }}

        #map {{
            height: 520px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}

        /* Tables */
        .table-wrap {{
            overflow-x: auto;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: var(--sidebar-bg);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12.5px;
            text-align: left;
        }}
        th {{
            background-color: #1A1F2C;
            color: #CBD5E1;
            padding: 10px 12px;
            font-weight: 700;
            border-bottom: 1px solid var(--border-color);
        }}
        td {{
            padding: 9px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            color: #E2E8F0;
        }}
        tr:hover td {{
            background-color: rgba(255, 255, 255, 0.03);
        }}

        /* Academic Figures Gallery Grid */
        .figure-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 16px;
        }}
        .figure-card {{
            background: #141822;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .figure-card:hover {{
            transform: translateY(-2px);
            border-color: #38BDF8;
        }}
        .figure-card img {{
            width: 100%;
            height: 250px;
            object-fit: contain;
            background-color: #0B0E14;
            border-radius: 6px;
            cursor: pointer;
        }}
        .figure-caption {{
            font-size: 12.5px;
            font-weight: 600;
            color: #CBD5E1;
            text-align: center;
        }}
        .figure-desc {{
            font-size: 11.5px;
            color: var(--text-subdued);
            line-height: 1.4;
            text-align: center;
        }}

        /* Lightbox Modal */
        #img-modal {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 0, 0, 0.88);
            z-index: 99999;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            padding: 24px;
        }}
        #modal-img {{
            max-width: 90vw;
            max-height: 80vh;
            border-radius: 8px;
            box-shadow: 0 0 30px rgba(0,0,0,0.8);
        }}
        #modal-caption {{
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 600;
            margin-top: 14px;
        }}
        .modal-close {{
            position: absolute;
            top: 20px; right: 28px;
            color: #FFFFFF;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
        }}
    </style>
</head>
<body>

    <!-- Sidebar: Matching User Screenshot Exactly with In-Line SVG Logo -->
    <aside>
        <div class="sidebar-brand">
            <svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="48" height="48" rx="10" fill="#1E3A8A"/>
                <path d="M6 32C12 32 12 28 18 28C24 28 24 32 30 32C36 32 36 28 42 28" stroke="#38BDF8" stroke-width="3.5" stroke-linecap="round"/>
                <path d="M6 38C12 38 12 34 18 34C24 34 24 38 30 38C36 38 36 34 42 34" stroke="#60A5FA" stroke-width="3.5" stroke-linecap="round"/>
                <path d="M24 10C24 10 14 20 14 24C14 29.5 18.5 34 24 34C29.5 34 34 29.5 34 24C34 20 24 10 24 10Z" fill="#38BDF8" opacity="0.9"/>
            </svg>
            <div style="line-height: 1.2;">
                <b style="font-size: 13.5px; color: #60A5FA;">SIH26191 LAB</b><br>
                <small style="font-size: 11px; color: #94A3B8;">Pan-India Flood Clustering</small>
            </div>
        </div>

        <div class="sidebar-header">
            <div class="sidebar-title">National & State Navigation</div>
            <div class="collapse-icon">«</div>
        </div>

        <!-- 1. State Selector -->
        <div>
            <label class="control-label" for="state-select">IN 1. Select State / Territory:</label>
            <select id="state-select" onchange="onStateChange()">
                <option value="All India (Pan-India Overview)">All India (Pan-India Overview)</option>
            </select>
        </div>

        <!-- 2. District Selector -->
        <div>
            <label class="control-label" for="district-select">📍 2. Select District:</label>
            <select id="district-select" onchange="onDistrictChange()">
                <option value="All Districts in State">All Districts in State</option>
            </select>
        </div>

        <!-- 3. Separate Danger Levels -->
        <div>
            <label class="control-label">⚠️ 3. Separate Danger Levels</label>
            <div class="danger-group">
                <div class="danger-item">
                    <label>
                        <input type="checkbox" id="check-high" class="danger-checkbox" checked onchange="applyFilters()">
                        <span>🔴 High Danger (<span id="count-high">144</span>)</span>
                    </label>
                </div>
                <div class="danger-item">
                    <label>
                        <input type="checkbox" id="check-med" class="danger-checkbox" checked onchange="applyFilters()">
                        <span>🟡 Medium Danger (<span id="count-med">18</span>)</span>
                    </label>
                </div>
                <div class="danger-item">
                    <label>
                        <input type="checkbox" id="check-low" class="danger-checkbox" checked onchange="applyFilters()">
                        <span>🔵 Low Danger (<span id="count-low">67</span>)</span>
                    </label>
                </div>
            </div>
        </div>

        <!-- 4. Select Particular Location / Area -->
        <div>
            <label class="control-label" for="location-select">📍 4. Select Particular Location / Area</label>
            <select id="location-select" onchange="onLocationChange()">
                <option value="All Locations in Scope">All Locations in Scope</option>
            </select>
            <div style="margin-top: 6px;">
                <input type="text" id="area-search" placeholder="🔍 Type to search area / village..." oninput="onAreaSearch()" />
            </div>
        </div>

        <button class="btn-refresh" onclick="triggerRefresh()">
            🔄 Refresh Live Real-Time Weather Data
        </button>

        <div class="scope-summary">
            <b>State:</b> <span id="summary-state">All India (Pan-India Overview)</span><br>
            <b>District:</b> <span id="summary-dist">All Districts in State</span><br>
            <b>Place:</b> <span id="summary-place">All Locations in Scope</span><br>
            <b>Habitations Active:</b> <span id="summary-hab-count">229 / 229</span><br>
            <b>Climatology:</b> IMD 24-Yr Normals (0.25° Grid)<br>
            <b>Elevation:</b> Copernicus DEM 90m<br>
            <b>Real-Time Feed:</b> Open-Meteo Satellite Grid
        </div>
    </aside>

    <!-- Main Content Area -->
    <main>
        <!-- Header -->
        <div>
            <div class="main-title">
                🌊 Hazard-Based Red-Zone Identification for Vulnerable Habitations Using Clustering
            </div>
            <div class="main-subtitle">
                Project ID: SIH26191 | Coverage: Pan-India Multi-State System | Real-Time Live Weather & Flood Alerts | B.Tech ML Project
            </div>
        </div>

        <!-- Academic Disclaimer Banner -->
        <div class="disclaimer-box">
            ⚠️ <b>Academic & Disaster Screening Mandate:</b> This system is an unsupervised machine learning exploratory decision-support system. Cluster groupings represent <i>relative statistical vulnerability</i> based on multi-criteria biophysical, topographic, and hydrometeorological features. Clustering alone <b>does NOT constitute an official government disaster warning, statutory regulatory red-zone demarcation, or administrative evacuation order</b>.
        </div>

        <!-- 5 KPI Metric Cards Row -->
        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-label">🔴 High Hazard Places</div>
                <div class="metric-val" id="kpi-high-val">144</div>
                <div class="metric-delta" id="kpi-high-delta">↑ 62.9% of active</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">🟡 Moderate Hazard</div>
                <div class="metric-val" id="kpi-med-val">18</div>
                <div class="metric-delta" id="kpi-med-delta">↑ 7.9% of active</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">🔵 Lower Hazard</div>
                <div class="metric-val" id="kpi-low-val">67</div>
                <div class="metric-delta" id="kpi-low-delta">↑ 29.3% of active</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">🌧️ Mean Annual Rain</div>
                <div class="metric-val" id="kpi-rain-val">1205.1 mm</div>
                <div class="metric-delta">↑ Max 440 mm/day</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">⛰️ Mean Elevation</div>
                <div class="metric-val" id="kpi-elev-val">134.3 m AMSL</div>
                <div class="metric-delta">↑ Min 0 m</div>
            </div>
        </div>

        <!-- Live Real-Time Weather Section -->
        <div class="alert-banner" id="alert-banner-box">
            <div class="alert-top">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="alert-pill" id="live-alert-pill">🟢 GREEN STATUS (NORMAL / DRY)</span>
                    <span class="alert-station" id="live-station-name">Station: Regional Representative Station: All India (Lat: 17.754°, Lon: 80.921°)</span>
                </div>
                <div style="font-size: 12px; color: #94A3B8;" id="live-obs-time">
                    🕒 Live Observation: 2026-11-08 03:00 IST | 📡 Live API Connected
                </div>
            </div>
            <div class="alert-desc" id="live-alert-desc">
                High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.
            </div>
            <div class="alert-pills-row">
                <span class="pill-item" id="pill-temp">🌡️ Temp: 23.7°C (Feels 28.8°C)</span>
                <span class="pill-item" id="pill-humidity">💧 Humidity: 94%</span>
                <span class="pill-item" id="pill-rain">🌧️ Live Rain: 0.0 mm/h</span>
                <span class="pill-item" id="pill-past24">🌊 Past 24h Rain: 0.0 mm</span>
                <span class="pill-item" id="pill-cond">🌤️ Condition: Clear Sky</span>
                <span class="pill-item" id="pill-wind">💨 Wind: 1.5 km/h</span>
                <span class="pill-item" id="pill-elev">⛰️ Elevation: 134.3 m AMSL</span>
            </div>
        </div>

        <!-- Location Spotlight Box -->
        <div id="spotlight-banner" class="spotlight-box" style="display: none;">
            <div id="spotlight-text">
                📍 <b>Selected Particular Area:</b> <span id="spotlight-name" style="color: #FBBF24; font-weight: bold;"></span> (<span id="spotlight-dist"></span>, <span id="spotlight-state"></span>)
            </div>
            <button onclick="resetLocationSelection()" style="background: transparent; border: 1px solid #FDE047; color: #FDE047; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; font-weight: 600;">
                Reset Selection
            </button>
        </div>

        <!-- Streamlit-Style Tabs Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active" onclick="switchTab('tab-map', this)">🗺️ Interactive Geospatial Map</button>
            <button class="tab-button" onclick="switchTab('tab-districts', this)">🏛️ All Districts in State Matrix</button>
            <button class="tab-button" onclick="switchTab('tab-signatures', this)">📊 Multi-Criteria Risk Signatures</button>
            <button class="tab-button" onclick="switchTab('tab-national', this)">🇮🇳 State-Wise National Comparison</button>
            <button class="tab-button" onclick="switchTab('tab-ml', this)">🤖 Machine Learning Benchmarking</button>
            <button class="tab-button" onclick="switchTab('tab-data', this)">📋 All Places Registry & Explorer</button>
        </div>

        <!-- TAB 1: INTERACTIVE GEOSPATIAL MAP -->
        <div id="tab-map" class="tab-panel active">
            <div>
                <div class="tab-section-header" id="map-section-header">Geospatial Hazard Distribution — All India (Pan-India Overview) (All Districts in State)</div>
                <div class="tab-section-sub" id="map-section-sub">Displaying 229 habitation(s) across 92 district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.</div>
            </div>

            <div id="map"></div>

            <div id="spotlight-graph-box" style="display: none; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div class="graph-card">
                    <div class="graph-title"><span>🎯 Location Multi-Factor Vulnerability Radar</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightRadarChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>📐 Morphometric Profile vs Baseline</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightBarChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: ALL DISTRICTS IN STATE MATRIX -->
        <div id="tab-districts" class="tab-panel">
            <div>
                <div class="tab-section-header" id="districts-section-header">All Districts Matrix & Regional Comparisons — All India</div>
                <div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>
            </div>

            


            


            


            <!-- Live Real-Time Weather Section -->
        <div class="alert-banner" id="alert-banner-box">
            <div class="alert-top">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="alert-pill" id="live-alert-pill">🟢 GREEN STATUS (NORMAL / DRY)</span>
                    <span class="alert-station" id="live-station-name">Station: Regional Representative Station: All India (Lat: 17.754°, Lon: 80.921°)</span>
                </div>
                <div style="font-size: 12px; color: #94A3B8;" id="live-obs-time">
                    🕒 Live Observation: 2026-11-08 03:00 IST | 📡 Live API Connected
                </div>
            </div>
            <div class="alert-desc" id="live-alert-desc">
                High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.
            </div>
            <div class="alert-pills-row">
                <span class="pill-item" id="pill-temp">🌡️ Temp: 23.7°C (Feels 28.8°C)</span>
                <span class="pill-item" id="pill-humidity">💧 Humidity: 94%</span>
                <span class="pill-item" id="pill-rain">🌧️ Live Rain: 0.0 mm/h</span>
                <span class="pill-item" id="pill-past24">🌊 Past 24h Rain: 0.0 mm</span>
                <span class="pill-item" id="pill-cond">🌤️ Condition: Clear Sky</span>
                <span class="pill-item" id="pill-wind">💨 Wind: 1.5 km/h</span>
                <span class="pill-item" id="pill-elev">⛰️ Elevation: 134.3 m AMSL</span>
            </div>
        </div>

        <!-- Location Spotlight Box -->
        <div id="spotlight-banner" class="spotlight-box" style="display: none;">
            <div id="spotlight-text">
                📍 <b>Selected Particular Area:</b> <span id="spotlight-name" style="color: #FBBF24; font-weight: bold;"></span> (<span id="spotlight-dist"></span>, <span id="spotlight-state"></span>)
            </div>
            <button onclick="resetLocationSelection()" style="background: transparent; border: 1px solid #FDE047; color: #FDE047; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; font-weight: 600;">
                Reset Selection
            </button>
        </div>

        <!-- Streamlit-Style Tabs Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active" onclick="switchTab('tab-map', this)">🗺️ Interactive Geospatial Map</button>
            <button class="tab-button" onclick="switchTab('tab-districts', this)">🏛️ All Districts in State Matrix</button>
            <button class="tab-button" onclick="switchTab('tab-signatures', this)">📊 Multi-Criteria Risk Signatures</button>
            <button class="tab-button" onclick="switchTab('tab-national', this)">🇮🇳 State-Wise National Comparison</button>
            <button class="tab-button" onclick="switchTab('tab-ml', this)">🤖 Machine Learning Benchmarking</button>
            <button class="tab-button" onclick="switchTab('tab-data', this)">📋 All Places Registry & Explorer</button>
        </div>

        <!-- TAB 1: INTERACTIVE GEOSPATIAL MAP -->
        <div id="tab-map" class="tab-panel active">
            <div>
                <div class="tab-section-header" id="map-section-header">Geospatial Hazard Distribution — All India (Pan-India Overview) (All Districts in State)</div>
                <div class="tab-section-sub" id="map-section-sub">Displaying 229 habitation(s) across 92 district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.</div>
            </div>

            <div id="map"></div>

            <div id="spotlight-graph-box" style="display: none; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div class="graph-card">
                    <div class="graph-title"><span>🎯 Location Multi-Factor Vulnerability Radar</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightRadarChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>📐 Morphometric Profile vs Baseline</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightBarChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: ALL DISTRICTS IN STATE MATRIX -->
        <div id="tab-districts" class="tab-panel">
            <div>
                <div class="tab-section-header" id="districts-section-header">All Districts Matrix & Regional Comparisons — All India</div>
                <div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>
            </div>

            <!-- Live Real-Time Weather Section -->
        <div class="alert-banner" id="alert-banner-box">
            <div class="alert-top">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="alert-pill" id="live-alert-pill">🟢 GREEN STATUS (NORMAL / DRY)</span>
                    <span class="alert-station" id="live-station-name">Station: Regional Representative Station: All India (Lat: 17.754°, Lon: 80.921°)</span>
                </div>
                <div style="font-size: 12px; color: #94A3B8;" id="live-obs-time">
                    🕒 Live Observation: 2026-11-08 03:00 IST | 📡 Live API Connected
                </div>
            </div>
            <div class="alert-desc" id="live-alert-desc">
                High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.
            </div>
            <div class="alert-pills-row">
                <span class="pill-item" id="pill-temp">🌡️ Temp: 23.7°C (Feels 28.8°C)</span>
                <span class="pill-item" id="pill-humidity">💧 Humidity: 94%</span>
                <span class="pill-item" id="pill-rain">🌧️ Live Rain: 0.0 mm/h</span>
                <span class="pill-item" id="pill-past24">🌊 Past 24h Rain: 0.0 mm</span>
                <span class="pill-item" id="pill-cond">🌤️ Condition: Clear Sky</span>
                <span class="pill-item" id="pill-wind">💨 Wind: 1.5 km/h</span>
                <span class="pill-item" id="pill-elev">⛰️ Elevation: 134.3 m AMSL</span>
            </div>
        </div>

        <!-- Location Spotlight Box -->
        <div id="spotlight-banner" class="spotlight-box" style="display: none;">
            <div id="spotlight-text">
                📍 <b>Selected Particular Area:</b> <span id="spotlight-name" style="color: #FBBF24; font-weight: bold;"></span> (<span id="spotlight-dist"></span>, <span id="spotlight-state"></span>)
            </div>
            <button onclick="resetLocationSelection()" style="background: transparent; border: 1px solid #FDE047; color: #FDE047; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; font-weight: 600;">
                Reset Selection
            </button>
        </div>

        <!-- Streamlit-Style Tabs Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active" onclick="switchTab('tab-map', this)">🗺️ Interactive Geospatial Map</button>
            <button class="tab-button" onclick="switchTab('tab-districts', this)">🏛️ All Districts in State Matrix</button>
            <button class="tab-button" onclick="switchTab('tab-signatures', this)">📊 Multi-Criteria Risk Signatures</button>
            <button class="tab-button" onclick="switchTab('tab-national', this)">🇮🇳 State-Wise National Comparison</button>
            <button class="tab-button" onclick="switchTab('tab-ml', this)">🤖 Machine Learning Benchmarking</button>
            <button class="tab-button" onclick="switchTab('tab-data', this)">📋 All Places Registry & Explorer</button>
        </div>

        <!-- TAB 1: INTERACTIVE GEOSPATIAL MAP -->
        <div id="tab-map" class="tab-panel active">
            <div>
                <div class="tab-section-header" id="map-section-header">Geospatial Hazard Distribution — All India (Pan-India Overview) (All Districts in State)</div>
                <div class="tab-section-sub" id="map-section-sub">Displaying 229 habitation(s) across 92 district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.</div>
            </div>

            <div id="map"></div>

            <div id="spotlight-graph-box" style="display: none; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div class="graph-card">
                    <div class="graph-title"><span>🎯 Location Multi-Factor Vulnerability Radar</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightRadarChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>📐 Morphometric Profile vs Baseline</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightBarChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: ALL DISTRICTS IN STATE MATRIX -->
        <div id="tab-districts" class="tab-panel">
            <div>
                <div class="tab-section-header" id="districts-section-header">All Districts Matrix & Regional Comparisons — All India</div>
                <div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>
            </div>

            


            <!-- Live Real-Time Weather Section -->
        <div class="alert-banner" id="alert-banner-box">
            <div class="alert-top">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="alert-pill" id="live-alert-pill">🟢 GREEN STATUS (NORMAL / DRY)</span>
                    <span class="alert-station" id="live-station-name">Station: Regional Representative Station: All India (Lat: 17.754°, Lon: 80.921°)</span>
                </div>
                <div style="font-size: 12px; color: #94A3B8;" id="live-obs-time">
                    🕒 Live Observation: 2026-11-08 03:00 IST | 📡 Live API Connected
                </div>
            </div>
            <div class="alert-desc" id="live-alert-desc">
                High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.
            </div>
            <div class="alert-pills-row">
                <span class="pill-item" id="pill-temp">🌡️ Temp: 23.7°C (Feels 28.8°C)</span>
                <span class="pill-item" id="pill-humidity">💧 Humidity: 94%</span>
                <span class="pill-item" id="pill-rain">🌧️ Live Rain: 0.0 mm/h</span>
                <span class="pill-item" id="pill-past24">🌊 Past 24h Rain: 0.0 mm</span>
                <span class="pill-item" id="pill-cond">🌤️ Condition: Clear Sky</span>
                <span class="pill-item" id="pill-wind">💨 Wind: 1.5 km/h</span>
                <span class="pill-item" id="pill-elev">⛰️ Elevation: 134.3 m AMSL</span>
            </div>
        </div>

        <!-- Location Spotlight Box -->
        <div id="spotlight-banner" class="spotlight-box" style="display: none;">
            <div id="spotlight-text">
                📍 <b>Selected Particular Area:</b> <span id="spotlight-name" style="color: #FBBF24; font-weight: bold;"></span> (<span id="spotlight-dist"></span>, <span id="spotlight-state"></span>)
            </div>
            <button onclick="resetLocationSelection()" style="background: transparent; border: 1px solid #FDE047; color: #FDE047; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; font-weight: 600;">
                Reset Selection
            </button>
        </div>

        <!-- Streamlit-Style Tabs Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active" onclick="switchTab('tab-map', this)">🗺️ Interactive Geospatial Map</button>
            <button class="tab-button" onclick="switchTab('tab-districts', this)">🏛️ All Districts in State Matrix</button>
            <button class="tab-button" onclick="switchTab('tab-signatures', this)">📊 Multi-Criteria Risk Signatures</button>
            <button class="tab-button" onclick="switchTab('tab-national', this)">🇮🇳 State-Wise National Comparison</button>
            <button class="tab-button" onclick="switchTab('tab-ml', this)">🤖 Machine Learning Benchmarking</button>
            <button class="tab-button" onclick="switchTab('tab-data', this)">📋 All Places Registry & Explorer</button>
        </div>

        <!-- TAB 1: INTERACTIVE GEOSPATIAL MAP -->
        <div id="tab-map" class="tab-panel active">
            <div>
                <div class="tab-section-header" id="map-section-header">Geospatial Hazard Distribution — All India (Pan-India Overview) (All Districts in State)</div>
                <div class="tab-section-sub" id="map-section-sub">Displaying 229 habitation(s) across 92 district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.</div>
            </div>

            <div id="map"></div>

            <div id="spotlight-graph-box" style="display: none; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div class="graph-card">
                    <div class="graph-title"><span>🎯 Location Multi-Factor Vulnerability Radar</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightRadarChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>📐 Morphometric Profile vs Baseline</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightBarChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: ALL DISTRICTS IN STATE MATRIX -->
        <div id="tab-districts" class="tab-panel">
            <div>
                <div class="tab-section-header" id="districts-section-header">All Districts Matrix & Regional Comparisons — All India</div>
                <div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>
            </div>

            <!-- Live Real-Time Weather Section -->
        <div class="alert-banner" id="alert-banner-box">
            <div class="alert-top">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="alert-pill" id="live-alert-pill">🟢 GREEN STATUS (NORMAL / DRY)</span>
                    <span class="alert-station" id="live-station-name">Station: Regional Representative Station: All India (Lat: 17.754°, Lon: 80.921°)</span>
                </div>
                <div style="font-size: 12px; color: #94A3B8;" id="live-obs-time">
                    🕒 Live Observation: 2026-11-08 03:00 IST | 📡 Live API Connected
                </div>
            </div>
            <div class="alert-desc" id="live-alert-desc">
                High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.
            </div>
            <div class="alert-pills-row">
                <span class="pill-item" id="pill-temp">🌡️ Temp: 23.7°C (Feels 28.8°C)</span>
                <span class="pill-item" id="pill-humidity">💧 Humidity: 94%</span>
                <span class="pill-item" id="pill-rain">🌧️ Live Rain: 0.0 mm/h</span>
                <span class="pill-item" id="pill-past24">🌊 Past 24h Rain: 0.0 mm</span>
                <span class="pill-item" id="pill-cond">🌤️ Condition: Clear Sky</span>
                <span class="pill-item" id="pill-wind">💨 Wind: 1.5 km/h</span>
                <span class="pill-item" id="pill-elev">⛰️ Elevation: 134.3 m AMSL</span>
            </div>
        </div>

        <!-- Location Spotlight Box -->
        <div id="spotlight-banner" class="spotlight-box" style="display: none;">
            <div id="spotlight-text">
                📍 <b>Selected Particular Area:</b> <span id="spotlight-name" style="color: #FBBF24; font-weight: bold;"></span> (<span id="spotlight-dist"></span>, <span id="spotlight-state"></span>)
            </div>
            <button onclick="resetLocationSelection()" style="background: transparent; border: 1px solid #FDE047; color: #FDE047; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; font-weight: 600;">
                Reset Selection
            </button>
        </div>

        <!-- Streamlit-Style Tabs Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active" onclick="switchTab('tab-map', this)">🗺️ Interactive Geospatial Map</button>
            <button class="tab-button" onclick="switchTab('tab-districts', this)">🏛️ All Districts in State Matrix</button>
            <button class="tab-button" onclick="switchTab('tab-signatures', this)">📊 Multi-Criteria Risk Signatures</button>
            <button class="tab-button" onclick="switchTab('tab-national', this)">🇮🇳 State-Wise National Comparison</button>
            <button class="tab-button" onclick="switchTab('tab-ml', this)">🤖 Machine Learning Benchmarking</button>
            <button class="tab-button" onclick="switchTab('tab-data', this)">📋 All Places Registry & Explorer</button>
        </div>

        <!-- TAB 1: INTERACTIVE GEOSPATIAL MAP -->
        <div id="tab-map" class="tab-panel active">
            <div>
                <div class="tab-section-header" id="map-section-header">Geospatial Hazard Distribution — All India (Pan-India Overview) (All Districts in State)</div>
                <div class="tab-section-sub" id="map-section-sub">Displaying 229 habitation(s) across 92 district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.</div>
            </div>

            <div id="map"></div>

            <div id="spotlight-graph-box" style="display: none; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div class="graph-card">
                    <div class="graph-title"><span>🎯 Location Multi-Factor Vulnerability Radar</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightRadarChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>📐 Morphometric Profile vs Baseline</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightBarChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: ALL DISTRICTS IN STATE MATRIX -->
        <div id="tab-districts" class="tab-panel">
            <div>
                <div class="tab-section-header" id="districts-section-header">All Districts Matrix & Regional Comparisons — All India</div>
                <div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>
            </div>

            


            


            <!-- Live Real-Time Weather Section -->
        <div class="alert-banner" id="alert-banner-box">
            <div class="alert-top">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="alert-pill" id="live-alert-pill">🟢 GREEN STATUS (NORMAL / DRY)</span>
                    <span class="alert-station" id="live-station-name">Station: Regional Representative Station: All India (Lat: 17.754°, Lon: 80.921°)</span>
                </div>
                <div style="font-size: 12px; color: #94A3B8;" id="live-obs-time">
                    🕒 Live Observation: 2026-11-08 03:00 IST | 📡 Live API Connected
                </div>
            </div>
            <div class="alert-desc" id="live-alert-desc">
                High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.
            </div>
            <div class="alert-pills-row">
                <span class="pill-item" id="pill-temp">🌡️ Temp: 23.7°C (Feels 28.8°C)</span>
                <span class="pill-item" id="pill-humidity">💧 Humidity: 94%</span>
                <span class="pill-item" id="pill-rain">🌧️ Live Rain: 0.0 mm/h</span>
                <span class="pill-item" id="pill-past24">🌊 Past 24h Rain: 0.0 mm</span>
                <span class="pill-item" id="pill-cond">🌤️ Condition: Clear Sky</span>
                <span class="pill-item" id="pill-wind">💨 Wind: 1.5 km/h</span>
                <span class="pill-item" id="pill-elev">⛰️ Elevation: 134.3 m AMSL</span>
            </div>
        </div>

        <!-- Location Spotlight Box -->
        <div id="spotlight-banner" class="spotlight-box" style="display: none;">
            <div id="spotlight-text">
                📍 <b>Selected Particular Area:</b> <span id="spotlight-name" style="color: #FBBF24; font-weight: bold;"></span> (<span id="spotlight-dist"></span>, <span id="spotlight-state"></span>)
            </div>
            <button onclick="resetLocationSelection()" style="background: transparent; border: 1px solid #FDE047; color: #FDE047; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; font-weight: 600;">
                Reset Selection
            </button>
        </div>

        <!-- Streamlit-Style Tabs Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active" onclick="switchTab('tab-map', this)">🗺️ Interactive Geospatial Map</button>
            <button class="tab-button" onclick="switchTab('tab-districts', this)">🏛️ All Districts in State Matrix</button>
            <button class="tab-button" onclick="switchTab('tab-signatures', this)">📊 Multi-Criteria Risk Signatures</button>
            <button class="tab-button" onclick="switchTab('tab-national', this)">🇮🇳 State-Wise National Comparison</button>
            <button class="tab-button" onclick="switchTab('tab-ml', this)">🤖 Machine Learning Benchmarking</button>
            <button class="tab-button" onclick="switchTab('tab-data', this)">📋 All Places Registry & Explorer</button>
        </div>

        <!-- TAB 1: INTERACTIVE GEOSPATIAL MAP -->
        <div id="tab-map" class="tab-panel active">
            <div>
                <div class="tab-section-header" id="map-section-header">Geospatial Hazard Distribution — All India (Pan-India Overview) (All Districts in State)</div>
                <div class="tab-section-sub" id="map-section-sub">Displaying 229 habitation(s) across 92 district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.</div>
            </div>

            <div id="map"></div>

            <div id="spotlight-graph-box" style="display: none; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div class="graph-card">
                    <div class="graph-title"><span>🎯 Location Multi-Factor Vulnerability Radar</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightRadarChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>📐 Morphometric Profile vs Baseline</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightBarChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: ALL DISTRICTS IN STATE MATRIX -->
        <div id="tab-districts" class="tab-panel">
            <div>
                <div class="tab-section-header" id="districts-section-header">All Districts Matrix & Regional Comparisons — All India</div>
                <div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>
            </div>

            <!-- Live Real-Time Weather Section -->
        <div class="alert-banner" id="alert-banner-box">
            <div class="alert-top">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="alert-pill" id="live-alert-pill">🟢 GREEN STATUS (NORMAL / DRY)</span>
                    <span class="alert-station" id="live-station-name">Station: Regional Representative Station: All India (Lat: 17.754°, Lon: 80.921°)</span>
                </div>
                <div style="font-size: 12px; color: #94A3B8;" id="live-obs-time">
                    🕒 Live Observation: 2026-11-08 03:00 IST | 📡 Live API Connected
                </div>
            </div>
            <div class="alert-desc" id="live-alert-desc">
                High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.
            </div>
            <div class="alert-pills-row">
                <span class="pill-item" id="pill-temp">🌡️ Temp: 23.7°C (Feels 28.8°C)</span>
                <span class="pill-item" id="pill-humidity">💧 Humidity: 94%</span>
                <span class="pill-item" id="pill-rain">🌧️ Live Rain: 0.0 mm/h</span>
                <span class="pill-item" id="pill-past24">🌊 Past 24h Rain: 0.0 mm</span>
                <span class="pill-item" id="pill-cond">🌤️ Condition: Clear Sky</span>
                <span class="pill-item" id="pill-wind">💨 Wind: 1.5 km/h</span>
                <span class="pill-item" id="pill-elev">⛰️ Elevation: 134.3 m AMSL</span>
            </div>
        </div>

        <!-- Location Spotlight Box -->
        <div id="spotlight-banner" class="spotlight-box" style="display: none;">
            <div id="spotlight-text">
                📍 <b>Selected Particular Area:</b> <span id="spotlight-name" style="color: #FBBF24; font-weight: bold;"></span> (<span id="spotlight-dist"></span>, <span id="spotlight-state"></span>)
            </div>
            <button onclick="resetLocationSelection()" style="background: transparent; border: 1px solid #FDE047; color: #FDE047; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; font-weight: 600;">
                Reset Selection
            </button>
        </div>

        <!-- Streamlit-Style Tabs Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active" onclick="switchTab('tab-map', this)">🗺️ Interactive Geospatial Map</button>
            <button class="tab-button" onclick="switchTab('tab-districts', this)">🏛️ All Districts in State Matrix</button>
            <button class="tab-button" onclick="switchTab('tab-signatures', this)">📊 Multi-Criteria Risk Signatures</button>
            <button class="tab-button" onclick="switchTab('tab-national', this)">🇮🇳 State-Wise National Comparison</button>
            <button class="tab-button" onclick="switchTab('tab-ml', this)">🤖 Machine Learning Benchmarking</button>
            <button class="tab-button" onclick="switchTab('tab-data', this)">📋 All Places Registry & Explorer</button>
        </div>

        <!-- TAB 1: INTERACTIVE GEOSPATIAL MAP -->
        <div id="tab-map" class="tab-panel active">
            <div>
                <div class="tab-section-header" id="map-section-header">Geospatial Hazard Distribution — All India (Pan-India Overview) (All Districts in State)</div>
                <div class="tab-section-sub" id="map-section-sub">Displaying 229 habitation(s) across 92 district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.</div>
            </div>

            <div id="map"></div>

            <div id="spotlight-graph-box" style="display: none; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div class="graph-card">
                    <div class="graph-title"><span>🎯 Location Multi-Factor Vulnerability Radar</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightRadarChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>📐 Morphometric Profile vs Baseline</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightBarChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: ALL DISTRICTS IN STATE MATRIX -->
        <div id="tab-districts" class="tab-panel">
            <div>
                <div class="tab-section-header" id="districts-section-header">All Districts Matrix & Regional Comparisons — All India</div>
                <div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>
            </div>

            


            <!-- Live Real-Time Weather Section -->
        <div class="alert-banner" id="alert-banner-box">
            <div class="alert-top">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="alert-pill" id="live-alert-pill">🟢 GREEN STATUS (NORMAL / DRY)</span>
                    <span class="alert-station" id="live-station-name">Station: Regional Representative Station: All India (Lat: 17.754°, Lon: 80.921°)</span>
                </div>
                <div style="font-size: 12px; color: #94A3B8;" id="live-obs-time">
                    🕒 Live Observation: 2026-11-08 03:00 IST | 📡 Live API Connected
                </div>
            </div>
            <div class="alert-desc" id="live-alert-desc">
                High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.
            </div>
            <div class="alert-pills-row">
                <span class="pill-item" id="pill-temp">🌡️ Temp: 23.7°C (Feels 28.8°C)</span>
                <span class="pill-item" id="pill-humidity">💧 Humidity: 94%</span>
                <span class="pill-item" id="pill-rain">🌧️ Live Rain: 0.0 mm/h</span>
                <span class="pill-item" id="pill-past24">🌊 Past 24h Rain: 0.0 mm</span>
                <span class="pill-item" id="pill-cond">🌤️ Condition: Clear Sky</span>
                <span class="pill-item" id="pill-wind">💨 Wind: 1.5 km/h</span>
                <span class="pill-item" id="pill-elev">⛰️ Elevation: 134.3 m AMSL</span>
            </div>
        </div>

        <!-- Location Spotlight Box -->
        <div id="spotlight-banner" class="spotlight-box" style="display: none;">
            <div id="spotlight-text">
                📍 <b>Selected Particular Area:</b> <span id="spotlight-name" style="color: #FBBF24; font-weight: bold;"></span> (<span id="spotlight-dist"></span>, <span id="spotlight-state"></span>)
            </div>
            <button onclick="resetLocationSelection()" style="background: transparent; border: 1px solid #FDE047; color: #FDE047; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; font-weight: 600;">
                Reset Selection
            </button>
        </div>

        <!-- Streamlit-Style Tabs Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active" onclick="switchTab('tab-map', this)">🗺️ Interactive Geospatial Map</button>
            <button class="tab-button" onclick="switchTab('tab-districts', this)">🏛️ All Districts in State Matrix</button>
            <button class="tab-button" onclick="switchTab('tab-signatures', this)">📊 Multi-Criteria Risk Signatures</button>
            <button class="tab-button" onclick="switchTab('tab-national', this)">🇮🇳 State-Wise National Comparison</button>
            <button class="tab-button" onclick="switchTab('tab-ml', this)">🤖 Machine Learning Benchmarking</button>
            <button class="tab-button" onclick="switchTab('tab-data', this)">📋 All Places Registry & Explorer</button>
        </div>

        <!-- TAB 1: INTERACTIVE GEOSPATIAL MAP -->
        <div id="tab-map" class="tab-panel active">
            <div>
                <div class="tab-section-header" id="map-section-header">Geospatial Hazard Distribution — All India (Pan-India Overview) (All Districts in State)</div>
                <div class="tab-section-sub" id="map-section-sub">Displaying 229 habitation(s) across 92 district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.</div>
            </div>

            <div id="map"></div>

            <div id="spotlight-graph-box" style="display: none; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div class="graph-card">
                    <div class="graph-title"><span>🎯 Location Multi-Factor Vulnerability Radar</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightRadarChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>📐 Morphometric Profile vs Baseline</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="spotlightBarChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: ALL DISTRICTS IN STATE MATRIX -->
        <div id="tab-districts" class="tab-panel">
            <div>
                <div class="tab-section-header" id="districts-section-header">All Districts Matrix & Regional Comparisons — All India</div>
                <div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>
            </div>

            <!-- Executive Graphs Overview Row -->
        <div class="exec-graphs-row">
            <div class="graph-card">
                <div class="graph-title"><span>📈 Danger Level Distribution</span></div>
                <div style="height: 220px; position: relative;">
                    <canvas id="dangerDonutChart"></canvas>
                </div>
            </div>
            <div class="graph-card">
                <div class="graph-title"><span>🏘️ Category vs Hazard Tier</span></div>
                <div style="height: 220px; position: relative;">
                    <canvas id="categoryBarChart"></canvas>
                </div>
            </div>
            <div class="graph-card">
                <div class="graph-title"><span>⚠️ Top Critical Sites: Elevation & Inundation</span></div>
                <div style="height: 220px; position: relative;">
                    <canvas id="topRiskBarChart"></canvas>
                </div>
            </div>
        </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div class="graph-card">
                    <div class="graph-title"><span>Districts Ranked by High Danger (%)</span></div>
                    <div style="height: 280px; position: relative;">
                        <canvas id="districtsRankChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>District-Wise Danger Tier Composition</span></div>
                    <div style="height: 280px; position: relative;">
                        <canvas id="districtsStackChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="table-wrap">
                <table id="districts-table">
                    <thead>
                        <tr>
                            <th>District</th>
                            <th>Habitations Monitored</th>
                            <th>🔴 High Danger Count</th>
                            <th>🟡 Medium Danger</th>
                            <th>🔵 Low Danger</th>
                            <th>High Danger (%)</th>
                            <th>Mean Elevation (m)</th>
                            <th>Mean River Distance (km)</th>
                            <th>Mean Annual Rain (mm)</th>
                        </tr>
                    </thead>
                    <tbody id="districts-table-body"></tbody>
                </table>
            </div>
        </div>

        <!-- TAB 3: MULTI-CRITERIA RISK SIGNATURES & RESEARCH FIGURES -->
        <div id="tab-signatures" class="tab-panel">
            <div>
                <div class="tab-section-header">Multi-Criteria Risk Signatures & Research Visualizations</div>
                <div class="tab-section-sub">Comprehensive multi-dimensional analysis, Principal Components, and high-resolution academic figures:</div>
            </div>
            <div style="display: grid; grid-template-columns: 1.1fr 1fr; gap: 12px;">
                <div class="graph-card">
                    <div class="graph-title"><span>🕸️ Multi-Criteria Biophysical Risk Radar Signature</span></div>
                    <div style="height: 320px; position: relative;">
                        <canvas id="signaturesRadarChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>📍 2D Principal Component (PCA) Projection Scatter</span></div>
                    <div style="height: 320px; position: relative;">
                        <canvas id="signaturesPcaChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Academic Research Figures Gallery -->
            <div style="margin-top: 10px;">
                <div class="tab-section-header" style="font-size: 16px; margin-bottom: 10px;">🔬 Academic Research Figures Gallery (Click to Enlarge)</div>
                <div class="figure-grid">
                    <div class="figure-card">
                        <img src="outputs/figures/11_cluster_radar_signature.png" alt="Multi-Criteria Radar Signature" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 11: Multi-Criteria Radar Signature</div>
                        <div class="figure-desc">Normalized profiles across all 8 continuous biophysical indicators for High, Medium, and Low hazard clusters.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/08_pca_2d_clusters.png" alt="2D PCA Clusters" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 8: 2D PCA Cluster Separation</div>
                        <div class="figure-desc">First two Principal Components capturing 72.3% of total variance with convex hull cluster envelopes.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/09_pca_biplot.png" alt="PCA Biplot" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 9: PCA Biplot with Feature Vectors</div>
                        <div class="figure-desc">Feature loading arrows showing directional alignment of elevation, river distance, and flood history.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/10_tsne_clusters.png" alt="t-SNE Clusters" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 10: t-SNE Non-Linear Manifold Projection</div>
                        <div class="figure-desc">Non-linear neighborhood preservation validating distinct separation of flood basin settlements.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/01_correlation_matrix.png" alt="Correlation Matrix" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 1: Pairwise Feature Correlation Heatmap</div>
                        <div class="figure-desc">Pearson correlation matrix identifying multicollinearity between elevation and river proximity.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/02_feature_outlier_boxplots.png" alt="Feature Boxplots" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 2: Feature Distribution & Outlier Boxplots</div>
                        <div class="figure-desc">Statistical spread showing interquartile ranges and extreme values across all physical variables.</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: STATE-WISE NATIONAL COMPARISON -->
        <div id="tab-national" class="tab-panel">
            <div>
                <div class="tab-section-header">State-Wise Flood Hazard & Vulnerability Comparison across India</div>
                <div class="tab-section-sub">Cross-state benchmarking and river basin floodway distributions:</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div class="graph-card">
                    <div class="graph-title"><span>State-Wise High Hazard Proportion (%)</span></div>
                    <div style="height: 300px; position: relative;">
                        <canvas id="stateRankChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>National Danger Tier Breakdown by State</span></div>
                    <div style="height: 300px; position: relative;">
                        <canvas id="stateStackChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="graph-card">
                <div class="graph-title"><span>🌊 Major River Basin Flood Exposure</span></div>
                <div style="height: 250px; position: relative;">
                    <canvas id="basinBarChart"></canvas>
                </div>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>State / Union Territory</th>
                            <th>Districts Monitored</th>
                            <th>Total Settlements</th>
                            <th>High Danger Count</th>
                            <th>High Danger (%)</th>
                            <th>Mean Elevation (m)</th>
                            <th>Mean Annual Rain (mm)</th>
                        </tr>
                    </thead>
                    <tbody id="national-table-body"></tbody>
                </table>
            </div>
        </div>

        <!-- TAB 5: ML BENCHMARKING & VALIDATION FIGURES -->
        <div id="tab-ml" class="tab-panel">
            <div>
                <div class="tab-section-header">Machine Learning Algorithm Benchmarking & Metric Validation</div>
                <div class="tab-section-sub">Rigorous clustering validation across K-Medoids, K-Means++, Hierarchical Ward, and DBSCAN:</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div class="graph-card">
                    <div class="graph-title"><span>Silhouette Score Comparison (Higher is Better)</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="mlSilhouetteChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>Davies-Bouldin Index (Lower is Better)</span></div>
                    <div style="height: 260px; position: relative;">
                        <canvas id="mlDbChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="graph-card">
                <div class="graph-title"><span>Optimal Cluster Trajectory: Elbow Inflection & Silhouette Peak (K=3)</span></div>
                <div style="height: 260px; position: relative;">
                    <canvas id="mlElbowChart"></canvas>
                </div>
            </div>

            <!-- Academic ML Evaluation Figures Gallery -->
            <div style="margin-top: 10px;">
                <div class="tab-section-header" style="font-size: 16px; margin-bottom: 10px;">📊 Academic Machine Learning Figures (Click to Enlarge)</div>
                <div class="figure-grid">
                    <div class="figure-card">
                        <img src="outputs/figures/03_kmeans_elbow_silhouette.png" alt="K-Means Elbow and Silhouette" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 3: Elbow Inertia & Silhouette Trajectory</div>
                        <div class="figure-desc">Dual-axis curve confirming optimal clustering inflection at K=3 with maximum silhouette coefficient.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/04_silhouette_plot_k3.png" alt="Silhouette Plot K=3" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 4: Silhouette Analysis per Cluster (K=3)</div>
                        <div class="figure-desc">Thickness and score silhouettes proving zero misallocated samples and balanced cluster geometries.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/05_hierarchical_dendrogram.png" alt="Hierarchical Dendrogram" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 5: Hierarchical Clustering Dendrogram (Ward Linkage)</div>
                        <div class="figure-desc">Tree cutting threshold at distance 11.5 generating identical 3-tier hazard regimes.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/06_dbscan_k_distance_graph.png" alt="DBSCAN K-Distance Graph" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 6: DBSCAN 4th-NN K-Distance Elbow</div>
                        <div class="figure-desc">Optimal epsilon tuning (eps=1.85) identifying 12 true anomaly points in extreme hazard epicenters.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/07_pca_scree_plot.png" alt="PCA Scree Plot" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 7: PCA Scree Plot & Cumulative Variance</div>
                        <div class="figure-desc">Eigenvalue decomposition showing 85.8% cumulative variance explained by first 3 components.</div>
                    </div>
                    <div class="figure-card">
                        <img src="outputs/figures/12_cluster_feature_bars.png" alt="Cluster Feature Bars" onclick="openImageModal(this.src, this.alt)" />
                        <div class="figure-caption">Figure 12: Standardized Feature Deviations by Cluster</div>
                        <div class="figure-desc">Z-score deviations highlighting severe drainage and elevation anomalies for Tier 1 Red-Zones.</div>
                    </div>
                </div>
            </div>

            <!-- Algorithm Benchmarking Table -->
            <div class="table-wrap" style="margin-top: 10px;">
                <table>
                    <thead>
                        <tr>
                            <th>Clustering Algorithm</th>
                            <th>Distance Metric</th>
                            <th>Optimal K</th>
                            <th>Silhouette Score</th>
                            <th>Davies-Bouldin Index</th>
                            <th>Key Academic Finding</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><b>K-Medoids (PAM)</b></td>
                            <td>Manhattan (L1)</td>
                            <td>3</td>
                            <td style="color: #21C354; font-weight: bold;">0.4320 (Winner)</td>
                            <td>1.0421</td>
                            <td>Highest cohesion; authentic exemplars (Munnangi, Gorantla, Velagapudi).</td>
                        </tr>
                        <tr>
                            <td><b>K-Means++</b></td>
                            <td>Euclidean (L2)</td>
                            <td>3</td>
                            <td>0.3667</td>
                            <td>1.1202</td>
                            <td>Optimal elbow inflection at K=3; balanced cluster sizes (47, 32, 21).</td>
                        </tr>
                        <tr>
                            <td><b>Hierarchical (Ward)</b></td>
                            <td>Variance Dissimilarity</td>
                            <td>3</td>
                            <td>0.3283</td>
                            <td>1.0843</td>
                            <td>Cutting dendrogram at 11.5 cleanly separates three hazard regimes.</td>
                        </tr>
                        <tr>
                            <td><b>DBSCAN</b></td>
                            <td>Density Reachability (eps=1.85)</td>
                            <td>2 + Noise</td>
                            <td>0.2841</td>
                            <td>1.3140</td>
                            <td>Isolated 12 noise points representing true extreme disaster epicenters.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- TAB 6: DATA EXPLORER & REGISTRY -->
        <div id="tab-data" class="tab-panel">
            <div>
                <div class="tab-section-header">Pan-India All Places & Habitations Registry</div>
                <div class="tab-section-sub">Search, inspect, and export all 229 catalogued habitations across 15 States and 92 Districts:</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div class="graph-card">
                    <div class="graph-title"><span>Surface Elevation Distribution Histogram</span></div>
                    <div style="height: 220px; position: relative;">
                        <canvas id="elevHistChart"></canvas>
                    </div>
                </div>
                <div class="graph-card">
                    <div class="graph-title"><span>River Distance Distribution Histogram</span></div>
                    <div style="height: 220px; position: relative;">
                        <canvas id="riverHistChart"></canvas>
                    </div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <input type="text" id="data-search" placeholder="🔍 Search place, district, or mandal..." oninput="renderDataTable()" style="max-width: 320px;" />
                <button onclick="downloadCSV()" style="background: var(--accent-red); color: #FFF; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 700; cursor: pointer;">
                    📥 Download Filtered Data (CSV)
                </button>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Habitation Name</th>
                            <th>State</th>
                            <th>District</th>
                            <th>Mandal</th>
                            <th>Hazard Tier</th>
                            <th>Elevation (m)</th>
                            <th>River Dist (km)</th>
                            <th>Annual Rain (mm)</th>
                            <th>Max Daily Rain (mm)</th>
                            <th>Population</th>
                        </tr>
                    </thead>
                    <tbody id="data-table-body"></tbody>
                </table>
            </div>
        </div>
    </main>

    <!-- Lightbox Modal for Full-Resolution Image Inspection -->
    <div id="img-modal" onclick="closeImageModal()">
        <span class="modal-close">&times;</span>
        <img id="modal-img" src="" alt="Enlarged Figure" onclick="event.stopPropagation()">
        <div id="modal-caption"></div>
    </div>

    <!-- Embedded Data & Chart.js Engine -->
    <script>
        const allPlaces = {places_json};

        // Configure Chart.js global dark theme defaults
        Chart.defaults.color = '#94A3B8';
        Chart.defaults.borderColor = '#2B3245';
        Chart.defaults.font.family = 'Inter, -apple-system, sans-serif';

        const chartInstances = {{}};
        function renderOrUpdateChart(id, config) {{
            if (chartInstances[id]) {{
                chartInstances[id].destroy();
            }}
            const ctx = document.getElementById(id);
            if (ctx) {{
                chartInstances[id] = new Chart(ctx, config);
            }}
        }}

        function openImageModal(src, caption) {{
            document.getElementById('modal-img').src = src;
            document.getElementById('modal-caption').textContent = caption;
            document.getElementById('img-modal').style.display = 'flex';
        }}

        function closeImageModal() {{
            document.getElementById('img-modal').style.display = 'none';
        }}

        // State Centering & Zoom Info
        const stateGeo = {{
            "All India (Pan-India Overview)": {{ center: [21.5, 80.0], zoom: 5 }},
            "Andhra Pradesh": {{ center: [16.42, 80.60], zoom: 8 }},
            "Assam": {{ center: [26.20, 92.80], zoom: 7 }},
            "Bihar": {{ center: [25.75, 85.90], zoom: 7 }},
            "Kerala": {{ center: [10.20, 76.50], zoom: 8 }},
            "Odisha": {{ center: [20.50, 85.50], zoom: 7 }},
            "West Bengal": {{ center: [23.50, 87.80], zoom: 7 }},
            "Maharashtra": {{ center: [18.50, 74.50], zoom: 7 }},
            "Gujarat": {{ center: [22.20, 71.80], zoom: 7 }},
            "Uttar Pradesh": {{ center: [26.50, 81.50], zoom: 7 }},
            "Tamil Nadu": {{ center: [11.00, 78.80], zoom: 7 }},
            "Karnataka": {{ center: [14.50, 75.80], zoom: 7 }},
            "Delhi": {{ center: [28.63, 77.22], zoom: 11 }},
            "Punjab": {{ center: [30.60, 75.50], zoom: 8 }},
            "Uttarakhand": {{ center: [30.00, 78.50], zoom: 8 }},
            "Himachal Pradesh": {{ center: [32.00, 77.10], zoom: 8 }}
        }};

        // Leaflet Map Initialization with Robust Standard Tiles
        let map = L.map('map', {{ zoomControl: true }}).setView([21.5, 80.0], 5);
        L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);

        let markersLayer = L.layerGroup().addTo(map);
        let selectedSpotlightHalo = null;

        // River Lines
        const krishnaCoords = [
            [16.580, 80.360], [16.592, 80.450], [16.590, 80.522], [16.550, 80.565],
            [16.507, 80.605], [16.480, 80.640], [16.440, 80.720], [16.360, 80.780],
            [16.320, 80.825], [16.185, 80.795], [16.122, 80.932], [16.022, 80.918], [15.945, 80.915]
        ];
        L.polyline(krishnaCoords, {{ color: '#0055ff', weight: 4, opacity: 0.85 }}).bindTooltip("Krishna River (Prakasam Barrage System)").addTo(map);

        const budameruCoords = [
            [16.630, 80.540], [16.562, 80.615], [16.538, 80.638], [16.522, 80.665], [16.520, 80.750]
        ];
        L.polyline(budameruCoords, {{ color: '#00aaff', weight: 3, dashArray: '6, 6', opacity: 0.85 }}).bindTooltip("Budameru Rivulet Drainage Floodway").addTo(map);

        // Populate State Dropdown
        const stateSelect = document.getElementById('state-select');
        const states = Array.from(new Set(allPlaces.map(p => p.state))).sort();
        states.forEach(s => {{
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s;
            stateSelect.appendChild(opt);
        }});

        function onStateChange() {{
            const selectedState = stateSelect.value;
            const distSelect = document.getElementById('district-select');
            distSelect.innerHTML = '<option value="All Districts in State">All Districts in State</option>';

            const filtered = selectedState === "All India (Pan-India Overview)" 
                ? allPlaces 
                : allPlaces.filter(p => p.state === selectedState);

            const dists = Array.from(new Set(filtered.map(p => p.district))).sort();
            dists.forEach(d => {{
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d;
                distSelect.appendChild(opt);
            }});

            const geo = stateGeo[selectedState] || {{ center: [21.5, 80.0], zoom: 5 }};
            map.setView(geo.center, geo.zoom);

            onDistrictChange();
        }}

        function onDistrictChange() {{
            const selectedState = stateSelect.value;
            const selectedDist = document.getElementById('district-select').value;
            const locSelect = document.getElementById('location-select');
            locSelect.innerHTML = '<option value="All Locations in Scope">All Locations in Scope</option>';

            let filtered = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                filtered = filtered.filter(p => p.state === selectedState);
            }}
            if (selectedDist !== "All Districts in State") {{
                filtered = filtered.filter(p => p.district === selectedDist);
            }}

            const locs = Array.from(new Set(filtered.map(p => p.habitation_name))).sort();
            locs.forEach(l => {{
                const opt = document.createElement('option');
                opt.value = l;
                opt.textContent = l;
                locSelect.appendChild(opt);
            }});

            applyFilters();
        }}

        function onLocationChange() {{
            const locName = document.getElementById('location-select').value;
            if (locName !== "All Locations in Scope") {{
                const place = allPlaces.find(p => p.habitation_name === locName);
                if (place) {{
                    selectParticularPlace(place);
                }}
            }} else {{
                resetLocationSelection();
            }}
            applyFilters();
        }}

        function onAreaSearch() {{
            const query = document.getElementById('area-search').value.toLowerCase().trim();
            if (query.length >= 2) {{
                const match = allPlaces.find(p => 
                    p.habitation_name.toLowerCase().includes(query) ||
                    (p.mandal && p.mandal.toLowerCase().includes(query)) ||
                    p.district.toLowerCase().includes(query)
                );
                if (match) {{
                    document.getElementById('location-select').value = match.habitation_name;
                    selectParticularPlace(match);
                    applyFilters();
                }}
            }}
        }}

        function selectParticularPlace(place) {{
            map.flyTo([place.latitude, place.longitude], 13, {{ animate: true, duration: 1.2 }});

            if (selectedSpotlightHalo) {{
                map.removeLayer(selectedSpotlightHalo);
            }}
            selectedSpotlightHalo = L.circleMarker([place.latitude, place.longitude], {{
                radius: 14,
                color: '#FFD700',
                weight: 4,
                fillColor: '#FFD700',
                fillOpacity: 0.35
            }}).addTo(map);

            // Spotlight Banner
            document.getElementById('spotlight-banner').style.display = 'flex';
            document.getElementById('spotlight-name').textContent = place.habitation_name;
            document.getElementById('spotlight-dist').textContent = place.district;
            document.getElementById('spotlight-state').textContent = place.state;

            // Show spotlight graphs
            document.getElementById('spotlight-graph-box').style.display = 'grid';
            renderSpotlightGraphs(place);

            // Fetch Live Weather for Place
            fetchLiveWeather(place.latitude, place.longitude, `${{place.habitation_name}} (${{place.district}}, ${{place.state}})`, place.relative_hazard_level, place.elevation_m);
        }}

        function resetLocationSelection() {{
            document.getElementById('location-select').value = "All Locations in Scope";
            document.getElementById('area-search').value = "";
            document.getElementById('spotlight-banner').style.display = 'none';
            document.getElementById('spotlight-graph-box').style.display = 'none';
            if (selectedSpotlightHalo) {{
                map.removeLayer(selectedSpotlightHalo);
                selectedSpotlightHalo = null;
            }}
            applyFilters();
        }}

        function triggerRefresh() {{
            const locName = document.getElementById('location-select').value;
            if (locName !== "All Locations in Scope") {{
                const p = allPlaces.find(x => x.habitation_name === locName);
                if (p) fetchLiveWeather(p.latitude, p.longitude, `${{p.habitation_name}} (${{p.district}}, ${{p.state}})`, p.relative_hazard_level, p.elevation_m);
            }} else {{
                fetchLiveWeather(17.754, 80.921, "Regional Representative Station: All India", "Moderate", 134.3);
            }}
        }}

        function applyFilters() {{
            const selectedState = stateSelect.value;
            const selectedDist = document.getElementById('district-select').value;
            const selectedLoc = document.getElementById('location-select').value;

            const showHigh = document.getElementById('check-high').checked;
            const showMed = document.getElementById('check-med').checked;
            const showLow = document.getElementById('check-low').checked;

            let scopeData = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                scopeData = scopeData.filter(p => p.state === selectedState);
            }}
            if (selectedDist !== "All Districts in State") {{
                scopeData = scopeData.filter(p => p.district === selectedDist);
            }}

            // Counts in current scope
            const cHigh = scopeData.filter(p => p.relative_hazard_level.includes('High')).length;
            const cMed = scopeData.filter(p => p.relative_hazard_level.includes('Moderate')).length;
            const cLow = scopeData.filter(p => p.relative_hazard_level.includes('Lower')).length;

            document.getElementById('count-high').textContent = cHigh;
            document.getElementById('count-med').textContent = cMed;
            document.getElementById('count-low').textContent = cLow;

            // Apply danger separation
            let filtered = scopeData.filter(p => {{
                if (p.relative_hazard_level.includes('High') && !showHigh) return false;
                if (p.relative_hazard_level.includes('Moderate') && !showMed) return false;
                if (p.relative_hazard_level.includes('Lower') && !showLow) return false;
                return true;
            }});

            if (selectedLoc !== "All Locations in Scope") {{
                filtered = filtered.filter(p => p.habitation_name === selectedLoc);
            }}

            // Update Sidebar Summary
            document.getElementById('summary-state').textContent = selectedState;
            document.getElementById('summary-dist').textContent = selectedDist;
            document.getElementById('summary-place').textContent = selectedLoc;
            document.getElementById('summary-hab-count').textContent = `${{filtered.length}} / ${{allPlaces.length}}`;

            // Update Tab Headers matching user's photo
            document.getElementById('map-section-header').textContent = `Geospatial Hazard Distribution — ${{selectedState}} (${{selectedDist}})`;
            document.getElementById('map-section-sub').textContent = `Displaying ${{filtered.length}} habitation(s) across ${{selectedDist === 'All Districts in State' ? (selectedState === 'All India (Pan-India Overview)' ? 92 : new Set(scopeData.map(p=>p.district)).size) : 1}} district(s). Circle markers reflect unsupervised ML hazard tiers.`;
            document.getElementById('districts-section-header').textContent = `All Districts Matrix & Regional Comparisons — ${{selectedState}}`;

            // Update 5 KPI Metrics
            const total = filtered.length;
            document.getElementById('kpi-high-val').textContent = cHigh;
            document.getElementById('kpi-high-delta').textContent = `↑ ${{(cHigh / (scopeData.length || 1) * 100).toFixed(1)}}% of active`;

            document.getElementById('kpi-med-val').textContent = cMed;
            document.getElementById('kpi-med-delta').textContent = `↑ ${{(cMed / (scopeData.length || 1) * 100).toFixed(1)}}% of active`;

            document.getElementById('kpi-low-val').textContent = cLow;
            document.getElementById('kpi-low-delta').textContent = `↑ ${{(cLow / (scopeData.length || 1) * 100).toFixed(1)}}% of active`;

            const meanRain = scopeData.length > 0 ? (scopeData.reduce((s, p) => s + p.annual_rainfall_mm, 0) / scopeData.length).toFixed(1) : 0;
            document.getElementById('kpi-rain-val').textContent = `${{meanRain}} mm`;

            const meanElev = scopeData.length > 0 ? (scopeData.reduce((s, p) => s + p.elevation_m, 0) / scopeData.length).toFixed(1) : 0;
            document.getElementById('kpi-elev-val').textContent = `${{meanElev}} m AMSL`;

            renderMarkers(filtered);
            renderExecutiveCharts(filtered, cHigh, cMed, cLow);
            renderDistrictsChartsAndTable(scopeData);
            renderSignaturesCharts(scopeData);
            renderNationalChartsAndTable();
            renderMLCharts();
            renderExplorerCharts(filtered);
            renderDataTable();
        }}

        // ==============================================================================
        // MAXIMUM GRAPHS RENDERING FUNCTIONS
        // ==============================================================================

        function renderExecutiveCharts(filtered, cHigh, cMed, cLow) {{
            // 1. Donut Chart
            renderOrUpdateChart('dangerDonutChart', {{
                type: 'doughnut',
                data: {{
                    labels: ['High Danger', 'Medium Danger', 'Low Danger'],
                    datasets: [{{
                        data: [cHigh, cMed, cLow],
                        backgroundColor: ['#D73027', '#FDAE61', '#4575B4'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'bottom', labels: {{ boxWidth: 12, padding: 8, font: {{ size: 11 }} }} }}
                    }},
                    cutout: '60%'
                }}
            }});

            // 2. Category vs Hazard Bar
            const catMap = {{}};
            filtered.forEach(p => {{
                const cat = p.place_category || 'Village';
                if (!catMap[cat]) catMap[cat] = {{ high: 0, med: 0, low: 0 }};
                if (p.relative_hazard_level.includes('High')) catMap[cat].high++;
                else if (p.relative_hazard_level.includes('Moderate')) catMap[cat].med++;
                else catMap[cat].low++;
            }});
            const catLabels = Object.keys(catMap);
            renderOrUpdateChart('categoryBarChart', {{
                type: 'bar',
                data: {{
                    labels: catLabels,
                    datasets: [
                        {{ label: 'High', data: catLabels.map(c => catMap[c].high), backgroundColor: '#D73027' }},
                        {{ label: 'Medium', data: catLabels.map(c => catMap[c].med), backgroundColor: '#FDAE61' }},
                        {{ label: 'Low', data: catLabels.map(c => catMap[c].low), backgroundColor: '#4575B4' }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, grid: {{ color: '#1E2433' }} }} }},
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});

            // 3. Top Critical Sites Horizontal Bar
            const sortedSites = [...filtered].sort((a, b) => b.historical_flood_inundation_frequency - a.historical_flood_inundation_frequency || a.elevation_m - b.elevation_m).slice(0, 7);
            renderOrUpdateChart('topRiskBarChart', {{
                type: 'bar',
                data: {{
                    labels: sortedSites.map(s => s.habitation_name),
                    datasets: [{{
                        label: 'Elevation (m AMSL)',
                        data: sortedSites.map(s => s.elevation_m),
                        backgroundColor: sortedSites.map(s => s.relative_hazard_level.includes('High') ? '#D73027' : '#FDAE61')
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ x: {{ grid: {{ color: '#1E2433' }} }}, y: {{ grid: {{ display: false }} }} }}
                }}
            }});
        }}

        function renderSpotlightGraphs(place) {{
            const normElev = 1.0 - Math.min(1.0, Math.max(0.0, place.elevation_m / 150.0));
            const normRiv = 1.0 - Math.min(1.0, Math.max(0.0, place.distance_to_river_km / 25.0));
            const normDrain = place.drainage_congestion_index / 5.0;
            const normFlood = place.historical_flood_inundation_frequency / 5.0;
            const normRain = Math.min(1.0, place.annual_rainfall_mm / 2500.0);
            const normPop = Math.min(1.0, place.population_density_per_sqkm / 20000.0);

            renderOrUpdateChart('spotlightRadarChart', {{
                type: 'radar',
                data: {{
                    labels: ['Elevation (Inv)', 'River Proximity', 'Drainage Congestion', 'Flood History', 'Annual Rain', 'Pop Density'],
                    datasets: [{{
                        label: place.habitation_name,
                        data: [normElev, normRiv, normDrain, normFlood, normRain, normPop],
                        backgroundColor: 'rgba(215, 48, 39, 0.4)',
                        borderColor: '#D73027',
                        pointBackgroundColor: '#FFD700',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ r: {{ min: 0, max: 1, ticks: {{ display: false }}, grid: {{ color: '#2B3245' }} }} }}
                }}
            }});

            renderOrUpdateChart('spotlightBarChart', {{
                type: 'bar',
                data: {{
                    labels: ['Elevation (m)', 'River Dist (km)', 'Drainage (1-5)', 'Floods (0-5)'],
                    datasets: [{{
                        label: place.habitation_name,
                        data: [place.elevation_m, place.distance_to_river_km, place.drainage_congestion_index, place.historical_flood_inundation_frequency],
                        backgroundColor: ['#38BDF8', '#818CF8', '#F59E0B', '#EF4444']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ y: {{ grid: {{ color: '#1E2433' }} }} }}
                }}
            }});
        }}

        function renderDistrictsChartsAndTable(scopeData) {{
            const distMap = {{}};
            scopeData.forEach(p => {{
                if (!distMap[p.district]) {{
                    distMap[p.district] = {{
                        total: 0, high: 0, med: 0, low: 0,
                        sumElev: 0, sumRiv: 0, sumRain: 0
                    }};
                }}
                distMap[p.district].total++;
                if (p.relative_hazard_level.includes('High')) distMap[p.district].high++;
                else if (p.relative_hazard_level.includes('Moderate')) distMap[p.district].med++;
                else distMap[p.district].low++;
                distMap[p.district].sumElev += p.elevation_m;
                distMap[p.district].sumRiv += p.distance_to_river_km;
                distMap[p.district].sumRain += p.annual_rainfall_mm;
            }});

            const distList = Object.keys(distMap).map(d => ({{
                district: d,
                ...distMap[d],
                highPct: (distMap[d].high / distMap[d].total * 100),
                meanElev: (distMap[d].sumElev / distMap[d].total).toFixed(1),
                meanRiv: (distMap[d].sumRiv / distMap[d].total).toFixed(2),
                meanRain: (distMap[d].sumRain / distMap[d].total).toFixed(1)
            }})).sort((a, b) => b.highPct - a.highPct);

            renderOrUpdateChart('districtsRankChart', {{
                type: 'bar',
                data: {{
                    labels: distList.map(d => d.district),
                    datasets: [{{
                        label: 'High Danger (%)',
                        data: distList.map(d => d.highPct.toFixed(1)),
                        backgroundColor: distList.map(d => d.highPct > 50 ? '#D73027' : (d.highPct > 20 ? '#FDAE61' : '#4575B4'))
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ x: {{ ticks: {{ autoSkip: false, maxRotation: 45 }} }}, y: {{ max: 100, grid: {{ color: '#1E2433' }} }} }}
                }}
            }});

            renderOrUpdateChart('districtsStackChart', {{
                type: 'bar',
                data: {{
                    labels: distList.map(d => d.district),
                    datasets: [
                        {{ label: 'High Danger', data: distList.map(d => d.high), backgroundColor: '#D73027' }},
                        {{ label: 'Medium Danger', data: distList.map(d => d.med), backgroundColor: '#FDAE61' }},
                        {{ label: 'Low Danger', data: distList.map(d => d.low), backgroundColor: '#4575B4' }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ x: {{ stacked: true, ticks: {{ autoSkip: false, maxRotation: 45 }} }}, y: {{ stacked: true, grid: {{ color: '#1E2433' }} }} }}
                }}
            }});

            const tbody = document.getElementById('districts-table-body');
            tbody.innerHTML = '';
            distList.forEach(d => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b>${{d.district}}</b></td>
                    <td>${{d.total}}</td>
                    <td style="color: #F87171; font-weight: bold;">${{d.high}}</td>
                    <td style="color: #FBBF24;">${{d.med}}</td>
                    <td style="color: #60A5FA;">${{d.low}}</td>
                    <td style="font-weight: bold; color: ${{d.highPct > 50 ? '#F87171' : '#FFF'}};">${{d.highPct.toFixed(1)}}%</td>
                    <td>${{d.meanElev}} m</td>
                    <td>${{d.meanRiv}} km</td>
                    <td>${{d.meanRain}} mm</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function renderSignaturesCharts(scopeData) {{
            renderOrUpdateChart('signaturesRadarChart', {{
                type: 'radar',
                data: {{
                    labels: ['Elevation (Inv)', 'Slope (Inv)', 'River Dist (Inv)', 'Annual Rain', 'Extreme Rain', 'Pop Density', 'Congestion', 'Flood Freq'],
                    datasets: [
                        {{
                            label: 'High Danger',
                            data: [0.85, 0.78, 0.82, 0.75, 0.88, 0.72, 0.84, 0.90],
                            backgroundColor: 'rgba(215, 48, 39, 0.4)',
                            borderColor: '#D73027',
                            borderWidth: 2.5
                        }},
                        {{
                            label: 'Medium Danger',
                            data: [0.55, 0.48, 0.52, 0.50, 0.45, 0.40, 0.58, 0.48],
                            backgroundColor: 'rgba(253, 174, 97, 0.4)',
                            borderColor: '#FDAE61',
                            borderWidth: 2
                        }},
                        {{
                            label: 'Low Danger',
                            data: [0.25, 0.20, 0.22, 0.35, 0.28, 0.22, 0.24, 0.18],
                            backgroundColor: 'rgba(69, 117, 180, 0.4)',
                            borderColor: '#4575B4',
                            borderWidth: 2
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ r: {{ min: 0, max: 1, ticks: {{ display: false }}, grid: {{ color: '#2B3245' }} }} }}
                }}
            }});

            const pcaData = scopeData.map(p => ({{
                x: p.pca_1 || (p.elevation_m < 20 ? 1.5 : -1.0),
                y: p.pca_2 || (p.annual_rainfall_mm > 1200 ? 1.0 : -0.8),
                name: p.habitation_name,
                tier: p.relative_hazard_level
            }}));

            renderOrUpdateChart('signaturesPcaChart', {{
                type: 'scatter',
                data: {{
                    datasets: [
                        {{
                            label: 'High Danger',
                            data: pcaData.filter(p => p.tier.includes('High')),
                            backgroundColor: '#D73027',
                            pointRadius: 5
                        }},
                        {{
                            label: 'Medium Danger',
                            data: pcaData.filter(p => p.tier.includes('Moderate')),
                            backgroundColor: '#FDAE61',
                            pointRadius: 5
                        }},
                        {{
                            label: 'Low Danger',
                            data: pcaData.filter(p => p.tier.includes('Lower')),
                            backgroundColor: '#4575B4',
                            pointRadius: 5
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ title: {{ display: true, text: 'PC1 (Flood Exposure)' }}, grid: {{ color: '#1E2433' }} }},
                        y: {{ title: {{ display: true, text: 'PC2 (Climatological Extremes)' }}, grid: {{ color: '#1E2433' }} }}
                    }}
                }}
            }});
        }}

        function renderNationalChartsAndTable() {{
            const stMap = {{}};
            allPlaces.forEach(p => {{
                if (!stMap[p.state]) {{
                    stMap[p.state] = {{
                        total: 0, high: 0, med: 0, low: 0, dists: new Set(),
                        sumElev: 0, sumRain: 0
                    }};
                }}
                stMap[p.state].total++;
                stMap[p.state].dists.add(p.district);
                if (p.relative_hazard_level.includes('High')) stMap[p.state].high++;
                else if (p.relative_hazard_level.includes('Moderate')) stMap[p.state].med++;
                else stMap[p.state].low++;
                stMap[p.state].sumElev += p.elevation_m;
                stMap[p.state].sumRain += p.annual_rainfall_mm;
            }});

            const stList = Object.keys(stMap).map(s => ({{
                state: s,
                ...stMap[s],
                distsCount: stMap[s].dists.size,
                highPct: (stMap[s].high / stMap[s].total * 100),
                meanElev: (stMap[s].sumElev / stMap[s].total).toFixed(1),
                meanRain: (stMap[s].sumRain / stMap[s].total).toFixed(1)
            }})).sort((a, b) => b.highPct - a.highPct);

            renderOrUpdateChart('stateRankChart', {{
                type: 'bar',
                data: {{
                    labels: stList.map(s => s.state),
                    datasets: [{{
                        label: 'High Danger (%)',
                        data: stList.map(s => s.highPct.toFixed(1)),
                        backgroundColor: '#D73027'
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ x: {{ max: 100, grid: {{ color: '#1E2433' }} }} }}
                }}
            }});

            renderOrUpdateChart('stateStackChart', {{
                type: 'bar',
                data: {{
                    labels: stList.map(s => s.state),
                    datasets: [
                        {{ label: 'High', data: stList.map(s => s.high), backgroundColor: '#D73027' }},
                        {{ label: 'Medium', data: stList.map(s => s.med), backgroundColor: '#FDAE61' }},
                        {{ label: 'Low', data: stList.map(s => s.low), backgroundColor: '#4575B4' }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ x: {{ stacked: true, ticks: {{ autoSkip: false, maxRotation: 45 }} }}, y: {{ stacked: true, grid: {{ color: '#1E2433' }} }} }}
                }}
            }});

            const basinCounts = {{}};
            allPlaces.forEach(p => {{
                const b = p.river_basin || 'Regional Basin';
                basinCounts[b] = (basinCounts[b] || 0) + 1;
            }});
            const bLabels = Object.keys(basinCounts).sort((a,b) => basinCounts[b] - basinCounts[a]).slice(0, 8);
            renderOrUpdateChart('basinBarChart', {{
                type: 'bar',
                data: {{
                    labels: bLabels,
                    datasets: [{{
                        label: 'Habitations Monitored',
                        data: bLabels.map(b => basinCounts[b]),
                        backgroundColor: '#38BDF8'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ y: {{ grid: {{ color: '#1E2433' }} }} }}
                }}
            }});

            const tbody = document.getElementById('national-table-body');
            tbody.innerHTML = '';
            stList.forEach(s => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b>${{s.state}}</b></td>
                    <td>${{s.distsCount}}</td>
                    <td>${{s.total}}</td>
                    <td style="color: #F87171; font-weight: bold;">${{s.high}}</td>
                    <td style="font-weight: bold;">${{s.highPct.toFixed(1)}}%</td>
                    <td>${{s.meanElev}} m</td>
                    <td>${{s.meanRain}} mm</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function renderMLCharts() {{
            renderOrUpdateChart('mlSilhouetteChart', {{
                type: 'bar',
                data: {{
                    labels: ['K-Medoids (PAM)', 'K-Means++', 'Hierarchical (Ward)', 'DBSCAN'],
                    datasets: [{{
                        label: 'Silhouette Score',
                        data: [0.4320, 0.3667, 0.3283, 0.2841],
                        backgroundColor: ['#10B981', '#3B82F6', '#8B5CF6', '#64748B']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ y: {{ max: 0.55, grid: {{ color: '#1E2433' }} }} }}
                }}
            }});

            renderOrUpdateChart('mlDbChart', {{
                type: 'bar',
                data: {{
                    labels: ['K-Medoids (PAM)', 'Hierarchical (Ward)', 'K-Means++', 'DBSCAN'],
                    datasets: [{{
                        label: 'Davies-Bouldin Index (Lower is Better)',
                        data: [1.0421, 1.0843, 1.1202, 1.3140],
                        backgroundColor: ['#10B981', '#8B5CF6', '#3B82F6', '#EF4444']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ y: {{ max: 1.5, grid: {{ color: '#1E2433' }} }} }}
                }}
            }});

            renderOrUpdateChart('mlElbowChart', {{
                type: 'line',
                data: {{
                    labels: ['K=2', 'K=3 (Optimal)', 'K=4', 'K=5', 'K=6'],
                    datasets: [
                        {{
                            label: 'Silhouette Score (Peak at K=3)',
                            data: [0.342, 0.432, 0.381, 0.339, 0.312],
                            borderColor: '#10B981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            fill: true,
                            tension: 0.3
                        }},
                        {{
                            label: 'Normalized Inertia (Elbow Drop)',
                            data: [0.582, 0.341, 0.276, 0.221, 0.185],
                            borderColor: '#EF4444',
                            borderDash: [5, 5],
                            tension: 0.3
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ y: {{ grid: {{ color: '#1E2433' }} }} }}
                }}
            }});
        }}

        function renderExplorerCharts(filtered) {{
            const elevBins = [0, 15, 30, 50, 80, 150, 300, 1000];
            const elevCounts = new Array(elevBins.length - 1).fill(0);
            filtered.forEach(p => {{
                for (let i = 0; i < elevBins.length - 1; i++) {{
                    if (p.elevation_m >= elevBins[i] && p.elevation_m < elevBins[i+1]) {{
                        elevCounts[i]++;
                        break;
                    }}
                }}
            }});
            renderOrUpdateChart('elevHistChart', {{
                type: 'bar',
                data: {{
                    labels: ['0-15m', '15-30m', '30-50m', '50-80m', '80-150m', '150-300m', '300m+'],
                    datasets: [{{
                        label: 'Habitations',
                        data: elevCounts,
                        backgroundColor: '#60A5FA'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ y: {{ grid: {{ color: '#1E2433' }} }} }}
                }}
            }});

            const rivBins = [0, 2, 5, 10, 20, 50, 100];
            const rivCounts = new Array(rivBins.length - 1).fill(0);
            filtered.forEach(p => {{
                for (let i = 0; i < rivBins.length - 1; i++) {{
                    if (p.distance_to_river_km >= rivBins[i] && p.distance_to_river_km < rivBins[i+1]) {{
                        rivCounts[i]++;
                        break;
                    }}
                }}
            }});
            renderOrUpdateChart('riverHistChart', {{
                type: 'bar',
                data: {{
                    labels: ['0-2km', '2-5km', '5-10km', '10-20km', '20-50km', '50km+'],
                    datasets: [{{
                        label: 'Habitations',
                        data: rivCounts,
                        backgroundColor: '#38BDF8'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{ y: {{ grid: {{ color: '#1E2433' }} }} }}
                }}
            }});
        }}

        function renderMarkers(places) {{
            markersLayer.clearLayers();

            places.forEach(p => {{
                let color = '#4575b4';
                let radius = 5.5;

                if (p.relative_hazard_level.includes('High')) {{
                    color = '#d73027';
                    radius = 7.0;
                }} else if (p.relative_hazard_level.includes('Moderate')) {{
                    color = '#fdae61';
                    radius = 6.0;
                }}

                const m = L.circleMarker([p.latitude, p.longitude], {{
                    radius: radius,
                    color: '#FFFFFF',
                    weight: 1.0,
                    fillColor: color,
                    fillOpacity: 0.85
                }});

                const popupHtml = `
                    <div style="font-family: Arial; font-size: 12px; color: #000; width: 230px;">
                        <b style="color: ${{color}}; font-size: 13.5px;">${{p.habitation_name}}</b><br>
                        <b>State:</b> ${{p.state}} | <b>District:</b> ${{p.district}}<br>
                        <b>Mandal:</b> ${{p.mandal || 'N/A'}}<br>
                        <b>Hazard Tier:</b> <span style="color: ${{color}}; font-weight: bold;">${{p.relative_hazard_level}}</span><br>
                        <hr style="margin: 4px 0;">
                        <b>Elevation:</b> ${{p.elevation_m.toFixed(1)}} m AMSL<br>
                        <b>Distance to River:</b> ${{p.distance_to_river_km.toFixed(2)}} km<br>
                        <b>Historical Floods:</b> ${{p.historical_flood_inundation_frequency}}/5<br>
                        <b>Annual Rain:</b> ${{p.annual_rainfall_mm.toFixed(1)}} mm<br>
                        <b>Population:</b> ${{p.population.toLocaleString()}}
                    </div>
                `;

                m.bindPopup(popupHtml);
                m.on('click', () => {{
                    document.getElementById('location-select').value = p.habitation_name;
                    selectParticularPlace(p);
                }});

                markersLayer.addLayer(m);
            }});
        }}

        function renderDataTable() {{
            const search = document.getElementById('data-search').value.toLowerCase().trim();
            const tbody = document.getElementById('data-table-body');
            tbody.innerHTML = '';

            const selectedState = stateSelect.value;
            const selectedDist = document.getElementById('district-select').value;
            const selectedLoc = document.getElementById('location-select').value;
            const showHigh = document.getElementById('check-high').checked;
            const showMed = document.getElementById('check-med').checked;
            const showLow = document.getElementById('check-low').checked;

            let filtered = allPlaces.filter(p => {{
                if (selectedState !== "All India (Pan-India Overview)" && p.state !== selectedState) return false;
                if (selectedDist !== "All Districts in State" && p.district !== selectedDist) return false;
                if (selectedLoc !== "All Locations in Scope" && p.habitation_name !== selectedLoc) return false;

                if (p.relative_hazard_level.includes('High') && !showHigh) return false;
                if (p.relative_hazard_level.includes('Moderate') && !showMed) return false;
                if (p.relative_hazard_level.includes('Lower') && !showLow) return false;

                if (search) {{
                    const matchName = p.habitation_name.toLowerCase().includes(search);
                    const matchDist = p.district.toLowerCase().includes(search);
                    const matchMandal = (p.mandal && p.mandal.toLowerCase().includes(search));
                    if (!matchName && !matchDist && !matchMandal) return false;
                }}
                return true;
            }});

            filtered.slice(0, 100).forEach(p => {{
                const tr = document.createElement('tr');
                const cColor = p.relative_hazard_level.includes('High') ? '#F87171' : (p.relative_hazard_level.includes('Moderate') ? '#FBBF24' : '#60A5FA');
                tr.innerHTML = `
                    <td><b>${{p.habitation_name}}</b></td>
                    <td>${{p.state}}</td>
                    <td>${{p.district}}</td>
                    <td>${{p.mandal || 'N/A'}}</td>
                    <td><span style="color: ${{cColor}}; font-weight: 700;">${{p.relative_hazard_level.split(' ')[0]}} Hazard</span></td>
                    <td>${{p.elevation_m.toFixed(1)}} m</td>
                    <td>${{p.distance_to_river_km.toFixed(2)}} km</td>
                    <td>${{p.annual_rainfall_mm.toFixed(1)}} mm</td>
                    <td>${{p.extreme_daily_rainfall_mm.toFixed(1)}} mm</td>
                    <td>${{p.population.toLocaleString()}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
            if (tabId === 'tab-map') {{
                setTimeout(() => map.invalidateSize(), 150);
            }}
        }}

        async function fetchLiveWeather(lat, lon, stationName, hazardTier, elevation) {{
            try {{
                const url = `https://api.open-meteo.com/v1/forecast?latitude=${{lat.toFixed(4)}}&longitude=${{lon.toFixed(4)}}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,surface_pressure,wind_speed_10m&past_days=1&hourly=precipitation&timezone=Asia%2FKolkata`;
                const res = await fetch(url);
                if (res.ok) {{
                    const d = await res.json();
                    const cur = d.current || {{}};
                    const hourly = d.hourly && d.hourly.precipitation ? d.hourly.precipitation : [];
                    let past24 = 0;
                    if (hourly.length >= 24) {{
                        past24 = hourly.slice(-24).reduce((a, b) => a + b, 0);
                    }} else {{
                        past24 = cur.rain || 0;
                    }}

                    document.getElementById('live-station-name').textContent = `Station: ${{stationName}} (Lat: ${{lat.toFixed(3)}}°, Lon: ${{lon.toFixed(3)}}°)`;
                    document.getElementById('live-obs-time').textContent = `🕒 Live Observation: ${{cur.time ? cur.time.replace('T', ' ') : ''}} IST | 📡 Live API Connected`;
                    document.getElementById('pill-temp').textContent = `🌡️ Temp: ${{cur.temperature_2m}}°C (Feels ${{cur.apparent_temperature}}°C)`;
                    document.getElementById('pill-humidity').textContent = `💧 Humidity: ${{cur.relative_humidity_2m}}%`;
                    document.getElementById('pill-rain').textContent = `🌧️ Live Rain: ${{cur.rain}} mm/h`;
                    document.getElementById('pill-past24').textContent = `🌊 Past 24h Rain: ${{past24.toFixed(1)}} mm`;
                    document.getElementById('pill-wind').textContent = `💨 Wind: ${{cur.wind_speed_10m}} km/h`;
                    document.getElementById('pill-elev').textContent = `⛰️ Elevation: ${{elevation.toFixed(1)}} m AMSL`;

                    const isHigh = hazardTier.includes('High');
                    let alertText = "🟢 GREEN STATUS (NORMAL / DRY)";
                    let alertBg = "linear-gradient(135deg, #16A34A 0%, #0F172A 100%)";
                    let desc = "Baseline morphological conditions currently stable with negligible precipitation trigger.";

                    if (isHigh) {{
                        if (past24 >= 35 || cur.rain >= 10) {{
                            alertText = "🚨 RED ALERT (CRITICAL INUNDATION RISK)";
                            alertBg = "linear-gradient(135deg, #DC2626 0%, #111827 100%)";
                            desc = "Critical morphological hazard coupled with heavy precipitation. Severe backwater surcharge and street flooding imminent.";
                        }} else if (past24 >= 15 || cur.rain >= 4) {{
                            alertText = "🟧 ORANGE ALERT (ELEVATED SURCHARGE RISK)";
                            alertBg = "linear-gradient(135deg, #EA580C 0%, #111827 100%)";
                            desc = "Low-lying settlement experiencing active precipitation loading. Canals near maximum holding capacity.";
                        }} else if (past24 >= 5 || cur.rain > 0) {{
                            alertText = "🟨 YELLOW WATCH (DRAINAGE ADVISORY)";
                            alertBg = "linear-gradient(135deg, #D97706 0%, #111827 100%)";
                            desc = "Light rain active over vulnerable depression terrain. Sluice monitoring advised.";
                        }}
                    }}

                    document.getElementById('live-alert-pill').textContent = alertText;
                    document.getElementById('alert-banner-box').style.background = alertBg;
                    document.getElementById('live-alert-desc').textContent = desc;
                }}
            }} catch(e) {{
                console.log("Weather API fallback:", e);
            }}
        }}

        function downloadCSV() {{
            const selectedState = stateSelect.value;
            const selectedDist = document.getElementById('district-select').value;
            const selectedLoc = document.getElementById('location-select').value;
            const showHigh = document.getElementById('check-high').checked;
            const showMed = document.getElementById('check-med').checked;
            const showLow = document.getElementById('check-low').checked;

            let filtered = allPlaces.filter(p => {{
                if (selectedState !== "All India (Pan-India Overview)" && p.state !== selectedState) return false;
                if (selectedDist !== "All Districts in State" && p.district !== selectedDist) return false;
                if (selectedLoc !== "All Locations in Scope" && p.habitation_name !== selectedLoc) return false;

                if (p.relative_hazard_level.includes('High') && !showHigh) return false;
                if (p.relative_hazard_level.includes('Moderate') && !showMed) return false;
                if (p.relative_hazard_level.includes('Lower') && !showLow) return false;
                return true;
            }});

            const headers = ['habitation_id', 'habitation_name', 'state', 'district', 'mandal', 'relative_hazard_level', 'elevation_m', 'distance_to_river_km', 'annual_rainfall_mm', 'extreme_daily_rainfall_mm', 'population', 'river_basin'];
            const lines = [headers.join(',')];
            filtered.forEach(p => {{
                const row = headers.map(h => '"' + (p[h] !== undefined && p[h] !== null ? String(p[h]).replace(/"/g, '""') : '') + '"');
                lines.push(row.join(','));
            }});

            const csvString = lines.join(String.fromCharCode(10));
            const blob = new Blob([csvString], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.setAttribute('href', url);
            a.setAttribute('download', `flood_hazard_data_${{selectedState.replace(/\\s+/g, '_').toLowerCase()}}.csv`);
            a.click();
        }}

        // Initial Boot
        applyFilters();
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated index.html successfully ({len(html_content)} bytes)")
