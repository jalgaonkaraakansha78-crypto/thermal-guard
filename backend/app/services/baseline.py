import pandas as pd, numpy as np

def facility_key(lat,lon,precision=3): return f"{round(lat,precision)}:{round(lon,precision)}"

def build_facility_baselines(events, facility_radius_km=2.0, min_events=5):
    # Prototype facility association: cluster events spatially to a stable facility-like key.
    if events.empty: return []
    from .geospatial import haversine_km
    assigned=[]; facilities=[]
    for _,e in events.iterrows():
        best=None; bestd=1e9
        for f in facilities:
            d=haversine_km(e.latitude,e.longitude,f["lat"],f["lon"])
            if d<facility_radius_km and d<bestd: best=f; bestd=d
        if best is None:
            best={"facility_id":f"FAC-{len(facilities)+1:05d}","lat":e.latitude,"lon":e.longitude,"events":[]}; facilities.append(best)
        best["events"].append(e)
        assigned.append((e.event_id if "event_id" in e else None,best["facility_id"]))
    out=[]
    for f in facilities:
        g=pd.DataFrame(f["events"])
        if len(g)<min_events: continue
        out.append({"facility_id":f["facility_id"],"latitude":f["lat"],"longitude":f["lon"],"event_count":len(g),"frp_mean":float(g.frp_mean.mean()),"frp_std":float(g.frp_mean.std(ddof=0) or 0),"night_fraction":float((pd.to_datetime(g.first_seen,utc=True).dt.hour<6).mean())})
    return out

def baseline_deviation(frp, mean, std):
    if mean is None or std is None: return 0.0
    return float((frp-mean)/max(std,1.0))
