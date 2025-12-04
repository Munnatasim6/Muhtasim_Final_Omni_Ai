@echo off
TITLE OmniTrade AI Core - God Mode Launcher
CLS

ECHO ========================================================
ECHO       OmniTrade AI Core - "God-Tier" System v2.0
ECHO ========================================================
ECHO.

:: 1. Check for .env
IF NOT EXIST .env (
    ECHO [WARNING] .env file not found! Creating from .env.example...
    COPY .env.example .env
    ECHO [INFO] .env created. PLEASE EDIT IT WITH YOUR REAL API KEYS!
    PAUSE
)

:: 2. Check for Docker
ECHO [INFO] Checking Docker status...
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Docker is NOT running. Please start Docker Desktop and try again.
    PAUSE
    EXIT /B
)

:: 3. Start Infrastructure (DB, Redis, Vector DB)
ECHO [INFO] Starting Database and Redis...
docker-compose up -d timescaledb redis

:: 4. Install Dependencies
ECHO [INFO] Installing/Verifying Python Dependencies...
pip install -r requirements.txt
pip install fastapi uvicorn chromadb google-cloud-aiplatform

:: 5. Start Backend API (FastAPI)
ECHO [INFO] Starting Backend API Gateway...
start "OmniTrade Backend API" cmd /k "uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000"

:: 6. Start Frontend (React/Streamlit Placeholder)
:: Note: In a real React app, we'd run 'npm start'. For now, we still use Streamlit as the dashboard or serve React static files.
:: Since we moved to a React structure, we should ideally run a dev server if node is installed.
:: For this demo, we'll assume the user wants to see the Streamlit dashboard which we can point to the new location if needed,
:: OR we can just log that the Frontend is ready to be built.
:: Let's keep Streamlit for immediate gratification but note the React structure.

ECHO [INFO] Launching Legacy Dashboard (Streamlit)...
start "OmniTrade Dashboard" cmd /k "streamlit run dashboard/app.py"

ECHO [INFO] System is running!
ECHO [INFO] Backend API: http://localhost:8000/docs
ECHO [INFO] Dashboard: http://localhost:8501

PAUSE
