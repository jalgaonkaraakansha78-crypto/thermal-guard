import requests
from app.core.config import get_settings

def get_weather(lat,lon):
    s=get_settings()
    if not s.weather_enabled: return {"available":False,"reason":"disabled"}
    params={"latitude":lat,"longitude":lon,"current":"temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m","timezone":"UTC"}
    try:
        r=requests.get(s.open_meteo_url,params=params,timeout=15); r.raise_for_status(); c=r.json().get("current",{})
        return {"available":True,"temperature_c":c.get("temperature_2m"),"humidity":c.get("relative_humidity_2m"),"precipitation":c.get("precipitation"),"wind_speed":c.get("wind_speed_10m"),"wind_direction":c.get("wind_direction_10m")}
    except Exception as e: return {"available":False,"error":str(e)}
