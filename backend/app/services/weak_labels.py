def generate_weak_label(features, risk):
    industrial=features["nearest_industrial_km"]<=2
    abnormal=features["baseline_deviation"]>=1.5
    fire_like=(risk["score"]>=55 and (features["night"] or abnormal or features["detection_count"]>=10))
    if industrial and not fire_like and features["baseline_deviation"]<1.0:
        return {"label":"LIKELY_PERSISTENT_SOURCE","confidence":0.70,"reason":"Nearby industrial context with behaviour near baseline."}
    if fire_like:
        return {"label":"LIKELY_FIRE","confidence":0.65,"reason":"Elevated risk with temporal/thermal evidence."}
    return {"label":"UNCERTAIN","confidence":0.35,"reason":"Insufficient evidence for a reliable weak label."}
