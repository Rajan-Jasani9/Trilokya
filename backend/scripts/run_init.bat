@echo off
REM Script to initialize database with roles and users

cd /d "%~dp0\.."
python -m scripts.init_db

pause
