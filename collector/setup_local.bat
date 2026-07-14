@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================
echo   Lagi Tren - Setup Collector Lokal
echo ============================================
echo.

echo [1/4] git pull (ambil kode terbaru)...
git pull
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
echo.

echo [2/4] Buka Chrome untuk LOGIN (TikTok Trends, Instagram, X)...
python start_chrome.py
echo.
echo   ^>^> Login di KETIGA tab yang terbuka.
echo   ^>^> Untuk TikTok, login penuh membuka daftar 20 hashtag.
echo   ^>^> Setelah selesai login, JANGAN tutup Chrome. Kembali ke sini.
echo.
pause
echo.

echo [3/4] Kumpulkan data sekarang (tiktok + instagram + x)...
python run_local.py
echo.

echo [4/4] Daftarkan tugas terjadwal tiap 3 jam (otomatis)...
schtasks /Create /SC HOURLY /MO 3 /TN "LagiTrenCollect" /TR "\"%~dp0run_local_task.bat\"" /F
echo.

echo ============================================
echo   Selesai. Data diperbarui otomatis tiap 3 jam
echo   selama PC menyala. Log: collect.log
echo   Lihat/hapus jadwal:
echo     schtasks /Query /TN LagiTrenCollect
echo     schtasks /Delete /TN LagiTrenCollect /F
echo ============================================
pause
endlocal
