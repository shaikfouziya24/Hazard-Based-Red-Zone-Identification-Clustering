import pandas as pd
import json

# Load master dataset
df = pd.read_csv('data/processed/india_habitations_complete.csv')

# Ensure clean types and dictionary list
records = df.to_dict(orient='records')
places_json = json.dumps(records, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIH26191: Pan-India Flood Hazard & Real-Time Alert System</title>
    <!-- Leaflet CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #1E3A8A;
            --primary-light: #3B82F6;
            --danger-high: #d73027;
            --danger-med: #fdae61;
            --danger-low: #4575b4;
            --bg-light: #F8FAFC;
            --card-bg: #FFFFFF;
            --text-dark: #0F172A;
            --text-muted: #64748B;
            --border: #E2E8F0;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        body {{
            background-color: var(--bg-light);
            color: var(--text-dark);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        /* Top Navigation Header */
        header {{
            background: #FFFFFF;
            border-bottom: 1px solid var(--border);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            z-index: 100;
        }}
        .header-title {{
            font-size: 19px;
            font-weight: 800;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .header-sub {{
            font-size: 12.5px;
            color: var(--text-muted);
            margin-top: 2px;
        }}
        .header-badges {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 20px;
            background: #EFF6FF;
            color: #1D4ED8;
            border: 1px solid #BFDBFE;
        }}
        .badge-live {{
            background: #ECFDF5;
            color: #047857;
            border: 1px solid #A7F3D0;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .pulse-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
            70% {{ box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
        }}

        /* Main Workspace Layout */
        .workspace {{
            display: flex;
            flex: 1;
            overflow: hidden;
        }}

        /* Left Control Sidebar */
        aside {{
            width: 340px;
            background: #FFFFFF;
            border-right: 1px solid var(--border);
            padding: 18px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
            box-shadow: 2px 0 6px rgba(0,0,0,0.03);
            z-index: 50;
        }}
        .control-group {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .control-label {{
            font-size: 12.5px;
            font-weight: 700;
            color: #334155;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        select, input[type="text"] {{
            width: 100%;
            padding: 9px 12px;
            border: 1.5px solid #CBD5E1;
            border-radius: 7px;
            font-size: 13px;
            background: #FFFFFF;
            color: var(--text-dark);
            outline: none;
            transition: border 0.2s;
        }}
        select:focus, input[type="text"]:focus {{
            border-color: var(--primary-light);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        }}

        /* Danger Tier Separation Checkboxes */
        .hazard-filters {{
            background: #F8FAFC;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .hazard-toggle {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
            cursor: pointer;
            padding: 6px 10px;
            border-radius: 6px;
            transition: background 0.15s;
        }}
        .hazard-toggle:hover {{
            background: #EDF2F7;
        }}
        .hazard-toggle-left {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
        }}
        .hazard-count-badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 12px;
            color: #FFFFFF;
        }}

        /* Content Area */
        main {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            background: #F1F5F9;
        }}

        /* KPI Metric Cards Row */
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            padding: 16px 20px 0 20px;
        }}
        .kpi-card {{
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: 9px;
            padding: 12px 14px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        .kpi-title {{
            font-size: 11.5px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}
        .kpi-value {{
            font-size: 20px;
            font-weight: 800;
            color: var(--text-dark);
        }}
        .kpi-sub {{
            font-size: 11px;
            font-weight: 600;
            color: var(--primary-light);
        }}

        /* Live Alert Banner */
        .live-alert-container {{
            padding: 12px 20px;
        }}
        .live-alert-card {{
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
            color: #FFFFFF;
            border-radius: 9px;
            padding: 14px 18px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .alert-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .alert-pill {{
            font-size: 13.5px;
            font-weight: 800;
            padding: 4px 12px;
            border-radius: 20px;
            color: #FFFFFF;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .alert-station {{
            font-size: 13px;
            font-weight: 600;
            color: #E2E8F0;
        }}
        .alert-metrics {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 2px;
        }}
        .alert-metric-pill {{
            font-size: 11.5px;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.25);
            padding: 4px 10px;
            border-radius: 6px;
            color: #FFFFFF;
        }}

        /* View Tabs */
        .tabs-header {{
            display: flex;
            gap: 6px;
            padding: 0 20px;
            border-bottom: 1px solid var(--border);
            background: #FFFFFF;
        }}
        .tab-btn {{
            padding: 12px 18px;
            font-size: 13px;
            font-weight: 700;
            color: var(--text-muted);
            border: none;
            background: transparent;
            cursor: pointer;
            border-bottom: 2.5px solid transparent;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }}
        .tab-btn.active {{
            color: var(--primary);
            border-bottom-color: var(--primary);
        }}
        .tab-btn:hover:not(.active) {{
            color: var(--text-dark);
        }}

        /* Map & Tab Views */
        .tab-content {{
            flex: 1;
            display: none;
            flex-direction: column;
            padding: 16px 20px;
        }}
        .tab-content.active {{
            display: flex;
        }}
        #map-view {{
            width: 100%;
            height: 580px;
            border-radius: 9px;
            border: 1px solid var(--border);
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            z-index: 10;
        }}

        /* Table View */
        .table-container {{
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: 9px;
            overflow: auto;
            max-height: 600px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12.5px;
            text-align: left;
        }}
        thead {{
            background: #F8FAFC;
            position: sticky;
            top: 0;
            z-index: 1;
        }}
        th, td {{
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            font-weight: 700;
            color: #334155;
            white-space: nowrap;
        }}
        tbody tr:hover {{
            background: #F1F5F9;
        }}

        /* Disclaimer Footer */
        .disclaimer-banner {{
            background: #FEF3C7;
            border-left: 4px solid #F59E0B;
            padding: 8px 14px;
            border-radius: 4px;
            font-size: 12px;
            color: #92400E;
            margin: 0 20px 14px 20px;
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div>
            <div class="header-title">
                🌊 Hazard-Based Red-Zone Identification for Vulnerable Habitations
            </div>
            <div class="header-sub">
                <b>Project ID: SIH26191</b> | Pan-India Multi-State System (All 26 Andhra Pradesh Districts Included) | B.Tech Unsupervised ML Project
            </div>
        </div>
        <div class="header-badges">
            <span class="badge">229 Habitations</span>
            <span class="badge">92 Districts</span>
            <span class="badge-live"><div class="pulse-dot"></div> Live Weather Feed</span>
        </div>
    </header>

    <div class="workspace">
        <!-- Sidebar Controls -->
        <aside>
            <div style="font-size: 14px; font-weight: 800; color: var(--primary); margin-bottom: 4px;">
                🗺️ Geographic Navigation
            </div>

            <!-- 1. State Selector -->
            <div class="control-group">
                <label class="control-label" for="state-select">🇮🇳 1. Select State / Region</label>
                <select id="state-select" onchange="onStateChange()">
                    <option value="All India (Pan-India Overview)">All India (Pan-India Overview)</option>
                </select>
            </div>

            <!-- 2. District Selector -->
            <div class="control-group">
                <label class="control-label" for="district-select">📍 2. Select District</label>
                <select id="district-select" onchange="onDistrictChange()">
                    <option value="All Districts in State">All Districts in State</option>
                </select>
            </div>

            <!-- 3. Particular Location Selector -->
            <div class="control-group">
                <label class="control-label" for="location-select">🏘️ 3. Select Particular Location</label>
                <select id="location-select" onchange="onLocationChange()">
                    <option value="All Locations">All Locations in Scope</option>
                </select>
            </div>

            <!-- 4. Danger Tier Separation Filters -->
            <div class="control-group">
                <label class="control-label">⚠️ 4. Separate Danger Levels</label>
                <div class="hazard-filters">
                    <label class="hazard-toggle">
                        <div class="hazard-toggle-left">
                            <input type="checkbox" id="check-high" checked onchange="applyFilters()">
                            <span style="color: #d73027;">🔴 High Danger</span>
                        </div>
                        <span class="hazard-count-badge" id="count-high" style="background: #d73027;">0</span>
                    </label>
                    <label class="hazard-toggle">
                        <div class="hazard-toggle-left">
                            <input type="checkbox" id="check-med" checked onchange="applyFilters()">
                            <span style="color: #d97706;">🟡 Medium Danger</span>
                        </div>
                        <span class="hazard-count-badge" id="count-med" style="background: #d97706;">0</span>
                    </label>
                    <label class="hazard-toggle">
                        <div class="hazard-toggle-left">
                            <input type="checkbox" id="check-low" checked onchange="applyFilters()">
                            <span style="color: #3b82f6;">🔵 Low Danger</span>
                        </div>
                        <span class="hazard-count-badge" id="count-low" style="background: #3b82f6;">0</span>
                    </label>
                </div>
            </div>

            <div style="margin-top: auto; padding-top: 10px; border-top: 1px solid var(--border); font-size: 11.5px; color: var(--text-muted); line-height: 1.4;">
                <b>Climatology:</b> IMD 24-Yr Normals (0.25°)<br>
                <b>Elevation:</b> Copernicus DEM 90m<br>
                <b>Disaster History:</b> IIT Delhi IFI-Impacts
            </div>
        </aside>

        <!-- Main Display -->
        <main>
            <!-- Top KPI Cards -->
            <div class="kpi-row">
                <div class="kpi-card">
                    <div class="kpi-title">🔴 High Danger Places</div>
                    <div class="kpi-value" id="kpi-high-val" style="color: #d73027;">0</div>
                    <div class="kpi-sub" id="kpi-high-sub">0% of active</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">🟡 Medium Danger</div>
                    <div class="kpi-value" id="kpi-med-val" style="color: #d97706;">0</div>
                    <div class="kpi-sub" id="kpi-med-sub">0% of active</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">🔵 Low Danger</div>
                    <div class="kpi-value" id="kpi-low-val" style="color: #3b82f6;">0</div>
                    <div class="kpi-sub" id="kpi-low-sub">0% of active</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">🌧️ Mean Annual Rain</div>
                    <div class="kpi-value" id="kpi-rain-val">0 mm</div>
                    <div class="kpi-sub">IMD Long-Term Mean</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">⛰️ Mean Elevation</div>
                    <div class="kpi-value" id="kpi-elev-val">0 m</div>
                    <div class="kpi-sub">Copernicus DEM 90m</div>
                </div>
            </div>

            <!-- Live Alert Station -->
            <div class="live-alert-container">
                <div class="live-alert-card" id="alert-card-box">
                    <div class="alert-header">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span class="alert-pill" id="live-alert-pill" style="background: #16A34A;">🟢 GREEN STATUS</span>
                            <span class="alert-station" id="live-station-name">Station: Pan-India National Network</span>
                        </div>
                        <div style="font-size: 12px; opacity: 0.9;" id="live-obs-time">
                            🕒 Live Observation Connected | Open-Meteo Feed
                        </div>
                    </div>
                    <div style="font-size: 13px; line-height: 1.4; color: #F1F5F9;" id="live-alert-desc">
                        Optimal conditions. Normal baseline status with active multi-hazard monitoring.
                    </div>
                    <div class="alert-metrics">
                        <span class="alert-metric-pill" id="metric-temp">🌡️ Temp: -- °C</span>
                        <span class="alert-metric-pill" id="metric-humidity">💧 Humidity: -- %</span>
                        <span class="alert-metric-pill" id="metric-rain">🌧️ Live Rain: 0.0 mm/h</span>
                        <span class="alert-metric-pill" id="metric-past24">🌊 Past 24h Rain: 0.0 mm</span>
                        <span class="alert-metric-pill" id="metric-cond">🌤️ Condition: Loading...</span>
                        <span class="alert-metric-pill" id="metric-wind">💨 Wind: -- km/h</span>
                        <span class="alert-metric-pill" id="metric-elev">⛰️ Surface Elevation: -- m</span>
                    </div>
                </div>
            </div>

            <!-- Disclaimer -->
            <div class="disclaimer-banner">
                ⚠️ <b>Academic Mandate:</b> This system is an unsupervised machine learning exploratory decision-support framework.
                Cluster groupings represent relative statistical vulnerability based on multi-criteria biophysical features.
                Clustering alone <b>does NOT constitute an official government disaster warning or statutory red-zone demarcation</b>.
            </div>

            <!-- Tabs Navigation -->
            <div class="tabs-header">
                <button class="tab-btn active" onclick="switchTab('tab-map')">🗺️ Interactive Geospatial Map</button>
                <button class="tab-btn" onclick="switchTab('tab-districts')">🏛️ All Districts in State Matrix</button>
                <button class="tab-btn" onclick="switchTab('tab-data')">📋 All Places Registry & Data Explorer</button>
            </div>

            <!-- Tab 1: Map View -->
            <div id="tab-map" class="tab-content active">
                <div id="map-view"></div>
            </div>

            <!-- Tab 2: All Districts Matrix -->
            <div id="tab-districts" class="tab-content">
                <div class="table-container">
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
                                <th>Mean River Dist (km)</th>
                                <th>Annual Rainfall (mm)</th>
                            </tr>
                        </thead>
                        <tbody id="districts-table-body"></tbody>
                    </table>
                </div>
            </div>

            <!-- Tab 3: Data Explorer -->
            <div id="tab-data" class="tab-content">
                <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <input type="text" id="table-search" placeholder="🔍 Search habitation, district, mandal..." oninput="renderDataTable()" style="max-width: 320px;">
                    <button onclick="downloadCSV()" style="padding: 8px 14px; background: var(--primary); color: #FFF; border: none; border-radius: 6px; font-weight: 600; cursor: pointer;">
                        📥 Download Filtered Data (CSV)
                    </button>
                </div>
                <div class="table-container">
                    <table id="data-table">
                        <thead>
                            <tr>
                                <th>Habitation Name</th>
                                <th>State</th>
                                <th>District</th>
                                <th>Mandal</th>
                                <th>Danger Tier</th>
                                <th>Elevation (m)</th>
                                <th>River Dist (km)</th>
                                <th>Annual Rain (mm)</th>
                                <th>Max Daily Rain (mm)</th>
                                <th>Population</th>
                                <th>Drainage Score</th>
                            </tr>
                        </thead>
                        <tbody id="data-table-body"></tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <!-- Application Logic & Data -->
    <script>
        const allPlaces = {places_json};

        // State Geographies for Centering
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

        // Initialize Map
        let map = L.map('map-view').setView([21.5, 80.0], 5);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);

        let markersLayer = L.layerGroup().addTo(map);
        let selectedMarkerHalo = null;

        // River Polylines
        const krishnaCoords = [
            [16.580, 80.360], [16.592, 80.450], [16.590, 80.522], [16.550, 80.565],
            [16.507, 80.605], [16.480, 80.640], [16.440, 80.720], [16.360, 80.780],
            [16.320, 80.825], [16.185, 80.795], [16.122, 80.932], [16.022, 80.918], [15.945, 80.915]
        ];
        L.polyline(krishnaCoords, {{ color: '#0055ff', weight: 4, opacity: 0.8 }}).bindTooltip("Krishna River (Prakasam Barrage)").addTo(map);

        const budameruCoords = [
            [16.630, 80.540], [16.562, 80.615], [16.538, 80.638], [16.522, 80.665], [16.520, 80.750]
        ];
        L.polyline(budameruCoords, {{ color: '#00aaff', weight: 3, dashArray: '6, 6', opacity: 0.8 }}).bindTooltip("Budameru Rivulet Drainage Floodway").addTo(map);

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

            // Zoom map to state
            const geo = stateGeo[selectedState] || {{ center: [21.5, 80.0], zoom: 5 }};
            map.setView(geo.center, geo.zoom);

            onDistrictChange();
        }}

        function onDistrictChange() {{
            const selectedState = stateSelect.value;
            const selectedDist = document.getElementById('district-select').value;
            const locSelect = document.getElementById('location-select');
            locSelect.innerHTML = '<option value="All Locations">All Locations in Scope</option>';

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
            if (locName !== "All Locations") {{
                const place = allPlaces.find(p => p.habitation_name === locName);
                if (place) {{
                    map.flyTo([place.latitude, place.longitude], 12, {{ animate: true, duration: 1.2 }});
                    
                    if (selectedMarkerHalo) {{
                        map.removeLayer(selectedMarkerHalo);
                    }}
                    selectedMarkerHalo = L.circleMarker([place.latitude, place.longitude], {{
                        radius: 13,
                        color: '#FFD700',
                        weight: 4,
                        fillColor: '#FFD700',
                        fillOpacity: 0.3
                    }}).addTo(map);

                    fetchLiveWeather(place.latitude, place.longitude, place.habitation_name, place.relative_hazard_level, place.elevation_m);
                }}
            }} else {{
                if (selectedMarkerHalo) {{
                    map.removeLayer(selectedMarkerHalo);
                    selectedMarkerHalo = null;
                }}
            }}
            applyFilters();
        }}

        function applyFilters() {{
            const selectedState = stateSelect.value;
            const selectedDist = document.getElementById('district-select').value;
            const selectedLoc = document.getElementById('location-select').value;

            const showHigh = document.getElementById('check-high').checked;
            const showMed = document.getElementById('check-med').checked;
            const showLow = document.getElementById('check-low').checked;

            let filtered = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                filtered = filtered.filter(p => p.state === selectedState);
            }}
            if (selectedDist !== "All Districts in State") {{
                filtered = filtered.filter(p => p.district === selectedDist);
            }}
            if (selectedLoc !== "All Locations") {{
                filtered = filtered.filter(p => p.habitation_name === selectedLoc);
            }}

            // Count Tiers in this geographic scope
            const countHigh = filtered.filter(p => p.relative_hazard_level.includes('High')).length;
            const countMed = filtered.filter(p => p.relative_hazard_level.includes('Moderate')).length;
            const countLow = filtered.filter(p => p.relative_hazard_level.includes('Lower')).length;

            document.getElementById('count-high').textContent = countHigh;
            document.getElementById('count-med').textContent = countMed;
            document.getElementById('count-low').textContent = countLow;

            // Apply danger tier separation filters
            filtered = filtered.filter(p => {{
                if (p.relative_hazard_level.includes('High') && !showHigh) return false;
                if (p.relative_hazard_level.includes('Moderate') && !showMed) return false;
                if (p.relative_hazard_level.includes('Lower') && !showLow) return false;
                return true;
            }});

            // Update KPIs
            const total = filtered.length;
            document.getElementById('kpi-high-val').textContent = countHigh;
            document.getElementById('kpi-high-sub').textContent = total > 0 ? ((countHigh / total) * 100).toFixed(1) + "% of active" : "0%";

            document.getElementById('kpi-med-val').textContent = countMed;
            document.getElementById('kpi-med-sub').textContent = total > 0 ? ((countMed / total) * 100).toFixed(1) + "% of active" : "0%";

            document.getElementById('kpi-low-val').textContent = countLow;
            document.getElementById('kpi-low-sub').textContent = total > 0 ? ((countLow / total) * 100).toFixed(1) + "% of active" : "0%";

            const meanRain = total > 0 ? (filtered.reduce((s, p) => s + p.annual_rainfall_mm, 0) / total).toFixed(1) : 0;
            document.getElementById('kpi-rain-val').textContent = meanRain + " mm";

            const meanElev = total > 0 ? (filtered.reduce((s, p) => s + p.elevation_m, 0) / total).toFixed(1) : 0;
            document.getElementById('kpi-elev-val').textContent = meanElev + " m";

            // Render Map Markers
            renderMapMarkers(filtered);
            renderDistrictsTable();
            renderDataTable();
        }}

        function renderMapMarkers(places) {{
            markersLayer.clearLayers();

            places.forEach(p => {{
                let color = '#4575b4'; // Blue for Low
                let tierLabel = 'Low Danger';
                if (p.relative_hazard_level.includes('High')) {{
                    color = '#d73027'; // Red
                    tierLabel = 'High Danger';
                }} else if (p.relative_hazard_level.includes('Moderate')) {{
                    color = '#fdae61'; // Yellow/Orange
                    tierLabel = 'Medium Danger';
                }}

                const popupHtml = `
                    <div style="font-family: Arial; font-size: 12px; width: 250px; line-height: 1.4;">
                        <b style="font-size: 14px; color: ${{color}};">${{p.habitation_name}}</b><br>
                        <b>State:</b> ${{p.state}} | <b>District:</b> ${{p.district}}<br>
                        <b>Danger Level:</b> <span style="font-weight: bold; color: ${{color}};">${{tierLabel}}</span><br>
                        <hr style="margin: 5px 0;">
                        <b>Elevation:</b> ${{p.elevation_m.toFixed(1)}} m AMSL<br>
                        <b>Distance to River:</b> ${{p.distance_to_river_km.toFixed(2)}} km<br>
                        <b>Annual Rain:</b> ${{p.annual_rainfall_mm.toFixed(1)}} mm<br>
                        <b>Max Daily Rain:</b> ${{p.extreme_daily_rainfall_mm.toFixed(0)}} mm<br>
                        <b>Flood Inundations:</b> ${{p.historical_flood_inundation_frequency}}/5<br>
                        <b>Drainage Congestion:</b> ${{p.drainage_congestion_index}}/5<br>
                        <b>Population Density:</b> ${{Math.round(p.population_density_per_sqkm).toLocaleString()}} /km²
                    </div>
                `;

                const marker = L.circleMarker([p.latitude, p.longitude], {{
                    radius: p.relative_hazard_level.includes('High') ? 7 : 5.5,
                    fillColor: color,
                    color: '#000000',
                    weight: 1,
                    opacity: 0.9,
                    fillOpacity: 0.85
                }}).bindPopup(popupHtml).bindTooltip(`📍 ${{p.habitation_name}} (${{tierLabel}})`);

                marker.on('click', () => {{
                    fetchLiveWeather(p.latitude, p.longitude, p.habitation_name, p.relative_hazard_level, p.elevation_m);
                }});

                markersLayer.addLayer(marker);
            }});
        }}

        // Live Real-Time Weather Fetching (Open-Meteo API)
        async function fetchLiveWeather(lat, lon, name, hazardTier, elevation) {{
            document.getElementById('live-station-name').textContent = "Station: " + name;
            document.getElementById('live-alert-desc').textContent = "Fetching real-time satellite & ground meteorological telemetry...";

            try {{
                const url = `https://api.open-meteo.com/v1/forecast?latitude=${{lat.toFixed(4)}}&longitude=${{lon.toFixed(4)}}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m&past_days=1&hourly=precipitation&timezone=Asia%2FKolkata`;
                const res = await fetch(url);
                const data = await res.json();

                const cur = data.current || {{}};
                const hourly = (data.hourly && data.hourly.precipitation) ? data.hourly.precipitation : [];
                const past24h = hourly.length >= 24 ? hourly.slice(-24).reduce((a, b) => a + b, 0).toFixed(1) : (cur.rain || 0).toFixed(1);

                document.getElementById('metric-temp').textContent = `🌡️ Temp: ${{cur.temperature_2m || '--'}} °C (Feels ${{cur.apparent_temperature || '--'}} °C)`;
                document.getElementById('metric-humidity').textContent = `💧 Humidity: ${{cur.relative_humidity_2m || '--'}} %`;
                document.getElementById('metric-rain').textContent = `🌧️ Live Rain: ${{cur.rain || 0}} mm/h`;
                document.getElementById('metric-past24').textContent = `🌊 Past 24h Rain: ${{past24h}} mm`;
                document.getElementById('metric-wind').textContent = `💨 Wind: ${{cur.wind_speed_10m || '--'}} km/h`;
                document.getElementById('metric-elev').textContent = `⛰️ Surface Elevation: ${{elevation ? elevation.toFixed(1) : '--'}} m`;

                const wmoMap = {{
                    0: "Clear Sky ☀️", 1: "Mainly Clear 🌤️", 2: "Partly Cloudy ⛅", 3: "Overcast ☁️",
                    51: "Light Drizzle 🌦️", 61: "Rain 🌧️", 65: "Heavy Rain 🌧️", 80: "Showers ⛈️", 95: "Thunderstorm ⚡⛈️"
                }};
                document.getElementById('metric-cond').textContent = `Condition: ${{wmoMap[cur.weather_code] || 'Observed Clear ☀️'}}`;

                // Compute Dynamic Alert
                const pastRainNum = parseFloat(past24h) || 0;
                const rainRateNum = parseFloat(cur.rain) || 0;
                let alertLevel = "🟢 GREEN STATUS";
                let alertColor = "#16A34A";
                let alertDesc = "Optimal conditions. Normal baseline status with low weather trigger.";

                if (hazardTier.includes('High')) {{
                    if (pastRainNum >= 35 || rainRateNum >= 10) {{
                        alertLevel = "🚨 RED ALERT (CRITICAL)";
                        alertColor = "#DC2626";
                        alertDesc = "High morphological baseline vulnerability coupled with severe active precipitation! Inundation risk critical.";
                    }} else if (pastRainNum >= 15 || rainRateNum >= 4) {{
                        alertLevel = "🟧 ORANGE ALERT (ELEVATED)";
                        alertColor = "#EA580C";
                        alertDesc = "Active rainfall detected over low-lying floodway terrain. Drainage channels approaching surcharge.";
                    }} else if (pastRainNum >= 5 || rainRateNum > 0) {{
                        alertLevel = "🟨 YELLOW WATCH (MONITOR)";
                        alertColor = "#D97706";
                        alertDesc = "Light rain observed over high baseline vulnerability terrain. Maintain sluice gate monitoring.";
                    }}
                }} else if (hazardTier.includes('Moderate')) {{
                    if (pastRainNum >= 50 || rainRateNum >= 15) {{
                        alertLevel = "🚨 RED ALERT (CRITICAL)";
                        alertColor = "#DC2626";
                        alertDesc = "Severe rainfall exceeding intermediate terrain drainage capacity.";
                    }} else if (pastRainNum >= 25 || rainRateNum >= 5) {{
                        alertLevel = "🟧 ORANGE ALERT (ELEVATED)";
                        alertColor = "#EA580C";
                        alertDesc = "Localized surface waterlogging anticipated.";
                    }}
                }}

                const pill = document.getElementById('live-alert-pill');
                pill.textContent = alertLevel;
                pill.style.background = alertColor;
                document.getElementById('live-alert-desc').textContent = alertDesc;
                document.getElementById('live-obs-time').textContent = `🕒 Observation: ${{cur.time ? cur.time.replace('T', ' ') : 'Live'}} IST | API Connected`;

            }} catch (e) {{
                document.getElementById('live-alert-desc').textContent = "Real-time weather query ready. Select a place to inspect live observations.";
            }}
        }}

        // Tab Switching
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');

            if (tabId === 'tab-map') {{
                setTimeout(() => {{ map.invalidateSize(); }}, 200);
            }}
        }}

        // Render Districts Table
        function renderDistrictsTable() {{
            const selectedState = stateSelect.value;
            const filtered = selectedState === "All India (Pan-India Overview)" 
                ? allPlaces 
                : allPlaces.filter(p => p.state === selectedState);

            const distMap = {{}};
            filtered.forEach(p => {{
                if (!distMap[p.district]) {{
                    distMap[p.district] = {{ total: 0, high: 0, med: 0, low: 0, elev: 0, dist: 0, rain: 0 }};
                }}
                distMap[p.district].total++;
                if (p.relative_hazard_level.includes('High')) distMap[p.district].high++;
                else if (p.relative_hazard_level.includes('Moderate')) distMap[p.district].med++;
                else distMap[p.district].low++;
                distMap[p.district].elev += p.elevation_m;
                distMap[p.district].dist += p.distance_to_river_km;
                distMap[p.district].rain += p.annual_rainfall_mm;
            }});

            const tbody = document.getElementById('districts-table-body');
            tbody.innerHTML = '';

            Object.keys(distMap).sort().forEach(d => {{
                const info = distMap[d];
                const highPct = ((info.high / info.total) * 100).toFixed(1);
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b>${{d}}</b></td>
                    <td>${{info.total}}</td>
                    <td style="color: #d73027; font-weight: bold;">${{info.high}}</td>
                    <td style="color: #d97706; font-weight: bold;">${{info.med}}</td>
                    <td style="color: #3b82f6; font-weight: bold;">${{info.low}}</td>
                    <td><span style="background: rgba(215, 48, 39, 0.15); color: #d73027; padding: 2px 8px; border-radius: 4px; font-weight: 700;">${{highPct}}%</span></td>
                    <td>${{(info.elev / info.total).toFixed(1)}} m</td>
                    <td>${{(info.dist / info.total).toFixed(2)}} km</td>
                    <td>${{(info.rain / info.total).toFixed(1)}} mm</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Render Data Table
        function renderDataTable() {{
            const search = document.getElementById('table-search').value.toLowerCase();
            const selectedState = stateSelect.value;
            const selectedDist = document.getElementById('district-select').value;

            let filtered = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") {{
                filtered = filtered.filter(p => p.state === selectedState);
            }}
            if (selectedDist !== "All Districts in State") {{
                filtered = filtered.filter(p => p.district === selectedDist);
            }}
            if (search) {{
                filtered = filtered.filter(p => 
                    p.habitation_name.toLowerCase().includes(search) || 
                    p.district.toLowerCase().includes(search) ||
                    (p.mandal && p.mandal.toLowerCase().includes(search))
                );
            }}

            const tbody = document.getElementById('data-table-body');
            tbody.innerHTML = '';

            filtered.slice(0, 100).forEach(p => {{
                let badgeColor = '#4575b4';
                let tierText = 'Low Danger';
                if (p.relative_hazard_level.includes('High')) {{
                    badgeColor = '#d73027';
                    tierText = 'High Danger';
                }} else if (p.relative_hazard_level.includes('Moderate')) {{
                    badgeColor = '#d97706';
                    tierText = 'Medium Danger';
                }}

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b>${{p.habitation_name}}</b></td>
                    <td>${{p.state}}</td>
                    <td>${{p.district}}</td>
                    <td>${{p.mandal || 'N/A'}}</td>
                    <td><span style="color: ${{badgeColor}}; font-weight: bold;">${{tierText}}</span></td>
                    <td>${{p.elevation_m.toFixed(1)}} m</td>
                    <td>${{p.distance_to_river_km.toFixed(2)}} km</td>
                    <td>${{p.annual_rainfall_mm.toFixed(1)}} mm</td>
                    <td>${{p.extreme_daily_rainfall_mm.toFixed(0)}} mm</td>
                    <td>${{p.population.toLocaleString()}}</td>
                    <td>${{p.drainage_congestion_index}}/5</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function downloadCSV() {{
            const selectedState = stateSelect.value;
            const selectedDist = document.getElementById('district-select').value;
            let filtered = allPlaces;
            if (selectedState !== "All India (Pan-India Overview)") filtered = filtered.filter(p => p.state === selectedState);
            if (selectedDist !== "All Districts in State") filtered = filtered.filter(p => p.district === selectedDist);

            const headers = ['habitation_name', 'state', 'district', 'mandal', 'relative_hazard_level', 'elevation_m', 'distance_to_river_km', 'annual_rainfall_mm', 'extreme_daily_rainfall_mm', 'population', 'drainage_congestion_index'];
            const rows = [headers.join(',')];

            filtered.forEach(p => {{
                rows.push([
                    `"${{p.habitation_name}}"`,
                    `"${{p.state}}"`,
                    `"${{p.district}}"`,
                    `"${{p.mandal || ''}}"`,
                    `"${{p.relative_hazard_level}}"`,
                    p.elevation_m,
                    p.distance_to_river_km,
                    p.annual_rainfall_mm,
                    p.extreme_daily_rainfall_mm,
                    p.population,
                    p.drainage_congestion_index
                ].join(','));
            }});

            const blob = new Blob([rows.join('\\n')], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.setAttribute('href', url);
            a.setAttribute('download', `flood_hazard_data_${{selectedState.replace(/\\s+/g, '_').toLowerCase()}}.csv`);
            a.click();
        }}

        // Initial trigger
        onStateChange();
        // Initial live weather for Vijayawada
        fetchLiveWeather(16.5062, 80.6480, "Vijayawada Region (Capital Basin)", "High Relative Hazard / Vulnerability", 21.0);
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated index.html with {len(records)} habitations and complete interactive UI!")
