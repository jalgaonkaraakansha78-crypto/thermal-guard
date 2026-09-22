@echo off
cd /d "%~dp0backend"
if not exist .env copy .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
