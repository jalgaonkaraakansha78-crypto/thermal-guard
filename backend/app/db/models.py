from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

def now():
    return datetime.now(timezone.utc)

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    detection_count: Mapped[int] = mapped_column(Integer)
    frp_max: Mapped[float] = mapped_column(Float, default=0)
    frp_mean: Mapped[float] = mapped_column(Float, default=0)
    frp_sum: Mapped[float] = mapped_column(Float, default=0)
    confidence_mean: Mapped[float] = mapped_column(Float, default=0)
    bright_ti4_max: Mapped[float] = mapped_column(Float, default=0)
    bright_ti4_mean: Mapped[float] = mapped_column(Float, default=0)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Validation(Base):
    __tablename__ = "validations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(32), index=True)
    label: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str] = mapped_column(Text, default="")
    analyst: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class IncidentAlert(Base):
    __tablename__ = "incident_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(32), index=True)
    severity: Mapped[str] = mapped_column(String(32))
    channel: Mapped[str] = mapped_column(String(32), default="BROADCAST_WEBHOOK")
    recipient: Mapped[str] = mapped_column(String(128), default="EMERGENCY_DISPATCH")
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="DISPATCHED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    rows: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(Text, default="")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
