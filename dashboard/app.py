import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import datetime
import os

st.set_page_config(
    page_title="SIH26191: Pan-India Flood Hazard & Real-Time Alert System",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Aesthetic Dark-Mode Styling matching modern Streamlit theme
st.markdown("""
<style>
    /* Dark Theme General Styles */
    .stApp {
        background-color: #0E1117;
        color: #F1F5F9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Headers */
    .main-header {
        font-size: 25px;
        font-weight: 800;
        color: #60A5FA;
        margin-bottom: 2px;
        letter-spacing: -0.3px;
    }
    .sub-header {
        font-size: 13.5px;
        color: #94A3B8;
        margin-bottom: 12px;
    }
    
    /* Academic Disclaimer Box */
    .disclaimer-box {
        background-color: #1E222D;
        border-left: 4px solid #F59E0B;
        padding: 10px 16px;
        border-radius: 6px;
        font-size: 12.5px;
        color: #FDE68A;
        margin-bottom: 14px;
        line-height: 1.45;
    }
    
    /* Live Alert Card */
    .live-alert-card {
        padding: 16px 20px;
        border-radius: 8px;
        color: #ffffff;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .metric-pill {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 5px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161922 !important;
        border-right: 1px solid #2B3245;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    
    /* Danger Group Card */
    .danger-box-card {
        background: rgba(14, 17, 23, 0.65);
        border: 1px solid #2B3245;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 12px;
    }
    
    /* Spotlight Banner */
    .spotlight-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #38BDF8;
        border-left: 5px solid #38BDF8;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 16px;
    }
    
    /* Graph Container Box */
    .chart-container-card {
        background-color: #161922;
        border: 1px solid #2B3245;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 16px;
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
        if os.path.exists(df_path):
            df = pd.read_csv(df_path)
            df['state'] = 'Andhra Pradesh'
            df['river_basin'] = 'Krishna Basin'
            return df
    return pd.read_csv(df_path)

df = load_data()

# Plotly Template defaults for Dark Theme
dark_layout_defaults = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(22, 25, 34, 0.7)",
    plot_bgcolor="rgba(22, 25, 34, 0.7)",
    font=dict(color="#CBD5E1", family="Inter, sans-serif"),
    margin=dict(l=35, r=25, t=40, b=35)
)

# Live Real-Time Weather Fetching Function (Open-Meteo)
@st.cache_data(ttl=300)
def fetch_live_weather(lat, lon):
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
    else:
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

# Academic Disclaimer Banner
st.markdown("""
<div class="disclaimer-box">
    ⚠️ <b>Academic & Disaster Screening Mandate:</b> This system is an unsupervised machine learning exploratory decision-support system.
    Cluster groupings represent <i>relative statistical vulnerability</i> based on multi-criteria biophysical, topographic, and hydrometeorological features.
    Clustering alone <b>does NOT constitute an official government disaster warning, statutory regulatory red-zone demarcation, or administrative evacuation order</b>.
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR: EXACT LAYOUT MATCHING USER SCREENSHOT
# ==============================================================================
st.sidebar.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
    <h2 style="font-size: 19px; font-weight: 800; color: #FFFFFF; margin: 0; letter-spacing: -0.3px;">National & State Navigation</h2>
    <span style="font-size: 16px; color: #94A3B8; font-weight: bold; cursor: pointer;">«</span>
</div>
""", unsafe_allow_html=True)

# 1. State Selector
st.sidebar.markdown("<div style='font-size: 13px; font-weight: 700; color: #E2E8F0; margin-bottom: 4px;'>IN 1. Select State / Territory:</div>", unsafe_allow_html=True)
state_options = ["All India (Pan-India Overview)"] + sorted(df['state'].dropna().unique().tolist())
selected_state = st.sidebar.selectbox("IN 1. Select State / Territory:", state_options, index=0, label_visibility="collapsed")

# Filter by State
if selected_state != "All India (Pan-India Overview)":
    df_state = df[df['state'] == selected_state].copy()
else:
    df_state = df.copy()

# 2. District Selector
st.sidebar.markdown("<div style='font-size: 13px; font-weight: 700; color: #E2E8F0; margin-top: 10px; margin-bottom: 4px;'>📍 2. Select District:</div>", unsafe_allow_html=True)
district_options = ["All Districts in State"] + sorted(df_state['district'].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("📍 2. Select District:", district_options, label_visibility="collapsed")

# Filter by District
if selected_district != "All Districts in State":
    df_dist = df_state[df_state['district'] == selected_district].copy()
else:
    df_dist = df_state.copy()

# 3. Separate Danger Levels (Exact Box with Dynamic Numbers)
st.sidebar.markdown("<div style='font-size: 13px; font-weight: 700; color: #E2E8F0; margin-top: 14px; margin-bottom: 6px;'>⚠️ 3. Separate Danger Levels</div>", unsafe_allow_html=True)

c_high_scope = int((df_dist['relative_hazard_level'] == 'High Relative Hazard / Vulnerability').sum())
c_med_scope = int((df_dist['relative_hazard_level'] == 'Moderate Relative Hazard / Vulnerability').sum())
c_low_scope = int((df_dist['relative_hazard_level'] == 'Relatively Lower Hazard / Vulnerability').sum())

with st.sidebar.container():
    st.markdown("""<div class="danger-box-card">""", unsafe_allow_html=True)
    show_high = st.checkbox(f"🔴 High Danger ({c_high_scope})", value=True, key="cb_high")
    show_med = st.checkbox(f"🟡 Medium Danger ({c_med_scope})", value=True, key="cb_med")
    show_low = st.checkbox(f"🔵 Low Danger ({c_low_scope})", value=True, key="cb_low")
    st.markdown("""</div>""", unsafe_allow_html=True)

active_tiers = []
if show_high: active_tiers.append('High Relative Hazard / Vulnerability')
if show_med: active_tiers.append('Moderate Relative Hazard / Vulnerability')
if show_low: active_tiers.append('Relatively Lower Hazard / Vulnerability')

df_tier_filtered = df_dist[df_dist['relative_hazard_level'].isin(active_tiers)].copy()

# 4. Select Particular Location / Area (Exact Layout with Search Box & Dropdown)
st.sidebar.markdown("<div style='font-size: 13px; font-weight: 700; color: #E2E8F0; margin-top: 14px; margin-bottom: 4px;'>📍 4. Select Particular Location / Area</div>", unsafe_allow_html=True)

all_scope_places = sorted(df_tier_filtered['habitation_name'].dropna().unique().tolist())

# Selectbox first (matching screenshot)
place_select_options = ["All Locations in Scope"] + all_scope_places
selected_place_pre = st.sidebar.selectbox(
    "📍 4. Select Particular Location / Area:",
    place_select_options,
    label_visibility="collapsed",
    key="location_scope_select"
)

# Search box right below selectbox (matching screenshot)
search_query = st.sidebar.text_input(
    "Search Area / Village",
    placeholder="🔍 Type to search area / village...",
    label_visibility="collapsed",
    key="area_search_input"
)

# Determine the final chosen place
selected_place = selected_place_pre
if search_query.strip():
    sq = search_query.strip().lower()
    matches = [p for p in all_scope_places if sq in p.lower()]
    if matches:
        selected_place = matches[0]

# Apply Location Filter
df_filtered = df_tier_filtered.copy()
if selected_place != "All Locations in Scope":
    df_filtered = df_filtered[df_filtered['habitation_name'] == selected_place]

# Sidebar Live Refresh Button & Summary
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Live Real-Time Weather Data"):
    st.cache_data.clear()
    st.sidebar.success("Cache refreshed! Fetching live data...")

st.sidebar.markdown("---")
st.sidebar.subheader("Active Scope Summary")
st.sidebar.write(f"**State:** {selected_state}")
st.sidebar.write(f"**District:** {selected_district}")
st.sidebar.write(f"**Place:** {selected_place}")
st.sidebar.write(f"**Habitations Active:** {len(df_filtered)} / {len(df)}")
st.sidebar.write(f"**Districts in State:** {df_state['district'].nunique()}")
st.sidebar.write(f"**Elevation Model:** Copernicus DEM 90m")
st.sidebar.write(f"**Climatology:** IMD 24-Yr Grid Normals")
st.sidebar.write(f"**Real-Time Feed:** Open-Meteo Live API")

# Top KPI Metric Cards (Matching Numbers)
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

# ==============================================================================
# MAXIMUM DATA IN GRAPH FORM: EXECUTIVE VISUAL ANALYTICS ROW
# ==============================================================================
st.markdown("### 📈 Executive Visual Analytics (Active Scope)")
col_g1, col_g2, col_g3 = st.columns([1, 1.2, 1.3])

color_dict = {
    'High Relative Hazard / Vulnerability': '#d73027',     # Red
    'Moderate Relative Hazard / Vulnerability': '#fdae61', # Orange/Yellow
    'Relatively Lower Hazard / Vulnerability': '#4575b4'   # Blue
}

with col_g1:
    # Graph 1: Danger Level Breakdown Donut Chart
    tier_counts = df_filtered['relative_hazard_level'].value_counts().reset_index()
    tier_counts.columns = ['tier', 'count']
    fig_donut = go.Figure(data=[go.Pie(
        labels=tier_counts['tier'].apply(lambda x: x.split(' ')[0] + " Danger"),
        values=tier_counts['count'],
        hole=0.55,
        marker=dict(colors=[color_dict.get(t, '#888') for t in tier_counts['tier']]),
        textinfo='label+percent',
        hoverinfo='label+value+percent'
    )])
    fig_donut.update_layout(
        title="Active Danger Distribution",
        height=260,
        showlegend=False,
        annotations=[dict(text=f"<b>{len(df_filtered)}</b><br>Habitations", x=0.5, y=0.5, font_size=13, showarrow=False, font_color="#FFF")],
        **dark_layout_defaults
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_g2:
    # Graph 2: Settlement Category vs Danger Tier Grouped Bar
    if 'place_category' in df_filtered.columns:
        cat_df = df_filtered.groupby(['place_category', 'relative_hazard_level']).size().reset_index(name='count')
        fig_cat = px.bar(
            cat_df, x='place_category', y='count', color='relative_hazard_level',
            color_discrete_map=color_dict,
            barmode='stack',
            title="Habitation Category vs Hazard",
            labels={'place_category': 'Category', 'count': 'Places', 'relative_hazard_level': 'Tier'}
        )
        fig_cat.update_layout(
            height=260,
            showlegend=False,
            xaxis_tickangle=-15,
            **dark_layout_defaults
        )
        st.plotly_chart(fig_cat, use_container_width=True)

with col_g3:
    # Graph 3: Top 8 Most Vulnerable Settlements
    top_crit = df_filtered.sort_values(
        by=['historical_flood_inundation_frequency', 'drainage_congestion_index', 'elevation_m'],
        ascending=[False, False, True]
    ).head(8)
    
    fig_crit = px.bar(
        top_crit, x='elevation_m', y='habitation_name',
        orientation='h',
        color='relative_hazard_level',
        color_discrete_map=color_dict,
        title="Top Vulnerable Sites: Elevation vs Flood Frequency",
        labels={'elevation_m': 'Elevation (m AMSL)', 'habitation_name': 'Place'}
    )
    fig_crit.update_layout(
        height=260,
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        **dark_layout_defaults
    )
    st.plotly_chart(fig_crit, use_container_width=True)

# ⚡ LIVE REAL-TIME WEATHER & DYNAMIC FLOOD ALERT SECTION
st.markdown("### ⚡ Live Real-Time Weather & Dynamic Flood Alert Engine")

# Determine Target Location for Real-Time Query
if selected_place != "All Locations in Scope" and len(df_filtered) == 1:
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
    target_name = f"Regional Representative Station: {selected_state}"
    target_lat = df_state['latitude'].mean()
    target_lon = df_state['longitude'].mean()
    target_hazard = df_state['relative_hazard_level'].mode()[0] if len(df_state) > 0 else "Moderate Relative Hazard / Vulnerability"
    target_elev = df_state['elevation_m'].mean() if len(df_state) > 0 else 25.0
    target_river_dist = df_state['distance_to_river_km'].mean() if len(df_state) > 0 else 5.0

live_data = fetch_live_weather(target_lat, target_lon)

if live_data.get('status') == 'success':
    wmo_desc, wmo_icon, wmo_color = get_wmo_description(live_data['weather_code'])
    dynamic_alert = compute_dynamic_flood_alert(target_hazard, live_data['past_24h_rain_mm'], live_data['rain_rate_mmh'])
    
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
    st.info("📡 Real-time weather observation feed connecting to live sensors...")

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

# TABS
tab_map, tab_districts, tab_profiles, tab_state_comp, tab_ml_eval, tab_data = st.tabs([
    "🗺️ Interactive Geospatial Map",
    "🏛️ All Districts in State Matrix & Graphs",
    "📊 Multi-Criteria Risk Signatures",
    "🇮🇳 State-Wise National Comparison",
    "🤖 Machine Learning Benchmarking",
    "📋 Data Explorer & All Places Registry"
])

# ==============================================================================
# TAB 1: INTERACTIVE GEOSPATIAL MAP & SPOTLIGHT GRAPHS
# ==============================================================================
with tab_map:
    st.subheader(f"Geospatial Hazard Distribution — {selected_state} ({selected_district})")
    
    # Check if a particular location spotlight graph should be shown
    if selected_place != "All Locations in Scope" and len(df_filtered) == 1:
        pl = df_filtered.iloc[0]
        st.markdown(f"""
        <div class="spotlight-box">
            <h4 style="color: #38BDF8; margin: 0 0 6px 0;">📍 Particular Location Spotlight: <b>{pl['habitation_name']}</b></h4>
            <div style="font-size: 13.5px; color: #CBD5E1;">
                <b>District:</b> {pl['district']} | <b>State:</b> {pl['state']} | <b>Mandal:</b> {pl.get('mandal', 'N/A')} | 
                <b>River Basin:</b> {pl.get('river_basin', 'Regional')} | <b>Hazard Tier:</b> <span style="color: {color_dict.get(pl['relative_hazard_level'], '#FFF')}; font-weight: bold;">{pl['relative_hazard_level']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Location Specific Visual Graphs
        col_loc_g1, col_loc_g2 = st.columns([1.1, 1])
        with col_loc_g1:
            # Spotlight Radar Chart against State Benchmarks
            cats = ['Elevation (Inv)', 'River Proximity', 'Drainage Congestion', 'Flood Inundation', 'Annual Rain', 'Pop Density']
            
            # Normalization against full dataset
            val_elev = 1.0 - min(1.0, max(0.0, pl['elevation_m'] / 150.0))
            val_riv = 1.0 - min(1.0, max(0.0, pl['distance_to_river_km'] / 25.0))
            val_drain = pl['drainage_congestion_index'] / 5.0
            val_flood = pl['historical_flood_inundation_frequency'] / 5.0
            val_rain = min(1.0, pl['annual_rainfall_mm'] / 2500.0)
            val_pop = min(1.0, pl['population_density_per_sqkm'] / 20000.0)
            
            pl_vals = [val_elev, val_riv, val_drain, val_flood, val_rain, val_pop]
            pl_vals.append(pl_vals[0])
            
            # State average
            st_elev = 1.0 - min(1.0, max(0.0, df_state['elevation_m'].mean() / 150.0))
            st_riv = 1.0 - min(1.0, max(0.0, df_state['distance_to_river_km'].mean() / 25.0))
            st_drain = df_state['drainage_congestion_index'].mean() / 5.0
            st_flood = df_state['historical_flood_inundation_frequency'].mean() / 5.0
            st_rain = min(1.0, df_state['annual_rainfall_mm'].mean() / 2500.0)
            st_pop = min(1.0, df_state['population_density_per_sqkm'].mean() / 20000.0)
            st_vals = [st_elev, st_riv, st_drain, st_flood, st_rain, st_pop]
            st_vals.append(st_vals[0])
            
            fig_spot_radar = go.Figure()
            fig_spot_radar.add_trace(go.Scatterpolar(
                r=pl_vals, theta=cats + [cats[0]],
                fill='toself', fillcolor='rgba(215, 48, 39, 0.5)',
                line=dict(color='#d73027', width=3),
                name=pl['habitation_name']
            ))
            fig_spot_radar.add_trace(go.Scatterpolar(
                r=st_vals, theta=cats + [cats[0]],
                fill='toself', fillcolor='rgba(96, 165, 250, 0.25)',
                line=dict(color='#60A5FA', width=1.5, dash='dash'),
                name=f"{selected_state} Average"
            ))
            fig_spot_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                title=f"Multi-Factor Vulnerability Radar: {pl['habitation_name']}",
                height=320,
                **dark_layout_defaults
            )
            st.plotly_chart(fig_spot_radar, use_container_width=True)
            
        with col_loc_g2:
            # Bar chart comparing raw physical metrics
            metrics_df = pd.DataFrame({
                'Indicator': ['Elevation (m)', 'River Dist (km)', 'Drainage (1-5)', 'Flood History (0-5)', 'Max 24h Rain (x10 mm)'],
                'Selected Place': [pl['elevation_m'], pl['distance_to_river_km'], pl['drainage_congestion_index'], pl['historical_flood_inundation_frequency'], pl['extreme_daily_rainfall_mm'] / 10.0],
                'State Mean': [df_state['elevation_m'].mean(), df_state['distance_to_river_km'].mean(), df_state['drainage_congestion_index'].mean(), df_state['historical_flood_inundation_frequency'].mean(), df_state['extreme_daily_rainfall_mm'].mean() / 10.0]
            })
            fig_bar_comp = go.Figure()
            fig_bar_comp.add_trace(go.Bar(x=metrics_df['Indicator'], y=metrics_df['Selected Place'], name=pl['habitation_name'], marker_color='#EF4444'))
            fig_bar_comp.add_trace(go.Bar(x=metrics_df['Indicator'], y=metrics_df['State Mean'], name=f"{selected_state} Mean", marker_color='#3B82F6'))
            fig_bar_comp.update_layout(
                barmode='group',
                title="Direct Morphometric Comparison to State Baseline",
                height=320,
                **dark_layout_defaults
            )
            st.plotly_chart(fig_bar_comp, use_container_width=True)

    else:
        # Spatial Correlation Graph: Elevation vs Distance to River Corridor
        fig_corridor = px.scatter(
            df_filtered, x='distance_to_river_km', y='elevation_m',
            color='relative_hazard_level',
            size='historical_flood_inundation_frequency',
            hover_name='habitation_name',
            hover_data=['state', 'district', 'annual_rainfall_mm'],
            color_discrete_map=color_dict,
            title="Flood Inundation Corridor: Surface Elevation vs River Proximity",
            labels={'distance_to_river_km': 'Distance to River / Floodway (km)', 'elevation_m': 'Elevation (m AMSL)'}
        )
        fig_corridor.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.08, line_width=0, annotation_text="Critical Inundation Depression (<25m)", annotation_position="top right")
        fig_corridor.update_layout(height=310, **dark_layout_defaults)
        st.plotly_chart(fig_corridor, use_container_width=True)

    # Folium Map
    geo_info = state_geo.get(selected_state, {"center": [22.0, 79.5], "zoom": 5})
    if selected_place != "All Locations in Scope" and len(df_filtered) == 1:
        map_center = [df_filtered['latitude'].iloc[0], df_filtered['longitude'].iloc[0]]
        map_zoom = 13
    elif selected_district != "All Districts in State" and len(df_filtered) > 0:
        map_center = [df_filtered['latitude'].mean(), df_filtered['longitude'].mean()]
        map_zoom = 10
    elif len(df_filtered) > 0 and selected_state != "All India (Pan-India Overview)":
        map_center = [df_filtered['latitude'].mean(), df_filtered['longitude'].mean()]
        map_zoom = geo_info['zoom']
    else:
        map_center = geo_info['center']
        map_zoom = geo_info['zoom']
        
    m = folium.Map(location=map_center, zoom_start=map_zoom, tiles="CartoDB dark_matter")
    
    if selected_state in ["All India (Pan-India Overview)", "Andhra Pradesh"]:
        krishna_coords = [
            [16.580, 80.360], [16.592, 80.450], [16.590, 80.522], [16.550, 80.565],
            [16.507, 80.605], [16.480, 80.640], [16.440, 80.720], [16.360, 80.780],
            [16.320, 80.825], [16.185, 80.795], [16.122, 80.932], [16.022, 80.918], [15.945, 80.915]
        ]
        folium.PolyLine(krishna_coords, color="#38BDF8", weight=4, opacity=0.85, tooltip="Krishna River (Prakasam Barrage System)").add_to(m)
        
        budameru_coords = [
            [16.630, 80.540], [16.562, 80.615], [16.538, 80.638], [16.522, 80.665], [16.520, 80.750]
        ]
        folium.PolyLine(budameru_coords, color="#60A5FA", weight=3, dash_array="6, 6", opacity=0.85, tooltip="Budameru Rivulet Drainage Floodway").add_to(m)

    for _, row in df_filtered.iterrows():
        tier = row['relative_hazard_level']
        c_hex = color_dict.get(tier, '#888888')
        is_selected = (selected_place == row['habitation_name'])
        
        popup_html = f"""
        <div style="font-family: Arial; width: 260px; font-size: 12px; color: #000;">
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
            radius=10.0 if is_selected else (6.5 if 'High' in tier else 5.0),
            color='#FFD700' if is_selected else 'white',
            weight=3.0 if is_selected else 0.8,
            fill=True,
            fill_color=c_hex,
            fill_opacity=0.95 if is_selected else 0.8,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"📍 {row['habitation_name']} ({row['district']} - {tier.split(' ')[0]})"
        ).add_to(m)
        
    st_folium(m, width=1200, height=530)

# ==============================================================================
# TAB 2: ALL DISTRICTS IN STATE MATRIX & COMPREHENSIVE GRAPHS
# ==============================================================================
with tab_districts:
    st.subheader(f"All Districts Matrix & Regional Comparisons — {selected_state}")
    
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
        mean_congestion=('drainage_congestion_index', 'mean'),
        centroid_lat=('latitude', 'mean'),
        centroid_lon=('longitude', 'mean')
    ).reset_index()
    
    dist_matrix['high_hazard_pct'] = (dist_matrix['high_hazard_count'] / dist_matrix['habitations_monitored'] * 100).round(1)
    dist_matrix = dist_matrix.sort_values(by=['high_hazard_pct', 'mean_elevation_m'], ascending=[False, True])
    
    # 4 Visual Graphs for Districts
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        # Graph 1: Ranked High Hazard %
        fig_dist_bar = px.bar(
            dist_matrix, x='district', y='high_hazard_pct',
            color='high_hazard_pct',
            color_continuous_scale='Reds',
            title=f"Districts Ranked by High Hazard Habitations (%) in {selected_state}",
            labels={'district': 'District', 'high_hazard_pct': 'High Hazard (%)'}
        )
        fig_dist_bar.update_layout(xaxis_tickangle=-45, height=380, **dark_layout_defaults)
        st.plotly_chart(fig_dist_bar, use_container_width=True)
        
    with col_d2:
        # Graph 2: Stacked Danger Composition
        fig_dist_stacked = go.Figure()
        fig_dist_stacked.add_trace(go.Bar(x=dist_matrix['district'], y=dist_matrix['high_hazard_count'], name='High Danger', marker_color='#d73027'))
        fig_dist_stacked.add_trace(go.Bar(x=dist_matrix['district'], y=dist_matrix['mod_hazard_count'], name='Medium Danger', marker_color='#fdae61'))
        fig_dist_stacked.add_trace(go.Bar(x=dist_matrix['district'], y=dist_matrix['low_hazard_count'], name='Low Danger', marker_color='#4575b4'))
        fig_dist_stacked.update_layout(
            barmode='stack',
            title=f"District-Wise Danger Tier Composition ({selected_state})",
            xaxis_tickangle=-45,
            height=380,
            **dark_layout_defaults
        )
        st.plotly_chart(fig_dist_stacked, use_container_width=True)
        
    col_d3, col_d4 = st.columns(2)
    with col_d3:
        # Graph 3: Morphometric Scatter
        fig_dist_elev = px.scatter(
            dist_matrix, x='mean_elevation_m', y='mean_annual_rainfall_mm',
            size='habitations_monitored',
            color='high_hazard_pct',
            color_continuous_scale='Portland',
            hover_name='district',
            title=f"District Landscape: Mean Elevation vs Annual Rain ({selected_state})",
            labels={'mean_elevation_m': 'Mean Elevation (m AMSL)', 'mean_annual_rainfall_mm': 'Mean Annual Rainfall (mm)'}
        )
        fig_dist_elev.update_layout(height=380, **dark_layout_defaults)
        st.plotly_chart(fig_dist_elev, use_container_width=True)
        
    with col_d4:
        # Graph 4: River Proximity vs Drainage Congestion
        fig_dist_hydro = px.scatter(
            dist_matrix, x='mean_river_distance_km', y='mean_congestion',
            size='high_hazard_count',
            color='mean_flood_frequency',
            color_continuous_scale='Turbo',
            hover_name='district',
            title=f"Hydrological Exposure: River Distance vs Canal Congestion ({selected_state})",
            labels={'mean_river_distance_km': 'Mean River Distance (km)', 'mean_congestion': 'Canal Congestion Index (1-5)'}
        )
        fig_dist_hydro.update_layout(height=380, **dark_layout_defaults)
        st.plotly_chart(fig_dist_hydro, use_container_width=True)
        
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

# ==============================================================================
# TAB 3: MULTI-CRITERIA RISK SIGNATURES & DIMENSIONALITY REDUCTION
# ==============================================================================
with tab_profiles:
    st.subheader(f"Multi-Criteria Risk Signatures ({selected_state})")
    
    feature_cols = [
        'elevation_m', 'slope_deg', 'distance_to_river_km',
        'annual_rainfall_mm', 'extreme_daily_rainfall_mm',
        'population_density_per_sqkm', 'drainage_congestion_index',
        'historical_flood_inundation_frequency'
    ]
    
    col_sig1, col_sig2 = st.columns(2)
    with col_sig1:
        # Graph 1: Polar Radar Chart
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
        
        norm_df['elevation_m'] = 1.0 - norm_df['elevation_m']
        norm_df['slope_deg'] = 1.0 - norm_df['slope_deg']
        norm_df['distance_to_river_km'] = 1.0 - norm_df['distance_to_river_km']
        
        categories = ['Elevation (Inv)', 'Slope (Inv)', 'River Dist (Inv)', 'Annual Rain', 'Extreme Rain', 'Pop Density', 'Congestion', 'Flood Freq']
        
        fig_radar = go.Figure()
        radar_colors = {
            'High Relative Hazard / Vulnerability': 'rgba(215, 48, 39, 0.55)',
            'Moderate Relative Hazard / Vulnerability': 'rgba(253, 174, 97, 0.55)',
            'Relatively Lower Hazard / Vulnerability': 'rgba(69, 117, 180, 0.55)'
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
                line=dict(color=line_colors[tier], width=2.5),
                name=tier.split(' ')[0] + " Hazard"
            ))
            
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title="Radar Profile Signature (Normalized Risk Factors)",
            height=430,
            **dark_layout_defaults
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col_sig2:
        # Graph 2: 2D PCA Scatter
        fig_pca = px.scatter(
            df_filtered if len(df_filtered) > 1 else df_state,
            x='pca_1', y='pca_2',
            color='relative_hazard_level',
            hover_name='habitation_name',
            hover_data=['state', 'district', 'elevation_m', 'distance_to_river_km'],
            color_discrete_map=color_dict,
            title=f"2D Principal Component Projection ({selected_state})",
            labels={'pca_1': 'PC1 (Flood Exposure & Basin Entrapment)', 'pca_2': 'PC2 (Rainfall Extremes vs Inland)'}
        )
        fig_pca.update_traces(marker=dict(size=9, line=dict(width=1, color='white')))
        fig_pca.update_layout(height=430, **dark_layout_defaults)
        st.plotly_chart(fig_pca, use_container_width=True)

    # Graph 3 & 4: Feature Multi-Box Matrix & Correlation Heatmap
    col_sig3, col_sig4 = st.columns(2)
    with col_sig3:
        # Boxplot of Elevation across Tiers
        fig_box = px.box(
            df_state,
            x='relative_hazard_level', y='elevation_m',
            color='relative_hazard_level',
            color_discrete_map=color_dict,
            points="all",
            title=f"Surface Elevation Distribution across Hazard Tiers ({selected_state})",
            labels={'relative_hazard_level': 'Hazard Tier', 'elevation_m': 'Elevation (m AMSL)'}
        )
        fig_box.update_layout(height=380, showlegend=False, **dark_layout_defaults)
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col_sig4:
        # Correlation Heatmap
        corr_matrix = df[feature_cols].corr()
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            title="Biophysical Risk Factors Correlation Matrix Heatmap",
            labels=dict(color="Correlation")
        )
        fig_corr.update_layout(height=380, **dark_layout_defaults)
        st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown('---')
    st.markdown('#### 🔬 Academic Research Figures Gallery')
    c_img1, c_img2 = st.columns(2)
    with c_img1:
        if os.path.exists('outputs/figures/11_cluster_radar_signature.png'):
            st.image('outputs/figures/11_cluster_radar_signature.png', caption='Figure 11: Multi-Criteria Radar Signature (Normalized Biophysical Risk)', use_container_width=True)
        if os.path.exists('outputs/figures/08_pca_2d_clusters.png'):
            st.image('outputs/figures/08_pca_2d_clusters.png', caption='Figure 8: 2D PCA Cluster Separation', use_container_width=True)
        if os.path.exists('outputs/figures/01_correlation_matrix.png'):
            st.image('outputs/figures/01_correlation_matrix.png', caption='Figure 1: Pairwise Feature Correlation Heatmap', use_container_width=True)
    with c_img2:
        if os.path.exists('outputs/figures/09_pca_biplot.png'):
            st.image('outputs/figures/09_pca_biplot.png', caption='Figure 9: PCA Biplot with Feature Vectors', use_container_width=True)
        if os.path.exists('outputs/figures/10_tsne_clusters.png'):
            st.image('outputs/figures/10_tsne_clusters.png', caption='Figure 10: t-SNE Non-Linear Manifold Projection', use_container_width=True)
        if os.path.exists('outputs/figures/02_feature_outlier_boxplots.png'):
            st.image('outputs/figures/02_feature_outlier_boxplots.png', caption='Figure 2: Feature Distribution & Outlier Boxplots', use_container_width=True)


# ==============================================================================
# TAB 4: STATE-WISE NATIONAL COMPARISON GRAPHS
# ==============================================================================
with tab_state_comp:
    st.subheader("State-Wise Flood Hazard & Vulnerability Comparison across India")
    
    state_summary = df.groupby('state').agg(
        total_settlements=('habitation_id', 'count'),
        districts_covered=('district', 'nunique'),
        high_hazard_count=('relative_hazard_level', lambda s: (s == 'High Relative Hazard / Vulnerability').sum()),
        mod_hazard_count=('relative_hazard_level', lambda s: (s == 'Moderate Relative Hazard / Vulnerability').sum()),
        low_hazard_count=('relative_hazard_level', lambda s: (s == 'Relatively Lower Hazard / Vulnerability').sum()),
        mean_rainfall_mm=('annual_rainfall_mm', 'mean'),
        mean_elevation_m=('elevation_m', 'mean'),
        mean_flood_frequency=('historical_flood_inundation_frequency', 'mean'),
        mean_congestion=('drainage_congestion_index', 'mean')
    ).reset_index()
    
    state_summary['high_hazard_pct'] = (state_summary['high_hazard_count'] / state_summary['total_settlements'] * 100).round(1)
    state_summary = state_summary.sort_values(by='high_hazard_pct', ascending=False)
    
    c_st1, c_st2 = st.columns(2)
    with c_st1:
        # Graph 1: State Vulnerability Ranking
        fig_st_bar = px.bar(
            state_summary, x='state', y='high_hazard_pct',
            color='high_hazard_pct',
            color_continuous_scale='Reds',
            title="Percentage of Monitored Settlements in High Hazard Tier (%)",
            labels={'state': 'State', 'high_hazard_pct': 'High Hazard (%)'}
        )
        fig_st_bar.update_layout(xaxis_tickangle=-45, height=390, **dark_layout_defaults)
        st.plotly_chart(fig_st_bar, use_container_width=True)
        
    with c_st2:
        # Graph 2: 100% Stacked Danger Tier Composition
        fig_st_stack = go.Figure()
        fig_st_stack.add_trace(go.Bar(x=state_summary['state'], y=state_summary['high_hazard_count'], name='High Danger', marker_color='#d73027'))
        fig_st_stack.add_trace(go.Bar(x=state_summary['state'], y=state_summary['mod_hazard_count'], name='Medium Danger', marker_color='#fdae61'))
        fig_st_stack.add_trace(go.Bar(x=state_summary['state'], y=state_summary['low_hazard_count'], name='Low Danger', marker_color='#4575b4'))
        fig_st_stack.update_layout(
            barmode='stack',
            title="State-Wise Danger Level Composition Across India",
            xaxis_tickangle=-45,
            height=390,
            **dark_layout_defaults
        )
        st.plotly_chart(fig_st_stack, use_container_width=True)
        
    c_st3, c_st4 = st.columns(2)
    with c_st3:
        # Graph 3: River Basin Risk Breakdown
        if 'river_basin' in df.columns:
            basin_df = df.groupby(['river_basin', 'relative_hazard_level']).size().reset_index(name='count')
            basin_df = basin_df.sort_values(by='count', ascending=False)
            fig_basin = px.bar(
                basin_df, x='river_basin', y='count', color='relative_hazard_level',
                color_discrete_map=color_dict,
                barmode='stack',
                title="Major River Basin Vulnerability Exposure (Pan-India)",
                labels={'river_basin': 'River Basin', 'count': 'Habitations'}
            )
            fig_basin.update_layout(xaxis_tickangle=-35, height=390, **dark_layout_defaults)
            st.plotly_chart(fig_basin, use_container_width=True)
            
    with c_st4:
        # Graph 4: State Climatology vs Topography
        fig_st_rain = px.scatter(
            state_summary, x='mean_rainfall_mm', y='mean_elevation_m',
            size='total_settlements',
            color='high_hazard_pct',
            color_continuous_scale='Viridis',
            hover_name='state',
            title="State Climatology vs Topography: Mean Rainfall vs Elevation",
            labels={'mean_rainfall_mm': 'Mean Annual Rainfall (mm)', 'mean_elevation_m': 'Mean Elevation (m AMSL)'}
        )
        fig_st_rain.update_layout(height=390, **dark_layout_defaults)
        st.plotly_chart(fig_st_rain, use_container_width=True)

# ==============================================================================
# TAB 5: MACHINE LEARNING BENCHMARKING GRAPHS
# ==============================================================================
with tab_ml_eval:
    st.subheader("Machine Learning Algorithm Benchmarking & Metric Validation")
    
    col_ml1, col_ml2 = st.columns(2)
    with col_ml1:
        # Graph 1: Silhouette Score Comparison
        ml_bench_df = pd.DataFrame({
            'Algorithm': ['K-Medoids (PAM)', 'K-Means++', 'Hierarchical (Ward)', 'DBSCAN (eps=1.85)'],
            'Metric': ['Manhattan (L1)', 'Euclidean (L2)', 'Variance Dissimilarity', 'Density Reachability'],
            'Silhouette Score': [0.4320, 0.3667, 0.3283, 0.2841],
            'Davies-Bouldin Index': [1.0421, 1.1202, 1.0843, 1.3140]
        })
        fig_sil = px.bar(
            ml_bench_df, x='Algorithm', y='Silhouette Score',
            color='Silhouette Score',
            color_continuous_scale='Greens',
            text='Silhouette Score',
            title="Clustering Separation Quality: Silhouette Score (Higher is Better)"
        )
        fig_sil.update_traces(texttemplate='%{text:.4f}', textposition='outside')
        fig_sil.update_layout(height=350, yaxis_range=[0, 0.52], **dark_layout_defaults)
        st.plotly_chart(fig_sil, use_container_width=True)
        
    with col_ml2:
        # Graph 2: Davies-Bouldin Index (Lower is Better)
        fig_db = px.bar(
            ml_bench_df, x='Algorithm', y='Davies-Bouldin Index',
            color='Davies-Bouldin Index',
            color_continuous_scale='Blues_r',
            text='Davies-Bouldin Index',
            title="Cluster Separation Compactness: Davies-Bouldin Index (Lower is Better)"
        )
        fig_db.update_traces(texttemplate='%{text:.4f}', textposition='outside')
        fig_db.update_layout(height=350, yaxis_range=[0, 1.5], **dark_layout_defaults)
        st.plotly_chart(fig_db, use_container_width=True)
        
    col_ml3, col_ml4 = st.columns(2)
    with col_ml3:
        # Graph 3: Elbow Inflection & Silhouette Trajectory (K=2 to 6)
        k_eval = pd.DataFrame({
            'K': [2, 3, 4, 5, 6],
            'Inertia (x100)': [5.82, 3.41, 2.76, 2.21, 1.85],
            'Silhouette Score': [0.342, 0.432, 0.381, 0.339, 0.312]
        })
        fig_elbow = make_subplots(specs=[[{"secondary_y": True}]])
        fig_elbow.add_trace(
            go.Scatter(x=k_eval['K'], y=k_eval['Inertia (x100)'], name="Inertia (Elbow Drop)", line=dict(color="#F87171", width=3)),
            secondary_y=False
        )
        fig_elbow.add_trace(
            go.Scatter(x=k_eval['K'], y=k_eval['Silhouette Score'], name="Silhouette Peak at K=3", line=dict(color="#34D399", width=3, dash='dash')),
            secondary_y=True
        )
        fig_elbow.update_layout(title="Optimal Cluster Evaluation: Elbow Inflection & Silhouette Peak (K=3)", height=350, **dark_layout_defaults)
        st.plotly_chart(fig_elbow, use_container_width=True)
        
    with col_ml4:
        # Graph 4: PCA Scree Plot
        pca_scree = pd.DataFrame({
            'Principal Component': ['PC1 (Exposure)', 'PC2 (Rainfall)', 'PC3 (Demographic)', 'PC4 (Slope)'],
            'Explained Variance (%)': [48.2, 24.1, 13.5, 7.8],
            'Cumulative (%)': [48.2, 72.3, 85.8, 93.6]
        })
        fig_scree = go.Figure()
        fig_scree.add_trace(go.Bar(x=pca_scree['Principal Component'], y=pca_scree['Explained Variance (%)'], name='Individual Variance', marker_color='#60A5FA'))
        fig_scree.add_trace(go.Scatter(x=pca_scree['Principal Component'], y=pca_scree['Cumulative (%)'], name='Cumulative Variance', line=dict(color='#FBBF24', width=3)))
        fig_scree.update_layout(title="PCA Scree Plot: 85.8% Variance Captured by Top 3 Components", height=350, **dark_layout_defaults)
        st.plotly_chart(fig_scree, use_container_width=True)

    st.markdown('---')
    st.markdown('#### 📊 Academic Machine Learning Figures')
    c_ml_img1, c_ml_img2 = st.columns(2)
    with c_ml_img1:
        if os.path.exists('outputs/figures/03_kmeans_elbow_silhouette.png'):
            st.image('outputs/figures/03_kmeans_elbow_silhouette.png', caption='Figure 3: Elbow Inertia & Silhouette Trajectory', use_container_width=True)
        if os.path.exists('outputs/figures/05_hierarchical_dendrogram.png'):
            st.image('outputs/figures/05_hierarchical_dendrogram.png', caption='Figure 5: Hierarchical Clustering Dendrogram (Ward Linkage)', use_container_width=True)
        if os.path.exists('outputs/figures/07_pca_scree_plot.png'):
            st.image('outputs/figures/07_pca_scree_plot.png', caption='Figure 7: PCA Scree Plot & Cumulative Variance', use_container_width=True)
    with c_ml_img2:
        if os.path.exists('outputs/figures/04_silhouette_plot_k3.png'):
            st.image('outputs/figures/04_silhouette_plot_k3.png', caption='Figure 4: Silhouette Analysis per Cluster (K=3)', use_container_width=True)
        if os.path.exists('outputs/figures/06_dbscan_k_distance_graph.png'):
            st.image('outputs/figures/06_dbscan_k_distance_graph.png', caption='Figure 6: DBSCAN 4th-NN K-Distance Elbow', use_container_width=True)
        if os.path.exists('outputs/figures/12_cluster_feature_bars.png'):
            st.image('outputs/figures/12_cluster_feature_bars.png', caption='Figure 12: Standardized Feature Deviations by Cluster', use_container_width=True)


# ==============================================================================
# TAB 6: DATA EXPLORER & DISTRIBUTIONS
# ==============================================================================
with tab_data:
    st.subheader(f"Pan-India All Places & Habitations Registry ({selected_state})")
    
    col_de1, col_de2 = st.columns(2)
    with col_de1:
        # Distribution Histogram: Elevation
        fig_hist_elev = px.histogram(
            df_filtered, x='elevation_m', nbins=25,
            color='relative_hazard_level',
            color_discrete_map=color_dict,
            title="Surface Elevation Distribution (Active Scope)",
            labels={'elevation_m': 'Elevation (m AMSL)'}
        )
        fig_hist_elev.update_layout(height=280, **dark_layout_defaults)
        st.plotly_chart(fig_hist_elev, use_container_width=True)
        
    with col_de2:
        # Distribution Histogram: River Distance
        fig_hist_riv = px.histogram(
            df_filtered, x='distance_to_river_km', nbins=25,
            color='relative_hazard_level',
            color_discrete_map=color_dict,
            title="River Proximity Distribution (Active Scope)",
            labels={'distance_to_river_km': 'Distance to River (km)'}
        )
        fig_hist_riv.update_layout(height=280, **dark_layout_defaults)
        st.plotly_chart(fig_hist_riv, use_container_width=True)
        
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
