import numpy as np
from sklearn.cluster import DBSCAN

def cluster(df, eps_km=1.0, min_samples=2):
    out = df.copy()
    coords = np.radians(out[["latitude","longitude"]].to_numpy())
    model = DBSCAN(eps=eps_km/6371.0088, min_samples=min_samples, metric="haversine")
    out["cluster_id"] = model.fit_predict(coords)
    return out
