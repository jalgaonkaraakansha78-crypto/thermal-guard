from pathlib import Path
import hashlib
import pandas as pd
from app.core.config import get_settings
from app.services.firms import load_csv, fetch_firms_api, validate_schema
from app.services.cleaning import clean_firms
from app.services.clustering import cluster
from app.services.events import build_events

def stable_event_id(row):
    raw=f"{round(row.latitude,5)}|{round(row.longitude,5)}|{row.first_seen}|{row.detection_count}"
    return "TG-"+hashlib.sha1(raw.encode()).hexdigest()[:12].upper()

def run_pipeline(df, stable_ids=False):
    s=get_settings(); validate_schema(df); clean=clean_firms(df); cl=cluster(clean,s.cluster_eps_km,s.cluster_min_samples); events=build_events(cl)
    if events.empty: return clean,cl,events
    if stable_ids: events.insert(0,"event_id",events.apply(stable_event_id,axis=1).tolist())
    else: events.insert(0,"event_id",[f"TG-{i:06d}" for i in range(1,len(events)+1)])
    return clean,cl,events

def run_from_csv(path): return run_pipeline(load_csv(path), stable_ids=False)
def run_live(): return run_pipeline(fetch_firms_api(), stable_ids=True)
