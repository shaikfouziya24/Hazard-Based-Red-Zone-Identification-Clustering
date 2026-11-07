import os
import pandas as pd
import json

def realign_app_py():
    with open('dashboard/app.py', 'r', encoding='utf-8') as f:
        orig = f.read()

    # 1. Remove executive visual analytics from hero
    start_marker = '# ==============================================================================\n# MAXIMUM DATA IN GRAPH FORM: EXECUTIVE VISUAL ANALYTICS ROW'
    end_marker = '# ⚡ LIVE REAL-TIME WEATHER & DYNAMIC FLOOD ALERT SECTION'

    idx1 = orig.find(start_marker)
    idx2 = orig.find(end_marker)

    if idx1 != -1 and idx2 != -1:
        color_dict_def = '''# Color palette definition for hazard tiers
color_dict = {
    'High Relative Hazard / Vulnerability': '#d73027',     # Red
    'Moderate Relative Hazard / Vulnerability': '#fdae61', # Orange/Yellow
    'Relatively Lower Hazard / Vulnerability': '#4575b4'   # Blue
}

'''
        step1 = orig[:idx1] + color_dict_def + orig[idx2:]
    else:
        step1 = orig

    # 2. Realign Tab 1 & Tab 2
    t1_marker = '# ==============================================================================\n# TAB 1: INTERACTIVE GEOSPATIAL MAP & SPOTLIGHT GRAPHS\n# ==============================================================================\nwith tab_map:'
    t2_marker = '# ==============================================================================\n# TAB 2: ALL DISTRICTS IN STATE MATRIX & COMPREHENSIVE GRAPHS\n# ==============================================================================\nwith tab_districts:'
    t3_marker = '# ==============================================================================\n# TAB 3: MULTI-CRITERIA RISK SIGNATURES & DIMENSIONALITY REDUCTION'

    t1_idx = step1.find(t1_marker)
    t2_idx = step1.find(t2_marker)
    t3_idx = step1.find(t3_marker)

    if t1_idx != -1 and t2_idx != -1 and t3_idx != -1:
        new_tab1 = '''# ==============================================================================
# TAB 1: INTERACTIVE GEOSPATIAL MAP & SPOTLIGHT GRAPHS
# ==============================================================================
with tab_map:
    st.subheader(f"Geospatial Hazard Distribution — {selected_state} ({selected_district})")
    st.write(f"Displaying **{len(df_filtered)} habitation(s)** across **{df_filtered['district'].nunique()} district(s)**. Circle markers reflect unsupervised ML hazard tiers. Click any place marker for complete biophysical metrics.")
    
    # Check if a particular location spotlight info box should be shown
    if selected_place != "All Locations in Scope" and len(df_filtered) == 1:
        pl = df_filtered.iloc[0]
        st.markdown(f"""
        <div class="spotlight-box">
            <h4 style="color: #38BDF8; margin: 0 0 6px 0;">📍 Particular Location Spotlight: <b>{pl['habitation_name']}</b></h4>
            <div style="font-size: 13.5px; color: #CBD5E1;">
                <b>District:</b> {pl['district']} | <b>State:</b> {pl['state']} | <b>Mandal:</b> {pl.get('mandal', 'N/A')} | 
                <b>River Basin:</b> {pl.get('river_basin', 'Regional')} | <b>Hazard Tier:</b> <span style="color: {color_dict.get(pl['relative_hazard_level'], '#FFF')}; font-weight: bold;">{pl['relative_hazard_level']}</span><br>
                <b>Elevation:</b> {pl['elevation_m']:.1f} m AMSL | <b>River Distance:</b> {pl['distance_to_river_km']:.2f} km | <b>Historical Floods:</b> {pl['historical_flood_inundation_frequency']}/5 | <b>Drainage Congestion:</b> {pl['drainage_congestion_index']}/5
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Folium Interactive Map
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
        
    m = folium.Map(location=map_center, zoom_start=map_zoom, tiles="OpenStreetMap")
    
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

    # Detailed Visual Analytics below Map
    if selected_place != "All Locations in Scope" and len(df_filtered) == 1:
        pl = df_filtered.iloc[0]
        st.markdown("---")
        st.markdown(f"#### 🔍 Detailed Morphometric Diagnostic: {pl['habitation_name']}")
        col_loc_g1, col_loc_g2 = st.columns([1.1, 1])
        with col_loc_g1:
            cats = ['Elevation (Inv)', 'River Proximity', 'Drainage Congestion', 'Flood Inundation', 'Annual Rain', 'Pop Density']
            val_elev = 1.0 - min(1.0, max(0.0, pl['elevation_m'] / 150.0))
            val_riv = 1.0 - min(1.0, max(0.0, pl['distance_to_river_km'] / 25.0))
            val_drain = pl['drainage_congestion_index'] / 5.0
            val_flood = pl['historical_flood_inundation_frequency'] / 5.0
            val_rain = min(1.0, pl['annual_rainfall_mm'] / 2500.0)
            val_pop = min(1.0, pl['population_density_per_sqkm'] / 20000.0)
            pl_vals = [val_elev, val_riv, val_drain, val_flood, val_rain, val_pop]
            pl_vals.append(pl_vals[0])
            
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

'''

        old_tab2_body = step1[t2_idx:t3_idx]

        new_tab2_prefix = '''# ==============================================================================
# TAB 2: ALL DISTRICTS IN STATE MATRIX & COMPREHENSIVE GRAPHS
# ==============================================================================
with tab_districts:
    st.subheader(f"All Districts Matrix & Regional Comparisons — {selected_state}")
    st.write(f"Detailed multi-criteria breakdown across **all {df_state['district'].nunique()} districts** in **{selected_state}**:")
    
    # Executive Risk Analytics Row
    st.markdown("#### 📈 Active Scope Danger Distribution & Category Breakdown")
    col_g1, col_g2, col_g3 = st.columns([1, 1.2, 1.3])
    
    with col_g1:
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
'''

        dm_idx = old_tab2_body.find('dist_matrix = df_state.groupby')
        assert dm_idx != -1
        new_tab2 = new_tab2_prefix + '\n    ' + old_tab2_body[dm_idx:]

        final_app = step1[:t1_idx] + new_tab1 + new_tab2 + step1[t3_idx:]

        with open('dashboard/app.py', 'w', encoding='utf-8') as f:
            f.write(final_app)
        print("Realigned dashboard/app.py successfully!")

