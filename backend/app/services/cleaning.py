import pandas as pd
import numpy as np

def clean_firms(df):
    df = df.copy()
    numeric = ["latitude","longitude","bright_ti4","bright_ti5","frp","scan","track"]
    for c in numeric:
        if c in df: df[c] = pd.to_numeric(df[c], errors="coerce")
    conf = {"l":40.0,"n":60.0,"h":90.0}
    df["confidence_raw"] = df["confidence"].astype(str).str.lower()
    df["confidence_num"] = df["confidence_raw"].map(conf).fillna(pd.to_numeric(df["confidence"], errors="coerce")).fillna(50.0)
    times = df["acq_time"].astype(str).str.replace(r"\\.0$", "", regex=True).str.zfill(4)
    df["acq_datetime"] = pd.to_datetime(df["acq_date"].astype(str)+" "+times.str[:2]+":"+times.str[2:4], errors="coerce", utc=True)
    df = df.dropna(subset=["latitude","longitude","acq_datetime","frp"])
    df = df[df.latitude.between(-90,90) & df.longitude.between(-180,180)]
    return df.drop_duplicates(subset=["latitude","longitude","acq_datetime","frp"]).reset_index(drop=True)
