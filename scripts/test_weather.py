import requests

places = [
    ('Ajit Singh Nagar, NTR (Vijayawada)', 16.5360, 80.6380),
    ('Amalapuram Delta, Konaseema', 16.5787, 82.0061),
    ('Kurnool City (Tungabhadra)', 15.8281, 78.0373),
    ('Visakhapatnam Coast', 17.7231, 83.3013)
]

for name, lat, lon in places:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat:.4f}&longitude={lon:.4f}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,surface_pressure,wind_speed_10m&past_days=1&hourly=precipitation&timezone=Asia%2FKolkata"
    r = requests.get(url, timeout=5)
    d = r.json()
    cur = d.get('current', {})
    hourly = d.get('hourly', {}).get('precipitation', [])
    past24 = sum(hourly[-24:]) if len(hourly) >= 24 else 0.0
    print(f"{name}: Temp={cur.get('temperature_2m')}C, Humidity={cur.get('relative_humidity_2m')}%, Rain={cur.get('rain')}mm/h, Past24h={past24}mm, Code={cur.get('weather_code')}")
