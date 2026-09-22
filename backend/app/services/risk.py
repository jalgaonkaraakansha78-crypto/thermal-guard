from typing import Dict, Any, List

def score(features: Dict[str, Any], plume: Dict[str, Any] = None) -> Dict[str, Any]:
    score_val = 0
    reasons: List[str] = []
    contributions: List[Dict[str, Any]] = []

    # 1. Thermal Intensity (Max 35 pts)
    frp = features.get("frp_max", 0.0)
    if frp >= 120.0:
        score_val += 32
        reasons.append("Extreme Fire Radiative Power (>120 MW)")
        contributions.append({"factor": "Extreme FRP", "points": 32, "weight": "HIGH", "detail": f"{frp:.1f} MW"})
    elif frp >= 60.0:
        score_val += 22
        reasons.append("Elevated Fire Radiative Power (60-120 MW)")
        contributions.append({"factor": "Elevated FRP", "points": 22, "weight": "MED", "detail": f"{frp:.1f} MW"})
    elif frp >= 30.0:
        score_val += 12
        reasons.append("Moderate Fire Radiative Power (30-60 MW)")
        contributions.append({"factor": "Moderate FRP", "points": 12, "weight": "LOW", "detail": f"{frp:.1f} MW"})

    # 2. Detection Confidence (Max 15 pts)
    conf = features.get("confidence_mean", 0.0)
    if conf >= 85.0:
        score_val += 15
        reasons.append("Satellite detection confidence >85%")
        contributions.append({"factor": "High Confidence", "points": 15, "weight": "MED", "detail": f"{conf:.0f}%"})
    elif conf >= 65.0:
        score_val += 8
        contributions.append({"factor": "Moderate Confidence", "points": 8, "weight": "LOW", "detail": f"{conf:.0f}%"})

    # 3. Spatial Cluster Density (Max 15 pts)
    det_count = features.get("detection_count", 1)
    if det_count >= 8:
        score_val += 15
        reasons.append("Multi-pixel clustered event (>=8 detections)")
        contributions.append({"factor": "High Cluster Density", "points": 15, "weight": "HIGH", "detail": f"{det_count} detections"})
    elif det_count >= 3:
        score_val += 8
        reasons.append("Clustered anomaly footprint")
        contributions.append({"factor": "Cluster Footprint", "points": 8, "weight": "LOW", "detail": f"{det_count} detections"})

    # 4. Baseline Deviation (Max 20 pts)
    dev = features.get("baseline_deviation", 0.0)
    if dev >= 2.0:
        score_val += 20
        reasons.append(f"Significant thermal output surge (+{dev:.1f}σ above facility baseline)")
        contributions.append({"factor": "Baseline Surge", "points": 20, "weight": "HIGH", "detail": f"+{dev:.2f}σ"})
    elif dev >= 1.0:
        score_val += 10
        reasons.append(f"Above facility baseline (+{dev:.1f}σ)")
        contributions.append({"factor": "Above Baseline", "points": 10, "weight": "MED", "detail": f"+{dev:.2f}σ"})

    # 5. Night-time Thermal Anomaly (Max 8 pts)
    if features.get("night"):
        score_val += 8
        reasons.append("Night-time thermal anomaly (eliminates solar reflection)")
        contributions.append({"factor": "Night-time Anomaly", "points": 8, "weight": "LOW", "detail": "Confirmed Night Pass"})

    # 6. Environmental & Fire Spread Hazard (Max 15 pts)
    spread_idx = plume.get("fire_spread_index", 0.0) if plume else 0.0
    if spread_idx >= 60.0:
        score_val += 12
        reasons.append("High meteorological fire spread index (high wind & dry conditions)")
        contributions.append({"factor": "High Fire Spread Index", "points": 12, "weight": "HIGH", "detail": f"{spread_idx:.0f}/100"})
    elif spread_idx >= 35.0:
        score_val += 6
        contributions.append({"factor": "Moderate Spread Hazard", "points": 6, "weight": "MED", "detail": f"{spread_idx:.0f}/100"})

    # 7. Sensitive & Critical Infrastructure Proximity (Max 15 pts)
    ind_km = features.get("nearest_industrial_km", 99.0)
    hosp_km = features.get("nearest_hospital_km", 99.0)
    sch_km = features.get("nearest_school_km", 99.0)

    if ind_km <= 1.0:
        score_val += 10
        reasons.append(f"Within industrial facility perimeter ({ind_km:.2f} km)")
        contributions.append({"factor": "Industrial Perimeter", "points": 10, "weight": "HIGH", "detail": f"{ind_km:.2f} km"})

    if hosp_km <= 2.5 or sch_km <= 2.5:
        score_val += 12
        reasons.append("Immediate proximity to sensitive population centers (hospital/school <= 2.5km)")
        contributions.append({"factor": "Sensitive Facility Proximity", "points": 12, "weight": "CRITICAL", "detail": f"{min(hosp_km, sch_km):.2f} km"})

    # Downwind intersection bonus
    if plume and plume.get("threatened_count", 0) > 0:
        score_val += 8
        reasons.append(f"Smoke and fire plume blowing directly toward {plume['threatened_count']} vulnerable assets")
        contributions.append({"factor": "Downwind Plume Hazard", "points": 8, "weight": "HIGH", "detail": f"{plume['threatened_count']} assets threatened"})

    total_score = min(100, score_val)
    
    if total_score >= 65:
        level = "CRITICAL"
    elif total_score >= 42:
        level = "HIGH"
    elif total_score >= 22:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "score": total_score,
        "level": level,
        "reasons": reasons,
        "factor_contributions": contributions,
        "disclaimer": "Explainable multi-criteria risk index grounded in satellite, atmospheric, and geospatial intelligence."
    }
