from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.database import init_db
from app.api.events import router as events_router
from app.api.admin import router as admin_router

configure_logging(); settings=get_settings(); init_db()
@asynccontextmanager
async def lifespan(app):
    init_db(); yield
app=FastAPI(title=settings.app_name,version="2.0.0",description="Context-aware industrial thermal anomaly intelligence platform")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(events_router); app.include_router(admin_router)
@app.get("/")
def root(): return {"name":settings.app_name,"version":"2.0.0","status":"running"}
@app.get("/health")
def health(): return {"status":"ok","database":settings.database_url.split(":")[0]}
