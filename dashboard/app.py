import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import requests
import datetime
import os

st.set_page_config(
    page_title="SIH26191: Pan-India Flood Hazard & Real-Time Alert System",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Aesthetic Styling
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 800;
        color: #60A5FA;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #94A3B8;
        margin-bottom: 12px;
    }
    .disclaimer-box {
        background-color: #1E222D;
        border-left: 4px solid #F59E0B;
        padding: 9px 14px;
        border-radius: 4px;
        font-size: 12.5px;
        color: #FDE68A;
        margin-bottom: 14px;
    }
    .live-alert-card {
        padding: 16px 20px;
        border-radius: 8px;
        color: #ffffff;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .metric-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Load Processed Data (Pan-India Master Dataset)
@st.cache_data
def load_data():
    df_path = "data/processed/india_habitations_complete.csv"
    if not os.path.exists(df_path):
        df_path = "../data/processed/india_habitations_complete.csv"
    if not os.path.exists(df_path):
        df_path = "data/processed/habitations_complete_analysis.csv"
        df = pd.read_csv(df_path)
        df['state'] = 'Andhra Pradesh'
        df['river_basin'] = 'Krishna Basin'
        return df
    return pd.read_csv(df_path)

df = load_data()

# Live Real-Time Weather Fetching Function (Open-Meteo)
@st.cache_data(ttl=300)
def fetch_live_weather(lat, lon):
    """
    Fetches real-time weather and past 24h precipitation from Open-Meteo API.
    Cached for 5 minutes (300s) to balance freshness and low latency.
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat:.4f}&longitude={lon:.4f}&"
            f"current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,surface_pressure,wind_speed_10m&"
            f"past_days=1&hourly=precipitation&timezone=Asia%2FKolkata"
        )
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            d = res.json()
            cur = d.get('current', {})
            hourly = d.get('hourly', {}).get('precipitation', [])
            past_24h_rain = sum(hourly[-24:]) if len(hourly) >= 24 else float(cur.get('rain', 0.0))
            return {
                'status': 'success',
                'time': cur.get('time', ''),
                'temp_c': cur.get('temperature_2m', 0.0),
                'feels_like_c': cur.get('apparent_temperature', 0.0),
                'humidity_pct': cur.get('relative_humidity_2m', 0),
                'precip_mm': cur.get('precipitation', 0.0),
                'rain_rate_mmh': cur.get('rain', 0.0),
                'past_24h_rain_mm': round(past_24h_rain, 1),
                'weather_code': cur.get('weather_code', 0),
                'wind_kmh': cur.get('wind_speed_10m', 0.0),
                'pressure_hpa': cur.get('surface_pressure', 1013.0)
            }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    return {'status': 'unavailable'}

def get_wmo_description(code):
    wmo_map = {
        0: ("Clear Sky", "☀️", "#10B981"),
        1: ("Mainly Clear", "🌤️", "#34D399"),
        2: ("Partly Cloudy", "⛅", "#60A5FA"),
        3: ("Overcast", "☁️", "#6B7280"),
        45: ("Foggy", "🌫️", "#9CA3AF"),
        48: ("Rime Fog", "🌫️", "#9CA3AF"),
        51: ("Light Drizzle", "🌦️", "#38BDF8"),
        53: ("Moderate Drizzle", "🌧️", "#0284C7"),
        55: ("Dense Drizzle", "🌧️", "#0369A1"),
        61: ("Slight Rain", "🌦️", "#60A5FA"),
        63: ("Moderate Rain", "🌧️", "#2563EB"),
        65: ("Heavy Rain", "🌧️", "#1D4ED8"),
        80: ("Slight Showers", "🌦️", "#38BDF8"),
        81: ("Moderate Showers", "🌧️", "#0284C7"),
        82: ("Violent Showers", "⛈️", "#DC2626"),
        95: ("Thunderstorm", "⚡⛈️", "#DC2626"),
        96: ("Thunderstorm with Hail", "⚡🌨️", "#B91C1C"),
        99: ("Severe Thunderstorm", "⚡🌊", "#7F1D1D")
    }
    return wmo_map.get(code, ("Observed Weather", "🌦️", "#4B5563"))

def compute_dynamic_flood_alert(baseline_hazard_tier, past_24h_rain, rain_rate):
    """
    Synthesizes Unsupervised ML Baseline Hazard Cluster with Real-Time Rain Observation.
    Produces actionable dynamic multi-hazard alert level.
    """
    if 'High' in baseline_hazard_tier:
        if past_24h_rain >= 35.0 or rain_rate >= 10.0:
            return {
                'level': 'RED ALERT (CRITICAL RISK)',
                'icon': '🚨',
                'bg_color': '#DC2626',
                'text_color': '#FFFFFF',
                'desc': 'High morphological baseline vulnerability coupled with severe active/antecedent rainfall. High probability of inundation and drainage surcharge.'
            }
        elif past_24h_rain >= 15.0 or rain_rate >= 4.0:
            return {
                'level': 'ORANGE ALERT (ELEVATED RISK)',
                'icon': '🟧',
                'bg_color': '#EA580C',
                'text_color': '#FFFFFF',
                'desc': 'Active rainfall detected over low-lying / floodway terrain. Drainage channels nearing capacity; localized waterlogging anticipated.'
            }
        elif past_24h_rain >= 5.0 or rain_rate > 0.0:
            return {
                'level': 'YELLOW WATCH (MONITOR)',
                'icon': '🟨',
                'bg_color': '#D97706',
                'text_color': '#FFFFFF',
                'desc': 'Light rain observed over high baseline vulnerability terrain. Maintain vigilance on drainage sluices and local canal levels.'
            }
        else:
            return {
                'level': 'GREEN STATUS (NORMAL / DRY)',
                'icon': '🟢',
                'bg_color': '#16A34A',
                'text_color': '#FFFFFF',
                'desc': 'High baseline morphological vulnerability, but current weather is dry/clear. No immediate precipitation trigger active.'
            }
    elif 'Moderate' in baseline_hazard_tier:
        if past_24h_rain >= 50.0 or rain_rate >= 15.0:
            return {
                'level': 'RED ALERT (CRITICAL RISK)',
                'icon': '🚨',
                'bg_color': '#DC2626',
                'text_color': '#FFFFFF',
                'desc': 'Extreme localized precipitation surpassing intermediate terrain absorption and drainage thresholds.'
            }
        elif past_24h_rain >= 25.0 or rain_rate >= 5.0:
            return {
                'level': 'ORANGE ALERT (ELEVATED RISK)',
                'icon': '🟧',
                'bg_color': '#EA580C',
                'text_color': '#FFFFFF',
                'desc': 'Persistent rainfall accumulating over moderate hazard settlement. Urban runoff and street ponding likely.'
            }
        elif past_24h_rain >= 8.0:
            return {
                'level': 'YELLOW WATCH (MONITOR)',
                'icon': '🟨',
                'bg_color': '#D97706',
                'text_color': '#FFFFFF',
                'desc': 'Moderate precipitation loading within standard seasonal capacity.'
            }
        else:
            return {
                'level': 'GREEN STATUS (NORMAL / DRY)',
                'icon': '🟢',
                'bg_color': '#16A34A',
                'text_color': '#FFFFFF',
                'desc': 'Normal conditions. Zero or negligible precipitation detected.'
            }
    else:  # Relatively Lower Hazard
        if past_24h_rain >= 70.0:
            return {
                'level': 'ORANGE ALERT (CLOUDBURST ADVISORY)',
                'icon': '🟧',
                'bg_color': '#EA580C',
                'text_color': '#FFFFFF',
                'desc': 'Exceptional torrential rainfall. Elevated terrain promotes rapid runoff, but culvert blockage may cause temporary flash pooling.'
            }
        elif past_24h_rain >= 30.0:
            return {
                'level': 'YELLOW WATCH (MONITOR)',
                'icon': '🟨',
                'bg_color': '#D97706',
                'text_color': '#FFFFFF',
                'desc': 'Elevated plateau terrain naturally drains active rainfall effectively.'
            }
        else:
            return {
                'level': 'GREEN STATUS (NORMAL / OPTIMAL)',
                'icon': '🟢',
                'bg_color': '#16A34A',
                'text_color': '#FFFFFF',
                'desc': 'Optimal conditions. Upland/plateau morphology with negligible weather hazard.'
            }

# Header Section
st.markdown('<div class="main-header">🌊 Hazard-Based Red-Zone Identification for Vulnerable Habitations Using Clustering</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header"><b>Project ID: SIH26191</b> | <b>Coverage: Pan-India Multi-State System</b> | <b>Real-Time Live Weather & Flood Alerts</b> | B.Tech ML Project</div>', unsafe_allow_html=True)

# Academic Disclaimer
st.markdown("""
<div class="disclaimer-box">
    ⚠️ <b>Academic & Disaster Screening Mandate:</b> This system is an unsupervised machine learning exploratory decision-support system.
    Cluster groupings represent <i>relative statistical vulnerability</i> based on multi-criteria biophysical, topographic, and hydrometeorological features.
    Clustering alone <b>does NOT constitute an official government disaster warning, statutory regulatory red-zone demarcation, or administrative evacuation order</b>.
</div>
""", unsafe_allow_html=True)

# Sidebar: Multi-Level Geographic Selection
try:
    st.sidebar.image("https://img.icons8.com/fluency/96/flood.png", width=55)
except Exception:
    st.sidebar.markdown('<div style="font-size: 38px;">🌊</div>', unsafe_allow_html=True)
st.sidebar.title("National & State Navigation")

# 1. State Selector
state_options = ["All India (Pan-India Overview)"] + sorted(df['state'].dropna().unique().tolist())
selected_state = st.sidebar.selectbox("🇮🇳 1. Select State / Territory:", state_options, index=0)

# Filter by State
if selected_state != "All India (Pan-India Overview)":
    df_state = df[df['state'] == selected_state].copy()
else:
    df_state = df.copy()

# 2. District Selector
district_options = ["All Districts in State"] + sorted(df_state['district'].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("📍 2. Select District:", district_options)

# Filter by District
if selected_district != "All Districts in State":
    df_dist = df_state[df_state['district'] == selected_district].copy()
else:
    df_dist = df_state.copy()

# 3. Separate Danger Levels
st.sidebar.markdown("⚠️ **3. Separate Danger Levels**")
high_count = len(df_dist[df_dist['relative_hazard_level'] == 'High Relative Hazard / Vulnerability'])
med_count = len(df_dist[df_dist['relative_hazard_level'] == 'Moderate Relative Hazard / Vulnerability'])
low_count = len(df_dist[df_dist['relative_hazard_level'] == 'Relatively Lower Hazard / Vulnerability'])

c_high = st.sidebar.checkbox(f"🔴 High Danger ({high_count})", value=True)
c_med = st.sidebar.checkbox(f"🟡 Medium Danger ({med_count})", value=True)
c_low = st.sidebar.checkbox(f"🔵 Low Danger ({low_count})", value=True)

selected_tiers = []
if c_high:
    selected_tiers.append('High Relative Hazard / Vulnerability')
if c_med:
    selected_tiers.append('Moderate Relative Hazard / Vulnerability')
if c_low:
    selected_tiers.append('Relatively Lower Hazard / Vulnerability')

df_dist_tier = df_dist[df_dist['relative_hazard_level'].isin(selected_tiers)]

# 4. Select Particular Location / Area
st.sidebar.markdown("📍 **4. Select Particular Location / Area**")
place_options = ["All Locations in Scope"] + sorted(df_dist_tier['habitation_name'].dropna().unique().tolist())
selected_place = st.sidebar.selectbox("Select Particular Location / Area:", place_options, label_visibility="collapsed")
search_area = st.sidebar.text_input("Type to search area / village...", placeholder="🔍 Type to search area / village...", label_visibility="collapsed")

# Apply Filters
df_filtered = df_dist_tier.copy()
if selected_place != "All Locations in Scope":
    df_filtered = df_filtered[df_filtered['habitation_name'] == selected_place]
if search_area.strip():
    df_filtered = df_filtered[df_filtered['habitation_name'].str.contains(search_area.strip(), case=False, na=False)]

# Sidebar Live Refresh Button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Live Real-Time Weather Data"):
    st.cache_data.clear()
    st.sidebar.success("Cache refreshed! Fetching live data...")

st.sidebar.markdown("---")
st.sidebar.subheader("Active Scope Summary")
st.sidebar.write(f"**State:** {selected_state}")
st.sidebar.write(f"**District:** {selected_district}")
st.sidebar.write(f"**Location / Area:** {selected_place}")
st.sidebar.write(f"**Habitations Active:** {len(df_filtered)} / {len(df)}")
st.sidebar.write(f"**Districts in State:** {df_state['district'].nunique()}")
st.sidebar.write(f"**Elevation Model:** Copernicus DEM 90m")
st.sidebar.write(f"**Climatology:** IMD 24-Yr Grid Normals")
st.sidebar.write(f"**Real-Time Feed:** Open-Meteo Live API")

# Top KPI Metric Cards
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    high_count = (df_filtered['relative_hazard_level'] == 'High Relative Hazard / Vulnerability').sum()
    pct_high = (high_count / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    st.metric("🔴 High Hazard Places", f"{high_count}", delta=f"{pct_high:.1f}% of active")
with c2:
    mod_count = (df_filtered['relative_hazard_level'] == 'Moderate Relative Hazard / Vulnerability').sum()
    pct_mod = (mod_count / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    st.metric("🟡 Moderate Hazard", f"{mod_count}", delta=f"{pct_mod:.1f}% of active")
with c3:
    low_count = (df_filtered['relative_hazard_level'] == 'Relatively Lower Hazard / Vulnerability').sum()
    pct_low = (low_count / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    st.metric("🔵 Lower Hazard", f"{low_count}", delta=f"{pct_low:.1f}% of active")
with c4:
    mean_rain = df_filtered['annual_rainfall_mm'].mean() if len(df_filtered) > 0 else 0
    st.metric("🌧️ Mean Annual Rain", f"{mean_rain:.1f} mm", delta=f"Max {df_filtered['extreme_daily_rainfall_mm'].max():.0f} mm/day" if len(df_filtered) > 0 else "0")
with c5:
    mean_elev = df_filtered['elevation_m'].mean() if len(df_filtered) > 0 else 0
    st.metric("⛰️ Mean Elevation", f"{mean_elev:.1f} m AMSL", delta=f"Min {df_filtered['elevation_m'].min():.0f} m" if len(df_filtered) > 0 else "0")

# ⚡ LIVE REAL-TIME WEATHER & DYNAMIC FLOOD ALERT SECTION
st.markdown("### ⚡ Live Real-Time Weather & Dynamic Flood Alert Engine")

# Determine Target Location for Real-Time Query
if selected_place not in ["All Places in Selection", "All Locations in Scope"] and len(df_filtered) == 1:
    target_row = df_filtered.iloc[0]
    target_name = f"{target_row['habitation_name']} ({target_row['district']}, {target_row['state']})"
    target_lat = target_row['latitude']
    target_lon = target_row['longitude']
    target_hazard = target_row['relative_hazard_level']
    target_elev = target_row['elevation_m']
    target_river_dist = target_row['distance_to_river_km']
elif selected_district != "All Districts in State" and len(df_dist) > 0:
    target_row = df_dist.iloc[0]
    target_name = f"District Centroid: {selected_district} ({df_dist['state'].iloc[0]})"
    target_lat = df_dist['latitude'].mean()
    target_lon = df_dist['longitude'].mean()
    target_hazard = df_dist['relative_hazard_level'].mode()[0]
    target_elev = df_dist['elevation_m'].mean()
    target_river_dist = df_dist['distance_to_river_km'].mean()
else:
    # State or National capital/representative node
    target_name = f"Regional Representative Station: {selected_state}"
    target_lat = df_state['latitude'].mean()
    target_lon = df_state['longitude'].mean()
    target_hazard = df_state['relative_hazard_level'].mode()[0] if len(df_state) > 0 else "Moderate Relative Hazard / Vulnerability"
    target_elev = df_state['elevation_m'].mean() if len(df_state) > 0 else 25.0
    target_river_dist = df_state['distance_to_river_km'].mean() if len(df_state) > 0 else 5.0

# Fetch Live Weather
live_data = fetch_live_weather(target_lat, target_lon)

if live_data.get('status') == 'success':
    wmo_desc, wmo_icon, wmo_color = get_wmo_description(live_data['weather_code'])
    dynamic_alert = compute_dynamic_flood_alert(target_hazard, live_data['past_24h_rain_mm'], live_data['rain_rate_mmh'])
    
    # Render Live Alert Banner
    st.markdown(f"""
    <div class="live-alert-card" style="background: linear-gradient(135deg, {dynamic_alert['bg_color']} 0%, #111827 100%);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="font-size: 22px; font-weight: 800;">{dynamic_alert['icon']} {dynamic_alert['level']}</span>
                <span style="margin-left: 12px; font-size: 14px; opacity: 0.9;">Station: <b>{target_name}</b> (Lat: {target_lat:.3f}°, Lon: {target_lon:.3f}°)</span>
            </div>
            <div style="font-size: 13px; opacity: 0.9;">
                🕒 <b>Live Observation:</b> {live_data['time'].replace('T', ' ')} IST | <span style="background: rgba(255,255,255,0.2); padding: 3px 8px; border-radius: 4px;">📡 Live API Connected</span>
            </div>
        </div>
        <p style="margin-top: 8px; margin-bottom: 12px; font-size: 14.5px; line-height: 1.4;">{dynamic_alert['desc']}</p>
        <div>
            <span class="metric-pill" style="background: rgba(255,255,255,0.25);">🌡️ Temp: {live_data['temp_c']}°C (Feels {live_data['feels_like_c']}°C)</span>
            <span class="metric-pill" style="background: rgba(255,255,255,0.25);">💧 Humidity: {live_data['humidity_pct']}%</span>
            <span class="metric-pill" style="background: rgba(255,255,255,0.25);">🌧️ Live Rain: {live_data['rain_rate_mmh']} mm/h</span>
            <span class="metric-pill" style="background: rgba(255,255,255,0.25);">🌊 Past 24h Rain: {live_data['past_24h_rain_mm']} mm</span>
            <span class="metric-pill" style="background: rgba(255,255,255,0.25);">{wmo_icon} Condition: {wmo_desc}</span>
            <span class="metric-pill" style="background: rgba(255,255,255,0.25);">💨 Wind: {live_data['wind_kmh']} km/h</span>
            <span class="metric-pill" style="background: rgba(255,255,255,0.25);">⛰️ Elevation: {target_elev:.1f} m AMSL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("📡 Real-time weather observation feed connecting to live sensors... (Using fallback normal state)")

# State Center & Zoom Lookup
state_geo = {
    "All India (Pan-India Overview)": {"center": [22.0, 79.5], "zoom": 5},
    "Andhra Pradesh": {"center": [16.42, 80.60], "zoom": 8},
    "Assam": {"center": [26.20, 92.80], "zoom": 7},
    "Bihar": {"center": [25.75, 85.90], "zoom": 7},
    "Kerala": {"center": [10.20, 76.50], "zoom": 8},
    "Odisha": {"center": [20.50, 85.50], "zoom": 7},
    "West Bengal": {"center": [23.50, 87.80], "zoom": 7},
    "Maharashtra": {"center": [18.50, 74.50], "zoom": 7},
    "Gujarat": {"center": [22.20, 71.80], "zoom": 7},
    "Uttar Pradesh": {"center": [26.50, 81.50], "zoom": 7},
    "Tamil Nadu": {"center": [11.00, 78.80], "zoom": 7},
    "Karnataka": {"center": [14.50, 75.80], "zoom": 7},
    "Delhi": {"center": [28.63, 77.22], "zoom": 11},
    "Punjab": {"center": [30.60, 75.50], "zoom": 8},
    "Uttarakhand": {"center": [30.00, 78.50], "zoom": 8},
    "Himachal Pradesh": {"center": [32.00, 77.10], "zoom": 8}
}

# Tabs
tab_map, tab_districts, tab_profiles, tab_state_comp, tab_ml_eval, tab_data = st.tabs([
    "🗺️ Interactive Geospatial Map",
    "🏛️ All Districts in State Matrix",
    "📊 Multi-Criteria Risk Signatures",
    "🇮🇳 State-Wise National Comparison",
    "🤖 Machine Learning Benchmarking",
    "📋 Data Explorer & All Places Registry"
])

color_dict = {
    'High Relative Hazard / Vulnerability': '#d73027',     # Red
    'Moderate Relative Hazard / Vulnerability': '#fdae61', # Orange/Yellow
    'Relatively Lower Hazard / Vulnerability': '#4575b4'   # Blue
}

# TAB 1: INTERACTIVE GEOSPATIAL MAP
with tab_map:
    st.subheader(f"Geospatial Hazard Distribution — {selected_state} ({selected_district})")
    st.write(f"Displaying **{len(df_filtered)} habitation(s)** across **{df_filtered['district'].nunique()} district(s)**. Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.")
    
    geo_info = state_geo.get(selected_state, {"center": [22.0, 79.5], "zoom": 5})
    if selected_place not in ["All Places in Selection", "All Locations in Scope"] and len(df_filtered) == 1:
        map_center = [df_filtered['latitude'].iloc[0], df_filtered['longitude'].iloc[0]]
        map_zoom = 12
    elif selected_district != "All Districts in State" and len(df_filtered) > 0:
        map_center = [df_filtered['latitude'].mean(), df_filtered['longitude'].mean()]
        map_zoom = 10
    elif len(df_filtered) > 0 and selected_state != "All India (Pan-India Overview)":
        map_center = [df_filtered['latitude'].mean(), df_filtered['longitude'].mean()]
        map_zoom = geo_info['zoom']
    else:
        map_center = geo_info['center']
        map_zoom = geo_info['zoom']
        
    m = folium.Map(location=map_center, zoom_start=map_zoom, tiles="OpenStreetMap")
    
    # Render Krishna River & Budameru if viewing AP or All India
    if selected_state in ["All India (Pan-India Overview)", "Andhra Pradesh"]:
        krishna_coords = [
            [16.580, 80.360], [16.592, 80.450], [16.590, 80.522], [16.550, 80.565],
            [16.507, 80.605], [16.480, 80.640], [16.440, 80.720], [16.360, 80.780],
            [16.320, 80.825], [16.185, 80.795], [16.122, 80.932], [16.022, 80.918], [15.945, 80.915]
        ]
        folium.PolyLine(krishna_coords, color="#0055ff", weight=4, opacity=0.85, tooltip="Krishna River (Prakasam Barrage System)").add_to(m)
        
        budameru_coords = [
            [16.630, 80.540], [16.562, 80.615], [16.538, 80.638], [16.522, 80.665], [16.520, 80.750]
        ]
        folium.PolyLine(budameru_coords, color="#00aaff", weight=3, dash_array="6, 6", opacity=0.85, tooltip="Budameru Rivulet Drainage Floodway").add_to(m)

    # Plot Habitats
    for _, row in df_filtered.iterrows():
        tier = row['relative_hazard_level']
        c_hex = color_dict.get(tier, '#888888')
        is_selected = (selected_place == row['habitation_name'])
        
        popup_html = f"""
        <div style="font-family: Arial; width: 260px; font-size: 12px;">
            <b style="color: {c_hex}; font-size: 14px;">{row['habitation_name']}</b><br>
            <b>State:</b> {row['state']}<br>
            <b>District:</b> {row['district']} | <b>Mandal:</b> {row.get('mandal', 'N/A')}<br>
            <b>Basin:</b> {row.get('river_basin', 'Regional')}<br>
            <b>ML Hazard Tier:</b> <span style="color: {c_hex}; font-weight: bold;">{tier}</span><br>
            <hr style="margin: 4px 0;">
            <b>Elevation:</b> {row['elevation_m']:.1f} m AMSL<br>
            <b>Distance to River:</b> {row['distance_to_river_km']:.2f} km<br>
            <b>Historical Floods:</b> {row['historical_flood_inundation_frequency']}/5<br>
            <b>Drainage Congestion:</b> {row['drainage_congestion_index']}/5<br>
            <b>Annual Rain:</b> {row['annual_rainfall_mm']:.1f} mm<br>
            <b>Max 24h Rain:</b> {row['extreme_daily_rainfall_mm']:.1f} mm<br>
            <b>Pop Density:</b> {row['population_density_per_sqkm']:,.0f} /km²
        </div>
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=9.0 if is_selected else (6.5 if 'High' in tier else 5.0),
            color='#FFD700' if is_selected else 'black',
            weight=3.0 if is_selected else 0.7,
            fill=True,
            fill_color=c_hex,
            fill_opacity=0.9 if is_selected else 0.8,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"📍 {row['habitation_name']} ({row['district']} - {tier.split(' ')[0]})"
        ).add_to(m)
        
    st_folium(m, width=1200, height=560)

# TAB 2: ALL DISTRICTS IN STATE MATRIX & REAL-TIME MONITORING
with tab_districts:
    st.subheader(f"All Districts Matrix & Real-Time Monitoring — {selected_state}")
    st.write(f"Detailed multi-criteria breakdown across **all {df_state['district'].nunique()} districts** in **{selected_state}**:")
    
    # Aggregation across all districts in the state
    dist_matrix = df_state.groupby('district').agg(
        habitations_monitored=('habitation_id', 'count'),
        high_hazard_count=('relative_hazard_level', lambda s: (s == 'High Relative Hazard / Vulnerability').sum()),
        mod_hazard_count=('relative_hazard_level', lambda s: (s == 'Moderate Relative Hazard / Vulnerability').sum()),
        low_hazard_count=('relative_hazard_level', lambda s: (s == 'Relatively Lower Hazard / Vulnerability').sum()),
        mean_elevation_m=('elevation_m', 'mean'),
        min_elevation_m=('elevation_m', 'min'),
        mean_river_distance_km=('distance_to_river_km', 'mean'),
        mean_annual_rainfall_mm=('annual_rainfall_mm', 'mean'),
        max_daily_rainfall_mm=('extreme_daily_rainfall_mm', 'max'),
        mean_flood_frequency=('historical_flood_inundation_frequency', 'mean'),
        centroid_lat=('latitude', 'mean'),
        centroid_lon=('longitude', 'mean')
    ).reset_index()
    
    dist_matrix['high_hazard_pct'] = (dist_matrix['high_hazard_count'] / dist_matrix['habitations_monitored'] * 100).round(1)
    dist_matrix = dist_matrix.sort_values(by=['high_hazard_pct', 'mean_elevation_m'], ascending=[False, True])
    
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        fig_dist_bar = px.bar(
            dist_matrix, x='district', y='high_hazard_pct',
            color='high_hazard_pct',
            color_continuous_scale='Reds',
            title=f"Districts Ranked by High Hazard Habitations (%) in {selected_state}",
            labels={'district': 'District', 'high_hazard_pct': 'High Hazard (%)'},
            height=430
        )
        fig_dist_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_dist_bar, use_container_width=True)
        
    with col_d2:
        fig_dist_elev = px.scatter(
            dist_matrix, x='mean_elevation_m', y='mean_annual_rainfall_mm',
            size='habitations_monitored',
            color='high_hazard_pct',
            color_continuous_scale='Portland',
            hover_name='district',
            title=f"District Morphometry: Mean Elevation vs Annual Rain ({selected_state})",
            labels={'mean_elevation_m': 'Mean Elevation (m AMSL)', 'mean_annual_rainfall_mm': 'Mean Annual Rainfall (mm)'},
            height=430
        )
        st.plotly_chart(fig_dist_elev, use_container_width=True)
        
    st.markdown("#### District Multi-Hazard Profile Summary Table")
    st.dataframe(
        dist_matrix[[
            'district', 'habitations_monitored', 'high_hazard_count', 'mod_hazard_count',
            'low_hazard_count', 'high_hazard_pct', 'mean_elevation_m', 'mean_river_distance_km',
            'mean_annual_rainfall_mm', 'max_daily_rainfall_mm', 'mean_flood_frequency'
        ]].style.format({
            'high_hazard_pct': '{:.1f}%',
            'mean_elevation_m': '{:.1f} m',
            'mean_river_distance_km': '{:.2f} km',
            'mean_annual_rainfall_mm': '{:.1f} mm',
            'max_daily_rainfall_mm': '{:.0f} mm',
            'mean_flood_frequency': '{:.2f}/5'
        }).background_gradient(subset=['high_hazard_pct'], cmap='Reds'),
        use_container_width=True
    )
    
    # Real-Time Multi-District Live Weather Query Button
    st.markdown("---")
    st.markdown("#### ⚡ Live Multi-District Real-Time Meteorological Monitor")
    st.write(f"Fetch live real-time weather readings simultaneously across all {len(dist_matrix)} districts in {selected_state}:")
    
    if st.button(f"📡 Query Live Weather for All {len(dist_matrix)} Districts in {selected_state}"):
        with st.spinner("Connecting to Open-Meteo real-time satellite & ground observation grid..."):
            live_rows = []
            for _, r in dist_matrix.iterrows():
                w = fetch_live_weather(r['centroid_lat'], r['centroid_lon'])
                if w.get('status') == 'success':
                    alert = compute_dynamic_flood_alert(
                        'High' if r['high_hazard_count'] > 0 else 'Moderate',
                        w['past_24h_rain_mm'],
                        w['rain_rate_mmh']
                    )
                    wmo_text, wmo_ic, _ = get_wmo_description(w['weather_code'])
                    live_rows.append({
                        'District': r['district'],
                        'Live Temp (°C)': w['temp_c'],
                        'Humidity (%)': w['humidity_pct'],
                        'Live Rain Rate (mm/h)': w['rain_rate_mmh'],
                        'Past 24h Rain (mm)': w['past_24h_rain_mm'],
                        'Current Sky Condition': f"{wmo_ic} {wmo_text}",
                        'Wind (km/h)': w['wind_kmh'],
                        'Dynamic Alert Status': f"{alert['icon']} {alert['level']}"
                    })
            if live_rows:
                df_live_dist = pd.DataFrame(live_rows)
                st.success(f"Successfully retrieved live weather for {len(live_rows)} districts!")
                st.dataframe(df_live_dist, use_container_width=True)

# TAB 3: MULTI-CRITERIA RISK SIGNATURES
with tab_profiles:
    st.subheader(f"Multi-Criteria Risk Signatures ({selected_state})")
    
    feature_cols = [
        'elevation_m', 'slope_deg', 'distance_to_river_km',
        'annual_rainfall_mm', 'extreme_daily_rainfall_mm',
        'population_density_per_sqkm', 'drainage_congestion_index',
        'historical_flood_inundation_frequency'
    ]
    
    col_left, col_right = st.columns(2)
    with col_left:
        # Radar Chart
        tier_order = [
            'High Relative Hazard / Vulnerability',
            'Moderate Relative Hazard / Vulnerability',
            'Relatively Lower Hazard / Vulnerability'
        ]
        
        df_for_radar = df_filtered if df_filtered['relative_hazard_level'].nunique() > 1 else df
        tier_means = df_for_radar.groupby('relative_hazard_level')[feature_cols].mean()
        present_tiers = [t for t in tier_order if t in tier_means.index]
        tier_means = tier_means.loc[present_tiers]
        
        min_v = df[feature_cols].min()
        max_v = df[feature_cols].max()
        norm_df = (tier_means - min_v) / (max_v - min_v + 1e-6)
        
        # Invert features where lower value means higher hazard
        norm_df['elevation_m'] = 1.0 - norm_df['elevation_m']
        norm_df['slope_deg'] = 1.0 - norm_df['slope_deg']
        norm_df['distance_to_river_km'] = 1.0 - norm_df['distance_to_river_km']
        
        categories = ['Elevation (Inv)', 'Slope (Inv)', 'River Dist (Inv)', 'Annual Rain', 'Extreme Rain', 'Pop Density', 'Congestion', 'Flood Freq']
        
        fig_radar = go.Figure()
        radar_colors = {
            'High Relative Hazard / Vulnerability': 'rgba(215, 48, 39, 0.6)',
            'Moderate Relative Hazard / Vulnerability': 'rgba(253, 174, 97, 0.6)',
            'Relatively Lower Hazard / Vulnerability': 'rgba(69, 117, 180, 0.6)'
        }
        line_colors = {
            'High Relative Hazard / Vulnerability': '#d73027',
            'Moderate Relative Hazard / Vulnerability': '#fdae61',
            'Relatively Lower Hazard / Vulnerability': '#4575b4'
        }
        
        for tier in present_tiers:
            vals = norm_df.loc[tier].values.tolist()
            vals.append(vals[0])
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor=radar_colors[tier],
                line=dict(color=line_colors[tier], width=2),
                name=tier.split(' ')[0] + " Hazard"
            ))
            
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title="Radar Profile Signature (Normalized Risk Factors)",
            height=460
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col_right:
        # 2D PCA Scatter
        fig_pca = px.scatter(
            df_filtered if len(df_filtered) > 1 else df_state,
            x='pca_1', y='pca_2',
            color='relative_hazard_level',
            hover_name='habitation_name',
            hover_data=['state', 'district', 'elevation_m', 'distance_to_river_km'],
            color_discrete_map=color_dict,
            title=f"2D Principal Component Projection ({selected_state})",
            labels={'pca_1': 'PC1 (Flood Exposure & Basin Entrapment)', 'pca_2': 'PC2 (Rainfall Extremes vs Inland)'},
            height=460
        )
        fig_pca.update_traces(marker=dict(size=9, line=dict(width=1, color='DarkSlateGrey')))
        st.plotly_chart(fig_pca, use_container_width=True)

    # Feature comparison boxplots
    st.subheader("Feature Distribution by Hazard Tier")
    comp_feat = st.selectbox("Select Feature to Inspect:", [
        ('elevation_m', 'Surface Elevation (m AMSL)'),
        ('distance_to_river_km', 'Distance to River/Channel (km)'),
        ('historical_flood_inundation_frequency', 'Historical Inundation Frequency (Events)'),
        ('annual_rainfall_mm', 'Annual Rainfall (mm)'),
        ('extreme_daily_rainfall_mm', 'Max Single-Day Rain (mm)'),
        ('population_density_per_sqkm', 'Population Density (/km²)'),
        ('drainage_congestion_index', 'Drainage Congestion Score (1-5)')
    ], format_func=lambda x: x[1])
    
    fig_box = px.box(
        df_filtered if len(df_filtered) > 3 else df_state,
        x='relative_hazard_level', y=comp_feat[0],
        color='relative_hazard_level',
        color_discrete_map=color_dict,
        points="all",
        title=f"Distribution of {comp_feat[1]} across Tiers in {selected_state}",
        labels={'relative_hazard_level': 'Relative Hazard Tier', comp_feat[0]: comp_feat[1]}
    )
    st.plotly_chart(fig_box, use_container_width=True)

# TAB 4: STATE-WISE NATIONAL COMPARISON
with tab_state_comp:
    st.subheader("State-Wise Flood Hazard & Vulnerability Comparison across India")
    
    # State-level Aggregations
    state_summary = df.groupby('state').agg(
        total_settlements=('habitation_id', 'count'),
        districts_covered=('district', 'nunique'),
        high_hazard_count=('relative_hazard_level', lambda s: (s == 'High Relative Hazard / Vulnerability').sum()),
        mean_rainfall_mm=('annual_rainfall_mm', 'mean'),
        mean_elevation_m=('elevation_m', 'mean'),
        mean_flood_frequency=('historical_flood_inundation_frequency', 'mean'),
        mean_congestion=('drainage_congestion_index', 'mean')
    ).reset_index()
    
    state_summary['high_hazard_pct'] = (state_summary['high_hazard_count'] / state_summary['total_settlements'] * 100).round(1)
    state_summary = state_summary.sort_values(by='high_hazard_pct', ascending=False)
    
    c_bar1, c_bar2 = st.columns(2)
    with c_bar1:
        fig_st_bar = px.bar(
            state_summary, x='state', y='high_hazard_pct',
            color='high_hazard_pct',
            color_continuous_scale='Reds',
            title="Percentage of Monitored Settlements in High Hazard Tier (%)",
            labels={'state': 'State', 'high_hazard_pct': 'High Hazard (%)'},
            height=450
        )
        st.plotly_chart(fig_st_bar, use_container_width=True)
        
    with c_bar2:
        fig_st_rain = px.scatter(
            state_summary, x='mean_rainfall_mm', y='mean_elevation_m',
            size='total_settlements',
            color='high_hazard_pct',
            color_continuous_scale='Viridis',
            hover_name='state',
            title="State Climatology vs Topography: Mean Rainfall vs Elevation",
            labels={'mean_rainfall_mm': 'Mean Annual Rainfall (mm)', 'mean_elevation_m': 'Mean Elevation (m AMSL)'},
            height=450
        )
        st.plotly_chart(fig_st_rain, use_container_width=True)
        
    st.dataframe(state_summary.style.format({
        'mean_rainfall_mm': '{:.1f}',
        'mean_elevation_m': '{:.1f}',
        'mean_flood_frequency': '{:.2f}',
        'mean_congestion': '{:.2f}',
        'high_hazard_pct': '{:.1f}%'
    }).background_gradient(subset=['high_hazard_pct'], cmap='Reds'), use_container_width=True)

# TAB 5: MACHINE LEARNING BENCHMARKING
with tab_ml_eval:
    st.subheader("Machine Learning Algorithm Benchmarking & Metric Validation")
    
    col_km, col_hier = st.columns(2)
    with col_km:
        st.markdown("#### K-Means Clustering Benchmarking (Random vs K-Means++)")
        if os.path.exists("outputs/tables/kmeans_comparison_table.csv"):
            df_km = pd.read_csv("outputs/tables/kmeans_comparison_table.csv")
            st.dataframe(df_km.style.highlight_max(subset=['Silhouette Score'], color='#d1fae5')
                                  .highlight_min(subset=['Davies-Bouldin Index'], color='#dbeafe'),
                         use_container_width=True)
                         
        st.markdown("#### K-Medoids (PAM) with Manhattan (L1) vs Euclidean")
        if os.path.exists("outputs/tables/kmedoids_comparison_table.csv"):
            df_kmed = pd.read_csv("outputs/tables/kmedoids_comparison_table.csv")
            st.dataframe(df_kmed[['Algorithm', 'Distance Metric', 'K (Clusters)', 'Silhouette Score', 'Davies-Bouldin Index', 'Exemplar Medoids']],
                         use_container_width=True)
                         
    with col_hier:
        st.markdown("#### Hierarchical Clustering (Linkage Criteria, K=3)")
        if os.path.exists("outputs/tables/hierarchical_comparison_table.csv"):
            df_hier = pd.read_csv("outputs/tables/hierarchical_comparison_table.csv")
            st.dataframe(df_hier[['Linkage Criterion', 'Clusters (K)', 'Silhouette Score', 'Davies-Bouldin Index', 'Cluster Distribution']],
                         use_container_width=True)
                         
        st.markdown("#### Master Comparison across Paradigms")
        if os.path.exists("outputs/tables/master_clustering_comparison.csv"):
            df_master = pd.read_csv("outputs/tables/master_clustering_comparison.csv")
            st.dataframe(df_master[['Algorithm', 'Clusters', 'Noise Points', 'Silhouette Score', 'Davies-Bouldin Index', 'Key Advantages']],
                         use_container_width=True)

# TAB 6: DATA EXPLORER & ALL PLACES REGISTRY
with tab_data:
    st.subheader(f"Pan-India All Places & Habitations Registry ({selected_state})")
    st.write(f"Showing **{len(df_filtered)} habitations** matching State: **{selected_state}**, District: **{selected_district}**, Place: **{selected_place}**:")
    
    display_cols = [
        'habitation_name', 'state', 'district', 'mandal', 'relative_hazard_level',
        'elevation_m', 'distance_to_river_km', 'historical_flood_inundation_frequency',
        'drainage_congestion_index', 'annual_rainfall_mm', 'extreme_daily_rainfall_mm',
        'population', 'population_density_per_sqkm', 'river_basin'
    ]
    st.dataframe(df_filtered[display_cols].sort_values(by=['state', 'district', 'relative_hazard_level']), use_container_width=True)
    
    st.download_button(
        label=f"📥 Download Filtered Data for {selected_state} (CSV)",
        data=df_filtered.to_csv(index=False),
        file_name=f"flood_clusters_{selected_state.replace(' ', '_').lower()}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("<center><small>SIH26191 | Pan-India Multi-State Hazard-Based Red-Zone Identification System | Antigravity AI Data Science Lab</small></center>", unsafe_allow_html=True)