def realign_pages_builder():
    with open('scripts/build_github_pages_app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    sub1 = '<!-- Executive Graphs Overview Row -->'
    sub2 = '<!-- Live Real-Time Weather Section -->'

    idx1 = content.find(sub1)
    idx2 = content.find(sub2)

    if idx1 != -1 and idx2 != -1:
        exec_chunk = content[idx1:idx2]
        step1 = content[:idx1] + content[idx2:]
    else:
        print("Could not find executive graphs overview row in builder script")
        return

    # In Tab 1, ensure map is before spotlight-graph-box
    t1_map_marker = '<div id="map"></div>'
    t1_spot_marker = '<div id="spotlight-graph-box"'
    
    idx_map = step1.find(t1_map_marker)
    idx_spot = step1.find(t1_spot_marker)
    
    if idx_spot != -1 and idx_map != -1 and idx_spot < idx_map:
        end_spot_marker = '</div>\n            <div id="map"></div>'
        idx_end_spot = step1.find(end_spot_marker)
        if idx_end_spot != -1:
            spot_block = step1[idx_spot:idx_end_spot + 6]
            step1 = step1[:idx_spot] + '<div id="map"></div>\n\n            ' + spot_block + step1[idx_end_spot + len(end_spot_marker):]

    # In Tab 2, insert exec_chunk right after description
    t2_desc_marker = '<div class="tab-section-sub" id="districts-section-sub">Detailed multi-criteria breakdown across all monitored districts:</div>\n            </div>'
    idx_t2 = step1.find(t2_desc_marker)
    if idx_t2 != -1:
        insert_pos = idx_t2 + len(t2_desc_marker)
        step1 = step1[:insert_pos] + '\n\n            ' + exec_chunk.strip() + '\n' + step1[insert_pos:]

    with open('scripts/build_github_pages_app.py', 'w', encoding='utf-8') as f:
        f.write(step1)
    print("Realigned scripts/build_github_pages_app.py successfully!")

def verify_order():
    with open('index.html', 'r', encoding='utf-8') as f:
        text = f.read()

    pos_metrics = text.find('metrics-row')
    pos_alert = text.find('alert-banner')
    pos_tabs = text.find('tab-bar')
    pos_map_tab = text.find('id="tab-map"')
    pos_map_div = text.find('id="map"')
    pos_tab_dist = text.find('id="tab-districts"')
    pos_donut = text.find('dangerDonutChart')
    pos_tab_sig = text.find('id="tab-signatures"')

    print('Order of elements in index.html:')
    print('1. metrics-row:', pos_metrics)
    print('2. alert-banner:', pos_alert)
    print('3. tab-bar:', pos_tabs)
    print('4. tab-map:', pos_map_tab)
    print('5. map div:', pos_map_div)
    print('6. tab-districts:', pos_tab_dist)
    print('7. dangerDonutChart:', pos_donut)
    print('8. tab-signatures:', pos_tab_sig)

    assert pos_metrics < pos_alert < pos_tabs < pos_map_tab < pos_map_div
    assert pos_tab_dist < pos_donut < pos_tab_sig
    print('All elements in index.html are in PERFECT order matching user laptop screenshot!')

if __name__ == '__main__':
    realign_app_py()
    realign_pages_builder()
    # Now run build_github_pages_app.py
    os.system(r'.\.venv\Scripts\python.exe scripts\build_github_pages_app.py')
    verify_order()
