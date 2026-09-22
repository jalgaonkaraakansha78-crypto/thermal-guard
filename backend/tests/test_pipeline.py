from pathlib import Path
import unittest
from fastapi.testclient import TestClient

from app.services.pipeline import run_from_csv
from app.services.fnn_model import predict_fnn
from app.services.ml import predict
from app.services.plume import calculate_plume
from app.services.risk import score
from app.main import app

class TestThermalGuardEndToEnd(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_pipeline_clustering(self):
        csv = Path(__file__).resolve().parents[1] / "data" / "viirs-jpss1_2024_Bhutan.csv"
        clean, clustered, events = run_from_csv(csv)
        self.assertGreater(len(clean), 0)
        self.assertIn("cluster_id", clustered.columns)
        self.assertGreater(len(events), 0)
        self.assertTrue(events.event_id.iloc[0].startswith("TG-"))

    def test_fnn_prediction(self):
        res = predict_fnn({
            "frp_max": 140.0,
            "nearest_industrial_km": 0.4,
            "baseline_deviation": 3.2,
            "confidence_mean": 92.0
        })
        self.assertTrue(res["available"])
        self.assertIn(res["predicted_class"], [
            "CRITICAL_INDUSTRIAL_FIRE", "PERSISTENT_INDUSTRIAL_SOURCE",
            "VEGETATION_OR_AGRICULTURAL_FIRE", "CONTROLLED_OR_BENIGN"
        ])

    def test_xgboost_prediction(self):
        res = predict({
            "frp_max": 140.0,
            "nearest_industrial_km": 0.4,
            "baseline_deviation": 3.2,
            "confidence_mean": 92.0
        }, "./artifacts/xgboost.joblib")
        self.assertTrue(res["available"])
        self.assertIn("label", res)
        self.assertGreater(res["confidence"], 0.0)

    def test_plume_spread(self):
        weather = {
            "wind_speed": 18.0,
            "wind_direction": 220.0,
            "temperature_c": 32.0,
            "humidity": 25.0,
            "precipitation": 0.0
        }
        res = calculate_plume(26.85, 89.42, weather)
        self.assertIn("downwind_bearing_deg", res)
        self.assertGreater(res["fire_spread_index"], 10.0)
        self.assertIn("plume_endpoint", res)

    def test_api_health_and_stats(self):
        r_health = self.client.get("/health")
        self.assertEqual(r_health.status_code, 200)
        
        r_stats = self.client.get("/events/stats")
        self.assertEqual(r_stats.status_code, 200)
        data = r_stats.json()
        self.assertGreater(data["total_events"], 0)

    def test_api_analysis_and_report(self):
        r_list = self.client.get("/events/?limit=1")
        self.assertEqual(r_list.status_code, 200)
        events = r_list.json().get("events", [])
        self.assertGreater(len(events), 0)
        
        event_id = events[0]["event_id"]
        r_ana = self.client.get(f"/events/{event_id}/analysis")
        self.assertEqual(r_ana.status_code, 200)
        ana_data = r_ana.json()
        self.assertIn("risk", ana_data)
        self.assertIn("plume", ana_data)
        self.assertIn("ml", ana_data)
        self.assertIn("fnn", ana_data)

        r_rep = self.client.get(f"/events/{event_id}/report")
        self.assertEqual(r_rep.status_code, 200)
        rep_data = r_rep.json()
        self.assertIn("report_id", rep_data)
        self.assertIn("executive_summary", rep_data)

    def test_simulation_stream(self):
        r_sim = self.client.post("/events/simulate-stream")
        self.assertEqual(r_sim.status_code, 200)
        sim_data = r_sim.json()
        self.assertTrue(sim_data["ok"])
        self.assertEqual(len(sim_data["simulated_events"]), 2)

if __name__ == "__main__":
    unittest.main()
