@echo off
REM Script to initialize database with roles and users
REM Uses backend\venv when present (see project backend/venv).

cd /d "%~dp0\.."
set "PY=%~dp0..\venv\Scripts\python.exe"
if exist "%PY%" (
  "%PY%" -m scripts.init_db
) else (
  echo ERROR: backend\venv not found. Create it: cd backend ^& python -m venv venv ^& venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

pause
