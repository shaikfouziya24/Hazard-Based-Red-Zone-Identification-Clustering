import requests
import json

url = "https://zenodo.org/api/records/16994648"
try:
    r = requests.get(url, timeout=15)
    print("Zenodo status code:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print("Title:", data.get("metadata", {}).get("title"))
        print("Publication date:", data.get("metadata", {}).get("publication_date"))
        files = data.get("files", [])
        print(f"Total files: {len(files)}")
        for f in files:
            print("File:", f.get("key"), f.get("size"), "bytes", f.get("links", {}).get("self"))
except Exception as e:
    print("Error:", e)
