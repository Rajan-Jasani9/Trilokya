@echo off
echo Running TRL Definitions Initialization Script...
cd /d "%~dp0\.."
set "PY=%~dp0..\venv\Scripts\python.exe"
if exist "%PY%" (
  "%PY%" -m scripts.init_trl
) else (
  echo ERROR: backend\venv not found.
  pause
  exit /b 1
)
pause
