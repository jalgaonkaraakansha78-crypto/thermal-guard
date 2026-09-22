import requests
from app.core.config import get_settings
from app.services.catalog import get_catalog_context

def get_osm_context(lat: float, lon: float, radius_m: int = 2500):
    s = get_settings()
    catalog_res = get_catalog_context(lat, lon, radius_km=radius_m / 1000.0)
    
    if not s.osm_enabled:
        return {"available": True, "source": "catalog_offline", **catalog_res}
        
    q = f"""[out:json][timeout:15];(nw["industrial"](around:{radius_m},{lat},{lon});nw["power"](around:{radius_m},{lat},{lon});nw["amenity"="hospital"](around:{radius_m},{lat},{lon});nw["amenity"="school"](around:{radius_m},{lat},{lon}););out center tags;"""
    try:
        r = requests.post(s.osm_overpass_url, data=q, timeout=8)
        r.raise_for_status()
        els = r.json().get("elements", [])
        
        industrial, power, hospitals, schools = [], [], [], []
        for e in els:
            p = e.get("center", e)
            item = {
                "lat": p.get("lat"),
                "lon": p.get("lon"),
                "name": e.get("tags", {}).get("name", "Unnamed Facility"),
                "subtype": e.get("tags", {}).get("industrial") or e.get("tags", {}).get("amenity") or "facility",
                "hazard_rating": "HIGH" if "industrial" in e.get("tags", {}) else "STANDARD"
            }
            tags = e.get("tags", {})
            if "industrial" in tags:
                industrial.append(item)
            elif "power" in tags:
                power.append(item)
            elif tags.get("amenity") == "hospital":
                hospitals.append(item)
            elif tags.get("amenity") == "school":
                schools.append(item)
                
        # If Overpass returned few or no elements in this remote region, merge catalog assets
        if len(industrial) == 0 and len(catalog_res["industrial"]) > 0:
            industrial = catalog_res["industrial"]
        if len(power) == 0 and len(catalog_res["power"]) > 0:
            power = catalog_res["power"]
        if len(hospitals) == 0 and len(catalog_res["hospitals"]) > 0:
            hospitals = catalog_res["hospitals"]
        if len(schools) == 0 and len(catalog_res["schools"]) > 0:
            schools = catalog_res["schools"]

        return {
            "available": True,
            "source": "osm_live_with_catalog_enrichment",
            "industrial": industrial,
            "power": power,
            "hospitals": hospitals,
            "schools": schools
        }
    except Exception:
        # Graceful fallback to verified regional catalog
        return {
            "available": True,
            "source": "catalog_fallback",
            **catalog_res
        }
