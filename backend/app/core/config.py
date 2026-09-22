from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "ThermalGuard"
    env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "sqlite:///./thermalguard.db"
    firms_map_key: str = ""
    firms_source: str = "VIIRS_NOAA21_NRT"
    firms_bbox: str = "88,26,92,28"
    firms_days: int = 1
    poll_minutes: int = 60
    osm_enabled: bool = True
    weather_enabled: bool = True
    osm_overpass_url: str = "https://overpass-api.de/api/interpreter"
    open_meteo_url: str = "https://api.open-meteo.com/v1/forecast"
    cluster_eps_km: float = 1.0
    cluster_min_samples: int = 2
    facility_radius_km: float = 2.0
    baseline_min_events: int = 5
    model_path: str = "./artifacts/xgboost.joblib"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    agent_enabled: bool = True
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    webhook_url: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings():
    return Settings()
