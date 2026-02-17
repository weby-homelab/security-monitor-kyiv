import requests
from bs4 import BeautifulSoup

STATION_URL = "https://www.saveecobot.com/stations/1592"  # Station in Sviatoshynskyi district (Korolyova St)

def debug_rad():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(STATION_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Find all sensor names
        names = soup.find_all('div', class_='row-item')
        print(f"Found {len(names)} row items.")
        
        for row in names:
            name_el = row.find('span', class_='row-name')
            val_el = row.find('span', class_='value')
            if name_el and val_el:
                print(f"Sensor: {name_el.text.strip()} -> Value: {val_el.text.strip()}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_rad()
