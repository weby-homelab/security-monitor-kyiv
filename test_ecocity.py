import requests
import json

def test():
    # Attempting to use a public proxy for EcoCity or their direct API
    url = "https://api.eco-city.org.ua/public.json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # The structure is usually a list of stations
            for station in data:
                if station.get('id') == 16560:
                    print(json.dumps(station, indent=2, ensure_ascii=False))
                    return
            print("Station 16560 not found in list")
        else:
            print(f"Error: Status {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
