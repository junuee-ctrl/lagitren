@echo off
REM Alternatif: Chrome dengan FOLDER DATA TERPISAH.
REM Tidak pernah bentrok dengan Chrome biasa, jadi port debug selalu aktif.
REM Konsekuensi: profil baru ^-^> perlu login TikTok Shop sekali di jendela ini.
REM Login tersimpan, jadi cukup sekali saja.
setlocal enabledelayedexpansion

set "PORT=9222"
set "DATADIR=%LocalAppData%\lagitren-chrome"
set "PANEL=https://partner.tiktokshop.com/affiliate-product-management/affiliate-product-pool/ranking?tab=0&market=4&prePage=product_ranking"

set "CHROME="
for %%P in (
  "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
  "%LocalAppData%\Google\Chrome\Application\chrome.exe"
) do if not defined CHROME if exist %%P set "CHROME=%%~P"

if not defined CHROME (
  echo [X] chrome.exe tidak ditemukan. & pause & exit /b 1
)

echo [i] Folder data terpisah: %DATADIR%
echo [1/3] Menjalankan Chrome...
start "" "%CHROME%" --remote-debugging-port=%PORT% --user-data-dir="%DATADIR%" --no-first-run --no-default-browser-check "%PANEL%"

echo [2/3] Menunggu port %PORT% (maks. 25 detik)...
set "READY="
for /L %%i in (1,1,25) do (
  if not defined READY (
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr /r /c:":%PORT% .*LISTENING" >nul 2>&1
    if not errorlevel 1 set "READY=1"
  )
)

echo [3/3] Hasil:
echo.
if defined READY (
  echo [OK] Chrome siap di 127.0.0.1:%PORT%.
  echo      Jendela ini memakai profil BARU, jadi LOGIN dulu ke
  echo      partner.tiktokshop.com ^(sekali saja; tersimpan untuk seterusnya^).
  echo      Setelah login, JANGAN tutup Chrome, lalu jalankan:
  echo.
  echo         cd /d C:\lagitren\collector
  echo         python affiliate_panel.py --discover "%PANEL%"
) else (
  echo [X] Port %PORT% masih tidak mendengarkan.
  echo     Kemungkinan port dipakai proses lain. Periksa dengan:
  echo         netstat -ano ^| findstr :%PORT%
)
echo.
pause
