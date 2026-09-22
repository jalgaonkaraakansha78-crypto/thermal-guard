import json
from typing import Dict, Any, List
from app.core.config import get_settings

def investigate(event: Dict[str, Any], context: Dict[str, Any], features: Dict[str, Any], risk: Dict[str, Any], weak_label: Dict[str, Any], ml: Dict[str, Any] = None, fnn: Dict[str, Any] = None, plume: Dict[str, Any] = None) -> Dict[str, Any]:
    s = get_settings()
    
    frp_max = event.get("frp_max", 0.0)
    det_count = event.get("detection_count", 1)
    conf = event.get("confidence_mean", 0.0)
    risk_level = risk.get("level", "LOW")
    ind_km = features.get("nearest_industrial_km", 99.0)
    baseline_dev = features.get("baseline_deviation", 0.0)
    
    # Classification determination from models
    ai_label = (ml and ml.get("label")) or (fnn and fnn.get("predicted_class")) or weak_label.get("label", "UNCERTAIN")
    
    findings = []
    findings.append(f"Thermal Signature: Peak FRP of {frp_max:.1f} MW across {det_count} clustered satellite detections (Mean confidence: {conf:.0f}%).")
    
    if ind_km <= 2.0:
        findings.append(f"Industrial Proximity: Located {ind_km:.2f} km from heavy industrial perimeter. Active blast furnaces/chemical processes present in buffer.")
    else:
        findings.append(f"Remote / Rural Context: Anomaly is {ind_km:.2f} km away from industrial zoning, indicating open terrain or vegetation.")
        
    if baseline_dev > 1.5:
        findings.append(f"Baseline Anomaly: Radiation is {baseline_dev:.2f} standard deviations above the facility's historical 30-day baseline.")
    elif baseline_dev < 0.5 and ind_km <= 2.0:
        findings.append(f"Baseline Consistency: Thermal output is consistent with documented operational baseline ({baseline_dev:.2f}σ).")

    # Plume & Weather Findings
    plume_summary = "Calm winds; minimal atmospheric dispersion detected."
    threatened_str = ""
    if plume:
        w_speed = plume.get("wind_speed_kmh", 0.0)
        downwind = plume.get("downwind_bearing_deg", 0.0)
        threat_count = plume.get("threatened_count", 0)
        spread_idx = plume.get("fire_spread_index", 0.0)
        
        plume_summary = f"Winds at {w_speed:.1f} km/h blowing downwind at {downwind:.0f}°. Fire spread hazard index: {spread_idx:.1f}/100."
        if threat_count > 0:
            names = [a.get("name", "Facility") for a in plume.get("threatened_assets", [])[:2]]
            threatened_str = f"Downwind plume vector directly intersects: {', '.join(names)} within {plume.get('plume_reach_km', 2):.1f} km."
            findings.append(threatened_str)

    # Tactical Actions
    actions = []
    if risk_level == "CRITICAL" or ai_label == "CRITICAL_INDUSTRIAL_FIRE":
        actions.append("IMMEDIATE: Dispatch industrial hazmat and foam firefighting units to coordinates.")
        if threatened_str:
            actions.append(f"ALERT: Issue shelter-in-place / air-quality warnings to {threatened_str}")
        actions.append("ACTION: Request high-resolution optical satellite tasking (Planet/Sentinel-2) for damage assessment.")
        actions.append("ESCALATE: Transmit real-time incident packet to State Disaster Management Authority (SDMA).")
    elif ai_label == "PERSISTENT_INDUSTRIAL_SOURCE":
        actions.append("STATUS: Classified as routine persistent industrial source (smelter/flare stack).")
        actions.append("ACTION: Maintain automated baseline monitoring; no emergency deployment required unless FRP exceeds 150 MW.")
    elif ai_label == "VEGETATION_OR_AGRICULTURAL_FIRE":
        actions.append("ACTION: Notify local forest range officers / agricultural monitoring desk of biomass burning.")
        actions.append("MONITOR: Check wind forecast to ensure fire does not migrate toward power transmission lines.")
    else:
        actions.append("ACTION: Flagged for routine human analyst verification. Review satellite pass imagery at next revisit.")

    summary = f"[{risk_level} RISK] {ai_label}: Anomaly with FRP {frp_max:.1f} MW, {det_count} detections. {plume_summary}"

    result = {
        "mode": "deterministic_expert_system",
        "executive_summary": summary,
        "classification": ai_label,
        "risk_level": risk_level,
        "key_findings": findings,
        "plume_assessment": plume_summary,
        "threatened_assets_summary": threatened_str or "No immediate vulnerable facilities in direct plume path.",
        "recommended_actions": actions,
        "evidence_chain": [
            "NASA FIRMS VIIRS (JPSS-1/NOAA-21) 375m active fire detection product",
            "Open-Meteo High-Resolution Atmospheric Wind and Humidity Model",
            "OpenStreetMap Industrial and Critical Infrastructure Topology",
            "ThermalGuard Multi-Layer Feature Baseline Engine"
        ]
    }

    # Optional LLM Enhancement if configured
    if s.agent_enabled and s.openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=s.openai_api_key)
            prompt_data = {
                "event": event,
                "features": features,
                "risk": risk,
                "classification": ai_label,
                "plume": plume
            }
            resp = client.chat.completions.create(
                model=s.openai_model,
                messages=[
                    {"role": "system", "content": "You are ThermalGuard AI, an industrial disaster management forensic intelligence agent for Smart India Hackathon. Provide rigorous, clear, concise incident analysis."},
                    {"role": "user", "content": f"Analyze this industrial thermal event:\n{json.dumps(prompt_data, default=str)}"}
                ],
                max_tokens=400,
                temperature=0.2
            )
            result["mode"] = "hybrid_llm_augmented"
            result["llm_analysis"] = resp.choices[0].message.content
        except Exception as e:
            result["llm_note"] = f"Deterministic fallback active ({e})"

    return result
