@echo off
title ThermalGuard Mission Control Launcher
echo ====================================================================
echo   THERMALGUARD - AI Industrial Disaster Intelligence Platform
echo   Smart India Hackathon 2026 (Problem Statement SIH26162)
echo ====================================================================
echo.
echo Starting Backend (FastAPI + FNN/XGBoost AI Engine)...
start "ThermalGuard API Server" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting Frontend (React Mission Control Dashboard)...
start "ThermalGuard Mission Control UI" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ====================================================================
echo Services started!
echo - Web Dashboard:  http://localhost:5173
echo - Backend API:    http://127.0.0.1:8000
echo - Swagger Docs:   http://127.0.0.1:8000/docs
echo ====================================================================
pause
