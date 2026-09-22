from typing import Dict, List, Any
import math
from app.services.geospatial import haversine_km

KNOWN_ASSETS: List[Dict[str, Any]] = [
    {
        "name": "Pasakha Industrial Estate (Steel and Ferro-Alloys)",
        "type": "industrial",
        "subtype": "heavy_metal_smelting",
        "lat": 26.8521,
        "lon": 89.4215,
        "hazard_rating": "HIGH",
        "description": "Ferro-alloys, iron and steel smelting furnaces with continuous high thermal emission."
    },
    {
        "name": "Dungsam Cement and Rotary Kiln Complex",
        "type": "industrial",
        "subtype": "cement_kiln",
        "lat": 26.8780,
        "lon": 91.5640,
        "hazard_rating": "MEDIUM",
        "description": "Rotary cement kilns operating at >1400°C; persistent thermal signature."
    },
    {
        "name": "Phuentsholing Polymer and Chemical Complex",
        "type": "industrial",
        "subtype": "chemical_storage",
        "lat": 26.8610,
        "lon": 89.3850,
        "hazard_rating": "CRITICAL",
        "description": "Chemical synthesis and volatile solvent storage facility."
    },
    {
        "name": "Chhukha Hydropower Generation Station",
        "type": "power",
        "subtype": "hydroelectric",
        "lat": 27.0864,
        "lon": 89.5878,
        "hazard_rating": "CRITICAL",
        "description": "High-voltage switchyards and critical power transmission grid node."
    },
    {
        "name": "Tala Hydropower Complex Switchyard",
        "type": "power",
        "subtype": "substation",
        "lat": 26.9850,
        "lon": 89.6200,
        "hazard_rating": "CRITICAL",
        "description": "1020 MW national electrical transmission hub."
    },
    {
        "name": "Phuentsholing General Hospital and Trauma Center",
        "type": "hospital",
        "subtype": "emergency_care",
        "lat": 26.8655,
        "lon": 89.3892,
        "hazard_rating": "VULNERABLE",
        "description": "150-bed referral hospital and trauma centre."
    },
    {
        "name": "Gedu Regional Hospital",
        "type": "hospital",
        "subtype": "general",
        "lat": 26.9250,
        "lon": 89.5210,
        "hazard_rating": "VULNERABLE",
        "description": "District hospital serving educational and residential population."
    },
    {
        "name": "Pasakha Higher Secondary School Campus",
        "type": "school",
        "subtype": "educational",
        "lat": 26.8480,
        "lon": 89.4180,
        "hazard_rating": "VULNERABLE",
        "description": "Campus with 900+ students adjacent to industrial buffer."
    },
    {
        "name": "Gedu College Campus",
        "type": "school",
        "subtype": "university",
        "lat": 26.9280,
        "lon": 89.5250,
        "hazard_rating": "VULNERABLE",
        "description": "Residential university campus."
    }
]

def get_catalog_context(lat: float, lon: float, radius_km: float = 12.0) -> Dict[str, Any]:
    industrial, power, hospitals, schools = [], [], [], []
    for asset in KNOWN_ASSETS:
        dist = haversine_km(lat, lon, asset["lat"], asset["lon"])
        if dist <= radius_km:
            item = {
                "name": asset["name"],
                "lat": asset["lat"],
                "lon": asset["lon"],
                "distance_km": round(dist, 2),
                "subtype": asset.get("subtype", "general"),
                "hazard_rating": asset.get("hazard_rating", "STANDARD"),
                "description": asset.get("description", "")
            }
            atype = asset.get("type")
            if atype == "industrial": industrial.append(item)
            elif atype == "power": power.append(item)
            elif atype == "hospital": hospitals.append(item)
            elif atype == "school": schools.append(item)
    for grp in (industrial, power, hospitals, schools):
        grp.sort(key=lambda x: x["distance_km"])
    return {
        "catalog_used": True,
        "industrial": industrial,
        "power": power,
        "hospitals": hospitals,
        "schools": schools,
        "total_nearby_assets": len(industrial) + len(power) + len(hospitals) + len(schools)
    }