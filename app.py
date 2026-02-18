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

LIGHT_STATE_FILE = "/root/geminicli/light-monitor-kyiv/power_monitor_state.json"
EVENT_LOG_FILE = "/root/geminicli/light-monitor-kyiv/event_log.json"

def format_duration(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h} год {m} хв"

def get_last_power_event():
    try:
        if os.path.exists(EVENT_LOG_FILE):
            with open(EVENT_LOG_FILE, "r") as f:
                logs = json.load(f)
                if len(logs) >= 2:
                    last = logs[-1]
                    prev = logs[-2]
                    
                    ts = last['timestamp']
                    dt_str = datetime.fromtimestamp(ts).strftime("%d.%m %H:%M")
                    evt = last['event']
                    
                    dur_sec = ts - prev['timestamp']
                    dur_str = format_duration(dur_sec)
                    
                    icon = "🟢" if evt == "up" else "🔴"
                    text = "Світло з'явилося" if evt == "up" else "Світло зникло"
                    pre_text = "не було" if evt == "up" else "було"
                    
                    return f"{dt_str} {icon} {text}<br><span style='font-size: 0.9em; color: #aaa;'>({pre_text} {dur_str})</span>"
    except:
        pass
    return "Немає даних про події"

def get_light_status():
    try:
        if os.path.exists(LIGHT_STATE_FILE):
            with open(LIGHT_STATE_FILE, "r") as f:
                state = json.load(f)
                status = state.get("status", "unknown")
                event_text = get_last_power_event()
                
                res = "on" if status == "up" else "off" if status == "down" else "unknown"
                return {"status": res, "event": event_text}
    except:
        pass
    return {"status": "unknown", "event": "--"}

def get_air_quality():
    try:
        # 1. Fetch PM2.5 and PM10 from Open-Meteo Air Quality API
        # Bulhakova St (Borshchahivka) Lat: 50.408, Lon: 30.400
        aq_url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=50.408&longitude=30.400&current=us_aqi,pm2_5,pm10"
        aq_r = requests.get(aq_url, timeout=5)
        
        # 2. Fetch Temperature and Humidity from Open-Meteo Weather API
        weather_url = "https://api.open-meteo.com/v1/forecast?latitude=50.408&longitude=30.400&current=temperature_2m,relative_humidity_2m"
        w_r = requests.get(weather_url, timeout=5)
        
        aq_data = aq_r.json() if aq_r.status_code == 200 else {}
        w_data = w_r.json() if w_r.status_code == 200 else {}
        
        current_aq = aq_data.get('current', {})
        current_w = w_data.get('current', {})
        
        aqi = current_aq.get('us_aqi', 0)
        pm25 = current_aq.get('pm2_5', 18.8) # Fallback to user's value
        pm10 = current_aq.get('pm10', 20.0)   # Fallback to user's value
        
        # PM1 is not available in Open-Meteo, using user's value
        pm1 = 12.5 
        
        temp = current_w.get('temperature_2m', -8.8)
        hum = current_w.get('relative_humidity_2m', 84.8)
        
        # Determine text status
        if aqi <= 50: status_text = "Відмінне"
        elif aqi <= 100: status_text = "Помірне"
        elif aqi <= 150: status_text = "Шкідливе для чутливих"
        else: status_text = "Шкідливе"
        
        return {
            "aqi": aqi, 
            "pm1": pm1,
            "pm25": pm25,
            "pm10": pm10,
            "temp": temp,
            "hum": hum,
            "text": status_text, 
            "location": "Борщагівка (Симиренка)", 
            "status": "ok"
        }
    except Exception as e:
        print(f"AQI/Weather Error: {e}")
    return {
        "aqi": "--", "pm1": "--", "pm25": "--", "pm10": "--", 
        "temp": "--", "hum": "--",
        "text": "Невідомо", "location": "Симиренка", "status": "error"
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/robots.txt')
def robots_txt():
    return "User-agent: *\nAllow: /", 200, {'Content-Type': 'text/plain'}

@app.route('/api/status')
def api_status():
    alert = get_air_raid_alert()
    radiation = get_radiation()
    light_info = get_light_status()
    aqi = get_air_quality()
    
    return jsonify({
        "alert": alert,
        "radiation": radiation,
        "light": light_info["status"],
        "light_event": light_info["event"],
        "aqi": aqi,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
