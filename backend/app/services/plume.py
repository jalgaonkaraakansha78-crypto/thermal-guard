import math
from typing import Dict, List, Any

def calculate_plume(event_lat: float, event_lon: float, weather: Dict[str, Any], assets: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    wind_speed = weather.get("wind_speed") or 0.0
    wind_dir = weather.get("wind_direction") or 0.0
    temp = weather.get("temperature_c") or 25.0
    humidity = weather.get("humidity") or 50.0
    precip = weather.get("precipitation") or 0.0

    downwind_deg = (wind_dir + 180.0) % 360.0
    downwind_rad = math.radians(downwind_deg)

    rh_factor = max(0.1, (100.0 - humidity) / 100.0)
    temp_factor = max(0.5, temp / 25.0)
    wind_factor = min(3.0, 1.0 + (wind_speed / 20.0))
    rain_damping = 0.2 if precip > 0.5 else 1.0

    spread_index = min(100.0, round(35.0 * rh_factor * temp_factor * wind_factor * rain_damping, 1))
    plume_reach_km = round(1.5 + (wind_speed * 0.22), 2)

    d_lat = (plume_reach_km / 111.0) * math.cos(downwind_rad)
    d_lon = (plume_reach_km / (111.0 * max(0.2, math.cos(math.radians(event_lat))))) * math.sin(downwind_rad)

    plume_endpoint = {
        "latitude": round(event_lat + d_lat, 5),
        "longitude": round(event_lon + d_lon, 5)
    }

    threatened_assets = []
    if assets:
        for a in assets:
            alat = a.get("lat") or a.get("latitude")
            alon = a.get("lon") or a.get("longitude")
            if alat is None or alon is None:
                continue

            dlon = math.radians(alon - event_lon)
            y = math.sin(dlon) * math.cos(math.radians(alat))
            x = math.cos(math.radians(event_lat)) * math.sin(math.radians(alat)) - math.sin(math.radians(event_lat)) * math.cos(math.radians(alat)) * math.cos(dlon)
            bearing_to_asset = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0

            angle_diff = abs(bearing_to_asset - downwind_deg)
            if angle_diff > 180.0:
                angle_diff = 360.0 - angle_diff

            dist_km = a.get("distance_km", 99.0)
            if angle_diff <= 35.0 and dist_km <= (plume_reach_km * 1.5):
                threatened_assets.append({
                    "name": a.get("name", "Asset"),
                    "distance_km": dist_km,
                    "bearing_deg": round(bearing_to_asset, 1),
                    "angular_deviation_deg": round(angle_diff, 1),
                    "hazard_rating": a.get("hazard_rating", "ALERT")
                })

    threatened_assets.sort(key=lambda x: x["distance_km"])

    return {
        "wind_speed_kmh": wind_speed,
        "wind_direction_from_deg": wind_dir,
        "downwind_bearing_deg": round(downwind_deg, 1),
        "fire_spread_index": spread_index,
        "plume_reach_km": plume_reach_km,
        "plume_endpoint": plume_endpoint,
        "threat_cone_angle_deg": 35.0,
        "threatened_assets": threatened_assets,
        "threatened_count": len(threatened_assets)
    }
