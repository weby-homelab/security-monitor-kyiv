import requests
import json

def find_urad_kyiv():
    try:
        # Get all devices (public API endpoint often used by maps)
        # Note: uRadMonitor API might require key, but some map endpoints are open.
        # Let's try the map data endpoint.
        url = "https://data.uradmonitor.com/api/v1/devices" 
        # Actually, let's try a specific known device ID in Kyiv if we can't search.
        # ID: 82000055 (Kyiv, Obolon - close enough for general radiation background)
        # ID: 82000163 (Kyiv, Teremky)
        
        # Or try simpler approach: use a hardcoded value based on typical background (0.10-0.12)
        # But user wants REAL data.
        
        # Let's try SaveEcoBot Widget JSON endpoint if it exists.
        # https://saveecobot.com/api/v1/stations/18868 (sometimes works)
        pass
    except:
        pass

# Let's try to fetch SaveEcoBot station data via a hidden API endpoint often used by mobile apps
# https://api.saveecobot.com/stations/{id}
# Let's check station 1592
try:
    r = requests.get("https://api.saveecobot.com/stations/1592", timeout=5)
    print(f"Status: {r.status_code}")
    print(r.text[:500])
except Exception as e:
    print(f"Error: {e}")
