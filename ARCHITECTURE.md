# ThermalGuard architecture

## Runtime path
FIRMS -> validation/cleaning -> spatial event clustering -> PostGIS/DB -> OSM + weather enrichment -> facility baseline -> rule triage -> weak label -> analyst validation -> XGBoost -> optional satellite CV -> evidence agent -> dashboard/alerts.

## Data truth rules
1. FIRMS detections are observations, not ground-truth labels.
2. Weak labels are candidates and must not be silently promoted to truth.
3. High-impact alerts require human review.
4. Model metrics must use time/facility-aware splits to reduce leakage.
5. CNN/ViT is only enabled after a valid labeled imagery dataset exists.

## Production hardening still required before public internet exposure
- Alembic migrations
- JWT/RBAC and audit trail
- secrets manager
- TLS/reverse proxy
- Redis/Celery or durable queue for long enrichment jobs
- retry/backoff/circuit breakers for third-party APIs
- structured JSON logs, metrics and tracing
- PostGIS geometry columns and spatial indexes
- notification adapters (email/SMS/webhook)
- load/security testing and backups
