@echo off
REM Menjalankan Chrome dengan port debug untuk collector lokal
REM (TikTok, Instagram, X, panel afiliasi).
setlocal enabledelayedexpansion

set "PORT=9222"
set "PROFILE=chrome-lagitren"
set "PANEL=https://partner.tiktokshop.com/affiliate-product-management/affiliate-product-pool/ranking?tab=0&market=4&prePage=product_ranking"

set "CHROME="
for %%P in (
  "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
  "%LocalAppData%\Google\Chrome\Application\chrome.exe"
) do if not defined CHROME if exist %%P set "CHROME=%%~P"

if not defined CHROME (
  echo [X] chrome.exe tidak ditemukan di lokasi standar.
  echo     Buka Chrome -^> ketik  chrome://version  -^> salin baris "Command Line".
  pause & exit /b 1
)
echo [i] Chrome : "%CHROME%"
echo [i] Profil : %PROFILE%
echo.

echo [1/4] Menutup SEMUA proses Chrome...
taskkill /IM chrome.exe /F >nul 2>&1
timeout /t 3 /nobreak >nul
tasklist /FI "IMAGENAME eq chrome.exe" 2>nul | find /i "chrome.exe" >nul
if not errorlevel 1 (
  echo     [!] Masih ada chrome.exe berjalan. Menunggu 5 detik lagi...
  timeout /t 5 /nobreak >nul
  taskkill /IM chrome.exe /F >nul 2>&1
  timeout /t 2 /nobreak >nul
)

echo [2/4] Menjalankan Chrome dengan --remote-debugging-port=%PORT% ...
start "" "%CHROME%" --remote-debugging-port=%PORT% --profile-directory=%PROFILE% --no-first-run --no-default-browser-check "%PANEL%"

echo [3/4] Menunggu port %PORT% siap (maks. 25 detik)...
set "READY="
for /L %%i in (1,1,25) do (
  if not defined READY (
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr /r /c:":%PORT% .*LISTENING" >nul 2>&1
    if not errorlevel 1 set "READY=1"
  )
)

echo [4/4] Hasil:
echo.
if defined READY (
  echo [OK] Chrome siap di 127.0.0.1:%PORT%.
  echo      1^) Pastikan halaman partner.tiktokshop.com sudah LOGIN.
  echo      2^) JANGAN tutup Chrome.
  echo      3^) Di jendela perintah lain jalankan:
  echo.
  echo         cd /d C:\lagitren\collector
  echo         python affiliate_panel.py --discover "%PANEL%"
) else (
  echo [X] Port %PORT% tetap tidak mendengarkan setelah 25 detik.
  echo.
  echo     Diagnostik:
  tasklist /FI "IMAGENAME eq chrome.exe" 2>nul | find /i "chrome.exe" >nul
  if errorlevel 1 (
    echo     - chrome.exe TIDAK berjalan ^-^> Chrome gagal dijalankan sama sekali.
    echo       Coba jalankan baris ini manual dan lihat pesan errornya:
    echo         "%CHROME%" --remote-debugging-port=%PORT% --profile-directory=%PROFILE%
  ) else (
    echo     - chrome.exe berjalan, tetapi tanpa port debug.
    echo       Artinya flag diabaikan: ada instance Chrome lain ^(mis. dijalankan
    echo       Task Scheduler, atau proses latar dari ekstensi^) yang memakai
    echo       folder data yang sama.
    echo       Coba: matikan "Continue running background apps when Chrome is closed"
    echo       di chrome://settings/system , lalu jalankan berkas ini lagi.
    echo.
    echo     Alternatif cepat ^(profil terpisah, perlu login ulang sekali^):
    echo       start_chrome_cdp_isolated.bat
  )
)
echo.
pause
