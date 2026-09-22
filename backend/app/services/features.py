import pandas as pd
from .baseline import baseline_deviation

def make_features(event, weather, ctx, baseline=None):
    ts=pd.to_datetime(event["first_seen"],utc=True)
    hour=ts.hour + ts.minute/60
    night=int(hour<6 or hour>=18)
    dev=baseline_deviation(event["frp_mean"], baseline.get("frp_mean"), baseline.get("frp_std")) if baseline else 0.0
    return {
        "frp_max":event["frp_max"],"frp_mean":event["frp_mean"],"frp_sum":event["frp_sum"],"detection_count":event["detection_count"],
        "confidence_mean":event["confidence_mean"],"bright_ti4_max":event["bright_ti4_max"],"bright_ti4_mean":event["bright_ti4_mean"],"duration_minutes":event["duration_minutes"],
        "hour":hour,"night":night,"temperature_c":weather.get("temperature_c") or 0,"humidity":weather.get("humidity") or 0,
        "precipitation":weather.get("precipitation") or 0,"wind_speed":weather.get("wind_speed") or 0,"wind_direction":weather.get("wind_direction") or 0,
        "industrial_count":ctx["industrial_count"],"power_count":ctx["power_count"],"hospital_count":ctx["hospital_count"],"school_count":ctx["school_count"],
        "nearest_industrial_km":ctx["nearest_industrial_km"] if ctx["nearest_industrial_km"] is not None else 99,
        "nearest_hospital_km":ctx["nearest_hospital_km"] if ctx["nearest_hospital_km"] is not None else 99,
        "nearest_school_km":ctx["nearest_school_km"] if ctx["nearest_school_km"] is not None else 99,
        "baseline_deviation":dev,
    }
