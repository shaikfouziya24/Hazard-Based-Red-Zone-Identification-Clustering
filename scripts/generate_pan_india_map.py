import os
import folium
import pandas as pd

print("=== Generating Standalone Pan-India Interactive Folium Map ===")
df = pd.read_csv("data/processed/india_habitations_complete.csv")

m = folium.Map(location=[22.0, 79.5], zoom_start=5, tiles="OpenStreetMap")

# River Overlays (Krishna & Budameru)
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

# Feature Groups by Tier
fg_high = folium.FeatureGroup(name="High Relative Hazard / Vulnerability (Red)")
fg_mod = folium.FeatureGroup(name="Moderate Relative Hazard / Vulnerability (Orange)")
fg_low = folium.FeatureGroup(name="Relatively Lower Hazard / Vulnerability (Blue)")

color_map = {
    'High Relative Hazard / Vulnerability': ('#d73027', fg_high),
    'Moderate Relative Hazard / Vulnerability': ('#fdae61', fg_mod),
    'Relatively Lower Hazard / Vulnerability': ('#4575b4', fg_low)
}

for _, r in df.iterrows():
    c_hex, fg = color_map[r['relative_hazard_level']]
    
    popup_html = f"""
    <div style="font-family: Arial; width: 260px; font-size: 12px;">
        <h4 style="margin: 0 0 6px 0; color: {c_hex}; border-bottom: 2px solid {c_hex}; padding-bottom: 3px;">
            {r['habitation_name']}
        </h4>
        <b>State:</b> {r['state']}<br>
        <b>District:</b> {r['district']} | <b>Mandal:</b> {r.get('mandal', 'N/A')}<br>
        <b>River Basin:</b> {r.get('river_basin', 'Regional')}<br>
        <hr style="margin: 5px 0;">
        <b>Relative Cluster:</b> <span style="color: {c_hex}; font-weight: bold;">{r['relative_hazard_level']}</span><br>
        <b>Elevation:</b> {r['elevation_m']:.1f} m AMSL<br>
        <b>Distance to River:</b> {r['distance_to_river_km']:.2f} km<br>
        <b>Historical Floods:</b> {r['historical_flood_inundation_frequency']}/5<br>
        <b>Drainage Congestion:</b> {r['drainage_congestion_index']}/5<br>
        <b>Annual Rain:</b> {r['annual_rainfall_mm']:.1f} mm<br>
        <b>Max 24h Rain:</b> {r['extreme_daily_rainfall_mm']:.1f} mm<br>
        <b>Pop Density:</b> {r['population_density_per_sqkm']:,.0f} /km²
    </div>
    """
    
    folium.CircleMarker(
        location=[r['latitude'], r['longitude']],
        radius=6.5 if 'High' in r['relative_hazard_level'] else 5.0,
        color='black',
        weight=0.7,
        fill=True,
        fill_color=c_hex,
        fill_opacity=0.85,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{r['habitation_name']} ({r['state']} - {r['relative_hazard_level'].split(' ')[0]})"
    ).add_to(fg)

fg_high.add_to(m)
fg_mod.add_to(m)
fg_low.add_to(m)

# National Legend
legend_html = '''
<div style="position: fixed; 
     bottom: 25px; left: 25px; width: 340px; height: 185px; 
     background-color: white; border:2px solid #888; z-index:9999; font-size:11.5px;
     padding: 10px; border-radius: 6px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
     <b>SIH26191: Pan-India Flood Hazard & Vulnerability Tiers</b><br>
     <i>166 Settlements Across 15 Indian States / Territories</i><br>
     <hr style="margin: 5px 0;">
     <i class="fa fa-circle" style="color:#d73027"></i> &nbsp;<b>High Relative Hazard / Vulnerability</b><br>
     <i class="fa fa-circle" style="color:#fdae61"></i> &nbsp;<b>Moderate Relative Hazard / Vulnerability</b><br>
     <i class="fa fa-circle" style="color:#4575b4"></i> &nbsp;<b>Relatively Lower Hazard / Vulnerability</b><br>
     <span style="color:#0055ff; font-weight:bold;">―</span> &nbsp;Major River Channels (Krishna / Ganga / Brahmaputra)<br>
     <small style="color: #666;">Note: Academic unsupervised classification; not an official disaster warning.</small>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))
folium.LayerControl(collapsed=False).add_to(m)

out_map = "outputs/figures/pan_india_flood_hazard_map.html"
m.save(out_map)
print(f"Saved standalone Pan-India map to {out_map}!")
