@echo off
REM Dipanggil oleh Windows Task Scheduler (LagiTrenCollect) tiap 3 jam.
REM F5 (insiden 2026-08-18): -u = tanpa buffer, log harian, simpan 30 hari.
cd /d "%~dp0"
if not exist logs mkdir logs
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd"') do set TODAY=%%i
if "%TODAY%"=="" set TODAY=undated
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
REM Pakai "py" (Python launcher) bila ada — alias "python" bisa mati diam-diam.
where py >nul 2>nul
if %errorlevel%==0 (
  py -u run_local.py >> "logs\%TODAY%.log" 2>&1
) else (
  python -u run_local.py >> "logs\%TODAY%.log" 2>&1
)
REM Hapus log lebih tua dari 30 hari.
forfiles /P logs /M *.log /D -30 /C "cmd /c del @path" >nul 2>nul
exit /b 0
