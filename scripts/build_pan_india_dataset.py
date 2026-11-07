import os
import json
import urllib.request
import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, davies_bouldin_score
from scipy.spatial.distance import cdist

def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 6371.0 * 2 * asin(sqrt(a))

def get_elevation_batch(lats, lons):
    lat_str = ",".join([f"{lat:.4f}" for lat in lats])
    lon_str = ",".join([f"{lon:.4f}" for lon in lons])
    url = f"https://api.open-meteo.com/v1/elevation?latitude={lat_str}&longitude={lon_str}"
    req = urllib.request.Request(url, headers={'User-Agent': 'PanIndiaFloodProject/1.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())
        return data.get('elevation', [])

print("=== Building Comprehensive Pan-India Multi-State Dataset ===")

# Load existing 100 AP habitations
df_ap = pd.read_csv("data/processed/habitations_complete_analysis.csv")
df_ap['state'] = 'Andhra Pradesh'
df_ap['river_basin'] = 'Krishna Basin'

# Define Key Flood-Prone Habitations Across Other Indian States
# Based on CWC Flood Prone Areas, IIT Delhi IFI-Impacts, and IMD Climatological Atlas
pan_india_habitations = [
    # --- ASSAM (Brahmaputra & Barak Basins) ---
    {"state": "Assam", "district": "Kamrup Metropolitan", "mandal": "Guwahati", "name": "Guwahati (Bharalu Basin)", "category": "City", "lat": 26.1850, "lon": 91.7500, "pop": 960000, "area_sqkm": 65.0, "annual_rain": 1720.0, "monsoon_rain": 1150.0, "extreme_rain": 210.0, "flood_hist": 5, "congestion": 5, "river_basin": "Brahmaputra", "riv_lat": 26.1920, "riv_lon": 91.7550},
    {"state": "Assam", "district": "Majuli", "mandal": "Majuli", "name": "Garamur (Majuli Island)", "category": "Island Settlement", "lat": 26.9650, "lon": 94.2150, "pop": 168000, "area_sqkm": 352.0, "annual_rain": 2150.0, "monsoon_rain": 1480.0, "extreme_rain": 245.0, "flood_hist": 5, "congestion": 5, "river_basin": "Brahmaputra", "riv_lat": 26.9700, "riv_lon": 94.2200},
    {"state": "Assam", "district": "Golaghat", "mandal": "Bokakhat", "name": "Kaziranga Buffer Habitations", "category": "Eco-Settlement", "lat": 26.5850, "lon": 93.1720, "pop": 34000, "area_sqkm": 42.0, "annual_rain": 2240.0, "monsoon_rain": 1520.0, "extreme_rain": 260.0, "flood_hist": 5, "congestion": 4, "river_basin": "Brahmaputra", "riv_lat": 26.6500, "riv_lon": 93.1800},
    {"state": "Assam", "district": "Cachar", "mandal": "Silchar", "name": "Silchar (Barak Valley)", "category": "City", "lat": 24.8333, "lon": 92.7789, "pop": 230000, "area_sqkm": 28.0, "annual_rain": 3100.0, "monsoon_rain": 2100.0, "extreme_rain": 315.0, "flood_hist": 5, "congestion": 5, "river_basin": "Barak", "riv_lat": 24.8400, "riv_lon": 92.7850},
    {"state": "Assam", "district": "Dibrugarh", "mandal": "Dibrugarh", "name": "Dibrugarh Town", "category": "Town", "lat": 27.4728, "lon": 94.9120, "pop": 154000, "area_sqkm": 24.5, "annual_rain": 2550.0, "monsoon_rain": 1720.0, "extreme_rain": 230.0, "flood_hist": 4, "congestion": 4, "river_basin": "Brahmaputra", "riv_lat": 27.4850, "riv_lon": 94.9200},
    {"state": "Assam", "district": "Barpeta", "mandal": "Barpeta", "name": "Barpeta Lowlands", "category": "Town", "lat": 26.3200, "lon": 91.0100, "pop": 43000, "area_sqkm": 12.0, "annual_rain": 2350.0, "monsoon_rain": 1620.0, "extreme_rain": 250.0, "flood_hist": 5, "congestion": 5, "river_basin": "Brahmaputra", "riv_lat": 26.3400, "riv_lon": 91.0200},
    {"state": "Assam", "district": "Morigaon", "mandal": "Mayang", "name": "Mayang Flood Fringe", "category": "Village", "lat": 26.2350, "lon": 92.0550, "pop": 19500, "area_sqkm": 14.0, "annual_rain": 1950.0, "monsoon_rain": 1340.0, "extreme_rain": 220.0, "flood_hist": 4, "congestion": 4, "river_basin": "Brahmaputra", "riv_lat": 26.2600, "riv_lon": 92.0600},
    {"state": "Assam", "district": "Dhubri", "mandal": "Dhubri", "name": "Dhubri Riverport", "category": "Town", "lat": 26.0200, "lon": 89.9800, "pop": 64000, "area_sqkm": 16.0, "annual_rain": 2400.0, "monsoon_rain": 1650.0, "extreme_rain": 270.0, "flood_hist": 5, "congestion": 5, "river_basin": "Brahmaputra", "riv_lat": 26.0150, "riv_lon": 89.9750},

    # --- BIHAR (Kosi, Gandak, Bagmati & Ganga Basins) ---
    {"state": "Bihar", "district": "Patna", "mandal": "Patna Sadar", "name": "Patna (Rajendra Nagar / Kankarbagh)", "category": "City", "lat": 25.6050, "lon": 85.1550, "pop": 850000, "area_sqkm": 42.0, "annual_rain": 1120.0, "monsoon_rain": 940.0, "extreme_rain": 205.0, "flood_hist": 4, "congestion": 5, "river_basin": "Ganga", "riv_lat": 25.6200, "riv_lon": 85.1600},
    {"state": "Bihar", "district": "Supaul", "mandal": "Nirmali", "name": "Nirmali (Kosi Embankment)", "category": "Town", "lat": 26.3150, "lon": 86.6000, "pop": 24000, "area_sqkm": 8.5, "annual_rain": 1380.0, "monsoon_rain": 1180.0, "extreme_rain": 280.0, "flood_hist": 5, "congestion": 5, "river_basin": "Kosi", "riv_lat": 26.3200, "riv_lon": 86.5800},
    {"state": "Bihar", "district": "Bhagalpur", "mandal": "Kahalgaon", "name": "Kahalgaon Diara", "category": "Town", "lat": 25.2600, "lon": 87.2400, "pop": 48000, "area_sqkm": 15.0, "annual_rain": 1210.0, "monsoon_rain": 1020.0, "extreme_rain": 225.0, "flood_hist": 4, "congestion": 4, "river_basin": "Ganga", "riv_lat": 25.2750, "riv_lon": 87.2350},
    {"state": "Bihar", "district": "Darbhanga", "mandal": "Kusheshwar Asthan", "name": "Kusheshwar Asthan Chaur", "category": "Village Node", "lat": 25.8200, "lon": 86.1500, "pop": 31000, "area_sqkm": 18.0, "annual_rain": 1290.0, "monsoon_rain": 1090.0, "extreme_rain": 240.0, "flood_hist": 5, "congestion": 5, "river_basin": "Kamla-Balan", "riv_lat": 25.8300, "riv_lon": 86.1400},
    {"state": "Bihar", "district": "Muzaffarpur", "mandal": "Aurai", "name": "Aurai (Bagmati Floodway)", "category": "Village Node", "lat": 26.2800, "lon": 85.5200, "pop": 26000, "area_sqkm": 14.5, "annual_rain": 1250.0, "monsoon_rain": 1040.0, "extreme_rain": 235.0, "flood_hist": 5, "congestion": 5, "river_basin": "Bagmati", "riv_lat": 26.2900, "riv_lon": 85.5100},
    {"state": "Bihar", "district": "Khagaria", "mandal": "Alauli", "name": "Alauli Lowland Tract", "category": "Village", "lat": 25.6500, "lon": 86.4200, "pop": 18500, "area_sqkm": 11.0, "annual_rain": 1230.0, "monsoon_rain": 1030.0, "extreme_rain": 215.0, "flood_hist": 5, "congestion": 5, "river_basin": "Kosi-Gandak", "riv_lat": 25.6400, "riv_lon": 86.4300},
    {"state": "Bihar", "district": "Samastipur", "mandal": "Rosera", "name": "Rosera (Budhi Gandak)", "category": "Town", "lat": 25.7500, "lon": 86.0100, "pop": 35000, "area_sqkm": 9.5, "annual_rain": 1190.0, "monsoon_rain": 980.0, "extreme_rain": 195.0, "flood_hist": 4, "congestion": 4, "river_basin": "Budhi Gandak", "riv_lat": 25.7600, "riv_lon": 86.0050},
    {"state": "Bihar", "district": "Gaya", "mandal": "Gaya Sadar", "name": "Gaya Upland Plateau", "category": "City", "lat": 24.7950, "lon": 85.0000, "pop": 470000, "area_sqkm": 50.0, "annual_rain": 1010.0, "monsoon_rain": 880.0, "extreme_rain": 160.0, "flood_hist": 1, "congestion": 1, "river_basin": "Falgu", "riv_lat": 24.7800, "riv_lon": 85.0200},

    # --- KERALA (Periyar, Pamba, Chalakudy & Meenachil Basins) ---
    {"state": "Kerala", "district": "Alappuzha", "mandal": "Kuttanad", "name": "Champakkulam (Kuttanad Delta)", "category": "Delta Wetland", "lat": 9.4200, "lon": 76.4300, "pop": 28000, "area_sqkm": 16.0, "annual_rain": 2980.0, "monsoon_rain": 2150.0, "extreme_rain": 310.0, "flood_hist": 5, "congestion": 5, "river_basin": "Pamba", "riv_lat": 9.4250, "riv_lon": 76.4350},
    {"state": "Kerala", "district": "Ernakulam", "mandal": "Aluva", "name": "Aluva (Periyar Floodplain)", "category": "Town", "lat": 10.1080, "lon": 76.3550, "pop": 82000, "area_sqkm": 14.2, "annual_rain": 3120.0, "monsoon_rain": 2280.0, "extreme_rain": 335.0, "flood_hist": 5, "congestion": 4, "river_basin": "Periyar", "riv_lat": 10.1150, "riv_lon": 76.3500},
    {"state": "Kerala", "district": "Thrissur", "mandal": "Chalakudy", "name": "Chalakudy Riverfront", "category": "Town", "lat": 10.3070, "lon": 76.3330, "pop": 49000, "area_sqkm": 12.5, "annual_rain": 3050.0, "monsoon_rain": 2210.0, "extreme_rain": 340.0, "flood_hist": 5, "congestion": 4, "river_basin": "Chalakudy", "riv_lat": 10.3120, "riv_lon": 76.3280},
    {"state": "Kerala", "district": "Pathanamthitta", "mandal": "Chengannur", "name": "Ranni / Kozhencherry", "category": "Town", "lat": 9.3800, "lon": 76.7800, "pop": 34000, "area_sqkm": 15.0, "annual_rain": 2850.0, "monsoon_rain": 1950.0, "extreme_rain": 290.0, "flood_hist": 4, "congestion": 3, "river_basin": "Pamba", "riv_lat": 9.3850, "riv_lon": 76.7750},
    {"state": "Kerala", "district": "Wayanad", "mandal": "Mananthavady", "name": "Mananthavady (Kabini Reach)", "category": "Highland Valley", "lat": 11.8020, "lon": 76.0030, "pop": 42000, "area_sqkm": 28.0, "annual_rain": 3400.0, "monsoon_rain": 2600.0, "extreme_rain": 380.0, "flood_hist": 4, "congestion": 3, "river_basin": "Kabini", "riv_lat": 11.8100, "riv_lon": 76.0100},
    {"state": "Kerala", "district": "Idukki", "mandal": "Munnar", "name": "Munnar Highland Ridge", "category": "Mountain Town", "lat": 10.0889, "lon": 77.0595, "pop": 32000, "area_sqkm": 30.0, "annual_rain": 2750.0, "monsoon_rain": 1900.0, "extreme_rain": 250.0, "flood_hist": 2, "congestion": 1, "river_basin": "Muthirapuzha", "riv_lat": 10.0850, "riv_lon": 77.0650},

    # --- ODISHA (Mahanadi, Brahmani & Baitarani Deltas) ---
    {"state": "Odisha", "district": "Kendrapara", "mandal": "Marsaghai", "name": "Marsaghai (Mahanadi Delta)", "category": "Town Node", "lat": 20.4400, "lon": 86.4500, "pop": 31000, "area_sqkm": 14.0, "annual_rain": 1560.0, "monsoon_rain": 1180.0, "extreme_rain": 295.0, "flood_hist": 5, "congestion": 5, "river_basin": "Mahanadi", "riv_lat": 20.4350, "riv_lon": 86.4400},
    {"state": "Odisha", "district": "Cuttack", "mandal": "Cuttack Sadar", "name": "Cuttack (Kathajodi Island)", "category": "City", "lat": 20.4625, "lon": 85.8830, "pop": 650000, "area_sqkm": 48.0, "annual_rain": 1450.0, "monsoon_rain": 1120.0, "extreme_rain": 265.0, "flood_hist": 4, "congestion": 4, "river_basin": "Mahanadi", "riv_lat": 20.4700, "riv_lon": 85.8900},
    {"state": "Odisha", "district": "Puri", "mandal": "Kanas", "name": "Kanas (Daya-Bhargavi Reach)", "category": "Village Node", "lat": 19.9800, "lon": 85.6500, "pop": 22000, "area_sqkm": 12.0, "annual_rain": 1510.0, "monsoon_rain": 1140.0, "extreme_rain": 280.0, "flood_hist": 5, "congestion": 5, "river_basin": "Daya", "riv_lat": 19.9850, "riv_lon": 85.6400},
    {"state": "Odisha", "district": "Jagatsinghpur", "mandal": "Kujang", "name": "Kujang Estuarine Plain", "category": "Town", "lat": 20.3100, "lon": 86.5300, "pop": 38000, "area_sqkm": 16.5, "annual_rain": 1580.0, "monsoon_rain": 1210.0, "extreme_rain": 310.0, "flood_hist": 5, "congestion": 5, "river_basin": "Mahanadi Delta", "riv_lat": 20.3050, "riv_lon": 86.5200},
    {"state": "Odisha", "district": "Balasore", "mandal": "Jaleswar", "name": "Jaleswar (Subarnarekha)", "category": "Town", "lat": 21.8100, "lon": 87.2100, "pop": 41000, "area_sqkm": 15.0, "annual_rain": 1620.0, "monsoon_rain": 1240.0, "extreme_rain": 285.0, "flood_hist": 4, "congestion": 4, "river_basin": "Subarnarekha", "riv_lat": 21.8200, "riv_lon": 87.2000},
    {"state": "Odisha", "district": "Sambalpur", "mandal": "Sambalpur", "name": "Sambalpur (Hirakud Foothills)", "category": "City", "lat": 21.4669, "lon": 83.9756, "pop": 270000, "area_sqkm": 36.0, "annual_rain": 1410.0, "monsoon_rain": 1180.0, "extreme_rain": 210.0, "flood_hist": 2, "congestion": 2, "river_basin": "Mahanadi Upper", "riv_lat": 21.4800, "riv_lon": 83.9600},

    # --- WEST BENGAL (Ganga-Bhagirathi, Damodar & Teesta Basins) ---
    {"state": "West Bengal", "district": "Kolkata", "mandal": "Kolkata Urban", "name": "Kolkata (Beliaghata / Tiljala)", "category": "Mega City", "lat": 22.5400, "lon": 88.3800, "pop": 1200000, "area_sqkm": 35.0, "annual_rain": 1680.0, "monsoon_rain": 1250.0, "extreme_rain": 285.0, "flood_hist": 4, "congestion": 5, "river_basin": "Hooghly Delta", "riv_lat": 22.5500, "riv_lon": 88.3400},
    {"state": "West Bengal", "district": "Paschim Medinipur", "mandal": "Ghatal", "name": "Ghatal (Silabati Stagnation Basin)", "category": "Town", "lat": 22.6700, "lon": 87.7200, "pop": 58000, "area_sqkm": 14.5, "annual_rain": 1540.0, "monsoon_rain": 1160.0, "extreme_rain": 260.0, "flood_hist": 5, "congestion": 5, "river_basin": "Silabati", "riv_lat": 22.6750, "riv_lon": 87.7150},
    {"state": "West Bengal", "district": "South 24 Parganas", "mandal": "Gosaba", "name": "Gosaba (Sundarbans Estuary)", "category": "Delta Island", "lat": 22.1650, "lon": 88.8050, "pop": 42000, "area_sqkm": 28.0, "annual_rain": 1820.0, "monsoon_rain": 1390.0, "extreme_rain": 315.0, "flood_hist": 5, "congestion": 5, "river_basin": "Matla-Bidyadhari", "riv_lat": 22.1600, "riv_lon": 88.8100},
    {"state": "West Bengal", "district": "Malda", "mandal": "Manikchak", "name": "Manikchak (Ganga Erosion Bank)", "category": "Village Node", "lat": 25.0800, "lon": 87.9100, "pop": 29000, "area_sqkm": 16.0, "annual_rain": 1380.0, "monsoon_rain": 1080.0, "extreme_rain": 220.0, "flood_hist": 5, "congestion": 4, "river_basin": "Ganga", "riv_lat": 25.0750, "riv_lon": 87.9000},
    {"state": "West Bengal", "district": "Jalpaiguri", "mandal": "Jalpaiguri", "name": "Jalpaiguri (Teesta Flood Fringe)", "category": "Town", "lat": 26.5400, "lon": 88.7100, "pop": 108000, "area_sqkm": 18.0, "annual_rain": 3100.0, "monsoon_rain": 2400.0, "extreme_rain": 320.0, "flood_hist": 4, "congestion": 4, "river_basin": "Teesta", "riv_lat": 26.5500, "riv_lon": 88.7200},
    {"state": "West Bengal", "district": "Purulia", "mandal": "Purulia", "name": "Purulia Upland Ridge", "category": "Town", "lat": 23.3300, "lon": 86.3600, "pop": 121000, "area_sqkm": 24.0, "annual_rain": 1220.0, "monsoon_rain": 980.0, "extreme_rain": 170.0, "flood_hist": 1, "congestion": 1, "river_basin": "Kangsabati", "riv_lat": 23.3200, "riv_lon": 86.3800},

    # --- MAHARASHTRA (Konkan Coastal, Krishna-Panchaganga & Mithi Basins) ---
    {"state": "Maharashtra", "district": "Mumbai Suburban", "mandal": "Kurla", "name": "Kurla / Kalina (Mithi River Corridor)", "category": "Metro Locality", "lat": 19.0650, "lon": 72.8850, "pop": 920000, "area_sqkm": 28.0, "annual_rain": 2450.0, "monsoon_rain": 2200.0, "extreme_rain": 380.0, "flood_hist": 5, "congestion": 5, "river_basin": "Mithi", "riv_lat": 19.0680, "riv_lon": 72.8750},
    {"state": "Maharashtra", "district": "Ratnagiri", "mandal": "Chiplun", "name": "Chiplun (Vashishti River Basin)", "category": "Town", "lat": 17.5320, "lon": 73.5180, "pop": 55000, "area_sqkm": 14.0, "annual_rain": 3350.0, "monsoon_rain": 3050.0, "extreme_rain": 420.0, "flood_hist": 5, "congestion": 5, "river_basin": "Vashishti", "riv_lat": 17.5350, "riv_lon": 73.5120},
    {"state": "Maharashtra", "district": "Kolhapur", "mandal": "Karveer", "name": "Kolhapur (Panchaganga Basin)", "category": "City", "lat": 16.7050, "lon": 74.2433, "pop": 550000, "area_sqkm": 45.0, "annual_rain": 1850.0, "monsoon_rain": 1650.0, "extreme_rain": 260.0, "flood_hist": 5, "congestion": 4, "river_basin": "Panchaganga", "riv_lat": 16.7150, "riv_lon": 74.2350},
    {"state": "Maharashtra", "district": "Sangli", "mandal": "Miraj", "name": "Sangli-Miraj (Krishna Floodplain)", "category": "City", "lat": 16.8524, "lon": 74.5815, "pop": 440000, "area_sqkm": 40.0, "annual_rain": 950.0, "monsoon_rain": 780.0, "extreme_rain": 190.0, "flood_hist": 4, "congestion": 4, "river_basin": "Krishna", "riv_lat": 16.8500, "riv_lon": 74.5650},
    {"state": "Maharashtra", "district": "Raigad", "mandal": "Mahad", "name": "Mahad (Savitri Riverfront)", "category": "Town", "lat": 18.0830, "lon": 73.4170, "pop": 32000, "area_sqkm": 11.0, "annual_rain": 3650.0, "monsoon_rain": 3350.0, "extreme_rain": 440.0, "flood_hist": 5, "congestion": 5, "river_basin": "Savitri", "riv_lat": 18.0850, "riv_lon": 73.4120},
    {"state": "Maharashtra", "district": "Aurangabad", "mandal": "Chhatrapati Sambhajinagar", "name": "Chhatrapati Sambhajinagar Plateau", "category": "City", "lat": 19.8762, "lon": 75.3433, "pop": 890000, "area_sqkm": 75.0, "annual_rain": 720.0, "monsoon_rain": 610.0, "extreme_rain": 140.0, "flood_hist": 1, "congestion": 1, "river_basin": "Kham", "riv_lat": 19.8650, "riv_lon": 75.3350},

    # --- GUJARAT (Tapi, Narmada & Vishwamitri Basins) ---
    {"state": "Gujarat", "district": "Surat", "mandal": "Surat City", "name": "Surat (Adajan / Rander / Tapi Basin)", "category": "Mega City", "lat": 21.1950, "lon": 72.8100, "pop": 1600000, "area_sqkm": 60.0, "annual_rain": 1280.0, "monsoon_rain": 1190.0, "extreme_rain": 310.0, "flood_hist": 5, "congestion": 5, "river_basin": "Tapi", "riv_lat": 21.2050, "riv_lon": 72.8150},
    {"state": "Gujarat", "district": "Vadodara", "mandal": "Vadodara Urban", "name": "Vadodara (Vishwamitri Basin)", "category": "City", "lat": 22.3072, "lon": 73.1812, "pop": 980000, "area_sqkm": 55.0, "annual_rain": 980.0, "monsoon_rain": 910.0, "extreme_rain": 260.0, "flood_hist": 4, "congestion": 4, "river_basin": "Vishwamitri", "riv_lat": 22.3100, "riv_lon": 73.1900},
    {"state": "Gujarat", "district": "Bharuch", "mandal": "Bharuch", "name": "Bharuch (Narmada Estuary)", "category": "Town", "lat": 21.7051, "lon": 72.9959, "pop": 168000, "area_sqkm": 24.0, "annual_rain": 890.0, "monsoon_rain": 830.0, "extreme_rain": 220.0, "flood_hist": 4, "congestion": 4, "river_basin": "Narmada", "riv_lat": 21.6980, "riv_lon": 72.9850},
    {"state": "Gujarat", "district": "Kutch", "mandal": "Bhuj", "name": "Bhuj Arid Upland", "category": "Town", "lat": 23.2420, "lon": 69.6669, "pop": 145000, "area_sqkm": 32.0, "annual_rain": 380.0, "monsoon_rain": 340.0, "extreme_rain": 115.0, "flood_hist": 1, "congestion": 1, "river_basin": "Khari", "riv_lat": 23.2300, "riv_lon": 69.6500},

    # --- UTTAR PRADESH (Ganga, Yamuna, Ghaghra & Rapti Basins) ---
    {"state": "Uttar Pradesh", "district": "Gorakhpur", "mandal": "Gorakhpur Sadar", "name": "Gorakhpur (Rapti-Rohini Lowlands)", "category": "City", "lat": 26.7606, "lon": 83.3732, "pop": 710000, "area_sqkm": 52.0, "annual_rain": 1320.0, "monsoon_rain": 1150.0, "extreme_rain": 240.0, "flood_hist": 5, "congestion": 5, "river_basin": "Rapti", "riv_lat": 26.7550, "riv_lon": 83.3550},
    {"state": "Uttar Pradesh", "district": "Varanasi", "mandal": "Varanasi", "name": "Varanasi (Assi-Varuna Ghats)", "category": "City", "lat": 25.3176, "lon": 82.9739, "pop": 820000, "area_sqkm": 50.0, "annual_rain": 1050.0, "monsoon_rain": 910.0, "extreme_rain": 195.0, "flood_hist": 4, "congestion": 4, "river_basin": "Ganga", "riv_lat": 25.3120, "riv_lon": 83.0100},
    {"state": "Uttar Pradesh", "district": "Prayagraj", "mandal": "Prayagraj", "name": "Prayagraj (Sangam Lowland)", "category": "City", "lat": 25.4358, "lon": 81.8463, "pop": 860000, "area_sqkm": 58.0, "annual_rain": 1020.0, "monsoon_rain": 880.0, "extreme_rain": 190.0, "flood_hist": 4, "congestion": 4, "river_basin": "Ganga-Yamuna", "riv_lat": 25.4280, "riv_lon": 81.8850},
    {"state": "Uttar Pradesh", "district": "Ayodhya", "mandal": "Ayodhya", "name": "Ayodhya (Saryu Flood Corridor)", "category": "City", "lat": 26.7922, "lon": 82.1998, "pop": 250000, "area_sqkm": 30.0, "annual_rain": 1180.0, "monsoon_rain": 1020.0, "extreme_rain": 210.0, "flood_hist": 4, "congestion": 4, "river_basin": "Saryu", "riv_lat": 26.8020, "riv_lon": 82.2050},
    {"state": "Uttar Pradesh", "district": "Jhansi", "mandal": "Jhansi", "name": "Jhansi Bundelkhand Ridge", "category": "City", "lat": 25.4484, "lon": 78.5685, "pop": 510000, "area_sqkm": 44.0, "annual_rain": 850.0, "monsoon_rain": 760.0, "extreme_rain": 150.0, "flood_hist": 1, "congestion": 1, "river_basin": "Pahuj", "riv_lat": 25.4350, "riv_lon": 78.5400},

    # --- TAMIL NADU (Cauvery Delta & Adyar/Cooum Basins) ---
    {"state": "Tamil Nadu", "district": "Chennai", "mandal": "Velachery", "name": "Velachery / Pallikaranai Marsh", "category": "Metro Basin", "lat": 12.9800, "lon": 80.2200, "pop": 380000, "area_sqkm": 22.0, "annual_rain": 1420.0, "monsoon_rain": 850.0, "extreme_rain": 390.0, "flood_hist": 5, "congestion": 5, "river_basin": "Adyar", "riv_lat": 12.9900, "riv_lon": 79.2300},
    {"state": "Tamil Nadu", "district": "Cuddalore", "mandal": "Cuddalore", "name": "Cuddalore (Gadilam-Pennaiyar)", "category": "Town", "lat": 11.7500, "lon": 79.7600, "pop": 175000, "area_sqkm": 27.0, "annual_rain": 1390.0, "monsoon_rain": 910.0, "extreme_rain": 340.0, "flood_hist": 5, "congestion": 5, "river_basin": "Pennaiyar", "riv_lat": 11.7550, "riv_lon": 79.7650},
    {"state": "Tamil Nadu", "district": "Nagapattinam", "mandal": "Nagapattinam", "name": "Nagapattinam Delta Fringe", "category": "Coastal Town", "lat": 10.7600, "lon": 79.8400, "pop": 102000, "area_sqkm": 18.0, "annual_rain": 1350.0, "monsoon_rain": 890.0, "extreme_rain": 320.0, "flood_hist": 4, "congestion": 4, "river_basin": "Cauvery Delta", "riv_lat": 10.7650, "riv_lon": 79.8450},
    {"state": "Tamil Nadu", "district": "Thoothukudi", "mandal": "Thoothukudi", "name": "Thoothukudi (Thamirabarani Basin)", "category": "City", "lat": 8.7642, "lon": 78.1348, "pop": 410000, "area_sqkm": 38.0, "annual_rain": 710.0, "monsoon_rain": 420.0, "extreme_rain": 370.0, "flood_hist": 4, "congestion": 4, "river_basin": "Thamirabarani", "riv_lat": 8.7550, "riv_lon": 78.1400},
    {"state": "Tamil Nadu", "district": "Coimbatore", "mandal": "Coimbatore", "name": "Coimbatore Plateau", "category": "City", "lat": 11.0168, "lon": 76.9558, "pop": 950000, "area_sqkm": 68.0, "annual_rain": 680.0, "monsoon_rain": 390.0, "extreme_rain": 130.0, "flood_hist": 1, "congestion": 1, "river_basin": "Noyyal", "riv_lat": 11.0050, "riv_lon": 76.9400},

    # --- KARNATAKA (Krishna, Tungabhadra & Coastal Basins) ---
    {"state": "Karnataka", "district": "Belagavi", "mandal": "Chikkodi", "name": "Chikkodi (Krishna Flood Reach)", "category": "Town", "lat": 16.4300, "lon": 74.5900, "pop": 38000, "area_sqkm": 12.0, "annual_rain": 880.0, "monsoon_rain": 720.0, "extreme_rain": 210.0, "flood_hist": 5, "congestion": 4, "river_basin": "Krishna", "riv_lat": 16.4400, "riv_lon": 74.5800},
    {"state": "Karnataka", "district": "Bagalkot", "mandal": "Jamkhandi", "name": "Jamkhandi (Ghataprabha Reach)", "category": "Town", "lat": 16.5100, "lon": 75.3000, "pop": 68000, "area_sqkm": 17.5, "annual_rain": 650.0, "monsoon_rain": 510.0, "extreme_rain": 180.0, "flood_hist": 4, "congestion": 4, "river_basin": "Ghataprabha", "riv_lat": 16.5200, "riv_lon": 75.2900},
    {"state": "Karnataka", "district": "Dakshina Kannada", "mandal": "Mangaluru", "name": "Mangaluru (Netravati Basin)", "category": "City", "lat": 12.9141, "lon": 74.8560, "pop": 490000, "area_sqkm": 42.0, "annual_rain": 3850.0, "monsoon_rain": 3300.0, "extreme_rain": 360.0, "flood_hist": 4, "congestion": 4, "river_basin": "Netravati", "riv_lat": 12.8700, "riv_lon": 74.8500},
    {"state": "Karnataka", "district": "Bengaluru Urban", "mandal": "Bengaluru", "name": "Bengaluru Ridge Plateau", "category": "Metro City", "lat": 12.9716, "lon": 77.5946, "pop": 1800000, "area_sqkm": 110.0, "annual_rain": 920.0, "monsoon_rain": 680.0, "extreme_rain": 165.0, "flood_hist": 2, "congestion": 2, "river_basin": "Vrishabhavathi", "riv_lat": 12.9600, "riv_lon": 77.5700},

    # --- DELHI (National Capital Territory - Yamuna Basin) ---
    {"state": "Delhi", "district": "North East Delhi", "mandal": "Yamuna Vihar", "name": "Yamuna Bazar / Kashmiri Gate Lowland", "category": "Metro Locality", "lat": 28.6650, "lon": 77.2350, "pop": 240000, "area_sqkm": 11.0, "annual_rain": 780.0, "monsoon_rain": 650.0, "extreme_rain": 190.0, "flood_hist": 4, "congestion": 4, "river_basin": "Yamuna", "riv_lat": 28.6700, "riv_lon": 77.2400},
    {"state": "Delhi", "district": "East Delhi", "mandal": "Mayur Vihar", "name": "Mayur Vihar Yamuna Khadar", "category": "Metro Locality", "lat": 28.6050, "lon": 77.2950, "pop": 310000, "area_sqkm": 14.0, "annual_rain": 780.0, "monsoon_rain": 650.0, "extreme_rain": 190.0, "flood_hist": 4, "congestion": 4, "river_basin": "Yamuna", "riv_lat": 28.6000, "riv_lon": 77.2800},
    {"state": "Delhi", "district": "New Delhi", "mandal": "Chanakyapuri", "name": "Chanakyapuri Ridge", "category": "Urban Ridge", "lat": 28.5980, "lon": 77.1850, "pop": 85000, "area_sqkm": 18.0, "annual_rain": 760.0, "monsoon_rain": 630.0, "extreme_rain": 140.0, "flood_hist": 1, "congestion": 1, "river_basin": "Ridge", "riv_lat": 28.6100, "riv_lon": 77.2400},

    # --- PUNJAB / HARYANA (Indo-Gangetic - Sutlej & Ghaggar) ---
    {"state": "Punjab", "district": "Rupnagar", "mandal": "Anandpur Sahib", "name": "Rupnagar (Sutlej Floodplain)", "category": "Town", "lat": 30.9650, "lon": 76.5300, "pop": 56000, "area_sqkm": 15.0, "annual_rain": 940.0, "monsoon_rain": 780.0, "extreme_rain": 220.0, "flood_hist": 4, "congestion": 4, "river_basin": "Sutlej", "riv_lat": 30.9700, "riv_lon": 76.5200},
    {"state": "Punjab", "district": "Patiala", "mandal": "Samana", "name": "Samana (Ghaggar Overflow Basin)", "category": "Town", "lat": 30.1500, "lon": 76.1900, "pop": 54000, "area_sqkm": 14.0, "annual_rain": 680.0, "monsoon_rain": 550.0, "extreme_rain": 185.0, "flood_hist": 4, "congestion": 4, "river_basin": "Ghaggar", "riv_lat": 30.1400, "riv_lon": 76.1800},
    {"state": "Punjab", "district": "Bathinda", "mandal": "Bathinda", "name": "Bathinda Semiarid Plain", "category": "City", "lat": 30.2110, "lon": 74.9455, "pop": 285000, "area_sqkm": 35.0, "annual_rain": 420.0, "monsoon_rain": 340.0, "extreme_rain": 110.0, "flood_hist": 1, "congestion": 1, "river_basin": "Sirhind", "riv_lat": 30.2200, "riv_lon": 74.9600},

    # --- UTTARAKHAND & HIMACHAL PRADESH (Himalayan Cloudburst Basins) ---
    {"state": "Uttarakhand", "district": "Haridwar", "mandal": "Haridwar", "name": "Haridwar (Ganga Chandi Ghat)", "category": "Pilgrim Town", "lat": 29.9457, "lon": 78.1642, "pop": 230000, "area_sqkm": 25.0, "annual_rain": 1620.0, "monsoon_rain": 1340.0, "extreme_rain": 275.0, "flood_hist": 4, "congestion": 3, "river_basin": "Ganga Upper", "riv_lat": 29.9400, "riv_lon": 78.1700},
    {"state": "Himachal Pradesh", "district": "Kullu", "mandal": "Kullu", "name": "Kullu (Beas River Gorge)", "category": "Valley Town", "lat": 31.9579, "lon": 77.1095, "pop": 26000, "area_sqkm": 12.0, "annual_rain": 1450.0, "monsoon_rain": 1050.0, "extreme_rain": 290.0, "flood_hist": 4, "congestion": 3, "river_basin": "Beas", "riv_lat": 31.9600, "riv_lon": 77.1050}
]

df_other = pd.DataFrame(pan_india_habitations)
print(f"Defined {len(df_other)} habitations across {df_other['state'].nunique()} Indian States/UTs.")

# Fetch elevations for other states via Open-Meteo
print("Fetching real elevations via Open-Meteo API for other states...")
elevs_other = get_elevation_batch(df_other['lat'].tolist(), df_other['lon'].tolist())
df_other['elevation_m'] = elevs_other

# Compute river distance & slope for other states
df_other['distance_to_river_km'] = [
    round(haversine_km(lat, lon, rlat, rlon), 2)
    for lat, lon, rlat, rlon in zip(df_other['lat'], df_other['lon'], df_other['riv_lat'], df_other['riv_lon'])
]

df_other['slope_deg'] = np.clip(
    np.round(0.2 + (df_other['elevation_m'] - 5.0) * 0.04 + df_other['distance_to_river_km'] * 0.06, 2),
    0.2, 9.0
)

# Standardize columns to match AP dataset
df_other['habitation_id'] = [f"IND_{i+1:03d}" for i in range(len(df_other))]
df_other['habitation_name'] = df_other['name']
df_other['place_category'] = df_other['category']
df_other['latitude'] = df_other['lat']
df_other['longitude'] = df_other['lon']
df_other['population'] = df_other['pop']
df_other['annual_rainfall_mm'] = df_other['annual_rain']
df_other['monsoon_rainfall_mm'] = df_other['monsoon_rain']
df_other['extreme_daily_rainfall_mm'] = df_other['extreme_rain']
df_other['drainage_congestion_index'] = df_other['congestion']
df_other['historical_flood_inundation_frequency'] = df_other['flood_hist']
df_other['population_density_per_sqkm'] = (df_other['population'] / df_other['area_sqkm']).round(1)

# Ensure common columns
common_cols = [
    'habitation_id', 'habitation_name', 'state', 'district', 'mandal', 'place_category',
    'latitude', 'longitude', 'elevation_m', 'slope_deg', 'distance_to_river_km',
    'annual_rainfall_mm', 'monsoon_rainfall_mm', 'extreme_daily_rainfall_mm',
    'population', 'area_sqkm', 'population_density_per_sqkm',
    'drainage_congestion_index', 'historical_flood_inundation_frequency', 'river_basin'
]

df_combined = pd.concat([df_ap[common_cols], df_other[common_cols]], ignore_index=True)
print(f"Total Unified Pan-India Dataset: {len(df_combined)} habitations across {df_combined['state'].nunique()} States.")
print("State counts:\n", df_combined['state'].value_counts())

# Machine Learning: Clustering the Entire India Dataset
clustering_features = [
    'elevation_m',
    'slope_deg',
    'distance_to_river_km',
    'annual_rainfall_mm',
    'monsoon_rainfall_mm',
    'extreme_daily_rainfall_mm',
    'population_density_per_sqkm',
    'drainage_congestion_index',
    'historical_flood_inundation_frequency'
]

scaler = StandardScaler()
X_all = scaler.fit_transform(df_combined[clustering_features])

# K-Means++ Clustering (K=3)
km = KMeans(n_clusters=3, init='k-means++', n_init=30, random_state=42)
raw_km_labels = km.fit_predict(X_all)

# Sort clusters by relative hazard
df_combined['raw_cluster'] = raw_km_labels
hazard_score = df_combined.groupby('raw_cluster').apply(
    lambda g: g['historical_flood_inundation_frequency'].mean() + g['drainage_congestion_index'].mean() - (g['elevation_m'].mean() / 25.0)
).to_dict()

sorted_c = sorted(hazard_score.keys(), key=lambda c: hazard_score[c], reverse=True)
tier_map = {
    sorted_c[0]: "High Relative Hazard / Vulnerability",
    sorted_c[1]: "Moderate Relative Hazard / Vulnerability",
    sorted_c[2]: "Relatively Lower Hazard / Vulnerability"
}
tier_code_map = {sorted_c[0]: 1, sorted_c[1]: 2, sorted_c[2]: 3}

df_combined['cluster_k3'] = df_combined['raw_cluster'].map(tier_code_map)
df_combined['relative_hazard_level'] = df_combined['raw_cluster'].map(tier_map)

# PCA Dimensionality Reduction
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_all)
df_combined['pca_1'] = np.round(X_pca[:, 0], 4)
df_combined['pca_2'] = np.round(X_pca[:, 1], 4)

print(f"PCA PC1 Var: {pca.explained_variance_ratio_[0]*100:.2f}%, PC2 Var: {pca.explained_variance_ratio_[1]*100:.2f}%")

# Save Unified Pan-India Dataset
output_path = "data/processed/india_habitations_complete.csv"
df_combined.to_csv(output_path, index=False)
print(f"Saved complete Pan-India dataset to {output_path}!")
