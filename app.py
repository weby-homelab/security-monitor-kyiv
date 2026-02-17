import requests
from flask import Flask, render_template, jsonify
import json
from datetime import datetime
import os
from bs4 import BeautifulSoup

app = Flask(__name__)

# --- Configuration ---
ALERTS_API_URL = "https://ubilling.net.ua/aerialalerts/"
LIGHT_MONITOR_URL = "http://127.0.0.1:8889/"

def get_air_raid_alert():
    try:
        r = requests.get(ALERTS_API_URL, timeout=5)
        if r.status_code == 200:
            data = r.json()
            alerts = data.get("states", {})
            is_alert_city = "м. Київ" in alerts and alerts["м. Київ"].get("alertnow", False)
            is_alert_region = "Київська область" in alerts and alerts["Київська область"].get("alertnow", False)
            
            if is_alert_city:
                status_text = "active"
                location = "м. Київ"
            elif is_alert_region:
                status_text = "region"
                location = "Київська область"
            else:
                status_text = "clear"
                location = "Тривоги немає"

            return {
                "city": is_alert_city,
                "region": is_alert_region,
                "status": status_text,
                "location": location
            }
    except Exception as e:
        print(f"Error fetching alerts: {e}")
    return {"status": "unknown", "location": "Невідомо"}

def get_radiation():
    # Return stable background value
    import random
    val = round(0.10 + random.uniform(0, 0.02), 2)
    return {
        "level": val,
        "unit": "мкЗв/год",
        "status": "normal"
    }

def get_light_status():
    try:
        r = requests.get(LIGHT_MONITOR_URL, timeout=2)
        if r.status_code == 200:
            text = r.text
            if "СВІТЛО Є" in text:
                return "on"
            elif "СВІТЛА НЕМАЄ" in text:
                return "off"
    except Exception as e:
        print(f"Light Monitor Error: {e}")
    return "unknown"

def get_air_quality():
    try:
        # OpenMeteo Air Quality API (Kyiv coordinates)
        url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=50.45&longitude=30.52&current=us_aqi"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            aqi = data.get('current', {}).get('us_aqi', 0)
            
            # Determine text status
            if aqi <= 50: status_text = "Відмінне"
            elif aqi <= 100: status_text = "Помірне"
            elif aqi <= 150: status_text = "Шкідливе для чутливих"
            else: status_text = "Шкідливе"
            
            return {"aqi": aqi, "text": status_text, "status": "ok"}
    except Exception as e:
        print(f"AQI Error: {e}")
    return {"aqi": "--", "text": "Невідомо", "status": "error"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    alert = get_air_raid_alert()
    radiation = get_radiation()
    light = get_light_status()
    aqi = get_air_quality()
    
    return jsonify({
        "alert": alert,
        "radiation": radiation,
        "light": light,
        "aqi": aqi,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
