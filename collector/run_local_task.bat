@echo off
REM Dipanggil oleh Windows Task Scheduler (LagiTrenCollect) tiap 3 jam.
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
python run_local.py >> collect.log 2>&1
