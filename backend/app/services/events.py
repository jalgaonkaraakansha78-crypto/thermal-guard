import pandas as pd

def build_events(df):
    rows=[]
    for cid, g in df[df.cluster_id >= 0].groupby("cluster_id"):
        first,last=g.acq_datetime.min(),g.acq_datetime.max()
        rows.append({
            "cluster_id":int(cid), "latitude":float(g.latitude.mean()), "longitude":float(g.longitude.mean()),
            "detection_count":int(len(g)), "frp_max":float(g.frp.max()), "frp_mean":float(g.frp.mean()),
            "frp_sum":float(g.frp.sum()), "confidence_mean":float(g.confidence_num.mean()),
            "bright_ti4_max":float(g.bright_ti4.max()), "bright_ti4_mean":float(g.bright_ti4.mean()),
            "first_seen":first.isoformat(), "last_seen":last.isoformat(),
            "duration_minutes":float((last-first).total_seconds()/60),
        })
    return pd.DataFrame(rows).sort_values("first_seen").reset_index(drop=True) if rows else pd.DataFrame()
