from pathlib import Path
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from app.services.fnn_model import generate_benchmark_dataset

FEATURES = [
    "frp_max", "frp_mean", "frp_sum", "detection_count",
    "confidence_mean", "bright_ti4_max", "bright_ti4_mean",
    "duration_minutes", "hour", "night", "temperature_c",
    "humidity", "precipitation", "wind_speed", "wind_direction",
    "industrial_count", "power_count", "hospital_count", "school_count",
    "nearest_industrial_km", "nearest_hospital_km", "nearest_school_km",
    "baseline_deviation"
]

def train(rows: List[Dict[str, Any]], path: str):
    df = pd.DataFrame(rows).dropna(subset=["label"])
    valid_classes = ["CRITICAL_INDUSTRIAL_FIRE", "PERSISTENT_INDUSTRIAL_SOURCE", "VEGETATION_OR_AGRICULTURAL_FIRE", "CONTROLLED_OR_BENIGN", "FIRE", "PERSISTENT_SOURCE", "NORMAL"]
    df = df[df.label.isin(valid_classes)]
    
    if len(df) < 15 or df.label.nunique() < 2:
        # Augment with benchmark dataset if human labels are still sparse
        bench = generate_benchmark_dataset(300)
        df = pd.concat([df, bench], ignore_index=True)

    X = df[FEATURES].fillna(0)
    y = df.label.astype("category")
    mapping = {i: str(c) for i, c in enumerate(y.cat.categories)}
    yi = y.cat.codes

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        eval_metric="mlogloss",
        random_state=42
    )
    model.fit(X, yi)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    # Feature importances
    importances = dict(zip(FEATURES, [round(float(v), 4) for v in model.feature_importances_]))
    top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:6]

    bundle = {
        "model": model,
        "mapping": mapping,
        "features": FEATURES,
        "importances": importances,
        "top_features": top_features,
        "trained_rows": len(df)
    }
    joblib.dump(bundle, path)
    return {
        "trained_rows": len(df),
        "classes": list(mapping.values()),
        "top_features": top_features,
        "path": path
    }

def predict(features: Dict[str, Any], path: str):
    p = Path(path)
    if not p.exists():
        bench = generate_benchmark_dataset(350)
        train(bench.to_dict(orient="records"), str(p))

    bundle = joblib.load(p)
    X = pd.DataFrame([{k: features.get(k, 0.0) for k in bundle["features"]}])
    probs = bundle["model"].predict_proba(X)[0]
    idx = int(probs.argmax())
    label = bundle["mapping"][idx]
    
    prob_dict = {bundle["mapping"][i]: round(float(probs[i]), 4) for i in range(len(probs))}
    
    # Calculate feature contribution for this prediction
    contributions = []
    top_feats = bundle.get("top_features", [])
    for feat_name, importance in top_feats:
        val = features.get(feat_name, 0.0)
        contributions.append({
            "feature": feat_name,
            "value": val,
            "global_importance": importance
        })

    return {
        "available": True,
        "model_type": "XGBoost Gradient Boosted Decision Trees",
        "label": label,
        "confidence": round(float(probs[idx]), 4),
        "probabilities": prob_dict,
        "feature_contributions": contributions
    }
