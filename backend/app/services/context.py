from .geospatial import haversine_km

def summarize_context(lat,lon,osm):
    result={"industrial_count":0,"power_count":0,"hospital_count":0,"school_count":0,"nearest_industrial_km":None,"nearest_hospital_km":None,"nearest_school_km":None}
    if not osm.get("available"): return result
    for key,arr in [("industrial_count","industrial"),("power_count","power"),("hospital_count","hospitals"),("school_count","schools")]: result[key]=len(osm.get(arr,[]))
    for key,arr in [("nearest_industrial_km","industrial"),("nearest_hospital_km","hospitals"),("nearest_school_km","schools")]:
        ds=[haversine_km(lat,lon,x["lat"],x["lon"]) for x in osm.get(arr,[]) if x.get("lat") is not None and x.get("lon") is not None]
        result[key]=min(ds) if ds else None
    return result
