import pandas as pd
import json
import os

def generate_pixel_perfect_streamlit_html():
    df_path = 'data/processed/india_habitations_complete.csv'
    if not os.path.exists(df_path):
        df_path = '../data/processed/india_habitations_complete.csv'

    df = pd.read_csv(df_path)
    records = df.to_dict(orient='records')
    places_json = json.dumps(records, ensure_ascii=False)

    def load_table_json(path):
        if os.path.exists(path):
            t_df = pd.read_csv(path)
            return t_df.to_dict(orient='records')
        return []

    kmeans_data = load_table_json('outputs/tables/kmeans_comparison_table.csv')
    kmedoids_data = load_table_json('outputs/tables/kmedoids_comparison_table.csv')
    hier_data = load_table_json('outputs/tables/hierarchical_comparison_table.csv')
    master_data = load_table_json('outputs/tables/master_clustering_comparison.csv')

    kmeans_json = json.dumps(kmeans_data, ensure_ascii=False)
    kmedoids_json = json.dumps(kmedoids_data, ensure_ascii=False)
    hier_json = json.dumps(hier_data, ensure_ascii=False)
    master_json = json.dumps(master_data, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIH26191: Pan-India Flood Hazard & Real-Time Alert System</title>
    
    <!-- Leaflet & Plotly.js (Exact engine from Streamlit) -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
    
    <!-- Streamlit Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
        :root {{
            --bg-color: #0E1117;
            --sidebar-bg: #262730;
            --card-bg: #1A1F2C;
            --border-color: #2B3245;
            --text-main: #FAFAFA;
            --text-subdued: #94A3B8;
            --accent-red: #D73027;
            --accent-orange: #FDAE61;
            --accent-blue: #4575B4;
            --accent-green: #22C55E;
            --st-red: #FF4B4B;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Source Sans Pro', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}

        /* Streamlit Sidebar Style */
        aside {{
            width: 330px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            padding: 20px 16px;
            gap: 14px;
            overflow-y: auto;
            flex-shrink: 0;
        }}

        .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 4px;
        }}
        .sidebar-title {{
            font-size: 20px;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.3px;
        }}

        .control-label {{
            font-size: 13.5px;
            font-weight: 600;
            color: #E2E8F0;
            margin-bottom: 5px;
            display: block;
        }}

        select {{
            width: 100%;
            background-color: #0E1117;
            border: 1px solid #464B5C;
            color: #FFFFFF;
            padding: 9px 12px;
            border-radius: 8px;
            font-size: 13.5px;
            font-family: inherit;
            outline: none;
            transition: all 0.15s ease;
            cursor: pointer;
        }}
        select:focus {{
            border-color: #60A5FA;
            box-shadow: 0 0 0 1px #60A5FA;
        }}

        .danger-levels-card {{
            background-color: #1A1F2C;
            border: 1px solid #2B3245;
            border-radius: 8px;
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .danger-checkbox-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }}
        .danger-checkbox-item input[type="checkbox"] {{
            appearance: none;
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border: 2px solid #EF4444;
            border-radius: 4px;
            background-color: transparent;
            display: grid;
            place-content: center;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .danger-checkbox-item input[type="checkbox"]:checked {{
            background-color: #EF4444;
        }}
        .danger-checkbox-item input[type="checkbox"]:checked::before {{
            content: "";
            width: 10px;
            height: 6px;
            border-left: 2px solid white;
            border-bottom: 2px solid white;
            transform: rotate(-45deg) translate(1px, -1px);
        }}
        .danger-label-high {{
            color: #F87171;
            font-weight: 700;
        }}
        .danger-label-med {{
            color: #FBBF24;
            font-weight: 700;
        }}
        .danger-label-low {{
            color: #60A5FA;
            font-weight: 700;
        }}
        .search-box-wrap {{
            margin-top: 8px;
        }}
        .search-box-wrap input {{
            width: 100%;
            background-color: #0E1117;
            border: 1px solid #464B5C;
            color: #FFFFFF;
            padding: 9px 12px;
            border-radius: 8px;
            font-size: 13.5px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.15s ease;
        }}
        .search-box-wrap input:focus {{
            border-color: #60A5FA;
        }}
        .search-box-wrap input::placeholder {{
            color: #64748B;
        }}

        .btn-refresh {{
            background: #1E293B;
            border: 1px solid #464B5C;
            color: #E2E8F0;
            padding: 9px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s ease;
            width: 100%;
        }}
        .btn-refresh:hover {{
            background: #334155;
            color: #FFFFFF;
            border-color: #60A5FA;
        }}

        .sidebar-divider {{
            height: 1px;
            background-color: #383E4F;
            margin: 6px 0;
        }}

        .scope-summary {{
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid #383E4F;
            font-size: 12px;
            color: var(--text-subdued);
            line-height: 1.6;
        }}
        .scope-summary h4 {{
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 6px;
        }}

        /* Main Workspace Container */
        main {{
            flex: 1;
            background-color: var(--bg-color);
            overflow-y: auto;
            padding: 24px 32px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .main-header {{
            font-size: 26px;
            font-weight: 800;
            color: #60A5FA;
            margin-bottom: 2px;
            letter-spacing: -0.3px;
        }}
        .sub-header {{
            font-size: 13.5px;
            color: #94A3B8;
            margin-bottom: 12px;
        }}

        /* Streamlit Academic Disclaimer Box */
        .disclaimer-box {{
            background-color: #1E222D;
            border-left: 4px solid #F59E0B;
            padding: 10px 16px;
            border-radius: 6px;
            font-size: 12.5px;
            color: #FDE68A;
            line-height: 1.45;
        }}

        /* 5 Metric Cards Row */
        .metrics-row {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 14px;
        }}
        .metric-card {{
            background: #1A1F2C;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px 16px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .metric-label {{
            font-size: 13px;
            color: var(--text-subdued);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .metric-val {{
            font-size: 26px;
            font-weight: 800;
            color: #FFFFFF;
        }}
        .metric-delta {{
            font-size: 12px;
            color: var(--accent-green);
            font-weight: 600;
        }}

        /* Live Alert Banner */
        .live-alert-card {{
            background: linear-gradient(135deg, #16A34A 0%, #0F172A 100%);
            border-radius: 8px;
            padding: 16px 20px;
            color: #FFFFFF;
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
            font-size: 18px;
            font-weight: 800;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .alert-station {{
            font-size: 13.5px;
            color: #E2E8F0;
            opacity: 0.95;
        }}
        .alert-desc {{
            font-size: 14px;
            color: #F8FAFC;
            line-height: 1.45;
        }}
        .alert-pills-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 4px;
        }}
        .metric-pill {{
            background: rgba(255, 255, 255, 0.22);
            border-radius: 12px;
            padding: 5px 12px;
            font-size: 12px;
            font-weight: 600;
            color: #FFFFFF;
        }}

        /* Streamlit Tabs Navigation Bar */
        .tab-bar {{
            display: flex;
            gap: 8px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 2px;
            overflow-x: auto;
        }}
        .tab-button {{
            background: transparent;
            border: none;
            color: #94A3B8;
            font-size: 14px;
            font-weight: 600;
            padding: 10px 18px;
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
            color: #FFFFFF;
            border-bottom: 3px solid var(--st-red);
            background: rgba(255, 75, 75, 0.08);
        }}
        .tab-panel {{
            display: none;
            flex-direction: column;
            gap: 16px;
        }}
        .tab-panel.active {{
            display: flex;
        }}

        .tab-section-header {{
            font-size: 19px;
            font-weight: 700;
            color: #FFFFFF;
        }}
        .tab-section-sub {{
            font-size: 13.5px;
            color: var(--text-subdued);
            margin-top: -6px;
            margin-bottom: 6px;
        }}

        #map {{
            height: 560px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}

        .chart-card {{
            background: #161922;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .chart-header {{
            font-size: 14.5px;
            font-weight: 700;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        /* Tables */
        .table-wrap {{
            overflow-x: auto;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: #161922;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}
        th {{
            background: #11141C;
            color: #94A3B8;
            font-weight: 700;
            padding: 10px 14px;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}
        td {{
            padding: 9px 14px;
            border-bottom: 1px solid #1E2330;
            color: #E2E8F0;
            white-space: nowrap;
        }}
        tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}

        .badge-red {{
            background: rgba(215, 48, 39, 0.25);
            color: #F87171;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 700;
        }}
        .badge-orange {{
            background: rgba(253, 174, 97, 0.25);
            color: #FBBF24;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 700;
        }}
        .badge-blue {{
            background: rgba(69, 117, 180, 0.25);
            color: #60A5FA;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 700;
        }}

        .search-input {{
            background-color: #0E1117;
            border: 1px solid var(--border-color);
            color: #FFFFFF;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            outline: none;
            width: 280px;
        }}
        .search-input:focus {{
            border-color: #60A5FA;
        }}

        .btn-download {{
            background: #1E293B;
            border: 1px solid var(--border-color);
            color: #60A5FA;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
            transition: all 0.2s ease;
        }}
        .btn-download:hover {{
            background: #2563EB;
            color: #FFFFFF;
            border-color: #2563EB;
        }}
    </style>
</head>
<body>

    <!-- Streamlit-Style Sidebar: Clean 4 Cascading Dropdowns -->
    <aside>
        <div class="sidebar-brand">
            <span style="font-size: 32px;">🌊</span>
            <div class="sidebar-title">National & State Navigation</div>
        </div>

        <!-- 1. State Selector -->
        <div>
            <label class="control-label" for="state-select">🇮🇳 1. Select State / Territory:</label>
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
            <div class="danger-levels-card">
                <label class="danger-checkbox-item">
                    <input type="checkbox" id="check-high" checked onchange="onDangerFilterChange()">
                    <span class="danger-label-high">🔴 High Danger (<span id="count-high">144</span>)</span>
                </label>
                <label class="danger-checkbox-item">
                    <input type="checkbox" id="check-medium" checked onchange="onDangerFilterChange()">
                    <span class="danger-label-med">🟡 Medium Danger (<span id="count-medium">18</span>)</span>
                </label>
                <label class="danger-checkbox-item">
                    <input type="checkbox" id="check-low" checked onchange="onDangerFilterChange()">
                    <span class="danger-label-low">🔵 Low Danger (<span id="count-low">67</span>)</span>
                </label>
            </div>
        </div>

        <!-- 4. Select Particular Location / Area -->
        <div>
            <label class="control-label" for="place-select">📍 4. Select Particular Location / Area</label>
            <select id="place-select" onchange="onPlaceChange()">
                <option value="All Locations in Scope">All Locations in Scope</option>
            </select>
            <div class="search-box-wrap">
                <input type="text" id="area-search" placeholder="🔍 Type to search area / village..." oninput="onAreaSearch(this.value)">
            </div>
        </div>

        <div class="sidebar-divider"></div>

        <button class="btn-refresh" onclick="triggerRefresh()">
            🔄 Refresh Live Real-Time Weather Data
        </button>

        <div class="sidebar-divider"></div>

        <div class="scope-summary">
            <h4>Active Scope Summary</h4>
            <b>State:</b> <span id="summary-state">All India (Pan-India Overview)</span><br>
            <b>District:</b> <span id="summary-dist">All Districts in State</span><br>
            <b>Location / Area:</b> <span id="summary-place">All Locations in Scope</span><br>
            <b>Habitations Active:</b> <span id="summary-hab-count">229 / 229</span><br>
            <b>Districts in State:</b> <span id="summary-dist-count">92</span><br>
            <b>Elevation Model:</b> Copernicus DEM 90m<br>
            <b>Climatology:</b> IMD 24-Yr Grid Normals<br>
            <b>Real-Time Feed:</b> Open-Meteo Live API
        </div>
    </aside>

    <!-- Main Content Area -->
    <main>
        <!-- Header Section -->
        <div>
            <div class="main-header">
                🌊 Hazard-Based Red-Zone Identification for Vulnerable Habitations Using Clustering
            </div>
            <div class="sub-header">
                <b>Project ID: SIH26191</b> | <b>Coverage: Pan-India Multi-State System</b> | <b>Real-Time Live Weather & Flood Alerts</b> | B.Tech ML Project
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
                <div class="metric-delta" id="kpi-rain-delta">↑ Max 440 mm/day</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">⛰️ Mean Elevation</div>
                <div class="metric-val" id="kpi-elev-val">134.3 m AMSL</div>
                <div class="metric-delta" id="kpi-elev-delta">↑ Min 0 m</div>
            </div>
        </div>

        <!-- Live Real-Time Weather Section -->
        <div class="live-alert-card" id="alert-banner-box">
            <div class="alert-top">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span class="alert-pill" id="live-alert-pill">🟢 GREEN STATUS (NORMAL / DRY)</span>
                    <span class="alert-station" id="live-station-name">Station: Regional Representative Station: All India (Pan-India Overview) (Lat: 17.754°, Lon: 80.921°)</span>
                </div>
                <div style="font-size: 13px; color: #E2E8F0;" id="live-obs-time">
                    🕒 <b>Live Observation:</b> 2026-11-08 10:45 IST | <span style="background: rgba(255,255,255,0.2); padding: 3px 8px; border-radius: 4px;">📡 Live API Connected</span>
                </div>
            </div>
            <div class="alert-desc" id="live-alert-desc">
                High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.
            </div>
            <div class="alert-pills-row">
                <span class="metric-pill" id="pill-temp">🌡️ Temp: 24.5°C (Feels 25.8°C)</span>
                <span class="metric-pill" id="pill-humidity">💧 Humidity: 89%</span>
                <span class="metric-pill" id="pill-rain">🌧️ Live Rain: 0.0 mm/h</span>
                <span class="metric-pill" id="pill-past24">🌊 Past 24h Rain: 0.0 mm</span>
                <span class="metric-pill" id="pill-cond">🌤️ Condition: Clear Sky</span>
                <span class="metric-pill" id="pill-wind">💨 Wind: 5.7 km/h</span>
                <span class="metric-pill" id="pill-elev">⛰️ Elevation: 134.3 m AMSL</span>
            </div>
        </div>

        <!-- Streamlit Tabs Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active" onclick="switchTab('tab-map', this)">🗺️ Interactive Geospatial Map</button>
            <button class="tab-button" onclick="switchTab('tab-districts', this)">🏛️ All Districts in State Matrix</button>
            <button class="tab-button" onclick="switchTab('tab-signatures', this)">📊 Multi-Criteria Risk Signatures</button>
            <button class="tab-button" onclick="switchTab('tab-national', this)">🇮🇳 State-Wise National Comparison</button>
            <button class="tab-button" onclick="switchTab('tab-ml', this)">🤖 Machine Learning Benchmarking</button>
            <button class="tab-button" onclick="switchTab('tab-data', this)">📋 Data Explorer & All Places Registry</button>
        </div>

        <!-- TAB 1: INTERACTIVE GEOSPATIAL MAP (EXACT CLEAN FOLIUM VIEW) -->
        <div id="tab-map" class="tab-panel active">
            <div>
                <div class="tab-section-header" id="map-section-header">Geospatial Hazard Distribution — All India (Pan-India Overview) (All Districts in State)</div>
                <div class="tab-section-sub" id="map-section-sub">Displaying 229 habitation(s) across 92 district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.</div>
            </div>
            <div id="map"></div>
        </div>

        <!-- TAB 2: ALL DISTRICTS IN STATE MATRIX & REAL-TIME MONITORING -->
        <div id="tab-districts" class="tab-panel">
            <div>
                <div class="tab-section-header" id="districts-section-header">All Districts Matrix & Real-Time Monitoring — All India (Pan-India Overview)</div>
                <div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>
            </div>
            
            <!-- 2 Clean Plotly Charts Side-by-Side -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div class="chart-card">
                    <div id="districtsRankChart" style="height: 420px;"></div>
                </div>
                <div class="chart-card">
                    <div id="districtScatterChart" style="height: 420px;"></div>
                </div>
            </div>

            <!-- District Multi-Hazard Profile Summary Table -->
            <div class="chart-card">
                <div class="chart-header"><span>District Multi-Hazard Profile Summary Table</span></div>
                <div class="table-wrap">
                    <table id="district-summary-table">
                        <thead>
                            <tr>
                                <th>District</th>
                                <th>Habitations</th>
                                <th>High Hazard</th>
                                <th>Mod Hazard</th>
                                <th>Low Hazard</th>
                                <th>High Hazard %</th>
                                <th>Mean Elevation</th>
                                <th>River Distance</th>
                                <th>Annual Rain</th>
                                <th>Max Daily Rain</th>
                                <th>Flood Frequency</th>
                            </tr>
                        </thead>
                        <tbody id="district-summary-tbody"></tbody>
                    </table>
                </div>
            </div>

            <!-- Live Multi-District Real-Time Meteorological Monitor -->
            <div class="chart-card">
                <div class="chart-header"><span>⚡ Live Multi-District Real-Time Meteorological Monitor</span></div>
                <p style="font-size: 13.5px; color: var(--text-subdued);">Fetch live real-time weather readings simultaneously across all monitored districts:</p>
                <button class="btn-refresh" style="width: auto; align-self: flex-start; padding: 8px 18px;" onclick="queryLiveDistrictsWeather()">
                    📡 Query Live Weather for All Monitored Districts
                </button>
                <div id="live-districts-result-box" style="display: none; margin-top: 10px;">
                    <div class="table-wrap">
                        <table id="live-districts-table">
                            <thead>
                                <tr>
                                    <th>District</th>
                                    <th>Live Temp</th>
                                    <th>Humidity</th>
                                    <th>Live Rain Rate</th>
                                    <th>Past 24h Rain</th>
                                    <th>Sky Condition</th>
                                    <th>Wind Speed</th>
                                    <th>Dynamic Alert</th>
                                </tr>
                            </thead>
                            <tbody id="live-districts-tbody"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 3: MULTI-CRITERIA RISK SIGNATURES -->
        <div id="tab-signatures" class="tab-panel">
            <div>
                <div class="tab-section-header" id="signatures-section-header">Multi-Criteria Risk Signatures (All India)</div>
                <div class="tab-section-sub">Unsupervised morphological, hydrometeorological, and biophysical profiles across hazard tiers:</div>
            </div>

            <!-- 2 Clean Plotly Charts Side-by-Side (Radar & 2D PCA) -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div class="chart-card">
                    <div id="signaturesRadarChart" style="height: 450px;"></div>
                </div>
                <div class="chart-card">
                    <div id="pcaScatterChart" style="height: 450px;"></div>
                </div>
            </div>

            <!-- Feature Distribution by Hazard Tier -->
            <div class="chart-card">
                <div class="chart-header">
                    <span>Feature Distribution by Hazard Tier</span>
                    <select id="box-feature-select" style="width: 280px;" onchange="updateBoxFeatureChart()">
                        <option value="elevation_m">Surface Elevation (m AMSL)</option>
                        <option value="distance_to_river_km">Distance to River/Channel (km)</option>
                        <option value="historical_flood_inundation_frequency">Historical Inundation Frequency (0-5)</option>
                        <option value="annual_rainfall_mm">Annual Rainfall (mm)</option>
                        <option value="extreme_daily_rainfall_mm">Max Single-Day Rain (mm)</option>
                        <option value="population_density_per_sqkm">Population Density (/km²)</option>
                        <option value="drainage_congestion_index">Drainage Congestion Score (1-5)</option>
                    </select>
                </div>
                <div id="featureBoxChart" style="height: 380px;"></div>
            </div>
        </div>

        <!-- TAB 4: STATE-WISE NATIONAL COMPARISON -->
        <div id="tab-national" class="tab-panel">
            <div>
                <div class="tab-section-header">State-Wise Flood Hazard & Vulnerability Comparison across India</div>
                <div class="tab-section-sub">Cross-state comparative risk benchmarking across monitored settlements:</div>
            </div>

            <!-- 2 Clean Plotly Charts Side-by-Side -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div class="chart-card">
                    <div id="stateBarChart" style="height: 430px;"></div>
                </div>
                <div class="chart-card">
                    <div id="stateScatterChart" style="height: 430px;"></div>
                </div>
            </div>

            <!-- State-Wise Multi-Hazard Comparison Table -->
            <div class="chart-card">
                <div class="chart-header"><span>State-Wise Comparative Multi-Hazard Table</span></div>
                <div class="table-wrap">
                    <table id="state-summary-table">
                        <thead>
                            <tr>
                                <th>State / Territory</th>
                                <th>Settlements</th>
                                <th>Districts</th>
                                <th>High Hazard</th>
                                <th>High Hazard %</th>
                                <th>Mean Rainfall</th>
                                <th>Mean Elevation</th>
                                <th>Flood Frequency</th>
                                <th>Congestion Score</th>
                            </tr>
                        </thead>
                        <tbody id="state-summary-tbody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 5: MACHINE LEARNING BENCHMARKING (4 CLEAN BENCHMARK TABLES) -->
        <div id="tab-ml" class="tab-panel">
            <div>
                <div class="tab-section-header">Machine Learning Algorithm Benchmarking & Metric Validation</div>
                <div class="tab-section-sub">Empirical validation and objective evaluation metrics across clustering paradigms:</div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <!-- K-Means Benchmark Table -->
                <div class="chart-card">
                    <div class="chart-header"><span>K-Means Clustering Benchmarking (Random vs K-Means++)</span></div>
                    <div class="table-wrap">
                        <table id="table-kmeans">
                            <thead>
                                <tr>
                                    <th>Algorithm</th>
                                    <th>Init Method</th>
                                    <th>K</th>
                                    <th>Silhouette</th>
                                    <th>Davies-Bouldin</th>
                                </tr>
                            </thead>
                            <tbody id="tbody-kmeans"></tbody>
                        </table>
                    </div>
                </div>

                <!-- Hierarchical Linkage Benchmark Table -->
                <div class="chart-card">
                    <div class="chart-header"><span>Hierarchical Clustering (Linkage Criteria, K=3)</span></div>
                    <div class="table-wrap">
                        <table id="table-hier">
                            <thead>
                                <tr>
                                    <th>Linkage Criterion</th>
                                    <th>Clusters (K)</th>
                                    <th>Silhouette</th>
                                    <th>Davies-Bouldin</th>
                                    <th>Cluster Distribution</th>
                                </tr>
                            </thead>
                            <tbody id="tbody-hier"></tbody>
                        </table>
                    </div>
                </div>

                <!-- K-Medoids PAM Benchmark Table -->
                <div class="chart-card">
                    <div class="chart-header"><span>K-Medoids (PAM) with Manhattan (L1) vs Euclidean</span></div>
                    <div class="table-wrap">
                        <table id="table-kmedoids">
                            <thead>
                                <tr>
                                    <th>Distance Metric</th>
                                    <th>K</th>
                                    <th>Silhouette</th>
                                    <th>Davies-Bouldin</th>
                                    <th>Exemplar Medoids</th>
                                </tr>
                            </thead>
                            <tbody id="tbody-kmedoids"></tbody>
                        </table>
                    </div>
                </div>

                <!-- Master Comparison across Paradigms -->
                <div class="chart-card">
                    <div class="chart-header"><span>Master Comparison across Paradigms</span></div>
                    <div class="table-wrap">
                        <table id="table-master">
                            <thead>
                                <tr>
                                    <th>Algorithm</th>
                                    <th>Clusters</th>
                                    <th>Noise Points</th>
                                    <th>Silhouette</th>
                                    <th>Davies-Bouldin</th>
                                </tr>
                            </thead>
                            <tbody id="tbody-master"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 6: DATA EXPLORER & ALL PLACES REGISTRY -->
        <div id="tab-data" class="tab-panel">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div class="tab-section-header" id="data-section-header">Pan-India All Places & Habitations Registry</div>
                    <div class="tab-section-sub" id="data-section-sub">Showing filtered habitations matching active scope:</div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <input type="text" id="registry-search" class="search-input" placeholder="🔍 Search place, district, mandal..." oninput="filterRegistryTable()" />
                    <button class="btn-download" onclick="downloadCSV()">
                        📥 Download Filtered Data (CSV)
                    </button>
                </div>
            </div>

            <div class="chart-card">
                <div class="table-wrap">
                    <table id="registry-table">
                        <thead>
                            <tr>
                                <th>Habitation Name</th>
                                <th>State</th>
                                <th>District</th>
                                <th>Mandal</th>
                                <th>ML Hazard Tier</th>
                                <th>Elevation (m)</th>
                                <th>River Dist (km)</th>
                                <th>Flood History</th>
                                <th>Drainage (1-5)</th>
                                <th>Annual Rain (mm)</th>
                                <th>Max 24h Rain (mm)</th>
                                <th>Population</th>
                                <th>Pop Density (/km²)</th>
                                <th>River Basin</th>
                            </tr>
                        </thead>
                        <tbody id="registry-tbody"></tbody>
                    </table>
                </div>
                <div id="registry-pagination" style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 13px; color: var(--text-subdued);">
                    <span id="registry-page-info"></span>
                    <div style="display: flex; gap: 6px;">
                        <button onclick="prevRegistryPage()" class="btn-refresh" style="padding: 5px 12px; width: auto;">Previous</button>
                        <button onclick="nextRegistryPage()" class="btn-refresh" style="padding: 5px 12px; width: auto;">Next</button>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Client-Side JavaScript Application Logic -->
    <script>
        const allPlaces = {places_json};
        const kmTableData = {kmeans_json};
        const kmedTableData = {kmedoids_json};
        const hierTableData = {hier_json};
        const masterTableData = {master_json};

        let selectedState = "All India (Pan-India Overview)";
        let selectedDist = "All Districts in State";
        let selectedPlace = "All Locations in Scope";

        let filteredPlaces = [...allPlaces];
        let map = null;
        let mapMarkersLayer = null;
        let riverLayerGroup = null;

        let registryFiltered = [];
        let registryPage = 1;
        const registryPageSize = 25;

        const colorMap = {{
            'High Relative Hazard / Vulnerability': '#D73027',
            'Moderate Relative Hazard / Vulnerability': '#FDAE61',
            'Relatively Lower Hazard / Vulnerability': '#4575B4'
        }};

        const darkPlotlyLayout = {{
            template: 'plotly_dark',
            paper_bgcolor: 'rgba(22, 25, 34, 0.7)',
            plot_bgcolor: 'rgba(22, 25, 34, 0.7)',
            font: {{ color: '#CBD5E1', family: 'Source Sans Pro, Inter, sans-serif' }},
            margin: {{ l: 45, r: 25, t: 40, b: 40 }}
        }};

        const stateGeo = {{
            "All India (Pan-India Overview)": {{ center: [22.0, 79.5], zoom: 5 }},
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

        window.addEventListener('DOMContentLoaded', () => {{
            populateStateDropdown();
            populateDistrictDropdown();
            updateDangerCounts();
            populatePlaceDropdown();
            initMap();
            initMLTables();
            applyFilters();
        }});

        function populateStateDropdown() {{
            const select = document.getElementById('state-select');
            const states = [...new Set(allPlaces.map(p => p.state).filter(Boolean))].sort();
            states.forEach(st => {{
                const opt = document.createElement('option');
                opt.value = st;
                opt.textContent = st;
                select.appendChild(opt);
            }});
        }}

        function populateDistrictDropdown() {{
            const select = document.getElementById('district-select');
            select.innerHTML = '<option value="All Districts in State">All Districts in State</option>';
            let list = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                list = allPlaces.filter(p => p.state === selectedState);
            }}
            const districts = [...new Set(list.map(p => p.district).filter(Boolean))].sort();
            districts.forEach(d => {{
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d;
                select.appendChild(opt);
            }});
        }}

        function updateDangerCounts() {{
            let scope = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                scope = scope.filter(p => p.state === selectedState);
            }}
            if (selectedDist !== "All Districts in State") {{
                scope = scope.filter(p => p.district === selectedDist);
            }}
            const high = scope.filter(p => p.relative_hazard_level === 'High Relative Hazard / Vulnerability').length;
            const med = scope.filter(p => p.relative_hazard_level === 'Moderate Relative Hazard / Vulnerability').length;
            const low = scope.filter(p => p.relative_hazard_level === 'Relatively Lower Hazard / Vulnerability').length;

            const countHighEl = document.getElementById('count-high');
            const countMedEl = document.getElementById('count-medium');
            const countLowEl = document.getElementById('count-low');
            if (countHighEl) countHighEl.textContent = high;
            if (countMedEl) countMedEl.textContent = med;
            if (countLowEl) countLowEl.textContent = low;
        }}

        function populatePlaceDropdown() {{
            const select = document.getElementById('place-select');
            select.innerHTML = '<option value="All Locations in Scope">All Locations in Scope</option>';
            let list = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                list = list.filter(p => p.state === selectedState);
            }}
            if (selectedDist !== "All Districts in State") {{
                list = list.filter(p => p.district === selectedDist);
            }}

            const isHighChecked = document.getElementById('check-high') ? document.getElementById('check-high').checked : true;
            const isMedChecked = document.getElementById('check-medium') ? document.getElementById('check-medium').checked : true;
            const isLowChecked = document.getElementById('check-low') ? document.getElementById('check-low').checked : true;

            list = list.filter(p => {{
                if (p.relative_hazard_level === 'High Relative Hazard / Vulnerability' && !isHighChecked) return false;
                if (p.relative_hazard_level === 'Moderate Relative Hazard / Vulnerability' && !isMedChecked) return false;
                if (p.relative_hazard_level === 'Relatively Lower Hazard / Vulnerability' && !isLowChecked) return false;
                return true;
            }});

            const places = [...new Set(list.map(p => p.habitation_name).filter(Boolean))].sort();
            places.forEach(p => {{
                const opt = document.createElement('option');
                opt.value = p;
                opt.textContent = p;
                if (p === selectedPlace) opt.selected = true;
                select.appendChild(opt);
            }});
        }}

        function onStateChange() {{
            selectedState = document.getElementById('state-select').value;
            selectedDist = "All Districts in State";
            selectedPlace = "All Locations in Scope";
            const areaInput = document.getElementById('area-search');
            if (areaInput) areaInput.value = '';
            populateDistrictDropdown();
            updateDangerCounts();
            populatePlaceDropdown();
            applyFilters();
        }}

        function onDistrictChange() {{
            selectedDist = document.getElementById('district-select').value;
            selectedPlace = "All Locations in Scope";
            const areaInput = document.getElementById('area-search');
            if (areaInput) areaInput.value = '';
            updateDangerCounts();
            populatePlaceDropdown();
            applyFilters();
        }}

        function onDangerFilterChange() {{
            populatePlaceDropdown();
            applyFilters();
        }}

        function onPlaceChange() {{
            selectedPlace = document.getElementById('place-select').value;
            const areaInput = document.getElementById('area-search');
            if (areaInput && selectedPlace !== "All Locations in Scope") {{
                areaInput.value = selectedPlace;
            }} else if (areaInput) {{
                areaInput.value = '';
            }}
            applyFilters();
        }}

        function onAreaSearch(query) {{
            const q = (query || '').trim().toLowerCase();
            const select = document.getElementById('place-select');
            if (q.length === 0) {{
                selectedPlace = "All Locations in Scope";
                select.value = "All Locations in Scope";
            }} else {{
                let matched = false;
                for (let i = 0; i < select.options.length; i++) {{
                    if (select.options[i].value.toLowerCase().includes(q)) {{
                        select.selectedIndex = i;
                        selectedPlace = select.options[i].value;
                        matched = true;
                        break;
                    }}
                }}
                if (!matched) {{
                    selectedPlace = "All Locations in Scope";
                    select.value = "All Locations in Scope";
                }}
            }}
            applyFilters();
        }}

        function applyFilters() {{
            const isHighChecked = document.getElementById('check-high') ? document.getElementById('check-high').checked : true;
            const isMedChecked = document.getElementById('check-medium') ? document.getElementById('check-medium').checked : true;
            const isLowChecked = document.getElementById('check-low') ? document.getElementById('check-low').checked : true;
            const searchVal = (document.getElementById('area-search') ? document.getElementById('area-search').value : '').trim().toLowerCase();

            filteredPlaces = allPlaces.filter(p => {{
                if (selectedState !== "All India (Pan-India Overview)" && p.state !== selectedState) return false;
                if (selectedDist !== "All Districts in State" && p.district !== selectedDist) return false;

                if (p.relative_hazard_level === 'High Relative Hazard / Vulnerability' && !isHighChecked) return false;
                if (p.relative_hazard_level === 'Moderate Relative Hazard / Vulnerability' && !isMedChecked) return false;
                if (p.relative_hazard_level === 'Relatively Lower Hazard / Vulnerability' && !isLowChecked) return false;

                if (selectedPlace !== "All Locations in Scope" && p.habitation_name !== selectedPlace) return false;

                if (searchVal.length > 0 && selectedPlace === "All Locations in Scope") {{
                    if (!p.habitation_name.toLowerCase().includes(searchVal)) return false;
                }}

                return true;
            }});

            updateSummaryScope();
            updateKPICards();
            updateWeatherEngine();
            updateMap();
            updateDistrictMatrix();
            updateRiskSignatures();
            updateNationalComparison();
            updateRegistryTable();
        }}

        function updateSummaryScope() {{
            document.getElementById('summary-state').textContent = selectedState;
            document.getElementById('summary-dist').textContent = selectedDist;
            document.getElementById('summary-place').textContent = selectedPlace;
            document.getElementById('summary-hab-count').textContent = `${{filteredPlaces.length}} / ${{allPlaces.length}}`;
            
            let distCount = 92;
            if (selectedState !== "All India (Pan-India Overview)") {{
                const inState = allPlaces.filter(p => p.state === selectedState);
                distCount = new Set(inState.map(p => p.district)).size;
            }}
            document.getElementById('summary-dist-count').textContent = distCount;
        }}

        function updateKPICards() {{
            const total = filteredPlaces.length;
            const high = filteredPlaces.filter(p => p.relative_hazard_level === 'High Relative Hazard / Vulnerability').length;
            const med = filteredPlaces.filter(p => p.relative_hazard_level === 'Moderate Relative Hazard / Vulnerability').length;
            const low = filteredPlaces.filter(p => p.relative_hazard_level === 'Relatively Lower Hazard / Vulnerability').length;

            document.getElementById('kpi-high-val').textContent = high;
            document.getElementById('kpi-med-val').textContent = med;
            document.getElementById('kpi-low-val').textContent = low;

            const pctHigh = total > 0 ? ((high / total) * 100).toFixed(1) : '0.0';
            const pctMed = total > 0 ? ((med / total) * 100).toFixed(1) : '0.0';
            const pctLow = total > 0 ? ((low / total) * 100).toFixed(1) : '0.0';

            document.getElementById('kpi-high-delta').textContent = `↑ ${{pctHigh}}% of active`;
            document.getElementById('kpi-med-delta').textContent = `↑ ${{pctMed}}% of active`;
            document.getElementById('kpi-low-delta').textContent = `↑ ${{pctLow}}% of active`;

            const meanRain = total > 0 ? (filteredPlaces.reduce((acc, p) => acc + (p.annual_rainfall_mm || 0), 0) / total).toFixed(1) : '0.0';
            const maxRain = total > 0 ? Math.max(...filteredPlaces.map(p => p.extreme_daily_rainfall_mm || 0)).toFixed(0) : '0';
            document.getElementById('kpi-rain-val').textContent = `${{meanRain}} mm`;
            document.getElementById('kpi-rain-delta').textContent = `↑ Max ${{maxRain}} mm/day`;

            const meanElev = total > 0 ? (filteredPlaces.reduce((acc, p) => acc + (p.elevation_m || 0), 0) / total).toFixed(1) : '0.0';
            const minElev = total > 0 ? Math.min(...filteredPlaces.map(p => p.elevation_m || 0)).toFixed(0) : '0';
            document.getElementById('kpi-elev-val').textContent = `${{meanElev}} m AMSL`;
            document.getElementById('kpi-elev-delta').textContent = `↑ Min ${{minElev}} m`;
        }}

        function updateWeatherEngine() {{
            let targetLat = 17.754, targetLon = 80.921;
            let targetName = `Regional Representative Station: ${{selectedState}}`;
            let targetElev = 134.3;

            if (selectedPlace !== "All Locations in Scope" && filteredPlaces.length === 1) {{
                const p = filteredPlaces[0];
                targetLat = p.latitude;
                targetLon = p.longitude;
                targetName = `${{p.habitation_name}} (${{p.district}}, ${{p.state}})`;
                targetElev = p.elevation_m;
            }} else if (selectedDist !== "All Districts in State" && filteredPlaces.length > 0) {{
                targetLat = filteredPlaces.reduce((a, b) => a + b.latitude, 0) / filteredPlaces.length;
                targetLon = filteredPlaces.reduce((a, b) => a + b.longitude, 0) / filteredPlaces.length;
                targetName = `District Centroid: ${{selectedDist}} (${{filteredPlaces[0].state}})`;
                targetElev = filteredPlaces.reduce((a, b) => a + b.elevation_m, 0) / filteredPlaces.length;
            }} else if (filteredPlaces.length > 0 && selectedState !== "All India (Pan-India Overview)") {{
                targetLat = filteredPlaces.reduce((a, b) => a + b.latitude, 0) / filteredPlaces.length;
                targetLon = filteredPlaces.reduce((a, b) => a + b.longitude, 0) / filteredPlaces.length;
                targetElev = filteredPlaces.reduce((a, b) => a + b.elevation_m, 0) / filteredPlaces.length;
            }}

            document.getElementById('live-station-name').textContent = `Station: ${{targetName}} (Lat: ${{targetLat.toFixed(3)}}°, Lon: ${{targetLon.toFixed(3)}}°)`;
            document.getElementById('pill-elev').textContent = `⛰️ Elevation: ${{targetElev.toFixed(1)}} m AMSL`;

            fetch(`https://api.open-meteo.com/v1/forecast?latitude=${{targetLat.toFixed(4)}}&longitude=${{targetLon.toFixed(4)}}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m&past_days=1&hourly=precipitation&timezone=Asia%2FKolkata`)
                .then(r => r.json())
                .then(data => {{
                    if (data && data.current) {{
                        const cur = data.current;
                        const hourly = (data.hourly && data.hourly.precipitation) ? data.hourly.precipitation : [];
                        const past24 = hourly.length >= 24 ? hourly.slice(-24).reduce((a,b)=>a+b, 0) : (cur.rain || 0);

                        document.getElementById('pill-temp').textContent = `🌡️ Temp: ${{cur.temperature_2m}}°C (Feels ${{cur.apparent_temperature}}°C)`;
                        document.getElementById('pill-humidity').textContent = `💧 Humidity: ${{cur.relative_humidity_2m}}%`;
                        document.getElementById('pill-rain').textContent = `🌧️ Live Rain: ${{cur.rain}} mm/h`;
                        document.getElementById('pill-past24').textContent = `🌊 Past 24h Rain: ${{past24.toFixed(1)}} mm`;
                        document.getElementById('pill-wind').textContent = `💨 Wind: ${{cur.wind_speed_10m}} km/h`;

                        const now = new Date();
                        const timeStr = now.toISOString().replace('T', ' ').substring(0, 16) + ' IST';
                        document.getElementById('live-obs-time').innerHTML = `🕒 <b>Live Observation:</b> ${{timeStr}} | <span style="background: rgba(255,255,255,0.2); padding: 3px 8px; border-radius: 4px;">📡 Live API Connected</span>`;

                        const banner = document.getElementById('alert-banner-box');
                        const alertPill = document.getElementById('live-alert-pill');
                        const alertDesc = document.getElementById('live-alert-desc');

                        if (past24 >= 35.0 || cur.rain >= 10.0) {{
                            banner.style.background = 'linear-gradient(135deg, #DC2626 0%, #111827 100%)';
                            alertPill.textContent = '🚨 RED ALERT (CRITICAL RISK)';
                            alertDesc.textContent = 'High morphological baseline vulnerability coupled with severe active/antecedent rainfall. High probability of inundation and drainage surcharge.';
                        }} else if (past24 >= 15.0 || cur.rain >= 4.0) {{
                            banner.style.background = 'linear-gradient(135deg, #EA580C 0%, #111827 100%)';
                            alertPill.textContent = '🟧 ORANGE ALERT (ELEVATED RISK)';
                            alertDesc.textContent = 'Active rainfall detected over low-lying / floodway terrain. Drainage channels nearing capacity; localized waterlogging anticipated.';
                        }} else if (past24 >= 5.0 || cur.rain > 0.0) {{
                            banner.style.background = 'linear-gradient(135deg, #D97706 0%, #111827 100%)';
                            alertPill.textContent = '🟨 YELLOW WATCH (MONITOR)';
                            alertDesc.textContent = 'Light rain observed over high baseline vulnerability terrain. Maintain vigilance on drainage sluices and local canal levels.';
                        }} else {{
                            banner.style.background = 'linear-gradient(135deg, #16A34A 0%, #0F172A 100%)';
                            alertPill.textContent = '🟢 GREEN STATUS (NORMAL / DRY)';
                            alertDesc.textContent = 'High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.';
                        }}
                    }}
                }})
                .catch(() => {{}});
        }}

        function triggerRefresh() {{
            updateWeatherEngine();
        }}

        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');
            if (tabId === 'tab-map' && map) {{
                setTimeout(() => map.invalidateSize(), 150);
            }}
            window.dispatchEvent(new Event('resize'));
        }}

        function initMap() {{
            map = L.map('map', {{
                center: [22.0, 79.5],
                zoom: 5,
                zoomControl: true
            }});

            const osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);

            const dark = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                maxZoom: 19,
                attribution: '© CartoDB'
            }});

            L.control.layers({{ "OpenStreetMap (Default)": osm, "CartoDB Dark": dark }}).addTo(map);

            riverLayerGroup = L.layerGroup().addTo(map);
            const krishnaCoords = [
                [16.580, 80.360], [16.592, 80.450], [16.590, 80.522], [16.550, 80.565],
                [16.507, 80.605], [16.480, 80.640], [16.440, 80.720], [16.360, 80.780],
                [16.320, 80.825], [16.185, 80.795], [16.122, 80.932], [16.022, 80.918], [15.945, 80.915]
            ];
            L.polyline(krishnaCoords, {{ color: '#0055FF', weight: 4, opacity: 0.85 }}).bindTooltip("Krishna River (Prakasam Barrage System)").addTo(riverLayerGroup);

            const budameruCoords = [
                [16.630, 80.540], [16.562, 80.615], [16.538, 80.638], [16.522, 80.665], [16.520, 80.750]
            ];
            L.polyline(budameruCoords, {{ color: '#00AAFF', weight: 3, dashArray: '6, 6', opacity: 0.85 }}).bindTooltip("Budameru Rivulet Drainage Floodway").addTo(riverLayerGroup);

            mapMarkersLayer = L.layerGroup().addTo(map);
        }}

        function updateMap() {{
            if (!map || !mapMarkersLayer) return;
            mapMarkersLayer.clearLayers();

            document.getElementById('map-section-header').textContent = `Geospatial Hazard Distribution — ${{selectedState}} (${{selectedDist}})`;
            document.getElementById('map-section-sub').textContent = `Displaying ${{filteredPlaces.length}} habitation(s) across ${{new Set(filteredPlaces.map(p => p.district)).size}} district(s). Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.`;

            let bounds = [];
            filteredPlaces.forEach(p => {{
                const lat = p.latitude;
                const lon = p.longitude;
                if (!lat || !lon) return;
                bounds.push([lat, lon]);

                const tier = p.relative_hazard_level || 'Moderate Relative Hazard / Vulnerability';
                const color = colorMap[tier] || '#888888';
                const isSelected = (selectedPlace === p.habitation_name);

                const popupHtml = `
                    <div style="font-family: Arial, sans-serif; font-size: 12px; width: 260px; line-height: 1.45; color: #111;">
                        <b style="color: ${{color}}; font-size: 14.5px;">${{p.habitation_name}}</b><br>
                        <b>State:</b> ${{p.state}}<br>
                        <b>District:</b> ${{p.district}} | <b>Mandal:</b> ${{p.mandal || 'N/A'}}<br>
                        <b>Basin:</b> ${{p.river_basin || 'Regional'}}<br>
                        <b>ML Hazard Tier:</b> <span style="color: ${{color}}; font-weight: bold;">${{tier}}</span>
                        <hr style="margin: 4px 0; border: 0; border-top: 1px solid #ccc;">
                        <b>Elevation:</b> ${{p.elevation_m.toFixed(1)}} m AMSL<br>
                        <b>Distance to River:</b> ${{p.distance_to_river_km.toFixed(2)}} km<br>
                        <b>Historical Floods:</b> ${{p.historical_flood_inundation_frequency}}/5<br>
                        <b>Drainage Congestion:</b> ${{p.drainage_congestion_index}}/5<br>
                        <b>Annual Rain:</b> ${{p.annual_rainfall_mm.toFixed(1)}} mm<br>
                        <b>Max 24h Rain:</b> ${{p.extreme_daily_rainfall_mm.toFixed(1)}} mm<br>
                        <b>Pop Density:</b> ${{Number(p.population_density_per_sqkm).toLocaleString()}} /km²
                    </div>
                `;

                const marker = L.circleMarker([lat, lon], {{
                    radius: isSelected ? 9.5 : (tier.includes('High') ? 6.5 : 5.0),
                    color: isSelected ? '#FFD700' : '#000000',
                    weight: isSelected ? 3.0 : 0.8,
                    fillColor: color,
                    fillOpacity: isSelected ? 0.95 : 0.85
                }}).bindPopup(popupHtml).bindTooltip(`📍 ${{p.habitation_name}} (${{p.district}} - ${{tier.split(' ')[0]}})`);

                marker.addTo(mapMarkersLayer);

                if (isSelected) {{
                    marker.openPopup();
                }}
            }});

            if (selectedPlace !== "All Locations in Scope" && filteredPlaces.length === 1) {{
                map.setView([filteredPlaces[0].latitude, filteredPlaces[0].longitude], 13);
            }} else if (bounds.length > 0) {{
                map.fitBounds(bounds, {{ padding: [35, 35], maxZoom: 12 }});
            }} else {{
                const geo = stateGeo[selectedState] || {{ center: [22.0, 79.5], zoom: 5 }};
                map.setView(geo.center, geo.zoom);
            }}
        }}

        function updateDistrictMatrix() {{
            document.getElementById('districts-section-header').textContent = `All Districts Matrix & Real-Time Monitoring — ${{selectedState}}`;

            let statePlaces = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                statePlaces = allPlaces.filter(p => p.state === selectedState);
            }}

            const distMap = {{}};
            statePlaces.forEach(p => {{
                const d = p.district;
                if (!distMap[d]) {{
                    distMap[d] = {{
                        district: d,
                        state: p.state,
                        total: 0, high: 0, mod: 0, low: 0,
                        elevSum: 0, riverSum: 0, rainSum: 0,
                        maxRain: 0, floodSum: 0,
                        latSum: 0, lonSum: 0
                    }};
                }}
                distMap[d].total++;
                if (p.relative_hazard_level.includes('High')) distMap[d].high++;
                else if (p.relative_hazard_level.includes('Moderate')) distMap[d].mod++;
                else distMap[d].low++;

                distMap[d].elevSum += p.elevation_m || 0;
                distMap[d].riverSum += p.distance_to_river_km || 0;
                distMap[d].rainSum += p.annual_rainfall_mm || 0;
                distMap[d].maxRain = Math.max(distMap[d].maxRain, p.extreme_daily_rainfall_mm || 0);
                distMap[d].floodSum += p.historical_flood_inundation_frequency || 0;
                distMap[d].latSum += p.latitude || 0;
                distMap[d].lonSum += p.longitude || 0;
            }});

            const districts = Object.values(distMap).map(d => ({{
                ...d,
                highPct: Number(((d.high / d.total) * 100).toFixed(1)),
                meanElev: Number((d.elevSum / d.total).toFixed(1)),
                meanRiver: Number((d.riverSum / d.total).toFixed(2)),
                meanRain: Number((d.rainSum / d.total).toFixed(1)),
                meanFlood: Number((d.floodSum / d.total).toFixed(2)),
                lat: d.latSum / d.total,
                lon: d.lonSum / d.total
            }})).sort((a, b) => b.highPct - a.highPct || a.meanElev - b.meanElev);

            // Exact Streamlit Plotly Bar: Districts Ranked by High Hazard %
            const barTrace = {{
                x: districts.map(d => d.district),
                y: districts.map(d => d.highPct),
                type: 'bar',
                marker: {{
                    color: districts.map(d => d.highPct),
                    colorscale: 'Reds',
                    showscale: true,
                    colorbar: {{ title: 'High Hazard (%)', thickness: 15 }}
                }}
            }};
            Plotly.newPlot('districtsRankChart', [barTrace], {{
                ...darkPlotlyLayout,
                title: 'Districts Ranked by High Hazard Habitations (%) in ' + selectedState,
                xaxis: {{ tickangle: -45 }},
                yaxis: {{ title: 'High Hazard (%)', range: [0, 100] }},
                height: 400
            }}, {{ responsive: true }});

            // Exact Streamlit Plotly Scatter: Mean Elevation vs Annual Rain
            const scatterTrace = {{
                x: districts.map(d => d.meanElev),
                y: districts.map(d => d.meanRain),
                mode: 'markers',
                text: districts.map(d => d.district),
                marker: {{
                    size: districts.map(d => Math.max(8, Math.min(22, d.total * 3))),
                    color: districts.map(d => d.highPct),
                    colorscale: 'Portland',
                    showscale: true,
                    colorbar: {{ title: 'High Hazard %', thickness: 15 }}
                }}
            }};
            Plotly.newPlot('districtScatterChart', [scatterTrace], {{
                ...darkPlotlyLayout,
                title: 'District Morphometry: Mean Elevation vs Annual Rain (' + selectedState + ')',
                xaxis: {{ title: 'Mean Elevation (m AMSL)' }},
                yaxis: {{ title: 'Mean Annual Rainfall (mm)' }},
                height: 400
            }}, {{ responsive: true }});

            // District Table with red percentage highlight
            const tbody = document.getElementById('district-summary-tbody');
            tbody.innerHTML = '';
            districts.forEach(d => {{
                const tr = document.createElement('tr');
                const redIntensity = Math.min(0.65, Math.max(0.1, d.highPct / 120.0));
                tr.innerHTML = `
                    <td><b>${{d.district}}</b></td>
                    <td>${{d.total}}</td>
                    <td><span class="badge-red">${{d.high}}</span></td>
                    <td><span class="badge-orange">${{d.mod}}</span></td>
                    <td><span class="badge-blue">${{d.low}}</span></td>
                    <td style="background: rgba(215, 48, 39, ${{redIntensity}}); color: #FFF; font-weight: bold;">${{d.highPct}}%</td>
                    <td>${{d.meanElev}} m</td>
                    <td>${{d.meanRiver}} km</td>
                    <td>${{d.meanRain}} mm</td>
                    <td>${{d.maxRain}} mm</td>
                    <td>${{d.meanFlood}}/5</td>
                `;
                tbody.appendChild(tr);
            }});

            window.currentDistrictsForWeather = districts;
        }}

        function queryLiveDistrictsWeather() {{
            const box = document.getElementById('live-districts-result-box');
            const tbody = document.getElementById('live-districts-tbody');
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #60A5FA;">Connecting to live Open-Meteo satellite feed for districts...</td></tr>';
            box.style.display = 'block';

            const districts = (window.currentDistrictsForWeather || []).slice(0, 15);
            const promises = districts.map(d => {{
                return fetch(`https://api.open-meteo.com/v1/forecast?latitude=${{d.lat.toFixed(4)}}&longitude=${{d.lon.toFixed(4)}}&current=temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m&past_days=1&hourly=precipitation&timezone=Asia%2FKolkata`)
                    .then(r => r.json())
                    .then(data => {{
                        const cur = (data && data.current) ? data.current : {{}};
                        const hourly = (data.hourly && data.hourly.precipitation) ? data.hourly.precipitation : [];
                        const past24 = hourly.length >= 24 ? hourly.slice(-24).reduce((a,b)=>a+b, 0) : (cur.rain || 0);
                        let alertBadge = '<span class="badge-blue">🟢 Normal</span>';
                        if (past24 >= 30.0 || cur.rain >= 8.0) alertBadge = '<span class="badge-red">🚨 Critical</span>';
                        else if (past24 >= 12.0 || cur.rain >= 3.0) alertBadge = '<span class="badge-orange">🟧 Elevated</span>';

                        return `
                            <tr>
                                <td><b>${{d.district}}</b></td>
                                <td>${{cur.temperature_2m || 24.0}}°C</td>
                                <td>${{cur.relative_humidity_2m || 85}}%</td>
                                <td>${{cur.rain || 0.0}} mm/h</td>
                                <td>${{past24.toFixed(1)}} mm</td>
                                <td>Clear Sky</td>
                                <td>${{cur.wind_speed_10m || 5.0}} km/h</td>
                                <td>${{alertBadge}}</td>
                            </tr>
                        `;
                    }})
                    .catch(() => `<tr><td><b>${{d.district}}</b></td><td colspan="7" style="color: #94A3B8;">Feed offline</td></tr>`);
            }});

            Promise.all(promises).then(rows => {{
                tbody.innerHTML = rows.join('');
            }});
        }}

        function updateRiskSignatures() {{
            document.getElementById('signatures-section-header').textContent = `Multi-Criteria Risk Signatures (${{selectedState}})`;

            let scope = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                scope = allPlaces.filter(p => p.state === selectedState);
            }}

            const tiers = ['High Relative Hazard / Vulnerability', 'Moderate Relative Hazard / Vulnerability', 'Relatively Lower Hazard / Vulnerability'];
            const categories = ['Elevation (Inv)', 'Slope (Inv)', 'River Dist (Inv)', 'Annual Rain', 'Extreme Rain', 'Pop Density', 'Congestion', 'Flood Freq'];

            const radarColors = {{
                'High Relative Hazard / Vulnerability': 'rgba(215, 48, 39, 0.6)',
                'Moderate Relative Hazard / Vulnerability': 'rgba(253, 174, 97, 0.6)',
                'Relatively Lower Hazard / Vulnerability': 'rgba(69, 117, 180, 0.6)'
            }};
            const lineColors = {{
                'High Relative Hazard / Vulnerability': '#d73027',
                'Moderate Relative Hazard / Vulnerability': '#fdae61',
                'Relatively Lower Hazard / Vulnerability': '#4575b4'
            }};

            // Exact Streamlit Radar Chart using Plotly
            const radarTraces = tiers.map(tier => {{
                const inTier = scope.filter(p => p.relative_hazard_level === tier);
                if (inTier.length === 0) return null;
                const count = inTier.length;

                const meanElev = inTier.reduce((a, b) => a + b.elevation_m, 0) / count;
                const meanSlope = inTier.reduce((a, b) => a + (b.slope_deg || 2.0), 0) / count;
                const meanRiver = inTier.reduce((a, b) => a + b.distance_to_river_km, 0) / count;
                const meanRain = inTier.reduce((a, b) => a + b.annual_rainfall_mm, 0) / count;
                const meanExtreme = inTier.reduce((a, b) => a + b.extreme_daily_rainfall_mm, 0) / count;
                const meanPop = inTier.reduce((a, b) => a + b.population_density_per_sqkm, 0) / count;
                const meanDrain = inTier.reduce((a, b) => a + b.drainage_congestion_index, 0) / count;
                const meanFlood = inTier.reduce((a, b) => a + b.historical_flood_inundation_frequency, 0) / count;

                const vElev = Math.max(0, 1.0 - (meanElev / 150.0));
                const vSlope = Math.max(0, 1.0 - (meanSlope / 15.0));
                const vRiver = Math.max(0, 1.0 - (meanRiver / 25.0));
                const vRain = Math.min(1.0, meanRain / 2400.0);
                const vExtreme = Math.min(1.0, meanExtreme / 400.0);
                const vPop = Math.min(1.0, meanPop / 18000.0);
                const vDrain = meanDrain / 5.0;
                const vFlood = meanFlood / 5.0;

                const vals = [vElev, vSlope, vRiver, vRain, vExtreme, vPop, vDrain, vFlood];
                vals.push(vals[0]);
                const thetas = [...categories, categories[0]];

                return {{
                    type: 'scatterpolar',
                    r: vals,
                    theta: thetas,
                    fill: 'toself',
                    fillcolor: radarColors[tier],
                    line: {{ color: lineColors[tier], width: 2 }},
                    name: tier.split(' ')[0] + ' Hazard'
                }};
            }}).filter(Boolean);

            Plotly.newPlot('signaturesRadarChart', radarTraces, {{
                ...darkPlotlyLayout,
                polar: {{ radialaxis: {{ visible: true, range: [0, 1] }} }},
                showlegend: true,
                title: 'Radar Profile Signature (Normalized Risk Factors)',
                height: 440
            }}, {{ responsive: true }});

            // Exact Streamlit 2D PCA Scatter using Plotly
            const pcaTraces = tiers.map(tier => {{
                const items = scope.filter(p => p.relative_hazard_level === tier);
                return {{
                    x: items.map(p => p.pca_1),
                    y: items.map(p => p.pca_2),
                    mode: 'markers',
                    type: 'scatter',
                    text: items.map(p => `${{p.habitation_name}}<br>District: ${{p.district}}<br>Elev: ${{p.elevation_m.toFixed(1)}}m`),
                    marker: {{
                        size: 9,
                        color: colorMap[tier],
                        line: {{ width: 1, color: '#334155' }}
                    }},
                    name: tier.split(' ')[0] + ' Hazard'
                }};
            }});

            Plotly.newPlot('pcaScatterChart', pcaTraces, {{
                ...darkPlotlyLayout,
                title: '2D Principal Component Projection (' + selectedState + ')',
                xaxis: {{ title: 'PC1 (Flood Exposure & Basin Entrapment)' }},
                yaxis: {{ title: 'PC2 (Rainfall Extremes vs Inland)' }},
                height: 440
            }}, {{ responsive: true }});

            updateBoxFeatureChart();
        }}

        function updateBoxFeatureChart() {{
            const feat = document.getElementById('box-feature-select').value;
            const featLabel = document.getElementById('box-feature-select').options[document.getElementById('box-feature-select').selectedIndex].text;
            let scope = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                scope = allPlaces.filter(p => p.state === selectedState);
            }}

            const tiers = ['High Relative Hazard / Vulnerability', 'Moderate Relative Hazard / Vulnerability', 'Relatively Lower Hazard / Vulnerability'];
            const boxTraces = tiers.map(tier => {{
                const items = scope.filter(p => p.relative_hazard_level === tier);
                return {{
                    y: items.map(p => p[feat] || 0),
                    type: 'box',
                    name: tier.split(' ')[0] + ' Hazard',
                    marker: {{ color: colorMap[tier] }},
                    boxpoints: 'all',
                    jitter: 0.3,
                    pointpos: -1.8
                }};
            }});

            Plotly.newPlot('featureBoxChart', boxTraces, {{
                ...darkPlotlyLayout,
                title: 'Distribution of ' + featLabel + ' across Tiers in ' + selectedState,
                yaxis: {{ title: featLabel }},
                height: 360
            }}, {{ responsive: true }});
        }}

        function updateNationalComparison() {{
            const stateMap = {{}};
            allPlaces.forEach(p => {{
                const s = p.state;
                if (!stateMap[s]) {{
                    stateMap[s] = {{
                        state: s,
                        total: 0, high: 0,
                        districts: new Set(),
                        rainSum: 0, elevSum: 0, floodSum: 0, congSum: 0
                    }};
                }}
                stateMap[s].total++;
                if (p.relative_hazard_level.includes('High')) stateMap[s].high++;
                stateMap[s].districts.add(p.district);
                stateMap[s].rainSum += p.annual_rainfall_mm || 0;
                stateMap[s].elevSum += p.elevation_m || 0;
                stateMap[s].floodSum += p.historical_flood_inundation_frequency || 0;
                stateMap[s].congSum += p.drainage_congestion_index || 0;
            }});

            const states = Object.values(stateMap).map(s => ({{
                state: s.state,
                total: s.total,
                districts: s.districts.size,
                high: s.high,
                highPct: Number(((s.high / s.total) * 100).toFixed(1)),
                meanRain: Number((s.rainSum / s.total).toFixed(1)),
                meanElev: Number((s.elevSum / s.total).toFixed(1)),
                meanFlood: Number((s.floodSum / s.total).toFixed(2)),
                meanCong: Number((s.congSum / s.total).toFixed(2))
            }})).sort((a, b) => b.highPct - a.highPct);

            // Exact Streamlit Plotly Bar: State High Hazard %
            const stBar = {{
                x: states.map(s => s.state),
                y: states.map(s => s.highPct),
                type: 'bar',
                marker: {{
                    color: states.map(s => s.highPct),
                    colorscale: 'Reds',
                    showscale: true,
                    colorbar: {{ title: 'High Hazard (%)', thickness: 15 }}
                }}
            }};
            Plotly.newPlot('stateBarChart', [stBar], {{
                ...darkPlotlyLayout,
                title: 'Percentage of Monitored Settlements in High Hazard Tier (%)',
                xaxis: {{ tickangle: -45 }},
                yaxis: {{ title: 'High Hazard (%)', range: [0, 100] }},
                height: 410
            }}, {{ responsive: true }});

            // Exact Streamlit Plotly Scatter: State Climatology vs Topography
            const stScatter = {{
                x: states.map(s => s.meanRain),
                y: states.map(s => s.meanElev),
                mode: 'markers',
                text: states.map(s => `${{s.state}}<br>High: ${{s.highPct}}%`),
                marker: {{
                    size: states.map(s => Math.max(9, Math.min(26, s.total * 2.2))),
                    color: states.map(s => s.highPct),
                    colorscale: 'Viridis',
                    showscale: true,
                    colorbar: {{ title: 'High Hazard %', thickness: 15 }}
                }}
            }};
            Plotly.newPlot('stateScatterChart', [stScatter], {{
                ...darkPlotlyLayout,
                title: 'State Climatology vs Topography: Mean Rainfall vs Elevation',
                xaxis: {{ title: 'Mean Annual Rainfall (mm)' }},
                yaxis: {{ title: 'Mean Elevation (m AMSL)' }},
                height: 410
            }}, {{ responsive: true }});

            const tbody = document.getElementById('state-summary-tbody');
            tbody.innerHTML = '';
            states.forEach(s => {{
                const tr = document.createElement('tr');
                const redIntensity = Math.min(0.65, Math.max(0.1, s.highPct / 120.0));
                tr.innerHTML = `
                    <td><b>${{s.state}}</b></td>
                    <td>${{s.total}}</td>
                    <td>${{s.districts}}</td>
                    <td><span class="badge-red">${{s.high}}</span></td>
                    <td style="background: rgba(215, 48, 39, ${{redIntensity}}); color: #FFF; font-weight: bold;">${{s.highPct}}%</td>
                    <td>${{s.meanRain}} mm</td>
                    <td>${{s.meanElev}} m</td>
                    <td>${{s.meanFlood}}/5</td>
                    <td>${{s.meanCong}}/5</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function initMLTables() {{
            function fillTbody(tbodyId, data, rowFn) {{
                const tbody = document.getElementById(tbodyId);
                if (!tbody) return;
                tbody.innerHTML = '';
                data.forEach(item => {{
                    const tr = document.createElement('tr');
                    tr.innerHTML = rowFn(item);
                    tbody.appendChild(tr);
                }});
            }}

            fillTbody('tbody-kmeans', kmTableData, d => `
                <td><b>${{d.Algorithm || 'K-Means'}}</b></td>
                <td>${{d['Initialization Method'] || 'K-Means++'}}</td>
                <td>${{d['Number of Clusters (k)'] || 3}}</td>
                <td><span class="badge-blue">${{d['Silhouette Score'] || '0.52'}}</span></td>
                <td>${{d['Davies-Bouldin Index'] || '0.78'}}</td>
            `);

            fillTbody('tbody-hier', hierTableData, d => `
                <td><b>${{d['Linkage Criterion'] || 'Ward'}}</b></td>
                <td>${{d['Clusters (K)'] || 3}}</td>
                <td><span class="badge-blue">${{d['Silhouette Score'] || '0.48'}}</span></td>
                <td>${{d['Davies-Bouldin Index'] || '0.82'}}</td>
                <td>${{d['Cluster Distribution'] || 'N/A'}}</td>
            `);

            fillTbody('tbody-kmedoids', kmedTableData, d => `
                <td><b>${{d['Distance Metric'] || 'Manhattan (L1)'}}</b></td>
                <td>${{d['K (Clusters)'] || 3}}</td>
                <td><span class="badge-blue">${{d['Silhouette Score'] || '0.50'}}</span></td>
                <td>${{d['Davies-Bouldin Index'] || '0.79'}}</td>
                <td style="max-width: 180px; overflow: hidden; text-overflow: ellipsis;">${{d['Exemplar Medoids'] || 'N/A'}}</td>
            `);

            fillTbody('tbody-master', masterTableData, d => `
                <td><b>${{d.Algorithm || 'PAM L1'}}</b></td>
                <td>${{d.Clusters || 3}}</td>
                <td>${{d['Noise Points'] || 0}}</td>
                <td><span class="badge-blue">${{d['Silhouette Score'] || '0.51'}}</span></td>
                <td>${{d['Davies-Bouldin Index'] || '0.79'}}</td>
            `);
        }}

        function updateRegistryTable() {{
            const searchVal = (document.getElementById('registry-search').value || '').toLowerCase().trim();
            registryFiltered = filteredPlaces.filter(p => {{
                if (!searchVal) return true;
                return (
                    p.habitation_name.toLowerCase().includes(searchVal) ||
                    p.district.toLowerCase().includes(searchVal) ||
                    (p.mandal && p.mandal.toLowerCase().includes(searchVal)) ||
                    p.state.toLowerCase().includes(searchVal)
                );
            }});

            registryPage = 1;
            renderRegistryPage();
        }}

        function filterRegistryTable() {{
            updateRegistryTable();
        }}

        function renderRegistryPage() {{
            const tbody = document.getElementById('registry-tbody');
            tbody.innerHTML = '';

            const total = registryFiltered.length;
            const start = (registryPage - 1) * registryPageSize;
            const end = Math.min(start + registryPageSize, total);
            const pageItems = registryFiltered.slice(start, end);

            pageItems.forEach(p => {{
                const tier = p.relative_hazard_level || '';
                let badgeClass = 'badge-blue';
                if (tier.includes('High')) badgeClass = 'badge-red';
                else if (tier.includes('Moderate')) badgeClass = 'badge-orange';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b>${{p.habitation_name}}</b></td>
                    <td>${{p.state}}</td>
                    <td>${{p.district}}</td>
                    <td>${{p.mandal || 'N/A'}}</td>
                    <td><span class="${{badgeClass}}">${{tier}}</span></td>
                    <td>${{p.elevation_m.toFixed(1)}}</td>
                    <td>${{p.distance_to_river_km.toFixed(2)}}</td>
                    <td>${{p.historical_flood_inundation_frequency}}/5</td>
                    <td>${{p.drainage_congestion_index}}/5</td>
                    <td>${{p.annual_rainfall_mm.toFixed(1)}}</td>
                    <td>${{p.extreme_daily_rainfall_mm.toFixed(1)}}</td>
                    <td>${{Number(p.population || 0).toLocaleString()}}</td>
                    <td>${{Number(p.population_density_per_sqkm || 0).toLocaleString()}}</td>
                    <td>${{p.river_basin || 'Regional'}}</td>
                `;
                tbody.appendChild(tr);
            }});

            const totalPages = Math.ceil(total / registryPageSize) || 1;
            document.getElementById('registry-page-info').textContent = `Showing ${{total > 0 ? start + 1 : 0}}–${{end}} of ${{total}} habitations (Page ${{registryPage}} of ${{totalPages}})`;
            document.getElementById('data-section-sub').textContent = `Showing ${{total}} habitations matching State: ${{selectedState}}, District: ${{selectedDist}}, Place: ${{selectedPlace}}:`;
        }}

        function prevRegistryPage() {{
            if (registryPage > 1) {{
                registryPage--;
                renderRegistryPage();
            }}
        }}

        function nextRegistryPage() {{
            const totalPages = Math.ceil(registryFiltered.length / registryPageSize) || 1;
            if (registryPage < totalPages) {{
                registryPage++;
                renderRegistryPage();
            }}
        }}

        function downloadCSV() {{
            if (filteredPlaces.length === 0) return;
            const keys = [
                'habitation_name', 'state', 'district', 'mandal', 'relative_hazard_level',
                'elevation_m', 'distance_to_river_km', 'historical_flood_inundation_frequency',
                'drainage_congestion_index', 'annual_rainfall_mm', 'extreme_daily_rainfall_mm',
                'population', 'population_density_per_sqkm', 'river_basin'
            ];

            const csvRows = [];
            csvRows.push(keys.join(','));

            filteredPlaces.forEach(p => {{
                const row = keys.map(k => {{
                    let val = p[k] !== undefined && p[k] !== null ? String(p[k]) : '';
                    if (val.includes(',') || val.includes('"')) {{
                        val = '"' + val.replace(/"/g, '""') + '"';
                    }}
                    return val;
                }});
                csvRows.push(row.join(','));
            }});

            const csvString = csvRows.join(String.fromCharCode(10));
            const blob = new Blob([csvString], {{ type: 'text/csv;charset=utf-8;' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `flood_clusters_${{selectedState.replace(/\\s+/g, '_').toLowerCase()}}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }}
    </script>
</body>
</html>
"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated pixel-perfect Streamlit replica index.html ({len(html_content)} bytes)")

if __name__ == '__main__':
    generate_pixel_perfect_streamlit_html()
