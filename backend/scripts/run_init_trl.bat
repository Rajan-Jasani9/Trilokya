@echo off
echo Running TRL Definitions Initialization Script...
cd /d %~dp0..
python -m scripts.init_trl
pause
