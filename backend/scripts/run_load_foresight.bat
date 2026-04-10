@echo off
REM Load technology_foresight_seed.json (uses backend\venv)

cd /d "%~dp0\.."
set "PY=%~dp0..\venv\Scripts\python.exe"
if not exist "%PY%" (
  echo ERROR: backend\venv not found.
  pause
  exit /b 1
)
"%PY%" scripts\load_technology_foresight.py
pause
