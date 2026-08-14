@echo off
REM Dipanggil oleh Windows Task Scheduler (LagiTrenCollect) tiap 3 jam.
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
REM Pakai "py" (Python launcher) bila ada — alias "python" bisa mati diam-diam.
where py >nul 2>nul
if %errorlevel%==0 (
  py run_local.py >> collect.log 2>&1
) else (
  python run_local.py >> collect.log 2>&1
)
