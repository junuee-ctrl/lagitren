@echo off
REM Jalankan Chrome dengan port debug supaya collector lokal (TikTok, Instagram,
REM X, panel afiliasi) bisa memakai sesi login yang sama.
REM Chrome yang sedang berjalan HARUS ditutup dulu, kalau tidak flag-nya diabaikan.
setlocal

set "PORT=9222"
set "PROFILE=chrome-lagitren"

set "CHROME="
for %%P in (
  "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
  "%LocalAppData%\Google\Chrome\Application\chrome.exe"
) do if not defined CHROME if exist %%P set "CHROME=%%~P"

if not defined CHROME (
  echo [X] chrome.exe tidak ditemukan di lokasi standar.
  echo     Buka Chrome, ketik  chrome://version  , salin "Command Line",
  echo     lalu beri tahu path-nya.
  pause & exit /b 1
)

echo [1/3] Menutup Chrome yang sedang berjalan...
taskkill /IM chrome.exe /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Menjalankan Chrome dengan --remote-debugging-port=%PORT% ...
start "" "%CHROME%" --remote-debugging-port=%PORT% --profile-directory=%PROFILE% "https://partner.tiktokshop.com/affiliate-product-management/affiliate-product-pool/ranking?tab=0&market=4&prePage=product_ranking"
timeout /t 4 /nobreak >nul

echo [3/3] Memeriksa port %PORT% ...
netstat -ano | findstr /r /c:":%PORT% .*LISTENING" >nul
if errorlevel 1 (
  echo.
  echo [X] Port %PORT% belum mendengarkan.
  echo     Kemungkinan masih ada proses Chrome lain. Tutup SEMUA jendela Chrome
  echo     lalu jalankan berkas ini lagi.
) else (
  echo.
  echo [OK] Chrome siap di 127.0.0.1:%PORT%.
  echo      Pastikan halaman partner.tiktokshop.com sudah login,
  echo      JANGAN tutup Chrome, lalu jalankan:
  echo.
  echo        python affiliate_panel.py --discover "https://partner.tiktokshop.com/affiliate-product-management/affiliate-product-pool/ranking?tab=0^&market=4^&prePage=product_ranking"
)
echo.
pause
