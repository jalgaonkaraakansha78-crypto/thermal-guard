# ThermalGuard — Production-Oriented Full Stack (Python 3.14)

ThermalGuard converts satellite thermal observations into context-aware industrial thermal anomaly intelligence.

## Python 3.14 compatibility
This package is prepared for **CPython 3.14.x on Windows x64**. The dependency set uses versions with Python 3.14 wheels and the Windows installer forces binary wheels so pandas/NumPy/SciPy/scikit-learn do not attempt local C/C++ compilation.

Pandas 2.3.3 was the first pandas release with general Python 3.14 compatibility; this package uses pandas 3.0.5. NumPy 2.5.x and SciPy 1.18.x provide Python 3.14 wheels. XGBoost 3.4.1 publishes Windows x64 wheels for Python 3.14.

## Fastest Windows setup
Open PowerShell in the extracted `thermalguard` folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup_windows_py314.ps1
```

The script:
- verifies Python 3.14.x
- creates `backend\\venv`
- upgrades pip
- installs the pinned dependencies using `--only-binary=:all:`
- creates `.env` if missing
- verifies pandas/NumPy/scikit-learn/XGBoost imports

Then start the API:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`

## Frontend
Requires Node.js/npm:

```powershell
cd frontend
npm install
npm run dev
```

## What is included
- FIRMS CSV ingestion + live FIRMS Area API ingestion
- Robust cleaning and confidence normalization
- Spatio-temporal-ready DBSCAN event clustering
- OSM industrial/power/sensitive-location enrichment
- Open-Meteo weather enrichment
- Facility-style spatial grouping and baseline deviation features
- Transparent risk triage engine
- Weak-label generator: FIRE / PERSISTENT_SOURCE / UNCERTAIN candidates
- Human validation API
- XGBoost training/inference module (requires validated labels)
- Optional LLM investigation agent with deterministic fallback
- FastAPI backend + React dashboard
- SQLite for local development; PostgreSQL/PostGIS Docker deployment
- Scheduled live ingestion worker
- Automated pipeline test

## Important production truth
The bundled Bhutan dataset is unlabeled. FIRMS observations are treated as observations, not ground truth. XGBoost is not trained on fabricated labels. The rule engine is a triage score, not a calibrated fire probability. Satellite-image CV training requires a separate, properly labeled imagery dataset.

## Live FIRMS
1. Get a FIRMS MAP_KEY.
2. Put it in `backend/.env` as `FIRMS_MAP_KEY=...`.
3. Set `FIRMS_SOURCE` and `FIRMS_BBOX`.
4. Start the worker:

```powershell
cd backend
.\venv\Scripts\python.exe worker.py
```

FIRMS polling frequency is not the same thing as satellite revisit/observation latency.

## Docker / PostgreSQL + PostGIS
```powershell
cd infra
docker compose up --build
```

Before public deployment, configure non-default secrets, TLS/reverse proxy, authentication/RBAC, rate limits, backups, monitoring, alert delivery and database migrations.

## API
- GET `/health`
- GET `/events/`
- GET `/events/{event_id}`
- GET `/events/{event_id}/analysis`
- POST `/events/{event_id}/validate`
- POST `/events/ingest?live=true`
- GET `/admin/model/status`

## Production roadmap
1. Authoritative industrial registry + PostGIS facility geometry
2. Rolling facility-specific baseline with time-of-day/day-of-week seasonality
3. Label QA and double-review for high-impact labels
4. Time/facility-aware train/validation/test split
5. XGBoost calibration and PR-AUC/F1/recall reporting
6. Proper satellite-image dataset + CNN/ViT + multimodal fusion
7. LangGraph evidence workflow with provenance
8. Durable queue/workers
9. Auth/RBAC, audit logs, observability, migrations and backups
10. Load tests and disaster-recovery runbook
