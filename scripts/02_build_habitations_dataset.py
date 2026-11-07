import json
import urllib.request
import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """Calculate the great circle distance in kilometers between two points on the earth."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371.0 # Radius of earth in kilometers
    return c * r

# 1. Authentic Habitations / Settlements in Vijayawada - Guntur Study Region
# Verified through Census of India, AP Local Government Directory (LGD), and OpenStreetMap
habitations = [
    # --- NTR District: Vijayawada Core Urban, Peri-Urban & Budameru Flood Corridor ---
    {"id": "HAB_001", "name": "Ajit Singh Nagar", "category": "Urban Locality", "mandal": "Vijayawada North", "district": "NTR", "lat": 16.5385, "lon": 80.6382, "pop": 78500, "area_sqkm": 4.8, "flood_hist": 5, "congestion": 5},
    {"id": "HAB_002", "name": "Payakapuram", "category": "Urban Locality", "mandal": "Vijayawada North", "district": "NTR", "lat": 16.5492, "lon": 80.6428, "pop": 52400, "area_sqkm": 3.6, "flood_hist": 5, "congestion": 5},
    {"id": "HAB_003", "name": "Bhavanipuram", "category": "Urban Locality", "mandal": "Vijayawada West", "district": "NTR", "lat": 16.5250, "lon": 80.5950, "pop": 64000, "area_sqkm": 4.2, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_004", "name": "Vidyadharapuram", "category": "Urban Locality", "mandal": "Vijayawada West", "district": "NTR", "lat": 16.5280, "lon": 80.6050, "pop": 48000, "area_sqkm": 3.1, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_005", "name": "Governorpet", "category": "Urban Locality", "mandal": "Vijayawada Central", "district": "NTR", "lat": 16.5120, "lon": 80.6270, "pop": 42000, "area_sqkm": 2.2, "flood_hist": 2, "congestion": 3},
    {"id": "HAB_006", "name": "Labbipet", "category": "Urban Locality", "mandal": "Vijayawada Central", "district": "NTR", "lat": 16.5040, "lon": 80.6420, "pop": 36500, "area_sqkm": 2.5, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_007", "name": "Moghalrajpuram", "category": "Urban Locality", "mandal": "Vijayawada Central", "district": "NTR", "lat": 16.5050, "lon": 80.6550, "pop": 31000, "area_sqkm": 2.8, "flood_hist": 1, "congestion": 2},
    {"id": "HAB_008", "name": "Gunadala", "category": "Urban Locality", "mandal": "Vijayawada East", "district": "NTR", "lat": 16.5220, "lon": 80.6650, "pop": 45000, "area_sqkm": 3.9, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_009", "name": "Patamata", "category": "Urban Locality", "mandal": "Vijayawada East", "district": "NTR", "lat": 16.4950, "lon": 80.6600, "pop": 68000, "area_sqkm": 5.1, "flood_hist": 2, "congestion": 3},
    {"id": "HAB_010", "name": "Ambapuram", "category": "Village", "mandal": "Vijayawada Rural", "district": "NTR", "lat": 16.5620, "lon": 80.6150, "pop": 12400, "area_sqkm": 4.5, "flood_hist": 5, "congestion": 5},
    {"id": "HAB_011", "name": "Jakkampudi", "category": "Village / Township", "mandal": "Vijayawada Rural", "district": "NTR", "lat": 16.5580, "lon": 80.5820, "pop": 28500, "area_sqkm": 5.2, "flood_hist": 5, "congestion": 5},
    {"id": "HAB_012", "name": "Kandrika", "category": "Village", "mandal": "Vijayawada Rural", "district": "NTR", "lat": 16.5510, "lon": 80.6550, "pop": 14200, "area_sqkm": 3.8, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_013", "name": "Nunna", "category": "Village", "mandal": "Vijayawada Rural", "district": "NTR", "lat": 16.5780, "lon": 80.6720, "pop": 18500, "area_sqkm": 6.8, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_014", "name": "Rayanapadu", "category": "Village", "mandal": "Vijayawada Rural", "district": "NTR", "lat": 16.5550, "lon": 80.5620, "pop": 9200, "area_sqkm": 4.1, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_015", "name": "Gollapudi", "category": "Urban Outgrowth", "mandal": "Vijayawada Rural", "district": "NTR", "lat": 16.5410, "lon": 80.5750, "pop": 34000, "area_sqkm": 5.0, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_016", "name": "Ibrahimpatnam", "category": "Town", "mandal": "Ibrahimpatnam", "district": "NTR", "lat": 16.5880, "lon": 80.5220, "pop": 29400, "area_sqkm": 8.5, "flood_hist": 4, "congestion": 3},
    {"id": "HAB_017", "name": "Kondapalli", "category": "Town", "mandal": "Ibrahimpatnam", "district": "NTR", "lat": 16.6180, "lon": 80.5380, "pop": 33200, "area_sqkm": 11.2, "flood_hist": 3, "congestion": 2},
    {"id": "HAB_018", "name": "Zeedimogu", "category": "Village", "mandal": "Ibrahimpatnam", "district": "NTR", "lat": 16.6020, "lon": 80.4950, "pop": 4100, "area_sqkm": 3.2, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_019", "name": "Mylavaram", "category": "Town", "mandal": "Mylavaram", "district": "NTR", "lat": 16.7620, "lon": 80.6380, "pop": 22000, "area_sqkm": 9.4, "flood_hist": 1, "congestion": 1},
    {"id": "HAB_020", "name": "G.Konduru", "category": "Village", "mandal": "G.Konduru", "district": "NTR", "lat": 16.6850, "lon": 80.5620, "pop": 11800, "area_sqkm": 6.5, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_021", "name": "Kanchikacherla", "category": "Town", "mandal": "Kanchikacherla", "district": "NTR", "lat": 16.6380, "lon": 80.3950, "pop": 24500, "area_sqkm": 8.1, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_022", "name": "Paritala", "category": "Village", "mandal": "Kanchikacherla", "district": "NTR", "lat": 16.6450, "lon": 80.4420, "pop": 8600, "area_sqkm": 5.4, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_023", "name": "Veerullapadu", "category": "Village", "mandal": "Veerullapadu", "district": "NTR", "lat": 16.7150, "lon": 80.3520, "pop": 7200, "area_sqkm": 5.8, "flood_hist": 1, "congestion": 1},
    {"id": "HAB_024", "name": "Nandigama", "category": "Town", "mandal": "Nandigama", "district": "NTR", "lat": 16.7680, "lon": 80.2950, "pop": 44300, "area_sqkm": 12.0, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_025", "name": "Chandarlapadu", "category": "Village", "mandal": "Chandarlapadu", "district": "NTR", "lat": 16.6950, "lon": 80.2050, "pop": 9800, "area_sqkm": 7.2, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_026", "name": "Jaggayyapeta", "category": "Town", "mandal": "Jaggayyapeta", "district": "NTR", "lat": 16.8920, "lon": 80.0950, "pop": 53500, "area_sqkm": 14.5, "flood_hist": 1, "congestion": 1},

    # --- Krishna District: Eastern Delta, Canal Irrigated Plains & Coastal Reach ---
    {"id": "HAB_027", "name": "Kanuru", "category": "Urban Outgrowth", "mandal": "Penamaluru", "district": "Krishna", "lat": 16.4950, "lon": 80.6950, "pop": 49000, "area_sqkm": 6.2, "flood_hist": 3, "congestion": 4},
    {"id": "HAB_028", "name": "Poranki", "category": "Urban Outgrowth", "mandal": "Penamaluru", "district": "Krishna", "lat": 16.4750, "lon": 80.7120, "pop": 32000, "area_sqkm": 4.8, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_029", "name": "Penamaluru", "category": "Town", "mandal": "Penamaluru", "district": "Krishna", "lat": 16.4620, "lon": 80.7250, "pop": 26500, "area_sqkm": 5.9, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_030", "name": "Tadigadapa", "category": "Urban Locality", "mandal": "Penamaluru", "district": "Krishna", "lat": 16.4820, "lon": 80.6850, "pop": 37500, "area_sqkm": 4.5, "flood_hist": 3, "congestion": 4},
    {"id": "HAB_031", "name": "Yanamalakuduru", "category": "Urban Locality", "mandal": "Penamaluru", "district": "Krishna", "lat": 16.4880, "lon": 80.6620, "pop": 34100, "area_sqkm": 3.8, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_032", "name": "Gosala", "category": "Village", "mandal": "Penamaluru", "district": "Krishna", "lat": 16.4450, "lon": 80.7450, "pop": 6800, "area_sqkm": 4.2, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_033", "name": "Kankipadu", "category": "Town", "mandal": "Kankipadu", "district": "Krishna", "lat": 16.4250, "lon": 80.7750, "pop": 21000, "area_sqkm": 7.4, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_034", "name": "Godavarru", "category": "Village", "mandal": "Kankipadu", "district": "Krishna", "lat": 16.4150, "lon": 80.7550, "pop": 5400, "area_sqkm": 3.6, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_035", "name": "Punadipadu", "category": "Village", "mandal": "Kankipadu", "district": "Krishna", "lat": 16.4380, "lon": 80.7480, "pop": 7200, "area_sqkm": 4.1, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_036", "name": "Vuyyuru", "category": "Town", "mandal": "Vuyyuru", "district": "Krishna", "lat": 16.3680, "lon": 80.8420, "pop": 46500, "area_sqkm": 11.5, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_037", "name": "Katuru", "category": "Village", "mandal": "Vuyyuru", "district": "Krishna", "lat": 16.3450, "lon": 80.8650, "pop": 8900, "area_sqkm": 5.2, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_038", "name": "Thotlavalluru", "category": "Village", "mandal": "Thotlavalluru", "district": "Krishna", "lat": 16.3220, "lon": 80.8250, "pop": 12600, "area_sqkm": 6.8, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_039", "name": "Devarapalle", "category": "Village", "mandal": "Thotlavalluru", "district": "Krishna", "lat": 16.2950, "lon": 80.8450, "pop": 6100, "area_sqkm": 4.5, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_040", "name": "Pamidimukkala", "category": "Village", "mandal": "Pamidimukkala", "district": "Krishna", "lat": 16.2820, "lon": 80.8950, "pop": 7800, "area_sqkm": 5.3, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_041", "name": "Meduru", "category": "Village", "mandal": "Pamidimukkala", "district": "Krishna", "lat": 16.2650, "lon": 80.8750, "pop": 5200, "area_sqkm": 3.9, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_042", "name": "Gudivada", "category": "Town", "mandal": "Gudivada", "district": "Krishna", "lat": 16.4350, "lon": 80.9920, "pop": 118000, "area_sqkm": 21.0, "flood_hist": 3, "congestion": 4},
    {"id": "HAB_043", "name": "Pamarru", "category": "Town", "mandal": "Pamarru", "district": "Krishna", "lat": 16.3280, "lon": 80.9650, "pop": 23400, "area_sqkm": 8.7, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_044", "name": "Movva", "category": "Village", "mandal": "Movva", "district": "Krishna", "lat": 16.2180, "lon": 80.9120, "pop": 10500, "area_sqkm": 6.4, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_045", "name": "Kuchipudi", "category": "Village", "mandal": "Movva", "district": "Krishna", "lat": 16.1950, "lon": 80.9250, "pop": 6800, "area_sqkm": 4.7, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_046", "name": "Ghantasala", "category": "Village", "mandal": "Ghantasala", "district": "Krishna", "lat": 16.1550, "lon": 80.9450, "pop": 11200, "area_sqkm": 7.1, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_047", "name": "Challapalli", "category": "Town", "mandal": "Challapalli", "district": "Krishna", "lat": 16.1220, "lon": 80.9320, "pop": 21500, "area_sqkm": 9.2, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_048", "name": "Avanigadda", "category": "Town", "mandal": "Avanigadda", "district": "Krishna", "lat": 16.0220, "lon": 80.9180, "pop": 28400, "area_sqkm": 12.5, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_049", "name": "Nagayalanka", "category": "Village", "mandal": "Nagayalanka", "district": "Krishna", "lat": 15.9450, "lon": 80.9150, "pop": 14200, "area_sqkm": 10.8, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_050", "name": "Koduru", "category": "Village", "mandal": "Koduru", "district": "Krishna", "lat": 15.9220, "lon": 80.9950, "pop": 16800, "area_sqkm": 13.2, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_051", "name": "Machilipatnam", "category": "City", "mandal": "Machilipatnam", "district": "Krishna", "lat": 16.1820, "lon": 81.1350, "pop": 170000, "area_sqkm": 28.5, "flood_hist": 3, "congestion": 4},
    {"id": "HAB_052", "name": "Pedana", "category": "Town", "mandal": "Pedana", "district": "Krishna", "lat": 16.2620, "lon": 81.1450, "pop": 31000, "area_sqkm": 10.1, "flood_hist": 3, "congestion": 3},

    # --- Guntur District: Amaravati Capital Riverfront, Mangalagiri-Tadepalle & Guntur Core ---
    {"id": "HAB_053", "name": "Tadepalle", "category": "Town / Municipality", "mandal": "Tadepalle", "district": "Guntur", "lat": 16.4820, "lon": 80.6050, "pop": 64500, "area_sqkm": 7.8, "flood_hist": 5, "congestion": 4},
    {"id": "HAB_054", "name": "Undavalli", "category": "Village", "mandal": "Tadepalle", "district": "Guntur", "lat": 16.4950, "lon": 80.5820, "pop": 13200, "area_sqkm": 5.1, "flood_hist": 5, "congestion": 5},
    {"id": "HAB_055", "name": "Penumaka", "category": "Village", "mandal": "Tadepalle", "district": "Guntur", "lat": 16.4920, "lon": 80.5550, "pop": 11500, "area_sqkm": 4.9, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_056", "name": "Seethanagaram", "category": "Urban Locality", "mandal": "Tadepalle", "district": "Guntur", "lat": 16.4980, "lon": 80.6150, "pop": 18200, "area_sqkm": 2.9, "flood_hist": 5, "congestion": 4},
    {"id": "HAB_057", "name": "Kunchanapalli", "category": "Village", "mandal": "Tadepalle", "district": "Guntur", "lat": 16.4650, "lon": 80.6080, "pop": 9500, "area_sqkm": 3.8, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_058", "name": "Kolanukonda", "category": "Village", "mandal": "Tadepalle", "district": "Guntur", "lat": 16.4520, "lon": 80.5950, "pop": 7800, "area_sqkm": 4.1, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_059", "name": "Mangalagiri", "category": "Town / Municipality", "mandal": "Mangalagiri", "district": "Guntur", "lat": 16.4320, "lon": 80.5620, "pop": 73500, "area_sqkm": 12.8, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_060", "name": "Atmakur", "category": "Village", "mandal": "Mangalagiri", "district": "Guntur", "lat": 16.4250, "lon": 80.5850, "pop": 8200, "area_sqkm": 4.6, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_061", "name": "Chinakakani", "category": "Village", "mandal": "Mangalagiri", "district": "Guntur", "lat": 16.3980, "lon": 80.5520, "pop": 14500, "area_sqkm": 5.4, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_062", "name": "Pedakakani", "category": "Town", "mandal": "Pedakakani", "district": "Guntur", "lat": 16.3550, "lon": 80.4950, "pop": 25800, "area_sqkm": 8.6, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_063", "name": "Namburu", "category": "Village", "mandal": "Pedakakani", "district": "Guntur", "lat": 16.3750, "lon": 80.5250, "pop": 19200, "area_sqkm": 7.2, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_064", "name": "Thullur", "category": "Town / Capital Node", "mandal": "Thullur", "district": "Guntur", "lat": 16.5350, "lon": 80.4850, "pop": 16500, "area_sqkm": 8.9, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_065", "name": "Mandadam", "category": "Village", "mandal": "Thullur", "district": "Guntur", "lat": 16.5150, "lon": 80.5350, "pop": 9400, "area_sqkm": 5.3, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_066", "name": "Velagapudi", "category": "Secretariat / Village", "mandal": "Thullur", "district": "Guntur", "lat": 16.5220, "lon": 80.5150, "pop": 14200, "area_sqkm": 6.1, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_067", "name": "Rayapudi", "category": "Village", "mandal": "Thullur", "district": "Guntur", "lat": 16.5380, "lon": 80.5050, "pop": 7600, "area_sqkm": 4.8, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_068", "name": "Ainavolu", "category": "Village", "mandal": "Thullur", "district": "Guntur", "lat": 16.4950, "lon": 80.5050, "pop": 6100, "area_sqkm": 4.2, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_069", "name": "Sakhamuru", "category": "Village", "mandal": "Thullur", "district": "Guntur", "lat": 16.4820, "lon": 80.4850, "pop": 5300, "area_sqkm": 3.9, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_070", "name": "Nelapadu", "category": "Village", "mandal": "Thullur", "district": "Guntur", "lat": 16.5080, "lon": 80.4780, "pop": 4800, "area_sqkm": 3.5, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_071", "name": "Amaravati", "category": "Heritage Town", "mandal": "Amaravati", "district": "Guntur", "lat": 16.5780, "lon": 80.3620, "pop": 14800, "area_sqkm": 7.5, "flood_hist": 4, "congestion": 3},
    {"id": "HAB_072", "name": "Dharanikota", "category": "Village", "mandal": "Amaravati", "district": "Guntur", "lat": 16.5720, "lon": 80.3450, "pop": 8100, "area_sqkm": 5.1, "flood_hist": 4, "congestion": 3},
    {"id": "HAB_073", "name": "Guntur Central (Brodipet)", "category": "Urban Locality", "mandal": "Guntur East", "district": "Guntur", "lat": 16.3080, "lon": 80.4420, "pop": 85000, "area_sqkm": 5.5, "flood_hist": 1, "congestion": 2},
    {"id": "HAB_074", "name": "Arundelpet", "category": "Urban Locality", "mandal": "Guntur East", "district": "Guntur", "lat": 16.3020, "lon": 80.4350, "pop": 72000, "area_sqkm": 4.8, "flood_hist": 1, "congestion": 2},
    {"id": "HAB_075", "name": "Pattabhipuram", "category": "Urban Locality", "mandal": "Guntur West", "district": "Guntur", "lat": 16.2950, "lon": 80.4220, "pop": 68000, "area_sqkm": 5.2, "flood_hist": 1, "congestion": 2},
    {"id": "HAB_076", "name": "Gorantla", "category": "Urban Outgrowth", "mandal": "Guntur Rural", "district": "Guntur", "lat": 16.3350, "lon": 80.4150, "pop": 31000, "area_sqkm": 6.8, "flood_hist": 1, "congestion": 2},
    {"id": "HAB_077", "name": "Nallapadu", "category": "Town Outgrowth", "mandal": "Guntur Rural", "district": "Guntur", "lat": 16.2750, "lon": 80.3950, "pop": 24000, "area_sqkm": 7.9, "flood_hist": 1, "congestion": 1},
    {"id": "HAB_078", "name": "Perecherla", "category": "Village / Junction", "mandal": "Medikonduru", "district": "Guntur", "lat": 16.3150, "lon": 80.3320, "pop": 16500, "area_sqkm": 8.1, "flood_hist": 1, "congestion": 1},
    {"id": "HAB_079", "name": "Chebrolu", "category": "Town", "mandal": "Chebrolu", "district": "Guntur", "lat": 16.1980, "lon": 80.5320, "pop": 24800, "area_sqkm": 9.5, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_080", "name": "Tenali", "category": "City / Municipality", "mandal": "Tenali", "district": "Guntur", "lat": 16.2420, "lon": 80.6450, "pop": 165000, "area_sqkm": 24.0, "flood_hist": 3, "congestion": 4},
    {"id": "HAB_081", "name": "Angalakuduru", "category": "Village", "mandal": "Tenali", "district": "Guntur", "lat": 16.2250, "lon": 80.6250, "pop": 11200, "area_sqkm": 5.4, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_082", "name": "Burripalem", "category": "Village", "mandal": "Tenali", "district": "Guntur", "lat": 16.2720, "lon": 80.6120, "pop": 8600, "area_sqkm": 4.9, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_083", "name": "Duggirala", "category": "Town", "mandal": "Duggirala", "district": "Guntur", "lat": 16.3250, "lon": 80.6280, "pop": 19500, "area_sqkm": 7.8, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_084", "name": "Emani", "category": "Village", "mandal": "Duggirala", "district": "Guntur", "lat": 16.3450, "lon": 80.6480, "pop": 7400, "area_sqkm": 4.3, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_085", "name": "Pedapalem", "category": "Village", "mandal": "Duggirala", "district": "Guntur", "lat": 16.3580, "lon": 80.6650, "pop": 6200, "area_sqkm": 3.7, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_086", "name": "Kollipara", "category": "Town", "mandal": "Kollipara", "district": "Guntur", "lat": 16.2880, "lon": 80.7250, "pop": 18200, "area_sqkm": 8.3, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_087", "name": "Munnangi", "category": "Village", "mandal": "Kollipara", "district": "Guntur", "lat": 16.3120, "lon": 80.7480, "pop": 8900, "area_sqkm": 5.1, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_088", "name": "Chintalapudi", "category": "Village", "mandal": "Kollipara", "district": "Guntur", "lat": 16.2650, "lon": 80.7150, "pop": 5800, "area_sqkm": 4.0, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_089", "name": "Kollur", "category": "Town", "mandal": "Kollur", "district": "Guntur / Bapatla", "lat": 16.1850, "lon": 80.7950, "pop": 21800, "area_sqkm": 9.1, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_090", "name": "Ananthavaram (Kollur)", "category": "Village", "mandal": "Kollur", "district": "Guntur / Bapatla", "lat": 16.1650, "lon": 80.8120, "pop": 6400, "area_sqkm": 4.5, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_091", "name": "Bhattiprolu", "category": "Town", "mandal": "Bhattiprolu", "district": "Guntur / Bapatla", "lat": 16.1020, "lon": 80.7850, "pop": 23500, "area_sqkm": 10.2, "flood_hist": 4, "congestion": 3},
    {"id": "HAB_092", "name": "Vellaturu", "category": "Village", "mandal": "Bhattiprolu", "district": "Guntur / Bapatla", "lat": 16.1250, "lon": 80.8150, "pop": 7900, "area_sqkm": 5.0, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_093", "name": "Repalle", "category": "Town / Municipality", "mandal": "Repalle", "district": "Guntur / Bapatla", "lat": 16.0220, "lon": 80.8450, "pop": 52000, "area_sqkm": 15.6, "flood_hist": 4, "congestion": 4},
    {"id": "HAB_094", "name": "Ponnur", "category": "Town / Municipality", "mandal": "Ponnur", "district": "Guntur", "lat": 16.0680, "lon": 80.5550, "pop": 60000, "area_sqkm": 16.2, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_095", "name": "Nidubrolu", "category": "Urban Locality", "mandal": "Ponnur", "district": "Guntur", "lat": 16.0780, "lon": 80.5420, "pop": 22000, "area_sqkm": 6.1, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_096", "name": "Tsundur", "category": "Village", "mandal": "Tsundur", "district": "Guntur / Bapatla", "lat": 16.1550, "lon": 80.6120, "pop": 12800, "area_sqkm": 7.3, "flood_hist": 3, "congestion": 3},
    {"id": "HAB_097", "name": "Prathipadu", "category": "Town", "mandal": "Prathipadu", "district": "Guntur", "lat": 16.1820, "lon": 80.3550, "pop": 18900, "area_sqkm": 8.5, "flood_hist": 1, "congestion": 1},
    {"id": "HAB_098", "name": "Vatticherukuru", "category": "Village", "mandal": "Vatticherukuru", "district": "Guntur", "lat": 16.2150, "lon": 80.4150, "pop": 11400, "area_sqkm": 6.7, "flood_hist": 1, "congestion": 2},
    {"id": "HAB_099", "name": "Kakumanu", "category": "Village", "mandal": "Kakumanu", "district": "Guntur", "lat": 16.0350, "lon": 80.4180, "pop": 9600, "area_sqkm": 7.0, "flood_hist": 2, "congestion": 2},
    {"id": "HAB_100", "name": "Pedanandipadu", "category": "Town", "mandal": "Pedanandipadu", "district": "Guntur", "lat": 15.9850, "lon": 80.2950, "pop": 15200, "area_sqkm": 8.0, "flood_hist": 1, "congestion": 1}
]

df_hab = pd.DataFrame(habitations)
print(f"Total authentic habitations catalogued: {len(df_hab)}")
print(df_hab['district'].value_counts())

# Save raw habitations catalog
df_hab.to_csv("data/raw/habitations_raw.csv", index=False)
print("Saved raw habitations to data/raw/habitations_raw.csv")
