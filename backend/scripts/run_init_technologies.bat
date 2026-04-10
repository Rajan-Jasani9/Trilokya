@echo off
REM Seed technologies table and SVG placeholders (uses backend\venv)

cd /d "%~dp0\.."
set "PY=%~dp0..\venv\Scripts\python.exe"
if not exist "%PY%" (
  echo ERROR: backend\venv not found.
  pause
  exit /b 1
)
"%PY%" scripts\init_technologies.py
pause
