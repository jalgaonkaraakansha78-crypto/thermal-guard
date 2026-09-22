# ThermalGuard phases

1. **Observation** — FIRMS CSV/API ingestion.
2. **Quality control** — numeric normalization, confidence mapping, timestamp parsing, deduplication.
3. **Event formation** — geospatial clustering.
4. **Context** — OSM industrial/power/sensitive assets + weather.
5. **Facility baseline** — spatially associated historical event behaviour and deviation features.
6. **Triage** — transparent risk score with reasons.
7. **Weak supervision** — candidate labels only.
8. **Human validation** — analyst label API.
9. **XGBoost** — trained only from validated labels.
10. **Satellite CV** — optional ResNet/CNN starter in `ml/`, requiring a separate labeled imagery dataset.
11. **Agent investigation** — deterministic evidence synthesis with optional LLM enhancement.
12. **Live worker** — scheduled FIRMS ingestion.
13. **Deployment** — PostgreSQL/PostGIS Docker setup + migration scaffolding.
14. **Hardening** — auth/RBAC, secrets, durable queue, retries/circuit breakers, observability, notification policy, load/security testing.
