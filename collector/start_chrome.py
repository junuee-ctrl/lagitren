"""Jalankan Google Chrome ASLI dengan remote debugging (untuk collector CDP).

Buka Chrome dengan profil khusus 'chrome-lagitren' + port 9222. Login TikTok &
Instagram sekali di jendela ini (login manual = tidak terdeteksi bot). Biarkan
jendela terbuka saat menjalankan `python main.py tiktok instagram`.

  python start_chrome.py

Lalu di .env pastikan:  BROWSER_CDP=http://localhost:9222
"""
import os
import subprocess
import sys

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
]

def main() -> None:
    chrome = next((c for c in CANDIDATES if os.path.exists(c)), None)
    if not chrome:
        print("Chrome tidak ditemukan. Pasang Google Chrome dulu, atau edit path di file ini.")
        sys.exit(1)
    profile = os.path.expandvars(r"%USERPROFILE%\chrome-lagitren")
    if os.name != "nt":
        profile = os.path.expanduser("~/chrome-lagitren")
    subprocess.Popen(
        [chrome, "--remote-debugging-port=9222", f"--user-data-dir={profile}"]
    )
    print("Chrome debug berjalan di port 9222.")
    print("Profil:", profile)
    print(">> Login TikTok (ads.tiktok.com/business/creativecenter) & Instagram di jendela ini.")
    print(">> Biarkan jendela TERBUKA, lalu jalankan: python main.py tiktok instagram")


if __name__ == "__main__":
    main()
