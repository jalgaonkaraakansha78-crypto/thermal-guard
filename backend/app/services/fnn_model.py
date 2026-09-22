from pathlib import Path
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "frp_max", "frp_mean", "frp_sum", "detection_count",
    "confidence_mean", "bright_ti4_max", "bright_ti4_mean",
    "duration_minutes", "hour", "night", "temperature_c",
    "humidity", "precipitation", "wind_speed", "wind_direction",
    "industrial_count", "power_count", "hospital_count", "school_count",
    "nearest_industrial_km", "nearest_hospital_km", "nearest_school_km",
    "baseline_deviation"
]

CLASSES = [
    "CRITICAL_INDUSTRIAL_FIRE",
    "PERSISTENT_INDUSTRIAL_SOURCE",
    "VEGETATION_OR_AGRICULTURAL_FIRE",
    "CONTROLLED_OR_BENIGN"
]

def generate_benchmark_dataset(n_samples: int = 400) -> pd.DataFrame:
    np.random.seed(42)
    rows = []
    
    # 1. CRITICAL_INDUSTRIAL_FIRE
    for _ in range(n_samples // 4):
        rows.append({
            "frp_max": float(np.random.uniform(70, 280)),
            "frp_mean": float(np.random.uniform(50, 180)),
            "frp_sum": float(np.random.uniform(200, 1200)),
            "detection_count": int(np.random.randint(5, 25)),
            "confidence_mean": float(np.random.uniform(80, 100)),
            "bright_ti4_max": float(np.random.uniform(340, 380)),
            "bright_ti4_mean": float(np.random.uniform(330, 365)),
            "duration_minutes": float(np.random.uniform(60, 480)),
            "hour": float(np.random.uniform(0, 24)),
            "night": int(np.random.choice([0, 1], p=[0.4, 0.6])),
            "temperature_c": float(np.random.uniform(18, 38)),
            "humidity": float(np.random.uniform(15, 55)),
            "precipitation": 0.0,
            "wind_speed": float(np.random.uniform(12, 35)),
            "wind_direction": float(np.random.uniform(0, 360)),
            "industrial_count": int(np.random.randint(2, 10)),
            "power_count": int(np.random.randint(0, 4)),
            "hospital_count": int(np.random.randint(0, 3)),
            "school_count": int(np.random.randint(0, 4)),
            "nearest_industrial_km": float(np.random.uniform(0.1, 1.8)),
            "nearest_hospital_km": float(np.random.uniform(0.5, 8.0)),
            "nearest_school_km": float(np.random.uniform(0.4, 6.0)),
            "baseline_deviation": float(np.random.uniform(2.1, 6.5)),
            "label": "CRITICAL_INDUSTRIAL_FIRE"
        })

    # 2. PERSISTENT_INDUSTRIAL_SOURCE
    for _ in range(n_samples // 4):
        rows.append({
            "frp_max": float(np.random.uniform(35, 110)),
            "frp_mean": float(np.random.uniform(30, 85)),
            "frp_sum": float(np.random.uniform(120, 500)),
            "detection_count": int(np.random.randint(6, 30)),
            "confidence_mean": float(np.random.uniform(70, 95)),
            "bright_ti4_max": float(np.random.uniform(320, 350)),
            "bright_ti4_mean": float(np.random.uniform(315, 340)),
            "duration_minutes": float(np.random.uniform(120, 720)),
            "hour": float(np.random.uniform(0, 24)),
            "night": int(np.random.choice([0, 1])),
            "temperature_c": float(np.random.uniform(15, 32)),
            "humidity": float(np.random.uniform(30, 80)),
            "precipitation": float(np.random.uniform(0, 5)),
            "wind_speed": float(np.random.uniform(2, 18)),
            "wind_direction": float(np.random.uniform(0, 360)),
            "industrial_count": int(np.random.randint(3, 12)),
            "power_count": int(np.random.randint(0, 3)),
            "hospital_count": int(np.random.randint(0, 2)),
            "school_count": int(np.random.randint(0, 2)),
            "nearest_industrial_km": float(np.random.uniform(0.05, 0.9)),
            "nearest_hospital_km": float(np.random.uniform(1.5, 12.0)),
            "nearest_school_km": float(np.random.uniform(1.2, 10.0)),
            "baseline_deviation": float(np.random.uniform(-0.6, 0.8)),
            "label": "PERSISTENT_INDUSTRIAL_SOURCE"
        })

    # 3. VEGETATION_OR_AGRICULTURAL_FIRE
    for _ in range(n_samples // 4):
        rows.append({
            "frp_max": float(np.random.uniform(20, 90)),
            "frp_mean": float(np.random.uniform(15, 60)),
            "frp_sum": float(np.random.uniform(40, 250)),
            "detection_count": int(np.random.randint(2, 8)),
            "confidence_mean": float(np.random.uniform(55, 85)),
            "bright_ti4_max": float(np.random.uniform(310, 345)),
            "bright_ti4_mean": float(np.random.uniform(305, 335)),
            "duration_minutes": float(np.random.uniform(20, 180)),
            "hour": float(np.random.uniform(9, 17)),
            "night": 0,
            "temperature_c": float(np.random.uniform(20, 38)),
            "humidity": float(np.random.uniform(20, 60)),
            "precipitation": 0.0,
            "wind_speed": float(np.random.uniform(5, 25)),
            "wind_direction": float(np.random.uniform(0, 360)),
            "industrial_count": 0,
            "power_count": 0,
            "hospital_count": 0,
            "school_count": 0,
            "nearest_industrial_km": float(np.random.uniform(6.0, 45.0)),
            "nearest_hospital_km": float(np.random.uniform(8.0, 50.0)),
            "nearest_school_km": float(np.random.uniform(5.0, 40.0)),
            "baseline_deviation": 0.0,
            "label": "VEGETATION_OR_AGRICULTURAL_FIRE"
        })

    # 4. CONTROLLED_OR_BENIGN
    for _ in range(n_samples // 4):
        rows.append({
            "frp_max": float(np.random.uniform(4, 25)),
            "frp_mean": float(np.random.uniform(3, 18)),
            "frp_sum": float(np.random.uniform(8, 45)),
            "detection_count": int(np.random.randint(1, 3)),
            "confidence_mean": float(np.random.uniform(40, 70)),
            "bright_ti4_max": float(np.random.uniform(298, 320)),
            "bright_ti4_mean": float(np.random.uniform(295, 315)),
            "duration_minutes": float(np.random.uniform(0, 45)),
            "hour": float(np.random.uniform(0, 24)),
            "night": int(np.random.choice([0, 1])),
            "temperature_c": float(np.random.uniform(10, 30)),
            "humidity": float(np.random.uniform(40, 95)),
            "precipitation": float(np.random.uniform(0, 8)),
            "wind_speed": float(np.random.uniform(1, 14)),
            "wind_direction": float(np.random.uniform(0, 360)),
            "industrial_count": int(np.random.randint(0, 2)),
            "power_count": 0,
            "hospital_count": 0,
            "school_count": 0,
            "nearest_industrial_km": float(np.random.uniform(1.0, 30.0)),
            "nearest_hospital_km": float(np.random.uniform(2.0, 35.0)),
            "nearest_school_km": float(np.random.uniform(2.0, 30.0)),
            "baseline_deviation": float(np.random.uniform(-1.0, 0.4)),
            "label": "CONTROLLED_OR_BENIGN"
        })

    return pd.DataFrame(rows)

def train_fnn(df: pd.DataFrame, model_path: str) -> Dict[str, Any]:
    X = df[FEATURES].fillna(0)
    y = df["label"].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    fnn = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        alpha=0.001,
        batch_size=32,
        learning_rate_init=0.005,
        max_iter=300,
        random_state=42,
        early_stopping=True,
        n_iter_no_change=15
    )
    fnn.fit(X_scaled, y)
    
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model": fnn,
        "scaler": scaler,
        "classes": list(fnn.classes_),
        "features": FEATURES,
        "architecture": "FNN-MLP(23->64->32->4)"
    }
    joblib.dump(bundle, model_path)
    return {
        "status": "trained",
        "architecture": bundle["architecture"],
        "classes": bundle["classes"],
        "samples": len(df)
    }

def predict_fnn(features: Dict[str, Any], model_path: str = "./artifacts/fnn_model.joblib") -> Dict[str, Any]:
    p = Path(model_path)
    if not p.exists():
        df = generate_benchmark_dataset()
        train_fnn(df, str(p))
        
    bundle = joblib.load(p)
    fnn = bundle["model"]
    scaler = bundle["scaler"]
    
    x_df = pd.DataFrame([[features.get(k, 0.0) for k in bundle["features"]]], columns=bundle["features"])
    x_scaled = scaler.transform(x_df)
    
    probs = fnn.predict_proba(x_scaled)[0]
    best_idx = int(np.argmax(probs))
    best_label = bundle["classes"][best_idx]
    
    prob_dict = {bundle["classes"][i]: round(float(probs[i]), 4) for i in range(len(probs))}
    
    return {
        "available": True,
        "model_type": "Feedforward Neural Network (FNN / MLP)",
        "architecture": bundle.get("architecture", "FNN-MLP"),
        "predicted_class": best_label,
        "confidence": round(float(probs[best_idx]), 4),
        "probabilities": prob_dict
    }
