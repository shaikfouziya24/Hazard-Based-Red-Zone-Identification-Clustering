import requests
import json
import pandas as pd

query = """[out:json][timeout:35];
node["place"~"city|town|village|suburb|hamlet"](15.75,80.0,16.75,81.25);
out body;
"""

endpoints = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

success = False
for ep in endpoints:
    print(f"Trying endpoint: {ep}...")
    try:
        r = requests.post(ep, data={"data": query}, headers={"User-Agent": "BTechProjectDataCollector/1.0"}, timeout=30)
        print("Status code:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            elements = data.get("elements", [])
            print(f"Retrieved {len(elements)} elements from {ep}!")
            rows = []
            for el in elements:
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("name:en")
                if not name:
                    continue
                rows.append({
                    "osm_id": el.get("id"),
                    "name": name,
                    "name_en": tags.get("name:en", name),
                    "place_type": tags.get("place"),
                    "latitude": el.get("lat"),
                    "longitude": el.get("lon"),
                    "population": tags.get("population")
                })
            df = pd.DataFrame(rows)
            df.to_csv("data/raw/osm_settlements.csv", index=False)
            print(f"Saved {len(df)} settlements to data/raw/osm_settlements.csv")
            print(df.head(10))
            success = True
            break
        else:
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print("Exception:", e)

if not success:
    print("Could not query Overpass API directly. Checking alternative sources...")
