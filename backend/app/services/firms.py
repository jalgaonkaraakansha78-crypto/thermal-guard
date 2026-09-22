from pathlib import Path
import io, requests, pandas as pd
from app.core.config import get_settings

REQUIRED = ["latitude","longitude","bright_ti4","acq_date","acq_time","confidence","frp","daynight"]

def load_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)

def fetch_firms_api():
    s = get_settings()
    if not s.firms_map_key:
        raise RuntimeError("FIRMS_MAP_KEY is not configured. Put it in backend/.env")
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{s.firms_map_key}/{s.firms_source}/{s.firms_bbox}/{s.firms_days}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))

def validate_schema(df):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing: raise ValueError(f"Missing FIRMS columns: {missing}")
    return df
